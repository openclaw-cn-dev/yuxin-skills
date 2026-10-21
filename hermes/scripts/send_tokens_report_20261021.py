#!/usr/bin/env python3
"""Send tokens daily report to Feishu chat (2026-10-21)."""
import urllib.request
import json

APP_ID = "cli_a964873dd7b8dbda"
APP_SECRET = "***SECRET***"


def get_token():
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    data = json.dumps({"app_id": APP_ID, "app_secret": APP_SECRET}).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode('utf-8')).get("tenant_access_token", "")


def send_message(chat_id, text):
    token = get_token()
    url = "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=chat_id"
    data = {
        "receive_id": chat_id,
        "msg_type": "text",
        "content": json.dumps({"text": text})
    }
    req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {token}"})
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode('utf-8'))


if __name__ == '__main__':
    msg = """📊 Tokens消耗日报 10-21

【今日 vs 7天均值】
今日: 10,529K | 7天均值: 197,928K
比例 0.1x，远低于均值 ✓ 无告警

【Top 3 消费Agent】
1. zhenglishi: 6,831K
2. default: 3,698K

【模型分布】
minimax 85% (8,954K) | glm 15% (1,575K)

📁 CSV: /Users/hua/.hermes/reports/tokens_2026-10-21.csv (可导入飞书多维表格)"""
    result = send_message("***SECRET***", msg)
    print(json.dumps(result, ensure_ascii=False))
