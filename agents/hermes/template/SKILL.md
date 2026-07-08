---
name: hermes-agent-new-profile-template
description: 新建 Hermes Agent 同事的标准化模板 — 从 0 到 1 创建新 profile
version: 2.0.0
tags: [template, onboarding, hermes, profile]
---

# Hermes Agent 新建 Profile 模板

## 使用场景
当需要新增一位 Hermes 同事（如旺财）时，用此模板快速生成完整 profile。

## 模板文件清单

创建 profile 需要以下 3 个文件：

```
agents/hermes/<name>/
├── MEMORY.md        # L1 记忆（自动注入每轮对话）
├── USER.md          # L2 用户档案（华哥 + 公司信息）
└── config.yaml      # Hermes 配置（LLM provider + 飞书 Bot）
```

## Step 1: 确定角色定位

| 字段 | 内容 |
|------|------|
| 名字 | 中文名（如旺财） |
| Profile名 | 英文/拼音（如 wangcai） |
| 核心职责 | 一句话概括（如 CAD/SolidWorks 出图 + 自媒体运营） |
| 平台 | macOS / Windows |
| 汇报对象 | 华哥 / 玉芬 |
| LLM Provider | minimax / volcengine-agent-plan |
| 飞书 Bot | App ID + Secret |

## Step 2: 创建 MEMORY.md

```markdown
# <名字> MEMORY（自动注入每轮对话）

§
## 身份层
- **名字**: <中文名> (渔芯 <职责>)
- **Profile**: <profile名>
- **角色**: <核心职责>
- **平台**: <平台>, <网关类型> 飞书
- **核心职责**: <详细职责列表>

§
## 核心能力
1. <能力1>: <工具/方法>
2. <能力2>: <工具/方法>
3. <能力3>: <工具/方法>

§
## 从<继承来源>继承的知识
- <关键知识1>
- <关键知识2>

§
## 团队层 (共享)
完整团队概览在 `~/hermes/team/memory/l1_shared/team_overview_l1.md`
详细团队档案在 `~/hermes/team/team_overview.md`
```

## Step 3: 创建 USER.md

```markdown
# <名字> USER 档案 L1
**创建日期**: YYYY-MM-DD
**来源**: <原始档案来源>

## 身份
- <名字> — 渔芯科技 <职位>
- 汇报对象: <汇报对象>
- 所在平台: <平台>

## 核心职责

### 1. <职责1>
- <具体工作描述>
- <工具链>

### 2. <职责2>
- <具体工作描述>
- <工具链>

### 3. 团队协作
- 通过飞书接收任务
- 产出推送到飞书云盘

## <平台> 环境特点
- <路径/工具/编码注意事项>

## 沟通风格
- <风格描述>
```

## Step 4: 创建 config.yaml

```yaml
# <名字> Hermes Agent 配置
# 复制到 ~/.hermes/profiles/<profile名>/config.yaml

provider: <LLM Provider>
model: <模型名>

# 飞书 Bot 凭证
feishu:
  app_id: <App ID>
  app_secret: "__REPLACE_ON_DEPLOYMENT__"

# Feishu WebSocket gateway
gateway:
  type: feishu
  websocket: true

# 工具集配置
toolsets:
  - hermes-cli
  - browser        # 如果需要浏览器自动化
  - web            # 如果需要网络搜索

# 默认工作目录
workdir: "<工作路径>"
```

## Step 5: 注册到团队

1. 更新 `agents/index.json` 添加新 agent 记录
2. 更新 `README.md` 添加新 agent 到目录
3. 如果是在现有机器部署: 直接复制 profile 文件
4. 如果是新机器部署: 提供部署脚本 + 说明书
