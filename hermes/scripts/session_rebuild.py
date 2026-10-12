#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""rebuild FTS + VACUUM，带重试。用于 DELETE 后回收 FTS tombstone 空间。
v2 修正：VACUUM 不能在 WAL 模式下跑，先切 DELETE 再 VACUUM，完了恢复 WAL。"""
import sqlite3, os, sys, time, argparse

ap = argparse.ArgumentParser()
ap.add_argument("--db", required=True)
args = ap.parse_args()

db_path = os.path.expanduser(args.db)
print(f"[{db_path}] 开始 rebuild FTS + VACUUM", flush=True)
before = os.path.getsize(db_path)
print(f"  优化前 {before/1e9:.2f} GB", flush=True)

con = sqlite3.connect(db_path, timeout=300)
con.execute("PRAGMA busy_timeout=300000")

# 1. WAL checkpoint（先清 WAL，确保无未落盘数据）
try:
    con.execute("PRAGMA wal_checkpoint(TRUNCATE)")
    print("  wal_checkpoint OK", flush=True)
except Exception as e:
    print(f"  wal_checkpoint 跳过: {e}", flush=True)

# 2. rebuild 两个 FTS 表（带重试，每次都 commit）
for tbl in ("messages_fts", "messages_fts_trigram"):
    for attempt in range(3):
        try:
            con.execute(f"INSERT INTO {tbl}({tbl}) VALUES('rebuild')")
            con.commit()
            print(f"  rebuild {tbl} OK", flush=True)
            break
        except Exception as e:
            print(f"  rebuild {tbl} 重试{attempt}: {e}", flush=True)
            time.sleep(3)

# 3. 切回 DELETE 模式（VACUUM 不能在 WAL 下跑）
try:
    con.execute("PRAGMA journal_mode=DELETE")
    con.commit()
    print("  journal_mode=DELETE OK", flush=True)
except Exception as e:
    print(f"  journal_mode 切换失败: {e}", flush=True)

# 4. VACUUM（带重试）
for attempt in range(5):
    try:
        con.execute("VACUUM")
        print("  VACUUM 成功", flush=True)
        break
    except Exception as e:
        print(f"  VACUUM 重试{attempt}: {e}", flush=True)
        time.sleep(5)

# 5. 恢复 WAL 模式（Hermes gateway 需要）
try:
    con.execute("PRAGMA journal_mode=WAL")
    con.commit()
    print("  恢复 journal_mode=WAL OK", flush=True)
except Exception as e:
    print(f"  恢复 WAL 失败: {e}", flush=True)

con.close()
after = os.path.getsize(db_path)
print(f"  优化后 {after/1e9:.2f} GB，回收 {(before-after)/1e9:.2f} GB", flush=True)
