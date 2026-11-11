import urllib.request, json

APP_ID = "cli_a964873dd7b8dbda"
APP_SECRET = "***SECRET***"
CHAT_ID = "***SECRET***"

msg = ("[管理进化 11/8 异常] 公司资产迁移(11-07)致约18个cron仍引用旧路径，"
       "2个已失败: 分身OS-生活流采集(每30m cd失败)、KB知识库自同步(timeout)。"
       "建议迁移收尾后统一改cron路径。详见 reports/management_evolution/2026-11-08.md")

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
