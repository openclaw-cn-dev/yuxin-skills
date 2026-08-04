#!/usr/bin/env python3
"""
staging_save.py — 渔芯 Agent 统一资料入站工具
=================================================
所有 agent 调研 / 生成的资料，**统一保存到 RKR 中转站**：
    ~/rkr_staging/文档中转站/

RKR 知识库（`local_staging_scanner.py`）每 60 秒扫描一次中转站：
- 新文件 → 复制到 `~/rkr_staging/文档库/<分类>/`
- 触发 process_shared_document → 向量化 + 知识图谱
- 处理完成后自动删除中转站原始文件

**调用时统一从 RKR API 读**（见 `staging_query.py` / `query_knowledge.py`）：
    GET /api/v1/library/knowledge?search=...
    GET /api/v1/projects/{id}/documents

用法：
    # 直接命令行
    python3 ~/.hermes/scripts/staging_save.py \
        --title "养殖池设计调研" \
        --content @file.md \
        --source "research" \
        --tag 养殖池 循环水

    # Python API
    from staging_save import stage
    stage(title="...", content="...", source="research", tags=[...])
"""

import argparse
import os
import sys
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional

# ── 全局常量 ──────────────────────────────────────────────
# 修复(2026-08-04):改用绝对路径,防止 Hermes profile 启动时 $HOME 被劫持
# 而写错位置。原代码:
#   STAGING_DIR = Path(os.path.expanduser("~/rkr_staging/文档中转站"))
# 问题:zhenglishi 等 profile 启动时 $HOME=~/.hermes/profiles/zhenglishi/home/,
# 导致 `~` 展开为 profile 镜像 home,写到了错地方。
# 现在用绝对路径,profile 无关,所有 agent 都写到真中转站。
STAGING_DIR = Path("/Users/hua/rkr_staging/文档中转站")
KNOWLEDGE_LIB = Path("/Users/hua/rkr_staging/文档库")

# $HOME 防御性检查 — 如果启动时 $HOME 不是 /Users/hua,警告(但仍用绝对路径)
_HOME = os.environ.get("HOME", "")
if _HOME != "/Users/hua":
    # 不阻断(可能 cron 进程 $HOME 是其他路径),只打印警告到 stderr
    print(
        f"⚠️ [staging_save] $HOME={_HOME!r} (非 /Users/hua),"
        f"已强制使用绝对路径 {STAGING_DIR},请确认环境正确。",
        file=sys.stderr,
    )

# 中转站子分类（按 agent 来源划分）
AGENT_SUBDIRS = {
    "research":   "01-调研资料",
    "generated":  "02-生成内容",
    "report":     "03-调研报告",
    "raw":        "04-原始资料",
    "yuxin":      "05-玉芬整理",
    "findera":    "06-寻元采集",
    "default":    "00-未分类",
}


def stage(
    title: str,
    content: str,
    source: str = "research",
    agent: Optional[str] = None,
    tags: Optional[list] = None,
    subdir: Optional[str] = None,
    meta: Optional[dict] = None,
) -> Path:
    """
    保存资料到 RKR 中转站。
    RKR scanner 会自动处理（复制到文档库 → 向量化 → 删原文件）。

    Args:
        title:    资料标题（必填）
        content:  Markdown 内容（必填）
        source:   来源类型：research/generated/report/raw/yuxin/findera
        agent:    哪个 agent 写入（默认从 $HERMES_AGENT 读）
        tags:     标签列表（写入 .meta.json 便于后续分类）
        subdir:   自定义子目录（覆盖 source 默认）
        meta:     额外元数据（写入 .meta.json）

    Returns:
        写入的文件路径
    """
    # 自动识别 agent
    if not agent:
        agent = os.environ.get("HERMES_AGENT", "default")

    # 子目录
    target_subdir = subdir or AGENT_SUBDIRS.get(source, AGENT_SUBDIRS["default"])
    target_dir = STAGING_DIR / target_subdir
    target_dir.mkdir(parents=True, exist_ok=True)

    # 文件名：<日期>_<uuid短>_<标题>.md（标题清理特殊字符）
    safe_title = "".join(
        c if c.isalnum() or c in "-_—，。" else "_"
        for c in title[:50]
    ).strip("_")
    if not safe_title:
        safe_title = "untitled"

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    short_uuid = uuid.uuid4().hex[:8]
    filename = f"{ts}_{short_uuid}_{safe_title}.md"
    file_path = target_dir / filename

    # 写文件
    frontmatter_lines = [
        f"# {title}",
        "",
        f"> 🤖 入站时间: {datetime.now().isoformat(timespec='seconds')}",
        f"> 📦 来源: {source}",
        f"> 🤝 Agent: {agent}",
    ]
    if tags:
        frontmatter_lines.append(f"> 🏷️  标签: {', '.join(tags)}")

    if meta:
        for k, v in meta.items():
            frontmatter_lines.append(f"> 📎 {k}: {v}")

    frontmatter_lines.extend(["", "---", ""])
    full_content = "\n".join(frontmatter_lines) + content

    file_path.write_text(full_content, encoding="utf-8")

    # 写 .meta.json（RKR scanner 识别的元数据）
    meta_data = {
        "title": title,
        "source": source,
        "agent": agent,
        "tags": tags or [],
        "filename": filename,
        "submitted_at": datetime.now().isoformat(timespec="seconds"),
        "staging_subdir": target_subdir,
        "expected_processing": "RKR scanner → 文档库 + 向量化",
    }
    if meta:
        meta_data["extra"] = meta
    (target_dir / f"{file_path.name}.meta.json").write_text(
        __import__("json").dumps(meta_data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(f"✅ 已入站: {file_path}")
    print(f"   Agent: {agent} | Source: {source}")
    print(f"   RKR scanner 将于 60 秒内处理（监控: tail -f ~/rkr_staging/logs/staging_scanner.log）")
    return file_path


def main():
    p = argparse.ArgumentParser(
        description="渔芯 Agent 统一资料入站工具（保存到 RKR 中转站）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    p.add_argument("--title", required=True, help="资料标题")
    p.add_argument("--content", help="Markdown 内容（@file.md 从文件读）")
    p.add_argument("--source", default="research",
                   choices=list(AGENT_SUBDIRS.keys()),
                   help="来源类型（默认: research）")
    p.add_argument("--agent", help="Agent 名字（默认从 $HERMES_AGENT 读）")
    p.add_argument("--tag", action="append", dest="tags", help="标签（可多次）")
    p.add_argument("--subdir", help="自定义子目录")
    p.add_argument("--meta", help="额外元数据（key=value 形式，可多次）")
    args = p.parse_args()

    if not args.content:
        p.error("需要 --content")
    if args.content.startswith("@"):
        content = Path(args.content[1:]).read_text(encoding="utf-8")
    else:
        content = args.content

    meta = {}
    if args.meta:
        for m in args.meta:
            if "=" in m:
                k, v = m.split("=", 1)
                meta[k] = v

    stage(
        title=args.title,
        content=content,
        source=args.source,
        agent=args.agent,
        tags=args.tags,
        subdir=args.subdir,
        meta=meta or None,
    )


if __name__ == "__main__":
    main()
