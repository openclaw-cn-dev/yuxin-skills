#!/usr/bin/env python3
"""公司项目每日扫描 — 渔芯 /6-产品研发/ 28 项目状态 + 进化信号

用法：
  python3 company-project-scan.py                  # 全量扫描（状态 + 信号）
  python3 company-project-scan.py --quick          # 仅状态（快）
  python3 company-project-scan.py --base /path     # 自定义根目录

输出：JSON 到 stdout，便于管道下游消费（cron 后处理 / 飞书汇报）。

设计目标：
- 60s 内完成 28 项目扫描（即使其中 FindEra/RKR 含 30万+ 文件）
- 排除 node_modules / .git / __pycache__ / venv / 数据目录
- 输出字段：状态、最近活跃、代码统计、git 状态、信号命中

历史：
- 2026-08-03 玉芬首次实现（替代纯 bash find，每次超时 60-180s）
- 替代 2026-07-13 reference/***SECRET***.md 的 bash 三阶段方案
- 解决了 FindEra 393k md / RKR 260k md / 出图 41k 文件的扫描超时
"""
import argparse
import json
import os
import subprocess
from datetime import datetime
from pathlib import Path

DEFAULT_BASE = Path("/Users/hua/6-产品研发")

EXCLUDE_DIRS = {
    "node_modules", ".git", "venv", ".venv", "__pycache__",
    ".next", "dist", "build", ".pytest_cache", ".mypy_cache",
    "target", "outputs", "checkpoints", "models", "data",
    ".cache", "frontend/node_modules", "chroma",
}

THRESH_ACTIVE = 7
THRESH_SLOW = 30
THRESH_STAGNANT = 90


def status_from_days(days: int) -> str:
    if days <= THRESH_ACTIVE:
        return "🟢 活跃"
    if days <= THRESH_SLOW:
        return "🟡 缓慢"
    if days <= THRESH_STAGNANT:
        return "🔴 停滞"
    return "⚫ 长停"


def has_readme(root: Path):
    """查找 README（按优先级顺序）"""
    for name in ["README.md", "readme.md", "README.rst", "README", "README.txt"]:
        if (root / name).exists():
            return True, name
    return False, None


def git_dirty_count(root: Path):
    """git dirty 文件数（-1 = 不是 git 仓库）"""
    if not (root / ".git").exists():
        return -1
    try:
        r = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=root, capture_output=True, text=True, timeout=8,
        )
        return len([l for l in r.stdout.splitlines() if l.strip()])
    except Exception:
        return -1


def scan_project(root: Path, now: datetime) -> dict:
    if not root.exists():
        return None
    top_mtime = datetime.fromtimestamp(root.stat().st_mtime)

    all_files = []
    code_count = 0
    md_count = 0
    big_count = 0  # > 1MB
    has_tests_dir = False
    has_docker = False
    test_file_count = 0
    max_depth = 4

    try:
        for dirpath, dirnames, filenames in os.walk(root):
            rel = Path(dirpath).relative_to(root).parts
            if len(rel) > max_depth:
                dirnames.clear()
                continue
            dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]
            if "tests" in dirnames or "test" in dirnames or "__tests__" in dirnames:
                has_tests_dir = True
            for fn in filenames:
                fp = Path(dirpath) / fn
                try:
                    mtime = datetime.fromtimestamp(fp.stat().st_mtime)
                    all_files.append((fp, mtime))
                except (OSError, PermissionError):
                    continue
                ext = fp.suffix.lower()
                if ext in {".py", ".js", ".ts", ".vue", ".tsx", ".jsx",
                           ".go", ".rs", ".java", ".kt", ".swift"}:
                    code_count += 1
                elif ext == ".md":
                    md_count += 1
                try:
                    if fp.stat().st_size > 1024 * 1024:
                        big_count += 1
                except OSError:
                    pass
                if fn in ("Dockerfile", "docker-compose.yml", "docker-compose.yaml"):
                    has_docker = True
                if fn.startswith("test_") or fn.endswith("_test.py") or ".test." in fn or ".spec." in fn:
                    test_file_count += 1
    except (OSError, PermissionError):
        pass

    if all_files:
        latest_file, latest_mtime = max(all_files, key=lambda x: x[1])
        days_since = (now - latest_mtime).days
        latest_rel = str(latest_file.relative_to(root))
    else:
        latest_mtime = top_mtime
        days_since = (now - top_mtime).days
        latest_rel = None

    has_rd, rd_name = has_readme(root)
    dirty = git_dirty_count(root)

    return {
        "name": root.name,
        "top_mtime": top_mtime.strftime("%Y-%m-%d"),
        "latest_mtime": latest_mtime.strftime("%Y-%m-%d"),
        "days_since": days_since,
        "status": status_from_days(days_since),
        "has_readme": has_rd,
        "readme_name": rd_name,
        "code_files": code_count,
        "md_files": md_count,
        "total_files": len(all_files),
        "big_files": big_count,
        "has_docker": has_docker,
        "has_tests": has_tests_dir or test_file_count > 0,
        "test_files": test_file_count,
        "is_git": dirty >= 0,
        "dirty_count": dirty,
        "latest_file": latest_rel,
    }


