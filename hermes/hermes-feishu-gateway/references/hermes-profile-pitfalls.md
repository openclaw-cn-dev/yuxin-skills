# 踩坑速查(给 hermes-feishu-gateway 主页用)

本文件收录 SKILL.md 因路径白名单无法直接 patch、但确实从踩坑里总结出来的小型经验。每条独立、可直接搬到 SKILL.md 常见坑表里。

---

## `HERMES_PROFILE` 环境变量对 `hermes chat` 不生效(2026-06-15)

**症状**:

```bash
$ HERMES_PROFILE=xiaobao hermes chat -q "你是谁"
# 回话:"我是 Hermes Agent, 跑在 boss-control profile 下"
# 期望:"我是小宝,盯盘助手..."
```

**根因**:`HERMES_PROFILE` 环境变量**只在 hermes 全局命令里被读**(像 `hermes gateway list` / `hermes gateway status` 这些对 profile 敏感的元数据查询)。`hermes chat` / `hermes gateway run` 走的是**当前 active profile**(由 `hermes profile use X` 切换后写入 `~/.hermes/state.db`)。**两者不互通**。

**正确做法**:显式用 `--profile` flag——`--profile` 是**主命令的 flag**,**不是子命令的**:

```bash
hermes --profile xiaobao chat -q "..."
hermes --profile xiaobao gateway run
```

`hermes chat --profile xiaobao` **错**(把 flag 给了子命令 chat,hermes 解析不到);`hermes --profile xiaobao chat` **对**。

**查当前 active profile**:

```bash
hermes config show | head -3
# 第一行 Profile: <active_name>
# 或
hermes profile list
# 标记 ◆ 的就是 active
```

**调试 SOUL.md 人设的 3 步法**:

1. `cat ~/.hermes/profiles/<期望名>/SOUL.md` 确认有改
2. `hermes --profile <期望名> chat -q "你是谁"`
3. 回话风格对得上 SOUL.md 才是通的

**不预防的代价**(2026-06-15 小宝 profile):改了 SOUL.md → chat 验 → 看到 boss-control 风格的人设 → 怀疑 SOUL 没加载 → 改 SOUL 几遍 → 才发现是 flag 写错位置,白白浪费 5 分钟。

---

## 飞书 send_message 报 `230002 Bot/User can NOT be out of the chat`(2026-06-15)

**症状**:`send_message` 推指定 chat_id,飞书 API 返 `code=230002`。

**根因**:这个 App 的 bot **没在那个 chat_id 的群里**。飞书 OpenAPI 限制:bot 只能向**自己加过的群/会话**发消息。

**修法**:
1. 飞书侧 → 群设置 → 机器人 → 添加 `盯盘助手`(或对应 bot 名)
2. 或**建个新群专门给这个 bot** → 拿到新 chat_id → send_message 用新 chat_id

**快速验证 bot 加过哪些群**:

```python
# 不需要 hermes,直接走飞书 OpenAPI
import requests
token = requests.post(
    'https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal',
    json={'app_id': APP_ID, 'app_secret': APP_SECRET}
).json()['tenant_access_token']
r = requests.get(
    'https://open.feishu.cn/open-apis/im/v1/chats',
    headers={'Authorization': f'Bearer {token}'},
    params={'page_size': 50}
).json()
for c in r['data']['items']:
    print(f"{c['name']}: {c['chat_id']}")
```

**单用形态(沉默打工人)场景特别提醒**:如果走 `send_message` 主动推送,目标 chat_id **必须**提前把 bot 加进去,不然永远 230002。这跟"bot 自动收消息"是两套权限——`FEISHU_ALLOW_ALL_USERS=true` 只能让 bot **回**消息,**不能让 bot 主动**发。

---

## `hermes gateway stop`(不带 profile)会杀掉 active profile 的 gateway(2026-06-15)

**症状**:跑 `hermes gateway stop`(本意清僵尸)→ 顺手把 active profile(default)的 gateway 也干掉了。

**根因**:`gateway stop` 走的是**当前 active profile** 的 `gateway stop -p <active>`,不是字面意义的"全停"。

**安全停法**:

