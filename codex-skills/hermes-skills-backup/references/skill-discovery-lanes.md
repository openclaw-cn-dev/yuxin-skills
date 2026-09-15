# Skill Discovery Lanes — GitHub API 检索矩阵

2026-08-03 实测：只跑 `topic:ai-agents` 会漏掉所有 SKILL.md 仓库（它们不打 ai-agents topic）。**至少跑 3 条 lane 才能覆盖完整发现面**。

## Lane A：`topic:ai-agents`（agent framework / runtime）
```bash
curl -s "https://api.github.com/search/repositories?q=topic:ai-agents+created:>$(date -d '7 days ago' +%Y-%m-%d)&sort=stars&per_page=10"
```
**返回类型**：agent runtime、workflow engine、trace/audit 工具
**典型项目**：microsoft/skill-recorder(811⭐)、0xwilliamortiz/ratchet(411⭐)、uczltw6/trace-file-lineage(195⭐)
**不是 SKILL.md 来源**——但有 Codex 集成价值的仍可考虑（如 ratchet 给 Codex 加行为审计）

## Lane A1：`claude-code+skills` / `codex+skill`（SKILL.md 仓库专属）🆕
```bash
curl -s "https://api.github.com/search/repositories?q=claude-code+skills+created:>$(date -d '7 days ago' +%Y-%m-%d)&sort=stars&per_page=10"
curl -s "https://api.github.com/search/repositories?q=codex+skill+created:>$(date -d '7 days ago' +%Y-%m-%d)&sort=stars&per_page=8"
```
**返回类型**：直接给 Claude Code / Codex 用的 SKILL.md 仓库
**典型项目**：robbin/wechat-exporter(186⭐)、0rangec3t/Black-cat(181⭐)、ilindaniel/impeccable-lite(61⭐)、allenloves/de-ai-tone(58⭐)、SoraLabsOSS/skills(24⭐)
**这是 SKILL.md 的真正来源地**——过滤标准：⭐>50 + 描述含 `skill`/`agent`/`claude`/`codex`

## Lane A2：`mcp-server`（MCP 新插件）🆕
```bash
curl -s "https://api.github.com/search/repositories?q=mcp-server+created:>$(date -d '7 days ago' +%Y-%m-%d)&sort=stars&per_page=8"
```
**返回类型**：MCP server 新插件（Claude/Codex 通用）
**典型项目**：alxgntv/substack-api-mcp(80⭐)、talivia-group/agent(71⭐)
**安装方式**：`hermes mcp add <name>` 或 `codex mcp add <name>`（按平台）

## Lane B：上游 skills 仓库 diff（marketingskills / social-media-skills）
```bash
curl -s "https://api.github.com/repos/coreyhaines21/marketingskills/contents/skills" | python -c "import json,sys;d=json.load(sys.stdin);[print(f['name']) for f in d]"
diff <(ls ~/.codex/skills/ | sort) <(curl ... | sort) | grep "^>"
```
**触顶信号**：连续 N 周 diff 输出空 → 上游已无可补 → 必须主动建议 A/B/C 方向（plugin 切换 / 二套目录 / 审计卸载）

## Lane C：垂直场景（按业务需要）
```bash
# CAD / 3D 建模
curl -s "https://api.github.com/search/repositories?q=cad+ai+solidworks+created:>$(date -d '7 days ago' +%Y-%m-%d)&sort=stars&per_page=8"

# 社媒自动化
curl -s "https://api.github.com/search/repositories?q=social-media-automation+created:>$(date -d '7 days ago' +%Y-%m-%d)&sort=stars&per_page=10"
```
**注意**：垂直场景往往 ⭐ 都很低（<10），**只汇报不装**——等下次再观察

## 频率建议

| Lane | 跑频 | 理由 |
|---|---|---|
| A / A1 / A2 | **每次必跑**（9 点 cron） | 主发现通道，30 秒搞定 |
| B | 每周一次 | diff 稳定，频繁跑浪费 API 配额 |
| C | 每月一次 | 垂直场景变化慢 |

## 过滤原则（汇总）

| 标准 | 行动 |
|---|---|
| ⭐ > 50 + 含 SKILL.md / MCP | **评估后装** |
| ⭐ > 50 + 纯 framework | 写日报"潜在集成"段，老大拍板 |
| ⭐ 20-50 + 任何 | 写日报"待观察"段 |
| ⭐ < 20 | **跳过**，下周再看 |
| 描述含 `setup`/`template` 但无 SKILL.md | 多半 wrapper，**跳过** |
| 上游仓库 6 个月未更新 | **仓库失效**，日报标"marketingskills 仓库失效" |