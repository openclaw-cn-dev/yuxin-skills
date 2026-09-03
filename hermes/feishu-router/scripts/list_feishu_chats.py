import json, urllib.request, urllib.error, time
secrets_path = r"C:\Users\Administrator\feishu-secrets.json"
with open(secrets_path, "r", encoding="utf-8") as f:
    data = json.load(f)
def get_token(app_id, app_secret):
    body = json.dumps({"app_id": app_id, "app_secret": app_secret}).encode("utf-8")
    req = urllib.request.Request(
        "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
        data=body, headers={"Content-Type": "application/json; charset=utf-8"}, method="POST")
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.loads(r.read())["tenant_access_token"]
def list_chats(token):
    url = "https://open.feishu.cn/open-apis/im/v1/chats?page_size=50"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json; charset=utf-8"})
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.loads(r.read())
for name, info in data["agents"].items():
    print(f"\n=== {name} ({info['purpose']}) ===")
    print(f"    AppID: {info['app_id']}")
    try:
        token = get_token(info["app_id"], info["app_secret"])
        resp = list_chats(token)
        code = resp.get("code")
        items = resp.get("data", {}).get("items", [])
        if code == 0:
            if not items:
                print("    [empty] 机器人尚未加入任何群 (需在飞书 GUI 把机器人加进群)")
            else:
                print(f"    已加群 ({len(items)} 个):")
                for c in items:
                    print(f"        - {c.get('name','(unnamed)'):<20}  chat_id={c.get('chat_id','')}")
        else:
            print(f"    [ERR] code={code}: {resp.get('msg','')}")
    except urllib.error.HTTPError as e:
        print(f"    [ERR] HTTP {e.code}: {e.reason}")
    except Exception as e:
        print(f"    [ERR] {type(e).__name__}: {str(e)[:80]}")
    time.sleep(0.3)
