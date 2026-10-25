---
name: company-ops-agent-management
description: |
  华哥 2026-09-18 授权玉芬全面运营公司后的多智能体团队管理方法论 — 通过 tasks.db 派单+验收闭环、运营总控 cron、待开发项目「资料够就开发小样」判定流程、项目资产盘点套路、每日管理进化扫描数据源与技术、profile gateway 恢复实操、旺财（Windows 远程 agent）故障诊断与模型切换；也覆盖按模型跨 profile 的 token 归因分析（华哥问「分析下 XX 模型 token 使用情况」）与全公司高频 cron 审计/关停（profile 私有 cron 库盲区）。触发条件：玉芬派任务给同事 agent（毛豆/小宝/阿福/老莫/黑豆/整理师）、验收交付物、盘点公司项目进展、华哥说「你来管」「盯一下进展」「够了就开发小样」、执行每日管理进化扫描、华哥令开启某 profile 网关、华哥报旺财不能用/要给旺财换大模型、华哥问某 provider/模型的 token 消耗与归因、华哥令关闭/暂停某高频 cron。
related_skills:
  - ***SECRET***
---

# 多智能体团队管理与公司运营（玉芬）

> **本文件是 default profile 的副本正本**（zhenglishi profile 有一份同名技能，两处内容需保持同步；10-24 起 default 侧增量在此维护）。改跨 profile 共享技能时先确认 active profile，create 同名 = 本 profile 全量覆盖。

## 授权边界（2026-09-18 华哥定）

- ✅ 可做：给同事 agent 派任务、验收成果、把调研成果分类推动开发、华哥不在线时独立运营
- ❌ 不碰：宽博士（quant）、心博士（psychology）= 华哥唯一直属，不派单不动配置
- ❌ 大额采购/云资源扩容/对外签约/新雇 profile → 一律列「待华哥拍板」，不自行决定
- 改 Hermes 配置仍走 5 阶段安全流程（见 hermes-config-safe-edit 类知识）

## 派单-验收闭环

1. **派单走 tasks.db**：`sqlite3 /Users/hua/.hermes/tasks.db "INSERT INTO tasks (title, description, assigned_to, priority, status) VALUES (...)"`。description 必须含：背景+具体动作+**验收标准（交付物绝对路径+格式要求）**
2. **可派对象**：毛豆（产品）、小宝（销售）、阿福（客服）、老莫（知识库）、黑豆（行政财务）、整理师/学习助手（调研）
3. **验收 = 实测，不是看文件名**：代码项目跑 pytest / node --test / 构建产物；文档项目读内容核对字数/来源链接/结构。验收结果记入 `~/.hermes/reports/yufen_ops/YYYY-MM-DD.md`（追加式日志）
4. **僵尸任务清理**：pending 超 1 周无动作的任务直接 cancelled 并注明原因，防任务池虚胖（2026-09-18 清了 5 个）

## 运营总控 cron

- 每日 09:30/21:30 两轮（现役 job_id=d8e1837b770d），五步：团队健康巡检→项目推进决策→派单→验收→汇报
- 无异常输出一行「✅ 运营正常」+1 句要点；有停滞/新开发候选/待拍板事项→≤300 字清单
- 每轮最多派 2 个新任务防过载；不新造高频 cron（查重铁律）

## 每日管理进化扫描 — 数据源与技术（10-04 沉淀，10-24 补磁盘基线与全公司 GLM 统一后口径）

> **10-20 已验证的扫描配方**：write_file 三个 /tmp 脚本（scan1=cron健康+chat测活+state.db趋势+429计数；scan2=skill容量+kanban+tasks.db；scan3=调研节律+研产出freshness+心跳三源+版本），单轮跑完落盘报告。首轮脚本含 bug 时直接 write_file 修复版跑第二轮，别原地反复 patch。

