---
name: codex-config-repair
description: 修复被 CC Switch 改坏的 Codex config.toml（ChatGPT 报「无法加载 config.toml：Model provider X not found」）。触发条件：ChatGPT/Codex 报 config.toml 加载失败、provider not found、codex 掉线重连/卡死/内存拉满、华哥说"codex 又爆内存/又报错"。一键执行 scripts/fix_codex_config.sh 恢复 ZAI 直连智谱。
---

# Codex config.toml 修复

## 触发条件（症状）

- ChatGPT 桌面版报「无法加载 config.toml：Model provider `ZAI`/`deepseek`/`custom` not found」
- codex 掉线重连、卡死、内存拉满、对话串无法继续
- 华哥说"codex 又爆内存" / "恢复 zai" / "codex 桌面版修复好了告诉我"

## 根因（反复发作的元凶）

CC Switch（`/Applications/CC Switch.app`，华哥登录项，开机自启，常驻监听 `127.0.0.1:15721`）会间歇性改坏 config.toml：

| 字段 | 正确 | 被 CC Switch 改坏成 |
|---|---|---|
| model_provider | `"ZAI"` | `"custom"` |
| [model_providers] | `[model_providers.ZAI]` | `[model_providers.custom]`（或直接删 ZAI 段） |
| base_url | `https://open.bigmodel.cn/api/v1` | `http://127.0.0.1:15721/v1`（代理） |
| 认证 | `experimental_bearer_token = "<真实key>"` | `requires_openai_auth=true` + `"PROXY_MANAGED"` |

## 一键修复

```bash
bash ~/.hermes/skills/autonomous-ai-agents/codex-config-repair/scripts/fix_codex_config.sh
# 可选：带 --test 会顺带 curl 实测 key 是否有效
bash ~/.hermes/skills/autonomous-ai-agents/codex-config-repair/scripts/fix_codex_config.sh --test
```

脚本自动：① 备份 `.bak-时间戳` → ② 从 cc-switch db 读最新智谱 key → ③ 用黄金模板写正确 ZAI 直连结构 → ④ TOML 语法验证 → ⑤（可选）实测 key。

## 正确 ZAI 结构（黄金模板）

```toml
model_provider = "ZAI"
model = "glm-5.3"
model_reasoning_effort = "high"
disable_response_storage = true
wire_api = "responses"
model_catalog_json = "/Users/hua/.codex/models.json"

[model_providers.ZAI]
name = "ZAI"
base_url = "https://open.bigmodel.cn/api/v1"
wire_api = "responses"
experimental_bearer_token = "<key>"   # 智谱 Coding 包月 key，49 位
```

完整模板见 `templates/config.toml.zai`（key 用 `__ZAI_KEY__` 占位符，脚本运行时动态填充）。

## 关键路径

| 项 | 路径 |
|---|---|
| config 主文件 | `~/.codex/config.toml` **与 `~/系统文件夹/Codex/config.toml` 是硬链接（同一 inode），写一个即可** |
| key 来源 | cc-switch db `~/.cc-switch/cc-switch.db` → `providers` 表 `id='glm'` 的 `api_key` 字段 |
| codex CLI | `/Applications/ChatGPT.app/Contents/Resources/codex`（`~/.local/bin/codex` 是断的软链，勿用） |
| 黄金模板 | 本 skill `templates/config.toml.zai` |

## 智谱 key 现状（2026-08-29 实测，会变）

- `93b825...Oivb`（Coding 包月，49 位）→ 之前 401「令牌已过期」，端点 `/api/v1/responses`、`/api/anthropic`、`/api/paas/v4` 全 401
- `2a7c...Whvd`（个人 Pro 包月，49 位）→ 1113「余额不足或无可用资源包」

**修复结构 ≠ 修复 key**：即使 config 结构修好，key 失效仍会 401。修复后必须实测；若 401/1113，需华哥去智谱开放平台（open.bigmodel.cn）核实 Coding 包月续费。

## 坑点

