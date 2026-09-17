---
name: cron-self-evolution-toolkit
description: "Cron self-evolution 饱和/降本/守夜决策树工具集（跨 profile 适用：黑豆/阿福/老莫/毛豆/小宝/宽博士/整理师等所有跑 cron 自进化的 agent）。核心：三条件饱和判定（档数/产物池/复盘新鲜度）→ 静默兜底极简档；晚间守夜档字节递减铁律；整理师 5 维度扫描七段式报告结构；黑豆老莫 cron ROI 论据与轻量审计决策树；maodou cron heartbeat 的滚动表/催办/路线图诊断附表与 session 桥接方法论。触发：cron 心跳无任务进入 self-evolution 模式、当日已多档需判断是否静默、晚间守夜档字节控制、为 cron 降频提供量化依据、写 evolution 报告需标准结构时。"
license: MIT
metadata:
  author: 渔芯科技
  version: "1.0.0"
  created: "2026-09-17 curator consolidation"
  absorbed: [***SECRET***, ***SECRET***, ***SECRET***, ***SECRET***]
---

# Cron Self-Evolution Toolkit — 饱和判定 · 守夜降本 · 报告结构

> 🎯 本技能是所有 cron 自进化 agent 共用的类级工具集。按小节取用对应范式，session 级细节见 references/。

## §1 三条件饱和判定 → 静默兜底（主决策树 v1.16）

cron 自进化触发时，先跑三条件（阈值以黑豆为例，其他 profile 同构）：

| # | 条件 | 阈值 | 实操命令 |
|---|---|---|---|
| 1 | 当日已产档数 | ≥ 3 档 | `ls /Users/hua/.hermes/profiles/<profile>/evolution/$(date +%Y-%m-%d)_*.md 2>/dev/null \| wc -l` |
| 2 | 饱和主题数（产物池） | ≥ 30 件 memory | `find /Users/hua/.hermes/profiles/<profile>/memory -name "*.md" 2>/dev/null \| wc -l` |
| 3 | 复盘新鲜度 | ≤ 7 天无新业务数据 | `find /Users/hua/.hermes/profiles/<profile>/memory -name "*复盘*" -mtime -7 \| head -1` |

- **三条件全满足** → elif 分支命中 → 出「静默兜底型」极简报告，不要强行出政策学习/合同复盘。
- **任一不满足** → 走标准五阶段（政策学习 + 合同复盘 + SOP 优化 + skills 健康 + evolution 报告）。
- 实测收益（9-15 黑豆第 3 次静默兜底）：沿用产物池 12 件，节省字节 ≈ 80%，节省 30-65 min/档。

### 静默兜底型报告结构（每档 ≤ 3KB，标准 6 段）

1. **§1 cron 启动三确认** — 心跳（标准 + sqlite3 二次验证）+ 三条件命中确认
2. **§2 五阶段极简化处置表** — 阶段 1/2/3 🟡跳过 + 阶段 4/5 ✅执行 + 字节节省估算
3. **§3 沿用产物池** — 表格列 10-15 件近期 memory + 状态（🟢沿用/🟡部分沿用/🔴需更新）
4. **§4 skills 健康检查** — 已知坑命中计数（沿用累计表，只报新增）
5. **§5 给上级 + 玉芬的增量建议**（中段/末段档可省略）
6. **§6 元数据** — 本档路径/字节/增量/已产档数/沿用 SKILL/决策树版本

## §2 守夜档范式（晚间 ≥18 时 + 无任务）

当 cron prompt 模板（罗列 5 个进化方向）与饱和决策树冲突时，**优先决策树**——决策树是玉芬 + 黑豆长期实战蒸馏产物，prompt 只是模板。

五阶段守夜处置：0 三确认✅ → 1/2/3/4 🟡跳过 → 5 守夜档极简收口。

**字节递减铁律（实测）**：18 时档 3.5KB (100%) → 20 时档 2.5KB (71%) → 22 时档 1.8KB (51%) → 00 时档目标 ≤1.5KB。每晚一档字节严控 -30%。已知坑：skill loader 报 truncated 名称（如 heidou-adm）= 注册表名截断假象，非真缺。

## §3 整理师七段式报告结构（5 维度扫描型）

适用：整理师类「知识库扫描 + 趋势学习」型 agent 的 self-evolution 档。前置强制 30 秒自检（心跳绝对路径 → $HOME 验证 → PWD/USER → 关键脚本可达 → AGENTS.md skill 漂移检测），任一步失败按纪律处理（劫持→继续不停手用绝对路径；漂移→立 PITFALL）。七段：§1 桌面知识库扫描（文件数/大小/新增/待整理/标签 5 维）→ §2 新方法论学习 → §3 AI 趋势 3 点 → §4 skills 体检 → §5 PITFALL 跟踪表（跨会话累积 #KO-N）→ §6 给玉芬汇报 → §7 反思笔记。

## §4 ROI 论据与降频决策

当华哥/玉芬要求「为 cron 降频提供量化依据」时：按逐 profile 轻量审计决策树评估每档产出/成本比，用累计 ROI 数据（如黑豆 ROI evidence 系列）支撑降频/保频建议。原始论据与逐日数据见 `references/heidou-cron-roi-evidence/`。

## §5 maodou heartbeat 附表与 session 桥接

maodou cron heartbeat 的滚动表 / 催办清单 / 路线图诊断模板，以及跨 profile 跨 session 的方法论沉淀桥（maodou ↔ 主库），沿用 `references/***SECRET***.md`。session 桥的档案聚合结构与「承接纪要」惯例与 afu-self-evolution-protocol 保持兼容。

## §6 关联技能

- `afu-self-evolution-protocol` — 通用 5 步骤协议 + 6 文件级联升级 + Pitfall 1-22（协议层；本技能是饱和/降本决策层）
- `maodou-cron-heartbeat`（maodou profile）— §3.1.x 四轴 audit SOP
- `productivity/cron-home-hijack-bypass` — $HOME 劫持绕过（所有档位前置自检引用）
- `productivity/***SECRET***` — 跨 session 数据真实性铁律（报告数字必实测重取）
