# 0918-0921 cron 铁律 + 数据失真纠正（0921 立）

## 铁律 45 — AGENTS.md 数据必 fs 真算（0918 cron C 盘/插件数失真 → 0921 纠正）

**症状**：0918 cron 报 **C 盘 11G 95% P1** + **22 个 enabled 插件**，**实测均为错**：
- **C 盘实盘**：`df -h /c` = **172G/201G = 86%**（0918 cron 算 11G 95% 是把 `available` 字段误读为 `used`，反了）
- **enabled 插件数**：0918 AGENTS.md 报 22，实盘 `codex plugin list | grep "installed, enabled" | wc -l` = **20**

**铁律**：
- ✅ C 盘必跑 `df -h /c` 实测，不脑算
- ✅ 插件数必 `grep "installed, enabled" | wc -l`，不写「22」/「7+5+10」脑算
- ✅ 落后数必 `releases?per_page=15` 看 `prerelease` 字段双轨报数（沿用 0918 铁律 39）
- ✅ fs 真算必 0916 铁律 30 + 0918 铁律 42 三处校验（for-loop + 分类器 + 兄弟 cron canonical 对账）

**0921 实盘对账**：
| 项 | 0918 报 | 0921 实 | Δ |
|---|---|---|---|
| C 盘 11G 95% P1 | 11G 95% | 172G/201G = **86%** | -9% |
| AGENTS.md plugin 报 | 22 | **20** | -2 |
| 落后 stable | 2 | **3**（+ rust-v0.155.1） | +1 |
| Hermes 落后 | 57 天 | **60 天** | +3 |
| catalog stale | 74 天 | **77 天** | +3 |

---

## 铁律 46 — cron 断链监控（0919/0920 旺财进化 cron 缺 → 0921 首跑恢复）

**症状**：0918 cron 后 yuxin-skills 末次旺财进化 commit = `7c3366a`（2018-09-18 09:03:48），**0919/0920 9am 旺财进化 cron 全缺**，今天 0921 9am 是断链 **3 天后首跑**。

**6am 小红书 cron 0919-0921 全成功**（V97/V98/V99）→ **不是 hermes.exe 全挂**，是 9am cron 单独调度问题。

**铁律**：
- ✅ cron 启动第 1 步必 `git log --since=YYYY-MM-DD --grep="旺财进化 MMDD"` → 缺日数 ≥ 2 → 在日报首部报告「cron 断链恢复」
- ✅ 6am cron 跑 ≠ 9am cron 跑，两个 schedule 独立检查
- ✅ ef6c6fe 类 openclaw-cn-dev 自动 sync commit 不算旺财进化 cron 跑过（看 author 字段）

**根因待查**（3 套方案留给老大决策）：
- 方案 A：保留现状（断链 3 天正常，cron 调度偶然失败）
- 方案 B：跑 `hermes cron list` 查 0919/0920 旺财进化 cron 的 schedule 是否被系统 disable
- 方案 C：手动补 commit 0919/0920 双日报回 yuxin-skills

---

## 铁律 47 — SKILL.md 拆 split 临界值（0921 实盘 10.23KB）

**症状**：`codex-daily-evolution/SKILL.md` 当前 **10480 bytes = 10.23KB**，**踩 0910 铁律 10KB 阈值**（+0.23KB / +2.3%）。

**0910 铁律原话**：「SKILL.md > 10KB → patch/edit 工具全拒（0910 实测 = 146K 已被拒）」，但 **10.23KB 临界** vs 10KB 边界的判定此前未明确。

**铁律**：
- ✅ SKILL.md ≥ 10KB → **必拆 split**（不留临界值，避免下次 patch 因 +1KB 直接拒）
- ✅ 拆 split 必跑：`主体内容（铁律段/今日变更）→ references/YYYY-MM-DD-iron-rules.md`
- ✅ SKILL.md 只留：触发条件 + 5 个执行目标 + 编程铁律 + references 指针 + 状态速查
- ✅ 0921 临界值 **0922 cron 必拆**（不在 0921 拆避免影响日报 commit 路径稳定性）

---

## 铁律 48 — Anthropic-Cybersecurity-Skills 818 skill / 网络安全框架拒装（0921 立）

**症状**：mukul975/Anthropic-Cybersecurity-Skills **817 cybersecurity skill** Apache-2.0 跨 6 框架（MITRE ATT&CK / NIST CSF 2.0 / MITRE ATLAS / D3FEND / NIST AI RMF / MITF1 F3）。

**业务交集**：0（渔芯/水产/美食/AI 训练师/求职不碰网络安全框架）

**铁律**：
- ✅ mega-repo ≥ 500 skill + 业务交集 = 0 → 必拒装（沿用 0915 铁律 21「拒绝装 mega-repo」+ 0916 铁律 31「multi-pack 业务命中过滤」）
- ✅ 不破例硬装「看着像好东西」skill（沿用 0918 铁律 43「业务命中度高就破 0910 铁律硬装 → 必拒装」）

---

## 铁律 49 — dimillian/Skills README-only 拒装（0921 重申 0917 R3）

**症状**：Dimillian/Skills repo README + CONTRIBUTING + LICENSE 三件套，**实际 SKILL.md 内容未实化**。

**铁律**：
- ✅ mega-repo 仅 README 无 SKILL.md 实质内容 → 必拒装（不脑补「应该有」）
- ✅ 必 clone 到 `~/Desktop/eval-repos/dimillian-Skills/` 看实际目录结构再决策，不信 README 描述

---

## 0921 cron 5 维搜索总结

| 候选 | 决策 | 核心原因 |
|---|---|---|
| `vibeforge1111/keep-codex-fast`（0918 cron 留档 daily-0918/kcf.tar.gz） | 沿用维持 / 老大决策 | SKILL.md 12.08KB > 10KB，0918 cron 拒装但业务命中极强 |
| `Dimillian/Skills` | 拒装 | README-only，无实质 SKILL.md |
| `mukul975/Anthropic-Cybersecurity-Skills` 818 skill | 拒装 | 业务外（网络安全框架） |
| `rohitg00/awesome-claude-code-toolkit` 135 agents | 拒装 | mega-repo + install.sh 动 ~/.codex/config.toml（0916 铁律 29） |
| `composio-community/awesome-codex-skills/mcp-builder` | 沿用维持 | 已有 mcp-server-builder 388 mega-repo alirezarezvani 覆盖 |

**0921 0 命中 + 0 装**（沿用 0917 R2 铁律 33「走 web_search + 0917 铁律 34「0 装日不动 AGENTS.md」）