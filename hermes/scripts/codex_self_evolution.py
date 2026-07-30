#!/usr/bin/env python3
"""
Codex 自进化脚本 — 每日凌晨 2:00 执行
1. 检查 Codex 版本更新
2. 同步 Hermes Skills → Codex Skills
3. 更新 Codex AGENTS.md
4. 检查插件更新
5. 清理旧会话
6. 同步 Codex 状态/技能/插件到公司 GitHub 私仓 yuxin-skills/codex/
"""

import subprocess
import sys
import json
import os
import re
import shutil
from pathlib import Path
from datetime import datetime, timedelta

HERMES_HOME = Path(os.environ.get("HERMES_HOME", Path("/Users/hua/.hermes")))
# ⚠️ Hermes profile 可能把 $HOME 改成 ~/.hermes/profiles/<name>/home/，
#    导致 Path.home() / "~/.codex" 全部错位。必须显式硬编码 USER_HOME。
USER_HOME = Path("/Users/hua")
CODEX_HOME = USER_HOME / ".codex"
CODEX_SKILLS = CODEX_HOME / "skills"
LOG_FILE = HERMES_HOME / "logs" / "codex_evolution.log"

# ── GitHub 同步配置 ─────────────────────────────────────────────
GITHUB_USER = "openclaw-cn-dev"
GITHUB_REPO = "yuxin-skills"
GITHUB_URL = f"git@github.com:{GITHUB_USER}/{GITHUB_REPO}.git"
CODEX_SUBDIR = "codex"                              # yuxin-skills/codex/
SYNC_WORK_DIR = Path("/tmp") / f"{GITHUB_REPO}-codex-sync"
GITHUB_LOG = HERMES_HOME / "logs" / "codex_github_sync.log"

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
    raw = run("npm view @openai/codex version 2>&1", timeout=30)
    # 提取真正的版本号 (npm 报错时可能返回 "npm error...\n0.146.0" 多行)
    m = re.search(r'\d+\.\d+\.\d+(?:[\.\-][\w]+)*', raw) if raw else None
    latest = m.group(0) if m else ""
    if latest:
        log(f"  最新: {latest}")
        if ver and latest in ver:
            log("  ✅ 已是最新版本")
            return {"status": "up_to_date", "current": ver, "latest": latest}
        else:
            log(f"  ⚠️ 有新版本可用: {ver} → {latest}")
            return {"status": "update_available", "current": ver, "latest": latest}
    log(f"  ⚠️ npm 无法获取最新版本 (raw: {raw[:80]!r})")
    return {"status": "unknown", "current": ver, "latest_raw": raw[:200]}

def sync_skills() -> dict:
    """Sync useful Hermes skills to Codex skills directory."""
    log("2. Skills 同步")
    CODEX_SKILLS.mkdir(parents=True, exist_ok=True)

    # Core skills maintained for Codex
    # Already pre-populated in ~/.codex/skills/
    existing_files = list(CODEX_SKILLS.glob("*.md"))
    existing_dirs = [d for d in CODEX_SKILLS.iterdir() if d.is_dir()]
    total = len(existing_files) + len(existing_dirs)
    log(f"  Codex skills: {len(existing_files)} .md files + {len(existing_dirs)} dirs = {total} total")
    for f in sorted(existing_files):
        log(f"    📄 {f.name}")
    for d in sorted(existing_dirs)[:5]:
        log(f"    📁 {d.name}/")

    return {"total": total, "synced": 0, "files": len(existing_files), "dirs": len(existing_dirs)}

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
                    shutil.rmtree(d)
                    deleted += 1
            except Exception:
                pass

    log(f"  清理 {deleted} 个旧会话")
    return {"deleted": deleted}


# ════════════════════════════════════════════════════════════════
# GitHub 同步模块 — 仿 Claude Code 那套 yuxin-skills/claude-code/
# ════════════════════════════════════════════════════════════════

