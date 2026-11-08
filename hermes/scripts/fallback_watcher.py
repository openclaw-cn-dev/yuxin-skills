#!/usr/bin/env python3
"""
Fallback 监控脚本 — 检测 Hermes gateway 是否触发过 LLM provider fallback。
当检测到新的 fallback 事件时，通过飞书 Bot 通知华哥。

用法: python3 fallback_watcher.py
设计为 cron 每 5 分钟跑一次。状态文件记录上次检查位置，增量扫描。
"""

import os
import sys
import json
import re
import time
import urllib.request
import urllib.error
from datetime import datetime, timezone, timedelta

HOME = os.path.expanduser("~")
HERMES_HOME = os.path.join(HOME, ".hermes")
LOG_PATH = os.path.join(HERMES_HOME, "logs", "gateway.log")
STATE_FILE = os.path.join(HERMES_HOME, "scripts", ".fallback_watcher_state")
FEISHU_WEBHOOK_FILE = os.path.join(HERMES_HOME, "scripts", ".feishu_webhook_url")

# ── 状态管理 ──
def load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE) as f:
                return json.load(f)
        except:
            pass
    return {"last_pos": 0, "last_notified": None, "active_fallback": None}

def save_state(state):
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)

# ── 飞书通知 ──
def get_feishu_webhook():
    """从 .env 或 webhook 文件读取飞书 webhook URL"""
    # 优先从 webhook 文件读
    if os.path.exists(FEISHU_WEBHOOK_FILE):
        with open(FEISHU_WEBHOOK_FILE) as f:
            return f.read().strip()
    # 从 .env 读
    env_path = os.path.join(HERMES_HOME, ".env")
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                if line.startswith("FEISHU_WEBHOOK_URL="):
                    return line.split("=", 1)[1].strip()
    return None

def send_feishu(title, content, level="warning"):
    webhook = get_feishu_webhook()
    if not webhook:
        print("[WARN] 没有飞书 webhook URL，跳过通知")
        return False

    color_map = {"warning": "orange", "critical": "red", "info": "blue", "recovery": "green"}
    color = color_map.get(level, "orange")

    payload = {
        "msg_type": "interactive",
        "card": {
            "header": {
                "title": {"tag": "plain_text", "content": title},
                "template": color
            },
            "elements": [
                {"tag": "markdown", "content": content},
                {"tag": "note", "elements": [
                    {"tag": "plain_text", "content": f"🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | fallback_watcher"}
                ]}
            ]
        }
    }

    try:
        req = urllib.request.Request(
            webhook,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        urllib.request.urlopen(req, timeout=10)
        print(f"[OK] 飞书通知已发送: {title}")
        return True
    except Exception as e:
        print(f"[ERR] 飞书通知失败: {e}")
        return False

# ── 日志扫描 ──
def scan_log(state):
    """增量扫描 gateway.log，检测 fallback 事件"""
    if not os.path.exists(LOG_PATH):
        return None

    file_size = os.path.getsize(LOG_PATH)
    last_pos = state.get("last_pos", 0)

    # 日志轮转检测：如果文件变小了，从头开始
    if file_size < last_pos:
        last_pos = 0

    if last_pos >= file_size:
        return None

    with open(LOG_PATH, "r") as f:
        f.seek(last_pos)
        new_lines = f.read()
        state["last_pos"] = f.tell()

    if not new_lines:
        return None

    # 检测 fallback 相关日志
    # Hermes gateway 在 fallback 时的日志模式：
    # - "falling back to provider" / "fallback to" 
    # - "provider.*failed.*trying"
    # - 错误码 402/429 + 后续成功的 provider 切换
    patterns = [
        (r"falling back to provider[:\s]+(\S+)", "fallback"),
        (r"fallback to[:\s]+(\S+)", "fallback"),
        (r"provider[_\s]+fallback[:\s]+(\S+)", "fallback"),
        (r"switching to fallback provider[:\s]+(\S+)", "fallback"),
        (r"(?:402|429|insufficient[_ ]balance|rate[_ ]limit).*?(?:trying|fallback|switching)[:\s]+(\S+)", "fallback"),
    ]

    for line in new_lines.split("\n"):
        for pattern, event_type in patterns:
            m = re.search(pattern, line, re.IGNORECASE)
            if m:
                provider = m.group(1)
                return {"type": event_type, "provider": provider, "line": line.strip()[:200]}

    return None

# ── 当前活跃 provider 检测 ──
def get_active_provider():
    """读取 config.yaml 看当前活跃 provider"""
    config_path = os.path.join(HERMES_HOME, "config.yaml")
    try:
        import yaml
        with open(config_path) as f:
            cfg = yaml.safe_load(f)
        provider = cfg.get("model", {}).get("provider", "unknown")
        model = cfg.get("model", {}).get("default", "unknown")
        return provider, model
    except:
        return "unknown", "unknown"

# ── 主逻辑 ──
def main():
    state = load_state()
    event = scan_log(state)

    if event:
        provider_name = event["provider"]
        now = datetime.now().isoformat()

        # 检查是否已经通知过同一个 fallback（避免重复）
        last_notified = state.get("last_notified")
        if last_notified and last_notified.get("provider") == provider_name:
            # 同一个 provider fallback，检查是否超过 30 分钟
            last_time = last_notified.get("time", "")
            try:
                lt = datetime.fromisoformat(last_time)
                if (datetime.now() - lt).total_seconds() < 1800:
                    save_state(state)
                    return  # 30 分钟内不重复通知
            except:
                pass

        # 发送飞书通知
        title = f"🚨 LLM Fallback 触发"
        content = (
            f"**主力大模型不可用，已自动切换到备用模型**\n\n"
            f"**当前 Provider：** `{provider_name}`\n"
            f"**触发时间：** {now}\n"
            f"**日志摘要：** {event['line']}\n\n"
            f"请华哥检查套餐余额/限额状态。"
        )
        send_feishu(title, content, level="warning")

        state["last_notified"] = {"time": now, "provider": provider_name}
        state["active_fallback"] = provider_name

    # 检测恢复：如果之前有 fallback 但现在 active provider 是主力
    active_fallback = state.get("active_fallback")
    if active_fallback:
        provider, model = get_active_provider()
        if provider == "volcengine-agent-plan":
            title = "✅ LLM 已恢复主力"
            content = (
                f"**主力大模型已恢复正常**\n\n"
                f"**当前 Provider：** `{provider}` / `{model}`\n"
                f"**恢复时间：** {datetime.now().isoformat()}\n\n"
                f"之前使用的备用 `{active_fallback}` 已切回。"
            )
            send_feishu(title, content, level="recovery")
            state["active_fallback"] = None
            state["last_notified"] = None

    save_state(state)

if __name__ == "__main__":
    main()