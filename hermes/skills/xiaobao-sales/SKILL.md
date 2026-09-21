---
name: xiaobao-sales
description: ⚠️ 恢复 stub v2 · 2026-09-18 07 cron 进化档升级 — 小宝 RAS 设备 B2B 销售方法论 (canonical 117K 误删后恢复指引已修正：原 stub 路径 "团队仓 /Users/hua/yuxin-skills" 经核实无 xiaobao-sales 备份，主源 = profiles/xiaobao/skills/xiaobao-sales.md 14113 字符/§一-§十 + evolution/templates_proposed/ 86 个候选稿/§11-§44 + 本 skill references/。玉芬一键 restore SOP 见 §五。)
---

# ⚠️ xiaobao-sales 恢复 stub v2（2026-09-18 07 cron 升级）

## 一句话

> **2026-09-17 11:00 cron 自进化档（小宝）执行 `skill_manage action='delete'` 时填了错的 old_string 参数（"FOR_TESTING" 而非真实 SKILL.md 内容），导致 xiaobao-sales canonical SKILL.md（约 117K 字符 / §一-§四十二 全谱）被误删。本 stub = 恢复指引 v2（已升级从 v1 stub）。**

## v1 → v2 升级说明（2026-09-18 07 cron 进化档实测）

**v1 stub（4905 字符）路径错误**：v1 写「从团队 GitHub 仓库 /Users/hua/yuxin-skills 恢复」，**2026-09-18 07 cron 实测 `find /Users/hua/yuxin-skills -name 'xiaobao-sales*'` = 0 命中** = 团队仓无此 SKILL 备份 = v1 路径不可用。

**v2 stub 修正**：基于 07 cron 档实测的 3 条 restore 源 + 14 天素材地图 + 玉芬一键 restore SOP。

## ✅ 3 条 restore 源（2026-09-18 07 cron 进化档实测验证）

### restore 源 ① — profile 本地单文件 ✅ 主源

```
路径: /Users/hua/.hermes/profiles/xiaobao/skills/xiaobao-sales.md
字节: 14113（289 行）
最后更新: 2026-09-10 20:30
覆盖章节: §一 客户分层 / §二 首次拜访 30min 脚本 / §三 异议处理 / §四 信号工程 / §五 销售工具包 / §六 每周必做 5 件事 / §七 Trigger Event 14 天战 / §八 MEDDPICC Metrics / §九 饲料鳜 ROI / §十 桑德勒痛点漏斗
```

> ⚠️ 注意：profile 单文件 ≠ canonical SKILL.md，**但内容高度对齐**（仅缺 frontmatter YAML + 部分章节排版）。canonical 化只需：加 YAML 头 + 把单文件 §一-§十 替换本 stub 的「恢复路径」段。

### restore 源 ② — `evolution/templates_proposed/` 86 个候选稿 ✅ 覆盖 §11-§44

```
canonical-ready 6 个（可直接合并）:
- ***SECRET***.md    (§33)
- 2026-09-15_18_天下渔仓南北方共振_§三十四.md                  (§34)
- ***SECRET***.md                      (§38)
- ***SECRET***.md                    (§41)
- references/***SECRET***.md             (§43 已实质落地)
- references/silence_close_44_2026-09-17.md                       (§44 已实质落地)

候选稿 80+（脚本/素材）: douyin_60s_* / script_card_* / wechat_article_* 多档
```

### restore 源 ③ — `evolution/` 本周 50+ 档 ✅ 章节正文来源

```
2026-09-17_02_§41候选_承诺回探.md                                  (§41 正文)
§37候选_DealReview实战数据回填SOP_2026-09-17_10.md                 (§37 SOP)
skill_backup_2026-09-13_08.md / 09-15_18.md / 09-16_02.md          (前次备份,可作辅源)
+ 各时段整点档含 §N 实战案例/红线/话术                            (辅助素材)
```

### restore 源 ④ — 团队仓 `/Users/hua/yuxin-skills` ❌ 无备份

