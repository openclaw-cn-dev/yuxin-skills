#!/usr/bin/env python3
"""
渔芯任务监听器 watchdog
极轻量：扫描飞书云盘任务目录，检测到新任务文件时通知玉芬
无Agent介入，纯API轮询，接近0 token消耗

用法:
  python3 task_watchdog.py              # 检测+通知
  python3 task_watchdog.py --dry-run     # 只打印，不通知
  python3 task_watchdog.py --status      # 查看状态
"""

import os
import sys
import json
import sqlite3
from datetime import datetime
from pathlib import Path
from pathlib import PurePath
from typing import Optional

HERMES_HOME = Path.home() / ".hermes"
STATE_DB = HERMES_HOME / "task_watchdog.db"

# 飞书云盘任务派发根目录token
CLOUD_DRIVE_TOKEN = "Vb83fsimklzqKDdd0dHcc3g2nhd"  # 任务派发根目录

# 需要监控的Agent子文件夹
AGENT_FOLDERS = {
    "毛豆": "毛豆",
    "老莫": "老莫",
    "小宝": "小宝",
    "黑豆": "黑豆",
    "阿福": "阿福",
    "宽博士": "宽博士",
    "学习助手": "学习助手",
}

# 玉芬的飞书OpenID（通知接收人）
YUFEN_OPEN_ID = "***SECRET***"

# 汇报群
REPORT_CHAT_ID = "***SECRET***"


def get_feishu_client():
    """获取飞书客户端"""
    sys.path.insert(0, str(HERMES_HOME / "hermes-agent"))
    from lark_oapi import Client

    client = (
        Client.builder()
        .app_id(os.environ.get("FEISHU_APP_ID", ""))
        .app_secret(os.environ.get("FEISHU_APP_SECRET", ""))
        .build()
    )
    return client


