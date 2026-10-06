#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""sessions 按 epoch started_at 统计 + kanban.db 只读重试"""
import sqlite3, datetime, os, shutil, tempfile

NOWDT = datetime.datetime.now()
OUT = []
P = OUT.append

# sessions: started_at is epoch float
try:
    # copy to temp for safe read (WAL mode issue workaround)
    tmp = tempfile.mktemp(suffix=".db")
    shutil.copy2("/Users/hua/.hermes/state.db", tmp)
    # also copy wal/shm if exist
    for ext in ["-wal", "-shm"]:
        if os.path.exists("/Users/hua/.hermes/state.db" + ext):
            shutil.copy2("/Users/hua/.hermes/state.db" + ext, tmp + ext)
    con = sqlite3.connect(tmp)
    cur = con.cursor()
    for d in range(5, -1, -1):
        day_start = (NOWDT - datetime.timedelta(days=d)).replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + datetime.timedelta(days=1)
        ts1, ts2 = day_start.timestamp(), day_end.timestamp()
        cur.execute("SELECT COUNT(*), COALESCE(SUM(input_tokens),0), COALESCE(SUM(output_tokens),0) FROM sessions WHERE started_at >= ? AND started_at < ?", (ts1, ts2))
        cnt, it, ot = cur.fetchone()
        P("DAY %s sessions=%d in=%d out=%d" % (day_start.strftime("%Y-%m-%d"), cnt, it, ot))
    for d in [1, 0]:
        day_start = (NOWDT - datetime.timedelta(days=d)).replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + datetime.timedelta(days=1)
        cur.execute("SELECT title, input_tokens FROM sessions WHERE started_at >= ? AND started_at < ? ORDER BY input_tokens DESC LIMIT 3", (day_start.timestamp(), day_end.timestamp()))
        for t, it in cur.fetchall():
            P("TOP %s in=%s | %s" % (day_start.strftime("%m-%d"), it, str(t)[:60]))
    con.close()
    os.remove(tmp)
except Exception as e:
    P("state.db copy err: %s" % e)

# kanban: copy-read
try:
    tmp2 = tempfile.mktemp(suffix=".db")
    shutil.copy2("/Users/hua/.hermes/kanban.db", tmp2)
    for ext in ["-wal", "-shm"]:
        if os.path.exists("/Users/hua/.hermes/kanban.db" + ext):
            shutil.copy2("/Users/hua/.hermes/kanban.db" + ext, tmp2 + ext)
    con = sqlite3.connect(tmp2)
    cur = con.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    P("kanban_tables=%s" % [r[0] for r in cur.fetchall()])
    try:
        cur.execute("SELECT id, title, status, priority, assignee, created_at, updated_at FROM tasks ORDER BY updated_at DESC")
        for r in cur.fetchall():
            tid, title, status, prio, asg, ca, ua = r
            age = ""
            if ua:
                try:
                    ua_dt = datetime.datetime.fromtimestamp(ua) if isinstance(ua, (int, float)) else datetime.datetime.fromisoformat(str(ua))
                    age = "%.1fd" % ((NOWDT - ua_dt).total_seconds() / 86400)
                except Exception:
                    age = "?"
            P("KB id=%s [%s] prio=%s asg=%s upd(%s) %s" % (tid, status, prio, asg, age, str(title)[:55]))
    except Exception as e:
        P("kanban tasks err: %s" % e)
    con.close()
    os.remove(tmp2)
except Exception as e:
    P("kanban copy err: %s" % e)

print("\n".join(OUT))
