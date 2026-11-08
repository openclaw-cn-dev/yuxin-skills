import urllib.request, json, yaml

with open("/Users/hua/.hermes/config.yaml") as f:
    cfg = yaml.safe_load(f)

APP_ID = cfg["FEISHU_APP_ID"]
APP_SECRET = cfg["FEISHU_APP_SECRET"]

# Get tenant access token
req = urllib.request.Request(
    "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
    data=json.dumps({"app_id": APP_ID, "app_secret": APP_SECRET}).encode(),
    headers={"Content-Type": "application/json"}
)
with urllib.request.urlopen(req) as resp:
    result = json.loads(resp.read())
assert result.get("code") == 0, f"Token fetch failed: {result}"
token = result["tenant_access_token"]

msg = """📊 Tokens多维统计日报（10月7日）

【今日消耗 vs 7天均值】
今日: 113,341K tokens
7天均值: 299,941K tokens
比例: 0.4x ✅ 正常（远低于均值，无异常）

【Top 3消费Agent（今日）】
1️⃣ default: 79,093K (69.7%)
2️⃣ zhenglishi: 32,937K (29.1%)
3️⃣ laomo: 1,311K (1.2%)

【模型分布（今日）】
• glm: 69% (78,702K)
• minimax: 31% (34,638K)

【CSV文件（导入飞书多维表格）】
/Users/hua/.hermes/reports/tokens_2026-10-07.csv"""

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
with urllib.request.urmlopen if False else urllib.request.urlopen(req) as resp:
    result = json.loads(resp.read())
assert result.get("code") == 0, f"Message send failed: {result}"
print("Sent:", result["data"]["message_id"])
