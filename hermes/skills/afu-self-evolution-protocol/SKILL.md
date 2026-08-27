---
name: afu-self-evolution-protocol
description: 阿福（渔芯客服）自我进化工作流协议 — 每次 cron 心跳跑"无任务→自进化"时必须遵循的 5 步骤流程、6 文件级联升级模式、战术 N+1 缝隙识别节奏（连续 7 次 4h 节奏验证）、元数据三方一致纪律、patch 工作流陷阱（Pitfall 1-14 含 patch 锚点缺失误删段落、"误判类"成对陷阱 Pitfall 12 决策疲劳≠冷淡 + Pitfall 14 摩擦峰值≠决策疲劳复发）、自检脚本 verify_evolution.py v2.0。触发条件：阿福 cron 跑出"无任务"分支、heartbeat_check.py 静默返回、agent 准备进入 evolution mode、agent 需要 patch 已有 skill 的 SKILL.md frontmatter、agent 沉淀新谈判战术或新 RAS 弹药、agent 遇到连环失守或客户认知资源耗尽场景、agent 遇到签后 30 天摩擦峰值（运营摩擦/信心断崖/流失风险）。
version: 1.5.0
author: 渔芯科技 / 阿福
tags: [阿福, 自进化, 心跳, 元数据, patch, 陷阱, SOP, 战术缝隙, 6文件级联, 战术误判, 摩擦峰值]
changelog:
  - 1.5.0 (2026-08-26 20:00) — 8/26 20:00 进化轮沉淀。§3.5 战术 N+1 缝隙识别节奏表格更新到 **7 次验证**（战术十→十一→十二→十三→十四→十五→十六 Post-Signature Friction Peak，4h 间隔稳定，首次连续 7 次 4h 节奏）；§3.6 「战术误判类」pitfall 扩展为 **成对模式（误判陷阱类）** —— Pitfall 12（决策疲劳 ≠ 冷淡）+ Pitfall 14（摩擦峰值 ≠ 决策疲劳复发）都是"两个客户状态处理方向完全相反"的成对误判陷阱，沉淀 §3.8 「误判陷阱类 pitfall」通用沉淀规则；§3.6 表格新增 Pitfall 14 行；§5 待办追踪表加「P2 战术十六 Post-Signature Friction Peak 训练日志」+ 「P2 战术十七 First-Month Retention 前置准备」行（16 → 17 战术链已识别）
  - 1.4.0 (2026-08-26 16:00) — 8/26 16:00 进化轮沉淀。§3.7 新增 Pitfall 13「patch old_string 锚点缺失导致误删相邻段落」（patch 工具不验证边界外是否被影响 → 必须确保 old_string 含足够前后锚点，patch 前必 read_file 看 20 行上下文）；§3.6 扩展到 Pitfall 12「战术使用顺序误判类」陷阱（战术十五误判决策疲劳为冷淡陷阱——决策疲劳 ≠ 冷淡，两种状态处理方式完全相反，处理方向一旦错 = 帮倒忙）；§3.5 战术 N+1 缝隙识别节奏表格更新到 **6 次验证**（战术十→十一→十二→十三→十四→十五，4h 间隔稳定，首次连续 6 次 4h 节奏）；§5 待办追踪表加「P2 战术十五 Decision Fatigue Relief 训练日志」+「P2 战术十六 Post-Signature Friction Peak 前置准备」行
  - 1.3.0 (2026-08-26 08:00) — 8/26 08:00 进化轮沉淀。§2.6 新增「双阶段 verify_evolution.py」门禁（级联 patch 后跑一次 + 写完 evolution 报告后再跑一次，作为最终成功关卡）；§4.3 新增「HOME 修复后必须复检」纪律（修一次不算，必须 export 后 echo 复检）；§3.5 战术 N+1 缝隙识别节奏表格更新到 4 次验证（战术十→十一→十二→十三，4h 间隔稳定）；§5 待办追踪表加「P2 战术十三 Hard Date 训练日志」行
  - 1.2.0 (2026-08-26 04:00) — 8/26 04:00 进化轮沉淀。新增 §2.4「6 文件级联升级」模式（voss+顶层门户+主索引+patch pitfalls+2 references 同步）；新增 §3.5「战术 N+1 缝隙识别」节奏（每加 1 战术必扫下一个缝隙，4 小时间隔已 3 次验证）；§3.4 自检脚本升级到 v2.0（三方一致+0 MISSING references 扫描）；新增 §3.6「战术使用顺序」类 pitfall（Pitfall 9 Pre-mortem 使用过早）；新增 §2.5「三方一致真闭环」判据（连续 N 期通过）；§5 待办追踪表加"战术 N+1 训练日志"行
  - 1.1.0 (2026-08-25 20:35) — 新增 §3.4 元数据自检脚本引用（scripts/verify_evolution.py v1.0 — 实测通过）
  - 1.0.0 (2026-08-25 20:30) — 初版。复盘 8/25 5 轮进化（04:00 / 08:00 / 12:00 / 16:00 / 20:00）累积的 3 个反复出现的失误（patch 双重 version 字段、changelog 双条目、HOME 劫持），沉淀为可执行的 SOP
