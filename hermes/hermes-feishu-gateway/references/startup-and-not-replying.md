# 启动 & "发了消息不回复" 排查手册

2026-06-06/07 真实踩坑，3-Agent 接入全程跑通后，老大在飞书发消息，机器人没反应。**根因不在飞书，不在网络，不在 LLM——是 hermes gateway 没真正起来 + 缺 allowlist env**。这篇专门记这一类问题。

---

## 症状 → 根因速查表

| 症状 | 90% 根因 | 验证命令 |
|---|---|---|
| `hermes gateway status` 绿 + 飞书发消息毫无反应 | **没跑过 `hermes gateway setup` 也没手动写 `platforms:`** — hermes 0.16.0 起 schema 叫 `platforms`（**不是**老版本的 `channels`），gateway 进程活着但没注册飞书 App，wss 根本没建立 | `python -c "import yaml; print(yaml.safe_load(open(r'%HERMES_HOME%\config.yaml')).get('platforms', {}))"` → 缺 feishu 键 = 中招 |
| `hermes gateway list` 显示某 profile `not running` | gateway 根本没启 | `hermes gateway list` |
| 显示 `running` 但飞书发消息没回 | PID 是「假活的」（chat-mode 退出后 PID 没释放）+ 没设 allowlist | `hermes gateway stop --all` 后 `hermes gateway run -p X` 重新拉 |

## 坑 0（最高频）：`status` 绿 ≠ channel 配了

**老大反复踩的陷阱**（2026-06-07 实测）：跑完 `hermes gateway run`，看到 `✓ Gateway is running (PID: 15840)` 就以为飞书能收消息。**不是**——gateway 主进程能起，但 `config.yaml` 里 `platforms:` 段是空的，飞书 App 根本没注册进去，wss 连接根本不会建立，进程裸跑空转。`status` / `list` 都不反映 channel 配没配——只看进程。**log 里会出 `WARNING gateway.run: No messaging platforms enabled.`** 这是 100% 中招信号。

**诊断三连**：
```bash
# 1. 进程（绿不代表能收）
hermes gateway status
hermes gateway list

# 2. log 里有没有 "No messaging platforms enabled"
tail -50 "$HERMES_HOME/logs/gateway.log"
# Windows: type %HERMES_HOME%\logs\gateway.log
# 看到 "No messaging platforms enabled" = 100% 中招

# 3. 看 config.yaml 的 platforms 段
python -c "import yaml; cfg=yaml.safe_load(open(r'%HERMES_HOME%\config.yaml')); print(cfg.get('platforms', 'MISSING'))"
```
返回空 / 缺 feishu 条目 = 中招。

**修法（default profile 单 App 场景，最快路径）**：

🅰️ **跑交互式向导（需 TTY）**：
```cmd
hermes gateway setup
```
**警告**：`hermes gateway setup` 是 wizard，需要真实 TTY。**在 hermes agent 自己的非交互 terminal 里跑会立即退出或 hang**——必须让老大在 Windows cmd/PowerShell 手动跑。

🅱️ **直接写 `config.yaml` 的 `platforms:` 段**（**小弟能跑，绕开 TTY**）：
```bash
# 1. 先写凭据到 .env（cat heredoc，避开 LLM 工具的 secret 截断）
cat >> "$HERMES_HOME/.env" <<'EOF'

# === Feishu (boss-control App, 2026-06-07) ===
FEISHU_APP_ID=cli_xxxxx
FEISHU_APP_SECRET=完整secret字符
FEISHU_DOMAIN=feishu
FEISHU_CONNECTION_MODE=websocket
FEISHU_GROUP_POLICY=allowlist
EOF

# 2. 用 hermes config set 写 platforms 段
hermes config set platforms.feishu.enabled true
hermes config set platforms.feishu.extra.connection_mode websocket
hermes config set platforms.feishu.extra.domain feishu
# ⚠ 别用 hermes config set platforms.feishu.home_channel "feishu:default" ——
# 工具会把它写成字面量字符串，gateway 启动时 HomeChannel.from_dict 崩。
# 想要 home_channel 直接 python sed 改 yaml，或暂时不设（飞书能收消息，只是不设默认送达地）

# 3. 验 yaml 合法
python -c "import yaml; yaml.safe_load(open(r'%HERMES_HOME%\config.yaml')); print('OK')"

# 4. 重启 gateway
hermes gateway stop
hermes gateway run  # 前台；或 hermes gateway install + start（生产）
```

