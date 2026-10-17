#!/usr/bin/env bash
# AGENTS.md 真相校验脚本 v1.0
# 用法: bash agents_md_truth_check.sh [profile_name]
# 默认 profile = maodou
# 来源: maodou-agents-md-truth-check skill · 2026-09-16

set -e

PROFILE="${1:-maodou}"
AGENTS_MD="$HOME/.hermes/profiles/$PROFILE/AGENTS.md"
SKILLS_DIR="$HOME/.hermes/profiles/$PROFILE/skills"

if [[ ! -f "$AGENTS_MD" ]]; then
  echo "❌ AGENTS.md 不存在: $AGENTS_MD"
  exit 1
fi

if [[ ! -d "$SKILLS_DIR" ]]; then
  echo "❌ skills 目录不存在: $SKILLS_DIR"
  exit 1
fi

echo "🔍 校验 $PROFILE profile 的 AGENTS.md skill 声明..."
echo ""

# 提取 AGENTS.md 中所有 skill 引用
declared=$(grep -oE "~/\.hermes/profiles/$PROFILE/skills/[a-z0-9_-]+" "$AGENTS_MD" | sort -u | sed "s|~/\.hermes/profiles/$PROFILE/skills/||")

if [[ -z "$declared" ]]; then
  echo "⚠️ AGENTS.md 中未找到任何 skill 引用"
  exit 0
fi

lying_count=0
ok_count=0
total=0

for skill in $declared; do
  total=$((total + 1))
  path="$SKILLS_DIR/$skill/SKILL.md"
  if [[ ! -s "$path" ]]; then
    echo "❌ AGENTS.md 撒谎: $skill (路径不存在或为空: $path)"
    lying_count=$((lying_count + 1))
  else
    size=$(wc -c < "$path" | tr -d ' ')
    echo "✅ $skill OK ($size bytes)"
    ok_count=$((ok_count + 1))
  fi
done

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "校验结果: 总 $total / OK $ok_count / 撒谎 $lying_count"
echo "耗时: $(date +%H:%M:%S)"
if [[ $lying_count -gt 0 ]]; then
  echo ""
  echo "⚠️ 发现 $lying_count 项撒谎 — 必须立即修复(补建或删除 AGENTS.md 声明)"
  exit 1
else
  echo "✅ 全部一致,AGENTS.md 准确可信"
fi
