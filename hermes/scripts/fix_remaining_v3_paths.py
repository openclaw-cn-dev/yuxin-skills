#!/usr/bin/env python3
"""fix_remaining_v3_paths.py — 修正恢复后 cron 的残留旧路径

1. d01b4320aead claude-code-research-weekly: 3-公司项目资料 → A2-公司运营/部门空间
2. e2052c9b44c8 工作空间每周审计: 3-公司项目资料 → A2-公司运营 + audit_workspace.py 审计范围需 v3
3. a5f2061c110c 360行主控: 调研项目清单.md 路径指错(C1 下没有清单,在 A3) — 之前替换时把清单路径也换成 C1 了,需改回 A3
"""
import json

MAIN = "/Users/hua/.hermes/cron/jobs.json"
d = json.load(open(MAIN))

FIXES = {
    # claude-code-weekly: 调研产出原写 3-公司项目资料 → v3 部门空间
    "d01b4320aead": [
        ("/Users/hua/rkr_staging/文档库/3-公司项目资料/301-智能体/", "/Users/hua/rkr_staging/文档库/A-渔芯科技/A2-公司运营/部门空间/zhenglishi/"),
        ("/Users/hua/rkr_staging/文档库/3-公司项目资料/", "/Users/hua/rkr_staging/文档库/A-渔芯科技/A2-公司运营/"),
        ("文档库/3-公司项目资料/301-智能体/", "文档库/A-渔芯科技/A2-公司运营/部门空间/zhenglishi/"),
        ("文档库/3-公司项目资料/", "文档库/A-渔芯科技/A2-公司运营/"),
    ],
    # 工作空间审计: 审计范围 3-公司项目资料 → A2-公司运营/部门空间
    "e2052c9b44c8": [
        ("3-公司项目资料", "A-渔芯科技/A2-公司运营/部门空间"),
        ("文档库/3-公司项目资料/", "文档库/A-渔芯科技/A2-公司运营/部门空间/"),
    ],
    # 360行主控: 之前批量替换把"调研项目清单.md"也带成了 C1 前缀,清单实际在 A3
    "a5f2061c110c": [
        ("/Users/hua/rkr_staging/文档库/C-渔芯独角兽/C1-360行种子池/调研项目清单.md",
         "/Users/hua/rkr_staging/文档库/A-渔芯科技/A3-基础设施/调研项目清单.md"),
    ],
}

for j in d.get("jobs", []):
    jid = j.get("id", "")
    if jid not in FIXES:
        continue
    p = j.get("prompt", "")
    orig = p
    for old, new in FIXES[jid]:
        p = p.replace(old, new)
    if p != orig:
        j["prompt"] = p
        print(f"fixed: {jid[:12]} {j.get('name','')}")
        # 显示修正后的关键行
        for line in p.splitlines():
            if "文档库" in line and ("清单" in line or "资料" in line or "部门空间" in line):
                print("   ", line.strip()[:110])
                break

json.dump(d, open(MAIN, "w"), ensure_ascii=False, indent=2)
print("done")
