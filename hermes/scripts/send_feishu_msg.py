#!/usr/bin/env python3
import urllib.request
import json

APP_ID = "cli_a964873dd7b8dbda"
APP_SECRET = "***SECRET***"

def get_token():
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    data = json.dumps({"app_id": APP_ID, "app_secret": APP_SECRET}).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as resp:
        result = json.loads(resp.read().decode('utf-8'))
    return result.get("tenant_access_token", "")

def send_message(chat_id, text):
    token = get_token()
    url = f"https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=chat_id"
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
    import sys
    action = sys.argv[1]
    chat_id = sys.argv[2] if len(sys.argv) > 2 else "***SECRET***"
    if action == 'start':
        send_message(chat_id, "🔄 正在执行每日例行重启Hermes Gateway和Docker，预计2-3分钟恢复。")
        print("START message sent")
    elif action == 'done':
        send_message(chat_id, "✅ 每日重启完成，所有服务已恢复。")
        print("DONE message sent")
    elif action == 'report':
        send_message(chat_id, "每日重启完成。Docker容器（lookforge-chromadb、lookforge-backend、lookforge-redis、lookforge-db、memos）+ 7个Hermes Gateway profile + openclaw gateway 均已重启。")
        print("REPORT message sent")
