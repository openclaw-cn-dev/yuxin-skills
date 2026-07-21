import urllib.request, json, yaml

with open("/Users/hua/.hermes/config.yaml") as f:
    cfg = yaml.safe_load(f)

APP_ID = cfg["FEISHU_APP_ID"]
APP_SECRET = cfg["FEISHU_APP_SECRET"]

# Step 2 - get token
req = urllib.request.Request(
    "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
    data=json.dumps({"app_id": APP_ID, "app_secret": APP_SECRET}).encode(),
    headers={"Content-Type": "application/json"}
)
with urllib.request.urlopen(req) as resp:
    result = json.loads(resp.read())
assert result.get("code") == 0, f"Token fetch failed: {result}"
token = result["tenant_access_token"]

# Step 3 - send text message to 华哥
msg = """📊 Tokens多维统计日报（6月6日）

【今日消耗】
输入: 679K | 输出: 20K | 会话: 44
7天均值: 4.34M | 比例: 0.2x ✅
（远低于均值，无异常）

【Top 3消费Agent（30日）】
1️⃣ 飞书用户: 52.50M (33.7%)
2️⃣ 学习助手-知识库心跳: 22.61M (14.5%)
3️⃣ 宽博士-量化研究心跳: 19.21M (12.3%)

【模型分布（30日）】
• minimax-2.7: 83.18M (53.4%)
• M2.7-highspeed: 34.07M (21.9%)
• M2.7: 28.06M (18.0%)
• deepseek-v4-pro: 8.97M (5.8%)

【CSV文件（导入飞书多维表格）】
~/.hermes/cron/output/tokens_by_day_20260606.csv
~/.hermes/cron/output/tokens_by_agent_20260606.csv
~/.hermes/cron/output/tokens_by_model_20260606.csv
~/.hermes/cron/output/tokens_detail_20260606.csv"""

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