#!/usr/bin/env python3
"""zhenglishi 565 误写文件归档脚本 · 2026-08-04

把 ~/.hermes/profiles/zhenglishi/home/Desktop/渔芯科技/ 下的误写文件
迁移到真实中转站 ~/rkr_staging/文档中转站/。

按子目录对应 staging_save.py 的 AGENT_SUBDIRS:
  团队协作/文档中转站/ → 01-调研资料/(source=research, 因为这些是调研类)
  其他(10-爬虫研究/ 等) → 保留原分类,加 zhenglishi 标签

策略:
  1. cp 复制(不删) — 留备份
  2. 写 .meta.json(便于 RKR scanner 后续分类)
  3. 写入归档日志
  4. 迁移完报数给玉芬
"""
import json
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path

# 绝对路径
SOURCE_BASE = Path("/Users/hua/.hermes/profiles/zhenglishi/home/Desktop/渔芯科技")
TARGET_BASE = Path("/Users/hua/rkr_staging/文档中转站")
BACKUP_BASE = Path("/Users/hua/.hermes/profiles/zhenglishi/.***SECRET***")
LOG_FILE = Path("/Users/hua/.hermes/cron/output/zhenglishi_migration.log")


def classify(subdir_name: str) -> tuple[str, str]:
    """根据子目录名,返回 (target_subdir, source_tag)

    团队协作/文档中转站/ → 调研资料(原意图是 RKR 入站)
    其他子目录 → 保留为分类,加 zhenglishi 标签
    """
    if "团队协作" in subdir_name or "文档中转站" in subdir_name:
        return ("01-调研资料", "research")
    return ("01-调研资料", "research")  # 全按 research,因为都是学习助手 cron 调研产物


def write_meta(target_path: Path, original_path: Path, source: str) -> None:
    """写 .meta.json 便于 scanner 处理"""
    meta = {
        "title": target_path.stem,
        "source": source,
        "agent": "zhenglishi",
        "tags": ["zhenglishi", "path-fix-2026-08-04", "migrated"],
        "original_path": str(original_path),
        "migrated_at": datetime.now().isoformat(),
        "fix_reason": "zhenglishi profile $HOME 劫持导致 staging_save 误写",
    }
    meta_path = target_path.with_suffix(target_path.suffix + ".meta.json")
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)


def main():
    if not SOURCE_BASE.exists():
        print(f"❌ 源目录不存在: {SOURCE_BASE}")
        sys.exit(1)

    # 备份原目录(只备份,不删)
    if not BACKUP_BASE.exists():
        shutil.copytree(SOURCE_BASE, BACKUP_BASE, dirs_exist_ok=True)
        print(f"✅ 备份到: {BACKUP_BASE}")
    else:
        print(f"⚠️  备份已存在,跳过: {BACKUP_BASE}")

    # 收集所有 .md
    md_files = list(SOURCE_BASE.rglob("*.md"))
    print(f"📁 找到 {len(md_files)} 个 .md 文件")

    # 统计 + 分类
    target_subdir, source_tag = classify("")  # 全 research
    target_dir = TARGET_BASE / target_subdir
    target_dir.mkdir(parents=True, exist_ok=True)

    # 迁移
    log_lines = []
    log_lines.append(f"=== 归档开始 {datetime.now().isoformat()} ===")
    log_lines.append(f"源: {SOURCE_BASE}")
    log_lines.append(f"目标: {target_dir}")
    log_lines.append(f"备份: {BACKUP_BASE}")
    log_lines.append("")

    success = 0
    failed = 0
    for src in md_files:
        # 用 unique 文件名(原相对路径 → 文件名)
        rel = src.relative_to(SOURCE_BASE)
        # 改 / 为 __ 避免破坏目录结构
        new_name = str(rel).replace("/", "__").replace(" ", "_")
        target_path = target_dir / new_name
        try:
            shutil.copy2(src, target_path)
            write_meta(target_path, src, source_tag)
            success += 1
        except Exception as e:
            log_lines.append(f"❌ {src} → {e}")
            failed += 1

    log_lines.append("")
    log_lines.append(f"=== 归档完成 ===")
    log_lines.append(f"成功: {success}")
    log_lines.append(f"失败: {failed}")
    log_lines.append(f"源: {SOURCE_BASE} ({sum(f.stat().st_size for f in md_files) / 1024 / 1024:.1f} MB)")

    # 写日志
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write("\n".join(log_lines) + "\n")

    # 打印
    print()
    print("\n".join(log_lines))
    print()
    print(f"📋 日志: {LOG_FILE}")
    print(f"📦 备份: {BACKUP_BASE}(仍保留,确认无问题后可手动删)")


if __name__ == "__main__":
    main()
