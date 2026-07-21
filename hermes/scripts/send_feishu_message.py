import urllib.request
import json

with open('/Users/hua/.hermes/config/feishu_token') as f:
    token = f.read().strip()

url = "https://open.feishu.cn/open-apis/im/v1/messages/***SECRET***"
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}
payload = {
    "msg_type": "text",
    "content": {"text": "🔄 正在执行每日例行重启Hermes Gateway和Docker，预计2-3分钟恢复。"}
}

req = urllib.request.Request(url, data=json.dumps(payload).encode(), headers=headers, method='POST')
with urllib.request.urlopen(req) as resp:
    print(f"Status: {resp.status}")
    print(resp.read().decode())