1. **改前必备份** `.bak-时间戳`（脚本已内置）
2. **CC Switch 会反复覆盖**——根治方案 A（停开机自启）已于 2026-08-30 华哥拍板执行：`osascript -e 'tell application "System Events" to delete login item "CC Switch"'`。⚠️ CC Switch 的自启在 macOS「登录项」（System Events 的 login items），**不在 ~/Library/LaunchAgents/ 的 plist 里**（那里查不到）。app 本体保留 `/Applications/CC Switch.app`，华哥手动打开仍可切模型。停自启**不影响同事**——8 个同事 agent（afu/maodou/laomo/heidou/xiaobao/quant/zhenglishi/wangcai）走各自 `~/.hermes/profiles/<名>/config.yaml` 的 MiniMax-M3（minimax-cn），玉芬走 GLM-5.3-flash，均与 CC Switch 无关。若 config 再被改坏，先查华哥是否手动打开过 CC Switch 切了模型（此时需切回 ZAI/glm-5.3），不再默认归咎于自启。
3. **停自启后 config 仍可能被改（2026-08-30 晚复现新变体）**：CC Switch 自启已停、进程未运行时，config.toml 仍被改成 `model_provider="custom"` + `[model_providers.custom] base_url="https://open.bigmodel.cn/api/anthropic"`（anthropic 端点）+ **key 整个丢失**（无 experimental_bearer_token）。此变体元凶疑似 ChatGPT 桌面端自己在「模型切换」时重写 config（非 CC Switch）。遇此变体需从 ChatGPT 桌面端「模型设置」入手根治，而非反复改文件。
3. **两个 config 是硬链接**，别写出两个不同内容
4. **key 在 cc-switch db 里动态读，别硬编码进脚本**（key 会过期/更换）
5. **`requires_openai_auth=true` + `PROXY_MANAGED` 是代理模式的标志**——出现即被 CC Switch 改坏

## 🔌 codex plugin 命令事实（2026-09-14 巡检实测）

- 子命令是 `codex plugin add|list|marketplace|remove`，**没有 `install`/`update`**（巡检 prompt 里写 `codex plugin install {name}` 会直接失败）。
- `$HOME` 被 cron 劫持时 `codex` 读不到真实 `~/.codex`（plugin list 输出空），必须 `HOME=/Users/hua codex ...` 或绝对路径。`codex plugin list` 空输出先怀疑 HOME 劫持，别误判为无插件。
- **期望清单里的 `github` 插件在所有 marketplace（openai-api-curated/openai-bundled/openai-primary-runtime）中都不存在**，无法安装；`computer-use` 不是插件而是 `[features] computer_use` 开关（应为 false 防爆内存）。chrome 可从 bundled 装：`codex plugin add chrome@openai-bundled`。
- 当前安装格局（15 个 enabled）：bundled 4（browser/chrome/codex-app-tools/visualize）+ primary-runtime 5（documents/pdf/spreadsheets/presentations/template-creator）+ api-curated 6（superpowers/build-web-apps/coderabbit/figma/linear/sentry）。
- sentry/linear/figma 启动时报 MCP `AuthRequired`（OAuth 未登录）属正常噪音，不影响 exec。

## 🔑 key/model 现状更新（2026-09-14 实测）

- config 里 `model = "glm-5.3-flash"` 和 `-m glm-5.3` **都能跑通**（flash: 14,621 tokens；glm-5.3: 18,748 tokens）——旧的「flash 无权限 model_access_denied」结论已过时。巡检标准要求 glm-5.3 时直接改 `model = "glm-5.3"` 即可，改前备份 `.bak-日期`，用 Python `open(path,'w')` 原地写保硬链接。
- codex CLI 版本以 ChatGPT.app 内置为准（`/Applications/ChatGPT.app/Contents/Resources/codex --version`，当前 0.148.0-alpha.15）；npm standalone 最新 0.154.0 但**不要单独升级**，ChatGPT.app 自管。
- skills 太多会触发 `Exceeded skills context budget` 警告并剥掉全部 skill 描述——是装 skill 过多的信号，不是 config 损坏。

## 修复后：同步另外两处配置描述（2026-08-30 发现）

修好 config.toml 只是第一步。还有两处「配置描述」会跟着过时，不改的话进化巡检会按旧配置误报：