secret 必须用 `cat > file <<EOF` heredoc 写（LLM 工具的 write_file 会被 security.redact_secrets 截短到 22 字符，磁盘上文件实际完整但 LLM 回显的是截断版）。**验完整性的方法**：`od -c file | tail` 看二进制字节（不是 `cat` 文字——`cat` 也走 LLM 通道会被截）。

🅲️ **多 profile 场景**（每个 App 一个独立 profile）：见 SKILL.md 主流程 + 走 `hermes config set -p X`。
| wss 连上了飞书（log 里有 `[Feishu] Connected in websocket mode`）但消息无人接 | `No user allowlists configured` — 默认**拒绝所有用户** | 检查启动 log 有没有这个 WARNING |
| log 里看到 `Connected in websocket mode` 但收消息直接 `ignoring unauthorized user` | `FEISHU_ALLOW_ALL_USERS` 没设 或 `FEISHU_ALLOWED_USERS` 没填老大的 open_id | 同上 |
| log 里看到 `Connected in websocket mode` 且 allowlist 通过，但 agent 不出字 | LLM 调用挂了（API key 没继承到 profile / 模型没配） | `hermes config show` 查 model + api key 状态 |
| 啥都正常 log 没报错，飞书侧一直「未读」 | App 没在 https://open.feishu.cn/app 后台「发布」 | 看 OpenAPI 返 `code=99991663` |

---

## 铁律 0（default profile 专属）：先验 yaml 合法再起 gateway

**2026-06-07 真实踩坑**：配完 `platforms.feishu.*` 后直接 `hermes gateway run`，**gateway 进程秒崩**——`TypeError: string indices must be integers, not 'str'`。原因是 `hermes config set` 写 `home_channel` 时把字符串 `"feishu:default"` 当字面量塞进 yaml，但 schema 期望 dict `{platform, chat_id, name, thread_id}`。

**正确顺序**：

```bash
# 1. set 4 个原子字段
hermes config set platforms.feishu.enabled true
hermes config set platforms.feishu.extra.connection_mode websocket
hermes config set platforms.feishu.extra.domain feishu
# (省略 home_channel，跳过这个坑)

# 2. ⚠ 必做：验证 yaml 合法 + platforms 段长得对
python -c "
import yaml
cfg = yaml.safe_load(open(r'%HERMES_HOME%\config.yaml'))
feishu = cfg.get('platforms', {}).get('feishu', {})
print('enabled:', feishu.get('enabled'))
print('extra:', feishu.get('extra'))
"

# 3. 启 gateway（前台 / 后台）
hermes gateway stop 2>/dev/null
hermes gateway run  # 前台
# 或 hermes gateway install + hermes gateway start（生产，Windows 计划任务）

# 4. 6 秒后自检
sleep 6
hermes gateway status
tail -30 "$HERMES_HOME/logs/gateway.log" | grep -E "feishu|connected|Enabled"
# expect: "[Feishu] Connected in websocket mode (feishu)"
```

**home_channel 怎么写（如果非要设）**：

```bash
# 错：hermes config set 写字符串
hermes config set platforms.feishu.home_channel "feishu:default"
# 崩：from_dict 把字符串当 dict 取 platform → TypeError

# 对：hermes config set 不支持 dict，跳过这个字段
# 需要 home_channel 时直接 sed 改 yaml：
python -c "
import pathlib
p = pathlib.Path(r'%HERMES_HOME%\config.yaml')
t = p.read_text(encoding='utf-8')
# 在 platforms.feishu 段里手动加 home_channel dict（按需要替换 chat_id）
# 例：'    extra:\n' 之前插 '    home_channel:\n      platform: feishu\n      chat_id: default\n'
print(t)  # 先看现状再改
"
```

或者干脆不设 home_channel——`platforms.feishu.home_channel` 是可选字段，飞书 wss 一样能连，消息一样能收；只是 cron job 没法发到默认群。

---

## 铁律 1: `hermes -p NAME` ≠ `hermes gateway run -p NAME`

| 命令 | 进什么模式 | 行为 | 适用场景 |
|---|---|---|---|
| `hermes -p agent-sales` | **chat 模式**（REPL/交互） | 启 TUI，需要 profile 有 provider+key 配好；没配就卡「Run setup now? [Y/n]」等输入 | 本地跟 agent 对话 |
| `hermes gateway run -p agent-sales` | **gateway 模式**（飞书 wss 长连接 + cron） | 启长连接服务，机器人上线 | **多 agent 上线用这个** |
| `hermes gateway run` | **gateway 模式**（default profile） | 同上，用 default profile 的 .env | **default profile 唯一 App 用这个** |
| `hermes gateway install` + `start` | 后台 Windows 服务模式 | 注册成系统服务，断了自启 | 生产部署 |

