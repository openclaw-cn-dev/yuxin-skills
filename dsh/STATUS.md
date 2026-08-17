# DeepSeek Harness (dsh) 状态快照
> 导出时间: 2026-08-18 05:05:07
> 🤖 自动同步自 Hermes/玉芬 · dsh 自进化模块

## 版本
- 本地: `v0.1.0-rc.5` (commit `47f9438`)
- npm 最新: ``
- upstream 落后: `-1` commit
- 状态: `unknown`

## 安装方式
- 源码 monorepo: `git clone https://github.com/deepseek-ai/deepseek-harness.git`
- 本地路径: `系统文件夹/deepseek-harness` (与 Claude/Codex 平级)
- 运行: `pnpm dsh web` (Web UI 默认 127.0.0.1:3080)
- 配置目录: `~/.dsh` (⚠️ 尚未软链接到系统文件夹)

## 会话 (4 个)
- `Users-hua-6-产品研发-ok-GEO`: 2 会话
- `Users-hua-6-产品研发-37-boss deck御书房`: 2 会话

## 同步策略
- 仅同步状态快照 + 配置结构, 不上传真实凭据
- `.credentials.yaml` 自动脱敏 (DEEPSEEK_API_KEY → <REDACTED>)
- 更新策略: 检测 + 通知, 不自动 git pull (预览版有破坏性变更风险)
- 一键更新: `bash ~/.hermes/scripts/dsh_update.sh`

## 仓库结构
```
yuxin-skills/
├── claude-code/    ← Claude Code
├── codex/          ← Codex
├── hermes/         ← Hermes
└── dsh/            ← 本目录 (DeepSeek Harness)
```

> 🔒 公司内部资产，禁止对外公开。
