# 2026-09-15 Codex 每日进化巡检 runbook

**执行时间**：2026-09-15 09:00 ~ 09:18（cron 模式）
**决策结果**：**0 装日 — 4 候选全拒或暂缓**

---

## 第 1 步：mutable state 实盘校验（沿用 0910 铁律）

```
CLI wrapper: codex-cli 0.153.0 (0911 维持)
version.json latest_version: 0.142.5 (last_checked 2026-07-06 = **stale 69 天 P1 持续**)
fs skills: 117 → 117 (0 装)
fs plugins: 22 enabled (3 marketplace)
SKILL.md: 6254 bytes < 10KB ✓
```

## 第 2 步：兄弟 cron 远端检查

- 0914 sync 已 commit `7daf464` 上线；0915 0 装无需 fetch

## 第 3 步：本 cron 6 维 GitHub search 7d trending

| 维度 | 0915 命中 | 决策 |
|------|------|------|
| Dim1 agent-harness-OS | affaan-m/ECC 258402⭐ MIT 50MB | **拒装**（mega-repo + 与 9 个现有 skill 重叠） |
| Dim2 UI/UX design | nextlevelbuilder/ui-ux-pro-max 127638⭐ MIT 8MB | **暂不装**（6 个 SKILL.md > 10KB + 与 refactoring-ui 重叠 + 业务命中弱） |
| Dim3 30天热点调研 | mvanhorn/last30days 62037⭐ MIT 59MB | **暂不装**（254KB SKILL.md + 13 个付费 API keys） |
| Dim4 科学计算 | K-Dense-AI/scientific-agent-skills 44929⭐ MIT 258MB | **拒装**（老大栈外） |
| Dim5 营销 skill | coreyhaines31/marketingskills 已装（50/50 覆盖） | **0 装** |
| Dim6 其他 | — | **0 装** |

## 第 4 步：上游源 diff 校验

**marketingskills (coreyhaines31) 50 个 vs 本地 117 个**：
- 缺 3 个：`aso` / `sms` / `events` — **全在 9 点 cron 拒装清单**（无 App / 付费 / 产品上线阶段才用）
- 拒装沿用铁律

**social-media-skills (blacktwist) 14 个 vs 本地**：
- 0 缺（本地 14/14 全覆盖）

## 第 5 步：4 候选评估（拒装决策树）

### 5.1 affaan-m/ECC 拒装决策

**仓库概况**：
- 258402⭐ MIT 50MB (2026-09-14 最后 push)
- 292 skills + 68 agents + 94 commands + harness hooks + rules
- 描述："The agent harness performance optimization system. Skills, instincts, memory, security, and research-first development for Claude Code, Codex, Opencode, Cursor and beyond."
- topics: ai-agents / anthropic / claude / claude-code / developer-tools / llm / mcp / productivity

**拒装 3 重证据**：
1. **mega-repo 风险**：292 个 skill 触发 0914 铁律 21（单仓库 > 100 = mega-repo，必 sparse-checkout）
2. **重叠证据**：292 skills 中仅 `harness-optimizer` / `loop-operator` / `autonomous-loops` / `continuous-agent-loop` / `eval-harness` 5 个有潜在独立价值，但与现有 9 个 skill 重叠：
   - `using-superpowers` (obra) — agent skill 编排
   - `subagent-driven-development` — subagent 委派
   - `executing-plans` — plan-then-execute
   - `dispatching-parallel-agents` — parallel agent orchestration
   - `test-driven-development` — TDD 流程
   - `verification-before-completion` — completion 验证
   - `spec-literal-execution` — spec literal
   - `systematic-debugging` — debug
   - `fix-ci` — CI 修复
3. **0914 决策约束**：0914 cron 已破例 2 次（rag-architect + mcp-server-builder），0915 决策回归铁律不再破例装 mega-repo

**保留意见**：ECC 整体质量极高（agent harness OS），但**不与现有 9 个 skill 互补**——装入必然产生 namespace 冲突 + context budget 撑爆

### 5.2 nextlevelbuilder/ui-ux-pro-max-skill 暂不装决策

**仓库概况**：
- 127638⭐ MIT 8MB (2026-09-15 当天 push)
- 单仓库 6 个 skill: ui-ux-pro-max / design / design-system / ui-styling / brand / banner-design / slides
- 79 UI styles + 192 color palettes + 74 font pairings + 119 UX guidelines + 25 chart types + 22 tech stacks
- platforms: claude / cursor / windsurf / codex / qoder / opencode / continue / etc. 19 平台

**暂不装 3 重证据**：
1. **SKILL.md 全部 > 10KB**（0910 铁律）：
   - ui-ux-pro-max: 16183B
   - design: 13748B
   - ui-styling: 10956B
   - design-system: 7706B
   - banner-design: 7216B
   - brand: 3623B
   - slides: 1764B
2. **context budget 警告触发**：6 个 skill 全部装入 → 117 + 6 = 123 skills（突破铁律 23 临界点 115）
3. **业务命中弱**：与现有 `refactoring-ui` 部分重叠（UI 设计）；4 业务线（美食/养殖/设备/A 股）+ 渔芯平台 不强依赖 UI/UX 升级路径

**保留意见**：老大如有 UI/UX 升级需求可单独评估 ui-styling / brand 2 个（SKILL.md 11KB + 3.6KB）

### 5.3 mvanhorn/last30days-skill 暂不装决策

