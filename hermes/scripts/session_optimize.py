#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""只做 optimize FTS + VACUUM，不删数据。用于补跑已删除但 FTS 空间未回收的库。"""
import sqlite3, os, argparse

ap = argparse.ArgumentParser()
ap.add_argument("--db", required=True)
args = ap.parse_args()

db_path = os.path.expanduser(args.db)
con = sqlite3.connect(db_path, timeout=120)
con.execute("PRAGMA journal_mode=WAL")
before = os.path.getsize(db_path)
print(f"[{db_path}] 优化前 {before/1e9:.2f} GB")

for tbl in ("messages_fts", "messages_fts_trigram"):
    try:
        con.execute(f"INSERT INTO {tbl}({tbl}) VALUES('optimize')")
        print(f"  optimize {tbl} OK")
    except Exception as e:
        print(f"  optimize {tbl} 跳过: {e}")

con.execute("PRAGMA wal_checkpoint(TRUNCATE)")
print("  VACUUM 中...")
con.execute("VACUUM")

after = os.path.getsize(db_path)
con.close()
print(f"优化后 {after/1e9:.2f} GB，回收 {(before-after)/1e9:.2f} GB")