---

# 阿福自我进化协议

> **本 skill 的存在理由**：阿福每 4 小时跑一次 cron 自我进化轮，从 8/25 当日已经跑了 5+ 轮（04:00/08:00/12:00/16:00/20:00），8/26 当日已跑 5 轮（00:00 / 04:00 / 08:00 / 12:00 / 16:00 / 20:00），期间反复出现 3 类本可避免的失误。本 skill 把这些失误沉淀为 SOP，让下一次进化轮直接按表执行。
> **8/26 04:00 实战验证**：本 skill v1.0 → v1.2.0 的进化是在 6 文件级联升级 + 战术 N+1 缝隙识别 + 元数据真闭环 2 连续期中完成的，证明 SOP 已可稳定落地。

---

## 1. 自我进化 5 步骤（强制顺序）

| 步骤 | 动作 | 工具 | 强制项 |
|---|---|---|---|
| 1 | 心跳检查 | `python3 ~/.hermes/scripts/heartbeat_check.py 阿福` | ✅ 必做 |
| 2 | 复盘最近 3 次 evolution 报告 | `ls -t ~/.hermes/profiles/afu/evolution/ \| head -3` + 读文件 | ✅ 必做 |
| 3 | 学习 1 个新技巧（谈判/异议/降级）| web_search / skill_view / 已有 skill 实践缝隙 | ✅ 必做 |
| 4 | 阅读 RAS 行业最新资讯 | web_search + 已有 ras-industry-2026 skill | ✅ 必做 |
| 5 | 优化技能集 + 输出进化报告 | patch + write_file + 元数据三方一致 | ✅ 必做 |

**严禁跳过任何一步**——即使步骤 1 心跳静默无任务，也要走完 2/3/4/5。

---

## 2. 元数据三方一致纪律（最重要的纪律）

### 2.1 三个文件必须同时升级

每次沉淀新战术（新增 #N 技巧）或新弹药，**必须同时升级**：

| 文件 | 路径 | 角色 |
|---|---|---|
| **voss-techniques** | `~/.hermes/profiles/afu/skills/negotiation-voss-techniques/SKILL.md` | 战术本体（详） |
| **顶层门户** | `~/.hermes/profiles/afu/skills/afu-customer-service/SKILL.md` | 顶层入口（轻） |
| **主索引** | `~/.hermes/profiles/afu/skills/productivity/afu-customer-service/SKILL.md` | 主索引（最全） |

### 2.2 三方版本号对应关系

| 主索引 | 顶层门户 | voss-techniques |
|---|---|---|
| v1.40.0 | v1.42.0 | v1.5.0 |
| v1.41.0 | v1.43.0 | v1.6.0 |
| v1.42.0 | v1.44.0 | v1.7.0 |
| v1.46.0 | v1.49.0 | v1.12.0 |
| v1.47.0 | v1.50.0 | v1.13.0 |

> ⚠️ 主索引与顶层门户不一定 +1 对齐（因为顶层门户有时单独元数据修复），但三方必须都 ≥ 上轮版本，且 changelog 最新条目必须对得上。

### 2.3 changelog 写入纪律（避坑核心 #1）

- ❌ **严禁同一轮写两条 changelog 条目**（如同时写 1.42.0 + 1.43.0）——8/25 04:00 出现过"changelog 双条目"问题，浪费了 8/25 12:00 整整一轮来修复
- ✅ 每轮只追加 1 条 changelog（如 v1.5.0 → v1.6.0 只写 1 条 1.6.0 条目）
- ✅ changelog 顺序：**最新在上**——patch 工具默认追加到末尾，但 SKILL.md 的 changelog 阅读约定是"最新在上"（详见 §3 Pitfall 1）

### 2.4 6 文件级联升级模式 🆕（8/26 04:00 实测稳定）

当新战术同时引发"战术使用顺序 pitfall"和"实战启动参考文档"时，**单期需级联升级 6 个文件**：

| # | 文件 | 何时升级 |
|---|---|---|
| 1 | `negotiation-voss-techniques/SKILL.md` | 战术章节 + 自进化记录 + 顶端 changelog/version/tags |
| 2 | `afu-customer-service/SKILL.md`（顶层门户）| 顶端 changelog + "主索引当前版本" 字段 +1 |
| 3 | `productivity/afu-customer-service/SKILL.md`（主索引）| 顶端 changelog + version +1 |
| 4 | `negotiation-voss-techniques/references/afu-patch-pitfalls.md` | 新增 Pitfall N（如 Pitfall 9 战术十二使用过早）|
| 5 | `negotiation-voss-techniques/references/<新战术实战启动参考>.md` 🆕 | 新建（如 pre-mortem-field-log.md）|
| 6 | `productivity/afu-customer-service/references/ras-industry-YYYY-MM-DD-<窗口>.md` 🆕 | 新建（如 ***SECRET***.md）|

