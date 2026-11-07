#!/usr/bin/env bash
# 抓中国渔业协会 20 频道 → 122 篇 → /tmp
# 用法: bash pull_cappma.sh
set -e
cd /tmp

URLS=(
  'http://www.cappma.org.cn/more.php?pid=1&ty=11'
  'http://www.cappma.org.cn/more.php?pid=1&ty=12'
  'http://www.cappma.org.cn/more.php?pid=1&ty=338'
  'http://www.cappma.org.cn/more.php?pid=4&ty=23'
  'http://www.cappma.org.cn/more.php?pid=4&ty=61'
  'http://www.cappma.org.cn/more.php?pid=5&ty=24'
  'http://www.cappma.org.cn/more.php?pid=5&ty=25'
  'http://www.cappma.org.cn/more.php?pid=5&ty=26'
  'http://www.cappma.org.cn/more.php?pid=5&ty=27'
  'http://www.cappma.org.cn/more.php?pid=6&ty=28'
  'http://www.cappma.org.cn/more.php?pid=6&ty=29'
  'http://www.cappma.org.cn/more.php?pid=7&ty=30'
  'http://www.cappma.org.cn/more.php?pid=7&ty=31'
  'http://www.cappma.org.cn/more.php?pid=7&ty=32'
  'http://www.cappma.org.cn/more.php?pid=7&ty=33'
  'http://www.cappma.org.cn/more.php?pid=66&ty=67'
  'http://www.cappma.org.cn/more.php?pid=66&ty=68'
  'http://www.cappma.org.cn/more.php?pid=66&ty=69'
  'http://www.cappma.org.cn/more.php?pid=66&ty=70'
  'http://www.cappma.org.cn/more.php?pid=66&ty=227'
  'http://www.cappma.org.cn/more.php?pid=66&ty=340'
)

UA='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'

for url in "${URLS[@]}"; do
  fn=$(echo "$url" | sed 's/[^a-zA-Z0-9]/_/g')
  size=$(curl -L -s -A "$UA" --max-time 8 "$url" -o "cap_${fn}.html" -w '%{size_download}')
  http=$(curl -L -s -A "$UA" --max-time 8 "$url" -o /dev/null -w '%{http_code}')
  if [ "$size" -gt 15000 ]; then
    echo "✓ $url → HTTP:$http SIZE:$size"
  else
    echo "✗ $url → HTTP:$http SIZE:$size"
  fi
done

echo ""
echo "Total .html files:"
ls -la /tmp/cap_*.html 2>/dev/null | wc -l
