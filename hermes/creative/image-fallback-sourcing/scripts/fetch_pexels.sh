#!/bin/bash
# 批量拉 Pexels CC0 图（curl，Python SSL 不靠谱）
# 用法：bash fetch_pexels.sh 725992 566344 566345
UA='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124 Safari/537.36'
OUT="${1:-.}"
mkdir -p "$OUT"
shift
for pid in "$@"; do
  fn="$OUT/pexels_${pid}.jpg"
  curl -L -s -A "$UA" --max-time 10 -o "$fn" -w "$pid HTTP:%{http_code} SIZE:%{size_download}B\n" \
    "https://images.pexels.com/photos/${pid}/pexels-photo-${pid}.jpeg?w=1200" | tail -1
done
echo "下载完成。务必 vision 验真图！"
