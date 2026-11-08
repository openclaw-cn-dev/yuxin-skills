---
name: llm-cli-setup
description: Install, configure, and verify a local LLM coding CLI (Claude Code, OpenAI Codex CLI, Gemini CLI, Qwen Code, etc.) against any provider — Anthropic first-party, OpenAI first-party, or third-party/中转 endpoints. Covers the full "npm install -g → DNS verify provider domain → collect 4 must-have config items → write env vars → smoke test" workflow. Use when老板 says "装 Claude Code", "装 Codex", "配 API Key", "接中转", "接 MiniMax / DeepSeek / 硅基流动 / 任意国产模型平台", "Claude Code 跑不通", "model not found", "API 401/403/404". Triggers on "安装 LLM CLI", "配置大模型", "接 API", "换模型", "CLI 装机", "claude code 配置", "codex 装".
---

# LLM CLI Setup — 装 + 配 + 验

为老大在 Windows 机器上装、配置、验证一个 LLM coding CLI(默认 Claude Code,方法论可移植到 Codex CLI / Gemini CLI / Qwen Code)。

## 0. 安全原则(最重要,先讲)

**小弟绝不替老大管 API Key。** 两种边界:

- **CLI 装机**小弟可以代劳(`npm install -g`,纯网络下载,不涉密)
- **配置 Key / 写 env 文件**绝对交给老大自己——这事儿过手就可能泄
- 装完用**占位符 + 注释**写好 env 模板,老大自己填值

理由:terminal/文件操作链上任何一步被截留,Key 就裸奔。Key 一旦换,损失的是真金白银的额度+隐私数据。

## 1. 工作流(4 步强制)

任何 LLM CLI 配置都走这 4 步,**第 1 步没过不许进第 2 步**:

```
[1] 装 CLI      → npm/pnpm install
[2] 验域名      → nslookup 矩阵(如果接第三方平台)
[3] 收 4 项配置  → Key / base URL / 模型名 / 协议
[4] 写 env+验收 → setx 或 .env 文件,claude --version 之外还要跑一次最小对话
```

跳步 = 装出哑炮,老大回头骂小弟。

## 2. [1] 装机 — Claude Code 标准操作

```bash
# 0) 前置检查
node --version          # 必须 ≥18,建议 ≥20
npm --version
npm config get registry # 看源

# 1) 装(npmmirror 源 9 秒,官方源 30-60 秒)
npm install -g @anthropic-ai/claude-code

# 2) 验收
claude --version        # 应输出 "2.1.x (Claude Code)"
which claude             # Windows: where claude
```

**已知坑**(记在 memory 里的):
- Windows 机器 terminal 跑 `npm install -g` **有概率卡死等确认**——如果卡了 Ctrl+C 出来,改成让老大在 PowerShell GUI 里手敲
- npm 源在 `~/.npmrc` 里,写死 npmmirror 装得快;切官方源要 `npm config set registry https://registry.npmjs.org/`

**其他 CLI 的对照**(同类操作,不重复展开):
- **Codex CLI: `npm i -g @openai/codex`** — 0.138+ 必须用 `~/.codex/config.toml` 的 `[model_providers.xxx]` 块接中转,不走 env 套娃。详见 `references/codex-cli-config.md` + `templates/codex-config.toml`
- Gemini CLI: `npm i -g @google/gemini-cli`
- Qwen Code: `npm i -g @qwen-code/qwen-code`(国产,开箱用通义千问)

## 3. [2] 域名验真 — 这一步是小弟栽过的坑

**接任何第三方平台,第一件事 `nslookup` 它的主域 + 控制台子域 + www 子域。**

```bash
nslookup platform.xxx.cn
nslookup www.xxx.cn
nslookup xxx.cn
```

**判定矩阵**:

| nslookup 结果 | 行动 |
|---|---|
| 全有 IP | 进第 3 步 |
| 主域有 IP,子域没 | 问老大控制台具体 URL,可能有 path 前缀 |
| **主域 Non-existent domain** | **域名本身不存在**——停下来让老大贴正确链接/截图。**不要瞎猜 base URL**,猜了写进 env 等于把 Key 投喂给任意第三方 |
| DNS 解析超时 | 网络问题,重试一次,还不行就 ping 8.8.8.8 验证出口 |

