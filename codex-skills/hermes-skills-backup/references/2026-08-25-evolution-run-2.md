# 2026-08-25 Codex 进化 runbook（**第二次 9 点 cron，结构性补完**）

**核心结论**：**首次给 `~/.hermes/skills/` 装 skill**——`kanban-orchestrator` v3.0.0 + `kanban-worker` v2.0.0 来自 `forcewake/hermes-conductor`（57⭐）。补完旺财之前 87 个 skill 全堆在 Codex 的结构性缺口。Codex 本日 0 变更（CLI 0.149.1 与昨日一致，7 插件已满）。

---

## 1. 命令序列（与前次 cron 一致 + 新增 Hermes skills 检测）

```bash
# 既有 Codex 序列
codex --version
codex plugin marketplace list
codex plugin list
codex update    # ⚠️ 本日撞 npm EPERM unlink codex.exe（进程锁）→ 跳过；CLI 已是 0.149.1

# Codex skills 盘点
ls ~/.codex/skills/ | wc -l    # 88
find ~/.codex/skills -name SKILL.md -not -path '*/.system/*' | wc -l

# 🆕 Hermes skills 盘点（**首次纳入巡检**）
ls ~/.hermes/skills/ 2>&1 | wc -l
# 之前是 0，今天首次变成 2
```

---

## 2. 今日变更（2 条主 + 3 段漏斗）

### 2.1 Hermes skills 首次启用

- 8-25 之前 `~/.hermes/skills/` 一直是空（**所有 87 个 skill 都在 Codex 那边**）
- 今日装：`kanban-orchestrator` v3.0.0（14.8KB SKILL.md + 2 references） + `kanban-worker` v2.0.0（11KB）
- 来源：`forcewake/hermes-conductor`（57⭐）—— 真身 = **Hermes skill**（`metadata.hermes.tags: [kanban, multi-agent, orchestration, routing]`）
- 配套：`hermes kanban list` 已可用（Hermes 内置 kanban 系统），这俩 skill 是**路由方法论 playbook**——"decompose don't execute" + worker 生命周期

### 2.2 5 维 GitHub 搜索 + 三段漏斗

5 维搜索（ai-agents / claude-skill / xhs-douyin / solidworks / crm）返回 ~30 个候选。三段漏斗（frontmatter / 结构 / 业务匹配）过滤后：

| Repo | ⭐ | 评估 | 决策 |
|---|---|---|---|
| **forcewake/hermes-conductor** | 57 | Hermes skill, kanban 多 worker 路由 | ✅ 装 |
| **cclank/lanshu-create-ai-presenter-video** | 837 | AI 数字人付费 API（OpenAI/Kling/Veo）| ❌ 业务不匹配 |
| **HanyuanWang/LiveStream-Agent-Studio** | 116 | **不是 skill** 是 Python 项目（4 个 agent + Windows 网关）| ❌ 非 skill 类型 |
| **LB623/no-negative-echo** | 344 | 已装 0823,本次仅 provenance 文件差异 | ❌ 已装 |
| **duty1g/x64dbg-mcp-server** | 1229 | x64dbg 调试 MCP | ❌ 业务无关 |

**3 段漏斗口诀**：① frontmatter 有 `metadata.hermes.tags` / `metadata.codex.tags` 才算合格；② SKILL.md + references + scripts 完整子树；③ 业务匹配 = **老大 4 业务线 + 当前痛点**（"理论上能用"不算）。

---

## 3. 踩坑 / 新发现

### 3.1 SSH clone 后 cd 路径污染

**症状**：连续 3 次 `cd /c/.../<repo>` 失败（"No such file or directory"），导致后续 `head SKILL.md` 读的是**上一个成功 cd 的目录**的内容。

**根因**：git clone 输出 "Cloning into 'xxx'..." 后 stderr 丢失，terminal 工具的 `cd` 失败但**未重置工作目录**，后续命令在错的目录跑。

**判定**：
```bash
# clone 后必跑：pwd 与预期对比
git clone --depth 1 git@github.com:xxx/yyy.git eval-repos/yyy 2>&1 | tail -3
cd eval-repos/yyy && pwd   # 期望: .../eval-repos/yyy
head -5 SKILL.md            # 期望是 yyy 的 frontmatter
```

**铁律**：**每次 clone 后必 `cd && pwd && ls` 三步验证**，再 `head` 内容。`cd` 失败 = 整个 terminal turn 重置。

### 3.2 Hermes skill 目录之前完全未启用（结构性盲区）

**症状**：88 个 skill 全在 `~/.codex/skills/`，但 Hermes 自带 `~/.hermes/skills/` 目录空。老大说"加 skill"时，旺财**默认走 Codex**，从未主动探查 Hermes 路径。

**根因**：Hermes skill 没有自动 discovery 工具（不像 Codex 那样 `codex skills list`），只能 `ls ~/.hermes/skills/` 才知道有没有东西。

**修法（已写入 SKILL.md）**：明确两类路径分流 + frontmatter 判定脚本。

### 3.3 `codex update` 撞 npm EPERM（本日新增触发）

**症状**：
```
npm warn cleanup Failed to remove some directories
npm warn cleanup 'C:\Users\Administrator\AppData\Roaming\npm\node_modules\@openai\.codex-awaeVzrD'
npm warn cleanup [Error: EPERM: operation not permitted, unlink '...\codex.exe']
```

**根因**：CLI 进程锁住 `codex.exe`，npm 切新目录运行后清理旧目录失败。**当前 CLI 已是 0.149.1**（昨日 0824 升过），本次 skip update 合理。

**判定**：撞 EPERM + 当前版本 = 远端最新 = 直接 skip，不等修复。

### 3.4 yuxin-skills 备份路径分流（**新约定，8-25 立**）

今日首次备份 Hermes skill 到 `yuxin-skills/skills/`（顶层 `skills/` 目录，跟 `codex-skills/` dash 路径平行）：

| 目录 | 谁用 | 同步什么 |
|---|---|---|
| `yuxin-skills/skills/`（顶层）| 旺财 9 点 cron | **Hermes skills**（本次首次启用）|
| `yuxin-skills/codex-skills/`（dash）| 旺财 9 点 cron | Codex skill 精选 |
| `yuxin-skills/codex/`（slash）| 同事 auto-sync cron | yuxin-* 公司专属 |

**判定**：装 Hermes skill 前 `mkdir -p yuxin-skills/skills/`；装 Codex skill 走 `codex-skills/`。

---

## 4. 待办 / 老大需决策

- ⚠️ **P0：Hermes 升级**（持续 5 周）：v0.19.0 → 远端 v0.20.5。老大手动 `hermes update` ZIP fallback + 重启 Windows
- ⚠️ **P0：yuxin-skills push 待老大解 unblock**（已知 0820-0823 撞 secret-scanner 4 次,本日 commit 7f2e34b 清洁但仍未推）
- 💡 **`~/.hermes/skills/` 启用**——可考虑迁移部分 Hermes 高频 skill（`aquaculture-media-content` / `feishu-router` 等）过来,让飞书/Hermes 调度更快
- 💡 本次漏装：`cclank/lanshu-create-ai-presenter-video`（837⭐,付费数字人）—— 等老大决定要不要做 IP 化数字人再说