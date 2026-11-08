#!/usr/bin/env python3
"""
DeepSeek Harness (dsh) 自进化脚本 — 每日 05:00 执行
1. 版本检查 (package.json version + git commit + npm view + git upstream 落后数)
2. 会话盘点 (按项目分组)
3. 会话清理 (>30 天)
4. 同步 dsh 状态到公司 GitHub 私仓 yuxin-skills/dsh/

设计原则 (针对 dsh 的 git 源码安装特性):
- dsh 是源码 monorepo (git clone + pnpm), 不是 npm 全局包
- 开发者预览版, AGENTS.md 明确"未来将出现破坏兼容性的变更"
- 因此: 只检测 + 通知, 不自动 git pull (由华哥手动触发一键更新)
"""
import subprocess
import sys
import json
import os
import re
import shutil
from pathlib import Path
from datetime import datetime, timedelta

# ⚠️ Hermes profile 可能把 $HOME 改成 ~/.hermes/profiles/<name>/home/,
#    导致 Path.home() / "~" 全部错位。必须显式硬编码。
USER_HOME = Path("/Users/hua")
HERMES_HOME = USER_HOME / ".hermes"

# dsh 源码仓库 (git clone 到系统文件夹, 与 Claude/Codex 平级)
DSH_REPO = USER_HOME / "系统文件夹" / "deepseek-harness"
# dsh 配置目录 (~/.dsh, 尚未软链接到系统文件夹)
DSH_HOME = USER_HOME / ".dsh"
DSH_SESSIONS = DSH_HOME / "sessions"

LOG_FILE = HERMES_HOME / "logs" / "dsh_evolution.log"

# ── GitHub 同步配置 ─────────────────────────────────────────────
GITHUB_USER = "openclaw-cn-dev"
GITHUB_REPO = "yuxin-skills"
GITHUB_URL = f"git@github.com:{GITHUB_USER}/{GITHUB_REPO}.git"
DSH_SUBDIR = "dsh"                                # yuxin-skills/dsh/
SYNC_WORK_DIR = Path("/tmp") / f"{GITHUB_REPO}-dsh-sync"
GITHUB_LOG = HERMES_HOME / "logs" / "dsh_github_sync.log"

# 会话保留天数
SESSION_RETENTION_DAYS = 30


def log(msg: str) -> None:
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")


def run(cmd: str, timeout: int = 60) -> str:
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return r.stdout.strip()
    except Exception as e:
        return f"__ERR__{e}"


def _read_pkg_version() -> str:
    """读 package.json 里的 version 字段."""
    pkg = DSH_REPO / "package.json"
    if not pkg.exists():
        return "?"
    try:
        return json.loads(pkg.read_text()).get("version", "?")
    except Exception:
        return "?"


def _git_short_hash() -> str:
    """当前 commit 短 hash."""
    out = run(f"git -C '{DSH_REPO}' rev-parse --short HEAD 2>&1")
    return out if out and not out.startswith("__ERR__") else "?"


def check_version() -> dict:
    """版本检查: 本地版本 + commit + git upstream 落后数.

    ⚠️ 2026-08-16 修正: 源码安装的判断依据是 git upstream 落后数, 不是 npm。
    之前的 bug: 拿 npm 发布版 CLI 包 `@deepseek-ai/dsh`(rc.6) 对比本地
    monorepo 根包 `@deepseek-ai/dsh-root`(rc.5, 此包在 npm 上 E404 不存在),
    两者是不同发布轨道, 导致"rc.6 已发布"误报。
    """
    log("1. 版本检查")
    ver = _read_pkg_version()
    commit = _git_short_hash()
    log(f"  本地: v{ver} (commit {commit})")

    # git upstream 落后数 (fetch 后统计) — 源码安装唯一可靠依据
    behind = -1
    fetch_out = run(f"git -C '{DSH_REPO}' fetch origin master 2>&1", timeout=90)
    if "__ERR__" in fetch_out or "fatal" in fetch_out.lower():
        log(f"  ⚠️ git fetch 失败: {fetch_out[:100]}")
    else:
        cnt = run(f"git -C '{DSH_REPO}' rev-list HEAD..origin/master --count 2>&1")
        if cnt.isdigit():
            behind = int(cnt)

    # 判断状态 (只看 git, npm 子包版本与 monorepo 根包不同轨, 仅日志参考)
    if behind > 0:
        log(f"  ⚠️ git upstream 落后 {behind} 个 commit")
        status = "update_available"
    elif behind == 0:
        log("  ✅ 已是最新 (与 origin/master 同步)")
        status = "up_to_date"
    else:
        status = "unknown"

    return {
        "status": status,
        "current": ver,
        "commit": commit,
        "npm_latest": "",   # 已弃用: npm @deepseek-ai/dsh 与本地 root 包不同轨
        "behind_commits": behind,
    }