def scan_signals(projects: list) -> dict:
    signals = {
        "shell_projects": [],
        "duplicate_candidates": [],
        "deployment_gap": [],
        "test_gap": [],
        "git_hygiene": [],
        "very_stale": [],
        "large_active": [],
    }

    for p in projects:
        if p["code_files"] == 0 and p["md_files"] <= 5 and p["days_since"] > 14:
            signals["shell_projects"].append({
                "name": p["name"], "days": p["days_since"], "files": p["total_files"],
            })
        if not p["has_docker"] and p["code_files"] >= 5:
            signals["deployment_gap"].append({
                "name": p["name"], "code": p["code_files"],
            })
        if p["code_files"] >= 10 and not p["has_tests"]:
            signals["test_gap"].append({
                "name": p["name"], "code": p["code_files"],
            })
        if p["dirty_count"] > 1000:
            signals["git_hygiene"].append({
                "name": p["name"], "dirty": p["dirty_count"],
            })
        if p["days_since"] > 30:
            signals["very_stale"].append({
                "name": p["name"], "days": p["days_since"], "status": p["status"],
            })
        if p["total_files"] > 100_000 and p["days_since"] <= 7:
            signals["large_active"].append({
                "name": p["name"], "files": p["total_files"], "days": p["days_since"],
            })

    name_groups = {}
    for p in projects:
        n = p["name"].lower()
        fp = "".join(c for c in n[:8] if not c.isdigit()).strip("-")
        if fp and len(fp) >= 3:
            name_groups.setdefault(fp, []).append(p["name"])
    for fp, names in name_groups.items():
        if len(names) >= 2 and not any("公共" in n or "组件" in n for n in names):
            signals["duplicate_candidates"].append({
                "fingerprint": fp, "candidates": names,
            })

    return signals


def main():
    parser = argparse.ArgumentParser(description="公司项目每日扫描")
    parser.add_argument("--base", default=str(DEFAULT_BASE), help="项目根目录")
    parser.add_argument("--quick", action="store_true", help="仅状态，跳过信号")
    args = parser.parse_args()

    base = Path(args.base)
    if not base.exists():
        print(json.dumps({"error": f"base not found: {base}"}))
        return
    now = datetime.now()

    projects = []
    for entry in sorted(base.iterdir()):
        if entry.is_dir() and not entry.name.startswith("."):
            proj_data = scan_project(entry, now)
            if proj_data is not None:
                projects.append(proj_data)

    status_order = {"🟢 活跃": 0, "🟡 缓慢": 1, "🔴 停滞": 2, "⚫ 长停": 3}
    projects.sort(key=lambda x: (status_order.get(x["status"], 9), x["days_since"]))

    output = {
        "scan_time": now.strftime("%Y-%m-%d %H:%M:%S"),
        "base": str(base),
        "project_count": len(projects),
        "projects": projects,
    }
    if not args.quick:
        output["signals"] = scan_signals(projects)

    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
