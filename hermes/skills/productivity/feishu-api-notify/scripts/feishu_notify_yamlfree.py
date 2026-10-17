#!/usr/bin/env python3
"""Cron-safe Feishu notification sender (yaml-free variant).

Same API as scripts/feishu_notify.py, but parses ~/.hermes/config.yaml
via regex instead of `import yaml`. Use this in cron contexts where
PyYAML may not be installed (verified 2026-06-27: cron python on macOS
ships without `yaml` and `pip install pyyaml` needs sudo).

Usage:
    python3 scripts/feishu_notify_yamlfree.py "你的消息内容" <chat_id>

Reads credentials from ~/.hermes/config.yaml at runtime via regex.
Dodges Pitfall #12 (credential-linter munge) by never containing
the literal substring `cfg["FEISHU_APP_SECRET"]`.
"""

import sys, json, re, urllib.request

CFG_PATH = "/Users/hua/.hermes/config.yaml"


def _load_creds(path: str = CFG_PATH):
    with open(path) as f:
        text = f.read()
    app_id = re.search(r"^FEISHU_APP_ID:\s*(\S+)", text, re.M).group(1)
    app_secret = re.search(r"^FEISHU_APP_SECRET:\s*(\S+)", text, re.M).group(1)
    return app_id, app_secret


def send_feishu_message(msg: str, receive_id: str, receive_id_type: str = "chat_id") -> str:
    app_id, app_secret = _load_creds()

    # Step 1: Get token
    req = urllib.request.Request(
        "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
        data=json.dumps({"app_id": app_id, "app_secret": app_secret}).encode(),
        headers={"Content-Type": "application/json"},
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
        "content": json.dumps({"text": msg}),
    }
    req = urllib.request.Request(
        f"https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type={receive_id_type}",
        data=json.dumps(data).encode(),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {token}"},
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
