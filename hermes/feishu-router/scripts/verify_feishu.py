import json, urllib.request, urllib.error, sys
secrets_path = r"C:\Users\Administrator\feishu-secrets.json"
with open(secrets_path, "r", encoding="utf-8") as f:
    data = json.load(f)
results = []
for name, info in data["agents"].items():
    body = json.dumps({"app_id": info["app_id"], "app_secret": info["app_secret"]}).encode("utf-8")
    req = urllib.request.Request(
        "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
        data=body, headers={"Content-Type": "application/json; charset=utf-8"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
        code = payload.get("code")
        if code == 0:
            tok = payload.get("tenant_access_token", "")[:10] + "..."
            results.append((name, "OK", tok, info["app_id"][-6:]))
        else:
            results.append((name, f"code={code}", payload.get("msg", ""), info["app_id"][-6:]))
    except urllib.error.HTTPError as e:
        results.append((name, f"HTTP {e.code}", e.reason, info["app_id"][-6:]))
    except Exception as e:
        results.append((name, type(e).__name__, str(e)[:60], info["app_id"][-6:]))
print(f"{'Agent':<14} {'Status':<12} {'Token/Err':<28} {'AppID tail'}")
print("-" * 75)
for row in results:
    print(f"{row[0]:<14} {row[1]:<12} {row[2]:<28} {row[3]}")
ok = sum(1 for r in results if r[1] == "OK")
print(f"\n{ok}/{len(results)} 凭据有效")
sys.exit(0 if ok == len(results) else 1)
