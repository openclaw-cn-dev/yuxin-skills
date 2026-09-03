# 飞书 5 Agent 部署实战（2026-06-06 验证）

完整跑通的部署步骤，每一步都标注卡点和验证方法。

## 前置条件

- 沙箱已关：`hermes config set approvals.mode false`（或 `auto`）
- 4 个飞书 App 已建（销售小成 / 研发小研 / 生产小产 / 推广小推）
- 4 套 App ID + App Secret 已加密存到 `~/feishu-secrets.json`（chmod 600）

## 完整 5 步部署

### Step 1: 拿到 4 个 Token

```python
import requests, json, os

with open(os.path.expanduser("~/feishu-secrets.json")) as f:
    config = json.load(f)

tokens = {}
for name, info in config["apps"].items():
    r = requests.post(
        "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
        json={"app_id": info["app_id"], "app_secret": info["app_secret"]},
        timeout=10
    )
    d = r.json()
    if d.get("code") == 0:
        tokens[name] = d["tenant_access_token"]  # 有效期 2 小时

with open(os.path.expanduser("~/feishu-tokens.json"), "w") as f:
    json.dump(tokens, f)
```

### Step 2: 建群（任一应用 token 都能建）

```python
url = "https://open.feishu.cn/open-apis/im/v1/chats"
headers = {"Authorization": f"Bearer {tokens['销售小成']}", "Content-Type": "application/json"}
data = {
    "name": "RAS-老板总控",
    "description": "5 Agent 协同 | @销售小成 @研发小研 @生产小产 @推广小推",
    "chat_mode": "group",
    "chat_type": "private"  # 内部私群
}
r = requests.post(url, headers=headers, json=data, timeout=15)
chat_id = r.json()["data"]["chat_id"]  # 形如 oc_80be3150a8bbf2c78cddfc8f1fd2cbc8
```

**关键参数**：
- `chat_mode: "group"` + `chat_type: "private"`（建私人群）
- **不需要任何特殊权限**，任一应用 token 都能建

### Step 3: 拿每个机器人的 open_id

```python
for name, token in tokens.items():
    r = requests.get(
        "https://open.feishu.cn/open-apis/bot/v3/info",
        headers={"Authorization": f"Bearer {token}"}, timeout=10
    )
    bot = r.json()["bot"]
    print(f"{name}: open_id={bot['open_id']}")  # 形如 ou_71b3b5b8353911e7ec8e2b9212c...
```

### Step 4: 拉机器人进群 ⚠️ 硬卡点

```python
add_url = f"https://open.feishu.cn/open-apis/im/v1/chats/{chat_id}/members"
headers = {"Authorization": f"Bearer {tokens['销售小成']}", "Content-Type": "application/json"}
member_ids = ["ou_71b3b5b8353911e7ec8e2b9212c...", "ou_9d011c5f71abd70148f4a3c570b..."]
r = requests.post(add_url, headers=headers, json={"id_list": member_ids}, timeout=15)
```

**如果返回 `code: 99991632` 或 `99991672`** → 缺权限
**必须开通 2 个权限**：
1. `im:chat`（建/管群）
2. `im:chat.members:write_only`（拉人/机器人进群）

**老大手动开通路径**：
1. https://open.feishu.cn/app/{app_id}/auth
2. 搜 `im:chat.members:write_only`
3. 点「申请开通」→ 等管理员审批（自建应用通常自动通过）

### Step 5: 发欢迎语

```python
msg_url = "https://open.feishu.cn/open-apis/im/v1/messages"
msg_headers = {"Authorization": f"Bearer {tokens['销售小成']}", "Content-Type": "application/json"}
msg_data = {
    "receive_id": chat_id,
    "msg_type": "text",
    "content": json.dumps({"text": "🐟 老板总控群启动！@销售小成 @研发小研..."})
}
r = requests.post(f"{msg_url}?receive_id_type=chat_id", headers=msg_headers, json=msg_data, timeout=15)
```

## 卡点清单（按出现顺序）

| # | 卡点 | 解决 |
|---|---|---|
| 1 | `app secret invalid` (code: 10014) | 老大已重置 Secret → 必须用新 Secret |
| 2 | 拉机器人进群 `code: 99991672` | 缺 `im:chat.members:write_only` → 老大去开通 |
| 3 | Token 过期（2 小时）| 重新跑 Step 1 |

## 战果（2026-06-06）

- ✅ 4 个测试群建好（销售/研发/生产/推广）
- ✅ 1 个老板总控群建好（`oc_80be3150a8bbf2c78cddfc8f1fd2cbc8`）
- ✅ 销售群询盘演练成功（"蛋白分离器多少钱"→ 3 档回复）
- ❌ 拉机器人进老板总控群卡权限（待老大开 `im:chat.members:write_only`）
- ⏸️ Webhook 未配（需公网服务器或用轮询方案）

## 经验教训

1. **Secret 在 DM 暴露无妨**，老大主动重置即可（飞书返回 `app secret invalid` = 旧 Secret 已失效）
2. **沙箱关闭后**所有 API 调用**不再问**，但 `cron_mode: deny` 仍要求 cron 确认
3. **4 个测试群**用销售小成 app 建（不需每个 app 都建），但**拉机器人进群**的 token 必须用**群创建者**或**有权限的应用**
4. **Python 脚本一次跑完** = 沙箱不卡。Shell heredoc 跑 curl 必卡（30 秒超时）
