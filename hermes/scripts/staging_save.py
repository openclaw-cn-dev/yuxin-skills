#!/usr/bin/env python3
"""
staging_save.py - RKR 中转站写入工具
将研究笔记保存到 staging 区,等待 scanner 自动归类到目标知识库。
"""
import argparse
import os
import sys
import subprocess
from pathlib import Path
from datetime import datetime

def main():
    parser = argparse.ArgumentParser(description="RKR staging 中转站写入")
    parser.add_argument("--title", required=True, help="文档标题")
    parser.add_argument("--content", help="内容(@file 读取文件, 或直接字符串)")
    parser.add_argument("--source", default="research", help="来源标签")
    parser.add_argument("--agent", default="zhenglishi", help="执行 agent")
    parser.add_argument("--target", default="1-通用知识", help="目标分类")
    args = parser.parse_args()

    # 解析 content
    content = ""
    if args.content:
        if args.content.startswith("@"):
            file_path = args.content[1:]
            p = Path(file_path).expanduser()
            if not p.exists():
                print(f"[ERROR] 内容文件不存在: {file_path}", file=sys.stderr)
                sys.exit(1)
            content = p.read_text(encoding="utf-8")
        else:
            content = args.content

    # staging 路径
    staging_dir = Path.home() / ".hermes" / "staging"
    staging_dir.mkdir(parents=True, exist_ok=True)

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_title = "".join(c if c.isalnum() or c in "-_" else "_" for c in args.title)[:80]
    out_file = staging_dir / f"{safe_title}_{ts}.md"

    # 写入元信息头
    header = f"""---
title: {args.title}
source: {args.source}
agent: {args.agent}
target: {args.target}
created: {datetime.now().isoformat()}
status: pending
---

"""
    out_file.write_text(header + content, encoding="utf-8")

    # 同时追加索引
    index_file = staging_dir / "INDEX.md"
    with index_file.open("a", encoding="utf-8") as f:
        f.write(f"\n- [{datetime.now().strftime('%Y-%m-%d %H:%M')}] {args.title} -> {out_file.name}\n")

    print(f"[OK] 已保存到 staging: {out_file}")
    print(f"[INFO] 等待 scanner 归类到 {args.target}/")

if __name__ == "__main__":
    main()
