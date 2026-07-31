#!/usr/bin/env python3
"""
migrate_agent_artifacts.py — 渔芯 Agent 历史资料批量迁移到 RKR 中转站
========================================================================
将"其他 agent 以前生成的资料"批量复制到 `~/rkr_staging/文档中转站/`，由
RKR scanner 自动处理（向量化 + 知识图谱 + 入库到 `~/rkr_staging/文档库/`）。

**特点**：
- **复制而非移动**（保留原文件不动）
- 排除：寻元项目、macOS 系统目录、代码/数据库/模型文件
- 写入中转站时加 frontmatter（来源、agent、原路径）
- 写 `~/.hermes/logs/migration_*.log` 记录

**用法**：
    # Dry run (只统计，不复制)
    python3 ~/.hermes/scripts/migrate_agent_artifacts.py --dry-run

    # 实际迁移
    python3 ~/.hermes/scripts/migrate_agent_artifacts.py --execute

    # 限制来源（只迁某个目录）
    python3 ~/.hermes/scripts/migrate_agent_artifacts.py --execute \\
        --only desktop       # 只迁 ~/Desktop/渔芯科技/
    python3 ~/.hermes/scripts/migrate_agent_artifacts.py --execute \\
        --only profiles     # 只迁 agent profiles
"""

import argparse
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path

# ── 配置 ──────────────────────────────────────────────────
STAGING_BASE = Path(os.path.expanduser("~/rkr_staging/文档中转站"))
HOME = Path(os.path.expanduser("~"))
LOG_DIR = Path(os.path.expanduser("~/.hermes/logs"))
STATE_DIR = Path(os.path.expanduser("~/.hermes/state"))
MANIFEST_FILE = STATE_DIR / "migration_manifest.json"

# 同事 agent profiles（不含 findera/寻元 + 不含 default）
AGENT_PROFILES = ["afu", "heidou", "laomo", "maodou", "quant", "xiaobao", "zhenglishi"]

# 桌面渔芯科技目录
DESKTOP_YUXIN = HOME / "Desktop" / "渔芯科技"

# 排除路径（路径片段匹配即排除）
EXCLUDE_PATH_PARTS = {
    "Library",  # macOS 系统目录
    "node_modules",
    ".cache",
    "__pycache__",
    ".git",
    "dist",
    "build",
    "venv",
    ".venv",
    "site-packages",  # Python 包数据
    "00-FindEra寻元",  # 寻元项目 — 不动
    "FindEra寻元",
    ".tmp",
    ".DS_Store",
    # Watchdog / 状态跟踪文件（mtime 持续变，不是资料）
    ".kb_watchdog_tracker.json",
    ".watchdog_state.json",
}

# 排除扩展名
EXCLUDE_EXT = {
    ".py", ".js", ".ts", ".jsx", ".tsx", ".html", ".css", ".scss", ".vue",
    ".db", ".sqlite", ".sqlite3",
    ".bin", ".pt", ".gguf", ".pkl", ".onnx", ".h5", ".safetensors",
    ".zip", ".tar", ".tar.gz", ".tgz", ".7z", ".rar",
    ".exe", ".dll", ".so", ".dylib",
    ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp", ".ico", ".svg",
    ".mp3", ".mp4", ".mov", ".avi", ".wav",
    ".DS_Store",
}

# 包含扩展名（资料类）
INCLUDE_EXT = {
    ".md", ".markdown",
    ".txt",
    ".pdf",
    ".docx", ".doc",
    ".json",   # 元数据（如 batch_upload_v2 配置等）
    ".yaml", ".yml",
    ".csv",
    ".html",   # 部分 html 是报告/笔记
}

# 单文件大小限制（50MB）
MAX_FILE_SIZE = 50 * 1024 * 1024


def is_excluded(path: Path) -> bool:
    """检查路径是否被排除。"""
    parts = set(path.parts)
    if parts & EXCLUDE_PATH_PARTS:
        return True
    if path.suffix.lower() in EXCLUDE_EXT:
        return True
    return False


# ════════════════════════════════════════════════════════════════
# 增量迁移 — manifest 跟踪
# ════════════════════════════════════════════════════════════════