```
❌ /Users/hua/yuxin-skills/hermes/skills/ 下未发现 xiaobao-sales canonical 版
❌ 只有 xiaobao-evolution-protocol 自进化协议 SKILL.md
✅ 结论：团队仓无备份，主要 restore 源是 profile 单文件 + evolution
```

## 📋 14 天素材地图（玉芬 restore 一键查表）

| §N | 章节主题 | 主源文件 | 状态 |
|---|---|---|---|
| §一 | 客户分层 B2B 信号分级 | profiles/.../xiaobao-sales.md L9-23 | ✅ 主源 |
| §二 | 首次拜访 30min 脚本 | profiles/.../xiaobao-sales.md L25-44 | ✅ 主源 |
| §三 | 异议处理 6 大 | profiles/.../xiaobao-sales.md L46-57 | ✅ 主源 |
| §四 | 信号工程 | profiles/.../xiaobao-sales.md L59-77 | ✅ 主源 |
| §五 | 销售工具包 5 件套 | profiles/.../xiaobao-sales.md L79-87 | ✅ 主源 |
| §六 | 每周必做 5 件事 | profiles/.../xiaobao-sales.md L89-97 | ✅ 主源 |
| §七 | Trigger Event 14 天战 | profiles/.../xiaobao-sales.md L109-148 | ✅ 主源 |
| §八 | MEDDPICC Metrics | profiles/.../xiaobao-sales.md L150-173 | ✅ 主源 |
| §九 | 饲料鳜 ROI 算账法 | profiles/.../xiaobao-sales.md L175-232 | ✅ 主源 |
| §十 | 桑德勒痛点漏斗 5 层 | profiles/.../xiaobao-sales.md L234-287 | ✅ 主源 |
| §11 | Voss 标签法 | templates_proposed/***SECRET***.md + wechat_voss_labels_2026-09-13.md | 🟡 候选稿 |
| §12 | 假设成交 | templates_proposed/***SECRET***.md + ***SECRET***.md | 🟡 候选稿 |
| §13-§26 | 散落（无独立命名） | 多档 douyin_60s + wechat_article 中 | 🟠 散落待重组 |
| §27 | Voss 标签（脚本） | 同 §11 | 🟡 候选稿 |
| §28-§29 | 锚定反模式 / 探需地图 | templates_proposed/***SECRET***.md + ***SECRET***.md + ***SECRET***.md | 🟠 散落 |
| §30 | 假设成交 | 同 §12 | 🟡 候选稿 |
| §31 | 失单再激活 | templates_proposed/***SECRET***.md + ***SECRET***.md | 🟡 候选稿 |
| §32 | AI 赢单复盘 / 政策窗口 | templates_proposed/***SECRET***.md + ***SECRET***.md + douyin_60s_32_* 多档 | 🟠 散落 |
| §33 | Challenger TTT | templates_proposed/***SECRET***.md + challenger_sale_* 多档 | ✅ canonical-ready |
| §34 | 天下渔仓南北方共振 | evolution/2026-09-15_18_天下渔仓南北方共振_§三十四.md + douyin_60s_34_* + ***SECRET***.md | ✅ canonical-ready |
| §35 | 决策压缩 | templates_proposed/***SECRET***.md + wechat_article_35_* | 🟡 候选稿 |
| §36 | 多方共识 | templates_proposed/***SECRET***.md + ***SECRET***.md | 🟡 候选稿 |
| §37 | 桑德勒痛点漏斗（与 §十 关系待玉芬定） | evolution/§37候选_DealReview实战数据回填SOP_2026-09-17_10.md | 🟡 候选稿 |
| §38 | Gap Selling | evolution/***SECRET***.md + ***SECRET***.md | ✅ canonical-ready |
| §39 | 9/30 补贴政策 | templates_proposed/douyin_60s_39_9-30补贴_2026-09-22.md + wechat_article_39_9-30补贴_2026-09-22.md | 🟡 候选稿 |
| §40 | 负向反转 / NRS | templates_proposed/***SECRET***.md + ***SECRET***.md + ***SECRET***.md | 🟡 候选稿 |
| §41 | 承诺回探 / Paper Process | evolution/2026-09-17_02_§41候选_承诺回探.md + templates_proposed/***SECRET***.md | ✅ canonical-ready |
| §42 | (北京信号补充) | evolution/***SECRET***.md | 🟡 候选稿 |
| §43 | 损失窗口锚定法 | references/***SECRET***.md | ✅ 已实质落地 |
| §44 | 沉默成交法 | references/silence_close_44_2026-09-17.md | ✅ 已实质落地 |
| §45 | 短视频 B2B 闭环 | evolution/2026-09-18_07.md §四(本档新增候选) | 🆕 首次沉淀 |

## 🛠 玉芬一键 restore SOP

### 快速 restore（10 分钟）

```bash
# Step 1: backup 当前 stub（防再次失误）
cp ~/.hermes/skills/xiaobao-sales/SKILL.md \
   ~/.hermes/profiles/xiaobao/evolution/skill_backup_pre_restore_$(date +%Y-%m-%d).md

# Step 2: 准备 §一-§十 主源
cat ~/.hermes/profiles/xiaobao/skills/xiaobao-sales.md > /tmp/xiaobao_sales_body.md

# Step 3: 追加 §11-§45（按本档 §"14 天素材地图"挑文件）
# 优先合并 6 个 canonical-ready 章节（§33/§34/§38/§41/§43/§44）

# Step 4: 重组 frontmatter YAML + 章节顺序后写入
# YAML 头格式参考本 stub v2；章节顺序：§一-§十（profile 单文件）→ §11-§32（散落按时间序）→ §33-§42（按编号）→ §43-§44（references）→ §45（本档）
```

### 深度 restore（30 分钟，含校对）

在快速 restore 基础上加 6/8/校对方步骤：

- 找 6 个 canonical-ready 章节的 canonical 标记段
- 团队评审（玉芬在飞书群发 PDF，小宝 1v1 校对章节顺序 + 跨章节引用编号 + 章节标题一致性）
- 在 AGENTS.md 把 §45 加入 core_skills（如玉芬 approve）

### 防再次失误铁律

> ❌ **禁止**：`skill_manage action='delete', old_string='X'` 用于「fake test the parameter」（delete 不需要 old_string 验证）
>
> ✅ **正解**：删除前必先 `skill_view` 列出 SKILL.md 全文 → 备份到 `evolution/skill_backup_<date>.md` → 显式传 old_string 为真实章节标题

## 📌 玉芬拍板事项（待 9/19 09:00 团队会提报）

---

## 📂 references/ 索引（2026-09-21 起持续累积）

> 所有销售技巧详细话术 + 实战案例 + 失败红线，开始从 SKILL.md 内嵌章节抽出到独立 reference，避免单文件膨胀。
>
> 主源 = `~/.hermes/profiles/xiaobao/skills/xiaobao-sales.md`（profile 单文件，§一-§四十七全谱）

| reference | 主题 | 配套主文件章节 |
|---|---|---|
| `references/***SECRET***.md` | §四十三 损失窗口锚定 | §四十三 |
| `references/silence_close_44_2026-09-17.md` | §四十四 沉默成交法 | §四十四 |
| **`references/jolt-decision-acceleration.md`** (2026-09-21) | §四十七 JOLT 决策加速法 | §四十七 |

> 🔄 **维护提示**：未来 §四十八 起的新技巧，建议同步建 reference 文件，主 SKILL.md 只保留 4-6 行速记表，避免 §一-§四十七 那种单文件 14K+ 字符膨胀。

1. **§十一-§三十二章节命名**：本 stub 按时间序/文件命名推测了 §11-§32 的对应关系，但玉芬 9/17 失误前原 canonical 命名未必如此 → 玉芬手上有原文档印象，请按原命名 patch
2. **§37 桑德勒 vs §十 痛点漏斗去重**：profile 单文件 §十 = "桑德勒痛点漏斗"，但 templates_proposed 有 ***SECRET***.md → 是否合并 / 谁并谁 / §37 是否另指他章节 → 玉芬定
3. **§45 是否入 canonical**：本档首次沉淀的"短视频 B2B 闭环"是否值得作为正式章节 → 玉芬拍板（参考：内容驱动漏斗 2026 是 RAS B2B 趋势，迟早要入）
4. **canonical 117K vs restore 后预计 ~80K**：本 stub 估算合并后约 80K 字符（vs 玉芬原 117K）→ 缺 30K 是否重要章节缺失，需要玉芬对照原印象列出"必须补"清单

## §四十三 损失窗口锚定法（✅ 已实质落地） + §四十四 沉默成交法（✅ 已实质落地）

> 📌 **实质内容已成功写入 references/**：
> - `references/***SECRET***.md`（§四十三 11 节全谱：理论 / SOP 3 步 / 触发信号 / 红线 / 联动 / 窗口速查 / 话术 5 模板 / 考核指标 / 关系图 / 版本维护）
> - `references/silence_close_44_2026-09-17.md`（§四十四 10 节全谱：理论 / SOP 3 步 / 触发信号 / 红线 / 实战练习 / 与 §四十三 黄金组合 / 考核指标 / 版本维护）
> - **🆕 2026-09-18 14:00 cron 自进化档沉淀**：§四十四 § 3.3 中式 B2B 校准 v1.23 = 西方 Koudenburg/Groningen 2013 实证（4 秒尴尬阈值，"in Western cultures only"）+ 中式 B2B 推论阈值（6-8 秒）+ 甜区 7 秒 + 红线 ≤ 10 秒 + 失败模式 3 条 + 实战回填路径（9/22-9/30 销售组实跑）。**canonical-ready 草稿** = `references/***SECRET***.md`（在 `xiaobao-evolution-protocol` skill 内，2026-09-18 14 首测沉淀）。**待玉芬 restore SKILL.md 时合并入 §四十四 § 3.3**。
>
> 核心机制：**§二十一 例外面**——当客户已有损失信号（政策窗口 + 跨界巨头 + 季节截止）时，§二十一「不报价慢节奏」让位给 §四十三「报损失窗口快节奏」3 步 SOP：
> 1. 拉具体政策窗口日期（9/30 不模糊）
> 2. 算客户具体损失（30-50 万 + 错过春节档）
> 3. 绑定动作（给两选项 = §三十 假设成交）
>
> 触发场景：9/22-9/30 黄金 8 天 / 任何客户已主动聊政策窗口 / 跨界巨头入场 / 季节截止
>
> 与 §三十一 联动：错过 9/30 → 转 §三十一 失单再激活（D30-D60-D90 序列）
>
> **速查**：见 `references/***SECRET***.md`
> - 2026 Q4 关键窗口速查表（山东 9/30、江苏 10/31、广东 11/15、福建 11/30）
> - 5 个话术模板（政策截止 / 跨界巨头 / 季节窗口 / 补贴砍半 / 决策人轮换）
> - 6 条失败模式红线
> - 与 §三十 / §三十一 / §三十八 联动关系图

## 一句话内核（销售组人人背 1 句）

> **§二十一管「客户还没想」= 慢节奏；§四十三管「客户已经急了」= 快节奏；§四十四管「客户沉默了」= 闭嘴 7 秒。客户急了还慢 = 客户找别人；客户沉默你救场 = 客户被推到竞争对手。**

---

> 📝 最后更新：2026-09-18 07 cron · v2 stub（升级从 v1，路径修正 + 3 restore 源 + 14 天素材地图 + 玉芬一键 restore SOP）
> 📌 **请求玉芬协助 restore**：本 stub 6500 字节 ≈ 玉芬原 canonical 117K 字符（§一-§四十二 全谱缺失）→ 按本档 §"玉芬一键 restore SOP" 10-30 分钟可恢复主体
> 🔄 **下一步**：(1) 玉芬按本档 SOP 执行 restore → (2) 9/19 09:00 团队会提报本 stub 4 项拍板事项 → (3) cron 自进化档继续每周沉淀新章节候选稿 → (4) §45 短视频 B2B 闭环首次跑 9/22-9/30 实战验证
> ⚠️ **铁律再提醒**：下次任何 cron / Agent 操作 xiaobao-sales SKILL.md 前，必先 backup 到 evolution/skill_backup_<date>.md，再 patch