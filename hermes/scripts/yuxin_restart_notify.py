import urllib.request, json, yaml

# Load credentials
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
    assert result.get("code") == 0, f"Token fetch failed: {result}"
    token = result["tenant_access_token"]

print("Token obtained")

# Target groups
targets = [
    {"name": "商务运营群（小宝）", "chat_id": "***SECRET***"},
    {"name": "知识库群（老莫）", "chat_id": "***SECRET***"},
    {"name": "产品群（毛豆）", "chat_id": "***SECRET***"},
    {"name": "行政群（黑豆）", "chat_id": "***SECRET***"},
    {"name": "客服群（阿福）", "chat_id": "***SECRET***"},
]

open_ids = {
    "老莫": "***SECRET***",
    "黑豆": "***SECRET***",
    "阿福": "***SECRET***",
}

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {token}"
}

results = []
for t in targets:
    name = t["name"]
    chat_id = t["chat_id"]

    if "老莫" in name:
        content = [[{"tag": "at", "user_id": open_ids["老莫"]}, {"tag": "text", "text": " 各位Agent，10分钟后（8:00）将重启Hermes Gateway和Docker，请整理好当前进度、记忆、待办事项，准备好交接。"}]]
        data = {"receive_id": chat_id, "msg_type": "post", "content": json.dumps({"zh_cn": {"title": "", "content": content}})}
    elif "黑豆" in name:
        content = [[{"tag": "at", "user_id": open_ids["黑豆"]}, {"tag": "text", "text": " 各位Agent，10分钟后（8:00）将重启Hermes Gateway和Docker，请整理好当前进度、记忆、待办事项，准备好交接。"}]]
        data = {"receive_id": chat_id, "msg_type": "post", "content": json.dumps({"zh_cn": {"title": "", "content": content}})}
    elif "阿福" in name:
        content = [[{"tag": "at", "user_id": open_ids["阿福"]}, {"tag": "text", "text": " 各位Agent，10分钟后（8:00）将重启Hermes Gateway和Docker，请整理好当前进度、记忆、待办事项，准备好交接。"}]]
        data = {"receive_id": chat_id, "msg_type": "post", "content": json.dumps({"zh_cn": {"title": "", "content": content}})}
    else:
        data = {"receive_id": chat_id, "msg_type": "text", "content": json.dumps({"text": "各位Agent，10分钟后（8:00）将重启Hermes Gateway和Docker，请整理好当前进度、记忆、待办事项，准备好交接。"})}

    url = f"https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=chat_id"
    req = urllib.request.Request(url, data=json.dumps(data).encode(), headers=headers, method="POST")

    try:
        with urllib.request.urlopen(req) as resp:
            result = json.loads(resp.read())
            code = result.get("code")
            if code == 0:
                results.append(f"[OK] {name}: message_id={result['data']['message_id']}")
            else:
                results.append(f"[FAIL] {name}: code={code} msg={result.get('msg','')}")
    except Exception as e:
        results.append(f"[ERROR] {name}: {e}")

for r in results:
    print(r)