```bash
# 1. 先看 list,记下要保留的 PID
hermes gateway list

# 2. 想停指定的某个 profile(不只 active)
hermes gateway stop -p xiaobao

# 3. 想全停(字面意义的全停)
hermes gateway stop --all
# ⚠️ 注意 --all 是字面"全部",**包括正在健康跑的其他 profile**
```

**重新拉起来**:

```bash
# 后台长跑(hermes 的 background=true 模式,不是 nohup &)
hermes gateway run -p xiaobao   # 在 terminal(background=true) 里
# 或前台
hermes gateway run -p xiaobao
```

---

## chat 模式 `background=true` 启动的 gateway 在 list 里看不到(2026-06-15)

**症状**:`hermes gateway list` 显示 "xiaobao not running",但 `ps -ef | grep gateway` 看到进程在跑,wss 也在连飞书。

**根因**:`hermes gateway list` 跟踪的是**PID 锁文件**(hermes 启动 `gateway run` 时写入 `~/.hermes/profiles/X/gateway.pid` 之类的锁),用 `terminal(background=true)` 启动不会写这个锁——它走的是 hermes 的进程管理机制,不是 hermes gateway 子命令自带的 PID 锁。

**验证 gateway 真活着**:

```bash
# 看 wss 连线
grep -iE "feishu.*connect" ~/.hermes/profiles/xiaobao/logs/gateway.log | tail -3

# 看 hermes 进程
ps -ef | grep "gateway run" | grep -v grep

# 看 wss 流量(连飞书前缘服务)
netstat -an | grep msg-frontier.feishu.cn
```

**这个不影响功能**——wss 真的在连,真能收消息,只是 list 命令的索引机制覆盖不到 hermes background=true 启动的实例。**老大别再误以为 "list 显示 not running = gateway 挂了"**。

---

## 应用:沉默打工人(单用形态)模式完整配置(2026-06-15)

针对"小弟不接群、只接 CLI 触发 + 主动 send_message 推送"的场景(典型:小宝盯盘助手、调研员、定时跑任务不接单的 worker):

**SOUL.md 必须明确写**:

```markdown
## 运行模式:沉默打工人(单用形态)
- **不接单**:不进入任何飞书群,不主动响应飞书侧消息
- **触发方式**:仅接受主动命令 — `hermes --profile X chat -q "..."` / cron 定时 / 后台 gateway run
- **输出方式**:
  - 报告/CSV → 桌面固定目录(落档)
  - 飞书 → `send_message(target="feishu:<具体 chat_id>", message=...)` 显式推
  - **不依赖 home_channel 配置**(避免 schema 坑)
```

**.env 飞书段**(`hermes gateway list` 跑时生效):

```bash
# 不接单但还要能 send_message 推送 → 留 ALLOWED_USERS 指向目标 chat,不走 open
FEISHU_APP_ID=cli_xxx
FEISHU_APP_SECRET=***
FEISHU_ALLOWED_USERS=<目标 chat_id 1>,<目标 chat_id 2>   # 显式列
FEISHU_GROUP_POLICY=allowlist                              # 配合 ALLOWED_USERS
FEISHU_DOMAIN=feishu
FEISHU_CONNECTION_MODE=websocket
```

**send_message 调用范式**:

```python
send_message(
    target="feishu:oc_529aff7485ccc35de97a9e7233d665dd",  # 显式指定,不依赖 home_channel
    message="🎯 报告: <标题>\n\n<摘要>...",
    # 不要带 topic / thread 参数
)
```

**典型 workflow**:

```
华哥说"跑一下" → hermes --profile xiaobao chat -q "跑全 A 涨停扫描"
  → 小宝起 python(akshare) → 扫 → 落 CSV 到桌面
  → send_message 推精简版到主控群
  → 报告(在 chat 回复 + CSV 文件)
```

**vs 接单模式差别**:
- 接单模式:必须 `FEISHU_ALLOW_ALL_USERS=true` + `FEISHU_GROUP_POLICY=open` + bot 加到目标群 + 飞书侧人工发消息触发
- 沉默打工人:`FEISHU_ALLOWED_USERS=<具体 chat>` + `FEISHU_GROUP_POLICY=allowlist` + bot 加到目标群(为 send_message 推送)+ **华哥 CLI 主动触发**,不接飞书侧消息
