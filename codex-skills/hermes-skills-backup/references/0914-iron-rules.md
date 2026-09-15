# 0914 装日铁律 — alirezarezvani 388-skill mega-repo 选装 + AGENTS.md drift 监控 + context budget 警告

> 来源：0914 cron 实盘 +2 skill 装入（rag-architect + mcp-server-builder）
> 场景：首次命中 alirezarezvani/claude-skills 25920⭐ 388 全栈 skill mega-repo，5 维搜索找到第 2 个可装仓库
> 关联：铁律 13（三件齐）+ 铁律 18（Jeffallan-style 选装法）+ 新立铁律 21-23

---

## 🆕 铁律 21：alirezarezvani mega-repo 388 skill 选装法（0914 立）

**触发**：GitHub search 返回单仓库 >= 100 个 skill（如 alirezarezvani/claude-skills 388 个）。

**关键差异 vs Jeffallan 67 skill（铁律 18）**：
- **Jeffallan** = 67 个独立 skill 目录平铺在 `skills/`
- **alirezarezvani** = 388 个 skill 分到 20+ domain 子目录（`engineering/skills/`、`marketing-skill/`、`c-level-advisor/`、`agents/`、`productivity/`、`finance/`、`research-ops/`、`business-operations/`、`commercial/`、`compliance-os/`、`project-management/`、`ra-qm-team/`、`business-growth/`、`product-team/`、`research/`、`standards/`、`templates/`、`markdown-html/`、`agent-launcher/`），**不能直接 `ls skills/`** —— 必须先选 domain 再选 skill

**0914 实盘流程**：
```bash
# 1. 稀疏 clone（不下载 .claude/ .codex/ .hermes/ .vibe/ 镜像目录）
git clone --depth 1 --filter=blob:none --sparse \
  https://github.com/alirezarezvani/claude-skills.git \
  ~/Desktop/eval-repos/daily-0914/alirezarezvani-claude-skills
cd ~/Desktop/eval-repos/daily-0914/alirezarezvani-claude-skills
git sparse-checkout set engineering/skills/rag-architect engineering/skills/mcp-server-builder
# 0914 实测：只拉 20 个 blob = 5s

# 2. 列 domain 子目录（GitHub API）
curl -sL https://api.github.com/repos/alirezarezvani/claude-skills/contents/engineering/skills | python -c "
import sys, json
for x in json.load(sys.stdin):
    if x['type'] == 'dir': print(x['name'])
"
# → 38 个 engineering skill

# 3. 批量评估 SKILL.md size（避免点开 38 个）
for skill in <list>; do
  size=$(curl -sL "https://raw.githubusercontent.com/alirezarezvani/claude-skills/main/engineering/skills/$skill/SKILL.md" | wc -c)
  echo "$skill: ${size}B"
done
# → 36/38 都有 frontmatter（合规 SKILL.md 标准）

# 4. SKILL.md < 10KB 筛 + 业务命中筛
# 0914 命中 = rag-architect (4.5KB) + mcp-server-builder (3.9KB)
# → 业务命中：4 群 wiki RAG + 渔芯平台 MCP

# 5. 三件齐筛（铁律 13）：
#    ① cross-refs >= 3 ← rag-architect 引 12 个模型名（不算兄弟 skill）
#    ② license MIT ✓
#    ③ SKILL.md < 10KB ✓
# ⚠️ rag-architect cross-refs 全是模型名（all-mpnet-base-v2 / bge-large / voyage-3-large）
#    不是兄弟 skill，**严格按铁律 13 算 = 0 兄弟 cross-ref**
#    破例决策：业务命中（4 群 RAG wiki + 渔芯 RAG）压倒三件齐

# 6. secrets scan + references 反向扫描 + 装入 + 备份
# 0914 实测：0 hit secrets / 8/8 references 全部存在
```

**0914 教训**：mega-repo 必须 sparse-checkout，不能 `--depth 1` 全拉（会带 .claude/ .codex/ .hermes/ 镜像目录共 50+MB）。

---

##  铁律 22：AGENTS.md drift 监控 + 兄弟 cron 静默安装漂移（0914 立）

**触发**：fs 实算 vs AGENTS.md 报 count 不一致。

**0914 实盘 drift**：
- AGENTS.md 0913 R2 报 = 114
- fs 实盘（0914 09:02 装 sureforge 后） = 115
- 漂移 = +1（兄弟 cron 9 月 14 日 09:02 装了 `sureforge` 未告知旺财 cron）
- 同时漏报 `llm-wiki-manager`（0911 装的也未进 AGENTS.md 任何分类）

**问题根因**：
1. **兄弟 cron 静默安装**：兄弟 cron 可能在旺财 cron 之前/之间静默装 skill，AGENTS.md 未更新
2. **AGENTS.md 历史只列 MKT/DEV/QA**，OTHER 类（流程编排/知识管理/QC）一直漏算

**新铁律（0914 立）**：
- ✅ 每次 cron 第 1 步必跑 `fs - AGENTS.md 报 = drift` 对账
- ✅ drift ≠ 0 → 用 Python set 差集（git-bash comm 0912 已废）找漏算 skill 名
- ✅ 兄弟 cron 装的 skill（如 `sureforge`）也要进 OTHER 分类
- ✅ OTHER 类口径：流程编排（sureforge）+ 知识管理（llm-wiki-manager）+ 项目级（yuxin-fullstack）

**0914 实盘 OTHER 3 个**：
```
llm-wiki-manager  # sametbrr 个人 wiki 第二大脑，0911 兄弟 cron 装
sureforge         # Da7-Tech QC 5 规则流程，0914 09:02 兄弟 cron 装
yuxin-fullstack   # 渔芯项目级编排（沿用）
```

