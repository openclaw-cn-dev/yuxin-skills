#!/usr/bin/env python3
import sys
import yaml
import json
import urllib.request

def send_feishu_message(chat_id: str, message: str) -> dict:
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
    data = {
        "receive_id": chat_id,
        "msg_type": "text",
        "content": json.dumps({"text": message})
    }
    req = urllib.request.Request(
        "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=chat_id",
        data=json.dumps(data).encode(),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {token}"}
    )
    with urllib.request.urlopen(req) as resp:
        result = json.loads(resp.read())
        return result

if __name__ == "__main__":
    chat_id = sys.argv[1]
    with open(sys.argv[2]) as f:
        message = f.read().strip()
    result = send_feishu_message(chat_id, message)
    print(json.dumps(result, indent=2, ensure_ascii=False))
