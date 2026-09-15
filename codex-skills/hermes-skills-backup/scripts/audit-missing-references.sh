#!/usr/bin/env bash
# audit-missing-references.sh
# 反向扫描已装 MKT skill 的 references 完整性 — 找出 SKILL.md 引用但实际缺失的文件
#
# 0908 实测漏洞：24 个已装 MKT skill 的 SKILL.md 引用了 references 文件
# 但实际缺失（0903 装 ai-seo 漏带 references 子目录 + 0905 装 5 个 MKT 漏）。
# Codex 跑这些 skill 时 references 链接全 404。
#
# 用法：
#   bash scripts/audit-missing-references.sh                    # 扫所有 MKT skill
#   bash scripts/audit-missing-references.sh ai-seo ads cro     # 扫指定 skill
#   bash scripts/audit-missing-references.sh --repo             # 扫 repo 而不是本地 ~/.codex/skills
#
# 输出：每行 "[skill] MISSING: refs/file1.md refs/file2.md"
#       空输出 = 全部完整

set -e

REPO_PATH="/c/Users/Administrator/Desktop/yuxin-skills/codex-skills"
LOCAL_PATH="/c/Users/Administrator/.codex/skills"
SCAN_PATH="$LOCAL_PATH"

# 解析参数
SKILLS=()
while [ $# -gt 0 ]; do
  case "$1" in
    --repo)
      SCAN_PATH="$REPO_PATH"
      shift
      ;;
    --local)
      SCAN_PATH="$LOCAL_PATH"
      shift
      ;;
    *)
      SKILLS+=("$1")
      shift
      ;;
  esac
done

# 默认扫全部 MKT skill
if [ ${#SKILLS[@]} -eq 0 ]; then
  cd "$SCAN_PATH"
  SKILLS=($(ls | grep -E "^(ab-testing|ad-creative|ads|ai-seo|analytics|attribution|churn-prevention|co-marketing|cold-email|community-marketing|competitor-profiling|competitors|content-strategy|copy-editing|copywriting|cro|customer-research|directory-submissions|emails|free-tools|image|launch|lead-magnets|marketing-council|marketing-ideas|marketing-loops|marketing-mindset|marketing-plan|marketing-psychology|offers|onboarding|paywalls|popups|pricing|product-marketing|programmatic-seo|prospecting|public-relations|referrals|revops|sales-enablement|schema|seo-audit|signup|site-architecture|social|sms|video)$"))
fi

# 反向扫描
cd "$SCAN_PATH"
MISSING_TOTAL=0
for skill in "${SKILLS[@]}"; do
  if [ -f "$skill/SKILL.md" ]; then
    refs=$(grep -oE "references/[a-zA-Z0-9_-]+\.md" "$skill/SKILL.md" 2>/dev/null | sort -u)
    missing=""
    for r in $refs; do
      if [ ! -s "$skill/$r" ]; then
        missing="$missing $r"
      fi
    done
    if [ -n "$missing" ]; then
      echo "[$skill] MISSING:$missing"
      MISSING_TOTAL=$((MISSING_TOTAL + 1))
    fi
  fi
done

if [ $MISSING_TOTAL -eq 0 ]; then
  echo "✅ 全部 references 完整 (扫了 ${#SKILLS[@]} skill)"
else
  echo ""
  echo "⚠️  $MISSING_TOTAL 个 skill 有缺失 references"
  echo ""
  echo "修复流程（0908 实测）："
  echo "  1. 本地已有 → 同步到 repo:"
  echo "     for skill in <names>; do"
  echo "       mkdir -p $REPO_PATH/\$skill/references"
  echo "       cp $LOCAL_PATH/\$skill/references/*.md $REPO_PATH/\$skill/references/"
  echo "     done"
  echo ""
  echo "  2. 本地缺 → 从上游拉（marketingskills 默认分支是 main）:"
  echo "     BASE=https://raw.githubusercontent.com/coreyhaines31/marketingskills/main/skills"
  echo "     sleep 1 # 防 GitHub raw 限速"
  echo "     curl -s --max-time 12 -o <out> \$BASE/<skill>/references/<file>.md"
  echo ""
  echo "  3. 验完整性：再跑一次本脚本"
fi

exit $MISSING_TOTAL