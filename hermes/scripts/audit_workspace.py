#!/usr/bin/env python3
"""
工作空间审计:扫描 ~/rkr_staging/文档库/3-公司项目资料/ 下过去 7 天新增/修改的文件。
按 agent 分组,生成 markdown 报告。
"""
import os
import sys
from pathlib import Path
from datetime import datetime, timedelta

ROOT = Path("/Users/hua/rkr_staging/文档库/3-公司项目资料")
WINDOW_DAYS = 7
THRESHOLD = datetime.now() - timedelta(days=WINDOW_DAYS)

# 同事 agent 目录
AGENT_DIRS = {
    "毛豆": "301-智能体/毛豆-产品交付",
    "小宝": "301-智能体/小宝-商务运营",
    "老莫": "301-智能体/老莫-技术运维",
    "阿福": "301-智能体/阿福-客服",
    "黑豆": "301-智能体/黑豆-行政财务法务",
}

# 不审计的子路径(前缀匹配)
EXCLUDE_PREFIXES = [
    "302-数据与素材库/",
    "antigravity-awesome-skills/",
    "awesome-claude-code/",
    "awesome-agent-skills/",
    "everything-claude-code/",
    "cad_samples/",
    "material_library/",
    "mech_drawing/",
    "mech_drawing_reverse/",
    "freecad-automation/",  # 老莫的,不算同事新写
    "career-ops/",
    "pipeline/",
    "research/",
    "skills/",
    "video_understanding/",
    "voiceprint_samples/",
    "web_search/",
    "EDAI自动审批测试/",  # 阿福测试,不是新写
]

def is_excluded(rel_path: str) -> bool:
    return any(rel_path.startswith(prefix) for prefix in EXCLUDE_PREFIXES)

# 扫描
agent_files = {agent: [] for agent in AGENT_DIRS}
shared_files = []  # 303-竞品库/ 304-公司运营/ 团队协作/

for path in ROOT.rglob("*"):
    if not path.is_file():
        continue
    rel = str(path.relative_to(ROOT))
    if is_excluded(rel):
        continue
    try:
        mtime = datetime.fromtimestamp(path.stat().st_mtime)
    except Exception:
        continue
    if mtime < THRESHOLD:
        continue
    # 找属于哪个 agent
    matched = False
    for agent, agent_dir in AGENT_DIRS.items():
        if rel.startswith(agent_dir + "/") or rel == agent_dir:
            agent_files[agent].append((rel, mtime, path.stat().st_size, path.suffix.lower()))
            matched = True
            break
    if not matched:
        shared_files.append((rel, mtime, path.stat().st_size, path.suffix.lower()))

# 生成报告
report = []
report.append(f"# 渔芯工作空间审计报告 (过去 {WINDOW_DAYS} 天)")
report.append(f"\n📅 审计时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
report.append(f"📂 审计范围: ~/rkr_staging/文档库/3-公司项目资料/")
report.append(f"🚫 排除: RKR 资源(awesome-*/cad_samples/material_library/mech_drawing 等)、EDAI 测试、个人脚本目录")

# 汇总
total_files = sum(len(v) for v in agent_files.values()) + len(shared_files)
report.append(f"\n## 📊 总览\n")
report.append(f"- 同事 agent 个人目录新增/修改: **{sum(len(v) for v in agent_files.values())} 个文件**")
report.append(f"- 共享工作区(303-竞品库/304-公司运营/团队协作)新增/修改: **{len(shared_files)} 个文件**")
report.append(f"- **合计: {total_files} 个文件**\n")

# 每个 agent
report.append("## 👥 各 agent 工作量\n")
for agent, files in agent_files.items():
    report.append(f"### {agent}({len(files)} 个文件)")
    if not files:
        report.append("- 过去 7 天无新增/修改\n")
        continue
    # 按文件类型统计
    by_ext = {}
    total_size = 0
    for rel, mtime, size, ext in files:
        by_ext[ext] = by_ext.get(ext, 0) + 1
        total_size += size
    report.append(f"- 总大小: {total_size / 1024:.1f} KB")
    report.append(f"- 文件类型: {', '.join(f'{k}({v})' for k, v in sorted(by_ext.items(), key=lambda x: -x[1]))}")
    # 列出前 10 个
    report.append(f"\n**前 10 个文件**(按修改时间):")
    for rel, mtime, size, ext in sorted(files, key=lambda x: -x[1].timestamp())[:10]:
        report.append(f"- `{rel}` ({mtime.strftime('%Y-%m-%d %H:%M')}, {size}B)")
    report.append("")

# 共享工作区
report.append("## 🌐 共享工作区(303-竞品库/304-公司运营/团队协作)\n")
if not shared_files:
    report.append("- 过去 7 天无新增/修改\n")
else:
    report.append(f"**{len(shared_files)} 个文件**:\n")
    for rel, mtime, size, ext in sorted(shared_files, key=lambda x: -x[1].timestamp())[:20]:
        report.append(f"- `{rel}` ({mtime.strftime('%Y-%m-%d %H:%M')}, {size}B)")

# 输出
# no_agent=True 模式:仅在有变更时输出报告,否则静默
if total_files == 0:
    # 静默,什么都不打印
    sys.exit(0)

print("\n".join(report))

# 也写入 ~/.hermes/state/workspace_audit_latest.md
out_dir = Path("/Users/hua/.hermes/state")
out_dir.mkdir(parents=True, exist_ok=True)
(out_dir / "workspace_audit_latest.md").write_text("\n".join(report), encoding="utf-8")

# 输出文件路径
sys.stderr.write(f"\n报告已保存: {out_dir / 'workspace_audit_latest.md'}\n")
