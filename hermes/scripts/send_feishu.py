#!/usr/bin/env python3
import subprocess
import json
import os

FEISHU_TOKEN_FILE = '/Users/hua/.hermes/scripts/feishu_token.txt'
CHAT_ID = '***SECRET***'

def get_token():
    with open(FEISHU_TOKEN_FILE, 'r') as f:
        return f.read().strip()

def send_message(text):
    token = get_token()
    data = {
        "receive_id": CHAT_ID,
        "msg_type": "text",
        "content": json.dumps({"text": text})
    }
    cmd = [
        'curl', '-s', '-X', 'POST',
        'https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=chat_id',
        '-H', f'Authorization: Bearer {token}',
        '-H', 'Content-Type: application/json',
        '-d', json.dumps(data)
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    print(f"Sent: {text[:30]}...")
    print(f"Response: {result.stdout[:200] if result.stdout else result.stderr[:200]}")

# Step 1: Send start message
send_message("🔄 正在执行每日例行重启Hermes Gateway和Docker，预计2-3分钟恢复。")
