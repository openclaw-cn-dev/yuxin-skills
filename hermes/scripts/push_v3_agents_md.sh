#!/usr/bin/env bash
# push_v3_agents_md.sh — 给 9 个同事 profile 的 AGENTS.md 注入文档库 v3 资料入库标准
# 用 patch 风格:在 "## 📂 资料写入与读取路径 SOP" 标题后插入 v3 标准,并把旧的 staging_save/staging_query 行替换掉
set -euo pipefail

STAMP="2026-09-13 v3"

insert_block () {
  local agent_name="$1"
  local file="/Users/hua/.hermes/profiles/${agent_name}/AGENTS.md"
  [ -f "$file" ] || { echo "SKIP(无文件): $file"; return; }
  # 幂等:已含 v3 标记则跳过
  if grep -q "文档库 v3 入库标准" "$file"; then
    echo "SKIP(已有v3): $agent_name"
    return
  fi
  python3 - "$file" "$agent_name" "$STAMP" <<'PYEOF'
import sys, re
path, agent, stamp = sys.argv[1], sys.argv[2], sys.argv[3]
text = open(path, encoding="utf-8").read()

block = f"""
> ⚠️ **文档库 v3 入库标准(2026-09-13 玉芬统一下发)**:RKR scanner 已停、`staging_save.py`/`staging_query.py` 已**废用**(写 ~/.hermes/staging 死区/RKR API 已停)。资料一律**直接写文件**到下列指定目录。权威索引:`/Users/hua/rkr_staging/文档库/INDEX.md`(v3)。旧顶层目录(1-通用知识/2-专业知识/3-公司项目资料/4-360行项目调研)已不存在,禁止重建。

### 资料落位速查(直接 write_file/cp,不走中转站)

| 资料类型 | 落位目录 |
|---|---|
| {agent} 本职结果性报告(方案/分析/SOP) | `~/rkr_staging/文档库/A-渔芯科技/A2-公司运营/部门空间/{agent}/` |
| 水产/RAS 专业资料 | `~/rkr_staging/文档库/A-渔芯科技/A1-水产养殖RAS/` 下贴切子目录 |
| 业务结果性报告(竞品/产品/技术/合同) | `~/rkr_staging/文档库/A-渔芯科技/A2-公司运营/<业务子目录>/` |
| 新行业/种子项目调研 | `~/rkr_staging/文档库/C-渔芯独角兽/C1-360行种子池/NN-项目名/`(新项目编号从 75 起) |
| 跨版块通用知识 | `~/rkr_staging/文档库/Z-共享/Z1-通用学科知识/` 下贴切子目录 |
| 量化研报(宽博士专用) | `~/rkr_staging/文档库/A-渔芯科技/A2-公司运营/量化研究/` |

**硬性禁区**:Z2/Z3/Z4、C2 手语数据集、`渔芯项目/`、`A3-基础设施/`(cron 管道区)。拿不准放哪 → 先看 INDEX.md 判断流程,再问玉芬。
"""

# 1) 在 SOP 标题后插入 v3 块
anchor = "## 📂 资料写入与读取路径 SOP"
if anchor in text:
    text = text.replace(anchor, anchor + "\n" + block, 1)

# 2) 替换写资料表里的 staging_save 行(通用+本领域)
text = re.sub(r'\| \*\*通用知识调研\*\* \| `python3 ~/\.hermes/scripts/staging_save\.py --source research --agent ' + agent + r'` \|',
              f'| **通用知识调研** | 直接写 `~/rkr_staging/文档库/Z-共享/Z1-通用学科知识/` 贴切子目录(v3,不走中转站) |', text)
# 本领域行(各 agent 第二行文案不同,统一兜底替换任意残留 staging_save 行)
text = re.sub(r'\| \*\*([^*]+)\*\* \| `python3 ~/\.hermes/scripts/staging_save\.py --source ' + agent + r' --agent ' + agent + r'` \|',
              f'| **\\1** | 直接写 `~/rkr_staging/文档库/A-渔芯科技/A2-公司运营/部门空间/{agent}/`(v3) |', text)

# 3) 替换读资料 staging_query 块
text = re.sub(r'```bash\npython3 ~/\.hermes/scripts/staging_query\.py (search|stats)[^\n]*\n```',
              '```bash\n# v3: staging_query.py 已废用(RKR API 停)。直接 ls/grep 文档库目录找资料:\nls ~/rkr_staging/文档库/  &&  grep -rl "<关键词>" ~/rkr_staging/文档库/A-渔芯科技/ --include="*.md" | head\n```', text)

# 4) 严禁清单第 1/2/4 条改写(归档层已重组)
text = text.replace("❌ 直接写 `~/rkr_staging/文档库/1-通用知识/...`(RKR 归档层)",
                    "❌ 重建旧顶层目录 `1-通用知识/` `2-专业知识/` `3-公司项目资料/` `4-360行项目调研/`(已重组进 ABCZ 四版块)")
text = text.replace("❌ 直接读 `~/rkr_staging/文档库/通用知识库/` 文件系统(走 staging_query.py)",
                    "❌ 引用 `通用知识库/`、`cleaned/` 旧路径(已并入 Z-共享)")
text = text.replace("❌ 写完归档层资料后 60 秒内就 `ls` 检查",
                    "❌ 写入 Z2/Z3/Z4、C2 手语数据集、`渔芯项目/`、`A3-基础设施/` 禁区")

open(path, "w", encoding="utf-8").write(text)
print(f"OK: {agent}")
PYEOF
}

for a in maodou afu heidou laomo xiaobao zhenglishi quant community psychology; do
  insert_block "$a"
done

echo "--- 完成,验证 v3 标记 ---"
grep -l "文档库 v3 入库标准" /Users/hua/.hermes/profiles/*/AGENTS.md | wc -l
