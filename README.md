# 渔芯 Agent 技能仓库 (yuxin-skills)

**统一的 Agent 能力管理中心** — 跨机器、跨 profile 共享技能、配置和记忆模板。

## 仓库结构

```
yuxin-skills/
├── profiles/          # Agent 身份/记忆模板
│   └── wangcai/      # 旺财 Profile (Windows CAD + 自媒体专员)
├── skills/            # 共享技能
│   ├── wangcai-cad/           # 旺财 CAD/SolidWorks 出图技能
│   └── wangcai-social-media/  # 旺财自媒体自动化运营技能
├── scripts/           # 部署脚本
│   ├── setup_wangcai.ps1     # Windows 一键部署 (PowerShell)
│   └── AGENTS.md             # Codex CLI 配置
└── references/        # 参考资料
    └── windows/       # Windows 部署说明书
        └── INSTALL.md
```

## 使用方式

### 已有 Hermes 用户
```bash
# 克隆仓库
git clone git@github.com:openclaw-cn-dev/yuxin-skills.git ~/.hermes/skills-repo

# 将需要的技能软链到 skills 目录
ln -s ~/.hermes/skills-repo/skills/wangcai-cad ~/.hermes/skills/
ln -s ~/.hermes/skills-repo/skills/wangcai-social-media ~/.hermes/skills/

# 创建 profile
cp -r ~/.hermes/skills-repo/profiles/wangcai ~/.hermes/profiles/wangcai
```

### 新机器 (Windows)
1. 克隆本仓库
2. 按照 `references/windows/INSTALL.md` 说明操作
3. 或运行 `scripts/setup_wangcai.ps1` 一键部署

## Agent 清单

| Profile | 角色 | 平台 | 核心技能 |
|---------|------|------|---------|
| wangcai | CAD + 自媒体专员 | Windows | CAD出图、自媒体运营 |

## 维护

```bash
# 拉取最新技能
cd ~/.hermes/skills-repo && git pull

# 添加新技能
cd ~/.hermes/skills-repo && git add skills/<新技能名>/ && git commit -m "feat: 添加 <新技能名>" && git push
```