def _decode_project_name(raw: str) -> str:
    """dsh 把项目路径编码成 ~XXXX (类似 escape 的 %uXXXX 变体), 解码成可读中文."""
    # --Users-hua-6-~4EA7~54C1... -> /Users/hua/6-产品研发/...
    def repl(m):
        try:
            return chr(int(m.group(1), 16))
        except Exception:
            return m.group(0)
    name = re.sub(r'~([0-9A-Fa-f]{4})', repl, raw)
    # 把 -- 还原成 /, 把剩余单个 - 还原成空格 (dsh 的路径→目录名约定)
    name = name.strip('-').replace('--', '/')
    return name


def inspect_sessions() -> dict:
    """会话盘点: 按项目分组统计 session 数."""
    log("2. 会话盘点")
    if not DSH_SESSIONS.exists():
        log("  无会话目录")
        return {"projects": {}, "total": 0}
    projects = {}
    total = 0
    for proj in DSH_SESSIONS.iterdir():
        if not proj.is_dir():
            continue
        name = _decode_project_name(proj.name)
        sessions = [d for d in proj.iterdir() if d.is_dir() and d.name.startswith("session-")]
        projects[name] = len(sessions)
        total += len(sessions)
    log(f"  {len(projects)} 个项目, {total} 个会话")
    for name, n in sorted(projects.items(), key=lambda x: -x[1]):
        log(f"    📁 {name}: {n}")
    return {"projects": projects, "total": total}


def cleanup_sessions() -> dict:
    """清理 >30 天的旧会话."""
    log("3. 会话清理")
    if not DSH_SESSIONS.exists():
        log("  无会话目录")
        return {"deleted": 0}
    cutoff = datetime.now() - timedelta(days=SESSION_RETENTION_DAYS)
    deleted = 0
    for proj in DSH_SESSIONS.iterdir():
        if not proj.is_dir():
            continue
        for sess in proj.iterdir():
            if not sess.is_dir():
                continue
            try:
                mtime = datetime.fromtimestamp(sess.stat().st_mtime)
                if mtime < cutoff:
                    shutil.rmtree(sess)
                    deleted += 1
            except Exception:
                pass
    log(f"  清理 {deleted} 个旧会话")
    return {"deleted": deleted}


# ════════════════════════════════════════════════════════════════
# GitHub 同步模块
# ════════════════════════════════════════════════════════════════

def _gh_log(msg: str) -> None:
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    GITHUB_LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(GITHUB_LOG, "a") as f:
        f.write(line + "\n")


def _run_git(args: list, cwd: Path, timeout: int = 60) -> tuple:
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


def _redact_yaml(text: str) -> str:
    """脱敏 credentials.yaml: 敏感字段值替换为 <REDACTED>, 只保留 key 名."""
    out = []
    for line in text.splitlines():
        # 匹配 key: value 形式, 且 key 含敏感关键词
        if re.search(r'(?i)(key|token|secret|password|credential|bearer)', line):
            key = line.split(":", 1)[0]
            out.append(f"{key}: <REDACTED>")
        else:
            out.append(line)
    return "\n".join(out)


def _build_status_md(version_info: dict, sessions_info: dict) -> str:
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    proj_lines = "\n".join(
        f"- `{name}`: {n} 会话" for name, n in
        sorted(sessions_info.get("projects", {}).items(), key=lambda x: -x[1])
    ) or "- (无)"
    return f"""# DeepSeek Harness (dsh) 状态快照
> 导出时间: {ts}
> 🤖 自动同步自 Hermes/玉芬 · dsh 自进化模块

## 版本
- 本地: `v{version_info.get('current', '?')}` (commit `{version_info.get('commit', '?')}`)
- npm 最新: `{version_info.get('npm_latest', '?')}`
- upstream 落后: `{version_info.get('behind_commits', '?')}` commit
- 状态: `{version_info.get('status', '?')}`

## 安装方式
- 源码 monorepo: `git clone https://github.com/deepseek-ai/deepseek-harness.git`
- 本地路径: `系统文件夹/deepseek-harness` (与 Claude/Codex 平级)
- 运行: `pnpm dsh web` (Web UI 默认 127.0.0.1:3080)
- 配置目录: `~/.dsh` (⚠️ 尚未软链接到系统文件夹)

## 会话 ({sessions_info.get('total', 0)} 个)
{proj_lines}

## 同步策略
- 仅同步状态快照 + 配置结构, 不上传真实凭据
- `.credentials.yaml` 自动脱敏 (DEEPSEEK_API_KEY → <REDACTED>)
- 更新策略: 检测 + 通知, 不自动 git pull (预览版有破坏性变更风险)
- 一键更新: `bash ~/.hermes/scripts/dsh_update.sh`

## 仓库结构
```
yuxin-skills/
├── claude-code/    ← Claude Code
├── codex/          ← Codex
├── hermes/         ← Hermes
└── dsh/            ← 本目录 (DeepSeek Harness)
```

> 🔒 公司内部资产，禁止对外公开。
"""


