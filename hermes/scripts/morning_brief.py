#!/usr/hua/Library/Python/3.9/bin/python3
"""TODO(tech-debt): 用 Claude Code 重写时改用 Hermes 官方 cron SDK 直接查 jobs.db"""
# -*- coding: utf-8 -*-
"""
渔芯科技 · 每日早间简报生成器
扫描所有 cron 的 last_run / status / next_run,生成 1 份 ≤ 800 字的简报,
供 8:00 早间简报 cron 调用,deliver 到华哥飞书。
"""
import json
import os
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any, Dict, List

# 绝对路径,防 profile 劫持
JOBS_JSON = Path("/Users/hua/.hermes/cron/jobs.json")
HERMES_HOME = Path("/Users/hua/.hermes")
OUTPUT_DIR = HERMES_HOME / "cron" / "output"

# 北京时区
CST = timezone(timedelta(hours=8))
NOW = datetime.now(CST)
TODAY_STR = NOW.strftime("%Y-%m-%d")
NOW_STR = NOW.strftime("%H:%M")


def load_jobs() -> List[Dict[str, Any]]:
    if not JOBS_JSON.exists():
        return []
    with open(JOBS_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("jobs", [])


def get_last_output(jid: str) -> str:
    """读 cron 的 last output(前 500 字符)"""
    out_dir = OUTPUT_DIR / jid
    if not out_dir.exists():
        return ""
    # 找最新文件
    files = sorted(out_dir.glob("*.txt"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not files:
        return ""
    try:
        content = files[0].read_text(encoding="utf-8", errors="ignore")
        return content[:500]
    except Exception:
        return ""


def fmt_time_ago(iso_time: str) -> str:
    if not iso_time:
        return "从未"
    try:
        # 处理 +08:00 / UTC 各种格式
        t = datetime.fromisoformat(iso_time.replace("Z", "+00:00"))
        if t.tzinfo is None:
            t = t.replace(tzinfo=CST)
        delta = NOW - t
        seconds = int(delta.total_seconds())
        if seconds < 60:
            return f"{seconds}秒前"
        if seconds < 3600:
            return f"{seconds // 60}分钟前"
        if seconds < 86400:
            return f"{seconds // 3600}小时前"
        return f"{seconds // 86400}天前"
    except Exception:
        return iso_time[:16]


def build_brief() -> str:
    jobs = load_jobs()
    if not jobs:
        return "❌ 无 cron 数据"

    # 分类
    enabled = [j for j in jobs if j.get("enabled") and not j.get("paused_at")]
    paused = [j for j in jobs if j.get("paused_at")]

    # 异常检测
    error_jobs = [j for j in enabled if j.get("last_status") == "error"]
    no_recent_run = []  # > 24h 未跑
    stale_threshold = 24 * 3600
    for j in enabled:
        last = j.get("last_run_at", "")
        if not last:
            no_recent_run.append(j)
            continue
        try:
            t = datetime.fromisoformat(last.replace("Z", "+00:00"))
            if t.tzinfo is None:
                t = t.replace(tzinfo=CST)
            if (NOW - t).total_seconds() > stale_threshold:
                no_recent_run.append(j)
        except Exception:
            pass

    # 接下来 4 小时要跑的(给华哥预期)
    soon_jobs = []
    for j in enabled:
        nxt = j.get("next_run_at", "")
        if not nxt:
            continue
        try:
            t = datetime.fromisoformat(nxt.replace("Z", "+00:00"))
            if t.tzinfo is None:
                t = t.replace(tzinfo=CST)
            if 0 <= (t - NOW).total_seconds() <= 4 * 3600:
                soon_jobs.append((t, j))
        except Exception:
            pass
    soon_jobs.sort(key=lambda x: x[0])

    # 组装简报
    lines = []
    lines.append(f"☀️ 渔芯科技 · 早间简报 · {TODAY_STR} {NOW_STR}")
    lines.append("")

    # 1. 健康总览
    lines.append(f"📊 **总览** · cron {len(enabled)} 启用 / {len(paused)} 暂停")
    if error_jobs:
        lines.append(f"⚠️  **异常** {len(error_jobs)} 个:")
        for j in error_jobs[:5]:
            lines.append(f"   - {j.get('name', '?')[:40]} | {fmt_time_ago(j.get('last_run_at', ''))}")
        if len(error_jobs) > 5:
            lines.append(f"   - ...还有 {len(error_jobs) - 5} 个")
    else:
        lines.append("✅ **异常** 0 个")
    lines.append("")

    # 2. 今日已完成
    today_done = []
    for j in enabled:
        last = j.get("last_run_at", "")
        if not last:
            continue
        try:
            t = datetime.fromisoformat(last.replace("Z", "+00:00"))
            if t.tzinfo is None:
                t = t.replace(tzinfo=CST)
            if t.strftime("%Y-%m-%d") == TODAY_STR:
                today_done.append(j)
        except Exception:
            pass
    lines.append(f"✅ **今日已跑** {len(today_done)} 个 cron")
    lines.append("")

    # 3. 接下来 4h 排期
    if soon_jobs:
        lines.append(f"⏰ **接下来 4 小时** {len(soon_jobs)} 个待跑:")
        for t, j in soon_jobs[:8]:
            lines.append(f"   - {t.strftime('%H:%M')} {j.get('name', '?')[:30]}")
        if len(soon_jobs) > 8:
            lines.append(f"   - ...还有 {len(soon_jobs) - 8} 个")
        lines.append("")

    # 4. 玉芬状态
    yuxin_jobs = [j for j in enabled if "玉芬" in j.get("name", "") or "yuxin" in j.get("name", "").lower()]
    if yuxin_jobs:
        lines.append(f"🤖 **玉芬相关** {len(yuxin_jobs)} 个,最近:")
        for j in yuxin_jobs[:5]:
            name = j.get("name", "?")[:35]
            last = fmt_time_ago(j.get("last_run_at", ""))
            status = j.get("last_status", "?")
            icon = "✅" if status == "ok" else "⚠️" if status == "error" else "⏸"
            lines.append(f"   {icon} {name} | {last}")
        lines.append("")

    # 5. 关键事项(华哥会关心的)
    lines.append("💡 **关键事项**")
    lines.append(f"   - 异常 {len(error_jobs)} 个 / 待跑 {len(soon_jobs)} 个 / 暂停 {len(paused)} 个")
    if no_recent_run:
        lines.append(f"   - {len(no_recent_run)} 个 cron 超过 24h 未跑(检查是否异常)")
    lines.append(f"   - Dashboard: http://127.0.0.1:8765/")

    return "\n".join(lines)


def main():
    brief = build_brief()
    # 写到 stdout(给 cron capture)+ 同时存文件
    print(brief)
    out_path = HERMES_HOME / "cron" / "output" / "morning_brief.txt"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(brief, encoding="utf-8")


if __name__ == "__main__":
    main()