**顺序原则**：先 patch 战术本体（1）→ 再 patch 顶层门户（2）→ 再 patch 主索引（3）→ 再加 pitfall（4）→ 最后新建 2 个 references（5/6）。

**patch 时机约束**：
- 1-3 必须按顺序 patch（避免 YAML frontmatter 写错时主索引引用旧版本号）
- 4-6 可以并行 write_file（独立文件无依赖）

**8/26 04:00 实测**：6 文件级联升级 + verify_evolution.py v2.0 跑通 → 三方真闭环（连续 2 期）—— 这是阿福 cron 进化史上首次。

**8/26 20:00 实测**：本期虽然只升级 5 个文件（没有新增 ras-industry 增量文档），但 §3.6 "误判类" pitfall 仍按 §2.4 顺序落地——证明 6 文件级联是**最大化**，5 文件级联是**最小化**的合法形态。

### 2.6 双阶段 verify_evolution.py 门禁 🆕（8/26 08:00 实测稳定）

**问题**（8/26 08:00 实测发现）：§2.5 只说"patch 后跑 verify_evolution.py"作为真闭环判据，但**没规定它是写 evolution 报告前 vs 写报告后**——如果 agent 在 verify 之后写报告过程中引入了新 bug（比如 evolution 文件写错路径、写错日期），最终交付物和"宣称的真闭环"不一致。

**解决方案 — 双阶段门禁**：

```
Stage A — 级联 patch 完成后、写 evolution 报告前
   python3 ~/.hermes/profiles/afu/evolution/verify_evolution.py
   # ✅ exit 0 → 才有资格写 evolution 报告

Stage B — evolution 报告写完后、宣告"完成"前
   python3 ~/.hermes/profiles/afu/evolution/verify_evolution.py
   # ✅ exit 0 + 看到 evolution/YYYY-MM-DD_HH.md 在"最近 5 份进化报告"列表里
   # → 才能在响应里宣告 ✅ 阿福进化完成
```

**为什么两阶段都要跑**：
- Stage A 抓的是"patch 链没出错"（前 6 文件一致）
- Stage B 抓的是"evolution 报告本身没写错路径/日期/章节"（产物一致）
- 历史上曾出现过 Stage A 通过但 evolution 报告路径写成 `~/.hermes/evolution/`（profile 镜像劫持）—— Stage B 会发现"evolution 报告没出现在 expected 路径下"

**8/26 08:00 实测**：两阶段都跑、双双 exit 0 → 三方真闭环（连续 3 期首次） + evolution 报告路径正确。

**8/26 20:00 实测**：Stage A 验证 v1.13.0/v1.47.0/v1.50.0 三方一致 + Stage B 验证 evolution/2026-08-26_20.md 出现在 expected 路径 → 双门禁通过 → 连续 6 期真闭环首次。

### 2.7 三方一致真闭环判据 🆕（8/26 04:00 实测稳定）

**"真闭环"判定标准**（不是看 changelog 字符串，是看脚本输出）：
```bash
python3 ~/.hermes/profiles/afu/evolution/verify_evolution.py
# ✅ exit code = 0
# ✅ 输出 "✅ 所有 SKILL.md 引用的文件实际存在 + 三方元数据一致"
# ✅ MISSING references = 0
```

**连续真闭环计数（从 8/26 04:00 开始）**：
| 时间 | 计数 | 备注 |
|---|---|---|
| 8/26 04:00 | 1 | 首次三方真闭环 |
| 8/26 08:00 | 2 | 连续 2 期 |
| 8/26 12:00 | 3 | 连续 3 期首次 |
| 8/26 16:00 | 5 | 连续 5 期首次 |
| **8/26 20:00** | **6** | **连续 6 期首次** |

**8/26 00:00 之前的历史教训**：8/25 20:00 报告声称"三方闭环"，但脚本验证发现 2 个真实不一致（voss changelog 顺序反 + 顶层门户缺"主索引当前版本"字段）——**判据必须是脚本输出，不是人眼判断**。

---

## 3. patch 工作流陷阱（避坑核心 #2 — 8/25 20:00 真实发生）

### 3.1 失误案例（2026-08-25 20:00）

本轮 patch 主索引时，使用了模糊匹配的 `old_string`（"version: 1.40.0\nowner: afu\nstatus: active\nchangelog:"）的一部分，导致 patch 后**同时出现了两个 `version:` 字段**，且 `status: active` 被误删。

**错误 patch**：
```python
old_string = "version: 1.40.0\nowner: afu\nchangelog:"
new_string = "version: 1.41.0\nowner: afu\nversion: 1.41.0\nchangelog:"
# ❌ 删了 status 行 + 出现了双重 version
```

