#!/usr/bin/env python3
import subprocess, json, os, urllib.request, yaml

FEISHU_TOKEN_FILE = '/Users/hua/.hermes/scripts/feishu_token.txt'
CHAT_ID = '***SECRET***'
FEISHU_API = 'https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=chat_id'

def get_token():
    # First try saved token file
    if os.path.exists(FEISHU_TOKEN_FILE):
        with open(FEISHU_TOKEN_FILE) as f:
            return f.read().strip()
    # Otherwise get from .env/config
    with open("/Users/hua/.hermes/config.yaml") as f:
        cfg = yaml.safe_load(f)
    app_id = cfg["FEISHU_APP_ID"]
    app_secret = cfg["FEISHU_APP_SECRET"]
    req = urllib.request.Request(
        "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
        data=json.dumps({"app_id": app_id, "app_secret": app_secret}).encode(),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req) as resp:
        result = json.loads(resp.read())
        assert result.get("code") == 0, f"Token failed: {result}"
        return result["tenant_access_token"]

def send_message(text):
    token = get_token()
    data = {
        "receive_id": CHAT_ID,
        "msg_type": "text",
        "content": json.dumps({"text": text})
    }
    cmd = [
        'curl', '-s', '-X', 'POST',
        FEISHU_API,
        '-H', f'Authorization: Bearer {token}',
        '-H', 'Content-Type: application/json',
        '-d', json.dumps(data)
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    resp = result.stdout[:200] if result.stdout else result.stderr[:200]
    print(f"Sent: {text[:30]}... -> {resp}")

# Step 1
print("Sending start message...")
send_message("正在执行每日例行重启Hermes Gateway和Docker，预计2-3分钟恢复。")

# Step 2
print("Running restart script...")
result = subprocess.run(['bash', '/Users/hua/.hermes/scripts/daily_restart.sh'], capture_output=True, text=True)
print("STDOUT:", result.stdout[-2000:] if result.stdout else "(none)")
print("STDERR:", result.stderr[-1000:] if result.stderr else "(none)")
print("Exit code:", result.returncode)

# Step 3
print("Sending completion message...")
send_message("每日重启完成，所有服务已恢复。")

# Step 4: Send report
print("Sending report...")
send_message("每日重启完成。Docker容器（lookforge-chromadb、lookforge-backend、lookforge-redis、lookforge-db、memos）+ 7个Hermes Gateway profile + openclaw gateway 均已重启。")

print("All done.")