**反面教材 + 自我纠偏(本会话两次踩坑的总结)**:

- **第 1 坑(DNS 不可达)**:老大说"MiniMax-M3 平台" → 小弟直接信了,浏览器跳 `platform.MiniMax.cn` 报 ERR_NAME_NOT_RESOLVED
  - `nslookup` 一查:`MiniMax.cn` 主域都不存在
  - 教训 1:哪怕老大斩钉钉铁说"就是这家",**DNS 不会骗人**,信 nslookup 不信口头确认

- **第 2 坑(DNS 通 ≠ 名字对)**:上面验出 `MiniMax.cn` 错后,老大换了"platform.MiniMax.cn",小弟还是直接信,又踩一次
  - 后来在 CC-Switch 官网(`ccswitch.io`)抓供应商列表时,**截图**里赫然写着 `platform.minimaxi.com`(末尾 i)
  - 教训 2:**DNS 解析通 ≠ 是老大要的那个平台**。域名拼写一字之差就是不同的厂商
  - 教训 3:拼写/平台归属的最终证据是**官方控制台截图**或**控制台右上角 URL**,不是 nslookup,也不是老大口述

- **合并后的流程**(更新到第 3 步前):
  ```
  [1] nslookup 主域/子域                  → 排除"完全不存在"
  [2] 在官方文档/官网/CC-Switch 预设列表   → 抓真实 URL 截图
  [3] 把截图 URL 跟老大口述的对照          → 不一致就停下问
  [4] 才开始收集 4 项配置
  ```
  跳 1/2/3 直接进 4 = 装出哑炮。

## 4. [3] 收 4 项必填配置

缺一项就跑不通。**这 4 项**:

| 项 | 例子 | 怎么拿 |
|---|---|---|
| ① API Key | `sk-ant-xxx` / `sk-xxx` | 平台控制台"API Keys"页**老大自己生成**,**别让小弟代填** |
| ② base URL | `https://api.anthropic.com` / `https://api.deepseek.com/v1` | 控制台"API 接入"或文档"endpoint"页 |
| ③ 模型名 | `claude-sonnet-4-5` / `deepseek-chat` | 控制台"模型列表"页。**修正(2026-06-13 实测)**:`MiniMax-M3` 这种带连字符的本地叫法**可以是** API 真实名(M3 系列在 minimaxi 模型广场真的就叫这个),**先按本地叫法试,真"model not found"再问老大**;别一上来就否定。 |
| ④ 协议 | Anthropic Messages / OpenAI Chat Completions / 自有 | 文档"接口协议"页;不确定就问老大或让老大贴文档链接 |

**怎么问老大**:一次性给 4 个空,**附 A/B/C 选项**让老大快速填,**不要反复确认**(老大的偏好"决策风格果断——喜欢给 ABC 选项快速决策")。

## 5. [4] 写 env + 验收

### A 方案:官方 Anthropic(最简单)
```cmd
setx ANTHROPIC_API_KEY "sk-ant-你的key"
```
新开终端跑 `claude` 会引导登录。

### B 方案:接第三方中转
```cmd
setx ANTHROPIC_BASE_URL "https://api.xxxxx.cn"
setx ANTHROPIC_AUTH_TOKEN "你的key"
setx ANTHROPIC_MODEL "平台侧实际模型名"
setx ANTHROPIC_SMALL_FAST_MODEL "小模型名"
```

> 注:Anthropic SDK 用的是 `ANTHROPIC_AUTH_TOKEN`(不是 `ANTHROPIC_API_KEY`)来兼容中转场景。记混了 401 报错不告诉你原因。

### C 方案:Codex CLI 接中转(独立路径)

Codex 0.42(非 0.43+)不用 env 套娃,走 `~/.codex/config.toml` 的 `[model_providers.xxx]` 块。模板在 `templates/codex-config.toml`,5 家已验证预设(MiniMax / Moose / DeepSeek / 硅基流动 / OpenAI 官方)直接复制。详见 `references/codex-cli-config.md`。

