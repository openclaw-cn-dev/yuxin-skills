# 渔芯 Agent 统一管理中心 — 新建智能体 SOP

**目标**: 10 分钟内从 0 到 1 创建一位新的公司智能体，完成配置、部署、培训全流程。

---

## 📋 流程总览

```
1. 确定角色      →  2. 选择模板    →  3. 填写配置    →  4. 注册索引    →  5. 部署上线    →  6. 培训验证
```

**预期时间**: 新 Hermes 同事 15-20 分钟 / Codex CLI 5 分钟 / Claude Code 5 分钟

---

## Phase 1: 确定角色

### 1.1 回答 5 个关键问题

| # | 问题 | 示例（旺财） |
|---|------|------------|
| ① | 智能体名字？ | 旺财 |
| ② | 核心职责是什么？ | CAD/SolidWorks 出图 + 自媒体运营 |
| ③ | 部署在什么平台？ | Windows |
| ④ | 用什么 LLM Provider？ | volcengine-agent-plan |
| ⑤ | 飞书 Bot 的 App ID + Secret？ | cli_aaaefb812938dbcd |

### 1.2 选择智能体类型

| 类型 | 适用场景 | 模板位置 |
|------|---------|---------|
| **Hermes Agent** | 飞书 Bot, 任务调度, 多 profile 管理 | `agents/hermes/template/` |
| **Codex CLI** | 编程引擎, 代码生成 (Python/CadQuery) | `agents/codex/template/` |
| **Claude Code** | 高级编程, 复杂重构, 架构决策 | `agents/claude-code/template/` |
| **OpenClaw** | AI 网关, API 路由 | `agents/openclaw/template/` |

> **组合模式**: 一个"角色"可能同时需要 Hermes Agent + Codex CLI（如旺财）。

---

## Phase 2: 选择模板并填写

### 2.1 复制模板

```bash
# 新同事叫 <name>
cp -r agents/hermes/template/ agents/hermes/<name>/
```

### 2.2 填写 MEMORY.md

按模板填写 4 段：
1. **身份层**: 名字、profile名、角色、平台、职责
2. **核心能力**: 3 条核心技能 + 工具链
3. **继承知识**: 从哪个同事继承了什么
4. **团队层**: 指向 `l1_shared/team_overview_l1.md`

**字节限制**: L1 严格控制在 2KB 以内（超过触发自动压缩）。

### 2.3 填写 USER.md

按模板填写：
- 身份信息
- 核心职责（分点）
- 环境特点（Windows/macOS 差异）
- 沟通风格

### 2.4 填写 config.yaml

关键字段：
- `provider` + `model` — LLM Provider 和模型
- `feishu.app_id` / `feishu.app_secret` — 飞书 Bot 凭证（⚠️ Secret 用占位符 `__REPLACE_ON_DEPLOYMENT__`）
- `gateway.type: feishu` + `websocket: true`
- 工具集（browser, web 等）

---

## Phase 3: 注册到索引

### 3.1 更新 agents/index.json

```json
{
  "name": "<name>",
  "role": "<角色>",
  "platform": "<平台>",
  "status": "deploying"
}
```

### 3.2 更新 README.md 目录

在 README 目录中添加新 agent 的一行记录。

---

## Phase 4: 部署上线

### 4.1 同机器部署

```bash
# 1. 创建 profile 目录
mkdir -p ~/.hermes/profiles/<name>/{memories,config}

# 2. 复制配置
cp agents/hermes/<name>/MEMORY.md ~/.hermes/profiles/<name>/memories/
cp agents/hermes/<name>/USER.md ~/.hermes/profiles/<name>/memories/
cp agents/hermes/<name>/config.yaml ~/.hermes/profiles/<name>/

# 3. 替换飞书 Secret（手动编辑 config.yaml）
# ⚠️ 不要提交真实 Secret 到 Git！

# 4. 创建 launchd plist（macOS）
hermes gateway install --profile <name>

# 5. 启动
launchctl load ~/Library/LaunchAgents/ai.hermes.gateway-<name>.plist

# 6. 验证
launchctl list | grep ai.hermes.gateway-<name>
```

### 4.2 新机器部署（Windows）

```powershell
# 1. 安装 Hermes Agent
pip install hermes-agent

# 2. 克隆本仓库
git clone https://github.com/openclaw-cn-dev/yuxin-skills.git ~\.hermes\skills-repo

# 3. 复制 profile
xcopy /E skills-repo\agents\hermes\<name> ~\.hermes\profiles\<name>\

# 4. 替换飞书 Secret（⚠️ 手动替换）
notepad ~\.hermes\profiles\<name>\config.yaml

# 5. 启动 Gateway
hermes gateway run --profile <name>
```

---

## Phase 5: 培训验证

### 5.1 飞书私聊激活

华哥飞书搜索新 bot 名字 → 发一句话 → 激活路由

### 5.2 功能验证

```bash
# 1. 健康检查
curl -s "https://open.feishu.cn/open-apis/im/v1/chats?page_size=5" \
  -H "Authorization: Bearer <token>"

# 2. 测试 LLM
hermes gateway status --profile <name>

# 3. 发送测试消息
# 飞书私聊新 bot: "你好，开始工作"
```

### 5.3 注册团队 Cron

```bash
# 添加心跳 cron
hermes cron create --profile <name> \
  --schedule "every 1h" \
  --prompt "心跳检查 + 飞书云盘任务扫描"
```

---

## 完整示例: 新建旺财

| 阶段 | 完成文件 | 关键内容 |
|------|---------|---------|
| 角色确定 | — | CAD + 自媒体, Windows, volcengine-agent-plan |
| MEMORY.md | `agents/hermes/wangcai/MEMORY.md` | 身份+能力+继承毛豆+团队层 |
| USER.md | `agents/hermes/wangcai/USER.md` | 职责+环境+沟通风格 |
| config.yaml | `agents/hermes/wangcai/config.yaml` | 飞书 Bot + 工具集 |
| Codex AGENTS.md | `agents/codex/wangcai/AGENTS.md` | 编程大脑配置 |
| 部署脚本 | `templates/hermes-agent/setup_wangcai.ps1` | Windows 一键部署 |
| 注册索引 | `agents/index.json` | wangcai 记录 |
| 培训 | — | 飞书激活 + 功能验证 |

---

## 常见陷阱

| 陷阱 | 表现 | 解决 |
|------|------|------|
| 飞书 Secret 提交到 Git | GitHub 推送被拒绝 | 用 `__REPLACE_ON_DEPLOYMENT__` 占位符 |
| launchd 服务被 disabled | `launchctl load` 报 I/O error | 先 `launchctl enable` 再 `load` |
| 私聊路由未激活 | bot 不回复私聊 | 华哥飞书发一句话激活 |
| 并发超限 | 429 rate limit | 减少 cron 频率或用 no-agent 模式 |
| L1 超 2KB | 自动压缩截断 | 控制在 2KB 以内 |
