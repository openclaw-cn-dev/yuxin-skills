#!/bin/bash
# daily_pull.sh - Fetch daily research briefing data
# Args: $1 = output dir (default: C:/Users/Administrator/Desktop/知识库)
#
# Usage:
#   bash daily_pull.sh
#   bash daily_pull.sh /c/Users/Administrator/Desktop/知识库

set -e

OUT_DIR="${1:-/c/Users/Administrator/Desktop/知识库}"
DATE=$(date +%Y-%m-%d)
TMP="/tmp/daily_${DATE}_$$"
mkdir -p "$TMP"

echo "🌊 每日简报抓取 | $DATE"
echo "   输出: $OUT_DIR"
echo "============================================"

UA="Mozilla/5.0"

# === SOURCE A: 中国渔业协会 ===
echo ""
echo "📡 [A] 中国渔业协会..."
PIDS=("5&ty=24" "5&ty=25" "5&ty=26" "5&ty=27"
      "7&ty=30" "7&ty=31" "7&ty=32" "7&ty=33"
      "66&ty=67" "66&ty=68" "66&ty=69" "66&ty=70" "66&ty=227" "66&ty=340"
      "4&ty=23" "4&ty=61" "1&ty=11" "1&ty=12" "1&ty=338" "6&ty=28" "6&ty=29")
for pty in "${PIDS[@]}"; do
  curl -L -s -A "$UA" --max-time 8 \
    "http://www.cappma.org.cn/more.php?pid=${pty%&*}&${pty#*&}" \
    -o "$TMP/cap_${pty//&/_}.html" 2>/dev/null || true
done
echo "  ✓ $(ls -1 $TMP/cap_*.html 2>/dev/null | wc -l) channels fetched"

# === SOURCE B: FAO GLOBFISH ===
echo ""
echo "🌍 [B] FAO GLOBFISH..."
SLUGS=(pangasius salmon shrimps tilapia tuna seabass-and-seabream
       lobster crab cephalopods bivalves seaweed groundfish small-pelagics)
for slug in "${SLUGS[@]}"; do
  curl -L -s -A "$UA" --max-time 10 \
    "https://www.fao.org/in-action/globefish/species-analysis/${slug}/en" \
    -o "$TMP/sp_${slug}.html" 2>/dev/null || true
done
curl -L -s -A "$UA" --max-time 12 \
  "https://www.fao.org/fishery/en/sofia" \
  -o "$TMP/blue_transformation.html" 2>/dev/null || true
echo "  ✓ $(ls -1 $TMP/sp_*.html $TMP/blue_*.html 2>/dev/null | wc -l) pages fetched"

# === SOURCE C: 抖音热榜 (via node skill) ===
echo ""
echo "🔥 [C] 抖音热榜..."
if [ -d "/c/Users/Administrator/.openclaw/workspace/skills/douyin-hot" ]; then
  (cd "/c/Users/Administrator/.openclaw/workspace/skills/douyin-hot" && \
   node scripts/douyin.js hot 100 2>/dev/null) > "$TMP/dy_hot.txt" || true
  AQUA_HITS=$(grep -cE "海|虾|蟹|鱼|养殖|海鲜|水产|鲍|海参" "$TMP/dy_hot.txt" 2>/dev/null || echo "0")
  echo "  ✓ Hot list fetched, $AQUA_HITS aquatic-related topics"
else
  echo "  ⚠ douyin-hot skill not found, skipping"
fi

echo ""
echo "📝 Merging..."
python "$(dirname "$0")/merge.py" "$TMP" "$OUT_DIR/${DATE}-水产简报.md"

rm -rf "$TMP"
echo ""
echo "✅ Done. Report: $OUT_DIR/${DATE}-水产简报.md"
