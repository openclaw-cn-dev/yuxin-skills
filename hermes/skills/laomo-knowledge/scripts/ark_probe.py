#!/usr/bin/env python3
"""Ark (Volcengine) account/model status probe — canonical copy, laomo-knowledge v1.88.73 R741.

R741 定性: desc/SOP 历史引用的 ark_unblock_probe.py 盘上不存在; /tmp/ark_probe.py 才是实际 canonical。
本副本固化自 /tmp/ark_probe.py，R742+ 一律调本副本，不再赌 /tmp 存活。

key 装载: VOLC_ARK_API_KEY 从 /Users/hua/.hermes/.env（fallback: laomo profile .env）读取，无硬编码 secret。

verdict 状态机三分法（R741 确立）:
  - models list 403 "overdue balance"                  -> 欠费阻塞态（唯一动作: 华哥充值账户 2117577211）
  - models list 200 + image POST 404 ModelNotOpen      -> 欠费已解除、模型服务未开通态（唯一动作: Ark Console 激活模型）
  - models list 200 + image POST 200                   -> 全通态（task #11 Ark 侧可关）

Usage: python3 ark_probe.py
"""
import os, json, urllib.request, urllib.error

def load_key():
    for p in ["/Users/hua/.hermes/.env", "/Users/hua/.hermes/profiles/laomo/.env"]:
        if os.path.exists(p):
            with open(p) as f:
                for line in f:
                    if "VOLC_ARK_API_KEY" in line and "=" in line and not line.strip().startswith("#"):
                        return line.split("=", 1)[1].strip().strip('"').strip("'")
    return None

key = load_key()
print("key prefix:", key[:12] if key else "NONE", "len:", len(key) if key else 0)

def post(url, payload):
    req = urllib.request.Request(url, data=json.dumps(payload).encode(), method="POST")
    req.add_header("Authorization", f"Bearer {key}")
    req.add_header("Content-Type", "application/json")
    try:
        r = urllib.request.urlopen(req, timeout=20)
        body = r.read().decode()
        return r.status, body[:500]
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()[:500]
    except Exception as e:
        return "ERR", str(e)[:300]

# 1. models list — 账户级状态判定（403 overdue / 200）
try:
    req = urllib.request.Request("https://ark.cn-beijing.volces.com/api/v3/models")
    req.add_header("Authorization", f"Bearer {key}")
    r = urllib.request.urlopen(req, timeout=20)
    print("models list:", r.status, r.read().decode()[:300])
except urllib.error.HTTPError as e:
    print("models list HTTP", e.code, e.read().decode()[:300])
except Exception as e:
    print("models list ERR", str(e)[:200])

# 2. seedream image models — ModelNotOpen(404) vs 200 判别
models = [
    "doubao-seedream-4-0-250828",
    "***SECRET***",
    "***SECRET***",
    "***SECRET***",
]
for m in models:
    code, body = post("https://ark.cn-beijing.volces.com/api/v3/images/generations",
                      {"model": m, "prompt": "a cat", "size": "1024x1024"})
    print(f"[{m}] {code} {body[:200]}")

# 3. chat models — 账户级状态二次确认
for m in ["doubao-seed-1-6-250615", "doubao-1-5-pro-32k-250115"]:
    code, body = post("https://ark.cn-beijing.volces.com/api/v3/chat/completions",
                      {"model": m, "messages": [{"role": "user", "content": "hi"}]})
    print(f"[chat {m}] {code} {body[:200]}")