def sync_to_github(version_info: dict, sessions_info: dict) -> dict:
    """同步 dsh 状态到 yuxin-skills/dsh/."""
    _gh_log("4. GitHub 同步开始")
    _gh_log(f"  目标: {GITHUB_URL} → {DSH_SUBDIR}/")

    # 1. clone or pull
    if SYNC_WORK_DIR.exists() and (SYNC_WORK_DIR / ".git").exists():
        rc, _, err = _run_git(["pull", "--rebase", "origin", "main"], SYNC_WORK_DIR, timeout=60)
        if rc != 0:
            _gh_log(f"  WARN: pull 失败 ({err[:120]})，重 clone")
            shutil.rmtree(SYNC_WORK_DIR)
    if not (SYNC_WORK_DIR.exists() and (SYNC_WORK_DIR / ".git").exists()):
        if SYNC_WORK_DIR.exists():
            shutil.rmtree(SYNC_WORK_DIR)
        rc, _, err = _run_git(
            ["clone", "--depth", "1", GITHUB_URL, str(SYNC_WORK_DIR)],
            Path("/tmp"), timeout=120,
        )
        if rc != 0:
            _gh_log(f"  ❌ clone 失败: {err[:300]}")
            return {"status": "clone_failed", "error": err}
    _gh_log("  ✅ 仓库就绪")

    # 2. 准备 dsh/ 子目录
    dsh_dir = SYNC_WORK_DIR / DSH_SUBDIR
    dsh_dir.mkdir(parents=True, exist_ok=True)

    # 2.1 STATUS.md
    (dsh_dir / "STATUS.md").write_text(_build_status_md(version_info, sessions_info))
    _gh_log("  📄 STATUS.md")

    # 2.2 credentials 结构 (脱敏)
    cred = DSH_HOME / ".credentials.yaml"
    if cred.exists():
        raw = cred.read_text()
        (dsh_dir / "credentials.yaml.redacted").write_text(_redact_yaml(raw))
        _gh_log("  📄 credentials.yaml.redacted (脱敏)")

    # 2.3 .gitignore
    (dsh_dir / ".gitignore").write_text(
        "# dsh sync generated\n*.log\n__pycache__/\n.DS_Store\n"
    )

    # 3. 检查变化
    rc, status_out, _ = _run_git(["status", "--porcelain"], SYNC_WORK_DIR)
    if not status_out:
        _gh_log("  ℹ️ 无变化，跳过 commit")
        return {"status": "no_changes"}

    # 4. commit + push
    _run_git(["add", "-A"], SYNC_WORK_DIR)
    ts = datetime.now().strftime("%Y%m%d-%H%M")
    msg = (f"🤖 dsh sync: {ts} | "
           f"v={version_info.get('current', '?')}@{version_info.get('commit', '?')}, "
           f"behind={version_info.get('behind_commits', '?')}, "
           f"sessions={sessions_info.get('total', 0)}")
    rc, _, err = _run_git(["commit", "-m", msg], SYNC_WORK_DIR)
    if rc != 0:
        _gh_log(f"  ❌ commit 失败: {err[:200]}")
        return {"status": "commit_failed", "error": err}
    rc, _, err = _run_git(["push", "origin", "main"], SYNC_WORK_DIR, timeout=120)
    if rc != 0:
        _gh_log(f"  ❌ push 失败: {err[:200]}")
        return {"status": "push_failed", "error": err}
    _gh_log("  ✅ push 成功 → origin/main")
    return {"status": "pushed", "version": version_info.get("current")}


def main():
    log("=" * 50)
    log("DeepSeek Harness (dsh) 自进化开始")

    results = {}
    results["version"] = check_version()
    results["sessions"] = inspect_sessions()
    results["cleanup"] = cleanup_sessions()

    try:
        results["github"] = sync_to_github(results["version"], results["sessions"])
    except Exception as e:
        log(f"  ⚠️ GitHub 同步异常 (不影响主流程): {e}")
        _gh_log(f"  ⚠️ 异常: {e}")
        results["github"] = {"status": "exception", "error": str(e)}

    log("-" * 50)
    log(f"完成: v={results['version']['status']}, "
        f"sessions={results['sessions']['total']}, "
        f"cleaned={results['cleanup']['deleted']}, "
        f"github={results['github'].get('status', '?')}")

    # 检测到更新 → 打印通知 (cron no_agent 模式会投递 stdout)
    if results["version"]["status"] == "update_available":
        v = results["version"]
        lines = [
            "🔔 **DeepSeek Harness (dsh) 有新版本可用**",
            f"当前: v{v['current']} (commit {v['commit']})",
        ]
        if v.get("npm_latest") and v["npm_latest"] != v["current"]:
            lines.append(f"npm 最新: v{v['npm_latest']}")
        if v.get("behind_commits", 0) > 0:
            lines.append(f"upstream 落后 {v['behind_commits']} commit")
        lines.append("")
        lines.append("一键更新: `bash ~/.hermes/scripts/dsh_update.sh`")
        lines.append("(预览版有破坏性变更风险，请手动确认后更新)")
        print("\n".join(lines))

    log("DeepSeek Harness (dsh) 自进化结束")


if __name__ == "__main__":
    main()
