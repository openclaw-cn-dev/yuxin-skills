#!/usr/bin/env python3
"""Feishu notification script for FindEra cron jobs.

Usage:
  python3 feishu_notify.py <message_text>                          # auto fallback chain
  python3 feishu_notify.py <message_text> <chat_id1> [chat_id2...] # explicit targets
  python3 feishu_notify.py --token                                 # refresh token only

No external deps (stdlib only). Reliable in cron/sandbox environments.
"""
import sys, os, re, urllib.request, json

# ── config extraction (no yaml dependency) ──────────────────────────
def _read_feishu_config():
    """Parse FEISHU_APP_ID and FEISHU_APP_SECRET from ~/.hermes/config.yaml."""
    config_path = os.path.expanduser("~/.hermes/config.yaml")
    with open(config_path) as f:
        text = f.read()
    app_id = re.search(r"FEISHU_APP_ID:\s*(\S+)", text)
    app_secret = re.search(r"FEISHU_APP_SECRET:\s*(\S+)", text)
    if not app_id or not app_secret:
        raise SystemExit("FEISHU_APP_ID or FEISHU_APP_SECRET not found in config")
    return app_id.group(1), app_secret.group(1)

# ── default fallback chain ──────────────────────────────────────────
# Bot status (2026-07-21):
#   gm_group    — 400 Bad Request (Bot removed from group) → skip
#   main_group  — working
#   hua_dm      — working (low-priority, direct message to 华哥)
FALLBACK_CHAIN = [
    "***SECRET***",  # 总经理群 (skip on 400/230001)
    "***SECRET***",  # 大群 (primary fallback)
    "***SECRET***",  # 华哥私聊 (last resort)
]

DEAD_CODES = {230001, 400}  # receive_id invalid — skip silently, don't retry

# ── token management ────────────────────────────────────────────────
def get_tenant_token():
    """Obtain tenant_access_token from Feishu API."""
    app_id, app_secret = _read_feishu_config()
    req = urllib.request.Request(
        "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
        data=json.dumps({"app_id": app_id, "app_secret": app_secret}).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        result = json.loads(resp.read())
    token = result["tenant_access_token"]
    print(f"TOKEN_OK: {token[:12]}...", file=sys.stderr)
    return token

def send_message(token, chat_id, text):
    """Send text message to a Feishu chat. Returns (code, msg)."""
    data = {
        "receive_id": chat_id,
        "msg_type": "text",
        "content": json.dumps({"text": text}),
    }
    req = urllib.request.Request(
        "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=chat_id",
        data=json.dumps(data).encode(),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read())
        return result.get("code", -1), result.get("msg", "")
    except urllib.error.HTTPError as e:
        body = json.loads(e.read()) if e.fp else {}
        return body.get("code", e.code), body.get("msg", str(e))

# ── main ────────────────────────────────────────────────────────────
if __name__ == "__main__":
    args = sys.argv[1:]

    # --token: just refresh and print the token
    if args and args[0] == "--token":
        token = get_tenant_token()
        print(token)
        sys.exit(0)

    if not args:
        print("Usage: feishu_notify.py <message> [chat_id ...]", file=sys.stderr)
        sys.exit(1)

    message = args[0]
    targets = args[1:] if len(args) > 1 else FALLBACK_CHAIN

    token = get_tenant_token()

    for chat_id in targets:
        code, msg = send_message(token, chat_id, message)
        if code == 0:
            print(f"SENT: {chat_id[:10]}...")
            break
        elif code in DEAD_CODES:
            print(f"SKIP({code}): {chat_id[:10]}...", file=sys.stderr)
            continue
        else:
            print(f"FAIL({code}): {chat_id[:10]}... {msg[:60]}", file=sys.stderr)
            continue
    else:
        print("ALL_TARGETS_FAILED", file=sys.stderr)
        sys.exit(2)