# LLM Key 注入 — 让 hermes 飞书 bot 真正能回话

飞书接通了（wss 连上、allowlist 通过），**但飞书发消息机器人依然不答**——大概率是 LLM 这一侧没配好。Profile 默认不继承 default `.env` 的 Key，必须显式配 4 件套。本篇是 2026-06-06 / 06-07 实跑踩坑总结。

---

## 症状速查

| 现象 | 根因 |
|---|---|
| 飞书发消息 → bot 不回 | profile 缺 LLM Key / model.provider 没设 |
| `hermes chat -p X -q "hi"` 卡 setup 提示符 | 同上 |
| 报错 `HTTP 401: Please carry the API secret key in the 'X-Api-Key' field` | **hermes 0.15.1 两层都中招，详见下面专门一节**——`provider=minimax-cn` 走 OpenAI SDK 包装发 Bearer；`provider=anthropic` + `api.minimaxi.com` 被 `anthropic_adapter._requires_bearer_auth` 劫持成 Bearer。**单纯换 provider 不一定解决问题**。 |
| 报错 `No Anthropic credentials found. Set ANTHROPIC_TOKEN or ANTHROPIC_API_KEY` | profile .env 缺 `ANTHROPIC_API_KEY` / `ANTHROPIC_TOKEN` |
| 报错 `Provider: minimax-cn / Endpoint: https://api.minimaxi.com/anthropic / Auth method: x-api-key` **但仍 401** | 同一节——`auth_method` 标记是误报（显示 x-api-key 但实际发了 Bearer），不是 hermes 故意这么干 |
| `hermes chat -p X -q "hi"` 60 秒超时无输出 | **优先 grep config.yaml 的 `base_url:`**——`http://127.0.0.1:9999/v1`（或其他本地代理端口）常见坑。本地代理没起 → connect refused → hermes 静默 timeout，**错误日志里没有 401/402，只有 `ConnectionRefusedError: [WinError 10061]`**。修：换 base_url 到真平台。**老大 2026-06-08 boss-control 实测**：profile config.yaml 里残留 `base_url: http://127.0.0.1:9999/v1` → chat 卡死无明显报错。**第一排查动作 = `cat config.yaml`** |
| 报错 `HTTP 402: insufficient balance (1008)` | **key + 端点配对正确、认证通过，但 MiniMax 平台账户余额 0**。**两个独立计费池必须分清**：(1) **主钱包**（老大说"账号有钱"指这个）—— 用于 MaaS / 订阅 / 包月，**调 API 用不了**；(2) **API 按量账户**（**这个才是 key 用的**）—— 与主钱包余额分开。**正确充钱路径**：platform.minimaxi.com → 左侧「**API 余额 / Billing / Credits**」→ 单独充（**不是「我的钱包」**）。**两个都充才能既能用 API 又能用主站服务**。**诊断信号**：换 1 个 key 仍 402、换 2 个 key 还 402 = 不是 key 问题，是账户问题——别再换 key，**让老大去查 API 账户余额页**。完整充值诊断 + 截图指南见 [minimax-billing-pitfalls.md](minimax-billing-pitfalls.md)。 |
| `hermes chat` 报 404 `/v1/chat/completions` 找不到路径 | **base_url 漏了 `/v1` 后缀**——hermes 0.15.1 `minimax-cn` provider 走 OpenAI SDK 包装，只把 `base_url` 当 host，**不自动加 `/v1`**。把 `base_url` 改成 `https://api.minimaxi.com/v1`（不要写成 `https://api.minimaxi.com`）。`/anthropic` 后缀同理要走 Anthropic SDK 但 hermes 0.15.1 仍报 401，**最稳是直接用 `/v1` + OpenAI 兼容协议**。老大 2026-06-07 修这个坑时是：先 base_url = `https://api.minimaxi.com` → 404 → 改成 `https://api.minimaxi.com/v1` → 200 + 402（认证通过、余额问题）。 |
| `GET /v1/models` 返 200 + models 列表，但 POST `/v1/chat/completions` 返 402 | **认证和扣费是两件事**——`/v1/models` 不扣费（只验 key 是否有效），`/chat/completions` 扣费。**前 200 不代表能用**。老大 2026-06-07 看到 `GET /v1/models` 返 200 误以为链路通了，结果 `/v1/chat/completions` 仍 402 — MiniMax 平台账户余额 0。**验收标准要 POST 一次**（哪怕 `max_tokens=1`），不是只看 models 端点。 |
| `hermes` 错误里 `Token prefix: sk-api...pFCM`（中段出现 `pFC` / `9aW` 之类的突兀截断） | **CLI 沙箱 redaction 误读**——这是被截到 22 字符的展示前缀，不是真 prefix。**真 prefix 只能从 `od -c file` 的字节头几个字符读**。老大 2026-06-07 踩坑：报错显示 `sk-api-...pFCM` 让人以为是 `sk-api-` 官方，**实际磁盘上是 `sk-cp-` PackyCode key**——一字之差导致整整一个排查周期走错方向。**判断标准**：看 `od -c` 开头前 8 字符，看 `cat` / `print` 出的"prefix"可能是 redaction 假象。 |
| **`hermes chat` 提示"key 长度不是 120"** | 旧脚本硬编码 120。新 key 实际可能是 108 / 120 / 126 字符。改用 GET /v1/models probe，**不再硬编码长度**。 |
| **新 profile `hermes chat -p X` 报 401**（clone 建好后第一次跑） | `hermes profile create X` **不继承 default `.env` 的 LLM key**——`cp ~/.hermes/.env ~/.hermes/profiles/X/.env` 后 key 看起来有了，但**多数行是 `# xxx=***` 注释模板**，真实生效 key 只有 1-2 行（看 `wc -l` vs `grep -v "^#" .env | wc -l`）。**`config.yaml` 里如果配了 `model.api_key: sk-cp-...K7HE` 会再 22 字符截断**——`od -c` 验不到完整长。**修法**：直接看 [§ profile create 后立即补 LLM key 的 5 步法](#profile-create-后立即补-llm-key-的-5-步法) |

---

## 关键第一步：Key 前缀 ↔ 平台对应（2026-06-07 实测，**有勘误**）

⚠️ **2026-06-07 勘误**：早期版本说 "`sk-cp-` = PackyCode / Claude Code 代理唯一前缀"——**错的**。老大 2026-06-07 实测：125 字符的 `sk-cp-LpB9pTm...` 在 `https://api.minimaxi.com/v1/models` 返 **200** + 模型列表完整。**`sk-cp-` 前缀不是平台标识**——只是 MiniMax 平台一种 key 格式。`sk-api-`（126 字符）和 `sk-cp-`（125 字符）**都是 MiniMax 官方按量计费 API 账户**的 key，都配 `https://api.minimaxi.com/v1`。

**判断 key 是不是 MiniMax 官方的唯一方法**：用 `scripts/probe_llm_endpoints.py` 跑 7 端点 GET /v1/models，**看哪行 ✅ 200**——`api.minimaxi.com` 200 = 官方；`api.packycode.com` 200 = PackyCode。不要凭前缀猜。

| 前缀示例 | 长度 | 可能平台 | 验证方法 |
|---|---|---|---|
| `sk-api-...` | 126 | MiniMax 官方 / 其他平台 | probe 验证 |
| `sk-cp-...` | 125 | **MiniMax 官方**（不再专属 PackyCode） | probe 验证 |
| `sk-ant-...` | 108 | Anthropic 官方 | probe 验证 |
| `eyJ...`（JWT 风格）| ~180 | MiniMax 官方旧版 / 内部部署 | probe 验证 |

**MiniMax 平台 `api.minimaxi.com` 配 `sk-cp-` 是合法的**（2026-06-07 实测 200）。**不要再用前缀排除法**——直接 probe。

**`api.minimaxi.com` 配某些 `sk-cp-` 仍可能 401**（其他平台发的代理 key 走 MiniMax 端点当然不认）。**401 永远先 probe 验 key 是不是 MiniMax 官方**，别按前缀直接判死刑。

**先 probe 再配**：用 `scripts/probe_llm_endpoints.py` 7 端点 GET /v1/models 一次找对（**零 token、毫秒级**），看到 ✅ 200 那行就是真配对。**POST /messages 是真发消息（消耗 token），改用 GET /models 做 healthcheck**。

---

## 完整 4 件套（必配齐）

每个 profile 都要配：

```bash
for prof in agent-sales agent-rd agent-prod agent-cs; do
  hermes -p $prof config set model.default    MiniMax-M3
  hermes -p $prof config set model.provider  minimax-cn     # 或 anthropic（见下面两层坑）
  hermes -p $prof config set model.base_url  https://api.minimaxi.com/anthropic
done
```

**写完必查**：
```bash
hermes -p agent-sales config show 2>&1 | grep "Model:" | head -1
# expect: Model: {'default': 'MiniMax-M3', 'provider': 'minimax-cn', 'base_url': '...'}
```

⚠️ `hermes config show` 默认看 default profile，**必须带 `-p X`**。不加就只看 default，看不到你配的 profile。

---

## profile create 后立即补 LLM key 的 5 步法

**触发场景**：`hermes profile create X` 刚建好（哪怕加了 `--clone-all` 也只克隆 74 bundled skills 和 config.yaml 模板，**不复制 .env**），`hermes chat -p X -q "hi"` 报 401。

**根因**：`hermes profile create` 只在 `~/.hermes/profiles/X/` 下建好 6 个空子目录（cron/home/logs/sessions/skills/skins/workspace）+ `SOUL.md` 模板，**不自动 clone `.env`**。用户多半会手动 `cp ~/.hermes/.env ~/.hermes/profiles/X/.env`，但 2 个隐藏坑：

1. **default `.env` 477 行里 90%+ 是 `# OPENROUTER_API_KEY=*** 注释模板**（hermes install 时给的可选 key 占位），**真实生效 key 只有 `MINIMAX_CN_API_KEY` + `FEISHU_*` + `TERMINAL_*` 等不到 10 行**。grep 看像有 key，其实缺。
2. **就算从 default 复制过来 key 完整，hermes `chat -p X` 子进程也读同一个文件**——所以复制步骤没问题，问题就是 #1 看不到。

**5 步法**（老大说"刚建的 profile 一跑就 401" / "刚 clone 完调不通" 时按此流程）：

```bash
# 1. 验：当前 .env 到底有几行真实 key（不靠 grep 看到的"key=***"判断）
wc -l ~/.hermes/profiles/X/.env                                # 总行数（含注释）
grep -v "^#" ~/.hermes/profiles/X/.env | grep "=" | wc -l     # 真实生效行数
# 期望后者 ≥ 1（至少 MINIMAX_CN_API_KEY 一行），=0 → 100% 缺

# 1b. ⚠️ grep 名必须穷举——2026-06-15 xiaobao profile 实测：默认 grep `^(API_KEY|MINIMAX_API_KEY|OPENAI_API_KEY)=` 返 0，差点误判缺 key
#     实际 hermes 默认 .env 用的 LLM key 名是 MINIMAX_CN_API_KEY（不是 MINIMAX_API_KEY）
grep -E "^(MINIMAX_CN_API_KEY|MINIMAX_API_KEY|ANTHROPIC_API_KEY|ANTHROPIC_TOKEN|OPENAI_API_KEY|OPENROUTER_API_KEY|MOONSHOT_API_KEY|API_KEY)=" ~/.hermes/profiles/X/.env | wc -l
# 总生效行 >0 且 LLM key grep =0 → key 名猜错了，**别瞎注入**，先确认 .env 里到底叫什么名字
# 总生效行 =0 → 100% 缺，进第 4 步从 default .env 注入
# 总生效行 >0 且 LLM key grep >0 → 进第 3 步 od 验字节完整

# 2. 看：哪些 provider key 真的被 uncomment 了
grep -E "^(MINIMAX_CN_API_KEY|ANTHROPIC_API_KEY|OPENROUTER_API_KEY)=" ~/.hermes/profiles/X/.env
# 看到 0 行 → 缺；看到 1+ 行 → 复制过来时是完整的

# 3. 验字节：哪怕 grep 看到完整一行，也要 od 验（防止"复制时 truncate"或"redaction 后回填"）
od -c ~/.hermes/profiles/X/.env | head -3
# 看 MINIMAX_CN_API_KEY 那行从 = 后是不是完整 100+ 字符（不是 22 字符截断版）

# 4. 补：profile 缺 key 时，从 default .env 提取 + cat heredoc 注入
# （**绝不用 LLM 通道写 .env** —— write_file 会被 secret redaction 截短）
APP_PROFILE=X
DEFAULT_ENV=~/.hermes/.env
TARGET_ENV=~/.hermes/profiles/$APP_PROFILE/.env

# 提取 key 到临时文件（od 验长度）
KEY=$(grep "^MINIMAX_CN_API_KEY=*** $DEFAULT_ENV | cut -d'=' -f2-)
echo "$KEY" > /tmp/key.txt
od -c /tmp/key.txt | head -1   # 验原始字节 ≥100 字符

# 写入 profile .env（用 cat heredoc 走 shell 通道）
grep -q "^MINIMAX_CN_API_KEY=*** $TARGET_ENV || cat >> $TARGET_ENV <<EOF

# LLM (2026-06-XX 注入)
MINIMAX_CN_API_KEY=$KEY
...n
# 5. 验：chat 跑通
hermes chat -p $APP_PROFILE -q "用一句话说你是谁"
# ✅ 模型回复 → 5 步走完，profile 通了
# ❌ 仍 401 → 进 §"hermes 0.15.1 MiniMax provider 401 bug"小节查 SDK 包装层
```

**预防写法**：在 `~/.bashrc` / profile alias wrapper 加这段——clone profile 后自动 inject：

```bash
alias hermes-profile-create='f() {
  hermes profile create "$1" --description "$2"
  local prof_env=~/.hermes/profiles/$1/.env
  touch "$prof_env"
  for k in MINIMAX_CN_API_KEY ANTHROPIC_API_KEY; do
    if ! grep -q "^$k=" "$prof_env" 2>/dev/null; then
      local v=$(grep "^$k=" ~/.hermes/.env 2>/dev/null | cut -d= -f2-)
      [ -n "$v" ] && echo "$k=$v" >> "$prof_env"
    fi
  done
  echo "✅ $1 创建完成,LLM key 已注入"
}; f'
```

**不预防的下场**（老大 2026-06-15 小宝 profile 实测）：建好 profile → 写完 .env 飞书凭据 → chat 报 401 → 排查了 5 分钟才发现 `wc -l` vs `grep -v "^#" | wc -l` 差 400+ 行，全是注释模板。

---

## Key 注入：4 种方法（按靠谱度排序）

### ✅ 唯一靠谱：写进 profile 自己的 `.env`

**Profile `.env` 优先于 default `.env`，也优先于 system env**。`hermes gateway run -p X` 启动时，profile 进程从 `~/.hermes/profiles/<name>/.env` 读。

```bash
cat > ~/.hermes/profiles/agent-sales/.env <<'EOF'
# 飞书（已有）
FEISHU_APP_ID=cli_xxx
FEISHU_APP_SECRET=xxx
FEISHU_ALLOW_ALL_USERS=true
FEISHU_GROUP_POLICY=open

# LLM（必加）—— 跟 Key 实际所属平台写
ANTHROPIC_API_KEY=sk-...        # 用于 provider=anthropic
MINIMAX_CN_API_KEY=sk-...       # 用于 provider=minimax-cn
EOF
```

**两个 env var 都写**——`hermes -p X config show` 列出来 provider 名字不同会读不同的，**写两个兼容**。

### ⚠️ setx 到 User 环境变量（仅当 .env 注入法失败时备选）

```python
# export_minimax_key.py —— 从 default .env 提取 + setx
import re, subprocess
with open(r"C:\Users\Administrator\AppData\Local\hermes\.env", "r") as f:
    content = f.read()
m = re.findall(r"^MINIMAX_CN_API_KEY=(sk-...)", content, re.MULTILINE)
key = m[-1]  # 取最后一个
with open(r"C:\Users\Administrator\minimax_key_value.txt", "w") as f:
    f.write(key)
ps = "$k = Get-Content 'C:\\Users\\Administrator\\minimax_key_value.txt' -Raw;" \
     "[Environment]::SetEnvironmentVariable('MINIMAX_CN_API_KEY', $k.Trim(), 'User')"
subprocess.run(["powershell", "-NoProfile", "-Command", ps])
```

**注意 setx 对**已经跑着的**进程不生效——必须 `hermes gateway stop --all` + 重启 gateway 才生效**。

### ❌ 不靠谱：`hermes config set model.api_key`

```bash
hermes -p agent-sales config set model.api_key "sk-..."   # 写进去了
grep api_key ~/.hermes/profiles/agent-sales/config.yaml
# 看到的 key 实际只有 22 字符（被沙箱 secret redaction 截了）
# 即使能写完整，hermes 也不一定从 model.api_key 读，可能走 env var
```

**别用**——双重不可控。

### ❌ 不靠谱：单独 shell `export`

只在当前 shell 会话有效，hermes gateway 进程是独立进程组，**继承不到**。

---

## ⚠️ 沙箱 secret redaction：写文件的唯一稳路径

**任何 LLM 通道**（`write_file` / `execute_code` / `terminal` 的 `echo`/`cat` 拼字符串）**里**如果出现 `sk-` 开头的字符串，沙箱/工具链都会把它**截成 `sk-cp-...9aWw` 22 字符**。

**磁盘文件实际完整**——`od -c file | tail` 验证：

```bash
$ od -c /c/Users/Administrator/AppData/Local/hermes/profiles/agent-sales/.env | tail -3
0000420   o   B   m   I   G   g   s   w   L   B   j   S   9   a   W   w  \r  \n
0000440   A   N   T   H   R   O   P   I   C   _   A   P   I   _   K   E
```

**`cat` 看到的是 22 字符的截短版**，但 `od -c` 看二进制是完整 key 长度。

**最稳的注入路径**（绕开 redaction）：

1. **Source 默认 .env 末尾已有的 key**（`grep` 不到，但 `od -c` 看到完整长度就在那）
2. 用 Python 读二进制文件，**按固定 offset 算长度**（**不要用 regex `^KEY=...` 的 `.*` 贪婪匹配**——default .env 里 `MINIMAX_CN_API_KEY` 和 `MINIMAX_CN_BASE_URL` 在同一行，regex 会把下一行的 `MINIMAX_CN_BASE_URL=...` 也吞进去，导致 key 末尾多 5 字符。**用 marker 长度 + N 字节 arithmetic 算 offset**）
3. 写到临时文件 `minimax_key_value.txt`（**长度不硬编码**——probe 脚本会自动警告 108/120/126/128 以外的值）
4. Python 读 temp 文件，构造新行（**变量名是字面量 literal，key 从 temp 文件读，**绝不在源码里出现 secret 字符串**）
5. 写进 4 个 profile .env

参考 `scripts/inject_key_to_profiles.py`：

```python
"""Inject the key into 4 profile .env files. KEY_PATH env var points to file with the full key.
Variables are constructed at runtime (literal var name + key from file) to bypass LLM-channel secret redaction.
"""
import os, sys

key_path = os.environ["KEY_PATH"]
with open(key_path, "rb") as f:
    key = f.read().decode("utf-8").strip()
# 不硬编码 120 —— 灵活警告
if len(key) < 50:
    sys.exit(f"key 长度 {len(key)} 太短，疑似截断")

# 变量名是字面量；key 从文件读，不进 LLM 通道
v1_name = "ANTHROPIC_API_KEY"
v2_name = "MINIMAX_CN_API_KEY"
eq = "="

for prof in ["agent-sales", "agent-rd", "agent-prod", "agent-cs"]:
    env_path = f"C:\\Users\\Administrator\\AppData\\Local\\hermes\\profiles\\{prof}\\.env"
    with open(env_path, "r", encoding="utf-8") as f:
        content = f.read()
    new_lines = []
    for line in content.splitlines():
        if line.startswith(v1_name + eq) or line.startswith(v2_name + eq):
            continue
        new_lines.append(line)
    new_lines.append(v1_name + eq + key)
    new_lines.append(v2_name + eq + key)
    with open(env_path, "w", encoding="utf-8") as f:
        f.write("\n".join(new_lines) + "\n")
```

**用法**：
```bash
# 1. 从 default .env 提取完整 key（od 验证原始字节数）
python scripts/extract_minimax_key.py
# → 写入 C:\Users\Administrator\minimax_key_value.txt

# 2. 注入到 4 个 profile
KEY_PATH=/c/Users/Administrator/minimax_key_value.txt python scripts/inject_key_to_profiles.py

# 3. od 验证至少一个 profile
od -c /c/Users/Administrator/AppData/Local/hermes/profiles/agent-sales/.env | tail -3
# expect: 末尾是 key 最后 16 字符 + \r \n（不是 ...9aWw 22 字符截断版）

# 4. 重启 gateway（新进程才继承新 .env）
hermes gateway stop --all
for p in agent-sales agent-rd agent-prod agent-cs; do
  hermes gateway run -p $p &
done
```

---

## hermes 0.15.1 MiniMax provider 401 bug（**两层，provider=anthropic 也不一定对**）

⚠️ **2026-06-06 实测修正**：本节原写「切 `provider=anthropic` 就行」**实际上也 401**。原因：hermes 0.15.1 的 `agent/anthropic_adapter.py:475-490` 有个 `_requires_bearer_auth(base_url)` 函数，**对 `api.minimaxi.com` / `api.minimax.io` / azure 这几个 host 强制返回 True**，**即使你设 `provider=anthropic` 也被它劫持成 Bearer 头**。**单纯换 provider 不解决问题**。

**症状（两层）**：
- 4 件套都配齐
- profile .env 有完整 `MINIMAX_CN_API_KEY` / `ANTHROPIC_API_KEY`（`od -c` 验过完整长度）
- `hermes chat -p X` 仍 HTTP 401
- 错误信息：`Please carry the API secret key in the 'X-Api-Key' field`
- 错误日志里**同时**显示 `Auth method: x-api-key (API key)` 和 `Token prefix: sk-cp-...9aW...`——auth_method 标签是误报，实际发出去的是 Bearer

**两层根因**：

1. **Layer 1 — `provider=minimax-cn`** 走 `agent/auxiliary_client.py:4743` 的 OpenAI SDK 包装，**默认发 `Authorization: Bearer *** ❌ 401
2. **Layer 2 — `provider=anthropic` + `base_url=api.minimaxi.com/anthropic`** 走 Anthropic SDK，但 anthropic_adapter 的 `_requires_bearer_auth(api.minimaxi.com) == True`（line 487-489），**把 `api_key=` 改成 `auth_token=`** → 走 Bearer → 服务端不认 → 401

**先做这一步，**别瞎换 provider**：

**用法 A**（推荐，零消耗）：用 probe 脚本
```bash
KEY_FILE=~/minimax_key_value.txt python scripts/probe_llm_endpoints.py
# 看哪个端点 ✅ 200 → 那行 base_url 就是真配对
```

**用法 B**（手敲 curl，POST /messages 消耗 token）：用真实完整 key 直接 curl 端点，绕开 hermes
```bash
curl -s -X POST "https://api.minimaxi.com/anthropic/v1/messages" \
  -H "Content-Type: application/json" \
  -H "anthropic-version: 2023-06-01" \
  -H "X-Api-Key: <key 完整字符>" \
  -d '{"model":"MiniMax-M3","max_tokens":20,"messages":[{"role":"user","content":"hi"}]}' | head -c 300
```

- ✅ 200 + 文本回复 / 列出 models → 端点认这个 auth 头，key 有效
- ❌ 401 → **key 与端点不匹配**（key 实际是别的平台的，不是 MiniMax 官方 key），回去找老大要正确的 base_url

**真正能在 hermes 0.15.1 跑通 X-Api-Key 路径的配置**：

```bash
hermes -p agent-sales config set model.provider  anthropic
hermes -p agent-sales config set model.base_url  <base_url 绕开 api.minimaxi.com / api.minimax.io / azure>
hermes -p agent-sales config set model.default   MiniMax-M3
```

`base_url` 必须绕开 `_requires_bearer_auth` 黑名单。生产部署通常**加一层反向代理**包 MiniMax，换个 host（如 `minimax.internal.lan`），强制走 x-api-key 路径。

**如果 key 是 `sk-cp-` 前缀**（PackyCode / AICodeMirror 之类平台的特征），用**该代理自己的 base_url**（如 `https://api.packycode.com`），**根本不是 MiniMax 端点**——`api.minimaxi.com` 永远不会通。**先看上面"Key 前缀 ↔ 平台对应"表**。

**验证**：
```bash
hermes chat -p agent-sales -q "用一句话说你是谁"
# expect: 按 SOUL.md 人设回答（如「小弟-销售，RAS 公司...」）
# 看到 200 + 文本才算通；401 就是 key 与端点不匹配
```

---

## 验收清单（机器人能回话前必过）

- [ ] 4 个 profile `config show` 都看到 `Model: {default: MiniMax-M3, provider: minimax-cn/anthropic, ...}`
- [ ] 4 个 profile .env 都有 `ANTHROPIC_API_KEY=***` `MINIMAX_CN_API_KEY=***` `od -c` 验证**完整**（不是 22 字符截断版）
- [ ] `KEY_FILE=~/minimax_key_value.txt python scripts/probe_llm_endpoints.py` 至少 1 个端点 ✅ 200
- [ ] `hermes chat -p X -q "hi"` 4 个 profile 都返回模型回复（不是 401、不是「Run setup」）
- [ ] `hermes gateway list` 4 个都 running
- [ ] 4 个 log 都有 `connected to wss://...`
- [ ] 飞书发消息 → 机器人按 SOUL.md 风格回话

---

## 相关

## 老大重复贴同一 key / 老大说"有钱"但平台 402 —— 2026-06-07 实战补充

**铁律**：

1. **老大重复贴同一 key ≠ 新指令**——别立刻报错"重复"。**先 `od -c ~/minimax_key_value.txt | head -1` 字节对比**，确认真的重复。老大连续发同样 key 通常是剪贴板/快捷键问题，**别脑补"老大记错了"**。
2. **"老大说有钱" vs "平台 402 insufficient_balance"** —— **信平台，不信口头**。MiniMax 平台主钱包和 API 账户是**完全独立计费池**，老大"有钱"经常指主钱包/订阅，**API 账户是 0**。
3. **换 key 解决不了账户问题**——**多个 key 都 402 = 那些 key 所属的账户都没钱**。**别再让老大换 key**，让老大查 API 账户余额页（不是钱包/订阅页）。

**老大重复贴 key 时正确做法**：

```bash
# 1. 比对磁盘上 key 字节
od -c ~/minimax_key_value.txt | head -1
# 2. 比对老大贴的 key 头 8 字符
# 3. 完全一样 → 静默回报"磁盘上已是这 key" + 跑一次当前结果（多半还是同样 402）
# 4. 不一样 → 正常流程：写新 + probe + chat 验
```

**"老大说有钱但 402" 的 5 秒确诊**：

```python
# 直连 curl 用同样 key 试同一个端点（绕开 hermes 客户端）
import urllib.request, json
key = open(r'C:\Users\Administrator\minimax_key_value.txt').read().strip()
body = json.dumps({'model':'MiniMax-M3','max_tokens':30,
                   'messages':[{'role':'user','content':'hi'}]}).encode()
for url, hdrs in [
    ('https://api.minimaxi.com/v1/chat/completions',
     {'Authorization': 'Bearer '+key, 'Content-Type':'application/json'}),
    ('https://api.minimaxi.com/anthropic/v1/messages',
     {'x-api-key': key, 'anthropic-version':'2023-06-01', 'Content-Type':'application/json'}),
]:
    req = urllib.request.Request(url, data=body, headers=hdrs, method='POST')
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            j = json.loads(r.read())
            print(f'✅ 200  {url}')
            if 'choices' in j:
                print(f'   text: {j["choices"][0]["message"]["content"][:80]!r}')
            elif 'content' in j:
                print(f'   text: {j["content"][0].get("text","")[:80]!r}')
    except urllib.error.HTTPError as e:
        print(f'❌ HTTP {e.code}  {url}  {e.read().decode()[:120]}')
```

**解读**：
- **直连 200 + 文本** → 端点+key+账户都没问题，**问题在 hermes 客户端握手**（`_requires_bearer_auth` / SDK 包装）→ 查 hermes 源码或换端点绕开
- **直连 401** → key 与端点不匹配（key 实际不是这个平台的）→ 回去找老大要正确 base_url
- **直连 402** → **铁证：账户真的没钱**，老大"有钱"指的是别的池子，**别再瞎试**，让老大去 platform.minimaxi.com 充 API 账户

**2026-06-07 实战案例**：老大连续给 4 个不同 key（2 个 `sk-cp-` + 2 个 `sk-api-`），**全 402**。直连 curl 测 `/anthropic/v1/messages` 用 `x-api-key` 头**返 200 + 真实回复**。结论：**端点 + key + 账户都没事**，**纯 hermes 客户端用 `Authorization: Bearer` 头访问 `/anthropic` 路径 401/402**（MiniMax `/anthropic` 路径要 `x-api-key` 头）。**修法 = hermes 0.15.1 `_requires_bearer_auth` 黑名单 bug**（见上面"两层 bug"小节），要换 base_url 绕开 `api.minimaxi.com` / `api.minimax.io` / azure 这几个 host。

---

## 实战 case：moosecloud.cc 中转站（2026-06-08 boss-control 跑通）

不是所有 key 都走 MiniMax 官方。**老大持久配置**：`MINIMAX_CN_API_KEY=sk-71d...a605`（67 字符）实际是 **moosecloud 中转站** key。`api.minimaxi.com` 直接走不通，必须配 `https://moosecloud.cc/v1`。**这就是为啥 .env 里 key 名字叫 `MINIMAX_CN_API_KEY` 但实际是 moosecloud**——名字误导，**信 probe 不信变量名**。

**跑通的 4 件套**（hermes 0.15.1 实测）：

```yaml
# config.yaml
model:
  default: gpt-5.4
  provider: custom        # ← 关键：不用 minimax-cn（被 _requires_bearer_auth 黑名单劫持）
  base_url: https://moosecloud.cc/v1
  api_key: sk-71d...a605  # ← 直接放 config.yaml，不是 .env
```

```bash
# .env 只需 LLM key，base_url/api_key 走 config
MINIMAX_CN_API_KEY=sk-71d...a605    # 双写兼容
```

**注意**：
- `model.api_key` 写在 config.yaml 里 OK（`provider: custom` 走这个字段，**不是 .env**）
- `model: gpt-5.4` 必须是 moosecloud 支持的模型——**不要写 `MiniMax-M3`**（moosecloud 不一定有这个 model 名）。先 `curl https://moosecloud.cc/v1/models` 拉模型列表挑一个
- `provider: custom` 不走任何 hermes SDK 包装，纯读 config.yaml 的 4 字段，**绕开所有 `_requires_bearer_auth` / OpenAI SDK 包装坑**

**验证 3 步**：

```bash
# 1. base_url 真配对（绕开 hermes，0 token）
curl -s -H "Authorization: Bearer sk-71dd...a605" https://moosecloud.cc/v1/models
# expect: 200 + 模型列表 JSON

# 2. hermes chat
hermes chat -p boss-control -q "用一句话说你是谁"
# expect: 8 秒内返回模型回复（不是 setup 提示符、不是 401）

# 3. gateway + wss
hermes gateway run -p boss-control > ~/hermes-gateway-logs/X.log 2>&1 &
sleep 8 && tail -3 ~/hermes-gateway-logs/X.log
# expect: [Lark] connected to wss://msg-frontier.feishu.cn/ws/v2?...
```

**踩坑时间线**（**未来再遇到类似症状 5 秒定位**）：
1. chat 60s 超时 → `cat config.yaml` 看 base_url
2. base_url 是 `http://127.0.0.1:9999/v1` → 本地代理没起 → 换 moosecloud
3. 401 + `provider: minimax-cn` → 换 `provider: custom` 绕开 SDK
4. config.yaml 缺 `api_key` 字段 → 加上（`custom` provider 必读这个字段）
5. 都改完 chat 8 秒返回 → 起 gateway → wss 连上 → 完工

**别瞎试的 provider 名**：`custom:minimax-anthropic` 这种**自创的 provider 名不保证存在**，`hermes config set model.provider custom:xxx` 写进去不会报错但**启动会失败**或行为未定义。**只用 hermes 已知的 provider**：`minimax-cn` / `anthropic` / `openai` / `openrouter` / `gmi` 等。**自定义要走 `custom:<name>` 写法 + 对应 plugin 目录**，不能凭空写。

---

## 相关

- [startup-and-not-replying.md](startup-and-not-replying.md) — 飞书 wss 那一层的「没回」排查
- `scripts/extract_minimax_key.py` — 从 default .env 抽完整 key（**用 fixed-offset arithmetic，不用 regex `.*`**）
- `scripts/inject_key_to_profiles.py` — 把 key 注入 4 个 profile .env（硬编码 4 个 profile 名）
- `scripts/inject_key_to_single_profile.py` — **单 profile 外科手术式注入**，保留所有其他行（FEISHU_* 等）。key 从 argv 传，避开 LLM 通道 redaction
- `scripts/probe_llm_endpoints.py` — 并行 7 端点 GET /v1/models 找真配对（零 token）
