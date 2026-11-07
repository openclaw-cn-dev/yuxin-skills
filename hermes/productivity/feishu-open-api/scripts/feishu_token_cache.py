# -*- coding: utf-8 -*-
"""feishu_token_cache.py — get + cache 飞书 tenant_access_token.

Usage:
    from feishu_token_cache import get_token
    tok = get_token("cli_xxx", "secret_yyy", cache_path="tok.json")
    # tok is the cached token string. Refreshed automatically if < 10 min remain.
"""
import urllib.request, urllib.parse, json, ssl, time, os

DEFAULT_REFRESH_MARGIN = 600  # 10 minutes before expiry


def get_token(app_id, app_secret, cache_path="feishu_token.json",
              refresh_margin=DEFAULT_REFRESH_MARGIN, timeout=15):
    """Return a valid tenant_access_token, refreshing cache if needed.

    Args:
        app_id: 飞书 app ID (cli_…)
        app_secret: 飞书 app secret
        cache_path: file to persist token
        refresh_margin: seconds before expiry to force refresh
        timeout: HTTP timeout

    Returns:
        str: a valid tenant_access_token
    """
    # Try cache first
    if os.path.exists(cache_path):
        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                cached = json.load(f)
            if (cached.get("app_id") == app_id
                    and cached.get("expire_at", 0) > time.time() + refresh_margin):
                return cached["tenant_access_token"]
        except (json.JSONDecodeError, KeyError, OSError):
            pass  # corrupt cache, fall through to refresh

    # Fetch fresh token
    data = urllib.parse.urlencode({
        "app_id": app_id,
        "app_secret": app_secret
    }).encode("utf-8")
    ctx = ssl.create_default_context()
    req = urllib.request.Request(
        "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
        data=data, method="POST",
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    with urllib.request.urlopen(req, context=ctx, timeout=timeout) as r:
        result = json.loads(r.read().decode("utf-8"))

    if result.get("code") != 0:
        raise RuntimeError(
            f"feishu token fetch failed: code={result.get('code')} msg={result.get('msg')}"
        )

    token = result["tenant_access_token"]
    expire = result.get("expire", 7200)
    cache_data = {
        "app_id": app_id,
        "tenant_access_token": token,
        "expire": expire,
        "expire_at": time.time() + expire,
        "fetched_at": time.time(),
    }
    os.makedirs(os.path.dirname(os.path.abspath(cache_path)) or ".", exist_ok=True)
    with open(cache_path, "w", encoding="utf-8") as f:
        json.dump(cache_data, f, indent=2, ensure_ascii=False)
    return token


def invalidate(cache_path):
    """Force the next call to fetch a new token."""
    if os.path.exists(cache_path):
        os.remove(cache_path)


if __name__ == "__main__":
    # CLI mode: python feishu_token_cache.py <app_id> <app_secret> [cache_path]
    import sys
    if len(sys.argv) < 3:
        print("Usage: python feishu_token_cache.py <app_id> <app_secret> [cache_path]")
        sys.exit(1)
    app_id = sys.argv[1]
    app_secret = sys.argv[2]
    cache_path = sys.argv[3] if len(sys.argv) > 3 else "feishu_token.json"
    tok = get_token(app_id, app_secret, cache_path)
    print(f"OK token cached to {cache_path}")
    print(f"   length: {len(tok)} chars")
    print(f"   preview: {tok[:24]}…")