**⚠️ 0.42 关键约束(2026-06 实测踩坑)**:顶层 `model` 必须是**字符串**(`model = "MiniMax-M3"`),**不能**写 `[model] name = "..."` 子表(0.42 不吃,报 `invalid type: map, expected a string in 'model'`)。

**Key 隔离原则**:**永远别用 `OPENAI_API_KEY` 这个槽**——跟 OpenAI 官方账号同名会污染。**强制**用专用名:`MINIMAX_API_KEY` / `MOOSE_API_KEY` / `DEEPSEEK_API_KEY`。

### 验收脚本
1. `claude --version` / `codex --version` → 至少 2.0.0 / 0.100.0
2. `claude -p "say hi"` / `codex -m "MiniMax-Text-01" -p "say hi"` → 期望看到模型回复
3. 失败处理:
   - `command not found` → PATH 问题,重开终端
   - `401` → Key 错
   - `404` → base URL 错或模型名错
   - `connection refused` → 网络/代理问题
   - `model not found` → 用平台侧真实模型名(常见坑:把本地叫法 `MiniMax-M3` 当 API 名传了)
   - `wire_api: openai_responses is not supported` → 改 `wire_api = "chat"`

## 6. 老大的偏好(写进 skill,下次自动遵守)

- 称呼:叫 AI 自己"小弟",叫用户"老大"
- 偏好 ABC 选项快速决策,**不反复确认**
- 装机/接 API 这种**涉密活儿**,小弟只做**不涉密的部分**(装 CLI、查文档、起模板),涉密部分(填 Key、设最终环境)交给老大
- 给"清单 + 数字 + 下一步建议",不要长段解释
- **少 AI 味**:短句、口语化、具体数字区间(90%、2℃、7 天那种)

## 7. 触发这个 skill 的典型场景

- "装 Claude Code / Codex / Gemini / Qwen Code"
- "接 MiniMax / DeepSeek / 智谱 / 硅基流动 / 月之暗面 / 任意国产模型平台"
- "claude code 跑不通 / 401 / 404 / model not found"
- "换模型 / 切 base URL"
- 老大提**任何不熟的平台名**,**先 nslookup** 再继续

## 8. Codex CLI 特殊配置 (2026-06 实测,接第三方中转必看)

**关键背景**:codex 0.43+ 强制 OpenAI Responses API 协议 (`wire_api = "responses"`),**不再支持 OpenAI Chat Completions 兼容**。任何走 chat 协议的国内中转(MiniMax、DeepSeek、火山、智谱 openai-mode)装最新 codex 必败。

### 8.1 决策:装新版 vs 装 0.42

| 场景 | 推荐版本 | 原因 |
|---|---|---|
| 走 OpenAI 官方 ChatGPT 登录 | 最新版(0.138+) | 用 Responses 原生 |
| 走第三方 OpenAI 兼容中转 | **强制 0.42.0** | 0.43+ 不再支持 `wire_api=chat` |

降级命令:
```bash
npm uninstall -g @openai/codex
npm install -g @openai/codex@0.42.0
codex --version   # 期望:codex-cli 0.42.0
```

### 8.2 0.42 的 config.toml 必填模板(接 MiniMax 实测)

```toml
# 不写 [model] 子表!0.42 要求 model 是字符串
model_provider = "minimax"
model = "MiniMax-M3"   # 2026-06-13 实测:本地叫法 MiniMax-M3 就是 API 真实名,直接用

[model_providers.minimax]
name = "MiniMax 中转"
base_url = "https://api.minimaxi.com/v1"   # 先 nslookup 验过再写
env_key = "MINIMAX_API_KEY"                # 走专用 env 名,不污染 OPENAI_API_KEY
wire_api = "chat"                          # 0.42 还支持这个值
requires_openai_auth = false
```

**配置错误速查**(都是真踩过的):
- `invalid type: map, expected a string in 'model'` → 0.42 要求 model 是字符串,不是 `[model] name = "..."` 子表
- `unknown variant 'openai-chat', expected 'responses'` → 用 `chat` 不是 `openai-chat`(0.138 才用 `responses`)
- `wire_api = "chat" is no longer supported` → 装错版本,降到 0.42

