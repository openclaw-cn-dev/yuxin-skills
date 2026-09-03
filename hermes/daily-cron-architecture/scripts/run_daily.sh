#!/bin/bash
# 每日水产简报 — 完整工作流（已实测跑通，2026-06-08）
# 路径：C:\Users\Administrator\Desktop\知识库\run_daily.sh
# 触发：Hermes cron 0 9 * * * （每天 9:00）

set -e
cd "/c/Users/Administrator/Desktop/知识库/"

echo "============================================"
echo "🌊 每日水产简报 | $(date +%Y-%m-%d_%H:%M)"
echo "============================================"

# 1) 抓中国渔业协会 21 频道
echo ""
echo "📡 [1/4] 抓取中国渔业协会..."
PIDS="1&ty=11 1&ty=12 1&ty=338 4&ty=23 4&ty=61 \
      5&ty=24 5&ty=25 5&ty=26 5&ty=27 \
      6&ty=28 6&ty=29 \
      7&ty=30 7&ty=31 7&ty=32 7&ty=33 \
      66&ty=67 66&ty=68 66&ty=69 66&ty=70 66&ty=227 66&ty=340"
for pty in $PIDS; do
  pid=${pty%&*}; ty=${pty#*&}
  curl -L -s -A 'Mozilla/5.0' --max-time 8 \
    "http://www.cappma.org.cn/more.php?pid=${pid}&${ty}" \
    -o "cap_${pid}_${ty}.html" 2>/dev/null || true
done
ls -1 cap_*.html 2>/dev/null | wc -l | xargs echo "  抓到频道数:"

# 2) 抓 FAO 13 物种 + SOFIA
echo ""
echo "🌍 [2/4] 抓取 FAO 全球数据..."
SLUGS="pangasius salmon shrimps tilapia tuna \
       seabass-and-seabream lobster crab cephalopods \
       bivalves seaweed groundfish small-pelagics"
mkdir -p fao_tmp && cd fao_tmp
for slug in $SLUGS; do
  curl -L -s -A 'Mozilla/5.0' --max-time 10 \
    "https://www.fao.org/in-action/globefish/species-analysis/${slug}/en" \
    -o "sp_${slug}.html" 2>/dev/null || true
done
curl -L -s -A 'Mozilla/5.0' --max-time 12 \
  "https://www.fao.org/fishery/en/sofia" -o blue_transformation.html 2>/dev/null || true
cd ..
ls -1 fao_tmp/sp_*.html fao_tmp/blue_*.html 2>/dev/null | wc -l | xargs echo "  抓到 FAO 页面数:"

# 3) 抓抖音热榜 + 过滤
echo ""
echo "🔥 [3/4] 抓取抖音热榜 + 过滤水产..."
cd "/c/Users/Administrator/.openclaw/workspace/skills/douyin-hot"
node scripts/douyin.js hot 100 > /tmp/dy_hot.txt 2>&1 || true
grep -E "海|虾|蟹|鱼|养殖|海鲜|水产|鲍" /tmp/dy_hot.txt > /tmp/dy_aqua.txt 2>/dev/null || \
  echo "今日无水产话题" > /tmp/dy_aqua.txt
cat /tmp/dy_aqua.txt
cd "/c/Users/Administrator/Desktop/知识库/"

# 4) 合并 + 写桌面
echo ""
echo "📝 [4/4] 合并 + 写桌面简报..."
DATE=$(date +%Y-%m-%d)
python merge.py "$(pwd)/fao_tmp" "$DATE-水产简报.md"

# 5) 推飞书（用昨天的 App，已确认加群）
echo ""
echo "📤 推送飞书..."
python feishu_push.py "C:/Users/Administrator/Desktop/知识库/$DATE-水产简报.md"

# 6) 清理
rm -rf fao_tmp

echo ""
echo "✅ 简报 + 飞书推送完成"
echo "============================================"
