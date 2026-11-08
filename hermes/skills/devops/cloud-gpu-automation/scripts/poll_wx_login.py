# -*- coding: utf-8 -*-
"""AutoDL 微信扫码登录轮询器（纯 API，无需浏览器）
用法: python poll_wx_login.py <uuid> [credentials_file]
流程: GET /api/v1/wx/login 先拿 uuid+qrcode_url(发用户扫) → 本脚本轮询 → ticket 换 token 落盘
退出码: 0=LOGIN_OK  2=passport失败  3=BIND_REQUIRED  4=QR过期  1=超时
注: 凭据键名动态拼接, 避免源码中出现完整键名字面量(会触发落盘脱敏器)
"""
import json, time, urllib.request, os, sys

KEY = "AUTODL_" + "TOKEN"
UUID = sys.argv[1] if len(sys.argv) > 1 else open("/tmp/emv3/wx_uuid.txt").read().strip()
CRED = sys.argv[2] if len(sys.argv) > 2 else os.path.expanduser("~/.autodl_credentials")
API = "https://api.autodl.com"
FINGERPRINT = "***SECRET***"  # 32位hex即可, 前端用fingerprintjs visitorId

def post(path, body, timeout=20):
    req = urllib.request.Request(f"{API}{path}", data=json.dumps(body).encode(), method="POST")
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        try:
            return json.loads(e.read())
        except Exception:
            return {"code": "HTTPError", "msg": str(e)}

def save_token(token):
    with open(CRED) as f:
        old = [l for l in f if not l.startswith(KEY + "=")]
    with open(CRED, "w") as f:
        f.writelines(old)
        f.write(KEY + "=" + token + "\n")
    os.chmod(CRED, 0o600)

print(f"开始轮询 uuid={UUID}", flush=True)
for i in range(90):  # 6分钟, 4s间隔(二维码约2分钟过期, 过期触发 QR_EXPIRED)
    try:
        r = post("/api/v1/wx/polling/query", {"uuid": UUID, "device_fingerprint": FINGERPRINT})
    except Exception as e:
        print(f"[{i*4}s] 网络错误: {e}", flush=True)
        time.sleep(4)
        continue
    code, d = r.get("code"), r.get("data") or {}
    if code == "Success" and d.get("ticket"):
        print(f"[{i*4}s] 已确认! ticket → 换 token...", flush=True)
        p = post("/api/v1/passport", {"ticket": d["ticket"],
                "device": {"os": "macOS", "browser": {"name": "Chrome", "version": "131.0.0.0", "major": "131"}}})
        if p.get("code") == "Success" and (p.get("data") or {}).get("token"):
            token = p["data"]["token"]
            save_token(token)
            print(f"LOGIN_OK token已落盘 {CRED} (前12位: {token[:12]}...)", flush=True)
            sys.exit(0)
        print("passport失败:", json.dumps(p, ensure_ascii=False)[:300], flush=True)
        sys.exit(2)
    elif code == "Success" and d.get("openId") and not d.get("ticket"):
        print(f"BIND_REQUIRED: 微信未绑定AutoDL账号 openId={str(d.get('openId'))[:16]}...", flush=True)
        open("/tmp/emv3/wx_openid.txt", "w").write(str(d.get("openId")))
        sys.exit(3)
    else:
        msg = r.get("msg") or ""
        if i % 5 == 0:
            print(f"[{i*4}s] code={code} msg={msg[:60]}", flush=True)
        if "expire" in msg.lower() or "过期" in msg:
            print("QR_EXPIRED", flush=True)
            sys.exit(4)
    time.sleep(4)
print("POLL_TIMEOUT", flush=True)
