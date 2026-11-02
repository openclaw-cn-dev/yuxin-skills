import urllib.request, json, yaml

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
assert result.get("code") == 0, f"Token fetch failed: {result}"
token = result["tenant_access_token"]

msg = """📊 Tokens 多维统计日报（2026-09-26）

【今日消耗 vs 7天均值】
今日 154,233K | 7天均值 220,441K
比例 0.7x ✅ 正常（低于均值，无告警）

【Top 3 消费 Agent（今日）】
1️⃣ default 79,313K（51.4%）
2️⃣ zhenglishi 71,228K（46.2%）
3️⃣ laomo 3,691K（2.4%）

【模型分布（今日）】
• GLM（glm）100%：154,233K

✅ 无告警项（无 Agent 超过 7天均值 2x）

📁 CSV文件（导入飞书多维表格）
/Users/hua/.hermes/reports/tokens_2026-09-26.csv"""

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
