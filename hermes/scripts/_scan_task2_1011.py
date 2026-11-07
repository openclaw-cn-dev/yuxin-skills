#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 玉芬管理进化扫描 2026-10-11 任务队列详细 dump
import sqlite3, shutil, os, datetime, tempfile

NOW = datetime.datetime.now().astimezone()
def d_iso(s):
    try:
        t = datetime.datetime.fromisoformat(s)
        return round((NOW - t).total_seconds()/86400.0, 1)
    except: return None
def d_epoch(e):
    try:
        t = datetime.datetime.fromtimestamp(float(e)).astimezone()
        return round((NOW - t).total_seconds()/86400.0, 1)
    except: return None

print("="*80)
print("TASKS.DB (业务池) — 全部 43 条按 status 分组")
print("="*80)
con = sqlite3.connect("/Users/hua/.hermes/tasks.db")
con.row_factory = sqlite3.Row
cur = con.cursor()
rows = cur.execute("SELECT * FROM tasks ORDER BY status, priority, updated_at DESC").fetchall()
from collections import defaultdict
by_status = defaultdict(list)
for r in rows:
    by_status[r['status']].append(r)
for st in sorted(by_status):
    print(f"\n### status={st} ({len(by_status[st])})")
    for r in by_status[st]:
        age = d_iso(r['updated_at'])
        created = d_iso(r['created_at'])
        print(f"  id={r['id']:<3} prio={r['priority']!r:<8} assigned={r['assigned_to']!r:<12} upd {age}d ago / created {created}d ago | {r['title'][:60]}")
con.close()

print("\n" + "="*80)
print("KANBAN.DB (看板池) — 36 条按 status 分组")
print("="*80)
tmp = tempfile.mktemp(suffix='.db')
shutil.copy2("/Users/hua/.hermes/kanban.db", tmp)
for ext in ['-wal','-shm']:
    p = "/Users/hua/.hermes/kanban.db"+ext
    if os.path.exists(p): shutil.copy2(p, tmp+ext)
con = sqlite3.connect(tmp)
con.row_factory = sqlite3.Row
cur = con.cursor()
rows = cur.execute("SELECT * FROM tasks ORDER BY status, priority, created_at DESC").fetchall()
by_status = defaultdict(list)
for r in rows:
    by_status[r['status']].append(r)
for st in sorted(by_status):
    print(f"\n### status={st} ({len(by_status[st])})")
    for r in by_status[st]:
        created = d_epoch(r['created_at'])
        started = d_epoch(r['started_at'])
        print(f"  id={r['id']:<3} prio={r['priority']!r} assignee={r['assignee']!r:<14} created {created}d ago / started {started} | {r['title'][:55]}")
con.close()
for ext in ['','-wal','-shm']:
    try: os.remove(tmp+ext)
    except: pass
