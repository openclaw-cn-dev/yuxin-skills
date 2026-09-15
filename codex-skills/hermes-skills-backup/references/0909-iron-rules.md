# 0909 cron 实测三条新铁律（plugin 滞后 / CLI 双版本 / SKILL.md 拆 split）

**来源**：2026-09-09 09:00 cron 实跑，原 SKILL.md 106K 触发拆 split 铁律，无法 patch 主文，本文件沉淀本次发现的 3 条新坑。

---

## 铁律 4：openai-curated-remote 插件数 = `codex plugin list | grep installed` 实算，不抄昨日 AGENTS.md

**症状**：AGENTS.md 写「`openai-curated` 7 个 enabled」（0908 末次报告），但 0909 cron 实跑 `codex plugin list` 出 **10 个** enabled：
- google-drive / canva / apollo / plugin-management / sales / product-design / creative-production / openai-templates / deep-research-work / app-69312da8e4dc8191...

**根因**：openai-curated-remote 是远程目录，codex 后台会**自动 enabled 老大手动启用的插件**（包括老大 CLI 配置变化、codex 自启 OAuth 流、或兄弟 cron 启用），cron 不轮询就无法发现。

**铁律**：
- 每日 cron 第 2 步（紧跟 fs 实算）必跑：
  ```bash
  codex plugin list | grep -c "installed, enabled"
  codex plugin list | grep -A 200 "Marketplace \`openai-curated-remote\`" | grep "installed, enabled" | wc -l
  ```
- AGENTS.md 的「已装插件」段**每日实算**填入，不沿用昨日（昨日写的 7 个今日可能 10 个）
- 每次新装插件（无论 cron 还是老大手动）→ 次日 cron 必出现在日报首段（哪怕只是「+1 enabled」也算增量）

**反模式**：
- ❌ AGENTS.md 写「7 个」就不动（漏算 3 个 enabled 插件 = 漏报 3 个新能力）
- ❌ 抄昨日报告 + 加今日新增 = 实际可能低估（后台自动 enabled 无通知）

---

## 铁律 5：Codex CLI 双版本口径 = `~/.codex/config.toml` 的 `model` 字段 vs `codex --version`

**症状**：
- `codex --version` → `codex-cli 0.153.0`（**本地 npm 安装版本**）
- yuxin-skills cron 报头 `🤖 Codex sync: 20260908-2237 | v=0.153.4`（**后端真实跑的版本**）
- `~/.codex/config.toml` `model = "gpt-5.6-terra"`（**配置默认模型**）
- 实际 `codex exec` 跑：model=`gpt-5.6-sol` / provider=`openai` / Hermes 调度路由是 `MiniMax-M3`

**根因**：
- npm 装的是 wrapper CLI（0.153.0），后端真实版本是 OpenAI 后端的 Codex runtime（0.153.4）
- wrapper 启动 → 走 OpenAI 协议 → 路由到 `gpt-5.6-terra` / `gpt-5.6-sol` 模型
- 老大只看到 `codex --version` = 0.153.0，会以为落后 4 个 patch，实际后端跑的是 0.153.4

**铁律**：
- 每日 cron 第 1 段「Codex 版本」必须**双口径并列**：
  ```
  - CLI wrapper: codex-cli 0.153.0（npm 本地，未升级 → 老大手动决策）
  - 后端 runtime: v=0.153.4（来自 yuxin-skills 兄弟 cron 报头）
  - config.toml 默认 model: gpt-5.6-terra / reasoning_effort: low
  - 当前会话路由: MiniMax-M3（provider: minimax，Hermes Agent 调度）
  - 真实 exec 端点: provider=openai / model=gpt-5.6-sol / approval=never / sandbox=read-only
  ```
- 不要再写「CLI 0.153.0 = 后端 0.153.0」这种错配
- patch 升级仍留给老大手动（沿用 0829 铁律），cron 只报 wrapper 与后端差异

---

## 铁律 6：SKILL.md > 100K 触发拆 split（patch/edit 全拒的真正逃逸路径）