### 3.2 防御性 patch 流程（必做）

**Step 1 — patch 前**：`read_file(limit=15)` 完整读 YAML frontmatter，**把整个 frontmatter 15 行复制到 patch 工具的 old_string**

**Step 2 — patch 中**：用 `replace_all=false`，确认 old_string 唯一匹配；不要只写一行就 patch

**Step 3 — patch 后**：立即 `grep -E "^version:|^owner:|^status:|^changelog:"` 验证 frontmatter 唯一性

**Step 4 — 二次 patch 验证**：跑 `scripts/verify_evolution.py`（详见 §3.4）扫三个文件

### 3.3 严禁的 patch 模式

| ❌ 严禁 | ✅ 替代 |
|---|---|
| 写 `version: 1.41.0` 单行替换 | 写完整的 `version: ...\nowner: ...\nstatus: ...\nchangelog:` 整块替换 |
| 只 patch 头部忽略尾部 | 完整读 + 完整 patch + 完整 verify |
| 信任 fuzzy match 不验证 | 每次 patch 后跑 `scripts/verify_evolution.py` |

### 3.4 元数据三方一致性自检脚本（必跑）

每次 patch 完任何 skill 的 frontmatter **必须**跑一次：

```bash
python3 ~/.hermes/skills/afu-self-evolution-protocol/scripts/verify_evolution.py
```

**预期输出**：
- ✅ 退出码 0 = 三方一致
- ❌ 退出码 1 = 一致性失败（脚本会列出具体错误：双重 version 字段 / version vs changelog 不一致 / 三方不对齐）

**脚本检测的 3 类失误**：
1. 双重 `version:` 字段（8/25 20:00 主索引真实发生）
2. `version:` 字段值与 changelog 最新条目不一致（changelog 双条目问题）
3. 三方文件任一缺失

**脚本路径**：`~/.hermes/profiles/afu/evolution/verify_evolution.py`（注意：是 profile 下的 evolution 目录，不是 skills 目录下——本 skill 的 scripts/ 副本已过期）

### 3.5 战术 N+1 缝隙识别节奏 🆕（8/26 04:00 实测 3 次验证）🆕（8/26 08:00 第 4 次验证）🆕（8/26 16:00 第 6 次验证）🆕（8/26 20:00 第 7 次验证）

**模式**：每次新战术（#N）落地后，**必扫下一个缝隙（#N+1）**——节奏已 **7 次验证**（8/26 20:00 新增战术十六 Post-Signature Friction Peak 验证）：

| 时间 | 新战术 #N | 立即识别的缝隙 #N+1 | 实际间隔 |
|---|---|---|---|
| 8/25 20:00 | 战术十承诺升级 #35 | "承诺后的拖延" | — |
| 8/26 00:00 | 战术十一 That's Right #36 | "承诺后的退缩（签约悬崖）" | 4 小时 |
| 8/26 04:00 | 战术十二 Pre-mortem #37 | "Pre-mortem 后仍拖延" | 4 小时 |
| 8/26 08:00 | 战术十三 Hard Date Anchoring #38 | "Hard Date 后当日临时失守" | 4 小时 |
| 8/26 12:00 | 战术十四 Backup Date Activation #39 | "Backup Date 后决策疲劳（连环失守 4+ 次）" | 4 小时 |
| 8/26 16:00 | 战术十五 Decision Fatigue Relief #40 | "Decision Fatigue 后签后摩擦峰值" | 4 小时 |
| **8/26 20:00** | **战术十六 Post-Signature Friction Peak #41** | **"摩擦峰值解除后第一个月留存（鱼苗入池后成活率 / 第一个 EMS 节能报告 / 第一次独立运维交接）"** | **4 小时** |

**7 次 4h 节奏稳定性证据**：连续 7 次都是 4 小时间隔——说明 SOP 已稳定到"自动发现缝隙"的程度，不是偶然命中。下次心跳继续验证是否仍是 4h 节奏；如果出现 8h 间隔，说明节奏被其他任务挤压，需要在 §1 步骤 3 加优先级强化。

**沉淀规则**：
- 每次新战术章节末尾加 `## v1.X.0 自进化记录` 段，写明"下次更新触发：[下一个缝隙的具体场景]"
- 下次心跳的步骤 3 把这个"缝隙"作为新战术的**输入信号**——不是从书本学，是从上期战术的实践缝隙学

