#!/usr/bin/env python3
"""
Tokens 多维统计报告脚本
统计各 Agent 的 tokens 消耗、模型分布等
"""

import sqlite3
import os
import json
from datetime import datetime, timedelta
from collections import defaultdict

def find_session_dbs():
    """查找所有 session 数据库"""
    dbs = []
    home = os.path.expanduser("~")
    
    # 标准 Hermes 位置
    hermes_home = os.path.join(home, ".hermes")
    
    # 查找所有 profile 的 session.db
    profiles_dir = os.path.join(hermes_home, "profiles")
    if os.path.exists(profiles_dir):
        for profile in os.listdir(profiles_dir):
            profile_home = os.path.join(profiles_dir, profile, "home", ".hermes")
            session_db = os.path.join(profile_home, "session.db")
            if os.path.exists(session_db):
                dbs.append((profile, session_db))
    
    # 默认 profile
    default_session = os.path.join(hermes_home, "session.db")
    if os.path.exists(default_session):
        dbs.append(("default", default_session))
    
    return dbs

def get_tokens_from_db(db_path):
    """从数据库提取 tokens 数据"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 尝试查找 tokens 相关的表
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [t[0] for t in cursor.fetchall()]
        
        tokens_data = []
        
        if "messages" in tables:
            # 检查 messages 表结构
            cursor.execute("PRAGMA table_info(messages);")
            cols = [c[1] for c in cursor.fetchall()]
            
            if "tokens" in cols and "model" in cols and "created_at" in cols:
                cursor.execute("""
                    SELECT created_at, model, tokens, role 
                    FROM messages 
                    WHERE tokens IS NOT NULL
                """)
                for row in cursor.fetchall():
                    tokens_data.append({
                        "created_at": row[0],
                        "model": row[1],
                        "tokens": row[2],
                        "role": row[3]
                    })
        
        conn.close()
        return tokens_data
    except Exception as e:
        return []

def generate_mock_data():
    """生成模拟数据（当没有真实数据时）"""
    today = datetime.now()
    agents = ["default", "maodou", "laomo", "afu", "xiaobao", "quant", "zhenglishi"]
    models = ["doubao-seed-2-0-pro-260215", "claude-3-5-sonnet-20241022", "gpt-4o", "deepseek-chat"]
    
    data = []
    
    # 生成过去 7 天的数据
    for day in range(7):
        date = today - timedelta(days=day)
        is_today = day == 0
        
        for agent in agents:
            # 每天每个 agent 有若干次调用
            num_calls = 3 if is_today else 2
            for _ in range(num_calls):
                model = models[hash(agent + str(day)) % len(models)]
                tokens = 5000 + hash(agent + model + str(day)) % 15000
                data.append({
                    "date": date.strftime("%Y-%m-%d"),
                    "agent": agent,
                    "model": model,
                    "tokens": tokens,
                    "created_at": date.isoformat()
                })
    
    return data

def analyze_data(data):
    """分析 tokens 数据"""
    today = datetime.now().strftime("%Y-%m-%d")
    
    # 按日期统计
    daily_totals = defaultdict(int)
    for item in data:
        date = item.get("date", item.get("created_at", "")[:10])
        daily_totals[date] += item.get("tokens", 0)
    
    # 今日消耗
    today_total = daily_totals.get(today, 0)
    
    # 7天均值
    seven_day_keys = sorted(daily_totals.keys())[:7]
    seven_day_avg = sum(daily_totals[d] for d in seven_day_keys) / len(seven_day_keys) if seven_day_keys else 0
    
    # 按 Agent 统计
    agent_totals = defaultdict(int)
    for item in data:
        agent = item.get("agent", "unknown")
        agent_totals[agent] += item.get("tokens", 0)
    
    top_agents = sorted(agent_totals.items(), key=lambda x: x[1], reverse=True)[:3]
    
    # 按模型统计
    model_totals = defaultdict(int)
    for item in data:
        model = item.get("model", "unknown")
        model_totals[model] += item.get("tokens", 0)
    
    model_dist = []
    total_tokens = sum(model_totals.values())
    for model, tokens in sorted(model_totals.items(), key=lambda x: x[1], reverse=True):
        pct = (tokens / total_tokens * 100) if total_tokens > 0 else 0
        model_dist.append((model, tokens, pct))
    
    # 检查告警（> 2x 均值）
    alert_ratio = today_total / seven_day_avg if seven_day_avg > 0 else 0
    has_alert = alert_ratio > 2
    
    return {
        "today": today,
        "today_total": today_total,
        "seven_day_avg": seven_day_avg,
        "alert_ratio": alert_ratio,
        "has_alert": has_alert,
        "top_agents": top_agents,
        "model_dist": model_dist,
        "total_tokens": total_tokens
    }

def format_report(result):
    """格式化报告"""
    lines = []
    lines.append(f"📊 Tokens 消耗日报 ({result['today']})")
    lines.append("")
    
    today_k = result['today_total'] / 1000
    avg_k = result['seven_day_avg'] / 1000
    lines.append(f"今日消耗: {today_k:.1f}K tokens")
    lines.append(f"7天均值: {avg_k:.1f}K tokens")
    
    if result['has_alert']:
        lines.append(f"⚠️  ALERT: 今日消耗是均值的 {result['alert_ratio']:.1f}x (阈值: 2x)")
    else:
        lines.append(f"比例: {result['alert_ratio']:.1f}x ✓ 正常")
    
    lines.append("")
    lines.append("🏆 Top 3 消费 Agent:")
    for i, (agent, tokens) in enumerate(result['top_agents'], 1):
        lines.append(f"  {i}. {agent}: {tokens/1000:.1f}K")
    
    lines.append("")
    lines.append("🤖 模型分布:")
    for model, tokens, pct in result['model_dist'][:3]:
        model_short = model.split("-")[0] if "-" in model else model[:12]
        lines.append(f"  • {model_short}: {pct:.0f}% ({tokens/1000:.0f}K)")
    
    lines.append("")
    csv_path = os.path.expanduser(f"~/.hermes/reports/tokens_{result['today']}.csv")
    lines.append(f"📁 CSV路径: {csv_path}")
    
    return "\n".join(lines)

def save_csv(data, result):
    """保存 CSV 文件"""
    report_dir = os.path.expanduser("~/.hermes/reports")
    os.makedirs(report_dir, exist_ok=True)
    
    csv_path = os.path.join(report_dir, f"tokens_{result['today']}.csv")
    
    with open(csv_path, 'w', encoding='utf-8') as f:
        f.write("date,agent,model,tokens\n")
        for item in data:
            date = item.get("date", item.get("created_at", "")[:10])
            f.write(f"{date},{item.get('agent','')},{item.get('model','')},{item.get('tokens',0)}\n")
    
    return csv_path

def main():
    # 尝试查找真实数据
    session_dbs = find_session_dbs()
    all_data = []
    
    for profile, db_path in session_dbs:
        tokens_data = get_tokens_from_db(db_path)
        for item in tokens_data:
            item["agent"] = profile
        all_data.extend(tokens_data)
    
    # 如果没有真实数据，使用模拟数据
    if not all_data:
        all_data = generate_mock_data()
        print("注意：使用模拟数据（未找到 session.db）")
    
    # 分析数据
    result = analyze_data(all_data)
    
    # 保存 CSV
    csv_path = save_csv(all_data, result)
    result["csv_path"] = csv_path
    
    # 输出报告
    print(format_report(result))
    
    # 同时保存 JSON 结果供后续使用
    report_dir = os.path.expanduser("~/.hermes/reports")
    json_path = os.path.join(report_dir, f"tokens_report_{result['today']}.json")
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
