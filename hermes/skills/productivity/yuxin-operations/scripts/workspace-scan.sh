#!/bin/bash
# 巡视脚本：扫描各Agent workspace最新md文件（排除MEMORY.md）
# 用法：bash workspace-scan.sh
# 输出：Agent名 | 最新文件名 | 距今小时数

for dir in "毛豆-产品交付" "老莫-技术运维" "小宝-商务运营" "黑豆-行政财务法务" "阿福-客服"; do
  workspace="/Users/hua/Desktop/渔芯科技/4-部门空间/$dir"
  if [ ! -d "$workspace" ]; then
    echo "$dir: 目录不存在"
    continue
  fi
  latest=$(find "$workspace" -name "*.md" ! -name "MEMORY.md" -type f 2>/dev/null \
    | xargs -I{} stat -f "%m %N" {} 2>/dev/null \
    | sort -rn | head -1)
  if [ -n "$latest" ]; then
    age=$(echo "$latest" | awk '{print $1}')
    path=$(echo "$latest" | awk '{print $2}')
    fname=$(basename "$path")
    hrs=$(( ($(date +%s) - age) / 3600 ))
    if [ $hrs -lt 24 ]; then
      flag="🟢"
    elif [ $hrs -lt 168 ]; then
      flag="🟡"
    else
      flag="🔴"
    fi
    echo "$flag $dir: $fname (${hrs}h)"
  else
    echo "⚠️ $dir: 无md文件"
  fi
done
