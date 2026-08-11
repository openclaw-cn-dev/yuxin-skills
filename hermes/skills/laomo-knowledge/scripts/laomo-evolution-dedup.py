#!/usr/bin/env python3
"""
laomo-evolution-dedup.py
老莫 cron evolution 阶段的 known_dois.txt 原子写入 + 报告自洽校验。

R15 (2026-08-10) 沉淀：消除 "Markdown 报告 vs known_dois.txt 实际状态" 漂移 bug。
R14 报告声称 "已加入 5 条 DOI"，但 grep 验证发现 known_dois.txt 实际未追加。
本脚本强制 "Write file FIRST, then report" 契约。

Usage:
    # 模式1: 添加新 DOI（原子合并去重）
    python3 scripts/laomo-evolution-dedup.py \\
        --new-dois-file /tmp/r15_new_dois.txt \\
        --known-dois-file /Users/hua/.hermes/profiles/laomo/evolution/known_dois.txt

    # 模式2: 校验报告与文件一致性
    python3 scripts/laomo-evolution-dedup.py \\
        --known-dois-file /Users/hua/.hermes/profiles/laomo/evolution/known_dois.txt \\
        --report-file /Users/hua/.hermes/profiles/laomo/evolution/2026-08-10_R15.md \\
        --verify

    # 模式3: 直接传 DOI 字符串（最少用，主要用于恢复场景）
    python3 scripts/laomo-evolution-dedup.py \\
        --known-dois-file /Users/hua/.hermes/profiles/laomo/evolution/known_dois.txt \\
        --add-doi 10.3390/fishes9100386 --add-doi 10.9734/acri/2024/v24i3650

退出码:
    0 - 成功
    1 - 报告与文件漂移（verify 模式发现 DRIFT）
    2 - 文件 IO 错误
"""

import argparse
import re
import sys
from pathlib import Path


DOI_PATTERN = re.compile(r"10\.[0-9]+/[a-zA-Z0-9._/-]+")


def extract_dois_from_text(text: str) -> set[str]:
    """从任意文本中提取 DOI 集合（容忍 markdown 表格/链接/纯文本）。"""
    return set(DOI_PATTERN.findall(text))


def normalize_doi(doi: str) -> str:
    """移除 DOI 前缀（如 'https://doi.org/'），统一格式。"""
    return doi.replace("https://doi.org/", "").replace("http://doi.org/", "").strip()


def load_known_dois(known_file: Path) -> set[str]:
    """读取已知 DOI 集合，容忍空行/注释/前缀。"""
    if not known_file.exists():
        return set()
    dois = set()
    for line in known_file.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        dois.add(normalize_doi(line))
    return {d for d in dois if DOI_PATTERN.fullmatch(d)}


def save_known_dois(known_file: Path, dois: set[str]) -> int:
    """原子写入：先写临时文件，再 rename 覆盖。返回写入数量。"""
    known_file.parent.mkdir(parents=True, exist_ok=True)
    tmp_file = known_file.with_suffix(known_file.suffix + ".tmp")
    # 排序后写入，便于 diff/wc
    content = "\n".join(sorted(dois)) + "\n"
    tmp_file.write_text(content)
    tmp_file.rename(known_file)
    return len(dois)


def cmd_add(args) -> int:
    """添加新 DOI 模式（默认）。"""
    known_file = Path(args.known_dois_file)
    existing = load_known_dois(known_file)
    initial_count = len(existing)

    new_dois: set[str] = set()
    if args.new_dois_file:
        new_file = Path(args.new_dois_file)
        if new_file.exists():
            for line in new_file.read_text().splitlines():
                line = line.strip()
                if line and DOI_PATTERN.fullmatch(normalize_doi(line)):
                    new_dois.add(normalize_doi(line))
        else:
            print(f"[WARN] new-dois-file not found: {new_file}", file=sys.stderr)
    if args.add_doi:
        for doi in args.add_doi:
            if DOI_PATTERN.fullmatch(normalize_doi(doi)):
                new_dois.add(normalize_doi(doi))

    # 找出真正新增的（去重）
    truly_new = new_dois - existing
    already_known = new_dois & existing

    if not new_dois:
        print(f"[INFO] no new DOIs to add. current known: {initial_count}")
        return 0

    print(f"[INPUT] {len(new_dois)} DOIs provided")
    print(f"  - truly new: {len(truly_new)}")
    if truly_new:
        for d in sorted(truly_new)[:10]:
            print(f"    + {d}")
        if len(truly_new) > 10:
            print(f"    ... +{len(truly_new) - 10} more")

    print(f"  - already in known_dois.txt: {len(already_known)}")
    if already_known:
        for d in sorted(already_known)[:5]:
            print(f"    = {d}")
        if len(already_known) > 5:
            print(f"    ... +{len(already_known) - 5} more")

    # 合并并写入
    merged = existing | new_dois
    final_count = save_known_dois(known_file, merged)

    print(f"\n[WRITE] {known_file}")
    print(f"  before: {initial_count}")
    print(f"  added:  +{len(truly_new)}")
    print(f"  after:  {final_count}")
    print(f"\n[VERIFY] wc -l {known_file}:")
    import subprocess
    result = subprocess.run(["wc", "-l", str(known_file)], capture_output=True, text=True)
    print(f"  {result.stdout.strip()}")
    return 0


