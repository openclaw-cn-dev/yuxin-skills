# 第三方 AI CLI 管理工具选型速查

处理"装个 cc switch / cline switch / model switch / 各种 *switch"这类请求时使用。npm 上带 "switch/manager" 关键词的包经常 5+ 个并存，且**没有官方命名约定**——必须先分清 UI 桌面 vs CLI 终端。

## 1. 先判定：UI 桌面 vs CLI 终端

**老大说"装 X switch"时主动问一句**："您要的是 Windows 桌面那种带图标的 GUI，还是命令行菜单版？"——3 秒的事，避免来回装卸。

UI 桌面的常见信号词：UI / 桌面 / GUI / 界面 / 可视化 / 图标 / 双击打开
CLI 终端的常见信号词：CLI / 终端 / 命令行 / 脚本 / 批处理（不加"UI"修饰）

## 2. CLI 终端版候选（npm 全局安装）

| 包名 | 维护者 | 干啥 | npm |
|---|---|---|---|
| `@kaitranntt/ccs` | kaitranntt | Claude/GLM/Kimi 多 profile 切换 | `npm i -g @kaitranntt/ccs` |
| `@sirtheo/claude-switch` | sirtheo | 多账号 + Max/Pro 限速绕过 | `npm i -g @sirtheo/claude-switch` |
| `claude-config-switch` | mwq30123 | 中文社区纯配置切换（带 ccs / cc-switch 两个 bin 别名） | `npm i -g claude-config-switch` |
| `claude-code-provider-switch` | - | 跨平台 provider 切换 | `npm i -g claude-code-provider-switch` |

**核验 CLI 包的标准动作**：

```bash
# 1) 看 bin 字段有几个（多个 = 有 alias，别只看主名）
npm view <pkg> bin
# 例：claude-config-switch 装出来 ccs + cc-switch + claude-config-switch 三个命令

# 2) 看描述里有 "TUI"/"inquirer" 还是 "GUI"/"electron"/"tauri"
npm view <pkg> description keywords

# 3) 卸干净 = npm uninstall + 手清残留
npm uninstall -g <pkg>
rm -f /c/Users/Administrator/AppData/Roaming/npm/<bin-name>
rm -f /c/Users/Administrator/AppData/Roaming/npm/<bin-name>.cmd
rm -f /c/Users/Administrator/AppData/Roaming/npm/<bin-name>.ps1
ls /c/Users/Administrator/AppData/Roaming/npm/node_modules/ | grep <pkg>
```

## 3. UI 桌面版候选（GitHub Releases 下载安装包）

**当前最热**（截至 2026-06）：`farion1231/cc-switch`（92.4k+ stars，Tauri 2 + Rust + React，国内 ccswitch.io 是官网）

**桌面 GUI 工具的标准核验流程**（**这是装这类的最大坑**）：

```bash
# Step 1: 官网"免费下载"按钮点进去看实际跳哪个 Release
# 用 browser 工具点，看 URL 落到哪
# 例：ccswitch.io 跳到 github.com/farion1231/cc-switch/releases/tag/v3.16.1

# Step 2: 在该 Release 页验证 Assets 列表
# 用 browser_console 跑：
# Array.from(document.querySelectorAll('a[href*="releases/download"]')).map(a => a.href)
# 看有没有 .msi / .exe / -Windows-*.zip

# Step 3: 没有就翻历史 Release
# https://github.com/<owner>/<repo>/releases?page=N
# 直到找到最后一版带目标平台包
# 注意 changelog 有没有 "修复 Windows 窗口" / "fix Windows build" 字样
```

**已知坑**（CC-Switch 实锤案例）：

- 官网"免费下载"按钮跳到最新 v3.16.1，**v3.16.1 没有 Windows 安装包**
- 翻 v3.16.0、v3.15.0 也都没有
- 翻到 v3.9.0（2026-01-08）才有 `CC-Switch-v3.9.0-Windows.msi` 和 `-Windows-Portable.zip`
- 官网"安装指南"明确写支持 Windows 10+，**但实际没 Assets**
- **结论**：v3.16.x 系列可能 Windows CI 流水线坏了，得等官方修

**给老大交付时必须讲清的两件事**：

1. **功能落后 N 个月**——v3.9.0 比 v3.16.1 落后 5 个月
2. **缺失的主要功能清单**——按 changelog 列出老大用不上的

## 4. curl 拉 GitHub Releases 不通的兜底

本机 terminal 跑 `curl -L https://github.com/.../releases/download/...` 经常返回：

```
curl: (52) Empty reply from server
HTTP=000 SIZE=0
```

不是用户确认/管理员权限那个卡顿问题，是**网络层拦截**。

**兜底方案：写 .url 桌面快捷方式**

```ini
[InternetShortcut]
URL=https://github.com/<owner>/<repo>/releases/download/<tag>/<asset>
```

存到 `C:\Users\Administrator\Desktop\`，Windows 双击用默认浏览器/IDM/迅雷下。比 curl 稳得多。

**配套说明文件**（可选）：`.bat` 列出下载链接 + 步骤，` .txt ` 写完整背景说明。

## 5. GitHub Releases 资产列表的"作弊 URL"

不用一页页翻 Release，直接 GET 这个 URL 拿到该 tag 的所有 assets 链接（**返回纯文本 HTML，无 JS 渲染**）：

```
https://github.com/<owner>/<repo>/releases/expanded_assets/<tag>
```

例：`https://github.com/farion1231/cc-switch/releases/expanded_assets/v3.9.0` 直接列出 14 个 assets（Linux/macOS/Windows/Source code）。

比 `releases/tag/<tag>` 页面简单——后者渲染慢、可能触发 GitHub 登录墙。

## 6. 完整桌面 GUI 工具装机模板（CC-Switch 模式）

```bash
# 1) 准备目录
mkdir -p /c/<ToolName>

# 2) 写 .url 快捷方式（curl 兜底）
cat > /c/Users/Administrator/Desktop/下载<ToolName>.url << 'EOF'
[InternetShortcut]
URL=<真实下载链接>
EOF

# 3) 写说明文件
cat > /c/Users/Administrator/Desktop/<ToolName>下载说明.txt << 'EOF'
<完整说明>
EOF

# 4) 验收
ls -la /c/Users/Administrator/Desktop/ | grep -iE "<toolname>"
```

然后等老大双击 .url 浏览器下完，再走解压 / 启动流程。

## 7. 触发这个 reference 的场景

- "装个 cc switch / cline switch / 装 model manager"
- "有 UI 版吗" / "要桌面那种"
- "Claude Code 怎么切换多个 API"（不是写 env，是 GUI 切换）
- "官网点了免费下载但没看到 Windows 包"
- "curl 下 GitHub 文件下不动"
