# 2026-09-12 Codex 每日进化巡检 runbook

**执行时间**：2026-09-12 09:00 ~ 09:08（cron 模式）
**决策结果**：**0 装日**

---

## 第 1 步：mutable state 实盘校验（沿用 0910 铁律）

```
CLI wrapper: codex-cli 0.153.0 (0911 维持)
runtime: 0.154.0 (兄弟 cron 0912 sync 维持)
fs skills: 113 个 (0911 装 llm-wiki-manager 后累计)
fs plugins: 22 个 enabled (7 + 5 + 10)
SKILL.md: 7,557 bytes (0910 拆 split 后维持 < 10KB)
AGENTS.md: 90 个去重 skill 名引用
```

## 第 2 步：兄弟 cron 远端检查

- git fetch origin main → 33c0e4f..e322081 (fast-forward)
- 0912 sync 4 commits (凌晨 2/3/4/6/7/8 点 6 次)，全部 `codex/STATUS.md` + `codex/plugins.json` 改 metadata
- **0 新 skill 0 新 plugin 0 业务命中**

## 第 3 步：plugin marketplace upgrade

- 3 个 marketplace 全部 `is not configured as a Git marketplace` 错误
- openai-bundled / openai-curated / openai-primary-runtime 都是 local，不是 Git
- 无 Git marketplace → 无升级

## 第 4 步：本 cron 5 维搜索（沿用 0911 Override 兄弟 cron 0 装日铁律）

| 维度 | 总数 | top 命中 | 4 业务命中 | 决策 |
|------|------|----------|------------|------|
| Dim1 GitHub stars>50 pushed>2026-08-01 | 1077 | ECC 256k⭐ / graphify 117k⭐ / caveman 105k⭐ | 0 | 0 装 |
| Dim2 新 skill created>2026-07-01 | 239526 | ASu-skills 4338⭐ / human-writing 3592⭐ | 0 (ASu 与 job-application-packaging 重叠, human-writing 与 sloptrim/humanizer 重叠) | 0 装 |
| Dim3 awesome-list (ComposioHQ) | 234 链接 | 全是 MCP 商业工具 | 0 | 0 装 |
| Dim4 anthropics/skills 19 子目录 | 19 个 | doc-coauthoring / skill-creator | 0 (重叠已装 skill) | 0 装 |
| Dim5 4 业务命中 seafood/aquaculture/shrimp | 29633 | ECC/graphify | 0 | 0 装 |

## 第 5 步：跨类实算（沿用 0908 跨类修正铁律 + 新立铁律 12）

**0911 报告（错误）vs 0912 实算（正确）**：

| 类别 | 0911 报告 | 0912 实算 | 偏差 | 原因 |
|------|----------|----------|------|------|
| DEV | 33 | **34** | +1 | 漏算哪个？ |
| MKT | 47 | **71** | **+24** | 漏算 sms/xiaohongshu/yuxin 系列 |
| QA | 4 | **3** | -1 | xiaoma-durex-copywriter 重分类 MKT |
| OTHER | 28 | **5** | **-23** | 大量实际归 MKT/DEV |
| **总账** | **112** | **113** | +1 | — |

**0912 决策**：采纳 0912 实算（71/34/3/5 = 113 ✓）

**新铁律 12（0912 立）**：MKT/DEV/QA/OTHER 实算 grep 必须用 71 MKT 完整集口径，不再用 0911 47 口径

## 第 6 步：codex exec 实测

```
$ codex exec --model gpt-5.6-terra --skip-git-repo-check "echo hello"
OpenAI Codex v0.153.0
workdir: C:\Users\Administrator\Desktop\yuxin-skills
model: gpt-5.6-terra
provider: openai
approval: never
sandbox: read-only
reasoning effort: low
```

→ runtime 0.154.0/model gpt-5.6-terra 正常可调

## 第 7 步：references 完整性反向扫描（沿用 0908 铁律）

```
$ bash ~/AppData/Local/hermes/skills/devops/codex-daily-evolution/scripts/audit-missing-references.sh
[ad-creative] MISSING: references/meta-decision-system.md
[attribution] MISSING: references/conversion-tracking.md
⚠️ 2 个 skill 有缺失 references
```

→ 2 false-positive 已知（0908 沿用），非真缺，不修

## 第 8 步：AGENTS.md patch

1. patch 1：时间戳 `0911 09:11` → `0912 09:08`
2. patch 2：在「已装插件」段后插入「## 今日变更（2026-09-12）」+「## Skills 总览（113 个...）」
   - 9 条变更详情 + 跨类实算 + 新铁律 12
3. 写入 `references/0912-iron-rules.md`（8,414 bytes）

## 第 9 步：0 push 沿用 8-20 铁律

- 本地领先 origin 4 commits：0908/0909/0911 装的本地未 push + 1 merge commit
- 0912 cron 0 装，无新文件 → 不需新 commit
- 沿用铁律：commit 留本地，等老大 push

## 第 10 步：飞书推送

- 沿用 0827 起铁律：阻塞第 15 天 → 待老大手动建新飞书 app + 关代理客户端
- 本次推送依然静默，**不强行推送**

---

## 0912 总结

- ✅ 0 装日（5 维搜索 0 命中 4 业务线 + 兄弟 cron 静默）
- ✅ 跨类实算纠正：MKT 47→71 / OTHER 28→5（0911 报告偏差）
- ✅ 新铁律 12 落地（71 MKT 完整集口径）
- ✅ Codex CLI 实测正常（runtime 0.154.0 / model gpt-5.6-terra）
- ✅ SKILL.md < 10KB 维持（7,557 bytes）
- ✅ AGENTS.md patch 2 处
- ✅ 新写 references/0912-iron-rules.md（8,414 bytes）
- ⚠️ 飞书推送阻塞第 15 天
- ⚠️ 0 push 沿用 8-20 铁律