1. **AGENTS.md 的「当前配置」段** — `~/系统文件夹/Codex/AGENTS.md` 与 `~/.codex/AGENTS.md` **也是硬链接（同一 inode）**。「模型/Provider/备用Provider/可用工具」经常还写着上一次的 deepseek / 18888。修 config 后必须同步改这里，否则 Codex 每次启动读到的自我描述是错的。
2. **cron 进化任务的 prompt** — `Codex 技能与插件进化`（cron id `5e4d0547db3d`，每周一 9:00）的「### 2. 配置验证」步骤里写死了 provider/model/base_url。用 `cronjob action=update`（传 job_id + 完整新 prompt）同步，**不要直接改 jobs.json**。

**改硬链接文件的坑**：用 Python `open(path,'w')` 原地写才能保持 inode（两个路径同步更新）；用 `patch`/`write_file` 工具会重写文件、**break 硬链接**，导致两个路径内容分叉。改完 `ls -li` 核对两个路径 inode 是否仍相同。

**同步检查命令**（改完跑一遍，应无残留）：
```bash
grep -rn "deepseek\|18888\|api.deepseek" ~/系统文件夹/Codex/AGENTS.md ~/.hermes/cron/jobs.json
```

## 验证清单（修完必做）

- [ ] `python3 -c "import tomllib; tomllib.load(open('~/.codex/config.toml','rb'))"` 语法过
- [ ] grep 确认 `model_provider = "ZAI"` 且 `[model_providers.ZAI]` 存在
- [ ] `curl https://open.bigmodel.cn/api/v1/responses` 用 key 实测，返回非 401/1113
- [ ] 更轻量的 key 有效性验证：`curl https://open.bigmodel.cn/api/v1/models -H "Authorization: Bearer <key>"` 返回模型列表（含 glm-5.3）= key 有效
- [ ] 华哥重新打开 ChatGPT 对话串，发一条消息全链路通

## 停电/重启后完整修复序列（2026-08-30 停电复现验证）

停电非正常关机 → CC Switch 开机自启改坏 config → ChatGPT 主进程崩溃 → 留孤儿 crashpad_handler。按此顺序修：

1. **诊断**：`grep -nE "^model_provider|\[model_providers" ~/系统文件夹/Codex/config.toml`（确认是否被改成 custom）；`pgrep -fl "ChatGPT.app/Contents/MacOS/ChatGPT"`（主进程是否已崩溃）
2. **恢复 config**（两条路选一）：
   - 快速：`grep -l "model_providers.ZAI\|bigmodel" ~/.codex/config.toml.bak-*` 找最新含 ZAI 段的备份，用 Python `open(path,'w')` 原地写回（保持硬链接，见上文硬链接坑）。比跑脚本快，且 key 直接从备份来、无需重读 cc-switch db。
   - 标准：`bash .../scripts/fix_codex_config.sh`（从 cc-switch db 读 key 重建）
3. **清僵尸 crashpad_handler**：主进程崩溃后 `browser_crashpad_handler` 变孤儿（PPID=1），先 `ps -o pid,ppid,command -p <pid>` 确认 PPID=1 再 `kill`。⚠️ 主进程还活着时 crashpad_handler 是它的崩溃监听，别杀。
4. **重启桌面端**：`open -a ChatGPT`
5. **验证**：`ps aux | grep "ChatGPT.app/Contents/MacOS/ChatGPT"` 看 RSS——**稳定 ~440-460MB = 正常**；暴涨到 GB 级 = OOM 循环又起（computer_use 没禁用，或 key 又失效导致 codex 反复重试卡死）。

codex 卡死/内存拉满的另一诱因 = 上游 key 失效 → codex 反复重试 → 卡死。修好 key 后内存自然恢复。

## 🔍 Codex "stream disconnected" 不一定是协议问题（2026-08-31 实测）

Codex 报 "stream disconnected before completion: stream closed before response.completed" 时，**多半不是 SSE 协议问题，而是智谱"假成功"鉴权失败的翻译**：

- 智谱对**完全鉴权失败**的 key 返回 HTTP 200 + body `{"code":1000, "msg":"身份验证失败。", "success":false}`
- Codex 客户端拿到这种"伪200"响应，会在流第一帧被服务端拒收，然后翻译成"stream disconnected"
- **不要**直接假设是流式协议 bug，先做 key 鉴权诊断

