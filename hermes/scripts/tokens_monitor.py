#!/usr/bin/env python3
"""
Tokens消耗监控脚本
统计 Hermes 的 tokens 使用情况，支持每日/每周/阈值告警
"""
import sqlite3
import sys
from datetime import datetime, timedelta

DB_PATH = "/Users/hua/.hermes/state.db"
ALERT_MULTIPLE = 2.0  # 当天消耗超过7天均值的2倍则告警

def query_tokens(sql, params=None):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute(sql, params or ())
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_daily_tokens(days_back=1):
    """获取指定天数的每日消耗"""
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    start_ts = (today_start - timedelta(days=days_back-1)).timestamp()

    rows = query_tokens("""
        SELECT
            date(started_at, 'unixepoch', 'localtime') as day,
            SUM(input_tokens) as input_tokens,
            SUM(output_tokens) as output_tokens,
            SUM(cache_read_tokens) as cache_read,
            SUM(cache_write_tokens) as cache_write,
            SUM(reasoning_tokens) as reasoning_tokens,
            COUNT(*) as session_count,
            SUM(api_call_count) as api_calls
        FROM sessions
        WHERE started_at >= ?
        GROUP BY date(started_at, 'unixepoch', 'localtime')
        ORDER BY day DESC
    """, (start_ts,))
    return rows

def format_num(n):
    if n >= 1_000_000:
        return f"{n/1_000_000:.1f}M"
    elif n >= 1_000:
        return f"{n/1_000:.0f}K"
    return str(n)

def main():
    today = datetime.now().strftime("%Y-%m-%d")
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

    # 今日数据
    today_rows = get_daily_tokens(1)
    today_data = next((r for r in today_rows if r['day'] == today), None)

    # 近7天数据
    days_7 = get_daily_tokens(7)
    today_7d = next((r for r in days_7 if r['day'] == today), None)

    # 近30天数据
    days_30 = get_daily_tokens(30)

    # 计算7天均值
    if len(days_7) >= 2:
        # 排除今天算均值
        past_7d = [r for r in days_7 if r['day'] != today]
        if past_7d:
            avg_input = sum(r['input_tokens'] for r in past_7d) / len(past_7d)
            avg_output = sum(r['output_tokens'] for r in past_7d) / len(past_7d)
            avg_total = sum(r['input_tokens'] + r['output_tokens'] for r in past_7d) / len(past_7d)
        else:
            avg_input = avg_output = avg_total = 0
    else:
        avg_input = avg_output = avg_total = 0

    # 输出报告
    lines = [f"📊 **Tokens消耗监控** {today}"]
    lines.append("")

    # 近7天趋势
    lines.append(f"**近7天趋势**（{len(days_7)}天）")
    for r in days_7[:7]:
        marker = "◀今天" if r['day'] == today else "  "
        total = r['input_tokens'] + r['output_tokens']
        lines.append(f"  {marker} {r['day']}  输入:{format_num(r['input_tokens'])}  输出:{format_num(r['output_tokens'])}  会话:{r['session_count']}")

    lines.append("")

    # 今日 vs 7天均值
    if today_7d:
        today_total = today_7d['input_tokens'] + today_7d['output_tokens']
        if avg_total > 0:
            ratio = today_total / avg_total
            emoji = "🔴" if ratio > ALERT_MULTIPLE else ("🟡" if ratio > 1.5 else "🟢")
            lines.append(f"{emoji} **今日消耗**: {format_num(today_total)}（7天均值: {format_num(avg_total)}，比例: {ratio:.1f}x）")
        else:
            lines.append(f"🟢 **今日消耗**: {format_num(today_total)}（尚无7天均值对比）")
    else:
        lines.append("ℹ️ 今日尚无会话记录")

    lines.append("")
    lines.append("**30天汇总**")
    total_30d_input = sum(r['input_tokens'] for r in days_30)
    total_30d_output = sum(r['output_tokens'] for r in days_30)
    total_30d_cache_r = sum(r['cache_read'] for r in days_30)
    total_30d_cache_w = sum(r['cache_write'] for r in days_30)
    lines.append(f"  输入: {format_num(total_30d_input)} | 输出: {format_num(total_30d_output)} | Cache读: {format_num(total_30d_cache_r)} | Cache写: {format_num(total_30d_cache_w)}")
    lines.append(f"  会话总数: {sum(r['session_count'] for r in days_30)}")

    print("\n".join(lines))

    # 告警检测
    if today_7d and avg_total > 0:
        today_total = today_7d['input_tokens'] + today_7d['output_tokens']
        if today_total > avg_total * ALERT_MULTIPLE:
            print(f"\n🚨 [告警] 今日消耗 {format_num(today_total)} 超过7天均值 {format_num(avg_total)} 的 {ALERT_MULTIPLE}x 阈值！")

if __name__ == "__main__":
    main()
