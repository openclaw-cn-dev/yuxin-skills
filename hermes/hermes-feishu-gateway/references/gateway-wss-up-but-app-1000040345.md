# Gateway wss up 但 App 鉴权 1000040345 — 静默无响应 (2026-06-15 实测)

## 症状

- `hermes gateway list` 显示 `gongzuo - PID xxx - running`
- 日志显示 `feishu connected` 和 `Channel directory built: 0 target(s)`
- **用户在飞书发消息，bot 0 响应**
- `errors.log` 里有：
  ```
  ERROR Lark: connect failed, err: 1000040345: app_id or app_secret is invalid
  ```

## 根因

wss 长连接建立**不需要** App Secret（握手只用 AppID 即可建立 websocket）。但**收到消息时调 `/im/v1/messages` 等 API 才会触发 token 校验**：

1. 飞书 IM 收到用户消息 → 推 wss 事件给 hermes
2. hermes 调 `tenant_access_token/internal` 拿 token（**需要 App Secret**）
3. token API 返 `1000040345: app_id or app_secret is invalid`
4. hermes **静默丢弃**消息（log 一行 ERROR，不返用户）
5. 用户视角：bot "在线"但无响应

**这是 feishu-agent-onboarding step 7 验证清单的盲区** — `[Lark] connected to wss://...` 验证行**不检查 token API 是否通**，所以"feishu connected"出现后老大以为搞定了。

## 诊断流程

```bash
# 1. 找 errors.log
ls -la "C:\Users\Administrator\AppData\Local\hermes\profiles\<PROFILE>\logs\"

# 2. 关键字符串搜索
grep -E "1000040345|99991663|app secret" "C:\Users\Administrator\AppData\Local\hermes\profiles\<PROFILE>\logs\errors.log"

# 3. 看是否真值
cat "C:\Users\Administrator\AppData\Local\hermes\profiles\<PROFILE>\.env" | grep FEISHU_APP_***

# 4. size 应该是 32 字符（小于 30 = 被截断）
for f in "C:\Users\...\profiles\<PROFILE>\.env"; do
  python -c "import re; t=open(r'$f').read(); m=re.search(r'FEISHU_APP_SECRET=(.*)', t); s=m.group(1).strip() if m else 'NONE'; print(f'len={len(s)} val_tail=...{s[-6:] if len(s)>=6 else s}')"
done
```

## 修法（按推荐度）

### 方案 1：补 per-profile .env（**最快 30 秒**）

`App Secret` 没真值或被截断。走 `hermes-secret-handling/scripts/setup_per_profile_env.bat` 让老大手动粘一次。

**关键**：
- 改完 **必须** 重启 gateway：`hermes gateway stop -p <PROFILE>` + `hermes gateway run -p <PROFILE>`
- **不要** `hermes gateway restart` —— 旧 PID 文件锁可能不释放

### 方案 2：直接用 Python curl 验 token

```python
import json, urllib.request
APP_ID = "cli_xxx"  # 从 per-profile .env 读
APP_SECRET = "..."   # 完整 32 字符
data = json.dumps({"app_id": APP_ID, "app_secret": APP_SECRET}).encode()
req = urllib.request.Request(
    "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
    data=data, headers={"Content-Type": "application/json"})
resp = json.loads(urllib.request.urlopen(req, timeout=10).read().decode())
print(resp)
# 期望: {"code": 0, "msg": "ok", "tenant_access_token": "t-..."}
# 错误: {"code": 1000040345, "msg": "app_id or app_secret is invalid"}
```

### 方案 3：用 `hermes-feishu-gateway` skill 的 `verify_feishu.py` 脚本

跑一次会报每个 profile 的 `code=0` / `code=1000040345` 状态。

## 加进 step 7 验证清单的额外 2 行

```
- [ ] grep errors.log 没有 1000040345 / 99991663 / "app secret is invalid"
- [ ] python -c "import json,urllib.request; ..." 调一次 tenant_access_token API, code=0
```

## 配套：chat_id 也没设置时的类似静默

`config.yaml` 的 `feishu.allowed_chats` 是 `oc_PENDING` 占位：
- 飞书消息**能**进 hermes（token 通过后）
- hermes 检查 `allowed_chats` 不匹配 → **静默丢弃**
- 错误日志可能只有一行 `event from unauthorized chat, dropping`

修法：`oc_PENDING` → 老大给的真 chat_id，重启 gateway。

## 给 skill 作者的复盘

`feishu-agent-onboarding` 的 pitfall #4 "No allowlist = total denial" 覆盖了 `allowed_chats` 静默丢弃，但**没覆盖** `app_secret` 错也静默 — 因为错是 1000040345 不是"default deny"。

**正确归类**：第 11 个 pitfall，叫"App Secret 错也静默" — 加进 SKILL.md 末尾。
