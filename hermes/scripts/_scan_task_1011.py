#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 玉芬管理进化扫描 2026-10-11 任务队列 (tasks.db + kanban.db)
import sqlite3, shutil, os, datetime, tempfile

NOW = datetime.datetime.now().astimezone()

def days_since_iso(s):
    try:
        t = datetime.datetime.fromisoformat(s)
        return (NOW - t).total_seconds() / 86400.0
    except Exception:
        return None

def days_since_epoch(e):
    try:
        t = datetime.datetime.fromtimestamp(float(e)).astimezone()
        return (NOW - t).total_seconds() / 86400.0
    except Exception:
        return None

print("="*70)
print("TASKS.DB (~/.hermes/tasks.db)")
print("="*70)
con = sqlite3.connect("/Users/hua/.hermes/tasks.db")
con.row_factory = sqlite3.Row
cur = con.cursor()
tables = [r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table'")]
print("tables:", tables)
for t in tables:
    if t.startswith('sqlite_'): continue
    cols = [c[1] for c in cur.execute(f"PRAGMA table_info({t})")]
    print(f"\n--- table {t} cols={cols} ---")
    try:
        rows = cur.execute(f"SELECT * FROM {t}").fetchall()
        print(f"count={len(rows)}")
    except Exception as e:
        print("err", e)
con.close()

print("\n" + "="*70)
print("KANBAN.DB (~/.hermes/kanban.db) via copy-to-tmp")
print("="*70)
tmp = tempfile.mktemp(suffix='.db')
shutil.copy2("/Users/hua/.hermes/kanban.db", tmp)
# also copy -wal/-shm if present
for ext in ['-wal','-shm']:
    p = "/Users/hua/.hermes/kanban.db"+ext
    if os.path.exists(p):
        shutil.copy2(p, tmp+ext)
con = sqlite3.connect(tmp)
con.row_factory = sqlite3.Row
cur = con.cursor()
tables = [r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table'")]
print("tables:", tables)
for t in tables:
    if t.startswith('sqlite_'): continue
    cols = [c[1] for c in cur.execute(f"PRAGMA table_info({t})")]
    print(f"\n--- table {t} cols={cols} ---")
    try:
        rows = cur.execute(f"SELECT * FROM {t}").fetchall()
        print(f"count={len(rows)}")
    except Exception as e:
        print("err", e)
con.close()
for ext in ['','-wal','-shm']:
    try: os.remove(tmp+ext)
    except: pass
