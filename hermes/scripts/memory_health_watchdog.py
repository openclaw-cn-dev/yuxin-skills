#!/usr/bin/env python3
"""记忆健康看门狗 Windows 版（玉芬 2026-11-10，移植自 Mac mnemosyne_health.sh）
no_agent 零 token：全部健康 → 空 stdout 静默；有异常 → 输出报告。
检查两项：
  ① L1 (memories/MEMORY.md / USER.md) 利用率 ≥55% → 提醒压缩（备份→下沉 L2 memory_store/）
  ② 各 profile mnemosyne.db working_memory 条数 >500 → 提醒跑 mnemosyne sleep 整合
只读不改：压缩/整合由 LLM 会话按本报告执行（看门狗不自带副作用）。
"""
import os
import sys
import sqlite3
from datetime import datetime
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HERMES = Path(os.environ.get("HERMES_HOME", "D:/yuxin/hermes"))
if not HERMES.exists():
    HERMES = Path.home() / ".hermes"

# 扫描根：主安装目录优先（保证 default+全部 profiles 覆盖），HERMES_HOME 若是
# 独立 profile 目录则追加；去重后无论 cron 在哪个环境下运行都全量覆盖。
roots = []
if HERMES.parent.name == "profiles":
    roots.append(HERMES.parent.parent)  # 主安装 D:/yuxin/hermes
roots.append(HERMES)
seen, scan_roots = set(), []
for r in roots:
    rp = r.resolve()
    if rp not in seen:
        seen.add(rp)
        scan_roots.append(rp)

L1_LIMITS = {"MEMORY.md": 2200, "USER.md": 1375}
L1_ALERT_RATIO = 0.55
WM_THRESHOLD = 500

alerts = []

# ① L1 水位（每个扫描根的 default + 所有 profiles；按解析路径去重，
#    防止 HERMES 主目录与 profile 目录重叠时同一文件重复报警）
candidates = []
for root in scan_roots:
    candidates.append((root / "memories", f"{root.name}/default"))
    prof_dir = root / "profiles"
    if prof_dir.exists():
        # glob("*/memories") 返回的 p 已是 memories 目录本身，直接用，勿再拼接
        candidates += [(p, f"{root.name}/{p.parent.name}") for p in sorted(prof_dir.glob("*/memories"))]

mem_dirs, seen_dirs = [], set()
for d, label in candidates:
    rp = d.resolve()
    if rp in seen_dirs:
        continue
    seen_dirs.add(rp)
    mem_dirs.append((d, label))

for d, label in mem_dirs:
    if not d.exists():
        continue  # 该 profile 无 L1，属正常
    if not any((d / name).exists() for name in L1_LIMITS):
        continue  # 两文件皆缺 = L1 尚未初始化的空 profile，属正常不报警
    for name, limit in L1_LIMITS.items():
        f = d / name
        if not f.exists():
            alerts.append(f"⚠️ L1[{label}] {name} 缺失（{f}）")
            continue
        n = len(f.read_text(encoding="utf-8"))
        ratio = n / limit
        if ratio >= L1_ALERT_RATIO:
            alerts.append(
                f"🗜️ L1[{label}] {name} {n}/{limit} 字符 = {ratio:.0%} ≥55% → 需压缩"
                f"（先备份 .bak.时间戳，细节下沉 memory_store/，L1 留摘要+指针）"
            )

# ② Mnemosyne working_memory 水位（每个扫描根的 default + 所有 profiles；按解析路径去重）
candidates = []
for root in scan_roots:
    candidates.append((root / "mnemosyne" / "data", f"{root.name}/default"))
    prof_dir = root / "profiles"
    if prof_dir.exists():
        candidates += [
            # glob("*/mnemosyne/data") 返回的 p 已是 data 目录本身，直接用，勿再拼接
            (p, f"{root.name}/{p.parent.parent.name}")
            for p in sorted(prof_dir.glob("*/mnemosyne/data"))
        ]

data_dirs, seen_dirs = [], set()
for d, label in candidates:
    rp = d.resolve()
    if rp in seen_dirs:
        continue
    seen_dirs.add(rp)
    data_dirs.append((d, label))

for d, label in data_dirs:
    db = d / "mnemosyne.db"
    if not db.exists():
        continue  # 该 profile 未启用 mnemosyne，属正常
    try:
        n = sqlite3.connect(str(db)).execute(
            "SELECT COUNT(*) FROM working_memory"
        ).fetchone()[0]
    except Exception as e:
        alerts.append(f"⚠️ [{label}] db 读取失败: {type(e).__name__}: {e}")
        continue
    if n > WM_THRESHOLD:
        alerts.append(
            f"🗜️ [{label}] working_memory {n} 条 > {WM_THRESHOLD} → 建议跑 mnemosyne sleep 整合"
        )

# 健康即静默（空 stdout = cron 不打扰）
if alerts:
    print(f"🧠 记忆健康看门狗（{datetime.now():%m-%d %H:%M}）")
    print()
    print("\n".join(alerts))