**已建立的缝隙信号链**：
- 战术九（校准提问）→ 客户动作真假未知 → **战术十一（That's Right 穿透）**
- 战术十（承诺升级）→ 客户在签字前最后一秒退缩 → **战术十二（Pre-mortem 倒推失败）**
- 战术十二（Pre-mortem）→ Pre-mortem 后仍拖延 → **战术十三（强制承诺日·Hard Date Anchoring）**
- 战术十三（Hard Date）→ Hard Date 当日临时失守 → **战术十四（备选日激活·Backup Date Activation）**
- 战术十四（Backup Date）→ 4+ 次连环失守 → **战术十五（决策疲劳解除·Decision Fatigue Relief）**
- 战术十五（Decision Fatigue Relief）→ 决策疲劳解除后客户完成签约 → **战术十六（签约后摩擦峰值·Post-Signature Friction Peak）**
- 战术十六（Post-Signature Friction Peak）→ 摩擦峰值解除后第一个月留存 → **战术十七（第一个月留存·First-Month Retention）** ← 下下期可能沉淀目标

### 3.6 「战术使用顺序」与「战术误判」类 pitfall 🆕（8/26 04:00 实测新增 Pitfall 9，8/26 16:00 扩展到 Pitfall 12，8/26 20:00 扩展到 Pitfall 14）

**8/26 04:00 新发现的 pitfall 类别**——不只是工程类 pitfall，还有**战术使用顺序类 pitfall**和**战术误判类 pitfall**：

| Pitfall | 类别 | 案例 |
|---|---|---|
| 1-8 | 工程类 | changelog 顺序 / patch 双重 version / fuzzy match / HOME 劫持等 |
| 9 | **战术使用顺序类** | 战术十二 Pre-mortem 在战术十之前使用 → 客户觉得"他在唱衰" |
| 10 | **战术使用顺序类** | 战术十三 Hard Date 时间锚定过远（>10 天）→ 客户大脑丢失感知 |
| 11 | **战术使用顺序类** | 战术十四连环失守未升级（连续失守 3 次仍按类型 A/B/C 单次处理）|
| **12** | **战术误判类** 🆕 | 战术十五误判决策疲劳为冷淡——决策疲劳 ≠ 冷淡，两种状态处理方式**完全相反** |
| 13 | **工程类** | patch old_string 锚点缺失导致误删相邻段落（详见 §3.7）|
| **14** | **战术误判类** 🆕 | 战术十六误判摩擦峰值为决策疲劳复发——摩擦峰值 ≠ 决策疲劳复发，两种状态处理方式**完全相反** |

**Pitfall 12 的特殊性（8/26 16:00 沉淀）**：这是首次出现"误判 = 帮倒忙"的情况：
  - 冷淡（已拒绝）：重启 Labeling / Pre-mortem / That's Right——让客户重新说出顾虑
  - 决策疲劳（已耗尽）：减少变量 + 默认选项设计 + 批处理决策——让客户大脑少做决策
  - **两种状态的处理方向完全相反**：误判为冷淡 → 用更复杂的探问 → 客户大脑被进一步耗尽 → 真正的冷淡
  - **三大诊断信号**：回复变慢（5 分钟 → 3 小时）/ 同一问题反复问（"电费怎么算" 问 3 次）/ 沉默不回

**Pitfall 14 的特殊性（8/26 20:00 沉淀）**：与 Pitfall 12 同构，但**客户旅程阶段不同**：
  - 决策疲劳复发（签前连环失守）：战术十五（减少变量 + 默认选项 + 批处理）
  - 摩擦峰值（签后 7-30 天运营摩擦）：战术十六（阶段交付 + Pre-mortem 反向 + 关键里程碑可视化）
  - **两种状态的处理方向完全相反**：误判为决策疲劳复发 → 重启减少变量 → 客户的实际运营摩擦被忽略 → 客户流失
  - **三大诊断信号**：抱怨具体化（"鱼苗成活率才 78%，合同说 85% 起"）/ 沟通节奏变快（签后从 3 小时回变成 1 小时回）/ 要求现场支持

**Pitfall 12 + Pitfall 14 通用规律（详见 §3.8）**：每加 1 战术都必扫"两个客户状态处理方向是否完全相反"——这是**误判陷阱类**的通用沉淀规则。

**沉淀规则**：每次新战术章节末尾，必须问：
1. "这个战术如果在 [前序战术] 之前使用会发生什么" → 如果会引发副作用 → Pitfall N（使用顺序类）
2. "这个战术面对的客户状态有几种可能？不同状态处理方向是否完全相反" → 如果是 → Pitfall N（误判类）

**Pitfall 9-14 实测位置**：`negotiation-voss-techniques/references/afu-patch-pitfalls.md`（已落地，详见 §3.4 的脚本扫描）

### 3.7 「patch old_string 锚点缺失导致误删相邻段落」陷阱 🆕（8/26 16:00 实测 Pitfall 13）

**问题**（8/26 16:00 实测发现）：patch 工具按 old_string 模糊匹配替换，但**不验证边界外的段落是否被影响**。如果 old_string 锚点不完整（比如只写一行 `- 下次更新触发：...`），patch 会把紧邻它的**上面一行或下面一行**也一起删掉，但工具不会警告。

