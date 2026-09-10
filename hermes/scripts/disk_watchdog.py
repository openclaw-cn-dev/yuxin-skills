#!/usr/bin/env python3
"""磁盘容量守护（no_agent cron 脚本，零 token）。

职责：
1. 每次运行检查 /System/Volumes/Data 可用空间。
2. 低于阈值（WARN<60GB / CRITICAL<30GB）输出飞书告警（stdout 非空即投递，静默=正常）。
3. CRITICAL 时自动清理 100% 可再生缓存：npm cache / uv cache / .hermes 30 天前旧日志。
   绝不触碰业务数据、模型文件、会话库、回收站。

设计约束（遵守 cron-home-hijack-bypass）：
- 全程绝对路径 /Users/hua，禁 ~ / Path.home() / expanduser。
- 同级别告警 12h 内不重复；升级立即告警。
- 缓存清理每 6h 最多一次。
- 测试模式：DISK_WATCHDOG_TEST=ok|warn|critical 强制水位；DISK_WATCHDOG_STATE 覆盖状态文件；
  DISK_WATCHDOG_NO_CLEAN=1 跳过清理动作。

退出码：0=正常；1=脚本自身异常（触发 cron 错误告警）。
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

HOME = Path("/Users/hua")
STATE_PATH = Path(
    os.environ.get("DISK_WATCHDOG_STATE", str(HOME / ".hermes/logs/disk_watchdog_state.json"))
)
LOG_PATH = HOME / ".hermes/logs/disk_watchdog.log"
LOCK_PATH = HOME / ".hermes/logs/disk_watchdog.lock"
MOUNT = "/System/Volumes/Data"

WARN_FREE_GB = 60.0
CRITICAL_FREE_GB = 30.0
REALERT_HOURS = 12
CLEAN_INTERVAL_HOURS = 6
TOP_SCAN_INTERVAL_HOURS = 6
DU_TIMEOUT_SEC = 180

TOP_DIRS = [
    HOME / "6-产品研发",
    HOME / ".hermes",
    HOME / "rkr_staging",
    HOME / "Library/Containers/com.docker.docker",
    HOME / ".cache",
    HOME / ".ollama",
    HOME / ".npm",
    HOME / "系统文件夹",
    HOME / "Library/Caches",
    HOME / "Downloads",
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
    """读取状态文件（告警节流 / 环比 / top 缓存）。"""
    try:
        return json.loads(STATE_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def save_state(state: dict) -> None:
    """写状态文件。"""
    try:
        STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
        STATE_PATH.write_text(json.dumps(state, ensure_ascii=False, indent=1), encoding="utf-8")
    except OSError as exc:
        log(f"state 写入失败: {exc}")


def free_gb() -> float:
    """返回数据卷可用 GB。"""
    st = os.statvfs(MOUNT if os.path.exists(MOUNT) else "/")
    return st.f_bavail * st.f_frsize / 1024**3


def total_gb() -> float:
    """返回数据卷总容量 GB。"""
    st = os.statvfs(MOUNT if os.path.exists(MOUNT) else "/")
    return st.f_blocks * st.f_frsize / 1024**3


def level_of(free: float) -> str:
    """按可用空间定级。"""
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
            ["/usr/bin/du", "-xsk", str(path)],
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
        for d in TOP_DIRS:
            gb = du_gb(d)
            if gb is not None:
                measured.append((str(d).replace(str(HOME), "~"), gb))
        if measured:
            rows = sorted(measured, key=lambda x: -x[1])[:5]
            state["top_rows"] = rows
            state["top_scan_ts"] = now
    return [f"  {i+1}. {name}  {gb:.0f}G" for i, (name, gb) in enumerate(rows)]


def clean_regenerable_caches() -> list[str]:
    """清理可再生缓存，返回动作结果行。CRITICAL 且距上次>6h 才调用。"""
    results: list[str] = []
    commands = [
        ("npm cache", ["/opt/homebrew/bin/npm", "cache", "clean", "--force"]),
        ("uv cache", ["/opt/homebrew/bin/uv", "cache", "clean"]),
    ]
    for name, cmd in commands:
        if not Path(cmd[0]).exists():
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
        for f in (HOME / ".hermes/logs").glob("*.log*"):
            if f.is_file() and f.stat().st_mtime < cutoff:
                f.unlink()
                removed += 1
        results.append(f"  - hermes 旧日志(>30天): 删除 {removed} 个")
    except OSError as exc:
        results.append(f"  - hermes 旧日志: 异常 {exc}")
    return results


def acquire_lock() -> bool:
    """防重入锁：上一 tick 还在跑（长 du 扫描）则本轮跳过。"""
    try:
        if LOCK_PATH.exists():
            pid = int(LOCK_PATH.read_text().strip() or 0)
            os.kill(pid, 0)  # 进程仍存活 → 跳过
            return False
    except (ValueError, ProcessLookupError, PermissionError):
        pass  # 锁残留/进程已死 → 接管
    except OSError:
        return False
    try:
        LOCK_PATH.write_text(str(os.getpid()), encoding="utf-8")
        return True
    except OSError:
        return False


def release_lock() -> None:
    """释放锁文件。"""
    try:
        LOCK_PATH.unlink()
    except OSError:
        pass


def main() -> int:
    """守护主流程。正常静默，告警时输出投递文本。"""
    if not acquire_lock():
        log("上一轮仍在运行，本轮跳过")
        return 0
    try:
        return _run()
    finally:
        release_lock()


def _run() -> int:
    """主流程本体（持锁执行）。"""
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
    lines.append(f"可用 {free:.1f}GB / {total_gb():.0f}GB（{pct:.0f}%）{delta_txt}")
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
    lines.append("以上 Top 为缓存/模型/数据分类参考；业务数据（6-产品研发/rkr_staging）不做自动清理。")

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
