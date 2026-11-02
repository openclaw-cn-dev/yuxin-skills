#!/usr/bin/env bash
# cron-paused-detector.sh
# 2026-06-21 16:02 patrol 新增
#
# 用途：扫描 jobs.json 中 state=paused 但 last_status=ok 的 cron。
# 这是"伪装健康"陷阱：表面看 last_run 1分钟前 + status=ok + enabled=True，
# 实际 state=paused 自 34 天前，cron 早就不触发了。
#
# 用法：
#   bash cron-paused-detector.sh                # 默认扫描主 cron jobs.json
#   bash cron-paused-detector.sh /path/to/jobs.json  # 指定文件
#   bash cron-paused-detector.sh --fix-dry-run  # 输出修复命令但不执行
#
# 退出码：
#   0 = 无 paused 伪装（健康）
#   1 = 检出 paused 伪装健康（需立即处置）
#   2 = jobs.json 不存在或解析失败

set -euo pipefail

JOBS_FILE="${1:-$HOME/.hermes/cron/jobs.json}"
FIX_DRY_RUN=false

if [[ "$JOBS_FILE" == "--fix-dry-run" ]]; then
    FIX_DRY_RUN=true
    JOBS_FILE="$HOME/.hermes/cron/jobs.json"
fi

if [[ ! -f "$JOBS_FILE" ]]; then
    echo "❌ jobs.json not found: $JOBS_FILE" >&2
    exit 2
fi

# 解析 paused 的 cron（state=paused + last_run_at 非空）
mapfile -t PAUSED < <(python3 -c "
import json, sys
try:
    data = json.load(open('$JOBS_FILE'))
except Exception as e:
    print(f'PARSE_ERROR: {e}', file=sys.stderr)
    sys.exit(1)
jobs = data if isinstance(data, list) else data.get('jobs', [])
for j in jobs:
    if j.get('state') == 'paused':
        name = j.get('name', '')
        last = j.get('last_run_at', '—') or '—'
        status = j.get('last_status', '—') or '—'
        paused_at = j.get('paused_at', '—') or '—'
        print(f'{name}|{last}|{status}|{paused_at}')
" 2>/dev/null)

if [[ ${#PAUSED[@]} -eq 0 ]]; then
    echo "🟢 无 paused 伪装健康 cron"
    exit 0
fi

echo "🔴 检出 ${#PAUSED[@]} 个 paused 伪装健康 cron："
echo "────────────────────────────────────────────────────────────────────"
printf "%-40s %-22s %-8s %-25s\n" "NAME" "LAST_RUN" "STATUS" "PAUSED_AT"
echo "────────────────────────────────────────────────────────────────────"
for entry in "${PAUSED[@]}"; do
    IFS='|' read -r name last status paused_at <<< "$entry"
    printf "%-40s %-22s %-8s %-25s\n" "${name:0:40}" "${last:0:22}" "${status:0:8}" "${paused_at:0:25}"
done
echo "────────────────────────────────────────────────────────────────────"
echo ""
echo "🔧 修复命令（unpause + 重新调度）："
for entry in "${PAUSED[@]}"; do
    IFS='|' read -r name _ _ _ <<< "$entry"
    echo "  hermes cron update \"$name\" --resume"
done

if [[ "$FIX_DRY_RUN" == "true" ]]; then
    echo ""
    echo "ℹ️  --fix-dry-run 模式：仅显示命令，未执行"
    exit 0
fi

# 默认退出码 1（表示检出问题）
exit 1