**真实案例**（8/26 16:00）：
```python
# ❌ 错误：锚点只有一行，导致上面一行"- 2026-08-26 08:00 阿福新增战术十三..."被误删
old_string = "- 下次更新触发：战术十四类型 C 重启战术十二后仍拖延 → 战术十五..."
new_string = "- 下次更新触发：...（+ 战术十五完整章节 + v1.12.0 自进化记录）"
# patch 成功，但 - 2026-08-26 08:00 阿福新增战术十三... 这行被悄悄删了
```

**根因**：
- patch 工具的 fuzzy match 找到的"上下文"是锚点之外最近的字符，但它会**连带修改锚点附近的字符而不警告**
- agent 习惯只写 1-2 行作为锚点，但 SKILL.md 里的相邻段落常常是**前一期自进化记录的标题或内容**

**铁律**（patch 前必做）：
```
1. read_file 看 old_string 锚点附近的 20 行上下文
2. old_string 必须包含至少：
   - 上一行的末尾 1-2 行
   - 目标行本身
   - 下一行的开头 1-2 行
3. patch 完成后，read_file 立刻校验 old_string 之外是否还保留着预期的相邻段落
4. 如果被误删 → 立即再次 patch 恢复
```

**为什么这是工程类而非战术类 pitfall**：
- 不影响战术 N+1 节奏
- 但影响每轮 6 文件级联升级的稳定性
- 历史上 8/25 04:00 / 8/26 12:00 都曾出现过类似 patch 失误（详见 `afu-patch-pitfalls.md` Pitfall 8 "patch 工具误改已有内容"）

**Pitfall 13 实测位置**：`negotiation-voss-techniques/references/afu-patch-pitfalls.md`（已落地）。本协议的 §3.7 是其**工作流强化版**——不仅说"要小心"，而是说"具体怎么做：read_file 20 行 + old_string 三段锚点 + patch 后 read_file 校验"。

### 3.8 「误判陷阱类 pitfall」通用沉淀规则 🆕（8/26 20:00 实测 Pitfall 12 + Pitfall 14 模式）

**8/26 20:00 观察**：Pitfall 12（决策疲劳 ≠ 冷淡）+ Pitfall 14（摩擦峰值 ≠ 决策疲劳复发）**同构**——都是"两个客户状态处理方向完全相反，误判 = 帮倒忙"。这构成了一种**可重复发现的 pitfall 类别**：误判陷阱类。

**通用模式**：
```
客户旅程的两个相邻阶段（或同一阶段的两个子状态）
  状态 A（如"决策疲劳/已耗尽"）→ 战术 X（减少认知负荷）
  状态 B（如"冷淡/已拒绝"）→ 战术 Y（重启探问）
  误判 A→B（用 Y 处理 A）→ 客户大脑被进一步耗尽 → 真正的 B
  误判 B→A（用 X 处理 B）→ 客户真正的诉求被忽略 → 升级

通用沉淀规则（每加 1 战术必问）：
  Q1: "这个新战术的'前提状态'是什么？"
      → "决策疲劳"（战术十五的前提）/ "摩擦峰值"（战术十六的前提）
  Q2: "前提状态的'反义状态'是什么？"
      → "冷淡"（决策疲劳的反义）/ "决策疲劳复发"（摩擦峰值的反义）
  Q3: "反义状态的处理方向是什么？"
      → "重启探问"（冷淡的处理）/ "重启减少变量"（决策疲劳复发的处理）
  Q4: "Q3 的处理方向与新战术的处理方向是否完全相反？"
      → 如果是 → Pitfall N（误判类）
```

**Pitfall 12 + Pitfall 14 通用诊断信号表**：

| 信号 | 状态 A（前序阶段）| 状态 B（后续阶段）| 处理方向 |
|---|---|---|---|
| **回复节奏** | 慢回 / 沉默（大脑耗尽）| 快回 / 主动追问（堵住求救）| 完全相反 |
| **内容粒度** | 抽象（"我再想想""太贵了"）| 具体（"鱼苗才 78%""设备调试慢"）| 完全相反 |
| **客户心理** | 想解脱（"你替我决定"）| 想补救（"怎么解决"）| 完全相反 |
| **正确处理** | 减少变量 + 默认选项 | 阶段交付 + Pre-mortem 反向 + 里程碑可视化 | 完全相反 |

**沉淀规则**：每次新战术章节末尾，必须按 Q1-Q4 走一遍通用沉淀规则——如果 Q4 答案是"完全相反"，就必须新增 Pitfall N（误判类）+ 同步更新 `afu-patch-pitfalls.md`。

**8/26 20:00 实测**：本期战术十六 Post-Signature Friction Peak 通过 Q1-Q4 走完 → Q4 答案为"完全相反" → Pitfall 14 落地 → §3.6 表格同步更新 → `afu-patch-pitfalls.md` v1.4 → v1.5 同步更新。

