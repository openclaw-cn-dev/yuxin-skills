#!/usr/bin/env python3
"""Generic Feishu text-message sender using Hermes config credentials.

Reads FEISHU_APP_ID / FEISHU_APP_SECRET from ~/.hermes/config.yaml at runtime
(never hardcode credentials; never paste credential lines from redacted tool
output — see references/copy-paste-redaction-pitfall.md).

Usage:
  python3 send_text.py <chat_id> "<message>"        # inline text
  python3 send_text.py <chat_id> -f message.txt     # text from file
  cat message.txt | python3 send_text.py <chat_id>  # text from stdin

chat_id is the oc_... group id (receive_id_type=chat_id).
Prints the om_... message_id on success — quote it as the delivery receipt.
"""
import json
import sys
import urllib.request
from pathlib import Path

import yaml

CONFIG = Path.home() / ".hermes" / "config.yaml"
TOKEN_URL = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
SEND_URL = "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=chat_id"


def get_token() -> str:
    cfg = yaml.safe_load(CONFIG.read_text())
    req = urllib.request.Request(
        TOKEN_URL,
        data=json.dumps(
            {"app_id": cfg["FEISHU_APP_ID"], "app_secret": cfg["FEISHU_APP_SECRET"]}
        ).encode(),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        result = json.loads(resp.read())
    assert result.get("code") == 0, f"Token fetch failed: {result}"
    return result["tenant_access_token"]


def send(chat_id: str, text: str) -> str:
    token = get_token()
    data = {
        "receive_id": chat_id,
        "msg_type": "text",
        "content": json.dumps({"text": text}),
    }
    req = urllib.request.Request(
        SEND_URL,
        data=json.dumps(data).encode(),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        result = json.loads(resp.read())
    # Feishu returns HTTP 200 even on failures (230002 bad chat_id, bot not in
    # group, ...) — always assert on the body code, not the HTTP status.
    assert result.get("code") == 0, f"Send failed: {result}"
    return result["data"]["message_id"]


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    chat_id = sys.argv[1]
    if "-f" in sys.argv:
        text = Path(sys.argv[sys.argv.index("-f") + 1]).read_text()
    elif len(sys.argv) > 2:
        text = sys.argv[2]
    else:
        text = sys.stdin.read()
    print("Sent:", send(chat_id, text))
