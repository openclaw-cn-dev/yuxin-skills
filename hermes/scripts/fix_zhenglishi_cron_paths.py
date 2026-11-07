#!/usr/bin/env python3
"""fix_zhenglishi_cron_paths.py — 学习助手 5 个调研 cron 的写入/读取路径升级到文档库 v3

旧 → 新映射:
  /Users/hua/rkr_staging/文档库/4-360行项目调研/调研项目清单.md
    → /Users/hua/rkr_staging/文档库/A-渔芯科技/A3-基础设施/调研项目清单.md
  /Users/hua/rkr_staging/文档库/4-360行项目调研/
    → /Users/hua/rkr_staging/文档库/C-渔芯独角兽/C1-360行种子池/
  /Users/hua/rkr_staging/文档库/C-渔芯独角兽/C1-360行种子池/4-360行项目调研/... (主控cron残留中间层)
    → /Users/hua/rkr_staging/文档库/C-渔芯独角兽/C1-360行种子池/...
staging_save.py 写入指令 → 直接写项目目录(v3)
"""
import json, shutil, re

JOBS = "/Users/hua/.hermes/profiles/zhenglishi/cron/jobs.json"
shutil.copy(JOBS, JOBS + ".bak-20260913-v3")

data = json.load(open(JOBS))
changed = []

V3_NOTE = ("\n\n### 文档库 v3 路径修正(2026-09-13 玉芬下发)\n"
           "- 文档库已重组为 ABCZ 四版块,`4-360行项目调研/` 旧顶层目录已不存在\n"
           "- 调研清单现位于: `/Users/hua/rkr_staging/文档库/A-渔芯科技/A3-基础设施/调研项目清单.md`\n"
           "- 调研成果/调研笔记直接写入: `/Users/hua/rkr_staging/文档库/C-渔芯独角兽/C1-360行种子池/<项目目录>/`\n"
           "- `staging_save.py` 已废用(RKR scanner 停机),严禁使用;直接 write_file/cp 到项目目录\n"
           "- 权威索引: `/Users/hua/rkr_staging/文档库/INDEX.md` v3\n")

for j in data.get("jobs", []):
    p = j.get("prompt") or ""
    if not p:
        continue
    orig = p

    # 1) 主控 cron 残留中间层(4-360行项目调研 挂在 C1 下)
    p = p.replace(
        "/Users/hua/rkr_staging/文档库/C-渔芯独角兽/C1-360行种子池/4-360行项目调研/",
        "/Users/hua/rkr_staging/文档库/C-渔芯独角兽/C1-360行种子池/")
    # 2) 旧顶层路径 → 新路径(先清单后目录,避免二次替换)
    p = p.replace(
        "/Users/hua/rkr_staging/文档库/4-360行项目调研/调研项目清单.md",
        "/Users/hua/rkr_staging/文档库/A-渔芯科技/A3-基础设施/调研项目清单.md")
    p = p.replace(
        "/Users/hua/rkr_staging/文档库/4-360行项目调研/<项目目录>/",
        "/Users/hua/rkr_staging/文档库/C-渔芯独角兽/C1-360行种子池/<项目目录>/")
    p = p.replace(
        "/Users/hua/rkr_staging/文档库/4-360行项目调研/",
        "/Users/hua/rkr_staging/文档库/C-渔芯独角兽/C1-360行种子池/")
    # 3) staging_save 写入指令 → v3 直接写
    p = p.replace(
        "- **写入**: `python3 ~/.hermes/scripts/staging_save.py --source research --agent zhenglishi`",
        "- **写入(v3)**: 直接 write_file/cp 到 `/Users/hua/rkr_staging/文档库/C-渔芯独角兽/C1-360行种子池/<项目目录>/`(staging_save.py 已废用)")
    # 4) "用 staging_save.py,禁止直接写 ~/rkr_staging/" 这条旧规则反转
    p = p.replace(
        "7. **写入路径**:用 staging_save.py,禁止直接写 ~/rkr_staging/",
        "7. **写入路径(v3)**:直接 write_file/cp 到项目目录 `~/rkr_staging/文档库/C-渔芯独角兽/C1-360行种子池/<项目目录>/`(staging_save.py 已废用)")
    # 5) "❌ 直接写 ~/rkr_staging/文档库/...(RKR 归档层)" 旧严禁反转
    p = p.replace(
        "- ❌ 直接写 `~/rkr_staging/文档库/...`(RKR 归档层)",
        "- ❌ 走 staging_save.py 中转站(已废用,scanner 停机)/重建 `4-360行项目调研/` 旧目录")
    # 6) "❌ 直接写 RKR 归档层"
    p = p.replace("- ❌ 直接写 RKR 归档层",
                  "- ❌ 重建 `4-360行项目调研/` 旧顶层目录(v3 已并入 C1-360行种子池)")

    if p != orig:
        j["prompt"] = p
        # 幂等注入 v3 说明块
        if "文档库 v3 路径修正" not in p:
            j["prompt"] = p + V3_NOTE
        changed.append((j.get("id", "")[:12], j.get("name", "")))

json.dump(data, open(JOBS, "w"), ensure_ascii=False, indent=2)
print("已修正 cron:")
for cid, name in changed:
    print("  ", cid, name)

# 主控 cron(玉芬库里的 a5f2061c110c)也要改,虽然 disabled,防止重新启用时写错
MAIN = "/Users/hua/.hermes/cron/jobs.json"
shutil.copy(MAIN, MAIN + ".bak-20260913-v3")
d2 = json.load(open(MAIN))
c2 = []
for j in d2.get("jobs", []):
    p = j.get("prompt") or ""
    orig = p
    p = p.replace(
        "/Users/hua/rkr_staging/文档库/C-渔芯独角兽/C1-360行种子池/4-360行项目调研/",
        "/Users/hua/rkr_staging/文档库/C-渔芯独角兽/C1-360行种子池/")
    p = p.replace(
        "/Users/hua/rkr_staging/文档库/4-360行项目调研/调研项目清单.md",
        "/Users/hua/rkr_staging/文档库/A-渔芯科技/A3-基础设施/调研项目清单.md")
    p = p.replace(
        "/Users/hua/rkr_staging/文档库/4-360行项目调研/",
        "/Users/hua/rkr_staging/文档库/C-渔芯独角兽/C1-360行种子池/")
    if p != orig:
        j["prompt"] = p
        c2.append((j.get("id", "")[:12], j.get("name", "")))
json.dump(d2, open(MAIN, "w"), ensure_ascii=False, indent=2)
print("玉芬主库已修正 cron:")
for cid, name in c2:
    print("  ", cid, name)
