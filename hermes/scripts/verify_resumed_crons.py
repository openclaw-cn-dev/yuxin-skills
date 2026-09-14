#!/usr/bin/env python3
"""verify_resumed_crons.py — 验证恢复后的 11 个 cron 路径有效性（v3 检查）"""
import json, os, re

d = json.load(open("/Users/hua/.hermes/cron/jobs.json"))
TARGETS = ["a5f2061c110c","d01b4320aead","e2052c9b44c8","19d72d5151ca",
           "29c08e9341ca","8f2120bcaf3d","4ff1449bd47a","5fb65e1ab750",
           "cadaf7d46252","9b6d34960c50","c6efc06949f1"]

print(f"{'cron':<14}{'名称':<26}{'enabled':<8}{'旧路径残留':<10}{'关键路径有效性'}")
print("-" * 80)
issues = []
for j in d.get("jobs", []):
    jid = j.get("id", "")
    if jid[:12] not in TARGETS:
        continue
    full = json.dumps(j, ensure_ascii=False)
    stale = re.findall(r"文档库/(?:4-360行项目调研|1-通用知识|2-专业知识|3-公司项目资料)[/\"']?", full)
    # 抽查 prompt 中的绝对路径是否存在
    paths = re.findall(r"/Users/hua/[\w\u4e00-\u9fff./-]+", full)
    missing = [p for p in paths if not os.path.exists(p.split('（')[0].rstrip('/.,;'))][:3]
    status = "❌"+str(len(stale)) if stale else "✓"
    miss_str = "; ".join(missing) if missing else "-"
    if stale or missing:
        issues.append((jid[:12], j.get("name",""), stale, missing))
    print(f"{jid[:12]:<14}{j.get('name','')[:24]:<26}{str(j.get('enabled')):<8}{status:<10}{miss_str[:60]}")

print()
if issues:
    print(f"⚠️ {len(issues)} 个 cron 需要路径修正:")
    for jid, name, stale, missing in issues:
        print(f"  {jid} {name}: stale={stale[:2]} missing={missing[:2]}")
else:
    print("✓ 全部路径有效")
