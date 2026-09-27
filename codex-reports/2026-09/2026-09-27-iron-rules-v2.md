# 🆕 2026-09-27 cron 二次校正版：铁律 92-94

> 0927 cron 二次校正版（沿 0923 铁律 67 救火 SOP）。本次 cron 实盘发现兄弟 cron 09:03 已写日报 + 装 golive，但日报 2 处错版需要校正。
> 沿 0924 拆 split 落地 — 铁律 92-94 追加到 SKILL.md references/0927 iron rules 文件末尾。

## 铁律 92：兄弟 cron 错版救火 SOP（0927 cron 二次校正版实盘）

**症状**：0927 cron 启动第 1 步查到日报已在 09:03 创建（兄弟 cron 跑），但 yuxin-skills 无 commit。日报 2 处错版：
1. 本地 + backup: 127 → 128（实盘 126 → 127，+1 = golive）
2. 0.157.0 latest stable 符合 SOP 不升级（实盘落后 1 stable patch）

**修法（沿 0923 铁律 67）**：
- 兄弟 cron 已跑过 → 必跑数据字段校验（fs / Codex stable / Hermes commit / C 盘 4 件齐）
- 错版检测命中 → 写日报校正版覆盖 + 日报首部报告覆盖前次 cron 错版
- 实盘数据 = ls SKILL.md grep bak | wc -l（沿 0926 口径）

## 铁律 93：yuxin-skills ahead origin 持续 10 commits 高亮（0927 实盘）

**症状**：本次 cron 实算 ahead = 10（0926 报 9 + 兄弟 cron 装 golive + 1 = 10）。

**沿 0926 铁律 85 持续高亮 SOP**：
- ahead = 7 → 8 首次突破 → P0 必显式高亮
- ahead 持续 8/9/10+ → 每次 cron 都高亮 P0 待 push
- ahead ≥ 10 → 老大决策 push 的紧迫性升级

铁律 51 是硬红线 → cron 不擅自 push。

## 铁律 94：golive skill 装后必跑 CLI 验证 + 业务路径挂接（0927 实盘）

**症状**：兄弟 cron 装入 mikehasa/golive-skill 979⭐ MIT TS，21 文件 2.6 万行。

**业务命中**：极高（直击渔芯科技官网 + 4 群商业化产品上线链路）

**判定**：已装入。

**待实跑**：
node ~/.codex/skills/golive/scripts/golive.mjs version --json

**铁律 94**：
- golive 装入后必实跑 version --json 验证 CLI 能用
- 不要因 2.6 万行拒装（mega-repo 阈值是 50000KB / 100MB+，2.6 万行是 TS 文件数不是 KB 字节）

## 0927 cron 二次校正版完整时序

- 09:01:05 date 自检
- 09:01:30 fs 真算 = 126（沿 0926 口径）
- 09:01:45 Codex --version = 0.157.0
- 09:02:00 upstream stable = rust-v0.157.1
- 09:02:30 5 维搜索 10 命中（沿 0926 铁律 84 query 模板）→ 全拒
- 09:02:45 发现兄弟 cron 09:03 已写日报 + 装 golive（沿 0923 铁律 67）
- 09:03:00 数据字段校验：日报错版 +1
- 09:03:30 写日报校正版覆盖（沿 0922 铁律 59）
- 09:04:00 cp 日报到 yuxin-skills/codex-reports/
- 09:04:15 写铁律 92-94 → 追加到 SKILL.md references/0927

## 反模式 0927 二次校正版新增

- 日报报 fs 数字无校验实盘（铁律 92）
- 日报报符合 SOP 不升级漏报落后 stable（铁律 92）
- 兄弟 cron 装入新 skill 没 commit 收尾（铁律 93）
- golive 装入没实跑 CLI 验证（铁律 94）

## 最后更新

2026-09-27 09:05 cron 二次校正版（铁律 92-94 追加，沿 0924 拆 split 落地）
