---
name: laomo-knowledge
description: '老莫知识库核心技能。v1.88.57 R613 增量 (P#129 升格 sed BSD 大小写防御盲点 + P#130 升格 双轨并存 R 编号冲突防御 / Docker ps 实证 3 容器 UP + RKR fleet 余 9 待 docker start / P#118 v3 chroma_18888 路由消失加深维持观察第 4 轮 / P#107 R547 范本累计第十二次复用 R547→R550→R559→R562→R564→R567→R570→R573→R576→R582→R607→R610→R613 + P#119 sed 双 case 第九次零补刀 + P#125 渐进型 2 轮重写 1916→1376 chars 砍幅 28% mini boundary / P#96 回滚自救第二次实证 / P#128 v2 双轨并存持续验证 range 589..613 零重号零跳号) + v1.88.56 R610 + v1.88.55 R607 + v1.88.54 R604 + v1.88.53 R601 + 历史。详见 references/changelog-v1.***SECRET***.md。'
license: MIT
metadata:
  author: 渔芯科技
  version: "1.88.57"
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

**description 阈值分层**（R181/R237/R344 实战）：30KB 安全区 / 40KB 警戒 / **48KB 早闸口 (chars 口径，非 bytes)** / 50KB 硬阈值。Wrapper `--prune N` 自动从最旧起 drop N 条，按出现顺序 drop 不可指定编号（恒 drop 最旧 N 条，R478 纪律）。

**blocked 任务 silent round**：task #11 (AI 照片修复) 持续 in_progress 永 completed（关键认知 1），根阻塞 = Ark 403 欠费 + Docker daemon DOWN。当无新事件时走 hourly silent round：零方向 1-4 执行、零台账写、零 B 轨 evolution 报告、只写最小 entry（≈2000-4500 chars）做状态采集 + Ark 复核 + 阻塞盘点 + R 编号断言。

**[SILENT] 汇报约定**：若 hourly silent round 零新事件零方向执行，仅当 prompt 显式要求时才输出 `[SILENT]`；hourly round 仍需输出完整 deliver report（含 last_r、状态、阻塞盘点、预案）。

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