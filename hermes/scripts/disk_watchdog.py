#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""磁盘容量守护（no_agent cron 脚本，零 token）。Windows 迁移版。

职责：
1. 每次运行检查 D: 盘可用空间。
2. 低于阈值（WARN<84GB / CRITICAL<30GB）输出告警文本（stdout 非空即投递，静默=正常）。
3. CRITICAL 时自动清理 100% 可再生缓存：npm cache / pip cache / .hermes 30 天前旧日志。
   绝不触碰业务数据、模型文件、会话库、回收站。
4. Top 占用扫描：D 盘业务目录 + 用户缓存目录（结果缓存 6h）。

设计约束（遵守 cron-home-hijack-bypass）：全程绝对路径，禁 ~ / Path.home() / expanduser。
- 同级别告警 12h 内不重复；升级立即告警。
- 缓存清理每 6h 最多一次。
- 锁防重入：Windows 下不能用 os.kill(pid,0)（会真杀进程），改用锁文件 mtime 陈旧判定。
- 测试模式：DISK_WATCHDOG_TEST=ok|warn|critical 强制水位；DISK_WATCHDOG_STATE 覆盖状态文件；
  DISK_WATCHDOG_NO_CLEAN=1 跳过清理动作。

退出码：0=正常；1=脚本自身异常（触发 cron 错误告警）。
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

HERMES_DIR = Path("D:/yuxin/hermes")
STATE_PATH = Path(
    os.environ.get("DISK_WATCHDOG_STATE", str(HERMES_DIR / "logs/disk_watchdog_state.json"))
)
LOG_PATH = HERMES_DIR / "logs/disk_watchdog.log"
LOCK_PATH = HERMES_DIR / "logs/disk_watchdog.lock"
DRIVE = "D:/"
WARN_FREE_GB = 84.0
CRITICAL_FREE_GB = 30.0
REALERT_HOURS = 12
CLEAN_INTERVAL_HOURS = 6
TOP_SCAN_INTERVAL_HOURS = 6
DU_TIMEOUT_SEC = 45
TOP_SCAN_BUDGET_SEC = 120  # 全局预算：Top 扫描总耗时超限即止（Git du 扫 Windows 大目录慢）
LOCK_STALE_SEC = 2 * 3600  # 锁超过 2h 视为残留，接管
NPM = "C:/Program Files/nodejs/npm.cmd"
DU = "C:/Program Files/Git/usr/bin/du.exe"

TOP_DIRS = [
    Path("D:/yuxin/company"),
    Path("D:/yuxin/hermes"),
    Path("D:/yuxin/rkr_staging"),
    Path("C:/Users/渔芯科技/AppData/Local/Docker"),
    Path("C:/Users/渔芯科技/AppData/Local/Temp"),
    Path("C:/Users/渔芯科技/AppData/Local/pip/cache"),
    Path("C:/Users/渔芯科技/AppData/Roaming/npm-cache"),
    Path("C:/Users/渔芯科技/Downloads"),
]


def log(msg: str) -> None:
    """追加运行日志，超 5MB 轮转一次。"""
    try:
        LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        if LOG_PATH.exists() and LOG_PATH.stat().st_size > 5 * 1024 * 1024:
            LOG_PATH.replace(LOG_PATH.with_suffix(".log.1"))
        with LOG_PATH.open("a", encoding="utf-8") as fh:
            fh.write(f"{datetime.now():%Y-%m-%d %H:%M:%S} {msg}\n")
    except OSError:
        pass


