import urllib.request, json, yaml

# Read config
with open("/Users/hua/.hermes/config.yaml") as f:
    cfg = yaml.safe_load(f)

APP_ID = cfg["FEISHU_APP_ID"]
APP_SECRET = cfg["FEISHU_APP_SECRET"]

# Get token
req = urllib.request.Request(
    "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
    data=json.dumps({"app_id": APP_ID, "app_secret": APP_SECRET}).encode(),
    headers={"Content-Type": "application/json"}
)
with urllib.request.urlopen(req) as resp:
    result = json.loads(resp.read())
    assert result.get("code") == 0, f"Token failed: {result}"
    token = result["tenant_access_token"]

# Build message
msg = """📊 Tokens 多维统计日报（2026-06-15）

【今日消耗】
• 输入 3.61M / 输出 239K（会话 160）
• 7天均值 6.77M | 今日比例 0.6x ✅ 正常

【Top 3 消费Agent（30日）】
1. 飞书用户 47.39M（32.2%）
2. 华哥 18.91M（12.9%）
3. Cron心跳 18.53M（12.6%）

【模型分布（30日）】
• MiniMax-M2.7 56.1%
• minimax-2.7 40.5%
• deepseek-v4-pro 2.5%
• MiniMax-M2.7-highspeed 0.8%

📁 CSV文件（导入飞书多维表格）
~/.hermes/cron/output/tokens_by_day_20260615.csv
~/.hermes/cron/output/tokens_by_agent_20260615.csv
~/.hermes/cron/output/tokens_by_model_20260615.csv
~/.hermes/cron/output/tokens_detail_20260615.csv"""

# Send to chat (oc_xxx = chat_id)
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
    if result.get("code") == 0:
        print("Sent:", result["data"]["message_id"])
    else:
        print("Failed:", result)