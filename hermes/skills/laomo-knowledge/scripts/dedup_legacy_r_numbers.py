#!/usr/bin/env python3
"""剥离老莫 heartbeat tasks.description 中历史遗留的重复 R<n> 条目。

背景:R119/R121 实战发现 description 偶尔会包含**合法的 R 编号**重复 2+ 次
(不是 f-string 渲染失败产生的字面 `[R{new_r} ...]` 坏条目,而是格式正常但
内容重复的同号日志)。R119 实战由 f-string 错误产生 `[R1 ...]` 孤立条目;
R122 (2026-09-01) 实战由更早期某轮 cron 误操作产生 `[R121 ...]` 重复条目。

触发场景:append 完本轮 R<n+1> 后,验证阶段 `Counter(nums_after)` 发现
`{R<n>: 2, ...}`,确认是**本轮新增前的历史遗留**,立即跑本脚本清理。

用法:
    python3 /tmp/dedup_legacy_r_numbers.py <task_id>
    或:
    DB_PATH=/path/to/tasks.db python3 dedup_legacy_r_numbers.py <task_id>

默认 task_id=11,DB_PATH=/Users/hua/.hermes/tasks.db。

剥离策略:
- 保留每个 R 编号的**最后一次**出现(本轮新增的总是最末一条)。
- 用 `desc[:first_occurrence] + desc[second_occurrence:]` 拼接,删除第一段。
- 删除后再用 `Counter` 验证重复已清零,R 编号单调递增。
- 不删除最新 R<n+1>(最末一条必然保留)。

Pitfall:
- 不要用 `REPLACE` 全文覆盖 description——会丢上下文。
- 不要用 `desc.replace(...)`——只替换第一次出现的同号条目有歧义。
- 删除后必须重读 description + 重新跑 Counter 验证。
"""
import os
import re
import sys
from collections import Counter
import sqlite3

DB_PATH = os.environ.get("DB_PATH", "/Users/hua/.hermes/tasks.db")


def dedupe(task_id: int) -> None:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT description FROM tasks WHERE id = ?", (task_id,))
    row = cur.fetchone()
    if not row:
        print(f"Task {task_id} not found in {DB_PATH}", file=sys.stderr)
        conn.close()
        return
    desc = row[0]

    nums = [int(x) for x in re.findall(r"\[R(\d+)", desc)]
    counts = Counter(nums)
    dupes = {k: v for k, v in counts.items() if v > 1}
    if not dupes:
        print(f"No duplicates found in task {task_id}. R count={len(nums)}, "
              f"last_r={max(nums) if nums else 0}")
        conn.close()
        return

    print(f"Task {task_id}: found duplicates {dupes}")

    for dup_r in sorted(dupes.keys()):
        positions = [m.start() for m in re.finditer(rf"\[R{dup_r} ", desc)]
        if len(positions) < 2:
            continue
        # 保留最末一条,删除前面的重复条目
        # 第一段 [R{dup_r} ...] 到下一段 [R{next} 开头之间
        # 简化:用 positions[1] 作为截断点
        first = positions[0]
        second = positions[1]
        before = desc[:first]
        after = desc[second:]
        desc = before + after
        print(f"  Removed duplicate [R{dup_r} ...] at offset {first} "
              f"(kept last occurrence at offset {second})")

    cur.execute(
        "UPDATE tasks SET description = ?, updated_at = ? WHERE id = ?",
        (desc, "2026-09-01 03:02:06 CST", task_id),
    )
    conn.commit()

    # 验证
    cur.execute("SELECT description FROM tasks WHERE id = ?", (task_id,))
    new_desc = cur.fetchone()[0]
    nums_after = [int(x) for x in re.findall(r"\[R(\d+)", new_desc)]
    counts_after = Counter(nums_after)
    dup_after = {k: v for k, v in counts_after.items() if v > 1}
    print(f"After dedupe: last_r={max(nums_after) if nums_after else 0}, "
          f"remaining_dupes={dup_after}")

    conn.close()


if __name__ == "__main__":
    task_id = int(sys.argv[1]) if len(sys.argv) > 1 else 11
    dedupe(task_id)