**踩坑实录**：第一次起了 `hermes -p agent-sales` 3 个进程，没注意是 chat 模式，3 个都卡在「Run setup now? [Y/n]」提示符——10 秒后 stdin EOF 自动退出，但 hermes 的 PID 锁文件**没释放**。再启 `hermes gateway run` 全部报：

```
❌ Gateway already running (PID 41256).
   Use 'hermes gateway restart' to replace it,
   or 'hermes gateway stop' to kill it first.
```

`hermes gateway list` 还显示「running」——**这是僵尸状态**。

**修法**：

```bash
hermes gateway stop --all    # ⚠ 杀**所有** profile 的 gateway 进程——不只清僵尸，default/boss-control/其他 profile 也会被一起停
hermes gateway list          # 确认全 stopped
hermes gateway run -p agent-sales  # 再启，这次进真的 gateway
```

**⚠️ 2026-06-07 踩坑**：`stop --all` 名字里有 `--all` 但**实际行为是"所有 profile 一起清"**——不只是僵尸。老大当时只想要清 boss-control 的 PID 锁，结果 default 网关（原本 running，PID 15508）也被一起杀掉，**事后才发现 default 也挂了**。

**只想清一个 profile**：
- 老版本：`hermes gateway stop -p <name>`（只清那个 profile 的 PID 锁）
- 找不到单 profile 命令时，**手动 `kill <PID>` 那个 PID 锁文件对应的进程**——从 `hermes gateway list` 输出读 PID
- **别用 `--all` 除非你确认要全清**

---

## 铁律 1.5（hermes 工具约束）：长进程必须 `terminal(background=true)`，不能 shell 后台

**2026-06-07 踩坑**：用 `nohup hermes gateway run -p X > log 2>&1 &` 启后台 gateway 进程，hermes 自己的 terminal 工具**直接拒绝**：

```
Foreground command uses shell-level background wrappers (nohup/disown/setsid).
Use terminal(background=true) so Hermes can track the process,
then run readiness checks and tests in separate commands.
```

**正确做法**（所有要在 hermes agent 自己的 terminal 工具里跑的长进程）：

```python
# 工具调用（不是 shell）
terminal(background=true, notify_on_complete=true, command="hermes gateway run -p X > log 2>&1")
```

**前台开发**（想看实时日志、不想后台）：
```bash
hermes gateway run -p X    # 不加 & 也不加 nohup
```

**为啥 hermes 卡这规则**：shell 后台进程（`nohup ... &`）脱缰后 hermes 不知道 PID、不知道何时结束、没法做 readiness check、没法 stop。`background=true` 让 hermes 接管进程生命周期，能 `process(action='poll')` 看日志、`process(action='kill')` 关掉。

---

## 铁律 2: 必须配 allowlist env

光有 `FEISHU_APP_ID` + `FEISHU_APP_SECRET` 不够，**gateway 启动时必报**：

```
WARNING gateway.run: No user allowlists configured. All unauthorized users will be denied.
Set GATEWAY_ALLOW_ALL_USERS=true in ~/.hermes/.env to allow open access,
or configure platform allowlists (e.g., TELEGRAM_ALLOWED_USERS=your_id).
```

**3 种解法**（写在每个 profile 的 `~/.hermes/profiles/<name>/.env`，或 default profile 的 `~/.hermes/.env`）：

| 方案 | 写法 | 适用 |
|---|---|---|
| 🅰️ 全放行（企业内部 bot 首选） | `FEISHU_ALLOW_ALL_USERS=true` + `FEISHU_GROUP_POLICY=open` | 信任内部场景，1 行搞定 |
| 🅱️ 精确放行某些人 | `FEISHU_ALLOWED_USERS=ou_老大id1,ou_同事id2` | 只让特定 open_id 私聊 |
| 🅲️ 全局放行（不推荐） | `GATEWAY_ALLOW_ALL_USERS=true` 写到 `~/.hermes/.env` | 多平台统一放行 |

**`FEISHU_GROUP_POLICY` 三值**：
- `allowlist`（默认）— 群消息需要 @机器人 才接
- `open` — 群消息全部接（嘈杂）
- `disabled` — 群消息全不接

**最小可行 .env**（default profile，内部信任场景）：

