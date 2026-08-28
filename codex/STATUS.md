# Codex 状态快照
> 导出时间: 2026-08-29 01:28:12
> 🤖 自动同步自 Hermes/玉芬 · Codex 自进化模块

## 版本
- 当前: `0.150.1`
- npm 最新: `0.150.1`
- 状态: `up_to_date`

## 公司专属 Skills (yuxin-*)
- 文件: 13 个
- 目录: 1 个

## 插件来源 (cache/)
- `openai-api-curated`
- `openai-bundled`
- `openai-curated-remote`
- `openai-primary-runtime`
- `sisyphuslabs`

## 数据源 (data/)
- `omo-sisyphuslabs`

## 同步策略
- 仅同步 `yuxin-*` 前缀的 skills (公司专属资产)
- 通用 skills (algorithmic-art, pdf, pptx 等) 不上传 (避免污染 GitHub)
- `config.toml` 自动脱敏 (含 token/secret/bearer 的字段值替换为 `<REDACTED>`)
- 同步缓存目录: `/tmp/yuxin-skills-codex-sync/`
- 触发: (1) 凌晨 2:00 self_evolution (2) 每小时 cron 轻量增量

## 仓库结构
```
yuxin-skills/
├── claude-code/    ← Claude Code 那边的 sync (已有)
├── drawing-skills/
├── hermes/         ← Hermes 那边的 sync (已有)
└── codex/          ← 本目录 (本次新增)
```

> 🔒 公司内部资产，禁止对外公开。