def _gh_log(msg: str) -> None:
    """GitHub 同步专用日志 (独立文件, 不污染主 evolution log)."""
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line, flush=True)
    GITHUB_LOG.parent.mkdir(parents=True, exist_ok=True)
    with GITHUB_LOG.open("a") as f:
        f.write(line + "\n")


def _run_git(args: list, cwd: Path, timeout: int = 60) -> tuple:
    """Run git command. Returns (returncode, stdout, stderr)."""
    env = {**os.environ, "GIT_TERMINAL_PROMPT": "0"}
    try:
        r = subprocess.run(
            ["git"] + args, cwd=str(cwd),
            capture_output=True, text=True, timeout=timeout, env=env,
        )
        return r.returncode, r.stdout.strip(), r.stderr.strip()
    except subprocess.TimeoutExpired:
        return -1, "", "timeout"
    except Exception as e:
        return -1, "", str(e)


_SENSITIVE_RE = re.compile(
    r'(?i)(token|secret|password|api_key|bearer|authorization|auth_token|credential)'
)


def _redact_toml(text: str) -> tuple:
    """脱敏 toml: 把含敏感关键词的字段值替换为 <REDACTED>.
    返回 (redacted_text, redacted_count).
    """
    pattern = re.compile(
        r'(?im)^(\s*[\w.\-]*?(?:' + '|'.join([
            'token', 'secret', 'password', 'api_key', 'bearer',
            'authorization', 'auth_token', 'credential',
        ]) + r')[\w.\-]*\s*=\s*)(["\'])([^"\']*?)\2'
    )
    count = 0

    def repl(m):
        nonlocal count
        count += 1
        return f'{m.group(1)}{m.group(2)}<REDACTED>{m.group(2)}'

    return pattern.sub(repl, text), count


def _collect_yuxin_skills() -> tuple:
    """收集 ~/.codex/skills/ 下 yuxin-* 前缀的所有文件和目录."""
    if not CODEX_SKILLS.exists():
        return [], []
    files = sorted([p for p in CODEX_SKILLS.glob("yuxin-*") if p.is_file()])
    dirs = sorted([p for p in CODEX_SKILLS.glob("yuxin-*") if p.is_dir()])
    return files, dirs


def _build_plugins_manifest() -> dict:
    """扫描 ~/.codex/plugins/ 生成清单."""
    plugins_root = CODEX_HOME / "plugins"
    cache_sources, data_sources = [], []
    cache = plugins_root / "cache"
    if cache.exists():
        cache_sources = sorted([d.name for d in cache.iterdir()
                               if d.is_dir() and not d.name.startswith(".")])
    data = plugins_root / "data"
    if data.exists():
        data_sources = sorted([d.name for d in data.iterdir()
                              if d.is_dir() and not d.name.startswith(".")])
    return {
        "scanned_at": datetime.now().isoformat(timespec="seconds"),
        "cache_sources": cache_sources,
        "data_sources": data_sources,
        "note": "manifest-only, 不上传插件二进制 (避免污染 GitHub)",
    }


def _build_status_md(version_info: dict, plugins_info: dict,
                     skill_files: int, skill_dirs: int) -> str:
    """生成 STATUS.md (Claude Code 那边的 STATUS.md 风格)."""
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cache_list = "\n".join(f"- `{s}`" for s in plugins_info.get("cache_sources", [])) or "- (无)"
    data_list = "\n".join(f"- `{s}`" for s in plugins_info.get("data_sources", [])) or "- (无)"
    return f"""# Codex 状态快照
> 导出时间: {ts}
> 🤖 自动同步自 Hermes/玉芬 · Codex 自进化模块

## 版本
- 当前: `{version_info.get('current', '?')}`
- npm 最新: `{version_info.get('latest', '?')}`
- 状态: `{version_info.get('status', '?')}`

## 公司专属 Skills (yuxin-*)
- 文件: {skill_files} 个
- 目录: {skill_dirs} 个

## 插件来源 (cache/)
{cache_list}

## 数据源 (data/)
{data_list}

## 同步策略
- 仅同步 `yuxin-*` 前缀的 skills (公司专属资产)
- 通用 skills (algorithmic-art, pdf, pptx 等) 不上传 (避免污染 GitHub)
- `config.toml` 自动脱敏 (含 token/secret/bearer 的字段值替换为 `<REDACTED>`)
- 同步缓存目录: `/tmp/yuxin-skills-codex-sync/`
- 触发: (1) 凌晨 2:00 self_evolution (2) 每小时 cron 轻量增量

## 仓库结构
```
yuxin-skills/
├── claude-code/    ← Claude Code 那边的 sync (已有)
├── drawing-skills/
├── hermes/         ← Hermes 那边的 sync (已有)
└── codex/          ← 本目录 (本次新增)
```

> 🔒 公司内部资产，禁止对外公开。
"""


