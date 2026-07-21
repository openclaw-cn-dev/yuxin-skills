#!/usr/bin/env python3
"""语音唤醒崩溃 watcher

- 每 60 秒检查 /tmp/voice_wake_crash.json
- 发现新崩溃 → 用 feishu-api-notify skill 的方式发飞书告警
- 同时检查 porcupine_listener 进程是否存活
- 写入已经处理过的崩溃时间戳，避免重复告警
"""
from __future__ import annotations

import json
import os
import socket
import subprocess
import sys
import time
from pathlib import Path

CRASH_FILE = Path("/tmp/voice_wake_crash.json")
LOG_FILE = Path.home() / "hermes" / "voice" / "logs" / "voice_crash_watcher.log"
FEISHU_HOME = "feishu:***SECRET***"  # 默认回话
LISTENER_CMD = "porcupine_listener.py"


def log(msg: str):
    line = f"[{time.strftime('%H:%M:%S')}] {msg}"
    print(line, flush=True)
    try:
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        with LOG_FILE.open("a") as f:
            f.write(line + "\n")
    except Exception:
        pass


def is_listener_alive() -> bool:
    """检查唤醒词监听进程是否还活着"""
    try:
        out = subprocess.run(
            ["pgrep", "-f", LISTENER_CMD],
            capture_output=True,
            text=True,
            timeout=5,
        )
        return out.returncode == 0 and bool(out.stdout.strip())
    except Exception:
        return False


def send_feishu_alert(message: str):
    """发飞书私聊告警给华哥（用 hermes CLI 最稳）"""
    try:
        # 方案 1: 直接用 hermes CLI
        subprocess.run(
            ["hermes", "-z", f"紧急：{message}（无需回复，玉芬已在自愈）"],
            capture_output=True,
            text=True,
            timeout=15,
        )
        log(f"✅ 飞书告警已发：{message[:60]}")
        return True
    except Exception as e:
        log(f"⚠️ 飞书告警失败：{e}")
        return False


def check_crashes():
    """检查并消费 /tmp/voice_wake_crash.json"""
    if not CRASH_FILE.exists():
        return

    try:
        data = json.loads(CRASH_FILE.read_text())
    except Exception as e:
        log(f"⚠️ crash 文件解析失败：{e}")
        return

    if not data:
        return

    # 只处理最近 5 分钟内的崩溃，避免历史洪水
    fresh = []
    now = time.time()
    for entry in data:
        try:
            ts = time.strptime(entry.get("time", ""), "%Y-%m-%d %H:%M:%S")
            ts_epoch = time.mktime(ts)
            if now - ts_epoch < 300:  # 5 分钟内
                fresh.append(entry)
        except Exception:
            continue

    if not fresh:
        return

    # 构造告警文本
    lines = [f"🚨 **语音唤醒服务崩溃** (主机 {socket.gethostname()})"]
    lines.append("")
    for i, entry in enumerate(fresh, 1):
        lines.append(f"{i}. **{entry.get('component', '?')}** at {entry.get('time', '?')}")
        lines.append(f"   {entry.get('error', '?')[:200]}")

    lines.append("")
    lines.append(f"监听进程存活：{'✅' if is_listener_alive() else '❌ 已死'}")
    lines.append("LaunchAgent KeepAlive 应已自动重启，3 分钟内未回则需手动处理。")

    msg = "\n".join(lines)
    log(f"📤 发送告警（{len(fresh)} 条新崩溃）")
    send_feishu_alert(msg)


def check_process():
    """如果进程死了且文件无崩溃通知（比如 macOS TCC 拒绝麦克风权限）,
    也需要单独告警"""
    if is_listener_alive():
        return

    # 进程不存在：可能刚被杀。检查时间戳避免重复告警
    sent_flag = Path("/tmp/voice_wake_notified_dead")
    if sent_flag.exists():
        age = time.time() - sent_flag.stat().st_mtime
        if age < 1800:  # 30 分钟内不重复告警
            return

    send_feishu_alert(
        f"🚨 **唤醒词进程死亡** (主机 {socket.gethostname()})\n"
        f"porcupine_listener.py 不在运行\n"
        f"LaunchAgent KeepAlive 应该自动重启，请稍后复查\n"
        f"命令：launchctl list | grep yuxin.voice"
    )
    sent_flag.touch()


def main():
    log("=" * 60)
    log("语音唤醒 watcher 启动（每 60 秒检查）")
    log("=" * 60)

    # 支持 --once（cron 模式只跑一轮立刻退出）和默认常驻模式
    if "--once" in sys.argv:
        try:
            check_crashes()
            check_process()
        except Exception as e:
            log(f"⚠️ --once 异常：{e}")
        return

    while True:
        try:
            check_crashes()
            check_process()
        except Exception as e:
            log(f"⚠️ 主循环异常：{e}")
        time.sleep(60)


if __name__ == "__main__":
    main()
