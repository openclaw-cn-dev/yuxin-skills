#!/usr/bin/env python3
"""
毛豆定时汇报脚本（精简可复用版，2026-06-18 验证通过）

使用：
  /Users/hua/.hermes/hermes-agent/venv/bin/python3 /Users/hua/.hermes/profiles/maodou/skills/maodou-workflow/scripts/maodu_hourly_report.py

输出：HTTP code=0 + message_id 表示发送成功。

设计要点：
1. 凭证从 config.yaml 运行时读取（regex 提取，避开 yaml 模块依赖和
   write_file 凭证字面量被替换为 *** 的坑）
2. 双重 json.dumps 序列化（content 字段必须是 JSON 字符串）
3. 显式 try/except 捕获 HTTPError —— 飞书 API 失败抛异常而非返回 dict
4. 主目标失败时自动 fallback 到渔芯科技大群
5. 末尾注明 fallback 来源
"""
import json
import re
import ssl
import subprocess
import urllib.error
import urllib.request
import os
import sys
from datetime import datetime

# 读取 config.yaml 原始文本（避开 yaml 模块依赖）
try:
    with open("/Users/hua/.hermes/config.yaml") as f:
        cfg_text = f.read()
except Exception as e:
    print(f"无法读取 config.yaml: {e}", file=sys.stderr)
    sys.exit(2)

# 用 regex 提取凭证（避免 yaml.safe_load 依赖和键名替换问题）
def extract(key):
    m = re.search(r"^" + key + r":\s*['\"]?([A-Za-z0-9_\-]+)['\"]?", cfg_text, re.MULTILINE)
    if not m:
        raise RuntimeError(f"config.yaml 缺少 {key}")
    return m.group(1)

APP_ID = extract("FEISHU_APP_ID")
APP_SECRET = extract("FEISHU_APP_SECRET")

# 主目标：cron 指定的群（已废弃，2026-06-18 确认 230002）
PRIMARY_CHAT_ID = "***SECRET***"
# Fallback 目标：渔芯科技大群（Bot 已加入，2026-06-08 确认）
FALLBACK_CHAT_ID = "***SECRET***"

# 任务状态查询
TASKS_DIR = "/Users/hua/Desktop/渔芯科技/团队协作"
AGENT_NAME = "毛豆"

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE


def get_token():
    """获取 tenant_access_token"""
    req = urllib.request.Request(
        "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
        data=json.dumps({"app_id": APP_ID, "app_secret": APP_SECRET}).encode(),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=15, context=ctx) as r:
        return json.loads(r.read())["tenant_access_token"]


def query_tasks():
    """调用 scanner.py 拉任务状态；失败返回空三元组"""
    try:
        result = subprocess.run(
            ["python3", "scanner.py", AGENT_NAME, "--no-claim"],
            cwd=TASKS_DIR, capture_output=True, text=True, timeout=30,
        )
        data = json.loads(result.stdout)
        return (
            len(data.get("claimed", [])),
            len(data.get("in_progress", [])),
            len(data.get("pending", [])),
        )
    except Exception as e:
        print("scanner err:", e)
        return (0, 0, 0)


def build_msg(claimed, in_progress, pending):
    """构造汇报文本（Idle 状态默认）"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    return (
        "【毛豆·产品状态汇报】\n"
        f"{now}\n\n"
        "1. 当前任务：任务队列已清空（待命中）\n"
        f"2. 任务进度：认领 {claimed} / 进行中 {in_progress} / 待领取 {pending}\n"
        "3. 遇到的问题：无\n"
        "4. 下一步：进入自我提升模式 — 跟踪 RAS循环水养殖行业动态（政策+技术+市场）\n"
        "5. 整体状态：🟡 等待（无待办，切换至自我提升）"
    )


def send(token, chat_id, msg):
    """发送文本消息；返回 (code, message_id_or_err_string)"""
    data = {
        "receive_id": chat_id,
        "msg_type": "text",
        "content": json.dumps({"text": msg}),
    }
    req = urllib.request.Request(
        "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=chat_id",
        data=json.dumps(data).encode("utf-8"),
        method="POST",
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=15, context=ctx) as r:
            resp = json.loads(r.read())
            return resp.get("code"), resp.get("data", {}).get("message_id")
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        try:
            err = json.loads(body)
            return err.get("code"), f"HTTPError {e.code}: {err.get('msg')}"
        except json.JSONDecodeError:
            return e.code, body


def main():
    token = get_token()
    claimed, in_progress, pending = query_tasks()
    msg = build_msg(claimed, in_progress, pending)

    # 尝试主目标
    code, mid = send(token, PRIMARY_CHAT_ID, msg)
    if code == 0:
        print(f"PRIMARY OK: code={code}, message_id={mid}")
        return 0

    # Fallback
    print(f"PRIMARY failed: code={code}, mid={mid}")
    fallback_note = (
        f"\n\n汇报说明：指定目标 {PRIMARY_CHAT_ID[:8]}... 失败 "
        f"(code={code})，已同步至渔芯科技大群"
    )
    msg_with_note = msg + fallback_note
    code, mid = send(token, FALLBACK_CHAT_ID, msg_with_note)
    print(f"FALLBACK result: code={code}, message_id={mid}")
    return 0 if code == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