def sync_to_github(version_info: dict, plugins_info: dict) -> dict:
    """Step 6: clone/pull 仓库 → 同步 codex/ 子目录 → commit → push."""
    _gh_log("6. GitHub 同步开始")
    _gh_log(f"  目标: {GITHUB_URL} → {CODEX_SUBDIR}/")

    # 1. clone or pull
    if SYNC_WORK_DIR.exists() and (SYNC_WORK_DIR / ".git").exists():
        _gh_log(f"  pull: {SYNC_WORK_DIR}")
        rc, _, err = _run_git(["pull", "--rebase", "origin", "main"], SYNC_WORK_DIR, timeout=60)
        if rc != 0:
            _gh_log(f"  WARN: pull 失败 ({err[:150]})，重 clone")
            shutil.rmtree(SYNC_WORK_DIR)
            rc, _, err = _run_git(
                ["clone", "--depth", "1", GITHUB_URL, str(SYNC_WORK_DIR)],
                Path("/tmp"), timeout=120,
            )
            if rc != 0:
                _gh_log(f"  ❌ clone 失败: {err[:300]}")
                return {"status": "clone_failed", "error": err}
    else:
        if SYNC_WORK_DIR.exists():
            shutil.rmtree(SYNC_WORK_DIR)
        _gh_log(f"  clone: {SYNC_WORK_DIR}")
        rc, _, err = _run_git(
            ["clone", "--depth", "1", GITHUB_URL, str(SYNC_WORK_DIR)],
            Path("/tmp"), timeout=120,
        )
        if rc != 0:
            _gh_log(f"  ❌ clone 失败: {err[:300]}")
            return {"status": "clone_failed", "error": err}

    _gh_log(f"  ✅ 仓库就绪")

    # 2. 准备 codex/ 子目录
    codex_dir = SYNC_WORK_DIR / CODEX_SUBDIR
    codex_dir.mkdir(parents=True, exist_ok=True)

    # 2.1 AGENTS.md (全文同步)
    agents_src = CODEX_HOME / "AGENTS.md"
    if agents_src.exists():
        shutil.copy2(agents_src, codex_dir / "AGENTS.md")
        _gh_log(f"  📄 AGENTS.md ({agents_src.stat().st_size} bytes)")

    # 2.2 config.toml (脱敏)
    config_src = CODEX_HOME / "config.toml"
    redacted_count = 0
    if config_src.exists():
        raw = config_src.read_text()
        redacted, redacted_count = _redact_toml(raw)
        (codex_dir / "config.toml").write_text(redacted)
        _gh_log(f"  📄 config.toml (脱敏 {redacted_count} 字段)")

    # 2.3 skills/yuxin-*
    skill_files, skill_dirs = _collect_yuxin_skills()
    skills_dst = codex_dir / "skills"
    skills_dst.mkdir(exist_ok=True)
    # 清空旧的 yuxin-* 内容 (避免远端残留过时文件)
    if skills_dst.exists():
        for old in skills_dst.glob("yuxin-*"):
            if old.is_dir():
                shutil.rmtree(old)
            else:
                old.unlink()
    for src in skill_files:
        shutil.copy2(src, skills_dst / src.name)
    for src in skill_dirs:
        shutil.copytree(src, skills_dst / src.name)
    _gh_log(f"  📁 skills/yuxin-* → {len(skill_files)} 文件 + {len(skill_dirs)} 目录")

    # 2.4 plugins.json
    (codex_dir / "plugins.json").write_text(
        json.dumps(plugins_info, indent=2, ensure_ascii=False) + "\n"
    )
    _gh_log(f"  📄 plugins.json (cache={len(plugins_info['cache_sources'])}, data={len(plugins_info['data_sources'])})")

    # 2.5 STATUS.md
    (codex_dir / "STATUS.md").write_text(
        _build_status_md(version_info, plugins_info, len(skill_files), len(skill_dirs))
    )
    _gh_log(f"  📄 STATUS.md")

    # 2.6 .gitignore
    (codex_dir / ".gitignore").write_text(
        "# Codex sync generated\n*.log\n__pycache__/\n.DS_Store\n"
    )

    # 3. 检查变化
    rc, status_out, _ = _run_git(["status", "--porcelain"], SYNC_WORK_DIR)
    if not status_out:
        _gh_log("  ℹ️ 无变化，跳过 commit")
        return {
            "status": "no_changes",
            "skills": len(skill_files) + len(skill_dirs),
        }

    # 4. commit
    _run_git(["add", "-A"], SYNC_WORK_DIR)
    ts = datetime.now().strftime("%Y%m%d-%H%M")
    msg = (
        f"🤖 Codex sync: {ts} | "
        f"v={version_info.get('current', '?').split()[0] if version_info.get('current') else '?'}, "
        f"skills={len(skill_files)+len(skill_dirs)}, "
        f"plugins={len(plugins_info['cache_sources'])}+{len(plugins_info['data_sources'])}, "
        f"redacted={redacted_count}"
    )
    rc, _, err = _run_git(["commit", "-m", msg], SYNC_WORK_DIR)
    if rc != 0:
        _gh_log(f"  ❌ commit 失败: {err[:200]}")
        return {"status": "commit_failed", "error": err}
    _gh_log(f"  ✅ commit: {msg[:80]}...")

    # 5. push
    rc, _, err = _run_git(["push", "origin", "main"], SYNC_WORK_DIR, timeout=120)
    if rc != 0:
        _gh_log(f"  ❌ push 失败: {err[:200]}")
        return {"status": "push_failed", "error": err}
    _gh_log(f"  ✅ push 成功 → origin/main")

    return {
        "status": "pushed",
        "skills": len(skill_files) + len(skill_dirs),
        "plugins": f"{len(plugins_info['cache_sources'])}+{len(plugins_info['data_sources'])}",
        "version": version_info.get("current"),
    }


