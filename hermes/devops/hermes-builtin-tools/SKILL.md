---
name: hermes-builtin-tools
description: 给老大提供"某种界面"或"某种交互方式"时,优先扫一下 Hermes 内置有没有 — `hermes dashboard`(本地 Web UI 9119 端口)、`hermes chat --tui`(现代 TUI)、`hermes portal`(云端登录)、`hermes gateway`(飞书/微信消息网关)等。避免老大每次说"弄个 UI"都让小弟去 GitHub 找。Use when 老大说 "想给你弄个 UI / 弄个聊天界面 / 在浏览器里能用吗 / 怎么操作你 / 给你弄个前端 / 部署一个面板",或 `hermes --help` 出现多个看似都跟界面相关的子命令时。
---

# Hermes 内置工具速查（class-level skill）

**核心教训(2026-06-13 实测)**:老大说"想给你弄个 UI 你去 GitHub 找一个"→ 小弟差点上 GitHub 翻 Open WebUI / LobeChat。**先 `hermes --help` + 扫本会话结果,内置就够,省得折腾**。

## 1. 4 个常被混淆的"看起来都跟 UI 相关"子命令

| 子命令 | 真实功能 | 何时用 | 何时**别**用 |
|---|---|---|---|
| `hermes dashboard` | **本地 Web UI**(管 config / API key / sessions) | 老大要在浏览器里看/改小弟的配置、调 session、看 API key | 老大要聊天界面(这是**管理界面**,不是聊天界面) |
| `hermes chat --tui` | **现代 TUI**(终端里带高亮/分屏的 chat) | 老大想升级 CLI 体验(默认是 classic REPL `--cli`),装 iTerm/WezTerm 体验更好 | 老大非要在浏览器里聊 → 用 `dashboard` 的 sessions 页面或走 `Open WebUI` |
| `hermes portal` | **Nous Portal 云端登录**(OAuth,绑订阅) | 老大想用 Nous 订阅、配置 Tool Gateway | 老大说"本地 UI" → 用 `dashboard` |
| `hermes gateway` | **消息网关**(飞书/微信/Telegram/Discord 接入) | 老大要把小弟接进飞书群、微信 | 老大要 Web 界面 → 用 `dashboard` |

**判定流程**(老大说"弄个 UI / 弄个前端 / 浏览器能用吗"时):

```
[1] 老大说"浏览器 / Web / 面板" → 90% 是 hermes dashboard(本地 9119)
[2] 老大说"飞书 / 微信 / 群里" → hermes gateway
[3] 老大说"终端好看点 / 升级 TUI" → hermes chat --tui
[4] 老大说"登录 / 订阅 / Portal" → hermes portal
[5] 都不沾,老大要"聊天 Web 界面" / "LobeChat 风格" → 再去 GitHub 找
```

**反模式(本会话栽过)**:直接跳去 GitHub 找"聊天 UI" → 浪费老大 1 轮 + 装一个 500MB+ 的 Node 应用 → 实则 `hermes dashboard` 5 秒就起来。

**重要边界(2026-06-13 实测)**:老大说"弄个 UI 你去 GitHub 找一个"→ 先 `clarify` 给 3 个 class 选项(Hermes 内置 / GitHub 第三方 / 自己写一个)。老大常要"自己写" → 见 §9 写自定义桌面 UI 模板,别再去 GitHub 翻。

## 2. hermes dashboard 实操模板

```bash
# 启动(后台,长生命周期,永不退出)
hermes dashboard --host 127.0.0.1 --port 9119 --skip-build &

# 健康检查
curl -sS -o /dev/null -w "HTTP %{http_code}\n" --max-time 5 http://127.0.0.1:9119/

# 关停
hermes dashboard --stop

# 状态
hermes dashboard --status
```

**关键参数**:
- `--host 127.0.0.1`(默认):**只本机能访问**,安全
- `--host 0.0.0.0 --insecure`:**局域网/远程可访问**,**会暴露 API key 到网络,谨慎**
- `--port 9119`(默认)
- `--skip-build`:dist 已编过(在 `hermes_cli/web_dist/`),跳过 5.7s 重编秒起
- `--no-open`:不自动弹浏览器(适合跑远程开发机)

**首次启动会触发**:`tsc -b && vite build`(~5.7s,2306 modules),**前台跑一次让 dist 落地**,之后 `--skip-build` 秒起。

**后台启动必须用 `background=true`**(本会话栽过):shell 层 `&` 会被 hermes 判定"foreground 用 backgrounding"拒跑。

**dist 路径**:`%LOCALAPPDATA%\hermes\hermes-agent\hermes_cli\web_dist\`,含 `index.html` + `assets/` + `fonts*` + `favicon.ico`。

**典型用法**(给老大):
- 看/改 API Key、Provider、Model
- 翻历史 Session、看 tool 调用
- 设 cron / 看 cron 状态
- 调 Skills / Plugins

**注意**:`hermes dashboard --status` 有缓存延迟(进程死了报"无进程"或"在跑"都可能错位)→ **以 `curl 127.0.0.1:9119/` 实测 HTTP 200 为准**。

## 3. hermes chat --tui 实操模板

```bash
# 启动现代 TUI
hermes chat --tui

# 开发模式(tsx,不编 dist)
hermes --tui --dev

