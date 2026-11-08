#!/usr/bin/env python3
"""
Tokens 多维统计报告脚本
统计各 Agent(profile) 的 tokens 消耗、模型分布等。

数据源：各 profile 的 state.db 中 sessions 表
  - 默认 profile:   ~/.hermes/state.db
  - 其它 profile:   ~/.hermes/profiles/<name>/state.db

tokens 口径：input + output + cache_read + cache_write + reasoning
"""

import sqlite3
import os
import json
from datetime import datetime, timedelta, timezone
from collections import defaultdict

HOME = os.path.expanduser("~")
HERMES_HOME = os.path.join(HOME, ".hermes")


def find_state_dbs():
    """查找所有 profile 的 state.db，返回 [(agent, db_path)]"""
    dbs = []

    # 默认 profile
    default_db = os.path.join(HERMES_HOME, "state.db")
    if os.path.exists(default_db):
        dbs.append(("default", default_db))

    # 其它 profile
    profiles_dir = os.path.join(HERMES_HOME, "profiles")
    if os.path.exists(profiles_dir):
        for profile in sorted(os.listdir(profiles_dir)):
            if profile == "default":
                continue
            db = os.path.join(profiles_dir, profile, "state.db")
            if os.path.exists(db):
                dbs.append((profile, db))

    return dbs


def get_sessions_from_db(db_path, since_ts):
    """提取 sessions 表中的 token 数据"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT started_at, model,
                   input_tokens, output_tokens, cache_read_tokens,
                   cache_write_tokens, reasoning_tokens
            FROM sessions
            WHERE started_at IS NOT NULL AND started_at > ?
            """,
            (since_ts,),
        )
        rows = cursor.fetchall()
        conn.close()

        data = []
        for started_at, model, inp, out, cr, cw, reason in rows:
            total = sum(x for x in (inp, out, cr, cw, reason) if x)
            if total <= 0:
                continue
            data.append({
                "started_at": started_at,
                "model": model or "unknown",
                "tokens": total,
            })
        return data
    except Exception:
        return []


def local_day(ts):
    """unix 时间戳 -> 本地日期字符串"""
    return datetime.fromtimestamp(ts).strftime("%Y-%m-%d")


def main():
    today = datetime.now()
    today_str = today.strftime("%Y-%m-%d")
    since_ts = (today - timedelta(days=7)).timestamp()

    all_data = []
    for agent, db_path in find_state_dbs():
        for item in get_sessions_from_db(db_path, since_ts):
            item["agent"] = agent
            item["date"] = local_day(item["started_at"])
            all_data.append(item)

    if not all_data:
        print("⚠️ 未找到任何 token 数据（state.db 无 sessions 记录）")
        return

    # 按日期聚合
    daily_totals = defaultdict(int)
    for item in all_data:
        daily_totals[item["date"]] += item["tokens"]

    today_total = daily_totals.get(today_str, 0)

    # 7 天均值（最近 7 个自然日，含今天）
    seven_days = sorted(daily_totals.keys())[-7:]
    seven_avg = sum(daily_totals[d] for d in seven_days) / len(seven_days) if seven_days else 0

    # 按 Agent 聚合（仅今日）
    agent_today = defaultdict(int)
    # 按 Agent 聚合（7 天）
    agent_7d = defaultdict(int)
    for item in all_data:
        agent_7d[item["agent"]] += item["tokens"]
        if item["date"] == today_str:
            agent_today[item["agent"]] += item["tokens"]

    top_agents = sorted(agent_today.items(), key=lambda x: x[1], reverse=True)[:3]
    if not top_agents:  # 今日无数据则回退到 7 天
        top_agents = sorted(agent_7d.items(), key=lambda x: x[1], reverse=True)[:3]

    # 按模型聚合（今日）
    model_today = defaultdict(int)
    model_7d = defaultdict(int)
    for item in all_data:
        model_7d[item["model"]] += item["tokens"]
        if item["date"] == today_str:
            model_today[item["model"]] += item["tokens"]

    total_today = sum(model_today.values()) or sum(model_7d.values())
    model_dist = []
    base_models = model_today if model_today else model_7d
    for model, tokens in sorted(base_models.items(), key=lambda x: x[1], reverse=True):
        pct = (tokens / total_today * 100) if total_today > 0 else 0
        model_dist.append((model, tokens, pct))

    # 告警（今日 > 2x 7天均值）
    alert_ratio = today_total / seven_avg if seven_avg > 0 else 0
    has_alert = alert_ratio > 2

    result = {
        "today": today_str,
        "today_total": today_total,
        "seven_day_avg": seven_avg,
        "alert_ratio": alert_ratio,
        "has_alert": has_alert,
        "top_agents": top_agents,
        "model_dist": model_dist,
    }

    # 保存 CSV（date,agent,model,tokens 聚合，便于飞书多维表格导入）
    report_dir = os.path.join(HERMES_HOME, "reports")
    os.makedirs(report_dir, exist_ok=True)
    csv_path = os.path.join(report_dir, f"tokens_{today_str}.csv")

    # 按 (date, agent, model) 聚合
    agg = defaultdict(int)
    for item in all_data:
        agg[(item["date"], item["agent"], item["model"])] += item["tokens"]

    with open(csv_path, "w", encoding="utf-8") as f:
        f.write("date,agent,model,tokens\n")
        for (d, agent, model), tokens in sorted(agg.items()):
            f.write(f"{d},{agent},{model},{tokens}\n")

    result["csv_path"] = csv_path

    # JSON 结果
    json_path = os.path.join(report_dir, f"tokens_report_{today_str}.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2, default=str)

    # 输出报告
    print(format_report(result))


def _short_model(model):
    if "deepseek" in model:
        if "flash" in model:
            return "deepseek-flash"
        return "deepseek"
    if "minimax" in model.lower() or model.lower().startswith("minimax"):
        return "minimax"
    if "claude" in model.lower():
        return "claude"
    if "gpt" in model.lower():
        return "gpt"
    if "qwen" in model.lower():
        return "qwen"
    if "glm" in model.lower():
        return "glm"
    if "doubao" in model.lower():
        return "doubao"
    return model[:16]


def format_report(result):
    lines = []
    lines.append(f"📊 Tokens 消耗日报 ({result['today']})")
    lines.append("")
    today_k = result["today_total"] / 1000
    avg_k = result["seven_day_avg"] / 1000
    lines.append(f"今日消耗: {today_k:,.0f}K tokens")
    lines.append(f"7天均值: {avg_k:,.0f}K tokens")
    if result["has_alert"]:
        lines.append(f"⚠️ ALERT: 今日是均值的 {result['alert_ratio']:.1f}x (阈值 2x)")
    else:
        lines.append(f"比例: {result['alert_ratio']:.1f}x ✓ 正常")
    lines.append("")
    lines.append("🏆 Top 3 消费 Agent (今日):")
    for i, (agent, tokens) in enumerate(result["top_agents"], 1):
        lines.append(f"  {i}. {agent}: {tokens/1000:,.0f}K")
    lines.append("")
    lines.append("🤖 模型分布 (今日):")
    for model, tokens, pct in result["model_dist"][:5]:
        lines.append(f"  • {_short_model(model)}: {pct:.0f}% ({tokens/1000:,.0f}K)")
    lines.append("")
    lines.append(f"📁 CSV路径: {result['csv_path']}")
    return "\n".join(lines)


if __name__ == "__main__":
    main()
