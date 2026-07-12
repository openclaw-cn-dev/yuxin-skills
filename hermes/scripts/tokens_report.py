#!/usr/bin/env python3
"""
Tokens多维统计脚本
维度：按天 / 按Agent / 按模型 / 按来源（飞书/cron/cli）

输出：
  1. CSV文件（供导入飞书多维表格）
  2. 摘要报告（供每日推送）
"""
import sqlite3
import os
import sys
from datetime import datetime, timedelta
from collections import defaultdict

DB_PATH = os.path.expanduser("~/.hermes/state.db")
OUTPUT_DIR = os.path.expanduser("~/.hermes/cron/output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# cron job_id -> 可读名称映射
JOB_NAME_MAP = {
    "262419748f9b": "阿福-客服心跳",
    "066886014d67": "小宝-商务运营心跳",
    "260b7b982ab7": "老莫-知识库心跳",
    "9071b1bae756": "黑豆-行政财务心跳",
    "ac9bae2949bd": "毛豆-产品交付心跳",
    "4c849d264b0b": "宽博士-量化研究心跳",
    "5dc4d8915fff": "学习助手-知识库心跳",
    "832fbbcc29f6": "飞书云盘同步",
    "9a1cee1a301b": "玉芬-团队每小时汇报",
    "92ab47de8cf4": "玉芬-每日汇报",
    "3f109abd481b": "玉芬-主动巡视",
    "51a621334eea": "每日早间简报",
    "9e8ce3699207": "Claude Code版本检查",
    "0e97c1739a99": "每日重启通知",
    "5f33d4ff3ee1": "每日重启执行",
    "dfa9e16c0276": "技能扫描-全量",
    "02b7b4944cc8": "技能扫描-增量",
}

def query(sql, params=None):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute(sql, params or ())
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def extract_agent_name(session_id, source, user_id, title):
    """从session信息推断Agent名称"""
    if source == "feishu":
        if user_id == "b1b1da2b":
            return "华哥"
        elif user_id:
            return f"飞书用户({user_id[:8]})"
        return "飞书用户"
    elif source == "cron":
        # 从session_id提取cron job_id
        # 格式: cron_<job_id>_<timestamp>
        parts = session_id.split("_")
        if len(parts) >= 2:
            job_id = parts[1]
            if job_id in JOB_NAME_MAP:
                return JOB_NAME_MAP[job_id]
            return f"Cron({job_id[:8]})"
        return "Cron未知"
    elif source == "cli":
        return "CLI交互"
    return source or "未知"

def get_sessions(days_back=30):
    """获取近N天的会话数据"""
    start_ts = (datetime.now() - timedelta(days=days_back)).timestamp()
    return query("""
        SELECT id, source, user_id, model, billing_provider, title,
               input_tokens, output_tokens, cache_read_tokens, cache_write_tokens,
               reasoning_tokens, api_call_count, session_count,
               started_at, ended_at, end_reason
        FROM (
            SELECT id, source, user_id, model, billing_provider, title,
                   input_tokens, output_tokens, cache_read_tokens, cache_write_tokens,
                   reasoning_tokens, api_call_count, 1 as session_count,
                   started_at, ended_at, end_reason
            FROM sessions
            WHERE started_at >= ?
        )
        ORDER BY started_at DESC
    """, (start_ts,))

def format_num(n):
    if n is None: return 0
    if n >= 1_000_000: return f"{n/1_000_000:.2f}M"
    if n >= 1_000: return f"{n/1_000:.0f}K"
    return str(n)

# ────────────────────────────────────────────────────────────────
# 维度1：按天汇总
# ────────────────────────────────────────────────────────────────
def report_by_day(sessions):
    sql = """
    SELECT
        date(started_at, 'unixepoch', 'localtime') as day,
        SUM(input_tokens) as input_tokens,
        SUM(output_tokens) as output_tokens,
        SUM(cache_read_tokens) as cache_read,
        SUM(cache_write_tokens) as cache_write,
        COUNT(*) as session_count,
        SUM(api_call_count) as api_calls
    FROM sessions WHERE started_at >= ?
    GROUP BY day ORDER BY day DESC
    """
    start_ts = (datetime.now() - timedelta(days=30)).timestamp()
    rows = query(sql, (start_ts,))
    return rows

# ────────────────────────────────────────────────────────────────
# 维度2：按Agent/来源汇总
# ────────────────────────────────────────────────────────────────
def report_by_agent(sessions):
    stats = defaultdict(lambda: {
        "input": 0, "output": 0, "cache_read": 0, "cache_write": 0,
        "sessions": 0, "api_calls": 0
    })
    for s in sessions:
        agent = extract_agent_name(s['id'], s['source'], s.get('user_id', ''), s.get('title', ''))
        st = stats[agent]
        st['input'] += s['input_tokens'] or 0
        st['output'] += s['output_tokens'] or 0
        st['cache_read'] += s['cache_read_tokens'] or 0
        st['cache_write'] += s['cache_write_tokens'] or 0
        st['sessions'] += 1
        st['api_calls'] += s['api_call_count'] or 0

    # 排序：总tokens降序
    result = sorted(stats.items(), key=lambda x: x[1]['input']+x[1]['output'], reverse=True)
    return [{"agent": k, **v, "total": v['input']+v['output']} for k, v in result]

# ────────────────────────────────────────────────────────────────
# 维度3：按模型/供应商汇总
# ────────────────────────────────────────────────────────────────
def report_by_model(sessions):
    stats = defaultdict(lambda: {
        "input": 0, "output": 0, "cache_read": 0, "cache_write": 0,
        "sessions": 0, "provider": ""
    })
    for s in sessions:
        key = f"{s['model'] or 'unknown'} ({s['billing_provider'] or 'unknown'})"
        st = stats[key]
        st['input'] += s['input_tokens'] or 0
        st['output'] += s['output_tokens'] or 0
        st['cache_read'] += s['cache_read_tokens'] or 0
        st['cache_write'] += s['cache_write_tokens'] or 0
        st['sessions'] += 1
        st['provider'] = s['billing_provider'] or 'unknown'

    result = sorted(stats.items(), key=lambda x: x[1]['input']+x[1]['output'], reverse=True)
    return [{"model": k, **v, "total": v['input']+v['output']} for k, v in result]

# ────────────────────────────────────────────────────────────────
# 输出CSV
# ────────────────────────────────────────────────────────────────
def write_csvs(sessions):
    today = datetime.now().strftime("%Y%m%d")

    # 维度1：按天
    by_day = report_by_day(sessions)
    path_by_day = os.path.join(OUTPUT_DIR, f"tokens_by_day_{today}.csv")
    with open(path_by_day, "w", encoding="utf-8") as f:
        f.write("日期,输入Tokens,输出Tokens,Cache读,Cache写,总会话数,API调用数,总Tokens\n")
        for r in by_day:
            total = r['input_tokens'] + r['output_tokens']
            f.write(f"{r['day']},{r['input_tokens']},{r['output_tokens']},{r['cache_read']},{r['cache_write']},{r['session_count']},{r['api_calls'] or 0},{total}\n")

    # 维度2：按Agent
    by_agent = report_by_agent(sessions)
    path_by_agent = os.path.join(OUTPUT_DIR, f"tokens_by_agent_{today}.csv")
    with open(path_by_agent, "w", encoding="utf-8") as f:
        f.write("Agent,输入Tokens,输出Tokens,Cache读,Cache写,总会话数,API调用数,总Tokens\n")
        for r in by_agent:
            f.write(f"{r['agent']},{r['input']},{r['output']},{r['cache_read']},{r['cache_write']},{r['sessions']},{r['api_calls']},{r['total']}\n")

    # 维度3：按模型
    by_model = report_by_model(sessions)
    path_by_model = os.path.join(OUTPUT_DIR, f"tokens_by_model_{today}.csv")
    with open(path_by_model, "w", encoding="utf-8") as f:
        f.write("模型(供应商),输入Tokens,输出Tokens,Cache读,Cache写,总会话数,总Tokens\n")
        for r in by_model:
            f.write(f"{r['model']},{r['input']},{r['output']},{r['cache_read']},{r['cache_write']},{r['sessions']},{r['total']}\n")

    # 原始明细
    path_detail = os.path.join(OUTPUT_DIR, f"tokens_detail_{today}.csv")
    with open(path_detail, "w", encoding="utf-8") as f:
        f.write("会话ID,来源,用户ID,Agent,模型,供应商,标题,输入Tokens,输出Tokens,Cache读,Cache写,会话数,API调用,开始时间,结束原因\n")
        for s in sessions:
            agent = extract_agent_name(s['id'], s['source'], s.get('user_id', ''), s.get('title', ''))
            start = datetime.fromtimestamp(s['started_at']).strftime("%Y-%m-%d %H:%M") if s['started_at'] else ""
            f.write(f"{s['id']},{s['source']},{s.get('user_id','')},{agent},{s['model']},{s['billing_provider']},{s.get('title','')},{s['input_tokens']},{s['output_tokens']},{s['cache_read_tokens']},{s['cache_write_tokens']},{s['api_call_count']},{start},{s['end_reason']}\n")

    return {
        "by_day": path_by_day,
        "by_agent": path_by_agent,
        "by_model": path_by_model,
        "detail": path_detail
    }

def main():
    sessions = get_sessions(30)
    csv_paths = write_csvs(sessions)

    today_str = datetime.now().strftime("%Y-%m-%d")

    # 生成飞书消息摘要
    by_agent = report_by_agent(sessions)
    by_model = report_by_model(sessions)
    by_day = report_by_day(sessions)

    # 总计
    total_input = sum(s['input_tokens'] or 0 for s in sessions)
    total_output = sum(s['output_tokens'] or 0 for s in sessions)
    total_cache_r = sum(s['cache_read_tokens'] or 0 for s in sessions)
    total_cache_w = sum(s['cache_write_tokens'] or 0 for s in sessions)
    total_sessions = len(sessions)

    # 今日数据
    today = datetime.now().strftime("%Y-%m-%d")
    today_data = next((r for r in by_day if r['day'] == today), None)

    # 7天均值
    past_7d = [r for r in by_day if r['day'] != today][:7]
    avg_7d = sum(r['input_tokens'] + r['output_tokens'] for r in past_7d) / max(len(past_7d), 1)

    lines = [
        f"📊 **Tokens 30日多维统计**（{today_str}）",
        f"",
        f"**30日总览**",
        f"  输入: {format_num(total_input)} | 输出: {format_num(total_output)} | 会话: {total_sessions}",
        f"  Cache读: {format_num(total_cache_r)} | Cache写: {format_num(total_cache_w)}",
        f"",
        f"**今日**（{today}）",
    ]

    if today_data:
        today_total = today_data['input_tokens'] + today_data['output_tokens']
        ratio = today_total / avg_7d if avg_7d > 0 else 0
        emoji = "🔴" if ratio > 2 else ("🟡" if ratio > 1 else "🟢")
        lines.append(f"  {emoji} 输入: {format_num(today_data['input_tokens'])} | 输出: {format_num(today_data['output_tokens'])} | 会话: {today_data['session_count']}")
        lines.append(f"  7天均值: {format_num(avg_7d)} | 今日比例: {ratio:.1f}x")
    else:
        lines.append(f"  ℹ️ 今日暂无会话")

    lines.append(f"")
    lines.append(f"**Top 5 Agent**（30日）")
    for r in by_agent[:5]:
        pct = r['total'] / (total_input + total_output) * 100 if (total_input + total_output) > 0 else 0
        lines.append(f"  {r['agent']}: {format_num(r['total'])} ({pct:.1f}%)")

    lines.append(f"")
    lines.append(f"**按模型分布**（30日）")
    for r in by_model[:4]:
        pct = r['total'] / (total_input + total_output) * 100 if (total_input + total_output) > 0 else 0
        lines.append(f"  {r['model']}: {format_num(r['total'])} ({pct:.1f}%)")

    lines.append(f"")
    lines.append(f"📁 详细CSV已生成（导入飞书多维表格用）：")
    for name, path in csv_paths.items():
        lines.append(f"  • `{name}` → {path}")

    print("\n".join(lines))

if __name__ == "__main__":
    main()
