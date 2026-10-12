#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""停 gateway 后执行：prune cron 会话 + 已归档会话 + VACUUM 回收空间。

用法:
  python3 session_prune.py --db <db> --archive <归档jsonl>   # 删 cron + 已归档白名单
  python3 session_prune.py --db <db> --cron-only              # 只删 cron
  python3 session_prune.py --db <db> --dry-run                # 只统计不删
"""
import sqlite3, json, os, argparse


def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def load_archived(archive_path):
    ids = set()
    if archive_path and os.path.exists(archive_path):
        for line in open(archive_path, encoding="utf-8"):
            line = line.strip()
            if line:
                try:
                    ids.add(json.loads(line)["session_id"])
                except Exception:
                    pass
    return ids


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", required=True)
    ap.add_argument("--archive", default="")
    ap.add_argument("--cron-only", action="store_true")
    ap.add_argument("--cron-days", type=int, default=30,
                    help="只删 started_at 早于 N 天前的 cron（0=删全部 ended cron）")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    db_path = os.path.expanduser(args.db)
    con = sqlite3.connect(db_path, timeout=120)
    con.execute("PRAGMA journal_mode=WAL")

    # cron 删除的 SQL 条件
    if args.cron_days > 0:
        import time
        cutoff = time.time() - args.cron_days * 86400
        cron_cond = "source='cron' AND ended_at IS NOT NULL AND started_at < ?"
        cron_params = [cutoff]
    else:
        cron_cond = "source='cron' AND ended_at IS NOT NULL"
        cron_params = []

    # 统计
    cron_rows = con.execute(
        f"SELECT COUNT(*), COALESCE(SUM(message_count),0) FROM sessions WHERE {cron_cond}",
        cron_params).fetchone()
    arch_ids = set() if args.cron_only else load_archived(args.archive)
    arch_in_db = set()
    if arch_ids:
        for chunk in chunks(list(arch_ids), 500):
            ph = ",".join("?" * len(chunk))
            arch_in_db |= {r[0] for r in con.execute(
                f"SELECT id FROM sessions WHERE id IN ({ph})", chunk).fetchall()}

    print(f"[{db_path}]")
    print(f"  cron 会话待删: {cron_rows[0]} 个 / {cron_rows[1]} 条消息")
    print(f"  已归档会话待删: {len(arch_in_db)} 个")
    total = cron_rows[0] + len(arch_in_db)

    if args.dry_run or total == 0:
        print("  (dry-run / 无待删，跳过)")
        con.close()
        return

    before = os.path.getsize(db_path)
    print(f"  删除前大小: {before/1e9:.2f} GB，开始删除 {total} 个会话...")

    all_ids = [r[0] for r in con.execute(
        f"SELECT id FROM sessions WHERE {cron_cond}", cron_params).fetchall()]
    all_ids += list(arch_in_db)

    with con:  # 事务
        for chunk in chunks(all_ids, 500):
            ph = ",".join("?" * len(chunk))
            con.execute(f"UPDATE sessions SET parent_session_id=NULL WHERE parent_session_id IN ({ph})", chunk)
            con.execute(f"DELETE FROM messages WHERE session_id IN ({ph})", chunk)
            con.execute(f"DELETE FROM sessions WHERE id IN ({ph})", chunk)

    print("  删除完成，rebuild FTS + VACUUM（可能需数分钟）...")
    # FTS5 删除是 tombstone 逻辑删除；optimize 可能膨胀，必须 rebuild 彻底重建索引
    for tbl in ("messages_fts", "messages_fts_trigram"):
        try:
            con.execute(f"INSERT INTO {tbl}({tbl}) VALUES('rebuild')")
        except Exception as e:
            print(f"  rebuild {tbl} 跳过: {e}")
    con.commit()
    con.execute("VACUUM")

    after = os.path.getsize(db_path)
    con.close()
    print(f"  删除后大小: {after/1e9:.2f} GB，回收 {(before-after)/1e9:.2f} GB")


if __name__ == "__main__":
    main()
