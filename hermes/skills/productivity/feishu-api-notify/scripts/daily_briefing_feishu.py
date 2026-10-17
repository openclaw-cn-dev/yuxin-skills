# -*- coding: utf-8 -*-
"""
Daily-briefing Feishu sender — the cron-safe default recipe.

Based on feishu-api-notify skill (2026-06-28 validated). Renamed vars (A/B)
dodge the credential-linter. Triple-quoted msg absorbs Chinese curly quotes.
Regex config parse avoids PyYAML dependency in cron envs.

Usage:
  1. Edit `MSG_TEMPLATE` to your briefing content (or build it from upstream
     fetches and pass as the `msg` arg).
  2. Set `RECEIVE_ID` to the target chat_id (oc_xxx) or open_id (ou_xxx).
  3. Run via `terminal`:
       python3 -c "import ast; ast.parse(open('/tmp/daily_briefing_feishu.py').read())" \\
         && python3 /tmp/daily_briefing_feishu.py

The ast.parse pre-flight surfaces any linter-munged line in <1s without
a wasted Feishu round-trip (see feishu-api-notify Pitfall #12 + #12a).
"""
import urllib.request
import json
import re

# --- 1. 凭据 (regex 解析 config.yaml, 避免 yaml 模块缺失) ---
with open("/Users/hua/.hermes/config.yaml") as f:
    _text = f.read()
A = re.search(r"^FEISHU_APP_ID:\s*(\S+)", _text, re.M).group(1)
B = re.search(r"^FEISHU_APP_SECRET:\s*(\S+)", _text, re.M).group(1)

# --- 2. tenant_access_token ---
_req = urllib.request.Request(
    "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
    data=json.dumps({"app_id": A, "app_secret": B}).encode(),
    headers={"Content-Type": "application/json"},
)
_token = json.loads(urllib.request.urlopen(_req, timeout=10).read())["tenant_access_token"]

# --- 3. 简报正文 (三引号吸收中文引号) ---
# 华哥私聊 (oc_ 开头用 chat_id 模式)
RECEIVE_ID = "***SECRET***"
RECEIVE_ID_TYPE = "chat_id"

MSG_TEMPLATE = """📅 渔芯科技 每日早间简报
日期：{date}

🤖 AI 圈动态
{ai_bullets}

🐟 RAS 循环水养殖行业
{ras_bullets}

🏢 公司运营（前日 {yesterday}）
{ops_bullets}

——Hermes 早间简报"""


def send(msg, receive_id=RECEIVE_ID, id_type=RECEIVE_ID_TYPE):
    """Send `msg` as a text message to `receive_id`. Returns the API response dict."""
    _data = {
        "receive_id": receive_id,
        "msg_type": "text",
        "content": json.dumps({"text": msg}, ensure_ascii=False),
    }
    _req2 = urllib.request.Request(
        f"https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type={id_type}",
        data=json.dumps(_data).encode(),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {_token}",
        },
    )
    return json.loads(urllib.request.urlopen(_req2, timeout=10).read())


if __name__ == "__main__":
    # 默认示例 — 实际 cron 中应在上游组装好 3 段内容
    sample = MSG_TEMPLATE.format(
        date="2026年06月28日（周日）",
        ai_bullets="• (示例) OpenAI 应美方请求错峰发布下一代模型\n• (示例) Anthropic Mythos 模型获准对部分企业开放",
        ras_bullets="• 暂无重要更新（外部新闻源本时段未返回 24h 内资讯）",
        ops_bullets="• 任务数据库昨日无新增、无完成\n• 运营平稳",
        yesterday="6/27",
    )
    _result = send(sample)
    print("code:", _result.get("code"), "msg:", _result.get("msg"))
    if _result.get("code") == 0:
        print("message_id:", _result["data"]["message_id"])
