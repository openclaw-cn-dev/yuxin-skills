#!/bin/bash
# 黑豆自进化 · memory 三维反查速查脚本
# 用途:每次 cron 启动后扫一遍 memory/ 四个子目录,做鸿沟识别
# 用法: bash ~/.hermes/skills/heidou/heidou-self-evolve-cron/scripts/memory-quick-scan.sh [关键词...]

set -euo pipefail

MEMORY_BASE="/Users/hua/.hermes/profiles/heidou/memory"
PROFILE_BASE="/Users/hua/.hermes/profiles/heidou"

echo "=========================================="
echo "黑豆 memory 速查 · $(date '+%Y-%m-%d %H:%M')"
echo "=========================================="
echo

# 1. 四个子目录文件清单
for sub in sop contracts compliance finance; do
  echo "📁 memory/$sub/ ($(ls -1 "$MEMORY_BASE/$sub" 2>/dev/null | wc -l | tr -d ' ') 个文件)"
  ls -1t "$MEMORY_BASE/$sub" 2>/dev/null | head -5 | sed 's/^/   - /'
  echo
done

# 2. 当日 evolution 已出文件
echo "📁 evolution/ 当日 ($(ls "$PROFILE_BASE/evolution/$(date +%Y-%m-%d)"_*.md 2>/dev/null | wc -l | tr -d ' ') 份)"
ls -1t "$PROFILE_BASE/evolution/$(date +%Y-%m-%d)"_*.md 2>/dev/null | sed 's/^/   - /'
echo

# 3. 关键词反查(如传入参数)
if [[ $# -gt 0 ]]; then
  echo "🔍 关键词反查: $*"
  for kw in "$@"; do
    echo
    echo "--- [$kw] ---"
    grep -rli "$kw" "$MEMORY_BASE" 2>/dev/null | sed 's/^/   /' || echo "   (无命中)"
  done
fi

echo
echo "=========================================="
echo "✅ 速查完成 · 下一步:沿用决策树 v1.13 做边际价值评估"
echo "=========================================="