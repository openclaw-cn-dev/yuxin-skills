#!/usr/bin/env python3
import yaml, urllib.request, json, sys

with open("/Users/hua/.hermes/config.yaml") as f:
    cfg = yaml.safe_load(f)

APP_ID = cfg["FEISHU_APP_ID"]
APP_SECRET = cfg["FEISHU_APP_SECRET"]

req = urllib.request.Request(
    "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
    data=json.dumps({"app_id": APP_ID, "app_secret": APP_SECRET}).encode(),
    headers={"Content-Type": "application/json"}
)
with urllib.request.urlopen(req) as resp:
    result = json.loads(resp.read())
    token = result["tenant_access_token"]

def send_msg(text, receive_id, receive_id_type="chat_id"):
    data = {
        "receive_id": receive_id,
        "msg_type": "text",
        "content": json.dumps({"text": text})
    }
    req = urllib.request.Request(
        f"https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type={receive_id_type}",
        data=json.dumps(data).encode(),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {token}"}
    )
    with urllib.request.urlopen(req) as resp:
        result = json.loads(resp.read())
        print(f"Sent to {receive_id}: {result.get('data',{}).get('message_id','FAILED')}")

send_msg("[OK] 每日重启完成，所有服务已恢复。", "***SECRET***", "chat_id")
send_msg("每日重启完成。Docker容器（lookforge-chromadb、lookforge-backend、lookforge-redis、lookforge-db、memos）+ 7个Hermes Gateway profile + openclaw gateway 均已重启。", "***SECRET***", "open_id")