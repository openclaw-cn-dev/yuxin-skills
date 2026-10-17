#!/usr/bin/env python3
"""
verify_references_paths.py — pitfall-77 协议补丁(心跳 #N+73 实测)

扫描 SKILL.md 工具栈速查入口表中所有 `references/*.md` 路径,
对照实际文件系统状态,输出:
- ✅ 存在
- ⚠️ 缺失(列出)
- 📊 缺失数:≥5 → P1 红旗(心跳协议)
- 📊 缺失数:1-4 → 普通记录(写入 evolution)
- 📊 缺失数:0 → 全部命中

执行 ≤3s,绝对路径(pitfall-63)。
心跳 Step 0 / Step 1 之间可调用,或独立 evolution 检查时调用。

使用:
    python3 /Users/hua/.hermes/profiles/quant/scripts/verify_references_paths.py
    python3 /Users/hua/.hermes/profiles/quant/scripts/verify_references_paths.py --strict
        # --strict: 缺失 ≥1 → exit 1(用于 pre-commit hook)
"""
import os
import re
import sys
from pathlib import Path

SKILL_PATH = Path("/Users/hua/.hermes/profiles/quant/references")  # 实际文件系统路径
SKILL_MD = Path("/Users/hua/.hermes/skills/quant/quantitative-research/SKILL.md")

# 从 SKILL.md 表格中正则提取所有 references/*.md 路径
# 表格行格式: | ... | `references/<name>.md` | ... |
PATTERN = re.compile(r"`(references/([a-zA-Z0-9_\-]+\.md))`")


def extract_paths():
    """从 SKILL.md 提取所有 references/*.md 引用路径"""
    if not SKILL_MD.exists():
        print(f"❌ SKILL.md 不存在: {SKILL_MD}")
        sys.exit(2)
    text = SKILL_MD.read_text(encoding="utf-8")
    matches = PATTERN.findall(text)
    # 去重保序
    seen = set()
    unique = []
    for full_path, name in matches:
        if name not in seen:
            seen.add(name)
            unique.append((full_path, name))
    return unique


def verify(paths):
    """核验每条路径是否存在"""
    results = []
    for rel_path, name in paths:
        full = SKILL_PATH / name
        status = "✅" if full.exists() else "⚠️"
        results.append((name, status, full))
    return results


def main():
    strict = "--strict" in sys.argv
    paths = extract_paths()
    if not paths:
        print("❌ SKILL.md 中未找到任何 references/*.md 引用")
        sys.exit(1)

    print(f"=== SKILL.md references/ 路径核验(心跳 #N+73 pitfall-77) ===")
    print(f"SKILL.md: {SKILL_MD}")
    print(f"实际目录: {SKILL_PATH}")
    print(f"引用总数: {len(paths)}")
    print()

    results = verify(paths)
    present = sum(1 for _, s, _ in results if s == "✅")
    missing = sum(1 for _, s, _ in results if s == "⚠️")

    # 列出全部路径(便于审计)
    for name, status, full in results:
        marker = status
        print(f"  {marker}  {name}")

    print()
    print(f"=== 汇总 ===")
    print(f"存在: {present}/{len(paths)}")
    print(f"缺失: {missing}/{len(paths)}")

    # pitfall-77 协议
    if missing == 0:
        print("✅ 全部命中")
        rc = 0
    elif missing <= 4:
        print(f"⚠️ 普通缺失({missing} 条) → evolution 报告记录,不触发红旗")
        rc = 1 if strict else 0
    else:
        print(f"🚨 P1 红旗: 缺失 ≥5 条({missing} 条) → SKILL.md 严重虚声明,建议批量创建桩文件")
        print(f"   推荐:心跳下次跑 `for name in missing_names; do touch references/$name; done`")
        rc = 1 if strict else 2

    sys.exit(rc)


if __name__ == "__main__":
    main()
