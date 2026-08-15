#!/usr/bin/env python3
"""Zenodo 同关键词 DUP 鉴别器 - R24 沉淀 (2026-08-14)

用法:
    python3 zenodo-dup-detector.py <id_a> <id_b>

判定规则: 标题完全一致 + 作者列表完全一致 = DUP
"""
import sys
import urllib.request
import json


UA = "mailto:research@yuxintech.com"


def fetch_zenodo(zenodo_id):
    """拉取 Zenodo 论文元数据"""
    url = f"https://zenodo.org/api/records/{zenodo_id}"
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read())


def check_dup(id_a, id_b):
    """检查两个 Zenodo DOI 是否 DUP"""
    try:
        data_a = fetch_zenodo(id_a)
        data_b = fetch_zenodo(id_b)
    except Exception as e:
        return {"error": str(e), "is_dup": None}

    title_a = data_a.get("metadata", {}).get("title", "")
    title_b = data_b.get("metadata", {}).get("title", "")

    creators_a = [c.get("name", "") for c in data_a.get("metadata", {}).get("creators", [])]
    creators_b = [c.get("name", "") for c in data_b.get("metadata", {}).get("creators", [])]

    title_match = title_a == title_b
    creators_match = creators_a == creators_b
    is_dup = title_match and creators_match

    return {
        "id_a": id_a,
        "id_b": id_b,
        "title_match": title_match,
        "creators_match": creators_match,
        "is_dup": is_dup,
        "title_a": title_a[:80],
        "title_b": title_b[:80],
        "creators_a": creators_a[:5],
        "creators_b": creators_b[:5],
    }


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("用法: python3 zenodo-dup-detector.py <zenodo_id_a> <zenodo_id_b>")
        print("示例: python3 zenodo-dup-detector.py 20966580 20966579")
        sys.exit(1)

    result = check_dup(sys.argv[1], sys.argv[2])
    print(json.dumps(result, ensure_ascii=False, indent=2))

    if result.get("is_dup"):
        print("\n❌ DUP 判定：两个 DOI 标题+作者完全一致，建议只保留一个（推荐保留较小 ID）")
        sys.exit(0)
    else:
        print("\n✅ 非 DUP：两个 DOI 是独立论文，可分别入库")
        sys.exit(0)