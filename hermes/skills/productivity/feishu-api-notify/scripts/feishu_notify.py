#!/usr/bin/env python3
"""Cron-safe Feishu notification sender.

Usage:
    python3 scripts/feishu_notify.py "你的消息内容" <chat_id>

Reads credentials from ~/.hermes/config.yaml at runtime.
"""

import sys, json, yaml, urllib.request

def send_feishu_message(msg: str, receive_id: str, receive_id_type: str = "chat_id") -> str:
    with open("/Users/hua/.hermes/config.yaml") as f:
        cfg = yaml.safe_load(f)
    APP_ID = cfg["FEISHU_APP_ID"]
    APP_SECRET = cfg["FEISHU_APP_SECRET"]

    # Step 1: Get token
    req = urllib.request.Request(
        "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
        data=json.dumps({"app_id": APP_ID, "app_secret": APP_SECRET}).encode(),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        result = json.loads(resp.read())
        if result.get("code") != 0:
            print(f"code: {result.get('code')} msg: {result.get('msg')}")
            return ""
        token = result["tenant_access_token"]

    # Step 2: Send message
    data = {
        "receive_id": receive_id,
        "msg_type": "text",
        "content": json.dumps({"text": msg})
    }
    req = urllib.request.Request(
        f"https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type={receive_id_type}",
        data=json.dumps(data).encode(),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {token}"}
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        result = json.loads(resp.read())
        print(f"code: {result.get('code')} msg: {result.get('msg')}")
        if result.get("code") == 0:
            return result["data"]["message_id"]
        return ""

if __name__ == "__main__":
    msg = sys.argv[1] if len(sys.argv) > 1 else "Cron notification"
    receive_id = sys.argv[2] if len(sys.argv) > 2 else "***SECRET***"
    receive_id_type = "chat_id" if receive_id.startswith("oc_") else "open_id"
    mid = send_feishu_message(msg, receive_id, receive_id_type)
    if mid:
        print(f"Sent: {mid}")