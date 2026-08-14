#!/usr/bin/env python3
"""报告自洽校验脚本 — R22 验证通过版本

用法：
    python3 report-self-consistency.py \\
        --known-dois-file /Users/hua/.hermes/profiles/laomo/evolution/known_dois.txt \\
        --report-file /Users/hua/.hermes/profiles/laomo/evolution/2026-08-14_R22.md

功能：
    1. 提取 Markdown 报告中所有 DOI（包括反引号/括号/逗号包围）
    2. 提取 known_dois.txt 中所有 DOI
    3. 验证 R22 新增 DOI 是否双向引用
    4. 检测报告↔文件漂移（报告引用但 known_dois.txt 缺失）
    5. 校验数量声明（如 "136 → 138"）是否与文件实际一致

依赖：Python 3 stdlib only
"""
import re
import argparse
import pathlib
import sys


def extract_dois_from_markdown(text):
    """从 Markdown 文本提取 DOI（处理反引号/括号/逗号包围）"""
    dois = set()
    # R21 修复版：兼容 `(10.xxx)`、`10.xxx`、`[10.xxx](url)`、`10.xxx,`
    pattern = r'(?:[` (]?)(10\.[0-9]+/[a-zA-Z0-9._/-]+)'
    for m in re.finditer(pattern, text):
        doi = m.group(1).rstrip("`.,;)")
        dois.add(doi)
    return dois


def extract_dois_from_file(path):
    """从 plain text 文件逐行提取 DOI（跳过注释行）"""
    dois = set()
    for line in pathlib.Path(path).read_text().strip().split("\n"):
        line = line.strip()
        if line and not line.startswith("#"):
            dois.add(line)
    return dois


def extract_quantity_claim(text):
    """提取报告中的数量声明（形如 '136 → 138' 或 '100 → 114'）"""
    m = re.search(r'(\d+)\s*→\s*(\d+)', text)
    if m:
        return int(m.group(1)), int(m.group(2))
    return None


def main():
    parser = argparse.ArgumentParser(description="Report ↔ known_dois.txt 自洽校验")
    parser.add_argument("--known-dois-file", required=True, help="known_dois.txt 路径")
    parser.add_argument("--report-file", required=True, help="evolution 报告 .md 路径")
    parser.add_argument("--new-dois", nargs="*", default=[], help="本轮新增 DOI（可选）")
    args = parser.parse_args()

    report_path = pathlib.Path(args.report_file)
    known_path = pathlib.Path(args.known_dois_file)

    if not report_path.exists():
        print(f"❌ 报告文件不存在: {report_path}")
        sys.exit(1)
    if not known_path.exists():
        print(f"❌ known_dois.txt 不存在: {known_path}")
        sys.exit(1)

    report = report_path.read_text()
    known = extract_dois_from_file(known_path)
    report_dois = extract_dois_from_markdown(report)

    print(f"=== 报告自洽校验 ===")
    print(f"报告: {report_path}")
    print(f"known_dois.txt: {known_path} ({len(known)} 条)")
    print(f"报告中提取的 DOI: {len(report_dois)} 条")
    print()

    # 1. 本轮新增 DOI 双向验证
    if args.new_dois:
        print(f"=== 本轮新增 DOI 校验 ({len(args.new_dois)} 篇) ===")
        all_ok = True
        for doi in args.new_dois:
            in_known = doi in known
            in_report = doi in report_dois
            status = "✅" if (in_known and in_report) else "❌"
            print(f"  {status} {doi}: known={in_known}, report={in_report}")
            if not (in_known and in_report):
                all_ok = False
        print()

    # 2. 漂移检测：报告引用但 known_dois.txt 缺失
    drift = report_dois - known
    if drift:
        print(f"⚠️ 报告引用但 known_dois.txt 缺失的 DOI ({len(drift)}):")
        for d in sorted(drift)[:20]:
            print(f"    {d}")
        # 注意：false positive 论文会在报告中出现但不入库，这是正常情况
        if len(drift) > 20:
            print(f"    ... 还有 {len(drift) - 20} 条")
    else:
        print(f"✅ 报告引用的所有 DOI 均在 known_dois.txt 中")

    # 3. known_dois.txt 多于报告（漏报）
    in_known_not_report = known - report_dois
    if in_known_not_report:
        print(f"\n⚠️ known_dois.txt 中存在但报告未引用的 DOI ({len(in_known_not_report)})")
        if args.new_dois:
            r22_missing = set(args.new_dois) & in_known_not_report
            if r22_missing:
                print(f"  本轮新增但未引用: {r22_missing}")

    # 4. 数量声明校验
    claim = extract_quantity_claim(report)
    if claim:
        old_count, new_count = claim
        actual_count = len(known)
        print(f"\n=== 数量声明校验 ===")
        print(f"  报告声明: {old_count} → {new_count}")
        print(f"  实际: {old_count} → {actual_count}")
        if new_count == actual_count:
            print(f"  ✅ 数量一致")
        else:
            print(f"  ⚠️ 数量不一致 (差 {actual_count - new_count})")

    print(f"\n=== 校验完成 ===")


if __name__ == "__main__":
    main()
