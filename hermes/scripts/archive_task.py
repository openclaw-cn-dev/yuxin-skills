#!/usr/bin/env python3
"""
任务完成归档脚本 - 各Agent完成任务后调用，写入归档目录
用法: python3 archive_task.py "task_id" "title" "result" "actor"
"""
import sys, os, json, hashlib
from datetime import datetime

ARCHIVE_DIR = "/Users/hua/Desktop/渔芯科技/团队协作/task_archive"

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: archive_task.py <task_id> <title> [result] [actor]")
        sys.exit(1)
    
    task_id = sys.argv[1]
    title = sys.argv[2]
    result = sys.argv[3] if len(sys.argv) > 3 else ""
    actor = sys.argv[4] if len(sys.argv) > 4 else ""
    
    os.makedirs(ARCHIVE_DIR, exist_ok=True)
    
    data = {
        "task_id": task_id,
        "title": title,
        "result": result,
        "actor": actor,
        "completed_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    # 用标题MD5哈希作为文件名的一部分，避免长标题问题
    h = hashlib.md5(title.encode()).hexdigest()[:12]
    fname = f"{datetime.now().strftime('%m%d%H%M%S')}_{h}.json"
    fpath = os.path.join(ARCHIVE_DIR, fname)
    
    with open(fpath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"Archived: {title}")