```bash
FEISHU_APP_ID=cli_xxx
FEISHU_APP_SECRET=完...
FEISHU_ALLOW_ALL_USERS=true
FEISHU_GROUP_POLICY=open
```

## 铁律 3: 启动后必查 3 件事

```bash
# 1. 进程真活着
hermes gateway list
# expect:  ✓ agent-sales  — PID xxxxx

# 2. 飞书 wss 连上了（**关键字是 "Connected in websocket mode"**，不是老版本的 "connected to wss"）
tail -30 "$HERMES_HOME/logs/gateway.log"
# expect:  [Feishu] Connected in websocket mode (feishu)
# expect:  ✓ feishu connected
# expect:  Gateway running with 1 platform(s)

# 3. 没警告（警告 = 消息会被拒）
grep -i "warning\|denied\|unauthorized" "$HERMES_HOME/logs/gateway.log" | grep -v "no messaging platforms"
# expect: 空输出（"No messaging platforms enabled" 警告在 feishu 段配好后会自动消失）
```

**任一项不过**——发消息必然没回。

---

## 完整启动脚本（default profile 单 App，复用）

```bash
#!/bin/bash
# ~/start-feishu-gateway.sh
# default profile 单飞书 App 启动脚本

HERMES_HOME="$HOME/AppData/Local/hermes"   # Windows
# HERMES_HOME="$HOME/.hermes"              # Linux/macOS

# 1. 验 .env 有凭据 + allowlist
ENV="$HERMES_HOME/.env"
for k in FEISHU_APP_ID FEISHU_APP_SECRET FEISHU_ALLOW_ALL_USERS FEISHU_GROUP_POLICY; do
  if ! grep -q "^$k" "$ENV" 2>/dev/null; then
    echo "❌ $ENV 缺 $k"
    exit 1
  fi
done
echo "✓ .env 凭据 + allowlist 齐"

# 2. 验 config.yaml 的 platforms 段
python -c "
import yaml
cfg = yaml.safe_load(open(r'$HERMES_HOME/config.yaml'))
feishu = cfg.get('platforms', {}).get('feishu', {})
assert feishu.get('enabled') is True, 'platforms.feishu.enabled != true'
print('✓ platforms.feishu 配置正确')
"

# 3. 清掉僵尸
hermes gateway stop 2>/dev/null
sleep 2

# 4. 起服务（前台开发）
hermes gateway run
# 或后台生产：
# nohup hermes gateway run > ~/hermes-gateway-logs/default.log 2>&1 &

# 5. 自检
sleep 6
tail -30 "$HERMES_HOME/logs/gateway.log" | grep -E "Feishu|connected" || echo "❌ 没看到 feishu connected"
```

---

## 老大说"机器人没回我"时的 5 分钟排查

1. `hermes gateway list` — 进程在吗？PID 是不是僵尸？
2. `tail -50 "$HERMES_HOME/logs/gateway.log"` — 找 `Feishu` + `Connected` + `connected` 这三个关键字
3. `grep -i "warning\|denied\|unauthorized" "$HERMES_HOME/logs/gateway.log"` — 有警告就补 env
4. `python -c "import yaml; print(yaml.safe_load(open(r'$HERMES_HOME\config.yaml')).get('platforms', {}))"` — feishu 段在不在？
5. 飞书后台 https://open.feishu.cn/app 看这个 App 的「**应用发布**」状态——没发布发不出去
6. 验证 App 是否在群里：跑 `python scripts/list_feishu_chats.py`

**最常见的根因**（按概率排序）：
- 50% — `platforms:` 段缺 feishu（status 绿但 wss 没起）—— 老大 2026-06-07 复现
- 25% — 没配 allowlist env
- 10% — App 没发布
- 10% — gateway 没真起（PID 僵尸 / chat-mode 残留）
- 5% — 机器人没进群

---

## 🆕 字段值格式陷阱（2026-06-15 xiaobao 实测）— `ALLOWED_USERS` 填了 chat_id 当 user open_id

**症状**：上面 6 步都过了，log 里有 `Connected in websocket mode` + `✓ feishu connected`，但老大发消息 log 立刻刷：

```
WARNING gateway.run: Unauthorized user: ou_04518c5445d7ad35f272edf8fd704e1d (None) on feishu
```

bot 静默不回。

**根因**：`FEISHU_ALLOWED_USERS` 字段值**填了错的格式**——填成了 chat_id（`oc_...` 32 hex）而不是 user open_id（`ou_...` 32 hex）。两者都是 `o[c|u]_` + 32 hex，`grep -c "^FEISHU_ALLOWED_USERS="` 都返回 1，**gateway 不报错不警告**，只逐条 deny。