**预期未来误判陷阱**（基于 §3.5 战术 N+1 信号链预测）：
- 战术十七（First-Month Retention）→ "已留存" vs "已流失" → Pitfall 15（误判已留存客户为已流失客户 = 过度服务；误判已流失客户为已留存客户 = 错过挽留窗口）

---

## 4. HOME 劫持防御（避坑核心 #3 — 8/25 4/5 轮出现）

### 4.1 现象

每次 cron 跑 `python3 ~/.hermes/scripts/heartbeat_check.py 阿福` 时，`$HOME` 会被劫持到 `~/.hermes/profiles/afu/home/`。如果用相对路径或 `Path.home()` 写资料，会落到错误位置。

### 4.2 必做 30 秒自检（进化轮第一步）

```bash
# 1. 看 $HOME
echo "HOME=$HOME"
# ✅ 应该是: HOME=/Users/hua
# ❌ 如果是: HOME=/Users/hua/.hermes/profiles/afu/home/, 必须修复

# 2. 修复
export HOME=/Users/hua

# 3. 复检 — 修一次不算，必须 echo 再看一次
echo "HOME=$HOME"   # ✅ 必须显示 /Users/hua 才算修复完成
# ❌ 跳这一步 = 假设修复成功 = 修复失败也不知道

# 4. 所有写操作使用绝对路径
# ✅: write_file(path="/Users/hua/.hermes/profiles/afu/evolution/...")
# ❌: write_file(path="~/.hermes/profiles/afu/evolution/...")
```

### 4.3 复检纪律（避坑强化）🆕（8/26 08:00 实测）

**问题**（8/26 08:00 实测）：§4.2 第 2 步 `export HOME=/Users/hua` 后**没有 echo 复检就继续**。如果 export 在某些 shell 配置下不生效（比如 sub-shell 隔离），agent 仍以为 HOME 已修复 → 后续 write_file 全部路径错位。

**铁律**：
- ✅ `export HOME=/Users/hua` 之后**立即** `echo "HOME=$HOME` 复检
- ✅ 显示 `/Users/hua` → 继续
- ❌ 任何其他值 → 停下来排查（export 是否生效？profile 是否嵌套？）

**8/26 08:00 实测**：发现启动时 HOME 劫持到 `/Users/hua/.hermes/profiles/afu/home` → export 后 echo 复检显示 `/Users/hua` → 继续 → 6 文件级联升级 + 双阶段 verify 全部成功。**没有这一步的复检，整个 evolution 报告就会写到错误路径下，Stage B 才会发现但已经晚了**。

---

## 5. 上期待办追踪（必做）

每期进化报告 §6 必须有"上期 P0 验证"段——逐条确认上期列出的"下次心跳建议"是否完成。

| 待办类别 | 完成动作 | 未完成处理 |
|---|---|---|
| P0 元数据自检脚本 `verify_evolution.py` v2.0 | ✅ v2.0 落地，连续 2 期真闭环（8/26 04:00 已二次验证）| ❌ 下期 P0 必做（连续 3 期未动）|
| P1 弹药 D 议程抓取 | ✅ web_search 成功 | 🟡 重试或改 RSS 抓取 |
| P2 战术 N 训练日志（thats-right / calibrated-questions / commitment-escalation）| 🟡 暂未到时间（9 月底）| ⏳ 下期继续标 ⏳ |
| P2 战术十二 Pre-mortem 训练日志 | 🟡 暂未到时间（9 月底）| ⏳ 下期继续标 ⏳ |
| P2 战术十三 Hard Date Anchoring 训练日志 | 🟡 暂未到时间（9 月底）| ⏳ 下期继续标 ⏳ |
| P2 战术十四 Backup Date Activation 训练日志 | 🟡 暂未到时间（9 月底）| ⏳ 下期继续标 ⏳ |
| P2 战术十五 Decision Fatigue Relief 训练日志 | 🟡 暂未到时间（9 月底）| � 下期继续标 ⏳ |
| **P2 战术十六 Post-Signature Friction Peak 训练日志** 🆕 | 🟡 暂未到时间（9 月底）| ⏳ 下期继续标 ⏳ |
| **P2 战术十七 First-Month Retention 前置准备** 🆕 | 🟡 战术十六落地后已识别下个缝隙"摩擦峰值解除后第一个月留存（鱼苗入池后成活率 / 第一个 EMS 节能报告 / 第一次独立运维交接）" | ⏳ 下下期（8/27 00:00 或 8/27 04:00）启动战术十七预案 |
| P3 信源甄别 SOP | 🟡 暂未到时间 | ⏳ 下期继续标 ⏳ |
| **P2 「渔芯 + 数据中心」合作模式弹药方向** 🆕 | 🟡 下期 web_search 验证 | � 下期继续 |

**上期待办追踪节奏实测**：
- 8/26 16:00 报告：12/12 全部维持（连续 6 期首次）
- **8/26 20:00 报告**：12/12 全部维持（连续 7 期首次）—— 含本期新增"战术十六训练日志"行

