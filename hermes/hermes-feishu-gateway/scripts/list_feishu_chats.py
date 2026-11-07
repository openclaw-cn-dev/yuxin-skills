"""List all chats (groups) each Feishu bot can see.

Reads ~/feishu-secrets.json. For each agent, gets a tenant_access_token,
then lists /open-apis/im/v1/chats?page_size=50.

Output format:
  === agent-sales (飞书销售群...) ===
      AppID: cli_xxx
      joined N groups:
        - group name   chat_id=oc_xxx

Usage:
  python list_feishu_chats.py [path-to-secrets.json]

Default path: C:/Users/Administrator/feishu-secrets.json (override with arg).

No args required, no env vars required (everything is read from the JSON).
"""
import json, sys, time, urllib.request

DEFAULT_SECRETS_PATH = r"C:\Users\Administrator\feishu-secrets.json"


def get_token(app_id, app_secret):
    body = json.dumps({"app_id": app_id, "app_secret": app_secret}).encode("utf-8")
    req = urllib.request.Request(
        "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
        data=body,
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.loads(r.read())["tenant_access_token"]


def list_chats(token):
    url = "https://open.feishu.cn/open-apis/im/v1/chats?page_size=50"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.loads(r.read())


def main(secrets_path):
    with open(secrets_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    for name, info in data["agents"].items():
        print(f"\n=== {name} ({info.get('purpose', '')}) ===")
        print(f"    AppID: {info['app_id']}")
        try:
            token = get_token(info["app_id"], info["app_secret"])
            resp = list_chats(token)
            code = resp.get("code")
            items = resp.get("data", {}).get("items", [])
            if code == 0:
                if not items:
                    print("    [empty] bot is not in any group yet (have the user add it via Feishu GUI)")
                else:
                    print(f"    joined {len(items)} groups:")
                    for c in items:
                        print(f"        - {c.get('name', '(no name)'):<20}  chat_id={c.get('chat_id', '')}")
            else:
                print(f"    [error] code={code}: {resp.get('msg', '')}")
        except Exception as e:
            print(f"    [error] {type(e).__name__}: {str(e)[:80]}")
        time.sleep(0.3)


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_SECRETS_PATH
    main(path)
