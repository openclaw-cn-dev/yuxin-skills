#!/usr/bin/env python3
"""修复僵尸 cron 会话：48h 前开始但 ended_at 为 NULL 的，补 ended_at=started_at+3600"""
import sqlite3, time, sys

for db in sys.argv[1:]:
    con = sqlite3.connect(db, timeout=120)
    cutoff = time.time() - 48 * 3600
    n = con.execute(
        "SELECT COUNT(*) FROM sessions WHERE source='cron' AND ended_at IS NULL AND started_at < ?",
        (cutoff,)).fetchone()[0]
    with con:
        con.execute(
            "UPDATE sessions SET ended_at = started_at + 3600 "
            "WHERE source='cron' AND ended_at IS NULL AND started_at < ?",
            (cutoff,))
    print(f"[{db}] 修正僵尸 cron 会话: {n} 个")
    con.close()
