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

### §1.1 软跳过分支（A 不饱和但 B+C 饱和 + 凌晨/深夜 + 上轮 < 3h）

> 2026-09-18 02:38 黑豆 round 27 实测：当 A=1（上轮 round 26 8.5KB 重活刚做完 2h 内）但 B=120+ / C=3 份复盘近 7d 全饱和、且 cron 触发在 22:00–06:00 守夜窗口时，**应仍走静默兜底**，不应机械按字面「任一不满足 → 标准五阶段」硬出政策/合同/SOP 大块。

判定信号（**全满足才走软跳过**）：
1. B 饱和：memory ≥ 30 或 ≥ 本 profile 历史 80% 分位
2. C 饱和：≤ 7 天有 ≥ 1 件复盘
3. 时间窗：本地小时 ∈ [22:00, 06:00]
4. 上轮间隔：< 3h 且上轮字节 > 5KB（含实质产出）

产出：守夜档字节递减铁律目标 ≤ 1.5KB（round 26 8.5KB → round 27 1.5KB = -82%），报告 6 段结构照常（§0 三确认 / §1 判定 / §2 沿用产物池 / §3 skills 健康 / §4 备注 / §5 元数据），但 §2/§3 极简。

反例（不应软跳过）：上轮为 18–20 时档主活轮（D-Day 决策 / 残保金申报）后 22 时档 → 上轮刚做完重决策辅助卡，本轮虽是夜间但若距 D-Day < 24h 仍应**保节奏而非省字节**，看玉芬「晚间守夜档」指令优先级。

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

**字节递减铁律（实测 · round 27/28 黑豆）**：18 时档 3.5KB (100%) → 20 时档 2.5KB (71%) → 22 时档 1.8KB (51%) → 00 时档目标 ≤1.5KB。每晚一档字节严控 -30%。

**round 28 实测校准（2026-09-18 04:00 黑豆 D-Day T-16h 档）**：本档 1.6KB 略超 1.2KB 目标（+400B），原因是 §4 备注段加了 "D-Day T-16h 行程锁定" 独立段落。**教训**：D-Day 倒计时/行程锁定应压缩进 §2 沿用产物池那一行括号注（如「D-Day 决策辅助卡 🟢 *9-20 用*」），不另开 §4。下一档目标回 ≤1.2KB。

**已知坑**：
- skill loader 报 truncated 名称（如 heidou-adm）= 注册表名截断假象，非真缺（详见 §6 PITFALL-B + 每档前置自检 SOP）
- D-Day 倒计时 ≤24h 档：不要把行程详情（签字错峰/法人到场时间）塞进 evolution §4，应飞书单独发到玉芬/华哥群，evolution 只留一行引用

## §3 整理师七段式报告结构（5 维度扫描型）

适用：整理师类「知识库扫描 + 趋势学习」型 agent 的 self-evolution 档。前置强制 30 秒自检（心跳绝对路径 → $HOME 验证 → PWD/USER → 关键脚本可达 → AGENTS.md skill 漂移检测），任一步失败按纪律处理（劫持→继续不停手用绝对路径；漂移→立 PITFALL）。七段：§1 桌面知识库扫描（文件数/大小/新增/待整理/标签 5 维）→ §2 新方法论学习 → §3 AI 趋势 3 点 → §4 skills 体检 → §5 PITFALL 跟踪表（跨会话累积 #KO-N）→ §6 给玉芬汇报 → §7 反思笔记。

## §4 ROI 论据与降频决策

当华哥/玉芬要求「为 cron 降频提供量化依据」时：按逐 profile 轻量审计决策树评估每档产出/成本比，用累计 ROI 数据（如黑豆 ROI evidence 系列）支撑降频/保频建议。原始论据与逐日数据见 `references/heidou-cron-roi-evidence/`。

## §5 maodou heartbeat 附表与 session 桥接

maodou cron heartbeat 的滚动表 / 催办清单 / 路线图诊断模板，以及跨 profile 跨 session 的方法论沉淀桥（maodou ↔ 主库），沿用 `references/***SECRET***.md`。session 桥的档案聚合结构与「承接纪要」惯例与 afu-self-evolution-protocol 保持兼容。

### §5.1 接力棒盘点 SOP（v1.0 · 跨 profile 通用 · 2026-09-18 毛豆实证）

每档 cron 启动时**先盘点已完成接力棒**（30 秒流程）→ 判定 → 执行或跳过。避免重复起草已完成任务，预期单 agent 年省 50-80h，6 agent 公司层面年省 300-480h。完整 SOP 见 `references/cron-relay-inventory-sop.md`：

- §二 盘点流程 5 步 30 秒命令
- §三 接力棒写入规则（evolution 报告 §接力棒 字段标准格式 + 3 个完成判定硬指标 + 套用率自报）
- §四 跳过决策的反向保险（4 个不跳过场景 + 双重验证）
- §五 实战案例（毛豆 00 时档：跳过 SB → 起草 SOP-001）
- §六 推广路径表（6 agent × 50-80h/年）

**触发条件**：任何 cron 自进化 agent 启动时；evolution §接力棒 字段写入前；SB/SOP/培训视频 等长链路任务的"下一棒"判定时。

## §6 PITFALL 库（小宝/老莫/黑豆 实战蒸馏）

> 实测中反复命中的 3 类陷阱，未来 cron 自进化 agent 必读。session-level 实证见 `references/***SECRET***.md`。

