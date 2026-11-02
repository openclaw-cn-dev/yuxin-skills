#!/bin/bash
# v2：清 zhenglishi/home 缓存 + 停 gateway + rebuild FTS + VACUUM + 重启 gateway
# 修正：正确 label(ai.hermes.gateway-default) + 正确进程检测 + 20s 兜底 kill
set +e
LOG=/Users/hua/.hermes/logs/state_rebuild_v2.log
UID_NUM=$(id -u)

echo "=== $(date '+%F %T') v2 开始：清缓存 + 停机 rebuild+vacuum ===" | tee -a "$LOG"

# 等待 15 秒让玉芬汇报送达
sleep 15

echo "[0/5] 清 zhenglishi/home 缓存..." | tee -a "$LOG"
rm -rf /Users/hua/.hermes/profiles/zhenglishi/home/.npm \
       /Users/hua/.hermes/profiles/zhenglishi/home/.cache \
       /Users/hua/.hermes/profiles/zhenglishi/home/.local \
       /Users/hua/.hermes/profiles/zhenglishi/home/Library/Python \
       /Users/hua/.hermes/profiles/zhenglishi/home/Library/Containers \
       "/Users/hua/.hermes/profiles/zhenglishi/home/Library/Mobile Documents" \
       /Users/hua/.hermes/profiles/zhenglishi/home/Library/Caches \
       /Users/hua/.hermes/profiles/zhenglishi/home/Library/pnpm 2>&1 | tee -a "$LOG"
echo "  缓存清理完成，home 剩余: $(du -sh /Users/hua/.hermes/profiles/zhenglishi/home 2>/dev/null | awk '{print $1}')" | tee -a "$LOG"

echo "[1/5] 停 gateway (label=ai.hermes.gateway-default)..." | tee -a "$LOG"
launchctl bootout gui/$UID_NUM/ai.hermes.gateway-default 2>&1 | tee -a "$LOG"
for i in $(seq 1 40); do
  WRAP=$(pgrep -f "gateway_launchd_wrapper.sh default" | wc -l | tr -d ' ')
  HM=$(pgrep -x hermes | wc -l | tr -d ' ')
  if [ "$WRAP" = "0" ] && [ "$HM" = "0" ]; then
    echo "  gateway 已完全停止 (${i}s, wrapper=$WRAP hermes=$HM)" | tee -a "$LOG"
    break
  fi
  if [ $i -eq 20 ]; then
    echo "  20s 未停，强制 kill..." | tee -a "$LOG"
    pkill -9 -f "gateway_launchd_wrapper.sh default" 2>/dev/null
    pkill -9 -x hermes 2>/dev/null
  fi
  sleep 1
done
sleep 2

echo "[2/5] 确认无进程持锁..." | tee -a "$LOG"
if lsof /Users/hua/.hermes/state.db >/dev/null 2>&1; then
  echo "  ⚠️ 仍有进程持锁" | tee -a "$LOG"
  lsof /Users/hua/.hermes/state.db 2>&1 | tee -a "$LOG"
else
  echo "  ✅ 无进程持锁" | tee -a "$LOG"
fi

echo "[3/5] rebuild FTS + VACUUM..." | tee -a "$LOG"
cd /Users/hua/.hermes || exit 1
python3 scripts/session_rebuild.py --db /Users/hua/.hermes/state.db 2>&1 | tee -a "$LOG"

echo "[4/5] 重启 gateway..." | tee -a "$LOG"
launchctl bootstrap gui/$UID_NUM /Users/hua/Library/LaunchAgents/ai.hermes.gateway-default.plist 2>&1 | tee -a "$LOG"
sleep 10
if pgrep -f "gateway_launchd_wrapper.sh default" >/dev/null 2>&1; then
  echo "  ✅ gateway 已重启" | tee -a "$LOG"
else
  echo "  ⚠️ gateway 未检测到" | tee -a "$LOG"
fi

echo "[5/5] 最终状态..." | tee -a "$LOG"
ls -lh /Users/hua/.hermes/state.db | tee -a "$LOG"
echo "  ~/.hermes: $(du -sh /Users/hua/.hermes 2>/dev/null | awk '{print $1}')" | tee -a "$LOG"
df -h / | tail -1 | tee -a "$LOG"

echo "=== $(date '+%F %T') 完成 ===" | tee -a "$LOG"
