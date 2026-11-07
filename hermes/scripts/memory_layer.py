#!/usr/bin/env python3
# TODO(tech-debt): 用 Claude Code 重写时改用 yaml 库代替手写

import argparse
import os
import sys
from datetime import datetime


MEMORY_ROOT = "/Users/hua/.hermes/memory_store"
SHARED_DIR = os.path.join(MEMORY_ROOT, "shared")
PUBLIC_DIR = os.path.join(MEMORY_ROOT, "public")
PROFILES_ROOT = "/Users/hua/.hermes/profiles"


def write_memory(args) -> None:
    today = datetime.now().strftime("%Y-%m-%d")

    if args.layer == "L0":
        fname = f"{today}_{args.title}.md"
        filepath = os.path.join(SHARED_DIR, fname)
        os.makedirs(SHARED_DIR, exist_ok=True)
        agent = args.agent or "unknown"
        content = f"""---
layer: L0
created: {today}
source: {agent}
---

# {args.title}

{args.content}
"""
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"✅ L0 写入: {filepath}")

    elif args.layer == "L1":
        category = args.category or "general"
        cat_dir = os.path.join(PUBLIC_DIR, category)
        os.makedirs(cat_dir, exist_ok=True)
        filepath = os.path.join(cat_dir, f"{args.title}.md")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"# {args.title}\n\n{args.content}\n")
        print(f"✅ L1 写入: {filepath}")

    elif args.layer == "L2":
        if not args.agent:
            print("❌ L2 需要 --agent", file=sys.stderr)
            sys.exit(1)
        mem_dir = os.path.join(PROFILES_ROOT, args.agent, "memories")
        os.makedirs(mem_dir, exist_ok=True)
        filepath = os.path.join(mem_dir, "MEMORY.md")
        entry = f"\n## {args.title} ({today})\n\n{args.content}\n"
        with open(filepath, "a", encoding="utf-8") as f:
            f.write(entry)
        print(f"✅ L2 追加: {filepath}")

    elif args.layer == "L3":
        if not args.agent:
            print("❌ L3 需要 --agent", file=sys.stderr)
            sys.exit(1)
        priv_dir = os.path.join(PROFILES_ROOT, args.agent, ".private")
        os.makedirs(priv_dir, exist_ok=True)
        filepath = os.path.join(priv_dir, f"{args.title}.md")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"# {args.title}\n\n{args.content}\n")
        print(f"✅ L3 写入: {filepath}")


def list_memory(args) -> None:
    layer = args.layer

    if layer == "L0":
        if os.path.isdir(SHARED_DIR):
            for fname in sorted(os.listdir(SHARED_DIR)):
                if fname.endswith(".md"):
                    print(f"  {fname}")
        else:
            print("  (目录不存在)")

    elif layer == "L1":
        if os.path.isdir(PUBLIC_DIR):
            for root, dirs, files in os.walk(PUBLIC_DIR):
                for fname in sorted(files):
                    if fname.endswith(".md"):
                        rel = os.path.relpath(os.path.join(root, fname), PUBLIC_DIR)
                        print(f"  {rel}")
        else:
            print("  (目录不存在)")

    elif layer == "L2":
        if not os.path.isdir(PROFILES_ROOT):
            print("  (目录不存在)")
            return
        for agent in sorted(os.listdir(PROFILES_ROOT)):
            mem_file = os.path.join(PROFILES_ROOT, agent, "memories", "MEMORY.md")
            if os.path.isfile(mem_file):
                print(f"  [{agent}] memories/MEMORY.md")

    elif layer == "L3":
        if not os.path.isdir(PROFILES_ROOT):
            print("  (目录不存在)")
            return
        for agent in sorted(os.listdir(PROFILES_ROOT)):
            priv_dir = os.path.join(PROFILES_ROOT, agent, ".private")
            if os.path.isdir(priv_dir):
                for fname in sorted(os.listdir(priv_dir)):
                    if fname.endswith(".md"):
                        print(f"  [{agent}] {fname}")


def read_memory(args) -> None:
    layer = args.layer
    rel_path = args.path

    base_map = {
        "L0": SHARED_DIR,
        "L1": PUBLIC_DIR,
        "L2": PROFILES_ROOT,
        "L3": PROFILES_ROOT,
    }
    base = base_map.get(layer)
    if base is None:
        print(f"❌ 不支持的 layer: {layer}", file=sys.stderr)
        sys.exit(1)

    filepath = os.path.join(base, rel_path)
    if not os.path.isfile(filepath):
        print(f"❌ 文件不存在: {filepath}", file=sys.stderr)
        sys.exit(1)

    with open(filepath, "r", encoding="utf-8") as f:
        print(f.read())


def main() -> None:
    parser = argparse.ArgumentParser(description="记忆分层管理")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # write
    p_write = subparsers.add_parser("write", help="写入记忆")
    p_write.add_argument("--layer", required=True, choices=["L0", "L1", "L2", "L3"], help="记忆层级")
    p_write.add_argument("--title", required=True, help="标题")
    p_write.add_argument("--content", required=True, help="正文")
    p_write.add_argument("--agent", default="", help="关联 Agent")
    p_write.add_argument("--category", default="", help="L1 分类目录")

    # list
    p_list = subparsers.add_parser("list", help="列出记忆")
    p_list.add_argument("--layer", required=True, choices=["L0", "L1", "L2", "L3"], help="记忆层级")

    # read
    p_read = subparsers.add_parser("read", help="读取记忆")
    p_read.add_argument("--layer", required=True, choices=["L0", "L1", "L2", "L3"], help="记忆层级")
    p_read.add_argument("--path", required=True, help="相对路径")

    args = parser.parse_args()

    if args.command == "write":
        write_memory(args)
    elif args.command == "list":
        list_memory(args)
    elif args.command == "read":
        read_memory(args)


if __name__ == "__main__":
    main()
