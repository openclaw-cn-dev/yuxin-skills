# 渔芯 Agent 统一管理中心 (yuxin-skills)

**统一的公司智能体能力管理中心** — 跨机器、跨 profile 共享技能、配置、记忆模板和部署 SOP。

## 仓库结构

```
yuxin-skills/
├── agents/                          # 📋 所有智能体定义
│   ├── index.json                   #   Master 注册表（所有 agent 清单）
│   ├── hermes/                      #   Hermes Agent profiles
│   │   ├── template/                #     新建 Hermes 同事模板
│   │   └── wangcai/                 #     旺财（CAD + 自媒体专员）
│   ├── codex/                       #   Codex CLI 配置
│   │   ├── template/                #     新建 Codex CLI 模板
│   │   └── wangcai/                 #     旺财的 Codex CLI 配置
│   ├── claude-code/                 #   Claude Code 配置
│   │   └── template/                #     新建 Claude Code 模板
│   └── openclaw/                    #   OpenClaw AI 网关配置
│       └── template/                #     新建 OpenClaw 模板
├── skills/                          # 🧰 共享技能
│   ├── wangcai-cad/                 #   旺财 CAD/SolidWorks 出图
│   └── wangcai-social-media/        #   旺财自媒体自动化运营
├── playbooks/                       # 📖 标准操作流程
│   ├── onboard-new-agent.md         #   新建智能体 SOP（核心文档）
│   ├── sync-skills-from-mac.md      #   技能同步指南
│   └── health-check-all-agents.md   #   全智能体健康检查
├── templates/                       # 🚀 部署模板
│   ├── hermes-agent/                #   Hermes Agent 部署包
│   │   ├── setup_wangcai.ps1       #     Windows 一键部署
│   │   └── INSTALL.md               #     Windows 部署说明书
│   └── codex-cli/                   #   Codex CLI 部署
│       └── AGENTS.md                #     Codex 角色配置
└── README.md                        # 本文件
```

## 智能体清单

### Hermes Agent (9 个 profile)

| Profile | 角色 | 平台 | LLM Provider | 状态 |
|---------|------|------|-------------|------|
| default | 玉芬-团队管理员 | macOS | minimax | ✅ |
| maodou | 产品经理+3D工程 | macOS | volcengine-agent-plan | ✅ |
| laomo | 知识库+测试 | macOS | minimax | ✅ |
| xiaobao | 销售+自媒体 | macOS | minimax | ✅ |
| heidou | 行政+财务+法务 | macOS | minimax | ✅ |
| afu | 客服+异议处理 | macOS | minimax | ✅ |
| quant | 量化研究 | macOS | minimax | ✅ |
| zhenglishi | 学习助手 | macOS | minimax | ✅ |
| wangcai | CAD+自媒体专员 | Windows | volcengine-agent-plan | 🚧 |

### Codex CLI (1 个配置)

| 名称 | 角色 | 版本 | 平台 | 状态 |
|------|------|------|------|------|
| wangcai-codex | 旺财编程大脑 | 0.142.5 | Windows | 🚧 |

### Claude Code (1 个配置)

| 名称 | 角色 | 版本 | 平台 | 状态 |
|------|------|------|------|------|
| yufen-claude | 玉芬编程辅助 | 2.1.203 | macOS | ✅ |

### OpenClaw (1 个配置)

| 名称 | 角色 | 版本 | 平台 | 状态 |
|------|------|------|------|------|
| main-gateway | 渔芯AI网关 | 2026.5.2 | macOS | ✅ |

## 快速开始 — 新建智能体

```bash
# 1. 克隆仓库
git clone git@github.com:openclaw-cn-dev/yuxin-skills.git ~/.hermes/skills-repo

# 2. 阅读 SOP
cat ~/.hermes/skills-repo/playbooks/onboard-new-agent.md

# 3. 选择模板
cp -r ~/.hermes/skills-repo/agents/hermes/template/ agents/hermes/<新同事名>/

# 4. 填写配置 → 部署 → 培训验证
```

> 完整流程详见 `playbooks/onboard-new-agent.md`

## 维护

```bash
# 拉取最新
cd ~/.hermes/skills-repo && git pull

# 添加新 agent
# 1. 创建 agents/hermes/<name>/
# 2. 更新 agents/index.json
# 3. git add && git commit && git push

# 添加新 skill
# 1. 创建 skills/<skill-name>/
# 2. 更新 README 技能清单
# 3. git add && git commit && git push
```
