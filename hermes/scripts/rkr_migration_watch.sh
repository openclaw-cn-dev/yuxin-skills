#!/bin/bash
# RKR 知识库重嵌入监控 —— 仅在 completed / failed / 异常停止 时输出，正常跑静默（配合 no_agent cron）
# 华哥 2026-11-03 拍板"a"=挂监控
MARK=/tmp/rkr_migration_notified
SSHPASS='Aa14472128+'
SSH="sshpass -p $SSHPASS ssh -o StrictHostKeyChecking=no -o ConnectTimeout=10 root@121.43.127.211"

STATUS=$($SSH 'docker exec rkr-postgres psql -U rkr_user -d rkr_knowledge -t -A -c "SELECT value FROM platform_settings WHERE key='"'"'embedding_migration_status'"'"';"' 2>/dev/null)

if [ -z "$STATUS" ]; then
  echo "⚠️ RKR 重嵌入监控：读不到迁移状态（服务器不可达或查询失败）"
  exit 0
fi

parse() { echo "$STATUS" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('$1',''))" 2>/dev/null; }
ST=$(parse status)
MIGRATED=$(parse migrated)
TOTAL=$(parse total)
FAILED=$(parse failed)

# 完成：只通知一次
if [ "$ST" = "completed" ]; then
  [ -f "$MARK" ] && exit 0
  touch "$MARK"
  echo "✅ RKR 知识库重嵌入完成：${MIGRATED}/${TOTAL} 条（failed=${FAILED}）"
  exit 0
fi

# 失败告警
if [ -n "$FAILED" ] && [ "$FAILED" != "0" ]; then
  echo "⚠️ RKR 重嵌入出现失败：failed=${FAILED}，进度 ${MIGRATED}/${TOTAL}"
  exit 0
fi

# status=running 但进程没了 = 异常停止
RUNNING=$($SSH 'ps aux | grep run_migration_sync | grep -v grep | grep -v "docker cp" | wc -l' 2>/dev/null | tr -d ' ')
if [ "$ST" = "running" ] && [ "$RUNNING" = "0" ]; then
  echo "⚠️ RKR 重嵌入异常停止：status=running 但无进程，进度 ${MIGRATED}/${TOTAL}"
  exit 0
fi

# 正常在跑：静默
exit 0