# 单次查询(-q)
hermes chat -q "今天的 A 股选股结果呢"
```

`hermes` 不带子命令默认 = `hermes chat`(进 classic REPL)。要现代 TUI 必须显式 `--tui` 或 `hermes --tui`。

`display.interface: tui` 写在 `~/.hermes/config.yaml` 可**永久**把默认切成 TUI。

## 4. hermes portal 实操模板

```bash
# 一键登录 + 配 Nous provider
hermes portal              # 等价 hermes setup --portal
hermes portal info         # 看当前 Portal 状态 + Tool Gateway 路由
hermes portal open         # 浏览器打开订阅页
hermes portal tools        # 列 Tool Gateway 路由了哪些 tool
```

**Portal ≠ 本地 UI** — 老大如果说"弄个本地 UI"但你跑去搞 portal,会被骂。

## 5. hermes gateway 实操模板

```bash
# 跑前台(WSL / Docker / Termux 推荐)
hermes gateway run

# 装成 systemd / launchd 后台服务
hermes gateway install
hermes gateway start
hermes gateway status

# 配消息平台
hermes gateway setup
```

**和 dashboard 不冲突** — gateway 是把小弟接进飞书群/微信,dashboard 是本地浏览器面板,两者可同时跑。

## 6. 触发这个 skill 的场景

- "弄个 UI / 弄个前端 / 浏览器能聊吗 / 给我弄个面板"
- "在终端里升级一下 / TUI 太丑"
- "接飞书 / 接微信 / 接 Telegram"
- "你看起来很复杂,怎么操作你"
- "想看你历史记录 / 看 config / 改 key"

## 7. 反模式

- ❌ 老大说"弄个 UI"立刻 `git clone open-webui` → 装 1GB + 5 分钟 + 还要配 base URL → `hermes dashboard` 5 秒搞定
- ❌ 老大说"在浏览器里用"立刻 `npm i -g lobe-chat` → 同上
- ❌ 把 `hermes portal`(云端登录)当本地 UI 推 → 老大要的是本地
- ❌ 把 `hermes dashboard` 当聊天 UI 推 → 这是**管理面板**,要聊天是 `hermes chat --tui` 或 LobeChat 类
- ❌ 启动 dashboard 用 shell `&` backgrounding → 改 `terminal(background=true)`

## 8. 配套资源

- `references/hermes-commands-cheatsheet.md`(待建):`hermes --help` 全子命令 1 页速查
- `templates/electron-hub/`(已就绪):可复用的 Electron 桌面 APP 脚手架(main.js + preload.js + index.html),改 base_url 和 model 名即可用

## 9. 写自定义桌面 UI(当 built-in 不够时)

**适用场景**(老大挑"自己写一个"时):
- 想要**真正的 .exe** 装到桌面/启动器(不只是浏览器面板)
- 想要**常驻系统托盘**(关窗 = 缩托盘)
- 想要**汉化 + 自定义主题**(内置 dashboard 是英文)
- 想要打包成 NSIS 安装器给其它机器用

**3 步法**:

```
[1] 脚手架:抄 templates/electron-hub/ → 改 base_url/model/key 走 minimax 中转
[2] 装依赖:npm install(注意 §10 的 Windows git-bash 坑)
[3] 跑:npm run dev 开发 / npm run build 出 .exe
```

**关键设计决定**(**本会话栽过**):

```
A. Electron 自己起 hermes dashboard 子进程(spawn 在 main.js)
   - 优:打包成 .exe 后,用户双击就用,不用预先装 hermes
   - 劣:会跟用户自己终端起的 dashboard 抢 9119 端口 → 内存翻倍
B. Electron 只连外部 dashboard,不 spawn
   - 优:不冲突,共享 9119
   - 劣:用户得自己先 `hermes dashboard` 起来,Electron 只是个壳
```

**推荐 A**(单机独立分发场景),但要:
- spawn 前 `curl 127.0.0.1:9119/` 先 ping 一下,有就复用 + 跳过 spawn
- spawn 时带 env `{...process.env, MINIMAX_API_KEY: ...}` 透传 key(否则 401)

**main.js 模板关键片段**(完整见 `templates/electron-hub/main.js`):

```js
// 自动起 dashboard(冲突检测 + 透传 key)
async function ensureDashboard() {
  try {
    const r = await fetch('http://127.0.0.1:9119/');
    if (r.ok) return;  // 已有,复用
  } catch {}
  spawn('hermes', ['dashboard', '--skip-build', '--host', '127.0.0.1', '--port', '9119'], {
    env: { ...process.env, MINIMAX_API_KEY: process.env.MINIMAX_API_KEY || '' },
    windowsHide: true
  });
  await new Promise(r => setTimeout(r, 3000));  // 等服务起来
}

// IPC:渲染进程调 /v1/chat/completions 走 OpenAI 兼容协议
ipcMain.handle('chat', async (_, { messages, model }) => {
  const resp = await fetch('http://127.0.0.1:9119/v1/chat/completions', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${process.env.MINIMAX_API_KEY}`
    },
    body: JSON.stringify({ model: model || 'MiniMax-M3', messages, stream: false })
  });
  return resp.json();
});
```

**反模式**(本会话栽过):
- ❌ Electron 自己起 dashboard + 用户终端已经起了 → 9119 端口冲突,内存翻倍 → 必须先 ping 再 spawn
- ❌ spawn 不透传 MINIMAX_API_KEY → 渲染进程 IPC 拿到 401 → spawn 时 **必须** 把 env 传过去
- ❌ 不写托盘逻辑,关窗 = 退出 → 老大预期"常驻托盘" → 加 `win.on('close', e => { e.preventDefault(); win.hide(); })` + Tray
- ❌ 前台跑 `hermes dashboard` 编译 + 后台拉 `electron .` → npm install 在 Electron 那边超时 → 见 §10
- ❌ 用最新 codex 0.138+ 想接 minimax 中转 → 必败(0.43+ 不再支持 `wire_api=chat`),`devops/llm-cli-setup` §8 有完整说明
