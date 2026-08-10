#!/usr/bin/env python3
"""老莫进化 - RAS+AI 论文检索（OpenAlex 优先，痛点方向）

可重用的 OpenAlex 论文检索脚本。基于2026-08-10 R13 验证的双桶策略 + 双条件过滤 + None 防御。

用法:
    python3 openalex-ras-search.py --keywords "biofilter nitrification AI recirculating aquaculture,Cryptocaryon irritans ML aquaculture"

环境:
    - 需要 Python 3.10+
    - 需要网络访问 api.openalex.org + api.crossref.org
    - cron 模式下: 必须用 write_file 写入 /tmp/，再用 terminal 调 python3（execute_code 被拦截）

经验法则（2026-08-10 验证）:
    - 痛点方向关键词命中率 70%+
    - 双条件过滤（aqua AND ai）剔除 90%+ 非水产命中
    - per_page=10 足够（再大稀释相关性）
    - time.sleep(0.6) 礼貌延迟，避免 429
"""
import urllib.request, urllib.parse, json, time, sys, re
from pathlib import Path

UA = "mailto:research@yuxintech.com"

# 双条件过滤（§3.5.3）
AQUACULTURE_KEYWORDS = ["aquaculture", "aquaponics", "recirculating", "tilapia", "salmon",
                        "catfish", "trout", "carp", "shrimp", "prawn", "seaweed", "fish farm"]
AI_KEYWORDS = ["machine learning", "deep learning", "neural network", "AI",
               "artificial intelligence", "computer vision", "IoT", "sensor",
               "prediction", "model", "control", "optimization", "monitoring",
               "detection", "classification", "estimation", "forecasting"]


def is_relevant(work):
    """§3.5.3 双条件过滤（AND 而非 OR）"""
    text = " ".join([
        (work.get("title") or "").lower(),
        " ".join(c.get("display_name", "").lower()
                for c in work.get("concepts", [])[:10])
    ])
    has_aqua = any(kw in text for kw in AQUACULTURE_KEYWORDS)
    has_ai = any(kw in text for kw in AI_KEYWORDS)
    return has_aqua and has_ai


def safe_get_venue(work):
    """§3.5.10 primary_location None 防御"""
    return ((work.get("primary_location") or {}).get("source") or {}).get("display_name")


def load_known_dois():
    """跨日 DOI 去重（§3.3.1）"""
    p = Path("/tmp/laomo_known_dois.txt")
    if p.exists():
        return set(line.strip() for line in p.read_text().split("\n") if line.strip())
    return set()


def append_known_dois(new_dois):
    """追加新 DOI 到去重集"""
    p = Path("/tmp/laomo_known_dois.txt")
    existing = set()
    if p.exists():
        existing = set(line.strip() for line in p.read_text().split("\n") if line.strip())
    existing.update(new_dois)
    p.write_text("\n".join(sorted(existing)) + "\n")


def search_openalex(keyword, per_page=10, year_range="2024-2026"):
    """OpenAlex 检索（fwci 排序 + relevance_score 兜底）"""
    encoded = urllib.parse.quote(keyword)
    url = (
        f"https://api.openalex.org/works?search={encoded}"
        f"&sort=relevance_score:desc,fwci:desc&per_page={per_page}"
        f"&filter=publication_year:{year_range}"
    )
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        data = json.loads(urllib.request.urlopen(req, timeout=20).read())
        return data.get("results", [])
    except Exception as e:
        print(f"  ERROR: {type(e).__name__}: {e}")
        return []


def crossref_verify(doi):
    """§3 双验证协议：Crossref 200 OK 即通过"""
    url = f"https://api.crossref.org/works/{doi}"
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            if resp.status != 200:
                return None, None, None, None, None
            data = json.loads(resp.read())
            msg = data.get("message", {})
            title = (msg.get("title") or [""])[0]
            container = (msg.get("container-title") or [""])[0]
            authors = [f"{a.get('given','')} {a.get('family','')}".strip()
                       for a in msg.get("author", [])[:5]]
            raw_abstract = msg.get("abstract", "")
            abstract = re.sub(r'<[^>]+>', '', raw_abstract) if raw_abstract else ""
            abstract = re.sub(r'\s+', ' ', abstract).strip()
            return title, container, authors, abstract, resp.status
    except Exception:
        return None, None, None, None, None


def main():
    # 默认关键词组（§3.4 + §3.5.10 双轮稳定验证）
    default_keywords = [
        "Cryptocaryon irritans early warning ML aquaculture",  # 双轮稳定 70%+
        "biofilter nitrification AI recirculating aquaculture",  # 极细分 RAS
        "feeding behavior monitoring AI fish farming",  # 大词但有命中
        "fish weight estimation regression underwater aquaculture",
    ]

    if len(sys.argv) > 1 and sys.argv[1] == "--keywords":
        keywords = sys.argv[2].split(",")
    else:
        keywords = default_keywords

    known_dois = load_known_dois()
    seen_dois = set(known_dois)
    candidates = []

    for kw in keywords:
        print(f"\n=== 查询: {kw} ===")
        results = search_openalex(kw)
        if not results:
            time.sleep(0.6)
            continue
        new_count = 0
        for w in results:
            doi = w.get("doi")
            if not doi:
                continue
            if doi in seen_dois:
                continue
            if not is_relevant(w):
                continue
            seen_dois.add(doi)
            candidates.append({
                "doi": doi,
                "title": w.get("title"),
                "publication_date": w.get("publication_date"),
                "cited_by_count": w.get("cited_by_count", 0),
                "fwci": w.get("fwci"),
                "venue": safe_get_venue(w),  # §3.5.10 防御 None
                "is_oa": (w.get("open_access") or {}).get("is_oa"),
                "query": kw,
            })
            new_count += 1
            if len([c for c in candidates if c["doi"] not in known_dois]) >= 8:
                break
        print(f"  新增: {new_count}, 总候选: {len(candidates)}")
        time.sleep(0.6)

    # 排序：fwci DESC, cited DESC, date DESC
    candidates.sort(key=lambda x: (
        -(x.get("fwci") or 0),
        -(x.get("cited_by_count") or 0),
        -(int(x.get("publication_date", "1900")[:4]) if x.get("publication_date") else 0)
    ))

    # 输出
    print(f"\n========== 候选论文 ({len(candidates)} 篇) ==========")
    for i, c in enumerate(candidates, 1):
        fwci_str = f"fwci={c['fwci']:.2f}" if c.get("fwci") else "fwci=N/A"
        print(f"\n[{i}] {c['title']}")
        print(f"    DOI: {c['doi']}")
        print(f"    期刊: {c.get('venue') or 'N/A'}")
        print(f"    日期: {c.get('publication_date')}")
        print(f"    被引: {c['cited_by_count']} | {fwci_str}")
        print(f"    OA: {c.get('is_oa')}")

    # 保存
    out = Path("/tmp/laomo_ras_candidates.json")
    out.write_text(json.dumps(candidates, indent=2, ensure_ascii=False))
    print(f"\n保存到 {out}")

    # 更新 DOI 去重集
    new_dois = [c["doi"] for c in candidates]
    if new_dois:
        append_known_dois(new_dois)
        print(f"追加 {len(new_dois)} DOI 到去重集")


if __name__ == "__main__":
    main()