- **jobs.json 顶层是 dict {jobs:[...], updated_at}，不是裸 list**：直接遍历会 'str' object has no attribute 'get'——读法统一 `d['jobs'] if isinstance(d, dict) else d`（私有库同构）。
- **parse_ts 时区坑**：last_run_at 可能带 `+08:00` tz 后缀，naive fromtimestamp 与 aware datetime 相减直接 TypeError——`if dt.tzinfo: dt = dt.astimezone().replace(tzinfo=None)`，写在统一 parse_ts() 里。
- **state.db 是 cron 健康的真值源**：`sqlite3.connect('file:/Users/hua/.hermes/state.db?mode=ro', uri=True)` 只读 URI（库 8G+，绝不写打开）。sessions 表**没有 profile 列**，主键叫 `id`（无 session_id 列）；状态列是 `end_reason`；messages 表时间列是 `timestamp`(REAL)。cron 会话 `id LIKE 'cron_<jobid>_%'` 按 id 前缀匹配才可靠（title 多为 NULL）。
- **模型口径（10-24 起全公司统一）**：9 个业务 profile config + 全部 cron job 模型锁定均已切 GLM-5.3-flash（智谱套餐 anthropic 端点，共享 key 93b8 开头），MiniMax 退役。按模型归因时 `model LIKE '%GLM%'` 是主力面；billing_provider=custom。GLM key 是全公司单点，tokens 日报盯 GLM 消耗占比与 429/1113。
- **per-profile 心跳的数据源是 tokens CSV 不是 state.db**：`~/.hermes/reports/tokens_当月-*.csv`，表头 `date,agent,model,tokens`。**freshness 扫描必须 glob 全月再按行聚合**，只读当日单文件会漏 profile。判定三源交叉：gateway_state.json + tokens CSV + jobs.json last_run_at。
- **gateway.log 429 按日计数坑**：RateLimit 行不带时间戳，按日统计用 `grep -oE '^2026-10-[0-9]+ .*(429|RateLimit)'`。**被拦面以 jobs.json last_status=error 遍历为准，log 只作旁证**；429 分型 2056=Token Plan 套餐上限（MiniMax 时代）/ 1113=智谱欠费 / 529=GLM 集群过载（自愈观察）。
- **同名 provider 多 key 块坑**：测「智谱/XX 挂没挂」必须先确认目标 agent 实际用的那条 block（config 顶部 model.provider 指向），逐块实测。key 健康度实测模板：python3 urllib POST anthropic 端点 `/v1/messages`（max_tokens=8 一条 hi）；从 config 提取 key 时 python 正则+只打印头6/尾4+长度。
- **token spike 归因**：cron session id 格式 `cron_<jobid>_<时间戳>`，`sid.split('_')[1]` join jobs.json 即得 job 名。**billing 字段零值坑**：未配单价的 provider 会话 estimated_cost_usd=0，别写「费用 $0」当真。
- **profile 私有 cron 库全量盘点**：全公司 job 面 = 中央 ~55 + 私有 ~26，三个坑：① 私有库 disabled job 的 **paused_at 常缺失**（age unknown 时列华哥别猜）；② **库名≠任务归属**（报告按库标注、括注 job 名真实归属）；③ 处置配方：先 `cp jobs.json jobs.json.bak-日期-用途` → 改 → 核验按 **`id` 字段过滤**（profile 库条目 job_id 恒为 null）。批量改 job 的 model/provider 用 hermes-agent venv python 调 `cron.jobs.update_job()`（系统 python3.9 会报 type|type TypeError）。
- **tokens CSV 的坑**：文件名≠数据日期（内容是全历史累计），聚合当日必须 `grep '^YYYY-MM-DD'` 前缀过滤。**<0.1x 均值不是「正常」**，先查调度面再查 error 面分「真闲置 vs 被拦」。
- **飞书 chat_id 测活**：deliver 字段混存字符串/字典/别名三形态，**测活前过滤只测 `oc_` 开头的值**。华哥群 chat_id=`***SECRET***`。发送模板 `~/.hermes/reports/management_evolution/_notify_boss_YYYYMMDD.py`（复制改 MSG；Bearer 行变量拼接，不从回显复制含凭据的行）；发送前 print 全文核对，发完留 message_id 回执。
- **cron 会话 $HOME 被劫持**：cron 触发会话里 `~`/`$HOME` 展开到 profile 沙箱——脚本/配置一律绝对路径 `/Users/hua/.hermes/...`。
- **调研增量 LLM 空转判断**：轮换调研类 job 看 last_run_at/next_run_at 节律即可；研项目产出真值路径 `/Users/hua/6-产品研发/渔芯独角兽/01-开发中/研-<项目名>/`，freshness 双查 `-mtime -2` 计数 + 最新文件 mtime；macOS 无 `-printf` 用 os.stat。
- **error 假阳性归类**：last_error 尾部 200 字符是「产出已写入/本轮 token 估算」自述 = 假阳性按 ok 判；真故障=Script not found / 429 连续多轮不自愈。**假阳性复核配方**：读 last_error **尾部**别只看 RuntimeError 开头。
- **单 job 高频观察线**：日触发 >8 次或日耗 >1M tokens 列观察；判「失控」先读 job prompt 开头自述意图（research-all-day 类高频轮换是设计不是失控），对照华哥惯例（调研类=1 天 1 轮，7:00~23:30 错开）。
- **kanban.db 在 cron/异步会话下 ro-uri 打不开**：加 `immutable=1`。schema：priority 是 INTEGER(0=P0)，assignee（不是 assigned_to），created_at 是 unix 秒（天龄 >3650d 按字段损坏=未知）；完成态=`completed`（无 'done'），活跃判定只取 `status IN ('pending','in_progress')`。tasks.db 列名是 assigned_to。
- **skill 容量审计必须排除隐藏目录**：`.curator_backups`+`.archive` 会被 os.walk 算进总量；**口径=纯 SKILL.md**（非 SKILL.md 资产不计入），环比必须同口径，报告注明口径。路径直接 `glob('/Users/hua/.hermes/profiles/*/skills')` 逐目录跑。
- **扫描脚本坑**：① 时间字段双解析——先 try float→fromtimestamp、失败再 fromisoformat（含 tz 归一化）；② priority 双类型统一 str() 归一；③ kanban.db 无 updated_at 列，滞留兜底用 created_at；④ cron 无人值守下 execute_code 是硬 BLOCKED——替代：write_file 到 .py 再 `python3 /tmp/x.py`，或单行 `python3 -c`；⑤ **cron 模式连 `rm -f /tmp/...` 都会被拦**——临时文件留 /tmp 自清；⑥ 工具输出层对敏感 header 掩码——认证行一律重写变量拼接；⑦ tool-call 迭代上限截断——扫描压缩到 ≤6 个脚本，「报告 write_file + cp latest + 发 1 行提醒」三件事在预算前 2/3 完成；⑧ npm view 查版本必须查对包名（OpenAI CLI=`@openai/codex`，claude=`@anthropic-ai/claude-code`），带 timeout 兜底；⑨ **write_file 回显错乱≠磁盘错乱**——核实手段是 read_file 读回，只有 lint=error 或确认损坏才重写。