def main():
    # 🎯 --sync-only 模式: 跳过 step 1-5，只跑 GitHub 同步 (hourly cron 用)
    if "--sync-only" in sys.argv:
        log("🎯 --sync-only 模式 (跳过 step 1-5)")
        version_info = check_version()
        plugins_manifest = _build_plugins_manifest()
        try:
            r = sync_to_github(version_info, plugins_manifest)
            log(f"sync-only 完成: {r.get('status')}, skills={r.get('skills')}")
        except Exception as e:
            log(f"❌ sync-only 异常: {e}")
            _gh_log(f"❌ sync-only 异常: {e}")
        return

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

    # 5. Plugins manifest (for GitHub sync)
    plugins_manifest = _build_plugins_manifest()

    # 6. GitHub sync (独立失败不影响主流程)
    try:
        results["github"] = sync_to_github(results["version"], plugins_manifest)
    except Exception as e:
        log(f"  ⚠️ GitHub 同步异常 (不影响其他步骤): {e}")
        _gh_log(f"  ⚠️ 异常: {e}")
        results["github"] = {"status": "exception", "error": str(e)}

    # Summary
    log("-" * 50)
    log(f"完成: v={results['version']['status']}, "
        f"skills={results['skills']['synced']}/{results['skills']['total']}, "
        f"sessions_deleted={results['cleanup']['deleted']}, "
        f"github={results['github'].get('status', '?')}")

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
