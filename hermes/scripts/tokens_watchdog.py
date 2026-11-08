#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全公司 DeepSeek token 消耗异常监控（no_agent watchdog）

- 数据源：default + 全部 profile 的 state.db `sessions` 表
- 口径：只统计 DeepSeek（model 含 'deepseek'），tokens = input+output+cache_read+cache_write+reasoning
- 行为：有异常 → 打印告警文本（cron 投递到华哥飞书）；无异常 → 空 stdout（静默，零 token 零消息）
- 用法：python3 tokens_watchdog.py          # 正常 watchdog
        python3 tokens_watchdog.py --show   # 打印当前指标（人工排查用，不告警）

设计原则（参考 feishu-api-notify 的 silent-watchdog 模式）：
  1. 空 stdout = 静默，绝不刷屏
  2. 每个规则独立冷却，异常持续时按冷却周期重告警（避免"沉默失败被遗忘"）
  3. no_agent=true 运行，脚本本身零 LLM token 消耗
"""

import sqlite3
import os
import json
import sys
import time
from datetime import datetime, timedelta
from collections import defaultdict

BASE = "/Users/hua/.hermes"  # 绝对路径（cron 下 $HOME 会被覆盖，不能用 ~）
STATE_FILE = os.path.join(BASE, "state", "tokens_watchdog.json")

# ── 阈值（2026-08-21 依据 7 天实测校准：中位日消耗 172M，中位小时 6M，p95 小时 15M，最大小时 74M）──
HOURLY_SPIKE_FLOOR = 30_000_000      # 单小时 DeepSeek > 30M（约 5x 中位小时 6M）→ 突发
HOURLY_SPIKE_RATIO = 4.0             # 或 > 4x 中位小时速率
DAILY_BURN_WARM = 1.5                # 今日累计 > 1.5x 7天中位日消耗 → 黄色预警
DAILY_BURN_HOT = 2.0                 # 今日累计 > 2x → 红色预警
RUNAWAY_SESSION = 100_000_000        # 单会话 > 100M（历史最大 56M 的 ~2 倍）→ 失控
MIN_ABS_DAILY = 30_000_000           # 日消耗绝对下限，低于此不告警（避免小样本误报）

# ── 冷却（秒）──
COOLDOWN_SPIKE = 2 * 3600
COOLDOWN_DAILY = 4 * 3600
COOLDOWN_RUNAWAY = 1 * 3600


def find_state_dbs():
    dbs = []
    default_db = os.path.join(BASE, "state.db")
    if os.path.exists(default_db):
        dbs.append(("default", default_db))
    profiles_dir = os.path.join(BASE, "profiles")
    if os.path.isdir(profiles_dir):
        for p in sorted(os.listdir(profiles_dir)):
            db = os.path.join(profiles_dir, p, "state.db")
            if os.path.exists(db):
                dbs.append((p, db))
    return dbs


def collect(since_ts):
    """返回 [(agent, started_at, tokens, cache_read, title, source)]，只含 DeepSeek 且 tokens>0"""
    rows = []
    for agent, db in find_state_dbs():
        try:
            conn = sqlite3.connect(f"file:{db}?mode=ro", uri=True, timeout=10)
            cur = conn.cursor()
            cur.execute(
                """SELECT started_at, model, input_tokens, output_tokens, cache_read_tokens,
                          cache_write_tokens, reasoning_tokens, title, source
                   FROM sessions WHERE started_at > ?""",
                (since_ts,),
            )
            for started_at, model, i, o, cr, cw, r, title, src in cur.fetchall():
                if not started_at:
                    continue
                if "deepseek" not in (model or "").lower():
                    continue
                total = sum(x for x in (i, o, cr, cw, r) if x)
                if total <= 0:
                    continue
                rows.append((agent, started_at, total, cr or 0, title or "", src or ""))
            conn.close()
        except Exception:
            continue
    return rows


def median(vals):
    if not vals:
        return 0
    s = sorted(vals)
    n = len(s)
    return s[n // 2] if n % 2 else (s[n // 2 - 1] + s[n // 2]) / 2


def load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE) as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def save_state(state):
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, ensure_ascii=False)


def fmt(n):
    if n >= 1_000_000:
        return f"{n/1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n/1_000:.0f}K"
    return str(int(n))


def now_str():
    return datetime.now().strftime("%Y-%m-%d %H:%M")


def main():
    show = len(sys.argv) > 1 and sys.argv[1] == "--show"
    now = datetime.now()
    now_ts = now.timestamp()
    today0 = now.replace(hour=0, minute=0, second=0, microsecond=0)
    today_str = now.strftime("%Y-%m-%d")
    since_ts = (today0 - timedelta(days=7)).timestamp()

    rows = collect(since_ts)

    # ── 聚合 ──
    daily = defaultdict(int)                 # date -> total
    hourly = defaultdict(int)                # hour-bucket(ts//3600) -> total
    agent_today = defaultdict(int)
    agent_1h = defaultdict(int)
    last_1h = now_ts - 3600
    last_3h = now_ts - 3 * 3600
    sess_recent = []                          # (tokens, agent, title, source, started_at) 近3h
    last1_total = 0
    today_total = 0

    for agent, st, t, cr, title, src in rows:
        d = datetime.fromtimestamp(st).strftime("%Y-%m-%d")
        daily[d] += t
        if d == today_str:
            today_total += t
            agent_today[agent] += t
        else:
            hourly[int(st // 3600)] += t
        if st >= last_1h:
            last1_total += t
            agent_1h[agent] += t
        if st >= last_3h:
            sess_recent.append((t, agent, title, src, st))

    full_days = [v for k, v in daily.items() if k != today_str]
    median_daily = median(full_days)
    hourly_vals = list(hourly.values())
    median_hourly = median(hourly_vals)

    # ── 判断规则 ──
    fired = []

    # 1. 小时突发
    spike_threshold = max(HOURLY_SPIKE_FLOOR, HOURLY_SPIKE_RATIO * median_hourly)
    if last1_total > spike_threshold:
        top1h = sorted(agent_1h.items(), key=lambda x: -x[1])[:3]
        fired.append(("spike", {
            "last1": last1_total, "threshold": spike_threshold,
            "median_hourly": median_hourly, "top": top1h,
        }))

    # 2. 日消耗（warm/hot）
    if median_daily > 0 and today_total > MIN_ABS_DAILY:
        ratio = today_total / median_daily
        if ratio > DAILY_BURN_HOT:
            level = "hot"
        elif ratio > DAILY_BURN_WARM:
            level = "warm"
        else:
            level = None
        if level:
            top_today = sorted(agent_today.items(), key=lambda x: -x[1])[:3]
            fired.append(("daily_" + level, {
                "today": today_total, "median": median_daily, "ratio": ratio,
                "top": top_today,
            }))

    # 3. 单会话失控
    if sess_recent:
        biggest = max(sess_recent, key=lambda x: x[0])
        if biggest[0] > RUNAWAY_SESSION:
            fired.append(("runaway", {
                "tokens": biggest[0], "agent": biggest[1],
                "title": biggest[2], "source": biggest[3],
            }))

    # ── 冷却判定 ──
    state = load_state()
    now_s = time.time()
    last_alert = state.get("last_alert", {})

    to_send = []
    for rule, detail in fired:
        cooldown = {
            "spike": COOLDOWN_SPIKE,
            "daily_warm": COOLDOWN_DAILY,
            "daily_hot": COOLDOWN_DAILY,
            "runaway": COOLDOWN_RUNAWAY,
        }.get(rule, 3600)
        last_ts = last_alert.get(rule, 0)
        if now_s - last_ts >= cooldown:
            to_send.append((rule, detail))
            last_alert[rule] = now_s
    state["last_alert"] = last_alert

    # ── 输出 ──
    if show:
        lines = [
            "📊 DeepSeek Token 监控当前指标",
            f"  今日累计: {fmt(today_total)} | 7天中位日: {fmt(median_daily)} | 比例: {today_total/median_daily if median_daily else 0:.2f}x",
            f"  近1小时: {fmt(last1_total)} | 中位小时: {fmt(median_hourly)} | 阈值: {fmt(spike_threshold)}",
            f"  今日 Top agent: " + ", ".join(f"{a}={fmt(v)}" for a, v in sorted(agent_today.items(), key=lambda x: -x[1])[:5]),
        ]
        print("\n".join(lines))
        return

    if not to_send:
        save_state(state)
        return  # 静默

    # 组装告警消息
    lines = [f"🚨 DeepSeek Token 异常预警 {now_str()}", ""]
    for rule, d in to_send:
        if rule == "spike":
            lines.append("🔴 小时消耗突发")
            lines.append(f"  近1小时 {fmt(d['last1'])} 已超阈值 {fmt(d['threshold'])}（中位小时 {fmt(d['median_hourly'])}）")
            lines.append("  主要来源: " + ", ".join(f"{a}={fmt(v)}" for a, v in d["top"]))
        elif rule == "daily_hot":
            lines.append("🔴 日消耗严重超标")
            lines.append(f"  今日 {fmt(d['today'])} 已达 7天中位日 {fmt(d['median'])} 的 {d['ratio']:.1f}x（阈值 2x）")
            lines.append("  主要来源: " + ", ".join(f"{a}={fmt(v)}" for a, v in d["top"]))
        elif rule == "daily_warm":
            lines.append("🟡 日消耗偏高")
            lines.append(f"  今日 {fmt(d['today'])} 已达 7天中位日 {fmt(d['median'])} 的 {d['ratio']:.1f}x（阈值 1.5x）")
            lines.append("  主要来源: " + ", ".join(f"{a}={fmt(v)}" for a, v in d["top"]))
        elif rule == "runaway":
            lines.append("🔴 单会话失控")
            lines.append(f"  单会话消耗 {fmt(d['tokens'])}（agent={d['agent']}, source={d['source']}）")
            lines.append(f"  标题: {d['title'][:60]}")
        lines.append("")

    lines.append("优化方案落实情况需人工核对，详见 ~/.hermes/scripts/tokens_report.py 日报。")
    save_state(state)
    print("\n".join(lines))


if __name__ == "__main__":
    main()
