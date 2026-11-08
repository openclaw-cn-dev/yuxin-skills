# Codex CLI 配置 — 2026-06 实测要点(0.42 + minimax 完整踩坑)

Codex 0.42 是接中转的稳定版(0.43+ 强制 Responses 协议,中转站不实现)。这一篇是踩过的坑汇总。

## 1. 配置入口:`~/.codex/config.toml`

Codex CLI **不**认 `ANTHROPIC_BASE_URL` 那种"环境变量套娃",所有非默认 provider **必须**写到 TOML 里。

**最小配置**(0.42 接 OpenAI 兼容中转,MiniMax 例):

```toml
# 顶层 model 必须是【字符串】(0.42 强制)
model_provider = "minimax"
model = "MiniMax-M3"

[model_providers.minimax]
name = "MiniMax 中转"
base_url = "https://api.minimaxi.com/v1"
env_key = "MINIMAX_API_KEY"
wire_api = "chat"
requires_openai_auth = false
```

**关键字段**:
- `model` 顶层字符串 — **不能**写 `[model] name = "..."` 子表(0.42 不吃,会报 `invalid type: map, expected a string`)
- `env_key` — Codex 启动时从 `process.env[env_key]` 读 key,不在文件里写明文
- `wire_api = "chat"` — OpenAI Chat Completions 协议(0.42);中转站都用这个。**不要**写成 `responses`(那是 OpenAI 新协议,中转站不实现)
- `requires_openai_auth = false` — 跳过 OpenAI 官方登录

## 2. CLI + GUI 共用同一份 config

**关键事实**:`~/.codex/config.toml` 同时被 Codex **桌面 GUI**(Electron 进程) 和 **CLI**(`codex` 命令) 读。**改这文件两个都会受影响。**

- GUI 段:`[plugins."browser@openai-bundled"]` / `[mcp_servers.node_repl]` / `[marketplaces.openai-bundled]` / `notify` 等
- CLI 段:顶层 `model_provider` / `model` / `[model_providers.xxx]`
- **写 CLI 配置时 GUI 段必须保留**,删了桌面启动会报连不上
- CLI 跑时如果看到一堆 `ERROR codex_core::mcp_connection_manager` 启动 120s 超时降级,是 GUI 段残留,不影响 API 调用,忽略

## 3. Key 隔离:别污染 `OPENAI_API_KEY`

很多中转站(尤其国产)key 也长 `sk-` 开头。直接设 `OPENAI_API_KEY` 会跟未来"接 OpenAI 官方"打架。**强制**用专用名:

- `MINIMAX_API_KEY` 接 minimaxi.com
- `MOOSE_API_KEY` 接 moosecloud.cc
- `DEEPSEEK_API_KEY` 接 deepseek.com

Config 里 `env_key = "MINIMAX_API_KEY"` 配 User 级 env,最干净。

**常见 key 前缀对照** (2026-06 实测):
| 平台 | key 前缀 |
|---|---|
| OpenAI 官方(新) | `sk-proj-` 长串 |
| OpenAI 官方(旧) | `sk-` 短串(已废弃) |
| MiniMax 中转 | `sk-cp-` 长串 |
| Moose 中转 | `sk-` + 自定义 |
| DeepSeek | `sk-` |

`sk-cp-` 是 minimaxi 中转的**正常**前缀,不是仿冒信号。

## 4. 验收脚本里的"set 占位符再判断"陷阱(本会话踩过)

**错误写法**:
```bat
set "MINIMAX_API_KEY=*** [SK] ***
if "%MINIMAX_API_KEY%"=="*** [SK] ***" (
  echo 没设
)
```
**坑**:这行 set **会覆盖**从父进程继承来的 env,本来已设的 key 也被清成占位符,永远走"没设"分支。

**正确写法**:
```bat
if not defined MINIMAX_API_KEY (
  echo 没设
)
```

`if not defined` 只检查变量是否在当前进程 env 里存在,**不会**修改它。User 级 env 在新开 cmd 自动继承,直接 `if not defined` 就拿到。

完整验收模板见 `templates/codex-exec-verify.bat`。

## 5. 启动 Codex 桌面 GUI

Codex 桌面是真 Electron 应用,**不能**用 `codex`(CLI)启动。启动路径:

```
%LOCALAPPDATA%\OpenAI\Codex\bin\<hash>\codex.exe
```

- `<hash>` 是安装 hash,每台机不同(如 `f1c7ee7a13db5fed`)
- 启动后主进程叫 `Codex.exe`,带多个 `codex.exe` / `Codex.exe` 子进程(Electron 架构:渲染/GPU/utility),都是正常的
- **在 Hermes terminal 里启动必须用 `background=true`**,**绝对不要**用 `&`(shell 层的 backgrounding,hermes 不会跟踪生命周期)

正确调用:
```python
terminal(command='"C:\\Users\\Administrator\\AppData\\Local\\OpenAI\\Codex\\bin\\<hash>\\codex.exe"',
         background=True, notify_on_complete=False)
```
`notify_on_complete=False` 是对的——GUI 永远不退出,没"完成"可言。

启动后 `tasklist | grep -i codex` 看到主进程 ~200MB + 多个子进程 = 启动成功。

## 6. CLI 0.42 非交互跑法

```bash
# 关键:非交互是 exec 子命令,不是 -p 标志(-p 在 0.42 是 --profile)
codex exec --skip-git-repo-check \
  -m "MiniMax-M3" \
  -c model_provider="minimax" \
  "你的 prompt"
```

**4 个必备参数**:
- `exec` 子命令(0.42 的非交互入口)
- `--skip-git-repo-check`(桌面/非 git 目录必加,否则拒跑)
- `-m` 跟中转侧实际模型名
- `-c model_provider="..."` 跟 config.toml 里的 `[model_providers.xxx]` 名一致

