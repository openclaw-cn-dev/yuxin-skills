#!/usr/bin/env python3
import sqlite3
import sys
import os

# Get agent name from command line
agent_name = sys.argv[1] if len(sys.argv) > 1 else None

# Path to tasks.db
db_path = os.path.expanduser("~/.hermes/tasks.db")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Create tasks table if it doesn't exist (for schema compatibility)
cursor.execute('''
    CREATE TABLE IF NOT EXISTS tasks (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        assigned_to TEXT NOT NULL,
        status TEXT DEFAULT 'pending',
        priority TEXT DEFAULT 'P2',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')

# Query for pending/in_progress tasks for this agent
cursor.execute('''
    SELECT id, title, status, priority FROM tasks 
    WHERE assigned_to = ? AND status IN ('pending', 'in_progress')
    ORDER BY CASE priority
        WHEN 'P0' THEN 1
        WHEN 'P1' THEN 2
        WHEN 'P2' THEN 3
        WHEN 'P3' THEN 4
        ELSE 5
    END ASC
''', (agent_name,))

tasks = cursor.fetchall()
conn.close()

# Output tasks if any (for cron job to detect)
for task in tasks:
    print(f"{task[0]}|{task[1]}|{task[2]}|{task[3]}")
