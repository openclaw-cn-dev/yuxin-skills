#!/usr/bin/env python3
"""Cron-safe Feishu notification sender.

Usage:
    python3 scripts/feishu_notify.py "你的消息内容" <chat_id>

Reads credentials from ~/.hermes/config.yaml at runtime.
"""

import sys, json, os, re, urllib.request

def _find_config_file():
    """Locate config.yaml across environments (Mac vs Windows yuxin host)."""
    candidates = [
        os.path.join(os.environ.get("HERMES_HOME", ""), "config.yaml") if os.environ.get("HERMES_HOME") else None,
        "D:/yuxin/hermes/config.yaml",            # Windows 主力机 (2026-11-12)
        os.path.expanduser("~/.hermes/config.yaml"),  # Mac / generic
    ]
    for p in candidates:
        if p and os.path.isfile(p):
            return p
    raise FileNotFoundError("config.yaml not found in HERMES_HOME, D:/yuxin/hermes/, or ~/.hermes/")

def send_feishu_message(msg: str, receive_id: str, receive_id_type: str = "chat_id") -> str:
    cfg_path = _find_config_file()
    with open(cfg_path, encoding="utf-8") as f:
        text = f.read()
    # config.yaml uses `KEY: value` (YAML-ish); .env uses `KEY=value`.
    m = re.search(r"^FEISHU_APP_ID\s*[:=]\s*(\S+)", text, re.M) or re.search(r"FEISHU_APP_ID\s*[:=]\s*(\S+)", text)
    APP_ID = m.group(1).strip().strip('"\'')
    m = re.search(r"^FEISHU_APP_SECRET\s*[:=]\s*(\S+)", text, re.M) or re.search(r"FEISHU_APP_SECRET\s*[:=]\s*(\S+)", text)
    APP_SECRET = m.group(1).strip().strip('"\'')

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