def cmd_verify(args) -> int:
    """校验报告 vs 文件一致性模式。"""
    known_file = Path(args.known_dois_file)
    report_file = Path(args.report_file)

    if not known_file.exists():
        print(f"[ERROR] known_dois file not found: {known_file}", file=sys.stderr)
        return 2
    if not report_file.exists():
        print(f"[ERROR] report file not found: {report_file}", file=sys.stderr)
        return 2

    file_dois = load_known_dois(known_file)
    report_text = report_file.read_text()
    report_dois = {normalize_doi(d) for d in extract_dois_from_text(report_text)}

    drift_in_report = report_dois - file_dois  # 报告里有但文件里没有
    drift_in_file = file_dois - report_dois   # 文件里有但报告里没（仅警告）

    print(f"[STATS]")
    print(f"  known_dois.txt: {len(file_dois)} DOIs")
    print(f"  report mentions: {len(report_dois)} DOIs")

    if not drift_in_report:
        print(f"\n[OK] ✓ report ↔ file consistent")
        print(f"     (no DOIs in report missing from file)")
        if drift_in_file:
            print(f"\n[INFO] {len(drift_in_file)} DOIs in file but not mentioned in report (legacy, OK)")
        return 0
    else:
        print(f"\n[FAIL] ✗ DRIFT detected: {len(drift_in_report)} DOIs in report but missing from file")
        print(f"\nMissing DOIs (must be added to {known_file}):")
        for d in sorted(drift_in_report):
            print(f"  - {d}")
        print(f"\n[FIX] run again with --add-doi for each missing DOI, or:")
        print(f"  python3 scripts/laomo-evolution-dedup.py \\")
        print(f"    --known-dois-file {known_file} \\")
        print(f"    --report-file {report_file} \\")
        print(f"    --recover-missing")
        return 1


def cmd_recover(args) -> int:
    """从报告恢复缺失 DOI 模式（verify 失败后的修复）。"""
    known_file = Path(args.known_dois_file)
    report_file = Path(args.report_file)

    file_dois = load_known_dois(known_file)
    report_text = report_file.read_text()
    report_dois = {normalize_doi(d) for d in extract_dois_from_text(report_text)}

    missing = report_dois - file_dois
    if not missing:
        print(f"[OK] no missing DOIs to recover")
        return 0

    print(f"[RECOVER] {len(missing)} missing DOIs from {report_file.name}:")
    for d in sorted(missing):
        print(f"  + {d}")

    merged = file_dois | missing
    final_count = save_known_dois(known_file, merged)
    print(f"\n[WRITE] {known_file}: {len(file_dois)} → {final_count}")
    return 0


def main():
    parser = argparse.ArgumentParser(
        description="老莫 cron evolution: known_dois.txt atomic write + report self-consistency check",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--known-dois-file", required=True, help="Path to known_dois.txt")
    parser.add_argument("--new-dois-file", help="File with newline-separated DOIs to add")
    parser.add_argument("--add-doi", action="append", help="DOI string to add (can repeat)", default=[])
    parser.add_argument("--report-file", help="Evolution report .md file (for --verify/--recover-missing)")
    parser.add_argument("--verify", action="store_true", help="Check report vs file consistency")
    parser.add_argument("--recover-missing", action="store_true", help="Add DOIs from report that are missing in file")

    args = parser.parse_args()

    if args.recover_missing:
        if not args.report_file:
            print("[ERROR] --recover-missing requires --report-file", file=sys.stderr)
            return 2
        return cmd_recover(args)

    if args.verify:
        if not args.report_file:
            print("[ERROR] --verify requires --report-file", file=sys.stderr)
            return 2
        return cmd_verify(args)

    return cmd_add(args)


if __name__ == "__main__":
    sys.exit(main())