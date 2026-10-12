#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 玉芬管理进化扫描 2026-10-11 chat_id 实测测活 (实证9)
import urllib.request, json, os, re

# 从 .env 读凭据 (实证5: 硬编码 secret 已失效)
env = open('/Users/hua/.hermes/.env').read()
def getenv(k):
    m = re.search(r'^%s\s*=\s*(.+)$' % re.escape(k), env, re.M)
    return m.group(1).strip().strip('"').strip("'") if m else None

APP_ID = getenv('FEISHU_APP_ID')
APP_SECRET = getenv('FEISHU_APP_SECRET')
print("APP_ID:", APP_ID[:8]+"..." if APP_ID else None, "| secret len:", len(APP_SECRET) if APP_SECRET else 0)

def req(url, data=None, token=None):
    r = urllib.request.Request(url, data=json.dumps(data).encode() if data else None,
        headers={"Content-Type":"application/json", **({"Authorization":f"Bearer {token}"} if token else {})})
    with urllib.request.urlopen(r, timeout=15) as resp:
        return json.loads(resp.read())

# 1. token
try:
    tr = req("https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
             {"app_id": APP_ID, "app_secret": APP_SECRET})
    print("token code:", tr.get("code"))
    if tr.get("code") != 0:
        print("TOKEN FAIL:", tr.get("msg"), tr.get("code"))
        raise SystemExit
    token = tr["tenant_access_token"]
except Exception as e:
    print("TOKEN EXC:", e)
    raise SystemExit

# 2. chat_id liveness
chats = {
 "***SECRET***": "华哥p2p(origin主通道)",
 "***SECRET***": "总经理群(上轮判定已解散)",
 "***SECRET***": "afu",
 "***SECRET***": "heidou",
 "***SECRET***": "laomo",
 "***SECRET***": "maodou-backup",
 "***SECRET***": "maodou-archive",
 "***SECRET***": "xiaobao",
 "***SECRET***": "xiaobao-origin",
 "***SECRET***": "quant",
 "***SECRET***": "zhenglishi",
}
print("\nchat_id 测活:")
for cid, label in chats.items():
    try:
        r = req(f"https://open.feishu.cn/open-apis/im/v1/chats/{cid}", token=token)
        code = r.get("code")
        if code == 0:
            name = r.get("data",{}).get("name","?")
            print(f"  ALIVE  code=0  {label:<28} {cid[:16]}... name={name}")
        else:
            print(f"  DEAD   code={code} msg={r.get('msg','')[:40]}  {label}  {cid[:16]}...")
    except Exception as e:
        print(f"  EXC    {label}  {cid[:16]}... {str(e)[:60]}")