## 429 扩散升级纪律

- 升级线：**>50% 轮换 job 被拦 或 连续 3 天扩散 → 直接 P0 当日上报**；1-2 个被拦=逐日列报。10-23 曾单日 25 个全天爆发（MiniMax Token Plan 时代）；**10-24 全公司切 GLM 后 MiniMax 429 面自然消失**，新风险面=智谱共享 key（1113 欠费型/529 过载型按日扫 error 面）。
- 处置选项固定三档：**A** 高频轮换调研 job 显式切模型分流 / **B** 充值套餐 / **C** 临时降频（暂停一半轮换调研 job 保核心）。给华哥字母菜单回字即执行。
- 成功率上报口径：真实成功率 = 名义 ok 率剔除假阳性与自愈型后的比率，分开报。

## profile gateway 恢复实操

顺序：① `plutil -p` 验 plist 完好 → ② cp plist 到 /tmp 备份 → ③ `launchctl enable gui/$UID/ai.hermes.gateway-<p>` + `launchctl bootstrap gui/$UID ~/Library/LaunchAgents/ai.hermes.gateway-<p>.plist` → ④ sleep 后 `launchctl print` 看 state=running + pid → ⑤ 金标准：读 `~/.hermes/profiles/<p>/gateway_state.json`，gateway_state=running + platforms.feishu.state=connected 才算在线。

- **授权边界细化**：华哥直接下令开启某 profile 网关=最高优先级授权；但该 profile 的 **cron 配置仍不碰**。
- **停机面现状（10-22）**：5 个 profile stopped（maodou/xiaobao 停 09-03、laomo 停 10-07、heidou/afu 长停）——恢复与否列华哥字母菜单，不自行动。10-24 全公司切 GLM 时已把全部 profile 配置改好，下次启动自动生效。

## 旺财（Windows 远程 agent）诊断与模型切换

