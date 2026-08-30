#!/usr/bin/env python3
"""
heartbeat_truth.py — 毛豆 cron 真实任务探测（绕开 heartbeat_check.py 误报）

用法：
  python3 heartbeat_truth.py 毛豆

原理：
  heartbeat_check.py 偶尔把 done 状态任务当作 pending 返回（已确认 bug）。
  本脚本直接查 kanban.db，过滤 status IN (pending, in_progress)，返回真值。
"""
import sqlite3
import os
import sys


def get_kanban_db():
    """获取真源 kanban.db 路径。"""
    default = "/Users/hua/.hermes/kanban.db"
    if os.path.exists(default) and os.path.getsize(default) > 0:
        return default
    return None


def list_active_tasks(agent_name):
    """查询指定 agent 的真 pending/in_progress 任务。"""
    db = get_kanban_db()
    if not db:
        print("ERROR: kanban.db not found or empty", file=sys.stderr)
        sys.exit(2)

    conn = sqlite3.connect(db)
    cur = conn.cursor()

    # 先列出表，避免 schema 差异
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [r[0] for r in cur.fetchall()]

    tasks = []
    for table in tables:
        if table not in ("tasks",):
            continue
        cur.execute(f"PRAGMA table_info({table})")
        cols = [r[1] for r in cur.fetchall()]
        if "assignee" not in cols or "status" not in cols:
            continue
        cur.execute(
            f"SELECT * FROM {table} WHERE assignee=? AND status IN ('pending','in_progress')",
            (agent_name,),
        )
        for row in cur.fetchall():
            task = dict(zip(cols, row))
            tasks.append(task)

    conn.close()
    return tasks


def main():
    if len(sys.argv) < 2:
        print("Usage: heartbeat_truth.py <agent_name>", file=sys.stderr)
        sys.exit(1)

    agent = sys.argv[1]
    tasks = list_active_tasks(agent)

    if not tasks:
        print(f"[{agent}] 真空闲：0 条 pending/in_progress 任务", file=sys.stderr)
        sys.exit(0)

    print(f"[{agent}] 真实活跃任务 ({len(tasks)} 条):", file=sys.stderr)
    for t in tasks:
        print(
            f"  - {t.get('id', t.get('task_id', '?'))} | "
            f"{t.get('priority', '?')} | "
            f"{t.get('status', '?')} | "
            f"{t.get('title', '?')[:50]}"
        )
    # 真有任务 → exit 0 让 cron 继续
    sys.exit(0)


if __name__ == "__main__":
    main()