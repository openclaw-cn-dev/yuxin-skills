# 渔芯项目 — 效率规则

> 加载时机：所有项目自动加载

## 工作流选择

### Print 模式（`claude -p`）— 一次性任务首选
```bash
# 必带 3 个参数
claude -p "任务" --max-turns 10 --max-budget-usd 1.0 --allowedTools 'Read,Edit'
```

**适用**：
- 一次性 bug 修复
- 重构单个模块
- 生成文档
- CI/CD 脚本

### 交互模式（tmux）— 复杂多轮
- 多轮迭代（设计 → 实现 → 测试 → 修复循环）
- 需要人决策
- 探索性编程

**适用**：
- 重构整个项目
- 复杂功能设计
- 调试棘手 bug

## 上下文管理

### 触发 /compact 的时机
- `/context` > 70% → 立即 `/compact [focus]`
- 长任务开始 → 主动 `/compact`
- 切换任务类型 → `/clear`

### 不要做的
- ❌ 同一会话跑 N 个不相关任务
- ❌ 让上下文撑爆到 90%+（幻觉风险）
- ❌ 频繁回滚对话

## 并行优先

### 3 个独立任务
```bash
# 同时开 3 个 tmux
tmux new-session -d -s task1 -x 140 -y 40
tmux new-session -d -s task2 -x 140 -y 40
tmux new-session -d -s task3 -x 140 -y 40

# 任务结束后清理
tmux kill-session -t task1
```

### 任务依赖
- 串行：A 完成才能 B
- 不串行浪费时间

## 成本控制

| 任务 | 模型 | 单次预算 |
|---|---|---|
| 简单查文档 | haiku | $0.05 |
| 写单测 | sonnet | $0.30 |
| 重构模块 | sonnet | $1.00 |
| 复杂设计 | opus | $2.00 |
| 架构决策 | opus + ultrathink | $3.00 |

**规则**：
- ✅ 必设 `--max-turns`（防无限循环）
- ✅ 必设 `--max-budget-usd`（硬卡成本）
- ✅ 简单任务用 haiku
- ✅ 关键决策用 opus + `ultrathink`
- ❌ 不浪费在琐碎任务上用 opus

## 完成汇报

完成后**立即**汇报：
- ✅ 改了什么（文件列表）
- ✅ 跑过什么测试
- ✅ 下一步建议
- ❌ 不"还在跑"（1 小时 1 报即可）
