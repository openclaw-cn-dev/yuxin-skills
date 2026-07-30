import urllib.request, json

APP_ID = "cli_a964873dd7b8dbda"
APP_SECRET = "***SECRET***"

# Step 1 — get token
req = urllib.request.Request(
    "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
    data=json.dumps({"app_id": APP_ID, "app_secret": APP_SECRET}).encode(),
    headers={"Content-Type": "application/json"}
)
with urllib.request.urlopen(req) as resp:
    result = json.loads(resp.read())
    assert result.get("code") == 0, f"Token failed: {result}"
    token = result["tenant_access_token"]

# Step 2 — send message
msg = "Claude Code 更新通知\n\n已自动更新 Claude Code:\n- 旧版本: 2.1.167\n- 新版本: 2.1.168\n\n更新已完成。"
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
    print(json.dumps(result, ensure_ascii=False))