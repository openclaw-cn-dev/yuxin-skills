#!/usr/bin/env python3
"""
feishu_token.py — 获取飞书 tenant_access_token
用法: python3 /tmp/feishu_token.py
输出: {"code":0,"tenant_access_token":"t-xxx"...}

⚠️ 凭据从 ~/.hermes/.env 读取 (FEISHU_APP_ID / FEISHU_APP_SECRET)。
   不要在脚本里硬编码 app_secret —— 飞书 app 重置后硬编码值会失效，
   报 code 10014 "app secret invalid"。
"""
import os, sys, json, urllib.request

ENV_PATH = os.path.expanduser('~/.hermes/.env')
if not os.path.exists(ENV_PATH):
    print(f"ERROR: env file not found: {ENV_PATH}", file=sys.stderr)
    sys.exit(1)

with open(ENV_PATH) as f:
    for line in f:
        line = line.strip()
        if line.startswith('FEISHU_APP_') and '=' in line and not line.startswith('#'):
            k, v = line.split('=', 1)
            os.environ.setdefault(k, v)

app_id = os.environ.get('FEISHU_APP_ID')
app_secret = os.environ.get('FEISHU_APP_SECRET')
if not app_id or not app_secret:
    print("ERROR: FEISHU_APP_ID / FEISHU_APP_SECRET not set in env file", file=sys.stderr)
    sys.exit(1)

body = json.dumps({"app_id": app_id, "app_secret": app_secret}).encode('utf-8')
req = urllib.request.Request(
    'https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal',
    data=body, method='POST'
)
req.add_header('Content-Type', 'application/json')
with urllib.request.urlopen(req, timeout=10) as r:
    resp = json.loads(r.read())
print(json.dumps(resp, ensure_ascii=False))