def load_state() -> dict:
    try:
        return json.loads(STATE_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def save_state(state: dict) -> None:
    try:
        STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
        STATE_PATH.write_text(json.dumps(state, ensure_ascii=False, indent=1), encoding="utf-8")
    except OSError as exc:
        log(f"state 写入失败: {exc}")


def free_gb() -> float:
    """返回 D: 盘可用 GB。"""
    return shutil.disk_usage(DRIVE).free / 1024**3


def total_gb() -> float:
    """返回 D: 盘总容量 GB。"""
    return shutil.disk_usage(DRIVE).total / 1024**3


def level_of(free: float) -> str:
    if free < CRITICAL_FREE_GB:
        return "critical"
    if free < WARN_FREE_GB:
        return "warn"
    return "ok"


def du_gb(path: Path) -> float | None:
    """du 实测目录占用 GB；超时/失败返回 None。"""
    if not path.exists():
        return None
    try:
        out = subprocess.run(
            [DU, "-sk", str(path)],
            capture_output=True, text=True, timeout=DU_TIMEOUT_SEC,
        ).stdout
        return int(out.split()[0]) / 1024**2
    except (subprocess.TimeoutExpired, ValueError, IndexError, OSError):
        return None


def top_consumers(state: dict) -> list[str]:
    """Top 占用清单；带缓存避免每小时全量 du。"""
    now = time.time()
    cached_at = state.get("top_scan_ts", 0)
    rows: list[tuple[str, float]] = state.get("top_rows") or []
    if now - cached_at > TOP_SCAN_INTERVAL_HOURS * 3600 or not rows:
        measured: list[tuple[str, float]] = []
        started = time.time()
        for d in TOP_DIRS:
            if time.time() - started > TOP_SCAN_BUDGET_SEC:
                log(f"Top 扫描预算用尽，剩余目录跳过（已测 {len(measured)} 个）")
                break
            gb = du_gb(d)
            if gb is not None:
                measured.append((str(d), gb))
        if measured:
            rows = sorted(measured, key=lambda x: -x[1])[:5]
            state["top_rows"] = rows
            state["top_scan_ts"] = now
    return [f"  {i+1}. {name}  {gb:.0f}G" for i, (name, gb) in enumerate(rows)]


def clean_regenerable_caches() -> list[str]:
    """清理可再生缓存，返回动作结果行。CRITICAL 且距上次>6h 才调用。"""
    results: list[str] = []
    commands = [
        ("npm cache", [NPM, "cache", "clean", "--force"]),
        ("pip cache", [sys.executable, "-m", "pip", "cache", "purge"]),
    ]
    for name, cmd in commands:
        if not Path(cmd[0]).exists() and name != "pip cache":
            results.append(f"  - {name}: 未安装，跳过")
            continue
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
            results.append(f"  - {name}: {'完成' if proc.returncode == 0 else '失败'}")
        except subprocess.TimeoutExpired:
            results.append(f"  - {name}: 超时跳过")
        except OSError as exc:
            results.append(f"  - {name}: 异常 {exc}")
    # 30 天前的 hermes 旧日志
    cutoff = time.time() - 30 * 86400
    removed = 0
    try:
        for f in (HERMES_DIR / "logs").glob("*.log*"):
            if f.is_file() and f.stat().st_mtime < cutoff:
                f.unlink()
                removed += 1
        results.append(f"  - hermes 旧日志(>30天): 删除 {removed} 个")
    except OSError as exc:
        results.append(f"  - hermes 旧日志: 异常 {exc}")
    return results


def acquire_lock() -> bool:
    """防重入锁（Windows 安全版）：锁存在且 <2h 视为上一轮仍在跑；超 2h 视为残留接管。"""
    try:
        if LOCK_PATH.exists():
            age = time.time() - LOCK_PATH.stat().st_mtime
            if age < LOCK_STALE_SEC:
                return False  # 上一轮仍在运行（长 du 扫描），本轮跳过
            log(f"锁残留 {age/3600:.1f}h，接管")
    except OSError:
        pass
    try:
        LOCK_PATH.parent.mkdir(parents=True, exist_ok=True)
        LOCK_PATH.write_text(str(os.getpid()), encoding="utf-8")
        return True
    except OSError:
        return False


def release_lock() -> None:
    try:
        LOCK_PATH.unlink()
    except OSError:
        pass


def main() -> int:
    if not acquire_lock():
        log("上一轮仍在运行，本轮跳过")
        return 0
    try:
        return _run()
    finally:
        release_lock()


def _run() -> int:
    state = load_state()
    test_mode = os.environ.get("DISK_WATCHDOG_TEST", "")
    free = free_gb()
    level = test_mode if test_mode in ("ok", "warn", "critical") else level_of(free)
    prev_free = state.get("last_free_gb")
    delta = (free - prev_free) if isinstance(prev_free, (int, float)) else None
    now = time.time()

    if level == "ok":
        state.update(last_free_gb=round(free, 1), last_ts=now, last_level="ok")
        save_state(state)
        log(f"ok: {free:.1f}G free")
        return 0

    # 节流：同级别 12h 内不重复告警（升级除外）
    last_level = state.get("last_level")
    last_alert = state.get("last_alert_ts", 0)
    escalated = level == "critical" and last_level != "critical"
    if not escalated and last_level == level and now - last_alert < REALERT_HOURS * 3600:
        state.update(last_free_gb=round(free, 1), last_ts=now)
        save_state(state)
        log(f"{level} (节流中): {free:.1f}G free")
        return 0

    lines: list[str] = []
    pct = free / total_gb() * 100 if total_gb() else 0
    delta_txt = f"，较上次 {delta:+.1f}G" if delta is not None else ""
    emoji = "🚨" if level == "critical" else "⚠️"
    label = "危急" if level == "critical" else "警告"
    lines.append(f"{emoji} 磁盘空间{label}告警")
    lines.append(f"D 盘可用 {free:.1f}GB / {total_gb():.0f}GB（{pct:.0f}%）{delta_txt}")
    if test_mode:
        lines.append(f"（测试模式 level={test_mode}）")

    if level == "critical" and not os.environ.get("DISK_WATCHDOG_NO_CLEAN"):
        if now - state.get("last_clean_ts", 0) > CLEAN_INTERVAL_HOURS * 3600:
            lines.append("已自动清理可再生缓存：")
            freed_before = free
            lines.extend(clean_regenerable_caches())
            after = free_gb()
            lines.append(f"清理回收 ≈{after - freed_before:.1f}GB，当前可用 {after:.1f}GB")
            state["last_clean_ts"] = now
        else:
            lines.append("（6h 内已清理过，本轮跳过）")

    lines.append("占用 Top5：")
    lines.extend(top_consumers(state))
    lines.append("以上 Top 为缓存/模型/数据分类参考；业务数据（company/rkr_staging）不做自动清理。")

    state.update(last_free_gb=round(free, 1), last_ts=now, last_level=level, last_alert_ts=now)
    save_state(state)
    log(f"{level} 告警: {free:.1f}G free")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:  # noqa: BLE001 — 守护自身故障必须外显
        log(f"脚本异常: {exc!r}")
        print(f"🚨 磁盘守护脚本异常: {exc!r}")
        sys.exit(1)