### 8.3 0.42 非交互跑法

```bash
# 关键:非交互是 exec 子命令,不是 -p 标志
codex exec --skip-git-repo-check \
  -m "MiniMax-Text-01" \
  -c model_provider="minimax" \
  "你的 prompt"
```

**4 个必备参数**:
- `exec` 子命令(0.42 的非交互入口)
- `--skip-git-repo-check`(桌面/非 git 目录必加,否则拒跑)
- `-m` 跟中转侧实际模型名
- `-c model_provider="..."` 跟 config.toml 里的 `[model_providers.xxx]` 名一致

### 8.4 端到端验收脚本(用模板,不要手敲)

不直接覆盖:用 `templates/codex-exec-verify.bat`(已就绪,双击跑 4 步验收:版本→key→env 注入→exec 最小对话)。**关键设计**:
- 不用 `***` 作任何占位符(memory 警告:渲染层会吞)
- `set "MINIMAX_API_KEY=*** %SK%` 显式从 User 级 env 拉 key 注入 batch 进程
- PowerShell → cmd → codex 链路不继承 env,必须在 batch 内 set
- 脱敏用 `!SK:~0,8!...!SK:~-4!`,不显示完整 key

### 8.5 反模式(接 codex + 中转时)

- ❌ 装最新 codex 想接中转 → 必败,直接降到 0.42
- ❌ `[model] name = "..."` 子表写法 → 0.42 不吃
- ❌ `wire_api = "openai-chat"` → 0.42 是 `chat`,0.138 是 `responses`,别混
- ❌ `codex -p "prompt"` → -p 在 0.42 是 `--profile`,非交互用 `exec`
- ❌ 在 git 仓库外的目录跑 codex exec → 必加 `--skip-git-repo-check`
- ❌ `codex -m "..." -p "..."` 调非交互 → 0.42 启动 TUI 卡死等用户选审批模式

## 8. 反模式(明确不要做)

- 替老大填 API Key 到 env
- 域名没验真就写 base URL
- 用本地叫法当 API 模型名
- 把第三方中转的 Key 写进 SKILL.md / 文档
- 装完不跑最小对话验收
- 反复确认同一个问题(老大说"先装上"就装上,别再问 3 遍)
- 接 Codex 0.138+ 时用 `OPENAI_API_KEY` 槽(跟 OpenAI 官方账号冲突)

## 12. Codex GUI 桌面启动(2026-06 实测)

Codex 桌面是真 Electron 应用,**不能用 `codex` CLI 启动**。启动路径:

```
%LOCALAPPDATA%\OpenAI\Codex\bin\<hash>\codex.exe
```

- `<hash>` 是安装 hash,每台机不同(本机是 `f1c7ee7a13db5fed`)
- **在 Hermes terminal 里启动必须用 `background=true` + `notify_on_complete=False`**,**绝对不要**用 `&`(shell 层 backgrounding,hermes 不会跟踪生命周期)
- GUI 永远不退出,所以 notify_on_complete 设 false(GUI 没"完成"可言,通知也白搭)
- 启动后主进程叫 `Codex.exe`(~200MB),带多个 `codex.exe` / `Codex.exe` 子进程(Electron 渲染/GPU/utility 架构)都是正常的

**CLI + GUI 共用 `~/.codex/config.toml`**——改这文件两个都受影响。CLI 段(`[model_providers.xxx]`)+ GUI 段(`[mcp_servers.node_repl]` / `[plugins."browser@openai-bundled"]`)都得保留。CLI 跑时 GUI 段会拉 MCP 启动 120s 超时降级,日志里看到一堆 `ERROR codex_core::mcp_connection_manager`,**不影响 API 调用,忽略**。

## 12. Electron 在 Windows + git-bash 装机的坑(2026-06-13 实测)