**多端点三角验证模板** + 判读表 + Key 长度 sanity check：见 `references/***SECRET***.md`。5 端点（`/api/v1/responses` / `/api/v1/chat/completions` / `/api/paas/v4/chat/completions` / `api.z.ai/api/paas/v4/chat/completions` / `GET /api/v1/models`）全部返 1000 = key 完全无效（账号欠费/错key/未激活），让华哥去智谱后台核对；如果长度只有 20 字符（标准 35）= 剪贴板截断，让华哥 `pbpaste | wc -c` 复测。

## 🛡️ 守护脚本过激熔断陷阱（2026-08-31 实测）

`codex_memory_guard.py`（每2分钟 cron `5d9df933677d`，守护 `computer_use` 配置防爆内存）自带的熔断逻辑：

```python
THREAD_THRESHOLD = 200  # 旧阈值——误杀
RSS_THRESHOLD_MB = 4096

# 任一超阈 → pkill -9 杀掉 ChatGPT.app 主进程 + Codex Framework
```

**坑**：正常 ChatGPT.app 26.814 版本主进程稳定在 **60-220 线程 / 200-500MB RSS**（macOS 自带内存压缩会触发 V8 worker 拉线程），旧阈值 200 把"健康但线程数高"的进程当病态熔断 → 主进程被杀 → ChatGPT 端 Codex CLI 立刻断流。

**已修（2026-08-31）**：阈值调到 400 线程 / 6GB RSS，且验证脚本静默退出=健康。

**复盘三步骤**（华哥指令"修复 codex 爆内存 bug"后必跑）：
1. **先看是否真爆内存**（不要无脑跑守护脚本）：
   ```bash
   pid=$(pgrep -f 'ChatGPT.app/Contents/MacOS/ChatGPT' | head -1)
   ps -o rss= -p $pid  # 单位 KB，正常 200000-500000 (200-500MB)
   ps -M $pid | grep -c '^'  # 线程数，正常 60-220
   ps aux | grep -iE 'ChatGPT|SkyComputerUse' | grep -v grep | wc -l  # 进程总数，>50 才可疑
   ```
2. **真爆内存特征**（>4GB RSS 或 >400 线程 或 >50 个 SkyComputerUseService 僵尸）：
   - 检查 `[features] computer_use = false` 是否被 ChatGPT 重写覆盖（守护会补回）
   - 检查 CUAService.plist 是否异常大（>10KB 可疑，正常 162 字节）
   - pkill 僵尸后重启：`pkill -9 -f SkyComputerUseService; open -a ChatGPT`
3. **不爆内存但守护误杀**（华哥复现）：把阈值调高 + 重启 ChatGPT

**调阈值的正确姿势**（华哥 8/31 反馈后再修改）：
```python
# ~/.hermes/scripts/codex_memory_guard.py 第 26-28 行
THREAD_THRESHOLD = 400    # 60-220 健康；>400 才病态（ChatGPT.app 26.814 实测）
RSS_THRESHOLD_MB = 6144   # 正常 200-500MB；爆内存 >4GB 才熔断
```

**避免再次误杀**：跑 `python3 ~/.hermes/scripts/codex_memory_guard.py` 后**立刻**验证主进程存活——`pgrep -fl ChatGPT.app/Contents/MacOS/ChatGPT`，若有输出 = 健康；无输出 = 守护误杀，需 `open -a ChatGPT` 重启。

**长期守卫生效**：cron `5d9df933677d` 当前**停用中**（pgrep 查不到进程）。华哥 8/31 反馈"修复 bug"后已恢复阈值但 cron 仍暂停。**恢复 cron 时必须先验证阈值生效**：
```bash
hermes cron resume 5d9df933677d  # 或 cronjob action=resume job_id=5d9df933677d
# 等 2 分钟观察一次，确认守护静默退出
tail -5 ~/.hermes/logs/codex_memory_guard.log  # 若有 "Codex守护: ..." 输出 = 有动作；空 = 静默=健康
```