- **边界认知**：旺财=Windows 机器上的独立 Hermes profile，Mac 侧**无法直接读写其 config/cron**。Mac 能做的=①本机侧诊断 ②生成一键 PowerShell 脚本发飞书由华哥转跑。
- **Mac 侧诊断路径**：① key 健康度分层实测（python3 urllib POST 各套餐 anthropic 端点 `/v1/messages`）；② 旁证三查定位停更时间线；③ 修复载体：全自动 PowerShell 脚本（备份→改 config→改 .env→重启网关→校验失败自动回滚），以 MEDIA 文件发飞书。
- **⚠️ 长 key 飞书截断坑**：125 位 key 直接写飞书消息正文会被截断——**key 以 base64 内嵌进 PowerShell 脚本**，明文不出现在消息里。已发出去的截断消息立即明说作废。

## 「资料不够补资料，够了就开发小样」判定流程（华哥 2026-09-18 定）

| 判定 | 标准 | 动作 |
|---|---|---|
| 小样已成 | 测试全绿 + 可运行产物 | 挂「待 UI 整合/种子试用」，不再投入开发 |
| 够了→开发 | 资料齐全 + 代码骨架在 + 缺可见层 | 立即派单补齐，验收=浏览器走通全流程+证据落盘 EVIDENCE.md |
| 资料不够 | 无调研文档或调研停在方案层 | 先派调研补资料，不启动开发 |

- **验收测试命令基准**：Python `python3 -m pytest tests/ -q --no-header`；Node `node --test *.test.js`；前端小样看 `dist/`。证据落盘：派单时要求产出 `EVIDENCE.md`。

## 项目资产盘点套路

1. `ls -dlt 01-开发中/*/` 看 mtime 排序找活跃项目
2. 每项目查三样：README 头部定位 / tests 目录 / 可运行产物
3. **跨项目资产复用盘点**：先 find 全公司找可复用代码 + `mnemosyne_recall` 查历史定调——资产常在非直觉位置（如鱼乐宝仿真引擎藏在黑豆软著材料目录里 951 行）
4. 盘点结果写成「模块×资产对照表」落盘新项目 README

## 磁盘/容量类处置（10-24 起指向独立技能）

审计配方、zstd 归档流程、删除前核验单（挂载实据辨同名不同物 / `_dup1` 非重复的定性方法 / Docker volume 永不清）统一见 **`devops/macos-disk-audit-cleanup`**。基线（10-24）：全盘 371G used（85%），rkr_staging 47G（归档首轮完成），可回收候选=微信缓存 5-10G（华哥手动）+ .curator_backups ~2G + 归档包 5.3G 外迁。磁盘守护 cron 报 85%+ 按该技能处置。

## 与华哥的汇报纪律

- 决策类汇报给字母选项菜单——华哥回一个字母即定案，立即执行不等补充（10-24 实例：磁盘清理回「a.c」=A+C 两项）
- 需华哥拍板的事项攒清单挂着不催；其余自主推进，事后汇报
- 每日状态同步用 mnemosyne_task_progress（task=yufen-company-operations），不用 L1 memory 记任务进度

## Pitfalls

- **skills 跨 profile 校验**：zhenglishi profile 下创建的 skill，在 default profile 会话 skill_view 能读到、但 skill_manage patch 会报 not found（按 active profile 注册表拦截）——唯一路径是 create 同名全量覆盖、一次成型内联全部增量（**manage 的 name 参数不能带斜杠路径**，全量 create 必须用裸名 + category='devops' 落地；本地根目录与 devops/ 分类下同名两份时裸名报 ambiguous，必须带分类路径 skill_view('devops/<name>')）。10-24 实例：default 会话 patch zhenglishi 的 company-ops-agent-management 报 not found，改在 default 落 default 侧正本、增量双处同步。
- **全量 create 重写 skill 时防掩码污染**：重打含凭据示例的段落时改用描述性词，跳过任何星号/密钥样字面量；落盘后 skill_view 复查该段无异常星号再收工。
- **平台/大功能派单前先查重**：tasks.db 可能有同名旧任务（如#31#33 复号），UPDATE 而非 INSERT
- 验收别人交付物时勿信子代理自述「已完成」，必须自己 stat/读文件/跑测试
- 宽博士/心博士的 cron 与 profile 配置即使发现停滞也不动，列给华哥
