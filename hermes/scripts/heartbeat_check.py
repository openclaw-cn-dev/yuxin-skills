#!/usr/bin/env python3
"""
心跳检查脚本 - 检查指定Agent是否有待处理任务
同时扫描三个任务源：kanban.db（新真源）、桌面tasks.db（历史遗留）、hermes tasks.db（创业项目）
用法: python3 heartbeat_check.py <agent_name>
"""
import os
import sys
import sqlite3
from datetime import datetime

def get_kanban_db_path():
    """获取kanban.db路径 - 支持多profile环境"""
    # 系统默认 kanban.db 是真源（profile 下的通常是空壳）
    default_kanban = "/Users/hua/.hermes/kanban.db"
    if os.path.exists(default_kanban):
        return default_kanban

    # fallback：profile 下的 kanban.db
    profile_home = os.path.expanduser("~")
    profile_kanban = os.path.join(profile_home, ".hermes", "kanban.db")
    if os.path.exists(profile_kanban):
        return profile_kanban

    return None

def get_tasks_db_path():
    """获取桌面tasks.db路径（历史遗留）"""
    return "/Users/hua/Desktop/渔芯科技/团队协作/tasks.db"

def get_hermes_tasks_db_path():
    """获取hermes内置tasks.db路径（创业项目等任务）"""
    return "/Users/hua/.hermes/tasks.db"

def query_kanban_tasks(agent_name, db_path):
    """查询kanban.db中的待处理任务"""
    if not db_path or not os.path.exists(db_path):
        return []
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, title, priority, status, 'kanban' as source
        FROM tasks 
        WHERE assignee = ? AND status IN ('pending', 'in_progress')
        ORDER BY priority ASC, created_at ASC
        LIMIT 5
    ''', (agent_name,))
    
    tasks = cursor.fetchall()
    conn.close()
    return tasks

def query_desktop_tasks(agent_name, db_path):
    """查询桌面tasks.db中的待处理任务（历史遗留）"""
    if not os.path.exists(db_path) or os.path.getsize(db_path) == 0:
        return []
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT task_id as id, title, priority, status, 'desktop' as source
        FROM tasks 
        WHERE status IN ('pending', 'in_progress')
          AND (assignee LIKE ? OR title LIKE ? OR description LIKE ?)
        ORDER BY CASE priority 
            WHEN 'P0' THEN 1 
            WHEN 'P1' THEN 2 
            WHEN 'P2' THEN 3 
            ELSE 4 
        END, created_at ASC
        LIMIT 5
    ''', (f'%{agent_name}%', f'%{agent_name}%', f'%{agent_name}%'))
    
    tasks = cursor.fetchall()
    conn.close()
    return tasks

def query_hermes_tasks(agent_name, db_path):
    """查询hermes tasks.db中的待处理任务（创业项目等）"""
    if not os.path.exists(db_path) or os.path.getsize(db_path) == 0:
        return []
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, title, priority, status, 'hermes' as source
        FROM tasks 
        WHERE assigned_to = ? AND status IN ('pending', 'in_progress')
        ORDER BY CASE priority 
            WHEN 'P0' THEN 1 
            WHEN 'P1' THEN 2 
            WHEN 'P2' THEN 3 
            ELSE 4 
        END, created_at ASC
        LIMIT 5
    ''', (agent_name,))
    
    tasks = cursor.fetchall()
    conn.close()
    return tasks

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 heartbeat_check.py <agent_name>")
        sys.exit(1)
    
    agent_name = sys.argv[1]
    
    # 查询三个数据源
    kanban_tasks = query_kanban_tasks(agent_name, get_kanban_db_path())
    desktop_tasks = query_desktop_tasks(agent_name, get_tasks_db_path())
    hermes_tasks = query_hermes_tasks(agent_name, get_hermes_tasks_db_path())
    
    # 合并并排序（P0优先）
    all_tasks = []
    for t in kanban_tasks:
        priority_map = {0: 'P0', 1: 'P1', 2: 'P2'}
        priority = priority_map.get(t[2], f'P{t[2]}')
        all_tasks.append((t[0], t[1], priority, t[3], t[4]))
    
    for t in desktop_tasks:
        all_tasks.append((t[0], t[1], t[2], t[3], t[4]))
    
    for t in hermes_tasks:
        all_tasks.append((t[0], t[1], t[2], t[3], t[4]))
    
    # 按优先级排序
    priority_order = {'P0': 0, 'P1': 1, 'P2': 2}
    all_tasks.sort(key=lambda x: priority_order.get(x[2], 99))
    
    # 只输出最高优先级的1个任务
    if all_tasks:
        t = all_tasks[0]
        print(f"{t[0]}|{t[1]}|{t[2]}|{t[3]}|{t[4]}")

if __name__ == "__main__":
    main()
