#!/usr/bin/env bash
# dsh 一键更新脚本 — git pull + pnpm install + pnpm build
# 手动触发用。预览版有破坏性变更风险，更新前建议先确认 Web UI 未在使用。
set -uo pipefail

DSH_REPO="/Users/hua/系统文件夹/deepseek-harness"

echo "=== dsh 更新开始 $(date '+%F %T') ==="
cd "$DSH_REPO" || { echo "❌ 找不到 $DSH_REPO"; exit 1; }

echo "--- 更新前状态 ---"
git log -1 --oneline
node -p "require('./package.json').version" 2>/dev/null | sed 's/^/本地版本: v/'

echo "--- 1/3 git pull ---"
git pull origin master || { echo "❌ git pull 失败"; exit 1; }

echo "--- 2/3 pnpm install ---"
pnpm install || { echo "❌ pnpm install 失败"; exit 1; }

echo "--- 3/3 pnpm build ---"
pnpm run build || { echo "⚠️ pnpm build 失败（可能不影响 web 运行，tsx 走源码）"; }

echo "--- 更新后状态 ---"
git log -1 --oneline
node -p "require('./package.json').version" 2>/dev/null | sed 's/^/本地版本: v/'

echo "=== 完成 ==="
echo "重启 Web UI: pnpm dsh web"
