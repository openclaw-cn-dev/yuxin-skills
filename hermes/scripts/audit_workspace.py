#!/usr/bin/env python3
"""工作空间审计:扫描部门空间过去 7 天新增/修改的文件,按 agent 分组生成 markdown 报告。

2026-09-21 玉芬修复:文档库已重组为 ABCZ 结构,旧树 3-公司项目资料/ 已废弃
(只剩 304-公司运营/老莫-技术运维/rkr-daily-updates 还在写)。
新 ROOT = A-渔芯科技/A2-公司运营/部门空间/,agent 目录为拼音命名。
"""
import sys
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path("/Users/hua/rkr_staging/文档库/A-渔芯科技/A2-公司运营/部门空间")
LEGACY_ROOT = Path("/Users/hua/rkr_staging/文档库/3-公司项目资料")
WINDOW_DAYS = 7

# agent -> 目录名列表(部门空间下)。拼音名是活跃区,中文名是历史壳,一并归组。
AGENT_DIRS = {
    "毛豆": ["maodou", "毛豆-产品交付"],
    "小宝": ["xiaobao", "小宝-商务运营"],
    "老莫": ["laomo", "老莫-技术运维"],
    "阿福": ["afu", "阿福-客服"],
    "黑豆": ["heidou", "黑豆-行政财务法务", "黑-行政财务法务"],
    "玉芬": ["zhenglishi", "玉芬自我提升", "商业"],
    "宽博士": ["quant"],
}

# 不计入审计的文件名 / 顶层条目
EXCLUDED_NAMES = {".DS_Store"}
TOP_EXCLUDES = {"_backup", "_backups", "_scripts", "_state_backups", "_v6总览",
                "references", "ClaudeCode编程能力提升研究", "auto", "daily",
                "学习笔记"}
# agent 目录内不审计的子目录名(备份/脚本/自动产出)
AGENT_INTERNAL_EXCLUDES = {"_backup", "_backups", "_scripts", "scripts", "auto",
                           "daily", "SKIP_audit", "_state_backups"}

# 旧树里仍在写入的共享目录前缀
LEGACY_SHARED_PREFIXES = ("304-公司运营/", "303-竞品库/", "团队协作/")


def iter_new_files(root, cutoff):
    """yield (rel, mtime, size) for files modified within the window."""
    if not root.exists():
        return
    for path in root.rglob("*"):
        try:
            if not path.is_file():
                continue
            st = path.stat()
            mtime = datetime.fromtimestamp(st.st_mtime)
        except OSError:
            continue
        if mtime < cutoff:
            continue
        yield str(path.relative_to(root)), mtime, st.st_size


def match_agent(rel):
    for agent, dirs in AGENT_DIRS.items():
        for d in dirs:
            if rel == d or rel.startswith(d + "/"):
                return agent
    return None


def excluded(rel):
    parts = rel.split("/")
    if parts[-1] in EXCLUDED_NAMES:
        return True
    if parts[0] in TOP_EXCLUDES:
        return True
    if len(parts) > 2:
        first = parts[0]
        for dirs in AGENT_DIRS.values():
            if first in dirs:
                if parts[1] in AGENT_INTERNAL_EXCLUDES:
                    return True
                break
    return False


def scan():
    cutoff = datetime.now() - timedelta(days=WINDOW_DAYS)
    agent_files = {a: [] for a in AGENT_DIRS}
    shared = []
    for rel, mtime, size in iter_new_files(ROOT, cutoff):
        if excluded(rel):
            continue
        agent = match_agent(rel)
        if agent:
            agent_files[agent].append((rel, mtime, size))
        else:
            shared.append((rel, mtime, size))
    for rel, mtime, size in iter_new_files(LEGACY_ROOT, cutoff):
        if parts_ok(rel):
            shared.append((rel, mtime, size))
    return agent_files, shared


def parts_ok(rel):
    if rel.endswith(".DS_Store"):
        return False
    return rel.startswith(LEGACY_SHARED_PREFIXES)


def render(agent_files, shared):
    now = datetime.now()
    n_agent = sum(len(v) for v in agent_files.values())
    n_shared = len(shared)
    total = n_agent + n_shared
    lines = []
    lines.append("# 渔芯工作空间审计报告 (过去 %d 天)" % WINDOW_DAYS)
    lines.append("")
    lines.append("📅 审计时间: %s" % now.strftime("%Y-%m-%d %H:%M"))
    lines.append("📂 审计范围: 部门空间(ABCZ 新树) + 旧树共享区(3-公司项目资料)")
    lines.append("🚫 排除: 备份/脚本/auto/daily/学习笔记/.DS_Store")
    lines.append("")
    lines.append("## 📊 总览")
    lines.append("")
    lines.append("- 同事 agent 个人目录新增/修改: **%d 个文件**" % n_agent)
    lines.append("- 共享工作区新增/修改: **%d 个文件**" % n_shared)
    lines.append("- **合计: %d 个文件**" % total)
    lines.append("")
    lines.append("## 👥 各 agent 工作量")
    lines.append("")
    for agent in agent_files:
        files = agent_files[agent]
        lines.append("### %s(%d 个文件)" % (agent, len(files)))
        if not files:
            lines.append("- 过去 7 天无新增/修改")
            lines.append("")
            continue
        total_size = sum(s for _, _, s in files)
        lines.append("- 总大小: %.1f KB" % (total_size / 1024))
        for rel, mtime, size in sorted(files, key=lambda x: -x[1].timestamp())[:10]:
            lines.append("- `%s` (%s, %dB)" % (rel, mtime.strftime("%Y-%m-%d %H:%M"), size))
        lines.append("")
    lines.append("## 🌐 共享工作区")
    lines.append("")
    if not shared:
        lines.append("- 过去 7 天无新增/修改")
    else:
        lines.append("**%d 个文件**:" % len(shared))
        lines.append("")
        for rel, mtime, size in sorted(shared, key=lambda x: -x[1].timestamp())[:20]:
            lines.append("- `%s` (%s, %dB)" % (rel, mtime.strftime("%Y-%m-%d %H:%M"), size))
    return "\n".join(lines), total


def main():
    agent_files, shared = scan()
    report, total = render(agent_files, shared)
    if total == 0:
        sys.exit(0)
    print(report)
    out_dir = Path("/Users/hua/.hermes/state")
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "workspace_audit_latest.md").write_text(report, encoding="utf-8")
    sys.stderr.write("报告已保存: /Users/hua/.hermes/state/workspace_audit_latest.md\n")


if __name__ == "__main__":
    main()
