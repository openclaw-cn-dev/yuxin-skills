import urllib.request, json, yaml

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
    token = result["tenant_access_token"]

def send_msg(receive_id, receive_id_type, text):
    data = {"receive_id": receive_id, "msg_type": "text", "content": json.dumps({"text": text})}
    req = urllib.request.Request(
        f"https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type={receive_id_type}",
        data=json.dumps(data).encode(),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {token}"}
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())

CHAT_ID = "***SECRET***"
HUAGE_OPEN_ID = "***SECRET***"

# 1. Starting message to big group
r1 = send_msg(CHAT_ID, "chat_id", "\u26f4 \u6b63\u5728\u6267\u884c\u6bcf\u65e5\u4f8b\u884c\u91cd\u542fHermes Gateway\u548cDocker\uff0c\u9884\u8ba12-3\u5206\u949f\u6062\u590d\u3002")
print("Msg1:", r1.get("code"), r1.get("msg"))

# 2. Completion message to big group
r2 = send_msg(CHAT_ID, "chat_id", "\u2705 \u6bcf\u65e5\u91cd\u542f\u5b8c\u6210\uff0c\u6240\u6709\u670d\u52a1\u5df2\u6062\u590d\u3002")
print("Msg2:", r2.get("code"), r2.get("msg"))

# 3. Report to Huage
r3 = send_msg(HUAGE_OPEN_ID, "open_id", "\u6bcf\u65e5\u91cd\u542f\u5b8c\u6210\u3002Docker\u5bb9\u5668\uff08lookforge-chromadb\u3001lookforge-backend\u3001lookforge-redis\u3001lookforge-db\u3001memos\uff09+ 7\u4e2aHermes Gateway profile + openclaw gateway \u5747\u5df2\u91cd\u542f\u3002")
print("Msg3:", r3.get("code"), r3.get("msg"))