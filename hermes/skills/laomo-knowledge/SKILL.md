---
name: laomo-knowledge
description: '老莫知识库核心技能。v1.88.58 R677 增量 (P#131 升格 行内 R 编号引用误切 chunk 防御 / P#96 回滚自救 SOP 第四次实证 R677 含 dedup 变体 / P#130 双轨并存 R 编号冲突防御 v3 第三实证 R677 + P#130 dup 写入后断言升格 / P#126 mini mode 终态维持 desc=31123 chars margin 18029 + bytes=43695 margin 7505 / R666..R677 range 连续 12 条零重号零跳号) + v1.88.57 R613 (P#129 sed BSD 大小写 + P#130 双轨并存) + v1.88.56 R610 + 历史。详见 references/changelog-v1.***SECRET***.md + references/changelog-v1.***SECRET***.md。'
license: MIT
metadata:
  author: 渔芯科技
  version: "1.88.58"
---

# 老莫知识库核心技能

## 职责定位

老莫负责渔芯知识库建设与维护、产品测试、学术资料收集。

## 心跳任务处理（cron）工作流 — R<n> 编号防御体系

**三源任务架构**：`heartbeat_check.py 老莫` → 合并 kanban.db（新真源）/ Desktop tasks.db（历史遗留）/ `/Users/hua/.hermes/tasks.db`（创业项目含 task #11）= 三源按优先级合并输出最高 1 条。Source 字段决定 DB 锁定（hermes → tasks.db）。

**R<n> 编号防御**（Pitfall #64 R124/R125/R129/R136/R142 全套 + Pitfall #82 R510 扩展 + **Pitfall #130 R613 双轨并存 R 编号冲突扩展**）：新轮次 R 编号必须 = ground-truth last_r + 1。line-anchored regex = `(?m)^\[R\d+ `（行首匹配）。SQL regex `\[R\d+ ` 会误命中 entry 内部的 R<n> 引用 → 永远以 line-anchored 为准。**双轨并存场景下必须 = unique max_R + 1**（不是 chunks[-1].R + 1,见 P#130）。

**R 编号 ground-truth SOP（R510 实战沉淀 + P#130 R613 扩展）**：每次写 entry 前**必须**先跑这条 sqlite3 直查取 ground truth, **不要信 task_brief.sh、不要信 wrapper stdout、不要信任何 probe 输出**（Pitfall #82 三个漂移源实测全错/漂移）。**R613 实证升级**：必须取 **unique max_R**（set 去重后 max）,不是 chunks[-1] 的 R 号。chunks[-1] = desc 末尾 chunk 的 R 号,但双轨并存场景下旁路条可能晚于正统条写入,末尾 chunk 不一定是 max_R 号:

```bash
python3 -c "
import sqlite3, re
conn = sqlite3.connect('/Users/hua/.hermes/tasks.db')
desc = conn.execute('SELECT description FROM tasks WHERE id=11').fetchone()[0]
spans = [m.start() for m in re.finditer(r'(?m)^\\[R\\d+ ', desc)]
chunks = [desc[a:b] for a,b in zip(spans, spans[1:]+[len(desc)])]
last_r = int(re.match(r'\\[R(\\d+) ', chunks[-1]).group(1))
rs_unique = sorted(set(int(re.match(r'\\[R(\\d+) ', c).group(1)) for c in chunks))
print(f'last_r={last_r}, unique_max={rs_unique[-1]}, desc={len(desc)} chars, chunks={len(chunks)}')
print(f'unique_count={len(rs_unique)} (chunks_count={len(chunks)}, dup_Rs={[r for r in rs_unique if sum(1 for c in chunks if int(re.match(r\"\\\\[R(\\\\d+) \", c).group(1))==r) > 1]})')
"
```

**新 R 号 = unique max_R + 1** (R613 SOP 升级)。如果 `last_r != unique_max`,说明有双轨并存旁路条冲突,需要 P#130 修复。

