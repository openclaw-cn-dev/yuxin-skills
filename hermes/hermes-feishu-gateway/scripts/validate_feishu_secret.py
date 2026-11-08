#!/usr/bin/env python3
"""
validate_feishu_secret.py — 5 秒验飞书 App Secret 是否被沙箱 redaction 截断

用法：
  python scripts/validate_feishu_secret.py <app_id> <app_secret>
  python scripts/validate_feishu_secret.py <app_id> --from-file ~/feishu-secret-tmp.txt

输出：
  ✅ LENGTH 32 + token ok → 完整版，直接用
  ❌ LENGTH <30 或 token 99991661 → 被 redaction 截了，让老大重发或走临时文件

原理：
  - 飞书 App Secret 标准 32 字符 base64 风格（如 <APP_SECRET>）
  - 沙箱 redact_secrets 把 16+ 字符的 base64 风格串截到 22 字符
  - 截断版调 token 接口 → code=99991661 "invalid app_secret"
  - 完整版调 token 接口 → code=0 + tenant_access_token
"""
import sys
import os
import json
import urllib.request

EXPECTED_LEN = 32  # 飞书 App Secret 标准长度


def read_secret(arg: str) -> str:
    if arg == "--from-file":
        path = sys.argv[3] if len(sys.argv) > 3 else "~/feishu-secret-tmp.txt"
        path = os.path.expanduser(path)
        with open(path, "r", encoding="utf-8") as f:
            return f.read().strip()
    return arg


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)

    app_id = sys.argv[1]
    secret = read_secret(sys.argv[2])

    print(f"APP_ID:   {app_id}")
    print(f"LENGTH:   {len(secret)}  (期望 {EXPECTED_LEN})")
    print(f"FIRST_4:  {secret[:4]}")
    print(f"LAST_4:   {secret[-4:]}")

    if len(secret) < 30:
        print(f"\n❌ Secret 太短（{len(secret)} 字符）—— 大概率被沙箱 redaction 截断了")
        print(f"   修法：让老大写到 ~/feishu-secret-tmp.txt（heredoc），重新跑")
        print(f"        python scripts/validate_feishu_secret.py {app_id} --from-file")
        sys.exit(2)

    # 调 token 接口验真伪
    data = json.dumps({"app_id": app_id, "app_secret": secret}).encode()
    req = urllib.request.Request(
        "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
        data=data,
        headers={"Content-Type": "application/json"},
    )
    try:
        resp = urllib.request.urlopen(req, timeout=10)
        result = json.loads(resp.read())
        code = result.get("code")
        token = result.get("tenant_access_token", "")
        if code == 0:
            print(f"\n✅ 完整版 + token 接口 OK")
            print(f"   TOKEN: {token[:20]}...（{len(token)} 字符）")
            sys.exit(0)
        else:
            print(f"\n❌ token 接口失败：code={code}, msg={result.get('msg')}")
            if code in (99991661, 99991663, 99991668):
                print(f"   code={code} 常见原因：")
                if code == 99991661:
                    print(f"   - Secret 仍被截（即使长度对，re 也可能改字符）→ 走临时文件")
                if code == 99991663:
                    print(f"   - App 没发布 → 飞书后台「版本管理与发布」走完")
                if code == 99991668:
                    print(f"   - App 权限不足 → 加 im:message 等 scope")
            sys.exit(3)
    except Exception as e:
        print(f"\n❌ 网络错误：{e}")
        sys.exit(4)


if __name__ == "__main__":
    main()