def init_state_db():
    """初始化状态数据库"""
    conn = sqlite3.connect(STATE_DB)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS last_check (
            agent TEXT PRIMARY KEY,
            last_file_token TEXT,
            last_check_at TEXT
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS seen_files (
            file_token TEXT PRIMARY KEY,
            agent TEXT,
            file_name TEXT,
            first_seen_at TEXT
        )
    """)
    conn.commit()
    return conn


def list_folder_files(client, folder_token: str, page_size: int = 50) -> list:
    """列出文件夹中的文件"""
    from lark_oapi.api.drive.v1 import ListFileRequest

    files = []
    page_token = ""

    while True:
        req = (
            ListFileRequest.builder()
            .folder_token(folder_token)
            .page_size(page_size)
            .order_by("EditedTime")
            .direction("DESC")
        )
        if page_token:
            req.page_token(page_token)

        request = req.build()
        response = client.request(request)

        if response.code != 0:
            print(f"[WARN] List folder {folder_token} failed: code={response.code} msg={response.msg}")
            break

        data = getattr(response, 'data', None)
        if not data:
            break

        items = data.files if hasattr(data, 'files') else []
        for item in items:
            files.append({
                "token": getattr(item, 'token', "") or "",
                "name": getattr(item, 'name', "") or "",
                "type": getattr(item, 'type', "") or "",
                "size": getattr(item, 'size', 0) or 0,
                "edited_time": getattr(item, 'edited_time', "") or "",
            })

        page_token = getattr(data, 'page_token', "") or ""
        if not page_token:
            break

    return files


def get_or_create_subfolder(client, parent_token: str, subfolder_name: str) -> Optional[str]:
    """获取或创建子文件夹，返回folder_token"""
    from lark_oapi.api.drive.v1 import CreateFolderRequest
    from lark_oapi.api.drive.v1 import CreateFolderRequestBuilder

    # 先列出看是否已存在
    files = list_folder_files(client, parent_token)
    for f in files:
        if f["type"] == "folder" and f["name"] == subfolder_name:
            return f["token"]

    # 不存在则创建
    req = (
        CreateFolderRequest.builder()
        .folder_token(parent_token)
        .name(subfolder_name)
        .folder_type("docx")
        .build()
    )
    response = client.request(req)
    if response.code != 0:
        print(f"[WARN] Create folder '{subfolder_name}' failed: code={response.code} msg={response.msg}")
        return None

    data = getattr(response, 'data', None)
    if data:
        return getattr(data, 'token', "") or ""
    return None


def get_subfolder_token(client, parent_token: str, subfolder_name: str) -> Optional[str]:
    """获取子文件夹token（只读，不创建）"""
    files = list_folder_files(client, parent_token)
    for f in files:
        if f["type"] == "folder" and f["name"] == subfolder_name:
            return f["token"]
    return None


def send_feishu_message(client, open_id: str, msg: str):
    """发送飞书私信"""
    from lark_oapi.api.im.v1 import CreateMessageRequest
    from lark_oapi.api.im.v1 import CreateMessageRequestBuilder
    from lark_oapi.adapter.oauth import DefaultAccessToken

    try:
        req = (
            CreateMessageRequest.builder()
            .receive_id(open_id)
            .msg_type("text")
            .content(json.dumps({"text": msg}))
            .build()
        )
        # 需要user_access_token方式
        response = client.request(
            req,
            option=DefaultAccessToken(
                os.environ.get("FEISHU_USER_ACCESS_TOKEN", "")
            )
        )
        if response.code != 0:
            print(f"[WARN] Send message failed: code={response.code} msg={response.msg}")
        return response.code == 0
    except Exception as e:
        print(f"[WARN] Send message exception: {e}")
        return False


def send_group_message(client, chat_id: str, msg: str):
    """发送飞书群消息"""
    from lark_oapi.api.im.v1 import CreateMessageRequest
    from lark_oapi.api.im.v1 import CreateMessageRequestBuilder
    from lark_oapi.adapter.oauth import DefaultAccessToken

    try:
        req = (
            CreateMessageRequest.builder()
            .receive_id(chat_id)
            .msg_type("text")
            .content(json.dumps({"text": msg}))
            .build()
        )
        response = client.request(
            req,
            option=DefaultAccessToken(
                os.environ.get("FEISHU_USER_ACCESS_TOKEN", "")
            )
        )
        if response.code != 0:
            print(f"[WARN] Send group message failed: code={response.code} msg={response.msg}")
        return response.code == 0
    except Exception as e:
        print(f"[WARN] Send group message exception: {e}")
        return False


def check_agent_folder(client, conn: sqlite3.Connection, agent: str, dry_run: bool = False) -> list:
    """检查单个Agent文件夹，返回新文件列表"""
    cur = conn.cursor()

    # 获取subfolder token
    subfolder_token = get_subfolder_token(client, CLOUD_DRIVE_TOKEN, agent)
    if not subfolder_token:
        return []

    # 列出所有文件
    files = list_folder_files(client, subfolder_token)
    if not files:
        return []

    # 获取上次检查记录
    cur.execute("SELECT last_file_token FROM last_check WHERE agent = ?", (agent,))
    row = cur.fetchone()
    last_top_token = row[0] if row else None

    new_files = []
    for f in files:
        # 检查是否新文件（不在seen列表中）
        cur.execute("SELECT 1 FROM seen_files WHERE file_token = ?", (f["token"],))
        if not cur.fetchone():
            new_files.append(f)

    # 如果有新文件，更新状态
    if new_files and not dry_run:
        top_file = files[0]  # 最新编辑的
        cur.execute("""
            INSERT OR REPLACE INTO last_check (agent, last_file_token, last_check_at)
            VALUES (?, ?, ?)
        """, (agent, top_file["token"], datetime.now().isoformat()))

        for f in new_files:
            cur.execute("""
                INSERT OR REPLACE INTO seen_files (file_token, agent, file_name, first_seen_at)
                VALUES (?, ?, ?, ?)
            """, (f["token"], agent, f["name"], datetime.now().isoformat()))

        conn.commit()

    return new_files


def main():
    import argparse
    parser = argparse.ArgumentParser(description="渔芯任务监听器 watchdog")
    parser.add_argument("--dry-run", action="store_true", help="只检测不通知")
    parser.add_argument("--status", action="store_true", help="查看状态")
    args = parser.parse_args()

    conn = init_state_db()

    if args.status:
        cur = conn.cursor()
        cur.execute("SELECT agent, last_file_token, last_check_at FROM last_check")
        rows = cur.fetchall()
        print("=== 监控状态 ===")
        if rows:
            for r in rows:
                print(f"  {r[0]}: 上次检查 {r[2]}")
        else:
            print("  暂无记录，首次运行将初始化")
        cur.execute("SELECT COUNT(*) FROM seen_files")
        count = cur.fetchone()[0]
        print(f"  已跟踪文件总数: {count}")
        conn.close()
        return

    # 主检测逻辑
    client = get_feishu_client()
    all_new_files = []

    for agent in AGENT_FOLDERS:
        new_files = check_agent_folder(client, conn, agent, dry_run=args.dry_run)
        if new_files:
            all_new_files.append((agent, new_files))

    if not all_new_files:
        print(f"[{datetime.now().isoformat()}] 无新任务文件")
        conn.close()
        return

    # 有新任务，通知玉芬
    lines = ["📋 检测到新任务文件："]
    for agent, files in all_new_files:
        for f in files:
            lines.append(f"• [{agent}] {f['name']}")

    msg = "\n".join(lines)
    print(msg)

    if not args.dry_run:
        # 发送到汇报群
        send_group_message(client, REPORT_CHAT_ID, msg)

    conn.close()


if __name__ == "__main__":
    main()
