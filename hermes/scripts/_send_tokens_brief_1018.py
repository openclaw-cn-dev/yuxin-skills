import urllib.request, json, yaml

with open("/Users/hua/.hermes/config.yaml") as f:
    cfg = yaml.safe_load(f)

APP_ID = cfg["FEISHU_APP_ID"]
APP_SECRET = cfg["FEISHU_APP_SECRET"]

req = urllib.request.Request(
    "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
    data=json.dumps({"app_id": APP_ID, "app_secret": APP_SECRET}).encode(),
    headers={"Content-Type": "application/json"},
)
with urllib.request.urlopen(req) as resp:
    result = json.loads(resp.read())
    assert result.get("code") == 0, f"Token failed: {result}"
    token = result["tenant_access_token"]

msg = """📊 Tokens 消耗日报（2026-10-18）

【今日消耗】1,469K tokens
【7天均值】137,169K tokens
比例 0.0x ✅ 正常（无告警，远低于均值）

【Top Agent（今日）】
1. default：1,469K（100%）

【模型分布】
• glm：100%（1,469K）

📁 CSV（导入飞书多维表格）：
/Users/hua/.hermes/reports/tokens_2026-10-18.csv"""

data = {
    "receive_id": "***SECRET***",
    "msg_type": "text",
    "content": json.dumps({"text": msg}),
}
req = urllib.request.Request(
    "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=chat_id",
    data=json.dumps(data).encode(),
    headers={"Content-Type": "application/json", "Authorization": f"Bearer {token}"},
)
with urllib.request.urlopen(req) as resp:
    result = json.loads(resp.read())
    if result.get("code") == 0:
        print("Sent OK, message_id:", result["data"]["message_id"])
    else:
        print("Failed:", json.dumps(result, ensure_ascii=False))