**症状**：
- codex-daily-evolution/SKILL.md 长到 **146K**（0909 实测 `wc -c`）
- patch / edit 工具**全拒**（"too large" 错误）
- 0908 立的跨类修正铁律已写进 references/（占 SKILL.md 约 30 行的「🆕 跨类修正铁律（0908 立）」段落实质重复）

**根因**：SKILL.md 长期累加「今日变更」段是反模式——近 2 周留 SKILL.md，更早的归 `references/changelog-<MMDD>.md`。当前 146K = 90+ 天日报 + 铁律段叠加。

**铁律（0909 立）**：
- **下次 cron（0910）第一步 = `wc -c ~/AppData/Local/hermes/skills/devops/codex-daily-evolution/SKILL.md`**
- **>95K → 主动拆 SKILL.md**：把 2026-08 前 13 个今日变更段（0910 → 0901）迁到 `references/changelog-0901-0910.md`
- SKILL.md 只保留：触发条件 / 执行目标 / 编程铁律 / 0908 跨类修正指针 / 0909 三铁律指针 + references 文件清单
- 每加一节都先问：「这段是否 14 天后还重要？」不重要就扔 references/

**逃逸路径（patch 工具拒时）**：
- ✅ `skill_manage write_file` 加新 references/ 文件（已 0909 验证可行）
- ✅ 新铁律段直接写 references/<date>-iron-rules.md，SKILL.md 加一行指针（但当前 146K 加指针也 patch 不进）
- ❌ 不要再加 SKILL.md 段落（除非先拆到 <95K）

---

**0910 cron 落地 TODO**

1. `wc -c SKILL.md` 验当前大小，若仍 >95K → 启动拆 split
2. 拆法：
   - 把 SKILL.md 中「## 已装插件（X 个）」段全系列（0901-0909）迁到 `references/changelog-0901-0910.md`
   - 把 SKILL.md 中「## Skills 总览（X 个）」段系列迁到同一文件
   - 把 SKILL.md 中「## 业务命中」系列迁到同一文件
   - SKILL.md 只保留：触发词 + 5 个执行目标 + 编程铁律 + 4 个 references 指针（cross-class-recategorization / 0909-iron-rules / changelog-0901-0910 / audit-missing-references）
3. 拆完 → `wc -c` 验 <50K → 后续 cron 可以正常 patch SKILL.md

**0910 实操修订（与上面 TODO 略有差异）**：
- ⚠️ 实际 archive 命名 = **`references/full-skill-archive.md`**（不是 `changelog-0901-0910.md`），原因：archive 含执行步骤段（不只是今日变更段），命名更准
- ✅ 0910 实操结果：SKILL.md **146.6KB → 6KB**（24 倍降，113 行），archive = 145KB / 2348 行
- ✅ patch 工具自验证通过：6KB 的 SKILL.md **可正常 patch**（不再被拒）
- ⚠️ SKILL.md 4 个 references 指针 = **类别指针**（P0/P1 优先级 + 用途说明），不是 4 个具体文件名清单（0909 TODO 写的第 4 个 audit-missing-references 实际是 scripts/ 不是 references/）
- ✅ 下次 SKILL.md 长到 50K+ 时，复用同样手法：行 N+ 整段迁 archive（不要按段分类迁，一次性最稳）

## 关联

- 0908 铁律：跨类修正 + 0 装日必跑 diff（见 `references/cross-class-recategorization-iron-rules.md`）
- 0905 铁律：MKT/OTHER 数 = `ls + grep + wc -l` 实算，不按昨日+今日增量推算
- 0829 铁律：Codex CLI wrapper 升级留给老大手动，cron 不自动跨版本号
- audit-missing-references.sh（0908 一次性写好）：`scripts/audit-missing-references.sh`（含 --repo + 指定 skill + 退出码 = 缺失数），下次 cron 必跑验 SKILL.md 引用的 references 全部实存

## 反模式

- ❌ SKILL.md 持续加段不拆（146K 已是反模式峰值）
- ❌ 「拆完不会变好」就不拆（patch/edit 工具已直接拒，再不拆下次 cron 90% 任务失败）
- ❌ 拆到 references/ 后忘了 SKILL.md 加指针（下次 cron 又会找不到铁律）
