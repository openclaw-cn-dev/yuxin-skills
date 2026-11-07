"""Verify all Feishu App credentials in ~/feishu-secrets.json by calling
POST /open-apis/auth/v3/tenant_access_token/internal.

Usage:
    python scripts/verify_feishu_apps.py
    python scripts/verify_feishu_apps.py --secrets /path/to/secrets.json

Exit code 0 = all valid, 1 = at least one failed.
"""
import json
import sys
import urllib.error
import urllib.request
import argparse
from pathlib import Path

DEFAULT_SECRETS = Path.home() / "feishu-secrets.json"
TOKEN_URL = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"


def verify(app_id: str, app_secret: str) -> tuple[bool, str]:
    body = json.dumps({"app_id": app_id, "app_secret": app_secret}).encode("utf-8")
    req = urllib.request.Request(
        TOKEN_URL, data=body,
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            payload = json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return False, f"HTTP {e.code} {e.reason}"
    except Exception as e:
        return False, f"{type(e).__name__}: {str(e)[:80]}"

    if payload.get("code") == 0:
        token = payload.get("tenant_access_token", "")
        return True, f"token={token[:12]}..."
    return False, f"code={payload.get('code')} {payload.get('msg', '')}"


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--secrets", default=str(DEFAULT_SECRETS))
    args = p.parse_args()

    path = Path(args.secrets)
    if not path.exists():
        print(f"❌ secrets file not found: {path}", file=sys.stderr)
        return 2

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    agents = data.get("agents", {})
    if not agents:
        print(f"❌ no agents in {path}", file=sys.stderr)
        return 2

    print(f"{'Agent':<16} {'Status':<10} {'Detail':<40} {'AppID tail'}")
    print("-" * 80)
    ok_count = 0
    for name, info in agents.items():
        valid, detail = verify(info["app_id"], info["app_secret"])
        status = "✅ OK" if valid else "❌ FAIL"
        print(f"{name:<16} {status:<10} {detail:<40} {info['app_id'][-6:]}")
        if valid:
            ok_count += 1

    print(f"\n{ok_count}/{len(agents)} 凭据有效")
    return 0 if ok_count == len(agents) else 1


if __name__ == "__main__":
    sys.exit(main())
