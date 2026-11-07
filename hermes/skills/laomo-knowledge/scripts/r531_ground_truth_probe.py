# -*- coding: utf-8 -*-
"""
R531 ground-truth probe — 老莫 heartbeat cron 第一动作
=====================================================
Pitfall #82 / #93 / #85 三重防御实证可重跑脚本。

功能:
  1. sqlite3 直连 ~/.hermes/tasks.db 读 task #11 description
  2. line-anchored regex `(?m)^\\[R\\d+ ` 切 chunks (Pitfall #64 防御)
  3. 取 chunks[-1] R 号 = ground truth last_r (Pitfall #82 三个漂移源防御)
  4. 计算 desc 余量 vs 48KB 早闸口 (Pitfall #84 / #91)
  5. 输出 last_r / desc_chars / chunks_count / first_chunk_R / margin_to_48KB 五元组

为什么 `+` 拼接不用 f-string:
  Pitfall #93 实证 — f-string 表达式部分禁止反斜杠转义,即使 raw string 也不行。
  本脚本纯英文,理论上 f-string OK,但走 `+` 拼接是 R529 范本统一风格,100% 兼容。

使用:
  python3 ~/.hermes/skills/laomo-knowledge/scripts/r531_ground_truth_probe.py
  python3 ~/.hermes/skills/laomo-knowledge/scripts/r531_ground_truth_probe.py --task 11
  python3 ~/.hermes/skills/laomo-knowledge/scripts/r531_ground_truth_probe.py --db /custom/path.db

历史:
  - R510: 内联 SKILL.md 写法,无独立脚本 (Pitfall #85 MISSING)
  - R531: 落 ~/.hermes/skills/laomo-knowledge/scripts/r531_ground_truth_probe.py (本版本)
"""

import argparse
import re
import sqlite3
import sys

DEFAULT_DB = "/Users/hua/.hermes/tasks.db"
DEFAULT_TASK_ID = 11
EARLY_GATE_CHARS = 49152  # 48KB 早闸口 (Pitfall #84 / #91)


def probe(db_path, task_id):
    conn = sqlite3.connect(db_path)
    row = conn.execute(
        "SELECT description FROM tasks WHERE id = ?", (task_id,)
    ).fetchone()
    conn.close()
    if row is None:
        print("ERROR: task " + str(task_id) + " not found in " + db_path)
        sys.exit(1)
    desc = row[0]
    spans = [m.start() for m in re.finditer(r"(?m)^\[R\d+ ", desc)]
    chunks = [desc[a:b] for a, b in zip(spans, spans[1:] + [len(desc)])]
    if not chunks:
        print("ERROR: no [R<n> chunks found in desc, desc=" + str(len(desc)) + " chars")
        sys.exit(2)
    last_r = int(re.match(r"\[R(\d+) ", chunks[-1]).group(1))
    first_r = int(re.match(r"\[R(\d+) ", chunks[0]).group(1))
    margin = EARLY_GATE_CHARS - len(desc)
    return {
        "task_id": task_id,
        "last_r": last_r,
        "first_chunk_r": first_r,
        "desc_chars": len(desc),
        "chunks_count": len(chunks),
        "margin_to_48kb": margin,
        "margin_to_50kb": 51200 - len(desc),
    }


def main():
    parser = argparse.ArgumentParser(description="R531 ground-truth probe")
    parser.add_argument("--db", default=DEFAULT_DB, help="tasks.db path")
    parser.add_argument("--task", type=int, default=DEFAULT_TASK_ID, help="task id")
    parser.add_argument("--json", action="store_true", help="JSON output")
    args = parser.parse_args()
    r = probe(args.db, args.task)
    if args.json:
        import json
        print(json.dumps(r, indent=2, ensure_ascii=False))
        return
    # + 拼接模式 (Pitfall #93 防御)
    print("=== R531 ground-truth probe ===")
    print("task_id          = " + str(r["task_id"]))
    print("last_r           = " + str(r["last_r"]))
    print("first_chunk_R    = " + str(r["first_chunk_r"]))
    print("desc_chars       = " + str(r["desc_chars"]))
    print("chunks_count     = " + str(r["chunks_count"]))
    print("margin_to_48KB   = " + str(r["margin_to_48kb"]) + " chars (早闸口)")
    print("margin_to_50KB   = " + str(r["margin_to_50kb"]) + " chars (硬阈值)")
    print("=== next_R = last_r + 1 = " + str(r["last_r"] + 1) + " ===")


if __name__ == "__main__":
    main()
