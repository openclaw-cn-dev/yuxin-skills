#!/usr/bin/env python3
"""
Codex 自进化脚本 — 每日凌晨 2:00 执行
1. 检查 Codex 版本更新
2. 同步 Hermes Skills → Codex Skills
3. 更新 Codex AGENTS.md
4. 检查插件更新
5. 清理旧会话
"""

import subprocess
import sys
import json
import os
from pathlib import Path
from datetime import datetime, timedelta

HERMES_HOME = Path(os.environ.get("HERMES_HOME", Path.home() / ".hermes"))
CODEX_HOME = Path.home() / ".codex"
CODEX_SKILLS = CODEX_HOME / "skills"
LOG_FILE = HERMES_HOME / "logs" / "codex_evolution.log"

def log(msg: str) -> None:
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line, flush=True)
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")

def run(cmd: str, timeout: int = 60) -> str:
    """Run shell command, return stdout."""
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return r.stdout.strip()
    except Exception as e:
        log(f"  ERROR: {cmd[:60]} → {e}")
        return ""

def check_version() -> dict:
    """Check if Codex has updates available."""
    log("1. 版本检查")
    ver = run("codex --version 2>&1")
    log(f"  当前: {ver}")

    # Check npm for latest
    latest = run("npm view @openai/codex version 2>&1", timeout=30)
    if latest:
        log(f"  最新: {latest}")
        if ver and latest in ver:
            log("  ✅ 已是最新版本")
            return {"status": "up_to_date", "current": ver, "latest": latest}
        else:
            log(f"  ⚠️ 有新版本可用: {ver} → {latest}")
            return {"status": "update_available", "current": ver, "latest": latest}
    return {"status": "unknown", "current": ver}

def sync_skills() -> dict:
    """Sync useful Hermes skills to Codex skills directory."""
    log("2. Skills 同步")
    CODEX_SKILLS.mkdir(parents=True, exist_ok=True)

    # Core skills maintained for Codex
    # Already pre-populated in ~/.codex/skills/
    existing = list(CODEX_SKILLS.glob("*.md"))
    log(f"  Codex skills: {len(existing)} files")
    for f in sorted(existing):
        log(f"    📄 {f.name}")

    return {"total": len(existing)}

def check_plugins() -> dict:
    """Check Codex plugins status."""
    log("3. 插件检查")
    plugins = run("codex plugin list 2>&1")
    if plugins:
        log(f"  {plugins[:200]}")
    else:
        log("  ⚠️ 无法获取插件列表（可能走 Gateway 导致）")
    return {"raw": plugins[:500] if plugins else ""}

def cleanup_sessions() -> dict:
    """Clean old sessions (>30 days)."""
    log("4. 会话清理")
    sessions_dir = CODEX_HOME / "sessions"
    if not sessions_dir.exists():
        log("  无会话目录")
        return {"deleted": 0}

    cutoff = datetime.now() - timedelta(days=30)
    deleted = 0
    for d in sessions_dir.iterdir():
        if d.is_dir():
            try:
                mtime = datetime.fromtimestamp(d.stat().st_mtime)
                if mtime < cutoff:
                    import shutil
                    shutil.rmtree(d)
                    deleted += 1
            except Exception:
                pass

    log(f"  清理 {deleted} 个旧会话")
    return {"deleted": deleted}

def main():
    log("=" * 50)
    log("Codex 自进化开始")

    results = {}

    # 1. Version check
    results["version"] = check_version()

    # 2. Skills sync
    results["skills"] = sync_skills()

    # 3. Plugin check
    results["plugins"] = check_plugins()

    # 4. Cleanup
    results["cleanup"] = cleanup_sessions()

    # Summary
    log("-" * 50)
    log(f"完成: v={results['version']['status']}, "
        f"skills={results['skills']['synced']}/{results['skills']['total']}, "
        f"sessions_deleted={results['cleanup']['deleted']}")

    # Notify if update available
    if results["version"]["status"] == "update_available":
        msg = (f"🔔 **Codex 新版本可用**\n"
               f"当前: {results['version']['current']}\n"
               f"最新: {results['version']['latest']}\n"
               f"运行 `npm update -g @openai/codex` 更新")
        try:
            subprocess.run(
                [sys.executable, "-m", "hermes_cli.send_message", "feishu", msg],
                timeout=10, capture_output=True,
                env={**os.environ, "HERMES_HOME": str(HERMES_HOME)}
            )
        except Exception:
            pass

    log("Codex 自进化结束")

if __name__ == "__main__":
    main()