**仓库概况**：
- 62037⭐ MIT 59MB (2026-09-15 当天 push)
- 1 个 skill: last30days（254KB SKILL.md）
- 8 数据源：Reddit / X / YouTube / TikTok / HN / Polymarket / GitHub / Web
- 13 个 optionalEnv API keys

**暂不装 3 重证据**：
1. **SKILL.md = 254KB**（0910 铁律 10KB 红线的 25 倍），单 skill context budget 就撑爆
2. **13 个付费 API keys**：SCRAPECREATORS_API_KEY / OPENAI_API_KEY / XAI_API_KEY / X_BEARER_TOKEN / OPENROUTER_API_KEY / PERPLEXITY_API_KEY / PARALLEL_API_KEY / BRAVE_API_KEY / APIFY_API_TOKEN / AUTH_TOKEN / CT0 / BSKY_HANDLE / BSKY_APP_PASSWORD
3. **API keys 全部未配**：老大当前 0 配任何 key，装入也无法跑

**业务命中**：4 群选题调研强相关（小红书/抖音/养殖/美食 30 天热点追踪），缺 API 配 → **留给老大决策**（是否要配 API + 装入）

### 5.4 K-Dense-AI/scientific-agent-skills 拒装决策

**仓库概况**：
- 44929⭐ MIT 258MB (2026-09-14 最后 push)
- 165 scientific skills + 100+ scientific databases

**拒装 1 重证据**：
- 老大栈外（渔芯/水产/美食/AI 训练师/求职 业务线不碰科学计算）
- 与 0915 4 业务线无交集

---

## 第 6 步：Hermes 版本检查（沿用 0913 R2 升级阈值铁律）

- 当前 v0.19.0 (2026-07-20, 本地 commit `b4f8c491`)
- 最新 v0.21.2 (v2026.9.11, 2026-09-11)
- 落后 **55 天 ≥ 30 天 = P1** ✅ 报（0914 报 54 天 → 0915 报 55 天，+1 天）
- **不在 cron 升级**（hermes.exe 自锁 + ZIP fallback 风险）→ 留老大手动

## 第 7 步：Codex version.json stale 校验

- 当前 latest_version: 0.142.5
- last_checked_at: 2026-07-06 (= **stale 69 天** P1）
- 0914 报 68 天 → 0915 报 69 天，+1 天
- **留给老大决策升级**

## 第 8 步：AGENTS.md drift 监控（沿用 0914 铁律 22）

```python
fs = 117 / MKT 77 / DEV 35 / QA 2 / OTHER 3 / classified unique 117 / drift = 0 ✓
```

0 装日兄弟 cron 无静默装风险，但漂移校验必跑（0914 教训）。

## 第 9 步：0 push 沿用 8-20 铁律

- 本地领先 origin N commits（含 0914 等），**等老大决策 push**

## 第 10 步：飞书推送

- 沿用 0827 起铁律：阻塞 → final response 由系统投递
- 不强行推送

---

## 0915 总结

- ✅ **0 装日**：4 候选全拒或暂缓（拒装 2 / 暂缓 2）
- ✅ 跨类实算稳定（MKT 77 / DEV 35 / QA 2 / OTHER 3 = 117）
- ✅ 上游源 diff：marketingskills 缺 3 全拒装 / social-media-skills 0 缺
- ✅ SKILL.md 维持 6254 bytes < 10KB
- ✅ 新写 references/2026-09-15-evolution-run.md（本文件）
- ✅ AGENTS.md 更新 0915 段 + 总览段（115 行新增）
- ⚠️ Hermes v0.19.0 → v0.21.2 落后 55 天 = P1，待老大手动升级
- ⚠️ Codex version.json stale 69 天 = P1 持续
- ⚠️ 飞书推送阻塞中（沿用铁律 → final response 投递）
- ℹ️ yuxin-skills 0 push 沿用 8-20 铁律（本地领先 origin N commits 待老大）

## 0915 决策总览（4 候选拒装/暂缓对比表）

| 候选 | stars | 体积 | SKILL.md | 业务命中 | 拒装/暂缓理由 |
|---|---|---|---|---|---|
| affaan-m/ECC | 258402⭐ | 50MB | 多个 (小) | 中（harness OS） | mega-repo + 与 9 个现有 skill 重叠 |
| nextlevelbuilder/ui-ux-pro-max | 127638⭐ | 8MB | 全部 > 10KB | 弱（与 refactoring-ui 重叠） | 0910 铁律 SKILL.md 红线 + 业务命中弱 |
| mvanhorn/last30days | 62037⭐ | 59MB | 254KB | 强（4 群选题） | 254KB SKILL.md 撑爆 + 13 个付费 API 未配 |
| K-Dense-AI/scientific-agent-skills | 44929⭐ | 258MB | 多个 | 无 | 老大栈外 |

## 0915 vs 0914 跨日漂移

| 字段 | 0914 报 | 0915 实算 | 漂移 |
|---|---|---|---|
| fs 总数 | 117 | 117 | 0（0 装日） |
| MKT | 77 | 77 | 0 |
| DEV | 35 | 35 | 0 |
| QA | 2 | 2 | 0 |
| OTHER | 3 | 3 | 0 |
| 桌面 catalog | 0.142.5 | 0.142.5 | 0 |
| CLI | 0.153.0 | 0.153.0 | 0 |
| 兄弟 runtime | 0.154.0 | 0.154.0 | 0 |
| SKILL.md size | 6254B | 6254B | 0 |
| Hermes stale | 54 天 | 55 天 | +1 天 |
| Codex stale | 68 天 | 69 天 | +1 天 |
| 飞书阻塞 | 17 天 | 18 天 | +1 天 |