def load_manifest() -> dict:
    """加载 manifest：{相对路径: {mtime, size, migrated_at, agent}}"""
    if MANIFEST_FILE.exists():
        try:
            import json
            return json.loads(MANIFEST_FILE.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def save_manifest(manifest: dict) -> None:
    """保存 manifest。"""
    import json
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    MANIFEST_FILE.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def filter_incremental(files: list, manifest: dict) -> tuple:
    """
    增量过滤：只保留 (新增 or 修改过) 的文件。
    返回 (to_migrate, skipped_count)。
    """
    to_migrate = []
    skipped = 0
    for f in files:
        # 用绝对路径作 key
        key = str(f)
        try:
            stat = f.stat()
            mtime = stat.st_mtime
            size = stat.st_size
        except OSError:
            continue

        prev = manifest.get(key)
        if prev and prev.get("mtime") == mtime and prev.get("size") == size:
            skipped += 1
            continue
        to_migrate.append(f)
    return to_migrate, skipped


def collect_source_files(source_type: str) -> list:
    """
    收集要迁移的源文件。

    source_type: "desktop" | "profiles" | "all"
    """
    files = []

    if source_type in ("desktop", "all"):
        # 桌面 ~/Desktop/渔芯科技/ 全部子目录
        if DESKTOP_YUXIN.exists():
            for p in DESKTOP_YUXIN.rglob("*"):
                if not p.is_file():
                    continue
                if is_excluded(p):
                    continue
                if p.suffix.lower() not in INCLUDE_EXT:
                    continue
                if p.stat().st_size > MAX_FILE_SIZE:
                    continue
                files.append(p)
        else:
            print(f"⚠️  Desktop 渔芯科技目录不存在: {DESKTOP_YUXIN}", file=sys.stderr)

        # 桌面 ~/Desktop/ 顶层其他散落 .md/.pdf
        for p in HOME.glob("Desktop/*"):
            if not p.is_file():
                continue
            if p.suffix.lower() not in INCLUDE_EXT:
                continue
            if is_excluded(p):
                continue
            if p.stat().st_size > MAX_FILE_SIZE:
                continue
            files.append(p)

    if source_type in ("profiles", "all"):
        # 7 个 agent profile
        for agent in AGENT_PROFILES:
            profile_home = HOME / ".hermes" / "profiles" / agent / "home"
            if not profile_home.exists():
                continue
            for p in profile_home.rglob("*"):
                if not p.is_file():
                    continue
                if is_excluded(p):
                    continue
                if p.suffix.lower() not in INCLUDE_EXT:
                    continue
                if p.stat().st_size > MAX_FILE_SIZE:
                    continue
                files.append(p)

    # 去重（不全局 sort — 保留 desktop→profiles 顺序，让 --limit 截断有可预测性）
    return list(dict.fromkeys(files))


def build_destination(source_path: Path, batch_dir: Path) -> Path:
    """
    构建目标路径。结构：
    ~/rkr_staging/文档中转站/migration_<日期>/<来源>/<相对路径>

    source_path 来源：
    - ~/Desktop/渔芯科技/...   → migration/<date>/desktop_yuxin/<相对>
    - ~/Desktop/foo.md          → migration/<date>/desktop_root/foo.md
    - ~/.hermes/profiles/<a>/home/... → migration/<date>/profile_<a>/...
    """
    # Desktop 渔芯科技
    if str(source_path).startswith(str(DESKTOP_YUXIN)):
        rel = source_path.relative_to(DESKTOP_YUXIN)
        return batch_dir / "desktop_yuxin" / rel
    # Desktop 顶层
    if str(source_path).startswith(str(HOME / "Desktop")):
        rel = source_path.relative_to(HOME / "Desktop")
        return batch_dir / "desktop_root" / rel
    # Agent profile
    for agent in AGENT_PROFILES:
        profile_home = HOME / ".hermes" / "profiles" / agent / "home"
        if str(source_path).startswith(str(profile_home)):
            rel = source_path.relative_to(profile_home)
            return batch_dir / f"profile_{agent}" / rel
    # 兜底
    return batch_dir / "other" / source_path.name


def write_with_frontmatter(source: Path, dest: Path, agent_label: str = "") -> None:
    """
    复制文件到 dest，加 frontmatter（仅 .md 文件），写 .meta.json。
    """
    # 创建目标目录
    dest.parent.mkdir(parents=True, exist_ok=True)

    # 处理 .md 文件：加 frontmatter
    if source.suffix.lower() in (".md", ".markdown"):
        try:
            content = source.read_text(encoding="utf-8", errors="ignore")
            ts = datetime.now().isoformat(timespec="seconds")
            front = [
                f"<!-- migration_meta",
                f"     source_path: {source}",
                f"     migrated_at: {ts}",
                f"     agent: {agent_label or 'unknown'}",
                f"     original_size: {source.stat().st_size}",
                "     migration_meta -->",
                "",
            ]
            # 避免重复加 frontmatter
            if not content.startswith("<!-- migration_meta"):
                content = "\n".join(front) + content
            dest.write_text(content, encoding="utf-8")
        except Exception as e:
            print(f"   ⚠️  写 .md 失败: {source} → {e}", file=sys.stderr)
            shutil.copy2(source, dest)
    else:
        # 其他文件：直接复制
        shutil.copy2(source, dest)

    # 写 .meta.json（不阻塞，错误忽略）
    try:
        import json
        meta = {
            "source_path": str(source),
            "source_size": source.stat().st_size,
            "migrated_at": datetime.now().isoformat(timespec="seconds"),
            "agent": agent_label,
            "extension": source.suffix.lower(),
        }
        (dest.parent / f"{dest.name}.meta.json").write_text(
            json.dumps(meta, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    except Exception:
        pass


def main():
    p = argparse.ArgumentParser(
        description="渔芯 Agent 历史资料批量迁移到 RKR 中转站",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    p.add_argument("--dry-run", action="store_true", help="只统计，不复制")
    p.add_argument("--execute", action="store_true", help="实际执行迁移")
    p.add_argument(
        "--only", choices=["desktop", "profiles", "all"], default="all",
        help="限制迁移来源（默认: all）",
    )
    p.add_argument(
        "--batch-name", default=None,
        help="批次目录名（默认: migration_YYYYMMDD）",
    )
    p.add_argument(
        "--limit", type=int, default=None,
        help="限制文件数（测试用）",
    )
    p.add_argument(
        "--incremental", action="store_true",
        help="增量模式：只迁移新增/修改过的文件（用 manifest 跟踪）",
    )
    args = p.parse_args()

    if not args.dry_run and not args.execute:
        p.error("需要 --dry-run 或 --execute")

    # 批次目录
    batch_name = args.batch_name or f"migration_{datetime.now().strftime('%Y%m%d')}"
    batch_dir = STAGING_BASE / batch_name

    print(f"🔍 扫描来源: {args.only}")
    print(f"📦 批次目录: {batch_dir}")
    print()

    files = collect_source_files(args.only)
    if args.limit:
        files = files[: args.limit]

    # 增量过滤
    if args.incremental:
        manifest = load_manifest()
        files, skipped = filter_incremental(files, manifest)
        print(f"🔄 增量模式: 跳过 {skipped} 个未变更文件，待迁移 {len(files)} 个")
        print()

    # 统计
    total_size = sum(f.stat().st_size for f in files)
    by_ext = {}
    by_agent = {}
    for f in files:
        ext = f.suffix.lower() or "(no ext)"
        by_ext[ext] = by_ext.get(ext, 0) + 1
        for agent in AGENT_PROFILES:
            if f"/.hermes/profiles/{agent}/" in str(f):
                by_agent[agent] = by_agent.get(agent, 0) + 1
                break
        else:
            by_agent["desktop"] = by_agent.get("desktop", 0) + 1

    print(f"📊 扫描结果:")
    print(f"   文件数: {len(files)}")
    print(f"   总大小: {total_size / 1024 / 1024:.1f} MB")
    print()
    print("   按扩展名:")
    for ext, n in sorted(by_ext.items(), key=lambda x: -x[1])[:10]:
        print(f"     {ext:10s}: {n}")
    print()
    print("   按来源:")
    for src, n in sorted(by_agent.items(), key=lambda x: -x[1]):
        print(f"     {src:15s}: {n}")
    print()

    if args.dry_run:
        print("🔍 Dry run 完成，未执行复制")
        return

    if not files:
        print("✅ 无文件需要迁移（增量模式：所有文件已同步）")
        return

    # 实际执行
    print(f"🚀 开始迁移 {len(files)} 个文件到 {batch_dir}")
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    log_file = LOG_DIR / f"migration_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    log_lines = []

    # 加载 manifest（如果是 incremental 模式）
    manifest = load_manifest() if args.incremental else {}

    copied = 0
    errors = 0
    for i, src in enumerate(files, 1):
        try:
            dest = build_destination(src, batch_dir)
            # 判断 agent 标签
            agent_label = "unknown"
            for a in AGENT_PROFILES:
                if f"/.hermes/profiles/{a}/" in str(src):
                    agent_label = a
                    break
            else:
                if str(src).startswith(str(DESKTOP_YUXIN)):
                    agent_label = "desktop_yuxin"
                elif str(src).startswith(str(HOME / "Desktop")):
                    agent_label = "desktop_root"
            write_with_frontmatter(src, dest, agent_label=agent_label)
            copied += 1

            # 更新 manifest（增量模式）
            if args.incremental:
                st = src.stat()
                manifest[str(src)] = {
                    "mtime": st.st_mtime,
                    "size": st.st_size,
                    "migrated_at": datetime.now().isoformat(timespec="seconds"),
                    "agent": agent_label,
                }

            if i % 100 == 0:
                print(f"   {i}/{len(files)} ({copied} ok, {errors} fail)")
        except Exception as e:
            errors += 1
            log_lines.append(f"FAIL: {src} → {e}")

    # 保存 manifest
    if args.incremental:
        save_manifest(manifest)
        print(f"📝 manifest 已更新: {MANIFEST_FILE} ({len(manifest)} 条记录)")

    # 写日志
    log_file.write_text("\n".join(log_lines), encoding="utf-8")

    print()
    print(f"✅ 迁移完成: {copied} ok, {errors} fail")
    print(f"📁 目标: {batch_dir}")
    print(f"📝 日志: {log_file}")
    print()
    print("⏰ RKR scanner 将在 60 秒内自动处理（中转站 → 文档库）")
    print(f"   监控: docker logs rkr-staging-pool --tail 50 --follow")


if __name__ == "__main__":
    main()
