import yaml, urllib.request, json, sys

with open("/Users/hua/.hermes/config.yaml") as f:
    cfg = yaml.safe_load(f)

APP_ID = cfg["FEISHU_APP_ID"]
APP_SECRET = cfg["FEISHU_APP_SECRET"]

# Step 2 — obtain token
req = urllib.request.Request(
    "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
    data=json.dumps({"app_id": APP_ID, "app_secret": APP_SECRET}).encode(),
    headers={"Content-Type": "application/json"}
)
with urllib.request.urlopen(req) as resp:
    result = json.loads(resp.read())
    assert result.get("code") == 0, f"Token fetch failed: {result}"
    token = result["tenant_access_token"]

# Step 3 — send text message
msg = "🔄 FindEra → RKR 同步完成\n推送: 20 条\n失败: 0 条\n环境状态: 正常"
data = {
    "receive_id": "***SECRET***",
    "msg_type": "text",
    "content": json.dumps({"text": msg})
}
req = urllib.request.Request(
    "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=chat_id",
    data=json.dumps(data).encode(),
    headers={"Content-Type": "application/json", "Authorization": f"Bearer {token}"}
)
with urllib.request.urlopen(req) as resp:
    result = json.loads(resp.read())
    assert result.get("code") == 0, f"Message send failed: {result}"
    print("Sent:", result["data"]["message_id"])
