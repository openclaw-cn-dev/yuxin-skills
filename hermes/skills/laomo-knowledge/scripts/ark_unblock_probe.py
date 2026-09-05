#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Ark definitive POST unblock probe — R201 范式固化版 (2026-09-05 R214 轮沉淀)

用途: task #11 (AI 照片修复/老照片上色) 唯一 unblock 依赖 = 火山引擎 Ark 账户
2117577211 充值状态的最小化 definitive 检测。

执行窗口: 距上次 POST 探测 >=4h (R171 最小化规则) 才跑, 不到 4h 跳过。
零成本原理: 欠费态 POST 返 403, 不产生生成费用 (403 零成本下 R167 GET-only
规则不适用, R201 澄清)。充值成功的瞬间, 本次 POST 直接成为核心能力冒烟测试
(1x doubao-seedream 2048x2048 生成)。

用法:
  python3 /Users/hua/.hermes/skills/laomo-knowledge/scripts/ark_unblock_probe.py

判读 (stdout 末行 VERDICT):
  STILL_OVERDUE  -> 账户仍欠费, 华哥充值仍为唯一动作 (403 零成本, 状态维持)
  KEY_AUTH_FAIL  -> key 认证失效 (401), 需换 key
  OTHER_ERROR    -> 其它错误, 读 POST_FAILED 报文
  POST_SUCCESS   -> 充值已生效, 记录 url/usage, task #11 核心能力恢复

历史: R201-R213 用 /tmp/ark_unblock_probe_r204.py (macOS /tmp 不保证跨轮/跨天
存活), R214 固化为 skill 内静态脚本。依赖
/Users/hua/.hermes/profiles/laomo/scripts/photo_restore.py 的
get_api_key / MODEL / _call (核心能力文件, verify-heartbeat-infra.sh 每轮
验证存在性)。
"""
import json
import sys

sys.path.insert(0, "/Users/hua/.hermes/profiles/laomo/scripts")
import photo_restore  # noqa: E402


def main():
    key = photo_restore.get_api_key()
    print("key_len:", len(key), "prefix:", key[:12])

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
        print("VERDICT: POST_SUCCESS")
    except RuntimeError as e:
        msg = str(e)
        print("POST_FAILED:", msg[:300])
        if "AccountOverdue" in msg or "overdue" in msg.lower() or "403" in msg:
            print("VERDICT: STILL_OVERDUE")
        elif "401" in msg or "Authentication" in msg:
            print("VERDICT: KEY_AUTH_FAIL")
        else:
            print("VERDICT: OTHER_ERROR")


if __name__ == "__main__":
    main()
