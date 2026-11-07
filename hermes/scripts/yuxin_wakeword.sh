#!/bin/bash
# 玉芬语音唤醒 Phase 3 — LaunchAgent 管理
# 用法：
#   ~/.hermes/scripts/yuxin_wakeword.sh start    # 启动（注册到 launchd）
#   ~/.hermes/scripts/yuxin_wakeword.sh stop     # 停止
#   ~/.hermes/scripts/yuxin_wakeword.sh restart  # 重启
#   ~/.hermes/scripts/yuxin_wakeword.sh status   # 状态
#   ~/.hermes/scripts/yuxin_wakeword.sh test     # 前台测试（30 秒自动停）
#   ~/.hermes/scripts/yuxin_wakeword.sh uninstall # 完全卸载

set -e
PLIST="$HOME/Library/LaunchAgents/com.yuxin.wakeword.plist"
LOG_DIR="$HOME/hermes/voice/logs"

cmd=${1:-status}

mkdir -p "$LOG_DIR"

case "$cmd" in
  start)
    if ! [ -f "$PLIST" ]; then
      echo "❌ plist 不存在：$PLIST"
      exit 1
    fi
    launchctl unload "$PLIST" 2>/dev/null || true
    launchctl load -w "$PLIST"
    echo "✅ 启动成功"
    sleep 1
    launchctl list | grep com.yuxin.wakeword || echo "⚠️  进程还没起，看 stderr 日志"
    ;;

  stop)
    launchctl unload "$PLIST" 2>/dev/null || true
    echo "✅ 停止成功"
    ;;

  restart)
    launchctl unload "$PLIST" 2>/dev/null || true
    sleep 1
    launchctl load -w "$PLIST"
    echo "✅ 重启成功"
    ;;

  status)
    echo "=== launchd 状态 ==="
    launchctl list | grep com.yuxin.wakeword || echo "未运行"
    echo ""
    echo "=== 进程 ==="
    pgrep -fl yuxin_wake_word.py || echo "未运行"
    echo ""
    echo "=== 最近日志（最后 20 行）==="
    [ -f "$LOG_DIR/wake_word.log" ] && tail -20 "$LOG_DIR/wake_word.log" || echo "无日志"
    ;;

  test)
    echo "=== 前台测试模式（按 Ctrl+C 退出）==="
    source ~/.hermes/hermes-agent/venv/bin/activate
    python3 ~/hermes/voice/yuxin_wake_word.py
    ;;

  uninstall)
    launchctl unload "$PLIST" 2>/dev/null || true
    rm -f "$PLIST"
    echo "✅ 卸载成功"
    ;;

  *)
    echo "用法：$0 {start|stop|restart|status|test|uninstall}"
    exit 1
    ;;
esac
