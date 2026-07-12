#!/usr/bin/env python3
"""
统一心跳检查脚本 - 方案2核心
用法: python3 heartbeat_check.py <agent_name> [feishu_chat_id]
检查该Agent是否有 pending/in_progress 任务
有任务 → 打印任务摘要（触发LLM处理）
无任务 → 静默退出（零LLM消耗）
"""
import os
import sqlite3
import sys
from datetime import datetime

AGENT_NAME = sys.argv[1] if len(sys.argv) > 1 else ""
FEISHU_CHAT = sys.argv[2] if len(sys.argv) > 2 else ""

# 任务库合并：Desktop tasks.db（历史）+ ~/.hermes/kanban.db（KB-* 派单真源）
DB_PATHS = [
    ("/Users/hua/Desktop/渔芯科技/团队协作/tasks.db", "desktop"),
    (os.path.expanduser("~/.hermes/kanban.db"), "kanban"),
]

def get_pending_tasks(agent):
    all_rows = []
    seen_ids = set()
    for db_path, db_kind in DB_PATHS:
        if not os.path.exists(db_path):
            continue
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        try:
            if db_kind == "desktop":
                # Desktop tasks.db: task_id / title / status / priority / updated_at
                cursor.execute("""
                    SELECT task_id, title, status, priority, updated_at
                    FROM tasks
                    WHERE assignee = ? AND status IN ('pending', 'in_progress')
                """, (agent,))
            else:
                # kanban.db: id / title / status / priority / created_at (INTEGER unix seconds)
                cursor.execute("""
                    SELECT id, title, status, priority, created_at
                    FROM tasks
                    WHERE assignee = ? AND status = 'pending'
                """, (agent,))
            for r in cursor.fetchall():
                if r[0] in seen_ids:
                    continue
                seen_ids.add(r[0])
                # kanban.db 字段转换：priority 数字 → P0/P1/P2, created_at unix 秒 → 字符串
                if db_kind == "kanban":
                    pr = r[3]
                    pr_str = f"P{pr}" if isinstance(pr, int) and pr < 10 else str(pr)
                    ts = datetime.fromtimestamp(float(r[4])).strftime("%Y-%m-%d %H:%M:%S")
                    r = (r[0], r[1], r[2], pr_str, ts)
                all_rows.append(r)
        except sqlite3.OperationalError:
            pass
        finally:
            conn.close()

    # 排序：P0 > P1 > P2，按时间戳升序
    def sort_key(r):
        pr_rank = {"P0": 0, "P1": 1, "P2": 2}.get(r[3], 3)
        return (pr_rank, r[4] or "")
    all_rows.sort(key=sort_key)
    return all_rows

def main():
    if not AGENT_NAME:
        print("用法: python3 heartbeat_check.py <agent_name> [feishu_chat_id]")
        sys.exit(0)

    tasks = get_pending_tasks(AGENT_NAME)

    if not tasks:
        # 无待处理任务，静默退出，零LLM消耗
        sys.exit(0)

    # 有待处理任务，打印摘要触发LLM
    status_emoji = {
        "pending": "⏳",
        "in_progress": "🔄",
    }
    priority_color = {
        "P0": "🔴",
        "P1": "🟡",
        "P2": "🟢",
    }

    lines = [f"🎯 **{AGENT_NAME}** 待处理任务({len(tasks)}个)**\n"]
    for task_id, title, status, priority, updated_at in tasks:
        emoji = status_emoji.get(status, "📋")
        p_emoji = priority_color.get(priority, "📋")
        lines.append(f"{emoji}{p_emoji} [{task_id}] {title}")

    print("\n".join(lines))

if __name__ == "__main__":
    main()
