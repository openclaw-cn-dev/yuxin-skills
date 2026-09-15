# 2026-08-24 Codex 进化巡检 runbook

## 一句话总结

CLI 升级 + 1 插件新增 + 0 skills 变化 + AGENTS.md 从 0 字节恢复。

## 执行序列

1. `codex --version` → `codex-cli 0.147.0`（基线）
2. `codex plugin marketplace list` → openai-bundled + openai-curated（双 local snapshot）
3. `codex plugin list` → 7 enabled（codex-app-tools/sites/browser/chrome/computer-use/latex/visualize）
4. `codex plugin marketplace upgrade --dry-run` → `unexpected argument '--dry-run'`（永久被拒，跳过）
5. `codex plugin marketplace upgrade`（裸跑）→ `No configured Git marketplaces to upgrade.`（local snapshot 限定，正常）
6. `codex update` → **升级成功 0.147.0 → 0.149.1**（npm EPERM 警告是噪音，看 `🎉 Update ran successfully` 判定）
7. `codex plugin add latex@openai-bundled` → 装上 v0.2.6（首次用 `add` 而不是误传 `install`）
8. `find ~/.codex/skills -name SKILL.md -not -path '*/.system/*' | wc -l` → **87 个用户 skill**
9. `find ~/.codex/skills/.system -name SKILL.md | wc -l` → 6 个 .system 内置
10. awk 分类脚本 → **24 DEV / 38 MKT / 25 OTHER**
11. `stat ~/.codex/AGENTS.md` → **size: 0**（空文件！）→ 走 write_file 重建
12. `write_file` 重建 AGENTS.md（3.7 KB，含版本/插件/skills/MCP/今日变更）

## 本次踩到的坑（升级入 SKILL.md 主文档）

### 坑 A：`codex update` npm EPERM 噪音

- 完整 EPERM 输出贴到 SKILL.md "🆕 `codex update` npm EPERM 噪音 ≠ 失败" 段
- 关键判定：`changed 2 packages in 5s` + `🎉 Update ran successfully!` → 成功
- `codex --version` 从 0.147.0 跳到 0.149.1 是终极证据

### 坑 B：AGENTS.md 0 字节（首次发现）

- 前 23 次 cron 跑（7-31 立 skill → 8-24 之间）日报都写"AGENTS.md 已更新"，但 `stat` 显示 0 字节
- **根因（推测）**：早期某次 `terminal(rm ...)` 或 `git checkout` 清掉 → 后续 `patch`/`write_file` 写 0 字节文件**不报错**（空文件等同不存在）
- **3c-bis drift 检测未触发**：因为根本没 AGENTS.md 可读
- **修复**：cron 第一步加 `test -s ~/.codex/AGENTS.md` 守卫，空文件直接走 write_file 重建，不尝试 patch

### 坑 C：`codex plugin install` 不存在（再踩一次）

- `codex plugin install latex@openai-bundled` → `unrecognized subcommand 'install'`
- 正确命令：`codex plugin add`（已在 SKILL.md 标 8-15 实坑，本次二次确认）

### 坑 D：`codex plugin marketplace upgrade --dry-run` 永久被拒（再踩一次）

- 8-16 / 8-21 / 8-24 连续三次命中 → 已把 skill 里两处 "v0.147.0" 改成 "v0.147.0+" 强调永久性
- 正确判定法：`codex plugin marketplace upgrade --json`（无 --dry-run）

## 当日数据快照（供下次 cron 对照）

| 项 | 值 |
|---|---|
| Codex CLI | 0.149.1（升级自 0.147.0） |
| 已装插件 | 7（+1 latex） |
| 用户 skill | 87 |
| .system 内置 | 6 |
| DEV 分类 | 24 |
| MKT 分类 | 38 |
| OTHER 分类 | 25（含 4 个渔芯自研 + 2 个小红书垂类） |
| AGENTS.md | 已从 0 字节恢复成 3.7 KB |
| yuxin-skills 备份 | 本次未跑（仅本机 skill 库无新增，cron 不触发） |

## 渔芯自研 skills 清单（OTHER 类精华）

- `yuxin-content-engine` — 渔芯内容引擎
- `yuxin-fullstack` — 渔芯全栈
- `xiaohongshu-concept-explainer` — 小红书概念拆解
- `xiaoma-durex-copywriter` — 小马杜蕾斯文案（写作风格训练）

## 建议下次 cron 关注

1. **AGENTS.md 自动校验**：日报里加一行 `AGENTS.md: <size> bytes, last_modified <date>` —— 下次 cron 比对昨日，发现 0 字节/巨大变更立刻 P0 报
2. **plugin list 自动 diff**：把"今日 enabled 列表"快照保存到 `~/.codex/daily-evolution/` 目录，下次 cron diff 后报新增/删除
3. **Codex CLI 升级策略**：v0.149 → v0.150+ 大版本时保守升级（先 `codex doctor` 看 MCP 状态），小版本可自动升