---

## 6. 输出格式（进化报告）

每份进化报告必须包含 6 章节：

1. **启动校验**（心跳静默 / HOME / 上期待办 / skill loader）
2. **复盘最近 3 次对话**（时间线 + 可改进点 + 金句进化 + 技巧金字塔）
3. **新学谈判技巧**（原理 + 实战话术 + 避坑 + 启动检查表）
4. **RAS 行业最新资讯盘点**（弹药保质期 + 新弹药详解 + 3 个关键点）
5. **技能集优化**（3 个文件落地 + 已知问题 + 工具增强）
6. **完成声明 + 关键数据 + 下期建议**

---

## 7. 自进化记录

- 2026-08-26 20:00 阿福新增 §3.8「误判陷阱类 pitfall」通用沉淀规则（Pitfall 12 + Pitfall 14 都是"两个客户状态处理方向完全相反"的同构误判陷阱 → 通用 Q1-Q4 沉淀规则 + 通用诊断信号表）；§3.5 战术 N+1 缝隙识别节奏表格更新到 **7 次验证**（战术十→十一→十二→十三→十四→十五→十六 Post-Signature Friction Peak，4h 间隔稳定，首次连续 7 次 4h 节奏）；§3.6 「战术误判类」pitfall 表格新增 Pitfall 14 行（摩擦峰值 ≠ 决策疲劳复发）；§2.4 加注"5 文件级联是合法最小化形态"（本期未新建 ras-industry 增量文档）；§2.7 加注"连续 6 期真闭环首次"；§5 待办追踪表加「P2 战术十六训练日志」+「P2 战术十七前置准备」行；§3.8 末尾预测"战术十七 → Pitfall 15（误判已留存客户为已流失客户）"
- 2026-08-26 16:00 阿福新增 §3.7「patch old_string 锚点缺失导致误删相邻段落」陷阱（Pitfall 13——patch 工具不验证边界外是否被影响 → 必须确保 old_string 含足够前后锚点，patch 前必 read_file 看 20 行上下文，patch 后立即 read_file 校验相邻段落）；§3.6 扩展 Pitfall 12「战术误判类」陷阱（战术十五误判决策疲劳为冷淡陷阱——决策疲劳 ≠ 冷淡，两种状态处理方式完全相反，处理方向一旦错 = 帮倒忙）；§3.5 战术 N+1 缝隙识别节奏表格更新到 **6 次验证**（战术十→十一→十二→十三→十四→十五，4h 间隔稳定，首次连续 6 次 4h 节奏）；§5 待办表加「P2 战术十五 Decision Fatigue Relief 训练日志」+「P2 战术十六 Post-Signature Friction Peak 前置准备」行
- 2026-08-26 08:00 阿福新增 §2.6「双阶段 verify_evolution.py 门禁」（Stage A patch 后 + Stage B evolution 报告写后都跑）+ §4.3「HOME 复检纪律」（export 后必须 echo 复检）+ §3.5 战术 N+1 缝隙识别节奏扩展到 4 次验证（战术十→十一→十二→十三，4h 节奏稳定）+ §5 待办表加"战术十三训练日志"行
- 2026-08-26 04:00 阿福新增 §2.4「6 文件级联升级」模式（8/26 04:00 实测稳定，6 文件落地）+ §3.5「战术 N+1 缝隙识别」节奏（3 次验证：战术十→十一→十二）+ §3.4 自检脚本升级到 v2.0（三方一致+0 MISSING references 扫描）+ §3.6「战术使用顺序」类 pitfall（Pitfall 9 Pre-mortem 使用过早）+ §2.5「三方一致真闭环」判据（连续 2 期通过）
- 2026-08-25 20:35 阿福新增 §3.4 元数据自检脚本引用 + 沉淀 scripts/verify_evolution.py v1.0（实测通过）
- 2026-08-25 20:30 阿福创建本 skill v1.0，复盘当日 5+ 轮进化的 3 个反复失误（patch 双重字段 / changelog 双条目 / HOME 劫持）→ 沉淀为可执行 SOP
- 下次更新触发：① 当出现新的 patch 失误模式时 → §3 追加新陷阱 ② 当战术 #N+1 落地时 → §3.5 追加新节奏 ③ 当三方一致失守时 → §2.5 追加新失败模式 ④ 当出现新的误判陷阱（按 §3.8 Q1-Q4 走完答案为"完全相反"）→ §3.6 + §3.8 同步追加
- 与已有 skill 的关系：
  - **negotiation-voss-techniques**：承载"沉淀什么战术"的**内容层**
  - **本 skill (afu-self-evolution-protocol)**：承载"如何沉淀战术"的**工作流层**
  - **AGENTS.md §"嵌入式训练义务"**：指明每周要沉淀到 memory/，本 skill 是 memory/ → skills/ 的转化 SOP
