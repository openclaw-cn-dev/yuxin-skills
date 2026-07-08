---
name: claude-code-template
description: Claude Code 智能体模板 — 高级编程辅助配置
version: 2.0.0
tags: [template, onboarding, claude, code]
---

# Claude Code 智能体模板

## 使用场景
当需要 Claude Code 作为高级编程引擎（复杂重构、架构决策、跨文件修改）时使用。
玉芬使用 Claude Code 辅助编程。

## 角色定位
Claude Code 是**高级编程辅助**，不是调度器。
- Hermes Agent 负责: 任务调度、飞书交互、轻量编码
- Claude Code 负责: **复杂重构、架构决策、跨文件大规模修改**

## 配置

```bash
# 1. 安装
npm install -g @anthropic-ai/claude-code

# 2. 授权
claude auth login

# 3. 验证
claude --version

# 4. 项目配置
# 在项目根目录创建 CLAUDE.md（自动加载）
```

## CLAUDE.md 模板

项目根目录的 CLAUDE.md 内容参考：

```markdown
# <项目名> Claude Code 配置

## 技术栈
- <语言/框架>
- <数据库>
- <工具链>

## 构建命令
- 构建: <命令>
- 测试: <命令>
- 启动: <命令>

## 代码风格
- <规范1>
- <规范2>
```

## 使用模式

| 场景 | 谁执行 | 说明 |
|------|--------|------|
| 轻量编码(单文件) | Hermes Agent | write_file/patch/terminal |
| 复杂重构(跨文件) | Claude Code | 玉芬在终端启动 |
| 架构决策 | Claude Code | 需要推理链 |
| 代码审查 | Claude Code | 拉 PR 审查 |