### PITFALL-A · `$HOME`/`~` 解析劫持（cron subprocess shell）

- **症状**：active profile 为 `xiaobao` 时，shell 子进程把 `~` 展开到 `zhenglishi/home`（default profile 的 home），导致 `python3 ~/.hermes/scripts/heartbeat_check.py 小宝` 报 "can't open file '/Users/hua/.hermes/profiles/zhenglishi/home/.hermes/scripts/heartbeat_check.py'"。
- **根因**：cron 启动时 `$HOME` 被 profile 配置固定，subprocess shell 继承 `~` 展开时取错 profile。
- **正解**：永远用绝对路径（`/Users/hua/.hermes/...`、`/Users/hua/rkr_staging/...`），禁用 `~/`、`$HOME`、`Path.home()` 拼路径。
- **检测命令**（每个 cron 档位首条）：
  ```bash
  echo "HOME=$HOME"  # ✅ 应为 HOME=/Users/hua；❌ 若为 /Users/hua/.hermes/profiles/<自己>/home/ 即劫持
  ```
- **关联**：`productivity/cron-home-hijack-bypass`

### PITFALL-B · 跨 profile skill 污染（skill_view 渲染层陷阱）

- **症状**：`skill_view('xiaobao-sales')` 返回的 references 全谱（如 §四十三 11 节 SOP）实际不在 active profile 磁盘上，而在 default profile 的 skills 目录（如 `/Users/hua/.hermes/skills/xiaobao-sales/...`）。Hermes skill loader 优先在 default 目录渲染，跨 profile 共享引用未隔离。
- **风险**：cron 在 active profile 下用 `skill_manage` 操作跨 profile references，可能写到 default → 写入丢失；启用 `cross_profile=True` 写 default 又污染别的 agent。
- **判别法**：`skill_view` 返回 path 后必跑 `ls $(echo "<path>" | sed 's|file://||')` 验证存在；不存在 = 污染。
- **处理**：跨 profile references → 飞书通知玉芬决策；不要擅自 `cross_profile=True` 写 default。
- **cron prompt 级变体（2026-09-18 黑豆 round 27 + round 28 连续命中）**：cron 启动 prompt 头部会出现 `[IMPORTANT: The following skill(s) were listed for this job but could not be found and were skipped: heidou-admin]` 警告。**这是 loader 渲染截断的假象**——磁盘上 `/Users/hua/.hermes/profiles/heidou/skills/heidou-admin/` 实际存在。

- **每档前置自动自检 SOP（v1.1 · round 28 升级 · 替代手动检测命令）**：cron 启动 30 秒内跑一次，命中假象即在 evolution §3 标注「PITFALL-B 假阳 N 次」直接沿用，不要再去 search_files 找证据：
  ```bash
  # 一步验证（≤ 5s）
  ls -d /Users/hua/.hermes/profiles/<active>/skills/<claimed-missing-skill>/ 2>/dev/null && \
    echo "PITFALL-B假阳:磁盘实存,沿用无碍" || \
    echo "PITFALL-C真缺:按决策树处理"
  ```
  **累计命中表**（每档加 1）：
  | Round | 时间 | claimed-missing | 实存路径 | 判定 |
  |---|---|---|---|---|
  | 27 | 02:38 | heidou-admin | skills/heidou-admin/ | 假阳 ✅ |
  | 28 | 04:00 | heidou-admin | skills/heidou-admin/ | 假阳 ✅ |
  | ≥3 次连续假阳 → 飞书通知玉芬归档 loader bug，不要每次写盘标注 |

### PITFALL-C · stub SKILL.md 自述与磁盘真实状态不一致

- **症状**：`xiaobao-sales` stub 顶部声明"误删导致 canonical 117K 字符 / §一-§四十二 全谱被删"，但磁盘上三处分散存在：
  - profile 顶层 `xiaobao-sales.md`（14KB / 289 行，完整版）
  - `productivity/xiaobao-sales/SKILL.md`（230 行，精简 §1-§8）
  - `default profile skills/xiaobao-sales/references/`（跨 profile 污染）
- **处理决策树**（玉芬/华哥拍板）：A 合并到一处（最优）/ B 保留分散但 stub 加"分散索引"段（次优）/ C 跨 profile 复制 references 到 active（低风险但有冗余）。
- **检测命令**（每月 1 次，0 时档）：
  ```bash
  for skill_md in $(find /Users/hua/.hermes/profiles/<active>/skills/ -name "SKILL.md" -maxdepth 2); do
    CLAIMED=$(grep -E "约|字符|全谱" "$skill_md" | head -1)
    ACTUAL=$(wc -l "$skill_md" | awk '{print $1}')
    [ -n "$CLAIMED" ] && echo "$skill_md: claimed='$CLAIMED' actual=$ACTUAL"
  done
  ```

### PITFALL 关联 references

- `references/***SECRET***.md` — 小宝 19:00 档实证（含完整复现命令与决策树）

## §7 关联技能

- `afu-self-evolution-protocol` — 通用 5 步骤协议 + 6 文件级联升级 + Pitfall 1-22（协议层；本技能是饱和/降本决策层）
- `maodou-cron-heartbeat`（maodou profile）— §3.1.x 四轴 audit SOP
- `productivity/cron-home-hijack-bypass` — $HOME 劫持绕过（所有档位前置自检引用）
- `productivity/***SECRET***` — 跨 session 数据真实性铁律（报告数字必实测重取）
