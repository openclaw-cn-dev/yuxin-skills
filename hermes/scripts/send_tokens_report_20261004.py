import urllib.request, json, yaml

with open("/Users/hua/.hermes/config.yaml") as f:
    cfg = yaml.safe_load(f)

req = urllib.request.Request(
    "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
    data=json.dumps({"app_id": cfg["FEISHU_APP_ID"], "app_secret": cfg["FEISHU_APP_SECRET"]}).encode(),
    headers={"Content-Type": "application/json"}
)
with urllib.request.urlopen(req) as resp:
    result = json.loads(resp.read())
    assert result.get("code") == 0, f"Token failed: {result}"
    token = result["tenant_access_token"]

msg = """📊 Tokens 多维统计日报（2026-10-04）

【今日消耗】85,684K tokens
7天均值 265,180K | 今日比例 0.3x ✅ 正常（远低于均值，无告警）

【Top 3 消费Agent（今日）】
1. default 85,684K（100%，今日仅此 Agent 有消耗）

【模型分布（今日）】
• glm 100%（85,684K）

📁 CSV路径（可导入飞书多维表格）：
/Users/hua/.hermes/reports/tokens_2026-10-04.csv"""

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
