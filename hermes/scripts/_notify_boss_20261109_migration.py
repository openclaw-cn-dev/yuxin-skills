import urllib.request, json

APP_ID = "cli_a964873dd7b8dbda"
APP_SECRET = "***SECRET***"
CHAT_ID = "***SECRET***"

msg = ("[管理进化 11/9] 迁移断链2脚本已修复(生活流采集+KB自同步,已验证)。"
       "⚠️新发现:Agent资料增量迁移→RKR中转站 job 已过期5天、引用已删的rkr_staging路径,下次11-15必失败;"
       "另有~13个活跃job的prompt仍内嵌旧研目录路径,建议批量改jobs.json路径前缀。详见 2026-11-09.md")

req = urllib.request.Request(
    "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
    data=json.dumps({"app_id": APP_ID, "app_secret": APP_SECRET}).encode(),
    headers={"Content-Type": "application/json"},
)
tok = json.loads(urllib.request.urlopen(req, timeout=15).read())
assert tok.get("code") == 0, tok
t = tok["tenant_access_token"]

data = {
    "receive_id": CHAT_ID,
    "msg_type": "text",
    "content": json.dumps({"text": msg}),
}
req = urllib.request.Request(
    "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=chat_id",
    data=json.dumps(data).encode(),
    headers={"Content-Type": "application/json", "Authorization": "Bearer " + t},
)
r = json.loads(urllib.request.urlopen(req, timeout=15).read())
print("send code:", r.get("code"), "msg_id:", r.get("data", {}).get("message_id"))
