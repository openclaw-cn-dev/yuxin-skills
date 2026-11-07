"""Cookie 有效性验证工具 — 给小弟拿到 cookie 字符串后第一次跑

用法:
    python cookie_verify.py zhihu 'z_c0=abc; SESSIONID=def'
    python cookie_verify.py xhs '{"web_session":"abc","a1":"def"}'
    python cookie_verify.py douyin 'sessionid=abc; ttwid=def'

支持平台: zhihu / xhs / douyin / weibo / bilibili
"""
import json
import subprocess
import sys


PLATFORM_PROBES = {
    "zhihu": {
        "url": "https://www.zhihu.com/api/v4/me",
        "success_keys": ["id", "name", "url_token"],
        "expired_signals": ["100", "未登录", "请先登录"],
    },
    "xhs": {
        "url": "https://edith.xiaohongshu.com/api/sns/web/v2/user/me",
        "success_keys": ["user_id", "nickname"],
        "expired_signals": ["登录已过期", "未登录"],
    },
    "douyin": {
        "url": "https://www.douyin.com/aweme/v1/web/user/profile/other/",
        "success_keys": ["user", "status_code"],
        "expired_signals": ["not login", "请先登录"],
    },
    "weibo": {
        "url": "https://m.weibo.cn/api/container/getIndex",
        "success_keys": ["ok", "user"],
        "expired_signals": ["登录", "expired"],
    },
    "bilibili": {
        "url": "https://api.bilibili.com/x/web-interface/nav",
        "success_keys": ["isLogin", "uname", "data"],
        "expired_signals": ["-101", "未登录"],
    },
}


def parse_cookies(arg: str) -> dict:
    """支持 'k=v; k=v' 或 '{"k":"v"}' 两种格式"""
    arg = arg.strip().strip('"').strip("'")
    if arg.startswith("{"):
        return json.loads(arg)
    cookies = {}
    for kv in arg.split(";"):
        kv = kv.strip()
        if not kv:
            continue
        if "=" not in kv:
            continue
        k, v = kv.split("=", 1)
        cookies[k.strip()] = v.strip()
    return cookies


def validate(platform: str, cookies: dict) -> dict:
    """返回 {"valid": bool, "info": str, "fingerprint": str}"""
    if platform not in PLATFORM_PROBES:
        return {"valid": False, "info": f"不支持的平台: {platform}", "fingerprint": ""}

    probe = PLATFORM_PROBES[platform]
    cookie_str = "; ".join(f"{k}={v}" for k, v in cookies.items())

    try:
        r = subprocess.run(
            ["curl", "-s", "-m", "10",
             "-H", f"Cookie: {cookie_str}",
             "-H", "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
             probe["url"]],
            capture_output=True, text=True, timeout=15
        )
        body = r.stdout
    except subprocess.TimeoutExpired:
        return {"valid": False, "info": "请求超时（10s）", "fingerprint": ""}

    # 找任一 success_key
    valid = any(k in body for k in probe["success_keys"])
    expired = any(sig.lower() in body.lower() for sig in probe["expired_signals"])

    fp = f"{platform}:{len(cookies)} cookies, " + ", ".join(list(cookies.keys())[:3])

    if valid and not expired:
        return {"valid": True, "info": f"✅ 有效 (响应 {len(body)} chars)", "fingerprint": fp}
    if expired:
        return {"valid": False, "info": "❌ 已过期或未登录", "fingerprint": fp}
    return {"valid": False, "info": f"⚠️ 状态不明 (响应 {len(body)} chars, 前 200: {body[:200]})", "fingerprint": fp}


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)

    platform = sys.argv[1].lower()
    cookie_arg = sys.argv[2]

    cookies = parse_cookies(cookie_arg)
    result = validate(platform, cookies)

    print(f"\n=== {platform.upper()} Cookie 验证 ===")
    print(f"指纹: {result['fingerprint']}")
    print(f"结果: {result['info']}")
    sys.exit(0 if result["valid"] else 2)


if __name__ == "__main__":
    main()