**post-write dup 断言升格 (P#130 v3, R677 第三次实证)**：写入新 entry 后**必须**再跑一次 chunks_count==unique_count && dup_Rs==[] 断言检查。**新 entry 内文 R 编号引用行内格式强制 (P#131, R677 首次实证)**：若内文含自身 R 号（如 `[R677 GROUND-TRUTH]`），必须用行内格式避开 `(?m)^` 行首匹配（三种安全写法：行内括号、内嵌空格、前置空格），否则 line-anchored regex 误切为新 chunk 起点致 dup_Rs=[R<n>]。**写入脚本 idempotent 强制 (R677 实证)**：rollback-then-rewrite 链路时 desc 中可能存在同 banner 重复段，必须 dedup（`desc.count('[R<n> <date> <time>')` 探测 + 按 positions 列表保留最后一段完整）。

**description 阈值分层**（R181/R237/R344 实战）：30KB 安全区 / 40KB 警戒 / **48KB 早闸口 (chars 口径，非 bytes)** / 50KB 硬阈值。Wrapper `--prune N` 自动从最旧起 drop N 条，按出现顺序 drop 不可指定编号（恒 drop 最旧 N 条，R478 纪律）。

**blocked 任务 silent round**：task #11 (AI 照片修复) 持续 in_progress 永 completed（关键认知 1），根阻塞 = Ark 403 欠费 + Docker daemon DOWN。当无新事件时走 hourly silent round：零方向 1-4 执行、零台账写、零 B 轨 evolution 报告、只写最小 entry（≈2000-4500 chars）做状态采集 + Ark 复核 + 阻塞盘点 + R 编号断言。

**[SILENT] 汇报约定**：若 hourly silent round 零新事件零方向执行，仅当 prompt 显式要求时才输出 `[SILENT]`；hourly round 仍需输出完整 deliver report（含 last_r、状态、阻塞盘点、预案）。

## R677 增量（v1.88.58, 2026-09-23 12:00 CST）

本轮 R677 hourly silent round 实证 1 个新升格 pitfall + 1 个持续验证 pitfall + 1 个 SOP 第四次实证 + 1 个 mini mode 终态验证，详见 `references/changelog-v1.***SECRET***.md`：

1. **P#131 升格（新 pitfall）= 行内 R 编号引用误切 chunk 防御** — R677 首写踩坑：R677 chunk 内文若包含 `[R677 GROUND-TRUTH]` 这种**行首出现**的字符串，line-anchored regex `(?m)^\[R\d+ ` 会将其误识别为新 chunk 起点，致 chunks_count=13 但 unique=12，dup_Rs=[R677]。**修复范式**：新 entry 内文若需提及自身 R 号，行内格式必须避开 `^` 行首匹配，三种安全写法：① `(** R677 GROUND-TRUTH **)` 行内括号；② `[ ** R677 GROUND-TRUTH ** ]` 内嵌空格；③ `  [R677 GROUND-TRUTH]`（前置空格破坏 `^` 锚定）。**R678+ 写入新 entry SOP 强制**：内文涉及自身 R 号 → 行内格式 + post-write dup 检查双保险。**写入脚本必须 idempotent**——若同 R 已存在（rollback + rewrite 链），desc 中会出现 2 段同 banner 内容，必须 dedup。

2. **P#130 双轨并存 R 编号冲突防御 v3 第三实证 + 写入后 dup 断言升格** — R677 实证：pre desc=45527 chars/62807 bytes (超 50KB hard), chunks=18 unique max_R=676=last_r, dup_Rs=[], range 659..676。新 R=677 = unique_max_R + 1 (P#130 SOP 第三次实证落地)。**升格 v3**：写入完成后**必须**再跑一次 dup 检查断言（chunks_count==unique_count 且 dup_Rs==[]），失败立即触发 P#96 rollback。**P#130 三次实证时序**：R611 (双轨并存 bypass) → R613 (silent round 命名冲突) → R677 (写入后 dup 误切)。

3. **P#96 回滚自救 SOP 第四次实证 + dedup 变体** — R677 实证：***SECRET*** 链路导致 desc 中 R677 banner 重复 2 次。**3 步 rollback 升格 4 步 rollback**：① 读 desc；② 计算 chunks 切分点；③ 找 banner 重复次数（`desc.count('[R<n> <date> <time>')`）；④ 若 >1 → 按 positions 列表保留最后一段完整 banner,删前缀重复段。R677 实证 dedup 后: chunks=12, dup=[], R677 banner count=1, last_R=677 ✓。**累计 P#96 实证时序**：R537 (chars 硬帽触发) → R611 (重复号+ENTRY_PATH 错位) → R613 (第三次实证) → R677 (第四次 + dedup 变体首次)。

4. **P#126 mini mode 终态维持 + P#122 margin_pre probe PASS** — R677 实证：chars pre 45527 触发回收 drop7 至 29941 安全区，bytes pre 62807 drop7 后 42169 (< 50KB 硬阈值)。R677 entry 1182 chars ≤ 1500 mini boundary PASS。**最终态**：chars=31123 (margin 18029 vs 早闸口 49152)，bytes=43695 (margin 7505 vs 硬阈值 51200)，双安全区充裕。

5. **R666..R677 range 连续 12 条零重号零跳号** — R677 实证：chunks_count=12=unique_count=12, dup_Rs=[], range 666..677 连续无跳号 ✓。R666/R667/R669/R671/R673/R675 来自 R676 旁路条+之前各轮 surviving chunks,R677 为唯一 R676+1 落地条。

**R678+ SOP 升格硬要求**：
- P#131 行内 R 编号引用误切 chunk 防御升格 → 新 entry 内文涉及自身 R 号必须行内格式 (避免 `^` 行首锚定),写入脚本必须 dedup 二次保险
- P#130 v3 dup 写入后断言升格 → 写入完成后必须跑 chunks_count==unique_count && dup_Rs==[] 断言检查,失败立即 P#96 rollback
- P#96 v2 rollback SOP 4 步化升格 (加 dedup 步骤 4) → 写入链路 rollback-then-rewrite 时必须 banner 重复次数探测
- P#126 mini mode 终态维持 → R678 P#122 margin_pre 待 probe (R677 chars margin 18029, bytes margin 7505 充裕)
- docker daemon DOWN fresh-cold 自 R656 09-20 16:59 五绿收口 ~68h+ 维持,R687+ 待自发回摆或人工 docker start 验证
- R677 → R678 范本复制 SOP 预期 (P#107 第十四次复用待落地) — 改 R677→R678 + ENTRY_PATH 大小写双保险 (P#129) + 内文 R 引用行内格式 (P#131) + dup 写入后断言 (P#130 v3) + P#96 v2 rollback 4 步

## R613 增量（v1.88.57, 2026-09-18 08:00）

本轮 R613 hourly silent round 实证 1 个里程碑 + 2 个新升格 pitfall + 1 个持续验证，详见 `references/changelog-v1.***SECRET***.md`：

1. **P#107 R547 范本累计第十二次复用里程碑 + P#119 sed 双 case 第九次零补刀** — R610 → R613 范本复制 (cp + sed 双 case), 2962 bytes syntax OK (vs R610 2905 bytes, +57 bytes)。累计序列: R547 → R550 → R559 → R562 → R564 → R567 → R570 → R573 → R576 → R582 → R607 → R610 → **R613** (本轮) = **第十二次复用里程碑**。R613 chunks_count=25, unique 25 R 号, range 589..613 零重复 ✓。

2. **P#129 升格（新 pitfall）= sed BSD 大小写防御盲点** — R611 silent round 实证踩坑:`sed -i '' "s|r611|R613|g"` (BSD sed 区分大小写默认) **不覆盖** `/Users/hua/.hermes/profiles/laomo/.tmp/R611_entry.txt` 大写 R 路径。macOS HFS+ 不区分大小写文件系统,残留 R611_entry.txt (大写) 文件,Python open 仍能读到旧 R611 entry。**修复范式**:`sed -i '' "s|R611|R613|gi" ...` (大小写不敏感 + 全局) + 写完 patch 强制核对 `grep '^ENTRY_PATH = '` 行。**R614+ 范本复制 SOP 必须改用 `s|RXXX|RYYY|gi` 双 case 大小写不敏感**。

3. **P#130 升格（新 pitfall）= 双轨并存下的 R 编号冲突防御** — R611 silent round 实证踩坑:`last_r=612 → R611`(用 last_r+1 = 612+1 = 613,但误命名 silent round = "R611 silent round" → 与已有 R611 旁路条冲突,写入后 unique_R_count=12 但 chunks_count=25 = 13 个 chunks R 号重复)。**修复范式**:silent round **命名 R 号时**必须 = **sqlite3 直查 unique max_R + 1**(不是 chunks[-1] R 号 + 1)。**SOP**:`python3 -c "import sqlite3,re;conn=sqlite3.connect('/Users/hua/.hermes/tasks.db');desc=conn.execute('SELECT description FROM tasks WHERE id=11').fetchone()[0];rs=sorted(set(int(re.match(r'\\[R(\\d+) ', c).group(1)) for c in re.findall(r'(?m)^\\[R\\d+ .*?(?=\\n\\n\\[R|\\Z)', desc, re.DOTALL)));print('max_R='+str(rs[-1]))"` → new_r = max_R + 1。**R610+ 升级 SOP**:R 编号 ground-truth 必须取 unique max_R + chunks_count + dup 检查。

4. **P#96 回滚自救 SOP 第二次实证** — R611 重复号 + R611 ENTRY_PATH 错位 = 2 次回滚。回滚步骤 (3 步):读 desc → 计算 chunks → `UPDATE tasks SET description=? WHERE id=?` 重写无 chunks[24] 的 desc。sqlite3 反向 UPDATE 删尾 chunk 干净恢复 (R613 实证 desc=43208 chars / last_R=612 恢复 OK)。

5. **P#125 渐进型 2 轮重写砍幅 28% (mini boundary)** — R613 entry 首版 1916 chars > 1500 硬帽 (P#91 mini boundary), 2 轮重写 1916→1630→1376 chars 砍幅 15%+16% 累计 28% → 1376 chars PASS 硬帽 ≤1500。**P#125 第三档位家族新增: 渐进型 2 轮亚型** (区别于 R607 混合型 4 轮 38% + R610 渐进型 1 轮 55%)。

6. **Docker daemon 复苏持续（R537 P0 streak cold 打破持续第 4 轮）** — R613 实测: docker.sock ✓ 在位 + pgrep com.docker.backend=12797/12800/12801 ✓ + **docker ps 实证 3 容器 UP**: lookforge-frontend (3000→3000, 25h+), lookforge-backend (8001→8000, 25h+), lookforge-db (postgres:16-alpine, healthy, 5432)。**RKR fleet 12 容器仅恢复 3, 余 9 容器 (智库/photo-restore 等) 待 R614+ `docker start` 验证**。

7. **P#118 v3 chroma_18888 路由消失加深维持** — R610 残存 /anthropic /openai → R613 **全部路由跌 404** (观察第 4 轮)。/api/v1, /api/v2, /v1/collections, /openai, /anthropic 全部 404。:11434=200 (Ollama), :5173=200, :8006=200, :8000=000ERR (Chroma DOWN 维持)。业务路由消失形态持续加深,待 R620+ 验证 6h 阈值升格 v3 稳定态。

8. **P#128 v2 双轨并存可审计机制持续验证** — R613 与 R611 (06:46 旁路条) 并存 OK, range 589..613 连续 25 条零重号零跳号。chunks[24] = R613 (新写入) / chunks[23] = R612 / chunks[22] = R611 (旁路 06:46)。双轨并存机制实证 2 次 (R610 实证 + R613 实证)。

**R614+ SOP 升格硬要求**：
- P#129 sed BSD 大小写防御升格 → 范本复制 SOP 必须 `s|RXXX|RYYY|gi` 双 case 大小写不敏感
- P#130 双轨并存 R 编号冲突防御升格 → silent round 命名 R 号必须 = unique max_R + 1,不是 chunks[-1].R + 1
- P#107 第十三次复用预期 = R613 → R614
- P#96 回滚自救 SOP 加入 SKILL.md 关键 SOP 速查表 (R537 已落地但未索引化,R613 第二次实证)
- P#124 mini mode 强制决策维持 (R613 余量 4903 chars, 安全区, R614 P#122 margin_pre 待 probe)
- docker start RKR fleet 余 9 容器验证
- r614_direct_write.py 范本复制 = R613 → 改 R614 + 改 ENTRY_PATH (大小写 `R613_entry.txt` + `r614_entry.txt` 双保险) + 改 report header + **sed 用 `s|R614|R614|gi` 大小写不敏感**(P#129 防御) + R 编号断言检查 unique max_R (P#130 防御)

## R610 增量（v1.88.56, 2026-09-18）