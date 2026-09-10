#!/usr/bin/env python3
"""老莫心跳 R 轮写入器 (laomo-heartbeat skill)。

内置四道防御, 对应 SKILL.md「写轮次的门」:
  1. R 编号断言: 新条目 R_NUM 必须 == 当前 last_r + 1 (防跳号/复用, R124 防御)
  2. R181 尺寸门: chars 口径 (非 bytes), 投影 >= 48KB 早闸口 -> 拒写并提示先剪枝
  3. keep_in_progress 铁律: status 恒写 in_progress, 永不 completed
  4. post-write verify: SELECT 回读 last_r + status

用法:
  python3 write_round.py entry.txt
      entry.txt = 以 "[RNNN " 开头的新轮次文本 (可多行)
  python3 write_round.py entry.txt --prune 3 --archive /path/to/task-11-log-archive.md
      追加前先从最旧起 drop 3 条, 每条先 append 到 --archive 文件再 drop (R209 协议)

entry 内容 (真实状态判定 / 阻塞盘点 / 剪枝预告) 仍按 SKILL.md 人工撰写,
本脚本只负责防御性落库, 不生成内容。
"""
import argparse
import os
import re
import sqlite3
import sys

DB = os.environ.get("TASKS_DB", "/Users/hua/.hermes/tasks.db")
TASK_ID = 11
EARLY_GATE_KB = 48.0  # 早闸口 (chars 口径); 50KB 硬阈值不允许触及


def split_entries(desc):
    """按行首 '[R<digits> ' 切成轮次条目块; 返回 (preamble, chunks)。"""
    spans = [m.start() for m in re.finditer(r"(?m)^\[R\d+ ", desc)]
    if not spans:
        return desc, []
    preamble = desc[: spans[0]]
    chunks = [desc[a:b] for a, b in zip(spans, spans[1:] + [len(desc)])]
    return preamble, chunks


def entry_num(chunk):
    return int(re.match(r"\[R(\d+) ", chunk).group(1))


def main():
    ap = argparse.ArgumentParser(description="task #11 R 轮防御性写入器")
    ap.add_argument("entry_file", help="新轮次文本文件, 以 '[RNNN ' 开头")
    ap.add_argument("--prune", type=int, default=0, metavar="N",
                    help="追加前从最旧起 drop N 条")
    ap.add_argument("--archive", default=None,
                    help="剪枝条目的 archive 文件路径 (先 append 再 drop, R209 协议)")
    args = ap.parse_args()

    entry = open(args.entry_file, encoding="utf-8").read().strip()
    m = re.match(r"\[R(\d+) ", entry)
    if not m:
        sys.exit(f"FATAL: entry 不以 '[RNNN ' 开头: {entry[:40]!r}")
    r_num = int(m.group(1))

    conn = sqlite3.connect(DB)
    row = conn.execute("SELECT description FROM tasks WHERE id=?", (TASK_ID,)).fetchone()
    if not row:
        sys.exit(f"FATAL: task #{TASK_ID} not found in {DB}")
    desc = row[0]
    preamble, chunks = split_entries(desc)
    last_r = entry_num(chunks[-1]) if chunks else 0

    # -- 防御 1: R 编号断言 (防跳号/复用)
    if r_num != last_r + 1:
        sys.exit(f"FATAL: R 编号断言失败: 期望 {last_r + 1}, 得到 {r_num}")
    if any(entry_num(c) == r_num for c in chunks):
        sys.exit(f"FATAL: R{r_num} 已存在 (复用)")

    # -- 剪枝: 先 append 到 archive 再 drop (R209 协议, 不直接删)
    if args.prune:
        if args.prune >= len(chunks):
            sys.exit(f"FATAL: --prune {args.prune} 会剪掉全部条目 (现有 {len(chunks)} 条)")
        if not args.archive:
            sys.exit("FATAL: --prune 必须配 --archive (R209: 先 archive 再 drop)")
        dropped = chunks[: args.prune]
        os.makedirs(os.path.dirname(os.path.abspath(args.archive)), exist_ok=True)
        with open(args.archive, "a", encoding="utf-8") as f:
            for c in dropped:
                f.write(c if c.endswith("\n") else c + "\n")
        print(f"prune OK: drop {len(dropped)} 条 (R{entry_num(dropped[0])}..R{entry_num(dropped[-1])}) -> {args.archive}")
        chunks = chunks[args.prune:]

    # -- 防御 2: R181 尺寸门 (chars 口径)
    base = preamble + "".join(chunks)
    sep = "" if (base.endswith("\n") or not chunks) else "\n"
    new_desc = base + sep + entry + "\n"
    proj_kb = len(new_desc) / 1024
    if proj_kb >= EARLY_GATE_KB:
        sys.exit(f"FATAL: 尺寸门 {proj_kb:.1f}KB chars >= {EARLY_GATE_KB}KB 早闸口 — 先 --prune 再写")

    # -- 防御 3: 写入, status 恒 in_progress (永不 completed)
    conn.execute(
        "UPDATE tasks SET description=?, status='in_progress', updated_at=CURRENT_TIMESTAMP WHERE id=?",
        (new_desc, TASK_ID),
    )
    conn.commit()

    # -- 防御 4: post-write verify
    d2, s2, u2 = conn.execute(
        "SELECT description, status, updated_at FROM tasks WHERE id=?", (TASK_ID,)
    ).fetchone()
    _, chunks2 = split_entries(d2)
    got_last = entry_num(chunks2[-1]) if chunks2 else 0
    if got_last != r_num:
        sys.exit(f"FATAL: post-write verify 失败: last_r={got_last} != {r_num}")
    print(f"pre-write OK: last_r={last_r}, entries={len(chunks)}")
    print(f"post-write OK: last_r={got_last}, status={s2}, updated_at={u2}, "
          f"desc={len(d2) / 1024:.1f}KB chars, entries={len(chunks2)}")
    conn.close()


if __name__ == "__main__":
    main()