`npm install electron` 装出来可能**没 `dist/electron.exe`**(只有 `locales/`)。根因是 `electron@32.x` 的 `install.js` 调 `extract-zip` 时用 `__dirname`-based 相对路径,git-bash + Windows 上被 `extract-zip@2` 拒(`Target directory is expected to be absolute`),且 `.catch` 报错被静默吞;另外 `stdin is not a tty` 会让 `@electron/get` 直接 `process.exit(0)` 不下 zip。

**1 行诊断**:
```bash
[ -f node_modules/electron/dist/electron.exe ] && echo OK || echo BROKEN
```

`BROKEN` = 走手动解压 + 写 `path.txt` + 写 `dist/version`,3 步 30 秒修好。完整根因 + 脚本见 `references/electron-windows-install.md`。

## 13. execute_code 里跑 npm 必败(2026-06 实测)

`from hermes_tools import terminal` 在 execute_code 里能用,但 **直接 `subprocess.run(["npm", ...])` 必败**:`FileNotFoundError: 系统找不到指定的文件`。

原因:execute_code 的 Python 子进程 PATH 不含 `%AppData%\Roaming\npm`。

**修法**:
- npm / 任何 CLI 工具的子进程调用,一律走 `terminal()` 工具,不要在 execute_code 里 subprocess.run
- terminal 工具的 PATH 才是完整的 Windows PATH

## 14. .bat 验收脚本的"set 占位符"陷阱(2026-06 实测)

`templates/codex-exec-verify.bat` 第一版用 `set "X=占位符"` 判 env,会**覆盖**父进程继承的 env,本来设好的 key 也会被清成占位符,永远走"没设"分支。

**正确**:`if not defined X` 只检查变量是否存在,**不修改**它。User 级 env 在新开 cmd 自动继承,直接 `if not defined` 就能拿到。详见 `templates/codex-exec-verify.bat` 最新版。

## 15. key 前缀安全识别(2026-06 更新)

`sk-cp-` 长串是 **MiniMax(minimaxi.com)中转站的正常 key 前缀**——不是仿冒信号。老 skill 里写的"`sk-` 旧格式就是仿冒"是过粗的启发式,要按平台区分:

| 平台 | key 前缀 | 真/假信号 |
|---|---|---|
| OpenAI 官方(2025+ 新) | `sk-proj-` 长串 | 真 |
| OpenAI 官方(2024 前 旧) | `sk-` 短串 | 真(老 key,但还能用) |
| MiniMax 中转 | `sk-cp-` 长串 | **真**(2026-06 实测,老大在用) |
| Moose 中转 | `sk-` + 自定义 | 真 |
| DeepSeek | `sk-` | 真 |

**真仿冒信号**才是判定标准:模型名小数点(GPT-5.5/4.5)、域名像 `gptapi.com`、价格低到不可信、同一 key 多次声称不同型号。`sk-cp-` 这些都不沾,放心接。

## 10. 第三方 CLI 管理工具(CC-Switch 这类)的选型陷阱

**老大说"装个 X switch"时,先厘清是 CLI 命令行版还是 GUI 桌面版**——npm 上带 "switch/manager" 关键词的包经常 5+ 个并存,**而且完全没人维护命名约定**。

**反面教材**(本会话栽过):老大说"装 cc switch" → 小弟列了 4 个候选,老大选 3 → 装出来是 `claude-config-switch`(CLI inquirer TUI)→ 老大立刻说"不是有 UI 版的吗,安装错了,重新安装" → 浪费一次安装卸载往返。

**判定流程**:

```
[1] 问老大/自己搜:UI 桌面 vs CLI 终端?
    - 短句带 "UI/桌面/GUI/界面/可视化" → 走桌面 GUI
    - 短句没强调或带 "cli/终端/命令行" → 走 CLI

[2] 桌面 GUI 工具的标准核验(CC-Switch 模式):
    a) 官网"免费下载"按钮点进去看实际跳哪个 Release
    b) 跳到的 Release Assets 里必须有 .msi / .exe / -Windows-*.zip
       **官方文档写"支持 Windows"但 Assets 没 Windows 包 = 常见**(CI 流水线 bug / 故意砍)
    c) 找到有 Windows 包的最后一版,**记录功能落后 N 个月**告诉老大
    d) curl 拉 GitHub Releases 经常被本机网络层拦(HTTP 000 Empty reply)
       → 改走 .url InternetShortcut 桌面快捷方式(见下方模板)

[3] CLI 工具的标准核验:
    npm view <pkg>  →  看 bin 字段有几个(多个说明有 alias 入口,别只看主名)
    npx <pkg> --help  →  验证是 TUI inquirer(菜单)还是 argparse(命令)
```

