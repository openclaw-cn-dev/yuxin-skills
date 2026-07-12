# Codex 项目级指令

## 通用规范

- **语言**：中文为主，代码注释用英文
- **编码风格**：遵循项目现有风格，不引入新范式
- **测试**：关键功能必须写测试，测试通过后再提交
- **提交**：每次提交一个原子变更，提交信息用英文，遵循 Conventional Commits
- **沙箱**：默认使用 `--full-auto` 模式，文件变更自动审批

## 编码原则

1. **先理解再动手** — 修改前先阅读相关代码，理解上下文
2. **最小变更** — 只改需要改的地方，不顺手重构无关代码
3. **防御性编程** — 边界检查、错误处理、日志记录
4. **性能意识** — 避免不必要的 I/O、内存分配、网络请求
5. **安全第一** — 不硬编码密钥，使用环境变量或密钥管理服务

## 项目结构

- `~/hermes/` — Hermes Agent 配置和技能
- `~/6-产品研发/` — 公司产品研发项目
- `~/codex-workspace/` — Codex 工作区（临时克隆用）

## 可用工具

- **GitHub CLI** (`gh`) — PR 创建、审查、合并
- **Computer Use** — macOS 桌面自动化
- **Browser** — 浏览器自动化（Playwright）
- **LLM Gateway** (`127.0.0.1:18888`) → DeepSeek V4 Pro（玉芬维护）

## 插件（共 15 个）

已安装插件：
- **代码类**：build-web-apps, coderabbit, superpowers
- **设计类**：figma
- **协作类**：github, linear, sentry
- **桌面类**：browser, computer-use, visualize
- **文档类**：documents, pdf, spreadsheets, presentations, template-creator
- **未装**：chrome（需要桌面 Chrome）

## 模型

- **当前**：`deepseek-v4-pro`（via 本地 Gateway `127.0.0.1:18888`）
- provider: custom，wire_api: responses
- 备用：火山引擎 Agent Plan（套餐限额，7/13 重置后可用）
