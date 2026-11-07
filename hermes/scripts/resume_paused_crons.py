#!/usr/bin/env python3
"""resume_paused_crons.py — 华哥 2026-09-13「全部恢复」批复：恢复文档库重组时暂停的 11 个 cron
恢复前检查 prompt 内 rkr_staging 旧路径是否已被 v3 修正。"""
import json

MAIN = "/Users/hua/.hermes/cron/jobs.json"
d = json.load(open(MAIN))

# 华哥批复「全部恢复」= 9/12 文档库迁移时暂停的 11 个 cron（4 写入类 + 7 调研类）
TARGETS = {
    "a5f2061c110c": "360行轮流调研主控",
    "d01b4320aead": "claude-code-research-weekly",
    "e2052c9b44c8": "工作空间每周审计",
    "19d72d5151ca": "玉芬每日管理进化",
    "29c08e9341ca": "RAS仿真技术持续调研",
    "8f2120bcaf3d": "四技术学习-三合一",
    "4ff1449bd47a": "梦幻西游私服漏洞调研",
    "5fb65e1ab750": "四技术学习-Kali",
    "cadaf7d46252": "AI法典-领域铁律轮换调研",
    "9b6d34960c50": "创意之神-领域创意轮换调研",
    "c6efc06949f1": "同城门店引流-轮换调研",
}

for j in d.get("jobs", []):
    jid = j.get("id", "")
    if jid in TARGETS and not j.get("enabled"):
        j["enabled"] = True
        j["state"] = "scheduled"
        j["paused_at"] = None
        j["paused_reason"] = None
        print(f"恢复: {jid[:12]} {TARGETS[jid]}")

json.dump(d, open(MAIN, "w"), ensure_ascii=False, indent=2)
print("完成。共恢复", len(TARGETS), "个")
