---
name: chrome-helper-guard
version: 1.0.0
description: "Google Chrome Helper 子进程治理：定时检查并清理 agent-browser 自动化遗留的无头 Chrome 会话，保留当前活动会话与用户正常 Chrome，避免 helper 数量失控导致页面崩溃/爆内存。当用户提到 Chrome Helper 太多、内存高、浏览器卡顿、自动化浏览器残留、agent-browser 会话清理，或需要查看/安装/调整清理守护时使用。支持 macOS launchd 每 10 分钟自动运行。"
metadata:
  requires:
    bins: ["node", "ps", "launchctl"]
  platforms: ["darwin"]
---

# Google Chrome Helper Guard

## 这个技能解决什么

Mac 上「Google Chrome Helper」是 Chrome 多进程架构的正常子进程（Renderer 渲染进程、GPU、网络/存储 Utility 等），**不是病毒**。
数量异常常见原因：标签页/扩展多 + **AI 自动化（agent-browser）每次验收启动的无头 Chrome 会话没有关闭**。
本技能用 `~/.local/bin/chrome-helper-guard.mjs` 定时清理这些自动化遗留会话，**不触碰用户正常 Chrome**。

## 安全边界（必须遵守）

1. 只识别同时满足：Chrome 主进程（`/Applications/Google Chrome.app/Contents/MacOS/Google Chrome`）+ `--headless=new` + `--remote-debugging-port=` + `--user-data-dir=*/agent-browser-chrome-*`。
2. 用户正常 Chrome（含标签页/扩展/Helper）**永不发信号**；若用户说“关掉没用的标签页”也只能给建议，不自动操作其浏览器。
3. 当前活动会话由 `~/.agent-browser/*.pid` 指向的 daemon 保护，永不清理；不要手动 kill 活动会话。
4. 删除临时目录仅限 `--user-data-dir` 位于 `/tmp` 或 `/var/folders/...` 且包含 `agent-browser-chrome-`。
5. 不处理 `com.znt.*` 等其他应用服务；本技能只治理 Chrome helper。

## 安装（已在本机安装）

- 脚本：`~/.local/bin/chrome-helper-guard.mjs`（Node ESM，无第三方依赖）
- 定时：`~/Library/LaunchAgents/com.yuxin.chrome-helper-guard.plist`
  - 登录自动加载，`StartInterval=600`（每 10 分钟），`RunAtLoad=true`
  - 日志：`~/Library/Logs/chrome-helper-guard.log`（JSONL，脚本自动轮转 1MB）
- 技能目录：`~/.claude/skills/chrome-helper-guard/`

## 常用命令

```bash
# 只检查、不杀（推荐先看 managed/stale）
node ~/.local/bin/chrome-helper-guard.mjs --dry-run --json

# 手动清理（默认：保留活动会话；清理 >5 分钟未活动的无头会话）
node ~/.local/bin/chrome-helper-guard.mjs

# 查看最近日志
tail -5 ~/Library/Logs/chrome-helper-guard.log

# 立即触发 launchd 一次
launchctl kickstart -k gui/$(id -u)/com.yuxin.chrome-helper-guard

# 暂停 / 恢复定时
launchctl bootout gui/$(id -u)/com.yuxin.chrome-helper-guard
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.yuxin.chrome-helper-guard.plist
```

## 输出解读

- `managed`：识别到的 agent-browser 无头 Chrome 会话；`active=true` 为当前活动会话。
- `stale`：未登记为活动、可清理的会话数。
- `killed`：实际清理的主进程与临时目录。
- `totalChrome` / `helperRssMb`：当前 Chrome 总进程数与 Helper 常驻内存（含用户 Chrome）。
- `errors`：安全跳过或 kill/删除失败信息；有错误时先看日志，不要强行 kill。

## 推荐工作流（AI/QA 每轮结束时）

1. 先 `--dry-run --json`，确认 `managed` 中当前会话 `active=true`，且没有误识别用户 Chrome。
2. 再直接运行清理（无需参数）。
3. 若 `stale=0` 且 `errors=[]`，说明本轮没有泄漏；若 `killed` 非空，说明已回收。
4. 永远不要用 `pkill -f "Google Chrome Helper"` 这类全局命令；会误杀用户浏览器，导致页面崩溃。

## 排障

- launchd 没跑：`launchctl print gui/$(id -u)/com.yuxin.chrome-helper-guard | head -40`；看 `state`、`last exit code`、日志。
- 脚本报 `another instance is running`：说明上一轮未结束（锁文件 `~/.cache/chrome-helper-guard/lock`）；等下次或确认无进程后删锁。
- 误识别/漏识别：用 `ps -axo pid,ppid,command | grep agent-browser-chrome` 核对命令行；不要改造成更宽泛的匹配。
- 用户 Chrome helper 仍然多：这是正常浏览器进程；建议关闭不用标签页、审查扩展，不做自动 kill。