**`.url` 桌面快捷方式模板**(curl 不通时的兜底):

```ini
[InternetShortcut]
URL=<真实 GitHub Release 下载 URL>
```

存到桌面,Windows 双击用默认浏览器/IDM/迅雷下。比 curl 稳,本会话实锤过。

**关键原则**:**永远不要让老大点"免费下载"按钮就算完**——必须自己打开 Release 页的 Assets 列表,**亲眼看到对应平台的 .msi/.exe** 才能写"装好了"。

## 🆕 仿冒 / 假 LLM 平台 key 检测(2026-06-07 实测)

**典型信号**(任一出现就停下来验证):

| 信号 | 例子 | 风险 |
|---|---|---|
| **模型名在 OpenAI 公开列表里不存在** | "GPT-5.5"、"GPT-5.4"、"GPT-4.5"、"GPT-4.5-turbo" | 仿冒站话术,**OpenAI 命名是整数(GPT-3 / 3.5 / 4 / 4o / 5),小数点是仿冒** |
| **key 格式与声称厂商不符** | 声称 OpenAI 但 key 是 `sk-` 老格式(OpenAI 现在是 `sk-proj-` 长串) | 盗刷的卡 key 或钓鱼中转 |
| **同一把 key 老大多轮重复发 + 归属漂移** | 第一条说 MiniMax,第二条说 GPT-5.5,第三条又说是 GPT-5.4 | 来历可疑,**每次发不一样型号** = 在乱试 |
| **base_url 是仿冒站常见域名** | `api.gptapi.com`、`api.aichat.com`、`api.gptplus.cn` | 99% 是中转站,跑路 / 盗卡 / 截数据三连 |
| **价格明显低到不可信** | "GPT-4 $0.5/M token" | 别人的卡开的,**3-7 天后原卡主封 key** |

**拒绝接入的标准话术**(既不伤老大面子,又守住安全线):

```
老大,这把 key 看着有 [具体可疑点],我先不接。
建议直接换正经渠道:[A/B/C 三个国内正规平台 + 链接]
挑一个,拿到新 key 给我,我 5 分钟接好。
```

**老大坚持要接**("就测试用 / 玩一下")的处理路径:

1. **不直接拒绝**(老大决策极果断,问完就拍,反复劝会烦)
2. **先打预防针**:"我把它当玩具层接,敏感数据(飞书群 ID / 业务线)仍走 MiniMax 主路径;24h 内你说切回去我立刻换"
3. **存到 `~/feishu-secrets.json` + chmod 600 / icacls 锁**(**不**直接写 .env 槽位当主 provider,避免污染主配置)
4. **24h 后自动审计**:token 消耗、调用成功率、是否被原卡主封 key
5. **如果用着用着发现 key 失效/被封**:立即回滚到上一把可用的 provider,不要等老大问

**写 env 的位置选择**(不要污染主 provider):
- 单独加 `CUSTOM_<NAME>_API_KEY` / `CUSTOM_<NAME>_BASE_URL` env 槽
- 不要直接覆盖 `MINIMAX_CN_API_KEY` / `OPENAI_API_KEY` 现有槽
- 不要改 `hermes config set model.provider`(会让所有 fallback 失效)

**记忆要点**(写进 memory):每接一把新 key,**必须**记录
- 来源(哪个平台 / 谁给的 / 哪条消息)
- 声称的模型名 + 实际指纹(key 前 8 + 后 4 字符)
- 接入时间
- 失效时间 / 回收时间

