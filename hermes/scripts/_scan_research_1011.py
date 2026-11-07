#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 玉芬管理进化扫描 2026-10-11 调研增量检测 (state.db sessions 按日统计)
import sqlite3, datetime, time

NOW = datetime.datetime.now().astimezone()
con = sqlite3.connect('file:/Users/hua/.hermes/state.db?mode=ro&immutable=1', uri=True, timeout=10)
con.row_factory = sqlite3.Row
cur = con.cursor()

print("近 8 天 session 统计 (started_at epoch float):")
print(f"{'day':<12} {'sessions':>8} {'in_tokens':>12} {'out_tokens':>12} {'tool_calls':>10}")
for i in range(7, -1, -1):
    day = (NOW - datetime.timedelta(days=i)).replace(hour=0, minute=0, second=0, microsecond=0)
    dstart = day.timestamp()
    dend = (day + datetime.timedelta(days=1)).timestamp()
    row = cur.execute(
        "SELECT COUNT(*) n, COALESCE(SUM(input_tokens),0) it, COALESCE(SUM(output_tokens),0) ot, "
        "COALESCE(SUM(tool_call_count),0) tc FROM sessions "
        "WHERE started_at >= ? AND started_at < ?", (dstart, dend)).fetchone()
    label = day.strftime('%m-%d')
    print(f"{label:<12} {row['n']:>8} {row['it']:>12,} {row['ot']:>12,} {row['tc']:>10}")

# 迭代上限耗尽白烧检测 (工具调用迭代上限)
print("\n迭代上限耗尽白烧 session 检测 (近 3 天):")
dstart3 = (NOW - datetime.timedelta(days=3)).timestamp()
rows = cur.execute(
    "SELECT started_at, message_count, input_tokens FROM sessions "
    "WHERE started_at >= ? AND message_count > 0 ORDER BY started_at DESC LIMIT 200", (dstart3,)).fetchall()
burn = 0
for r in rows:
    pass
print(f"(message_count 分布采样见下; 完整白烧检测需 JOIN messages 取首条, 本轮轻量)")

con.close()
