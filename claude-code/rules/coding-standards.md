# 渔芯项目 — 编码铁律（全局规则）

> 加载时机：所有项目自动加载
> 来源：~/.claude/CLAUDE.md（更详细版本）

## 核心原则

1. **直接、不绕弯** — 华哥不喜欢反复确认，结果导向
2. **先汇报再问** — 改完先报告，不边干边问
3. **不污染历史** — 新任务开新会话（/clear）

## 编码规范

- **缩进**：Python 4 空格，JS/TS/JSON/YAML 2 空格
- **命名**：Python snake_case，JS/TS camelCase，类 PascalCase
- **类型**：Python 加 type hints；TS 严格模式
- **注释**：函数必须有 docstring（Google 风格）
- **禁**：wildcard import、循环依赖

## Git 规范

- **分支**：`feature/xxx` / `fix/xxx` / `chore/xxx`
- **提交**：`<type>(<scope>): <描述>`（feat/fix/refactor/docs/test/chore/perf）
- **禁**：`git push --force` 到 main、`rm -rf`、直推 main
- **PR**：所有变更走 PR 流程

## 测试

- **新功能必测**（pytest / vitest）
- **覆盖率**：核心模块 > 80%
- **命名**：`test_<功能>_<场景>_<预期>`

## 渔芯特别提醒

- **渔芯 = 2 个品牌**：①渔芯水产养殖（RAS）②LookForge（数据仿真）
- **华哥 = 张路华** = 东莞市渔芯科技负责人
- **必须用 Claude Code 写代码**（不直接终端改）
- **网络能上**（api/内网/GitHub 都没问题）
- **中文路径陷阱**：`--workdir` 拒绝中文 → `ln -s` 到 `/tmp`