例子:
```
[CUSTOM_GPT_TEST]
key_fp: sk-71d...a605
claimed_model: "GPT-5.5"(疑仿冒)
real_provider: minimax-cn(用 minimax-cn 的 provider 接,model 字段填 minimax-M3)
added: 2026-06-07
```

**反模式补充**:
- 老大说"就测试一下"就信 → 仿冒站的 key 7 天后必封
- 拒绝时讲大道理 → 老大偏好 ABC 选项快速拍板,**直接给替代方案**
- 把测试 key 当主 provider 写 .env → 污染配置,**恢复难**

## 9. Windows git-bash 装 Electron 类 CLI 的统一坑(2026-06-13 实测)

**适用场景**:老大要在 Windows 机器上装任何 Electron 内核的 CLI(不只是 LLM CLI,还有 Postman / Insomnia / Discord 客户端 / VSCode 衍生品)。

### 9.1 症状

`npm install -g electron` 或 `electron-builder` 时:

```
npm install 成功
node_modules/electron/dist/ 目录下只有 locales/
electron.exe 没下下来
node install.js < /dev/null 直接 exit 0
```

### 9.2 真凶

**`@electron/get` 的 `extractFile()` 调 `extract-zip` 时,`distPath` 在 git-bash 解析下不是绝对盘符路径** → `Target directory is expected to be absolute` 报错。

但这个错误被 `install.js` 末尾的 `.catch(err => { console.error(err.stack); process.exit(1); })` 在后台进程里**静默吞掉**(非 TTY + pipe 双重压制),看起来像"装好了"实则没下完。

**`isInstalled()` 的假阳性**:解到一半留下的 `dist/locales/` 目录被 `isInstalled()` 当成"已装"判定,**下次跑 install.js 直接 `process.exit(0)` 跳过下载**。

### 9.3 修法(手动)

```bash
# 1) 找 zip 已经在 cache 里
ls "/c/Users/Administrator/AppData/Local/electron/Cache/" | head
# 看到一串 sha512 hash 子目录 + electron-vXX.X.X-win32-x64.zip

# 2) 手解到绝对路径
ZIP="/c/Users/Administrator/AppData/Local/electron/Cache/<hash>/electron-v32.3.3-win32-x64.zip"
cd /c/Users/Administrator/Desktop/<project>/node_modules/electron
rm -rf dist
mkdir -p dist && cd dist && unzip -q "$ZIP"

# 3) 骗过 isInstalled() — 写两个标记文件
echo "electron.exe" > ../path.txt
echo "v32.3.3" > dist/version

# 4) 验
./dist/electron.exe --version
# 期望: v32.3.3
```

### 9.4 一次性预防

`~/.npmrc` 提前设 ELECTRON 镜像 + 走 TTY 模式跑:

```bash
echo 'ELECTRON_MIRROR=https://npmmirror.com/mirrors/electron/' >> ~/.bashrc
```

但**注意**:`ELECTRON_MIRROR` 只影响 @electron/get 的下载,**不**修复 extract-zip 的绝对路径 bug。**根治得等 @electron/get 修这个 issue**,或者放弃 git-bash 走 PowerShell / cmd.exe。

完整排错记录见 `references/electron-windows-install.md`(解压失败的 stderr 截图 + 5 步手动恢复 SOP)。

## 16. 🆕 Codex 桌面维护（2026-07 实测追加）

### 16.1 换模型名

改 `~/.codex/config.toml` 第 2 行 `model = "xxx"` 即可，**不需要改其他配置**。base_url / auth.json / wire_api 都不动。

```bash
# 例：ark-code-latest → deepseek-v4-pro-260425
# 直接 patch config.toml 的 model 行
```

### 16.2 CODEX_CLI_PATH 过期

Codex 升级后 bin 目录 hash 会变，config.toml 里的 `CODEX_CLI_PATH` 指向旧 hash 目录（不存在）。**不影响桌面启动**（桌面用自己的路径），但 CLI 子进程调用会失败。