**反模式**:`codex -m "..." -p "..."` 在 0.42 会启动 TUI 卡死等用户选审批模式。

## 7. Domain 验真流程(中转站必走)

任何接第三方平台,第一件事 nslookup,顺序如下:

```bash
# 1) 主域验真(主域不存在 = 平台根本不存在,别再往下)
nslookup minimax.cn          # 老叫法,Non-existent → 停
nslookup minimaxi.com        # 真域名,通

# 2) API 子域验真
nslookup api.minimaxi.com    # 通 → 进下一步

# 3) HTTP 健康(根路径 404 正常,关键是能连上)
curl -sS -o /dev/null -w "HTTP %{http_code} (%{time_total}s)\n" --max-time 8 https://api.minimaxi.com/
```

**`MiniMax-M3` vs `minimax`**:老大的"minimax"是**公司/产品口语简称**,真实:
- 域名:`minimaxi.com`(末尾 i)
- API 域:`api.minimaxi.com`
- 模型名:`MiniMax-M3` / `MiniMax-Text-01` / `MiniMax-M1` 等(控制台"模型广场"查)

把"minimax"当 base URL 写 = 必败。

## 8. 故障矩阵(本会话全过过)

| 现象 | 修法 |
|---|---|
| `command not found` | PATH 问题,新开终端 / `where codex` |
| `401 Unauthorized` | env 没设 / 设错 / 还没新开 cmd |
| `404 Not Found` | base_url 末尾漏 `/v1`,或模型名拼错 |
| `model not found` | 用本地叫法当 API 名了,去控制台"模型广场"查真实名 |
| `wire_api: openai_responses is not supported` | 装错版本,降到 `@openai/codex@0.42.0` |
| `wire_api = "chat" is no longer supported` | 同上,降到 0.42 |
| `invalid type: map, expected a string in 'model'` | 顶层 model 必须是字符串,不能写 `[model] name="..."` 子表 |
| `unknown variant 'openai-chat', expected 'responses'` | 0.42 用 `chat` 不是 `openai-chat` |
| 一堆 `ERROR codex_core::mcp_connection_manager` | GUI 段残留,不影响 API,忽略 |
| `error sending request` | DNS/网络,先 `nslookup api.minimaxi.com` 验 |
| 终端 `npm: command not found` 在 execute_code 里 | subprocess 继承不到完整 PATH,**必须**用 terminal 工具跑 npm |

## 9. execute_code 子进程找不到 npm 的坑(本会话踩过)

`from hermes_tools import terminal` 在 execute_code 里**能**用,但 **直接 `subprocess.run(["npm", ...])` 会 `FileNotFoundError: 系统找不到指定的文件`**。

原因:execute_code 的 Python 进程 PATH 不含 npm 全局目录(`%AppData%\Roaming\npm`)。

**修法**:
- 涉及 npm / 任何 CLI 工具的子进程调用,一律走 `terminal()` 工具,不要在 execute_code 里 subprocess.run
- terminal 工具的 PATH 才是完整的 Windows PATH

## 10. 中转站速查(2026-06 已验证)

| 平台 | base_url | env_key 建议名 | wire_api | 备注 |
|---|---|---|---|---|
| MiniMax (minimaxi.com) | `https://api.minimaxi.com/v1` | `MINIMAX_API_KEY` | `chat` | 域通,endpoint 通,key 真有效,模型 MiniMax-M3 实测 |
| Moose (moosecloud.cc) | `https://moosecloud.cc/v1` | `MOOSE_API_KEY` | `chat` | 15 模型,gpt-5.4 稳、5.5 偶发 502 |
| DeepSeek (deepseek.com) | `https://api.deepseek.com/v1` | `DEEPSEEK_API_KEY` | `chat` | 国产稳 |
| 硅基流动 (siliconflow.cn) | `https://api.siliconflow.cn/v1` | `SILICONFLOW_API_KEY` | `chat` | 多模型聚合 |
| OpenAI 官方 | `https://api.openai.com/v1` | `OPENAI_API_KEY` | `chat` 或 `responses` | 需 OpenAI 账号 |

**反向提示**:任何"仿冒"信号(模型名小数点像 GPT-5.5、域名长得像 gptapi.com、价格低到不可信),**不接**。`sk-cp-` 是 minimax 中转的正常前缀,**不是**仿冒信号。

## 11. 一次完整的接 API 流程(Codex 0.42 + MiniMax)

```bash
# 1) 装 CLI(走 npmmirror 9 秒,官方源 30-60 秒)
npm install -g @openai/codex@0.42.0

# 2) 验域(老叫法 "minimax" 主域不存在,必查)
nslookup api.minimaxi.com

# 3) 写 config(小弟用 templates/codex-config.toml,改 base_url + env_key)
#    关键:model 顶层字符串,不能写 [model] name="..." 子表
#    GUI 段 [mcp_servers.node_repl] 等保留
#    codex --version → codex-cli 0.42.0
#    codex -c model="MiniMax-M3" -c model_provider="minimax" --help  # 不报错就 ok

# 4) 老大自己设 key(小弟不代填,这是安全原则)
powershell -Command "[Environment]::SetEnvironmentVariable('MINIMAX_API_KEY','sk-cp-...K7HE','User')"

# 5) 新开 cmd,跑最小对话(用 if not defined 校验,不污染 env)
codex exec --skip-git-repo-check -m "MiniMax-M3" -c model_provider="minimax" "say 'hello' and exit"

# 期望最后一行: hello from minimax
# 看到这句 = provider=minimax + model=MiniMax-M3 跑通,key 真有效
```
