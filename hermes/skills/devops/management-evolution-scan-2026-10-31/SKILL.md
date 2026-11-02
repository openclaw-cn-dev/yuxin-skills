---
name: ***SECRET***
description: 10-31 管理进化扫描增量 — 中央 57→58 job 辨析（新 job 建档非漂移）、AI智能大脑 RuntimeError 假阳性复核金标准（产物落盘=完成）、429 老账复核自愈闭环第 2 次实证、研目录空壳误判（.vite 缓存目录）、profiles/default 疑似主库副本。
version: 1.0.0
created: 2026-10-31
updated: 2026-10-31
---

# 管理进化扫描 2026-10-31 实战增量

> 背景：10-31 23:00 扫描，冻结期第 6 天。无新发关键异常；本轮 5 个口径修正/金标准。

## 金标准 1：中央 job 数漂移先查 created_at，不判异常

57→58 的 +1 不是 schema 漂移：「养殖百科研编-每日条目供给」10-31 11:10 建档、20:52 首跑 ok。金标准：按 created_at 排序取最新 job 核对建档时间 vs 昨日扫描时点；never_run jobs 清单同步看（当前 1 个：DeepSeek Harness 月度跟踪，schedule=每月 1 号 09:00、enabled=False，月度 job 未到首个触发日属正常）。

## 金标准 2：轮换调研 RuntimeError 假阳性的完成判定

「AI智能大脑分身-重点轮换调研」last_status=error，但 last_error 是「轮 54 开发完成汇报」正文（报告型假阳性，10-25 金标准再验证）。完成判定三步：① last_error 尾部是否进度/汇报正文；② 研目录产物 mtime 是否 ≈ last_run 时点（本轮 README+决策日志 12:39、life_stream 23:00 落盘）；③ next_run 是否未来时态。三者齐 = 判完成非故障，error 计数不进决策清单。

## 金标准 3：429 老账复核自愈闭环第 2 次实证

10-26 报过的 4 条轮换调研 429 error（配额 10-26 19:00 重置）→ 10-31 复核全部自愈：last_error 停旧日期、无新 error、gateway.log 当日 429=0（历史累计 662 条勿误读，必须 grep '当日日期.*429' 精确过滤）。10-24 纪律再次有效：报过的 429 下轮必须复核日期分布再降级，不让 P0 反复挂。

## 金标准 4：研目录空壳误判（.vite 缓存）

「研-空气处理设计助手」目录仅含 .vite/deps 缓存（vite dev server 产物误入目录），os.walk 统计会把它当"当日活跃"，实为空壳。金标准：研目录活跃判定看调研产物（.md/报告），排除 .vite/node_modules/缓存类；空壳目录从口径剔除并挂华哥 P2 处置清单。

## 金标准 5：profiles/default 是主库同步副本

~/.hermes/profiles/default/ created 05-04、skills 与主库内容一致（88 vs 主库非 archive 部分同构）、无独立 jobs.json/cron/output。skill 全库统计时它与中央主库是同一份数据的两面，**不要双计**；本轮主报告已把「profiles/default 89 个」标注为疑似副本。未来全库口径 = 中央主库 + 10 个非 default profile。

## 口径备忘

- 情商助手 pending 账龄精确算法：kanban created_at 是 Unix 秒（1788067928 = 2026-08-30 13:32）→ 62 天；GEO-02/03 created 09-26 → 35 天。上期"61.4d/挂起第 11 天"口径延续 +1 天。
- tokens CSV 文件是 08:00 生成截面，当天 20:00 后的行缺失——"今日 tokens"是低估截面，趋势看 7 日带。
- rkr_staging 47.0→49.6GB（+2.6GB）：baike 子目录 10-29 起有新 job 落盘（养殖百科），属新业务增量；设 +2GB/日 × 3 日连升的升级阈值，不立即报。
- .curator_backups 全库 ~2.13GB 与昨持平（昨报 +170MB 未延续），回收案维持挂账。
- management_evolution 目录内 4 个 _scan_*.py + latest.md.bak-20261012 临时文件挂 P2 合并包清理（rm 被 tirith 拦，等合并包统一处理）。