修法：`ls %LOCALAPPDATA%\OpenAI\Codex\bin\` 找新 hash，更新 config.toml 里的 `CODEX_CLI_PATH`。

### 16.3 语言/行为偏好——AGENTS.md

Codex 桌面启动时读取 `~/.codex/AGENTS.md` 作为全局指令。中文偏好写这里：

```markdown
# 语言规则
- 始终用中文回复
- 说人话，别"首先/其次"
- 短句、直接、不啰嗦
```

**注意**：AGENTS.md 是 Codex 桌面特有的，CLI 版不读这个文件。

### 16.4 auth.json 密钥存储

Codex 桌面的 API key 存在 `~/.codex/auth.json`，格式：
```json
{"OPENAI_API_KEY": "ark-xxx..."}
```
即使 config.toml 里没写 `env_key`，Codex 桌面也会从 auth.json 读 `OPENAI_API_KEY`。

- 老大说"装 X"就盲装同名包 → **先问 GUI 还是 CLI**
- 信官网首页的"免费下载"按钮跳到的就是能装的版本 → **点进去看 Assets**
- 官方文档说"支持 Windows"就以为有 Windows 包 → **必须亲眼看 Assets**
- `curl -L` GitHub Releases 失败时反复重试 → **切 .url 桌面快捷方式**
- 装错版本不立刻卸干净(残留 ccs / cc-switch 别名入口) → **`npm uninstall` 后手动清 npm 全局 bin 目录残留**
- 接 Codex 0.138+ 时把 key 写进 `OPENAI_API_KEY` env 槽 → 跟未来接 OpenAI 官方冲突,**用专用名 `MINIMAX_API_KEY`**

## 17. 🆕 配套资源(2026-06 更新)

- `references/codex-cli-config.md` — Codex **0.42** 完整配置指南(config.toml 格式 / 5 家预设 / bash→PS `$null` 陷阱 / 验收故障矩阵 / **GUI 桌面启动 / execute_code npm 坑 / set 占位符陷阱**)
- `references/provider-dns-checklist.md` — 11 家主流 LLM 平台域名+API 端点速查 + 反例域名清单 + 拼写错自检
- `references/ai-cli-manager-tools.md` — 第三方 CLI 管理工具(CC-Switch / cline-switch / 各种 *switch)选型速查:UI vs CLI 区分 + GitHub Releases 资产核验
- `templates/codex-config.toml` — Codex **0.42** 接任意 OpenAI 兼容中转的最小 config(**顶层 model 字符串,改 base_url + env_key 即可,GUI 段保留指引**)
- `templates/codex-exec-verify.bat` — Windows 端 codex 4 步验收(版本→key 校验→DNS 验→exec 最小对话),**用 `if not defined` 不污染 env**
- `templates/claude-code-env.bat` — Windows 端 4 项 env 占位符模板,老大自己填 Key 双击即生效
- `scripts/verify-claude.sh` — 装机 4 步验收脚本(Node 版本 / 可执行 / 版本号 / 最小对话)

## 12. 🆕 Codex CLI 0.138+ 关键差异(2026-06-09 实测踩坑)

**Codex 跟 Claude Code 走的不是同一条路**,这一节单独点出:

1. **配置入口不同** — Codex 走 `~/.codex/config.toml`,**不**走 env 套娃
2. **provider 必须显式写 TOML 块** — `[model_providers.<key>]` + `env_key` 字段引用环境变量
3. **`wire_api = "chat"`** 必写 — 中转站用 OpenAI Chat Completions 协议,新协议 `responses` 中转站不实现
4. **`requires_openai_auth = false`** 必写 — 中转站跳过 OpenAI 官方登录
5. **Key 隔离硬规则** — Codex 默认读 `OPENAI_API_KEY`,但接中转时**必须**改用专用名(`MINIMAX_API_KEY` 等),避免污染
6. **bash → PowerShell `$null` 陷阱** — git-bash 调 PS 设/清 env 时,`$null` 被 bash 提前吃掉导致 PS ParserError。**正确**:用 `[NullString]::Value` 或 heredoc(`powershell << 'EOF'`)
7. **User 级 env 必须新开终端生效** — codex 启动时从 `process.env` 读,旧终端看不到新值

完整实战见 `references/codex-cli-config.md`,配置模板见 `templates/codex-config.toml`。