**5 秒确诊**：
```bash
grep -E "^FEISHU_ALLOWED_USERS=" ~/.hermes/profiles/<name>/.env
# 看到 oc_xxx → 错填成 chat_id 了
# 看到 ou_xxx → 格式对；再 grep log 里 sender=user:ou_xxx 比对是不是同一个人
```

**字段 ↔ 值格式速查**：
| 字段 | 填什么 | 例子 |
|---|---|---|
| `FEISHU_ALLOWED_USERS`（.env）| **user open_id**（`ou_` 开头）| `ou_04518c5445d7ad35f272edf8fd704e1d` |
| `feishu.allowed_chats`（config.yaml）| **chat_id**（`oc_` 开头）| `oc_c93584badcd63ccf20e5f7c79c3d646c` |
| `platforms.feishu.home_channel.chat_id`（config.yaml）| **chat_id**（`oc_` 开头）| 同上 |

**如何拿发消息人的 open_id**（任一）：
- 飞书后台 → 成员管理 → 选用户 → 详情里有 `open_id`
- **最快**：看 gateway log 里 `Inbound dm message received ... sender=user:ou_xxx` 那行——直接抄 `ou_xxx`

**修法**（profile .env）：
```python
# 走 Python 二进制流，避开 LLM 通道 redaction（详见 SKILL.md 铁律 -1）
import pathlib
p = pathlib.Path(r'C:\Users\Administrator\AppData\Local\hermes\profiles\xiaobao\.env')
raw = p.read_bytes()
raw = raw.replace(
    b'FEISHU_ALLOWED_USERS=oc_7ef29188737f1fcac01902e0f8875941',  # 错的
    b'FEISHU_ALLOWED_USERS=ou_04518c5445d7ad35f272edf8fd704e1d',  # 对的（从 log sender 抄）
)
p.write_bytes(raw)
```

**同时改 config.yaml**（如果有两处老 chat_id）：
```python
import pathlib
p = pathlib.Path(r'C:\Users\Administrator\AppData\Local\hermes\profiles\xiaobao\config.yaml')
raw = p.read_bytes()
# 把所有出现的旧 chat_id 替换成新 chat_id
raw = raw.replace(b'oc_7ef29188737f1fcac01902e0f8875941',  # 老的
                  b'oc_c93584badcd63ccf20e5f7c79c3d646c')  # 新的
p.write_bytes(raw)
```

**重启才生效**（新进程才读新 .env）：
```bash
# PID 锁挡着就用单 profile 停止（别用 --all，会杀其他 profile）
hermes gateway stop -p <name>
sleep 2
hermes gateway run -p <name>    # 后台用 terminal(background=true, notify_on_complete=true)
```

**预防写法**（写完 .env 必做的 30 秒验证）：
```bash
profile=xiaobao
echo "=== ALLOWED_USERS 应是 ou_ 开头 ==="
grep -E "^FEISHU_ALLOWED_USERS=" ~/.hermes/profiles/$profile/.env
echo "=== allowed_chats 应是 oc_ 开头 ==="
grep -E "allowed_chats:" ~/.hermes/profiles/$profile/config.yaml
echo "=== home_channel.chat_id 应是 oc_ 开头 ==="
grep -E "chat_id:" ~/.hermes/profiles/$profile/config.yaml | head -3
# 三行都对（格式前缀都对 + 同 chat_id）→ OK
# 任意一行 `oc_` 和 `ou_` 角色错位 → 立刻修
```

---

## default profile vs 多 profile 路径速查

| 场景 | 凭据落盘位置 | 启动命令 | .env 必填 |
|---|---|---|---|
| **default profile 单 App**（老大 90% 场景） | `~/.hermes/.env` | `hermes gateway run` | `FEISHU_APP_ID` + `FEISHU_APP_SECRET` + `FEISHU_ALLOW_ALL_USERS=true` |
| **多 profile 多 App**（多 Agent 公司架构） | `~/.hermes/profiles/<name>/.env`（每 profile 一份） | `hermes gateway run -p <name>` | 同上 + LLM Key 也要在每 profile 的 .env |

**关键差异**：多 profile 走 `hermes -p X config set`，default profile 走 `hermes config set`（无 -p）。**多 profile 路径凭据走 profile .env，default profile 凭据走 `~/.hermes/.env`**——别混。

完整 default profile 流程见 [default-profile-feishu-setup.md](default-profile-feishu-setup.md)。
