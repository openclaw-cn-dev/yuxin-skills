"""Verify all Feishu App credentials in ~/feishu-secrets.json by calling
POST /open-apis/auth/v3/tenant_access_token/internal. Returns exit 0 iff
all credentials are valid. Prints a summary table with status + truncated token.

Usage:
    python verify_feishu.py

Dependencies: stdlib only (urllib). Hermes 0.15.1 has lark-oapi but you don't
need it for this — the raw HTTP API is simpler.

Output format:
    Agent          Status         Token/Err                        AppID tail
    --------------------------------------------------------------------------------
    agent-sales    OK             t-g10466bS...                    381be3
    agent-rd       OK             t-g10466c9...                    f89bdf
    ...
    4/4 credentials valid
"""
import json, sys, urllib.request, urllib.error

SECRETS_PATH = r"C:\Users\Administrator\feishu-secrets.json"
TOKEN_URL = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"


def get_token(app_id, app_secret):
    body = json.dumps({"app_id": app_id, "app_secret": app_secret}).encode("utf-8")
    req = urllib.request.Request(
        TOKEN_URL,
        data=body,
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read().decode("utf-8"))


def main():
    try:
        with open(SECRETS_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"ERROR: {SECRETS_PATH} not found. Run step 1 of the pipeline first.")
        sys.exit(2)

    results = []
    for name, info in data.get("agents", {}).items():
        app_id = info["app_id"]
        app_secret = info["app_secret"]
        try:
            payload = get_token(app_id, app_secret)
            code = payload.get("code")
            if code == 0:
                tok = payload.get("tenant_access_token", "")
                results.append((name, "OK", tok[:10] + "...", app_id[-6:]))
            else:
                results.append((name, f"FAIL code={code}", payload.get("msg", ""), app_id[-6:]))
        except urllib.error.HTTPError as e:
            results.append((name, f"FAIL HTTP {e.code}", e.reason, app_id[-6:]))
        except Exception as e:
            results.append((name, f"FAIL {type(e).__name__}", str(e)[:60], app_id[-6:]))

    print(f"{'Agent':<14} {'Status':<14} {'Token/Err':<32} {'AppID tail'}")
    print("-" * 80)
    for row in results:
        print(f"{row[0]:<14} {row[1]:<14} {row[2]:<32} {row[3]}")

    ok = sum(1 for r in results if r[1] == "OK")
    total = len(results)
    print(f"\n{ok}/{total} credentials valid")
    sys.exit(0 if ok == total else 1)


if __name__ == "__main__":
    main()
