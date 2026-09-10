#!/usr/bin/env python3
"""Ark 账户欠费探针（laomo task #11 definitive POST）— laomo-heartbeat skill 固化版。

来源：R204 首建 /tmp/ark_unblock_probe_r204.py（/tmp 易失），R274 固化到本 skill scripts/。
用途：距上次 definitive POST >4h（R171 规则）时，重探账户 2117577211 充值状态。
  - 403 'overdue balance' = 零成本诊断 → STILL_OVERDUE（唯一动作=华哥充值）
  - 200 = UNBLOCKED（充值生效 → 走 1x 2048x2048 生成冒烟闭环 + 复核 task #11 写路径）
用法：python3 ark_unblock_probe.py
注意：脚本内部已 pop 掉 session 残留的 VOLC_ARK_API_KEY / ARK_API_KEY（等效 env -u），
      防止污染 key 造成 401 假象（R248/R249 教训）。
Pitfall（R274 实测）：必须用 photo_restore.MODEL（图像模型 doubao-seedream-5-0-260128）。
  chat model id 会得 404 InvalidEndpointOrModel —— 那是 model 路由层报错，
  与账户欠费/认证无关，勿据此改判账户状态。
"""
import hashlib
import json
import os
import sys

# 等效 env -u：先清掉 session 残留 key，强制走 .env 直读
for k in ("VOLC_ARK_API_KEY", "ARK_API_KEY"):
    os.environ.pop(k, None)

sys.path.insert(0, "/Users/hua/.hermes/profiles/laomo/scripts")

try:
    import photo_restore
except ImportError as e:
    print(f"IMPORT_FAIL: photo_restore 不可用（{e}）")
    print("期望路径: /Users/hua/.hermes/profiles/laomo/scripts/photo_restore.py")
    print("勿自行猜测 endpoint 重建 —— 探针语义以 photo_restore._call 为准")
    sys.exit(2)

key = photo_restore.get_api_key()
print("key_len:", len(key), "prefix:", key[:12], "md5:", hashlib.md5(key.encode()).hexdigest()[:8])
print("model:", photo_restore.MODEL, "(须为 seedream 图像模型；404=路由层报错非欠费信号)")

payload = {
    "model": photo_restore.MODEL,
    "prompt": "一朵红色玫瑰 简单测试",
    "size": "2048x2048",
    "response_format": "url",
    "watermark": False,
}
try:
    result = photo_restore._call(payload)
    url = result.get("data", [{}])[0].get("url", "")
    print("POST_SUCCESS")
    print("url_present:", bool(url))
    print("model:", result.get("model", "n/a"))
    print("usage:", json.dumps(result.get("usage", {}), ensure_ascii=False))
    print("VERDICT: UNBLOCKED —— 充值已生效，走冒烟闭环 + 复核 task #11 写路径")
except RuntimeError as e:
    msg = str(e)
    print("POST_FAILED:", msg[:300])
    if "overdue" in msg.lower() or "AccountOverdue" in msg or "403" in msg:
        print("VERDICT: STILL_OVERDUE（唯一动作=华哥充值账户 2117577211，403 零成本）")
    elif "401" in msg or "Authentication" in msg:
        print("VERDICT: KEY_AUTH_FAIL —— 先做 .env 指纹扫描（LEN/prefix/md5），勿单点定论")
    elif "404" in msg:
        print("VERDICT: MODEL_OR_ENDPOINT_ERROR —— model id 错误或无权限；不反映账户欠费状态，勿据此改判")
    else:
        print("VERDICT: OTHER_ERROR —— 记录原文，下轮复探")