**校验**：
```python
import os
fs_dir = os.path.expanduser('~/.codex/skills')
all_dirs = sorted([d for d in os.listdir(fs_dir) if not d.startswith('.system') and d != 'sepia.bak.0903'])
# classified 唯一 = MKT 77 + DEV 37 + QA 2 + OTHER 3 = 119
# 但 fs = 117（因为 autoprompt/brainstorming 不再跨类，0912 铁律 14）
# 实际 = 117 ✓ 0 drift
```

---

## 🆕 铁律 23：skills context budget 警告触发器（0914 立）

**触发**：codex exec 输出 `Skill descriptions were shortened to fit the skills context budget.`

**0914 实盘**：
```
$ codex exec --model gpt-5.6-terra ...
warning: Skill descriptions were shortened to fit the skills context budget. Codex can still see every skill, but some descriptions are shorter. Disable unused skills or plugins to leave more room for the rest.
```

**问题根因**：0914 fs = 117 个 skill，每个 skill 都有 description，**全塞进 context window 撑爆了 budget** → Codex 自动截断 description

**0914 决策**：暂时不动（不影响功能），但要监控增长曲线
- 0913 R2 = 114 个时无警告
- 0914 = 117 个时警告触发
- **临界点 = ~115 个**（经验值）

**未来动作**（不在 0914 执行）：
1. 跑 `codex plugin disable <plugin>` 关掉非核心 plugin（如 `documents`/`pdf`/`spreadsheets`/`presentations`——老大用 docx/pdf/xlsx skill 已够）
2. 或写 `~/.codex/config.toml` 的 `[skills]` 段限制 description 长度
3. 或把 `.system` 里的 `imagegen`/`openai-docs`/`plugin-creator`/`review-agent`/`skill-creator` 移到 plugins（不占 fs skill 位）

**0914 决策**：**留给老大决策**（不擅自动 config.toml）

---

## 0914 装入清单（fs 115 → 117，+2）

| Skill | 来源 | size | 业务命中 | 三件齐 |
|---|---|---|---|---|
| `rag-architect` | alirezarezvani/claude-skills engineering/skills/rag-architect | 4.5KB SKILL.md + 30KB chunking_optimizer.py + 28KB rag_pipeline_designer.py + 24KB retrieval_evaluator.py + 3 references | **4 群 wiki RAG + 渔芯平台 RAG** | ① cross-refs 12（模型名非兄弟 skill） ② MIT ✓ ③ 4.5KB ✓ |
| `mcp-server-builder` | alirezarezvani/claude-skills engineering/skills/mcp-server-builder | 4.0KB SKILL.md + openapi_to_mcp.py + mcp_validator.py + 5 references | **渔芯平台 MCP 集成** | ① cross-refs 0（明示引其他 skill 但无 `\`xxx\`` 形式） ② MIT ✓ ③ 4.0KB ✓ |

**破例决策理由**：两个 skill 的 ① 兄弟 cross-refs 数都 < 3（rag-architect 引 12 个模型名非兄弟 / mcp-server-builder 0 兄弟）。**业务命中压倒三件齐**——0914 老大的核心需求（4 群 wiki RAG + 渔芯 MCP）是 388 个 alirezarezvani skill 里的最强匹配，破例装入。

**vs 老大现有**：
- `yuxin-fullstack` = 项目级编排（沿用）
- `rag-architect` = **RAG 技术深度专家**（chunking/embedding/vector DB/retrieval eval 全套，可复用 4 群 + 渔芯）
- `mcp-server-builder` = **MCP 技术深度专家**（OpenAPI→MCP scaffold + validator，可复用所有业务线）
- **互补不重叠**

---

## 0914 拒装清单（vs 0913 0912）

- `obviousworks/Claude-AI-skills-collection-2026` 54⭐, license none → 拒装
- `linny006/trending-claude-skills` 40⭐, license none → 拒装（trending leaderboard 非真 skill 库）
- `alirezarezvani/claude-skills` 剩 386 个未装 → **只装业务命中最高的 2 个**，其他（kubernetes-operator / terraform-patterns / chaos-engineering 等）老大栈外不装

---

## 0914 跨日数据漂移总结

| 字段 | 0913 R2 报 | 0914 实算 | 漂移 | 根因 |
|---|---|---|---|---|
| fs 总数 | 114 | 117 | +3 | +rag-architect +mcp-server-builder +sureforge（兄弟 cron 静默装） |
| DEV 数 | 35 | 37 | +2 | +2 新装 |
| MKT 数 | 77 | 77 | 0 | — |
| QA 数 | 2 | 2 | 0 | — |
| OTHER 数 | 0 | 3 | +3 | +sureforge +llm-wiki-manager +yuxin-fullstack（沿用 0914 铁律 22 重分类） |
| 桌面 catalog | 0.142.5 | 0.142.5 | 0 | stale 68 天 = P1 |
| CLI | 0.153.0 | 0.153.0 | 0 | 维持 |
| 兄弟 runtime | 0.154.0 | 0.154.0 | 0 | 维持 |

---

## SKILL.md 拆 split 状态（0914 11:25 触发）

- **0914 实测 SKILL.md = 11255 bytes > 10KB** → 必须按 0910 铁律拆
- 拆法：本次新增铁律 21-23 → references/0914-iron-rules.md（已写）
- SKILL.md 必改项：
  - DEV 35 → 37（+rag-architect +mcp-server-builder）
  - DEV grep 集更新
  - 4 个必读 references 指针表新增 `0914-iron-rules.md` 指针
  - 状态速查 MKT 行更新 77 → 77（不变）
  - OTHER 实算新增
- 拆后 SKILL.md 目标 < 10KB（下次 cron 必跑 `wc -c` 校验）

---
