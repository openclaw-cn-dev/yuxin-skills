#!/usr/bin/env python3
"""老莫进化 - Crossref 验证 + 摘要获取（Top N 批量）

基于2026-08-10 R13 验证的 Crossref 双验证流程。
从 /tmp/laomo_ras_candidates.json 读取候选，对每个候选执行 Crossref 验证并获取摘要。

用法:
    python3 crossref-batch-verify.py [--top N]

输出:
    /tmp/laomo_ras_verified.json 包含 Crossref 验证后的完整元数据
"""
import urllib.request, json, re, time, sys
from pathlib import Path

UA = "mailto:research@yuxintech.com"


def crossref_full(doi):
    """获取 Crossref 完整元数据 + 摘要清洗"""
    url = f"https://api.crossref.org/works/{doi}"
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            if resp.status != 200:
                return {"doi": doi, "crossref_status": resp.status, "verified": False}
            data = json.loads(resp.read())
            msg = data.get("message", {})

            # 摘要清洗（去除 <jats:p> 等 XML 标签）
            raw_abstract = msg.get("abstract", "")
            abstract = re.sub(r'<[^>]+>', '', raw_abstract) if raw_abstract else ""
            abstract = re.sub(r'\s+', ' ', abstract).strip()

            return {
                "doi": doi,
                "crossref_status": resp.status,
                "verified": True,
                "crossref_title": (msg.get("title") or [""])[0],
                "crossref_container": (msg.get("container-title") or [""])[0],
                "crossref_date": msg.get("published", {}).get("date-parts", [[None]])[0],
                "crossref_authors": [f"{a.get('given','')} {a.get('family','')}".strip()
                                     for a in msg.get("author", [])[:5]],
                "crossref_abstract": abstract[:3000],  # 限长
            }
    except Exception as e:
        return {"doi": doi, "crossref_status": None, "verified": False, "error": str(e)}


def main():
    top_n = 4
    if len(sys.argv) > 1 and sys.argv[1] == "--top":
        try:
            top_n = int(sys.argv[2])
        except (ValueError, IndexError):
            top_n = 4

    in_path = Path("/tmp/laomo_ras_candidates.json")
    if not in_path.exists():
        print(f"❌ {in_path} 不存在。先跑 openalex-ras-search.py 生成候选。")
        sys.exit(1)

    candidates = json.loads(in_path.read_text())
    selected = candidates[:top_n]

    print(f"========== Crossref 双验证 Top {len(selected)} ==========")
    results = []
    for c in selected:
        doi = c["doi"]
        title = c.get("title", "")[:80]
        print(f"\n>>> {doi}")
        print(f"    标题: {title}")
        result = crossref_full(doi)
        if result["verified"]:
            print(f"    ✅ Crossref 200 OK")
            print(f"    期刊: {result['crossref_container']}")
            print(f"    作者: {', '.join(result['crossref_authors'][:3])}")
            print(f"    摘要: {result['crossref_abstract'][:150]}...")
        else:
            print(f"    ❌ 验证失败: status={result['crossref_status']}, error={result.get('error')}")
        # 合并 OpenAlex 元数据
        result["openalex_title"] = title
        result["openalex_fwci"] = c.get("fwci")
        result["openalex_cited"] = c.get("cited_by_count")
        result["openalex_pub_date"] = c.get("publication_date")
        result["query"] = c.get("query")
        results.append(result)
        time.sleep(0.4)  # 礼貌延迟

    out_path = Path("/tmp/laomo_ras_verified.json")
    out_path.write_text(json.dumps(results, indent=2, ensure_ascii=False))
    verified_count = sum(1 for r in results if r["verified"])
    print(f"\n========== 验证汇总 ==========")
    print(f"Crossref 200 OK: {verified_count}/{len(results)}")
    print(f"保存到 {out_path}")


if __name__ == "__main__":
    main()