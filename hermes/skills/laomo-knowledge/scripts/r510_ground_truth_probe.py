#!/usr/bin/env python3
"""R 编号 ground-truth probe — R510 实战沉淀 (Pitfall #82 三个漂移源实测)

唯一可信的 last_r 查询路径：直接 sqlite3 tasks.db + write_round.py 同款 regex。
**不要信** task_brief.sh tail -1 / wrapper stdout / 任何 probe 输出。

用法:
    python3 r510_ground_truth_probe.py
    python3 r510_ground_truth_probe.py --task-id 11 --db /Users/hua/.hermes/tasks.db

输出:
    last_r=<N>, desc=<X> chars, chunks=<Y>
    + 整段 R 编号列表（chunks[0..-1] 各 chunk 的 R 号 + 实长）

写 entry 前必跑此脚本确认 new_R = last_r + 1。
"""
import argparse
import re
import sqlite3


def main():
    ap = argparse.ArgumentParser(description="R 编号 ground-truth probe")
    ap.add_argument("--task-id", type=int, default=11)
    ap.add_argument("--db", default="/Users/hua/.hermes/tasks.db")
    args = ap.parse_args()

    conn = sqlite3.connect(args.db)
    row = conn.execute(
        "SELECT description FROM tasks WHERE id=?", (args.task_id,)
    ).fetchone()
    if not row:
        raise SystemExit(f"FATAL: task #{args.task_id} not found in {args.db}")

    desc = row[0]
    spans = [m.start() for m in re.finditer(r"(?m)^\[R\d+ ", desc)]
    chunks = [desc[a:b] for a, b in zip(spans, spans[1:] + [len(desc)])]
    last_r = int(re.match(r"\[R(\d+) ", chunks[-1]).group(1)) if chunks else 0

    print(f"last_r={last_r}, desc={len(desc)} chars, chunks={len(chunks)}")
    print("--- chunks[0..-1] R 号 + 实长 (顺序 = drop 顺序, 最旧 = chunks[0]) ---")
    for i, c in enumerate(chunks):
        n = int(re.match(r"\[R(\d+) ", c).group(1))
        marker = " <-- OLDEST (next --prune 1 drops this)" if i == 0 else ""
        print(f"  chunks[{i}]: R{n} len={len(c)}{marker}")
    print(f"---")
    print(f"new_R = last_r + 1 = {last_r + 1}")


if __name__ == "__main__":
    main()