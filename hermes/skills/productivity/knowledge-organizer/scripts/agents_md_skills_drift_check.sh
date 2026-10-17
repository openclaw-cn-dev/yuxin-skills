#!/usr/bin/env bash
# AGENTS.md core_skills ↔ active profile skills/ directory 漂移检测器
# 关联 PITFALL: #KO-17（2026-09-10 09:09 整理师心跳立）
# 关联 PITFALL: #KO-19（2026-09-13 09:00 整理师心跳立）— grep 模式失效，已用 awk 替换
# 关联 skill: knowledge-organizer (cron-home-hijack-bypass)
#
# 用法:
#   bash agents_md_skills_drift_check.sh                    # 默认 zhenglishi
#   bash agents_md_skills_drift_check.sh --profile afu      # 指定 profile
#   bash agents_md_skills_drift_check.sh --agents-md /path  # 自定义 AGENTS.md
#
# 退出码:
#   0 = 全部命中
#   1 = 含 ❌（失引用，需上报）
#   2 = 含 🟡（跨 profile 引用，需评估）

set -euo pipefail

PROFILE="zhenglishi"
AGENTS_MD=""

while [ $# -gt 0 ]; do
  case "$1" in
    --profile)    PROFILE="$2"; shift 2 ;;
    --agents-md)  AGENTS_MD="$2"; shift 2 ;;
    *) echo "[ERROR] unknown arg: $1" >&2; exit 3 ;;
  esac
done

# 默认 AGENTS.md 路径
if [ -z "$AGENTS_MD" ]; then
  AGENTS_MD="/Users/hua/.hermes/profiles/$PROFILE/AGENTS.md"
fi

if [ ! -f "$AGENTS_MD" ]; then
  echo "[ERROR] AGENTS.md not found: $AGENTS_MD" >&2
  exit 3
fi

echo "=== AGENTS.md core_skills 命中实测 ==="
echo "Profile: $PROFILE"
echo "AGENTS.md: $AGENTS_MD"
echo ""

# 提取 markdown 表格中的 skill-name 列
#
# #KO-19 (2026-09-13 09:00 整理师心跳立):
#   原 grep 模式 `\| \d+ \| \K[a-z0-9_-]+` 假设 skill name 在第 3 列,
#   但 AGENTS.md 实际格式 `| 1 | zhenglishi-workflow | 学习助手工作流 |`
#   skill name 实际在第 2 列(数字后),导致脚本返回空 → 检测器静默失效。
#
# 修复策略:用 awk 按行 + FS='|' 解析,对每个匹配 `|<num>|` 的行,
# 扫所有列寻找匹配 `[a-z0-9-]+` 的短名(长度 3-40,纯小写字母+数字+连字符),
# 每行只取第一个匹配(避免读到中文/描述列)。
SKILLS=$(awk -F'|' '
  /^\| *[0-9]+ *\|/ {
    for (i=2; i<=NF; i++) {
      gsub(/^ +| +$/, "", $i)
      # skill name 特征:全小写字母+数字+连字符,长度 3-40
      if ($i ~ /^[a-z0-9-]+$/ && length($i) >= 3 && length($i) <= 40) {
        print $i
        break
      }
    }
  }
' "$AGENTS_MD" | sort -u)

if [ -z "$SKILLS" ]; then
  echo "[WARN] 没从 AGENTS.md 抽出任何 core_skill（格式可能又变了）"
  echo "[HINT] 手工验证 AGENTS.md 表格格式:| <num> | <skill-name> | <description> |"
  exit 0
fi

MISS=0
WARN=0

for skill in $SKILLS; do
  if [ -d "/Users/hua/.hermes/profiles/$PROFILE/skills/$skill" ]; then
    echo "✅ $skill"
  elif [ -d "/Users/hua/.hermes/skills/productivity/$skill" ]; then
    echo "🟡 $skill (default profile only)"
    WARN=$((WARN + 1))
  elif [ -d "/Users/hua/.hermes/skills/$skill" ]; then
    echo "🟡 $skill (default profile L1)"
    WARN=$((WARN + 1))
  else
    echo "❌ $skill (NOT FOUND)"
    MISS=$((MISS + 1))
  fi
done

echo ""
echo "=== 汇总 ==="
TOTAL=$(echo "$SKILLS" | wc -l | tr -d ' ')
echo "命中: $((TOTAL - MISS - WARN))/$TOTAL"
echo "🟡 跨 profile 引用: $WARN"
echo "❌ 失引用: $MISS"

if [ "$MISS" -gt 0 ]; then
  echo ""
  echo "[PITFALL] #KO-17 应在心跳报告 §4 立"
  exit 1
elif [ "$WARN" -gt 0 ]; then
  exit 2
fi

exit 0
