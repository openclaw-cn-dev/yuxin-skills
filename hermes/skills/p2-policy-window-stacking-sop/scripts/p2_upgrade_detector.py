#!/usr/bin/env python3
"""
P2 升级检测脚本（v1.62.12.6 中午档沉淀）
触发：当 cron 自进化模式进入"调研 → 话术升级"阶段时调用
功能：跑 web_search 命中新省份/新巨头/新亿元项目/新省级数据 → 输出升级建议
输出：P2 升级建议报告（v_(N+1) 触发条件命中清单）

用法：
    python3 p2_upgrade_detector.py [当前版本号]

示例：
    python3 p2_upgrade_detector.py v5
    # 输出：v6 升级建议 + 调研方向

依赖：仅 Python 标准库（json, subprocess）· 不需要第三方包
"""

import json
import subprocess
import sys
from datetime import datetime


# === 已知升级触发关键词库 ===
P2_TRIGGER_QUERIES = [
    # 新省份实证
    "循环水养殖 2026 {province} 工厂化 新案例",
    # 新互联网/饲料巨头入场
    "{company} 工厂化循环水 投资 {year} 上市",
    # 新亿元项目
    "工厂化循环水 {species} 投资 {amount}亿 {year}",
    # 新养殖品种省级数据
    "{province} {species} 工厂化循环水 水体 {volume}",
    # 全国/省级官方数据新维度
    "设施渔业 养殖容积 {province} 2026 农业农村部",
]

# 8 省已知实证库（v6 已沉淀）
KNOWN_PROVINCES = ["广东", "广西", "湖北", "江苏", "贵州", "福建", "山东", "四川"]

# 已知资本巨头（v6 已沉淀）
KNOWN_GIANTS = ["京东", "通威"]

# 已知养殖品种实证（v6 已沉淀）
KNOWN_SPECIES = ["加州鲈", "虹鳟", "鳜鱼", "对虾", "南美白对虾"]


def web_search(query: str, limit: int = 5) -> dict:
    """调用 web_search 工具（通过 hermes CLI）"""
    try:
        result = subprocess.run(
            ["hermes", "tools", "web_search", query, "--limit", str(limit)],
            capture_output=True,
            text=True,
            timeout=30,
        )
        return json.loads(result.stdout)
    except Exception as e:
        return {"success": False, "error": str(e)}


def detect_new_province(current_provinces: list) -> list:
    """检测新省份实证"""
    new_provinces = []
    common_provinces = ["浙江", "安徽", "江西", "湖南", "云南", "四川", "河南", "河北"]

    for province in common_provinces:
        if province in current_provinces:
            continue

        query = f"循环水养殖 2026 {province} 工厂化 新案例"
        print(f"[detect] 搜索 {province} ... ", end="", flush=True)
        result = web_search(query)

        if result.get("success") and result.get("data", {}).get("web"):
            sources = result["data"]["web"]
            if len(sources) >= 1:
                new_provinces.append({
                    "province": province,
                    "query": query,
                    "sources_count": len(sources),
                    "first_source_title": sources[0].get("title", ""),
                    "first_source_url": sources[0].get("url", ""),
                })
                print(f"✅ 命中 {len(sources)} 源")
            else:
                print("⚠️ 无源")
        else:
            print(f"❌ 失败 ({ {result.get('error')} })")

    return new_provinces


def detect_new_giants(current_giants: list) -> list:
    """检测新互联网/饲料/制造业巨头入场"""
    candidate_companies = [
        "美团", "阿里", "拼多多", "网易", "腾讯", "百度",
        "新希望", "海大", "大北农", "禾丰", "正大",
    ]

    new_giants = []
    for company in candidate_companies:
        if company in current_giants:
            continue

        query = f"{company} 工厂化循环水 投资 2026 上市"
        print(f"[detect] 搜索 {company} ... ", end="", flush=True)
        result = web_search(query)

        if result.get("success") and result.get("data", {}).get("web"):
            sources = result["data"]["web"]
            if len(sources) >= 1:
                new_giants.append({
                    "company": company,
                    "query": query,
                    "sources_count": len(sources),
                    "first_source_title": sources[0].get("title", ""),
                })
                print(f"✅ 命中 {len(sources)} 源")
            else:
                print("⚠️ 无源")
        else:
            print(f"❌ 失败")

    return new_giants


def generate_upgrade_report(current_version: str) -> dict:
    """生成 P2 升级建议报告"""
    print(f"=== P2 {current_version} 升级检测报告 ===")
    print(f"生成时间：{datetime.now().isoformat()}")
    print()

    # Step 1: 检测新省份
    print("[Step 1] 检测新省份实证 ...")
    new_provinces = detect_new_province(KNOWN_PROVINCES)
    print(f"→ 新省份命中：{len(new_provinces)} 个")
    for p in new_provinces:
        print(f"  - {p['province']}: {p['sources_count']} 源 ({p['first_source_title'][:50]}...)")

    # Step 2: 检测新巨头
    print()
    print("[Step 2] 检测新资本巨头入场 ...")
    new_giants = detect_new_giants(KNOWN_GIANTS)
    print(f"→ 新巨头命中：{len(new_giants)} 个")
    for g in new_giants:
        print(f"  - {g['company']}: {g['sources_count']} 源")

    # Step 3: 升级建议
    print()
    print("[Step 3] 升级建议 ...")
    triggers = len(new_provinces) + len(new_giants)

    if triggers == 0:
        recommendation = f"无需升级 P2 {current_version}（无新触发）"
    elif triggers == 1:
        next_version = current_version.upper().replace("V", "v") + ".next"
        recommendation = f"⚠️ 考虑升级（1 个触发条件命中）→ P2 {next_version}"
    elif triggers >= 2:
        next_version = current_version.upper().replace("V", "v") + ".next"
        recommendation = f"🔴 必须升级（{triggers} 个触发条件命中）→ P2 {next_version}"
    else:
        recommendation = f"❌ 未知状态"

    print(recommendation)

    return {
        "current_version": current_version,
        "detection_time": datetime.now().isoformat(),
        "new_provinces": new_provinces,
        "new_giants": new_giants,
        "triggers_count": triggers,
        "recommendation": recommendation,
    }


def main():
    current_version = sys.argv[1] if len(sys.argv) > 1 else "v6"
    report = generate_upgrade_report(current_version)
    print()
    print("=== JSON 输出（可保存到 evolution/）===")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()