#!/usr/bin/env bash
# hermes_home_preflight.sh
# 网关启动前的"项目搬家检测"hook
# 由 gateway_launchd_wrapper.sh 在启动 python 之前调用
# 作者:宽博士 · 2026-09-14

# === 配置 ===
EXPECTED_PROJECT="/Users/hua/6-产品研发/渔芯独角兽/00-基本完成/渔芯量化/渔芯量化"
STATE_FILE="/Users/hua/.hermes/profiles/quant/cron/output/hermes_home_preflight.log"
TIMEOUT_SEC=30

# === 安全开关:绝对路径,不被 sandbox HOME 劫持 ===
export HOME="/Users/hua"

mkdir -p "$(dirname "$STATE_FILE")"

echo "[$(date +%FT%T)] preflight start, profile=$1" >> "$STATE_FILE"

# === 1. 项目目录不存在 → 旧机器/项目被搬走 → 严重告警,但不阻塞网关 ===
if [ ! -d "$EXPECTED_PROJECT" ]; then
  echo "[$(date +%FT%T)] WARN: project not found at $EXPECTED_PROJECT" >> "$STATE_FILE"
  # 不阻塞网关启动,因为:
  # - 网关主要服务 ~/.hermes/ 数据,不依赖项目
  # - 项目是镜像,丢了网关也能跑
  # - 用户需要手动恢复项目(这超出自动化能力)
  exit 0
fi

# === 2. 项目位置变化 → 记录并提示 ===
LAST_PROJECT_FILE="/Users/hua/.hermes/profiles/quant/cron/output/.last_project_path"
if [ -f "$LAST_PROJECT_FILE" ]; then
  LAST=$(cat "$LAST_PROJECT_FILE")
  if [ "$LAST" != "$EXPECTED_PROJECT" ]; then
    echo "[$(date +%FT%T)] MIGRATION DETECTED: $LAST → $EXPECTED_PROJECT" >> "$STATE_FILE"
    # 这里将来可以加:通过飞书/微信通知华哥,但默认安静
  fi
fi
echo -n "$EXPECTED_PROJECT" > "$LAST_PROJECT_FILE"

# === 3. hermes_data 反向同步(带超时,失败不阻塞)===
HERMES_DATA="$EXPECTED_PROJECT/11-宽博士Hermes档案/hermes_data"
if [ -d "$HERMES_DATA" ]; then
  # 触发后台同步(后台跑,不阻塞网关启动)
  nohup /Users/hua/.hermes/scripts/sync_hermes_hourly.sh > /dev/null 2>&1 &
  echo "[$(date +%FT%T)] trigger async hermes_data sync, pid=$!" >> "$STATE_FILE"
else
  echo "[$(date +%FT%T)] hermes_data not present, skip sync" >> "$STATE_FILE"
fi

echo "[$(date +%FT%T)] preflight done" >> "$STATE_FILE"
exit 0