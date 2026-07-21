#!/usr/bin/env python3
"""
小宝心跳脚本 - no_agent模式
用法: python3 xiaobao_heartbeat.py
检查小宝是否有待处理任务：
- 无任务 → 静默退出（零LLM消耗）
- 有任务 → 打印触发信号
"""
import sqlite3
import sys
import os

DB_PATH = "/Users/hua/Desktop/渔芯科技/团队协作/tasks.db"

def get_pending_tasks(agent):
    if not os.path.exists(DB_PATH):
        return []
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT task_id, title, status, priority, updated_at
        FROM tasks
        WHERE assignee = ? AND status IN ('pending', 'in_progress')
        ORDER BY
            CASE priority WHEN 'P0' THEN 0 WHEN 'P1' THEN 1 ELSE 2 END,
            updated_at ASC
    """, (agent,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def main():
    agent = "小宝"
    tasks = get_pending_tasks(agent)

    if not tasks:
        # 无待处理任务，静默退出
        sys.exit(0)

    # 有待处理任务，打印任务摘要（触发LLM）
    lines = [f"[HEARTBEAT_TRIGGER] {agent} 有{len(tasks)}个待处理任务:\n"]
    for task_id, title, status, priority, updated_at in tasks:
        lines.append(f"[{status}] [{priority}] [{task_id}] {title}")

    print("\n".join(lines))

if __name__ == "__main__":
    main()
