#!/usr/bin/env python3
"""Report self-consistency check (R27 字符扫描法，避开 R21 bash grep 误报).

验证 evolution report 中声称"已加入 known_dois.txt"的 DOI 是否真的在文件中。
用字符扫描法（而非 regex）避免 Markdown 反引号/括号包围时的截断误报。

Usage:
    python3 report-self-consistency.py \
        --known-dois-file /Users/hua/.hermes/profiles/laomo/evolution/known_dois.txt \
        --report-file /Users/hua/.hermes/profiles/laomo/evolution/2026-08-15_R27.md \
        --new-dois 10.3390/encyclopedia4010023 10.3390/ani14172555
"""
import argparse
import pathlib
import re
import sys


def extract_dois_from_text(text):
    """字符扫描法：从文本中提取所有 DOI 列表（避开 R21 bash grep 误报）.

    R21 教训：bash `grep -oE '10\\.[0-9]+/[a-zA-Z0-9._/-]+'` 会把
    `10.48045/001c.166391` 截断为 `10.48045/001c`（遇到 `.` 停止）。

    字符扫描法：
    1. 找所有 `10.` 起点
    2. 验证前一个字符是标点/空白（不是字母数字，避免 IP 地址误判）
    3. 扫 registrant 数字
    4. 期待 `/` 分隔符
    5. 扫 suffix（字母/数字/.-_/），直到第一个非法字符
    """
    dois = []
    i = 0
    while i < len(text):
        idx = text.find("10.", i)
        if idx == -1:
            break
        # 验证前一个字符
        if idx > 0 and text[idx-1].isalnum():
            i = idx + 3
            continue
        # 扫 registrant（数字）
        j = idx + 3
        while j < len(text) and text[j].isdigit():
            j += 1
        # 期待 / 分隔符
        if j >= len(text) or text[j] != "/":
            i = idx + 3
            continue
        j += 1
        # 扫 suffix
        while j < len(text) and text[j] in "***SECRET***._-/":
            j += 1
        doi = text[idx:j]
        if len(doi) > 7:
            dois.append(doi)
        i = j
    return dois


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--known-dois-file", required=True)
    parser.add_argument("--report-file", required=True)
    parser.add_argument("--new-dois", nargs="+", default=[],
                        help="本轮新增 DOI 列表，用于重点校验")
    parser.add_argument("--expected-report-only", nargs="+", default=[],
                        help="报告中应只出现但不入 known_dois.txt 的 DOI（如假阳性/示例）")
    args = parser.parse_args()

    report_text = pathlib.Path(args.report_file).read_text()
    known_text = pathlib.Path(args.known_dois_file).read_text().strip()

    known = {line.strip() for line in known_text.split("\n")
             if line.strip() and not line.startswith("#")}
    report_dois = set(extract_dois_from_text(report_text))

    print(f"=== 报告自洽校验 (R27 字符扫描法) ===\n")
    print(f"Report: {args.report_file}")
    print(f"Known DOIs file: {args.known_dois_file} ({len(known)} 条)\n")

    # 1. 新增 DOI 逐条校验
    if args.new_dois:
        print(f"--- 新增 DOI 校验 ({len(args.new_dois)} 条) ---")
        all_ok = True
        for doi in args.new_dois:
            in_known = doi in known
            in_report = doi in report_dois
            status = "✅" if (in_known and in_report) else "❌"
            if not (in_known and in_report):
                all_ok = False
            print(f"  {status} {doi}: known={in_known}, report={in_report}")
        if not all_ok:
            print("\n❌ 新增 DOI 不一致，需修复")
            sys.exit(1)

    # 2. 整体漂移检查
    print("\n--- 整体漂移检查 ---")
    drift = report_dois - known
    expected_only = set(args.expected_report_only)
    real_drift = drift - expected_only

    if real_drift:
        print(f"⚠️ 报告中引用但 known_dois.txt 缺失的 DOI:")
        for d in sorted(real_drift):
            print(f"    {d}")
        sys.exit(1)
    else:
        print(f"✅ 无漂移（排除已知报告-only DOI {len(expected_only)} 条）")

    extra = known - report_dois
    print(f"\nknown_dois.txt 中报告未提及的 DOI: {len(extra)} 条（其他 cron/历史累积）")
    print(f"\n✅ 自洽校验通过")


if __name__ == "__main__":
    main()