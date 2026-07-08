---
name: codex-cli-template
description: Codex CLI 新建智能体模板 — AGENTS.md 配置指南
version: 2.0.0
tags: [template, onboarding, codex, CLI]
---

# Codex CLI 智能体模板

## 使用场景
当需要在 Windows/macOS 上为 Codex CLI 配置新的智能体角色时使用。
Codex CLI 是旺财的"编程大脑"——生成 CadQuery/SolidWorks 脚本、自媒体文案模板等。

## 模板文件

```
agents/codex/<name>/
└── AGENTS.md      # Codex CLI 角色定义
```

## Step 1: 确定角色

Codex CLI 的角色是**编程引擎**，不是调度器。
- Hermes Agent 负责: 调度、飞书交互、浏览器操作、任务管理
- Codex CLI 负责: **生成高质量代码**（Python/CadQuery/SolidWorks COM/文案模板）

## Step 2: 创建 AGENTS.md

```markdown
# <名字> — 渔芯 <角色>
# 复制到 ~/.codex/AGENTS.md

## 核心能力
- **<能力1>**: <详细描述>
- **<能力2>**: <详细描述>
- **<能力3>**: <详细描述>

## Codex CLI 角色
- 你是 <名字> 的"编程大脑"
- <Hermes Agent名> 负责调度、飞书交互、浏览器操作
- 你负责生成 **高质量代码**（<代码类型>）
- 生成代码后写入文件，<Hermes Agent名> 负责执行

## 工具链
- Python 3.11+
- <Python库1>
- <Python库2>
- <COM API> (Windows only)
- Hermes browser tools (browser_navigate/click/type/snapshot/vision)

## 文件结构
```
~/.hermes/profiles/<profile名>/
├── memories/MEMORY.md     # L1 记忆 (自动注入)
├── config.yaml            # Hermes 配置
└── config/
    └── skills/

~/<workspace>/
├── <输出目录1>/
├── <输出目录2>/
└── evolution/             # 自我进化
```

## 参考技能
- <技能1>: <描述>（GitHub 仓库）
- <技能2>: <描述>
```

## Step 3: 配置 Codex CLI

```bash
# 1. 安装 Codex CLI
npm install -g @openai/codex

# 2. 登录
codex auth login

# 3. 配置 AGENTS.md
cp AGENTS.md ~/.codex/AGENTS.md

# 4. 验证
codex --version
```
