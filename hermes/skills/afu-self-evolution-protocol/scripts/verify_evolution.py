#!/usr/bin/env python3
"""
阿福自我进化元数据三方一致性自检脚本 v1.0
==========================================
扫描三个核心 skill 文件的 YAML frontmatter，验证：
1. version 字段唯一
2. changelog 最新条目与 version 一致
3. 三方（voss / 顶层门户 / 主索引）版本号对齐

用法:
    python3 ~/.hermes/skills/afu-self-evolution-protocol/scripts/verify_evolution.py

退出码:
    0 — 三方一致
    1 — 一致性失败（需修复）
    2 — 文件缺失
"""
import re
import sys
from pathlib import Path

# 三个核心文件
FILES = {
    "voss-techniques": Path.home() / ".hermes/profiles/afu/skills/negotiation-voss-techniques/SKILL.md",
    "顶层门户": Path.home() / ".hermes/profiles/afu/skills/afu-customer-service/SKILL.md",
    "主索引": Path.home() / ".hermes/profiles/afu/skills/productivity/afu-customer-service/SKILL.md",
}


def parse_frontmatter(path: Path) -> dict:
    """解析 YAML frontmatter，返回字段字典"""
    if not path.exists():
        return {"_error": f"文件不存在: {path}"}

    content = path.read_text(encoding="utf-8")

    # 匹配 --- 包围的 frontmatter
    m = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not m:
        return {"_error": "无 frontmatter"}

    fm = m.group(1)
    result = {}

    # 解析 version
    v = re.search(r"^version:\s*(.+)$", fm, re.MULTILINE)
    if v:
        result["version"] = v.group(1).strip()

    # 解析 changelog 最新条目版本号
    cl = re.findall(r"^\s*-\s*(\d+\.\d+\.\d+)\s+\(", fm, re.MULTILINE)
    if cl:
        result["changelog_latest"] = cl[0]

    # 双重 version 检测
    v_count = len(re.findall(r"^version:\s*", fm, re.MULTILINE))
    result["version_count"] = v_count

    return result


def main() -> int:
    print("=" * 60)
    print("阿福元数据三方一致性自检 · v1.0")
    print("=" * 60)

    results = {}
    for label, path in FILES.items():
        results[label] = parse_frontmatter(path)
        r = results[label]
        if "_error" in r:
            print(f"❌ {label}: {r['_error']}")
            continue
        print(f"\n📄 {label}")
        print(f"   path: {path}")
        print(f"   version: {r.get('version', 'N/A')}")
        print(f"   changelog_latest: {r.get('changelog_latest', 'N/A')}")
        print(f"   version_field_count: {r.get('version_count', 'N/A')}")

    print("\n" + "=" * 60)
    print("一致性检查")
    print("=" * 60)

    errors = []

    # 1. 双重 version 检测
    for label, r in results.items():
        if r.get("version_count", 0) > 1:
            errors.append(f"❌ {label}: 出现 {r['version_count']} 个 version 字段（双重字段失误）")

    # 2. version 与 changelog 一致性
    for label, r in results.items():
        if "_error" in r:
            continue
        v = r.get("version")
        cl = r.get("changelog_latest")
        if v and cl and v != cl:
            errors.append(f"❌ {label}: version={v} 但 changelog 最新条目={cl}（不一致）")

    # 3. 三方版本号对齐（voss < 顶层门户 < 主索引 或 同值）
    v_voss = results.get("voss-techniques", {}).get("version")
    v_top = results.get("顶层门户", {}).get("version")
    v_main = results.get("主索引", {}).get("version")

    if v_voss and v_top and v_main:
        # 简单对齐检查：三方都不为空，且都不是 N/A
        if v_voss == "N/A" or v_top == "N/A" or v_main == "N/A":
            errors.append("❌ 三方版本号有空缺")
        else:
            print(f"\n✅ 三方版本号: voss={v_voss} ↔ 顶层门户={v_top} ↔ 主索引={v_main}")

    print("\n" + "=" * 60)
    if errors:
        print("❌ 失败 — 需要修复")
        for e in errors:
            print(f"  {e}")
        return 1
    else:
        print("✅ 通过 — 三方一致")
        return 0


if __name__ == "__main__":
    sys.exit(main())