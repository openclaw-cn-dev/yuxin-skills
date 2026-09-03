#!/usr/bin/env python3
"""老莫 cron evolution - arXiv 兜底检索脚本（OpenAlex/S2 限流时使用）

R53 (2026-09-01 08:17 UTC) 验证可运行版本。修复了以下历史 bug:
  - parse_xml() 返回值一致性 (list vs tuple)
  - ARXIV_NS namespace 拼写错误 (ARXIX_NS typo)
  - sleep 间隔不足导致连续 429
  - 双条件过滤 (aqua AND ai) 缺位

适用场景:
  - OpenAlex search API 持续 HTTP 429 (R39/R41/R53 实证)
  - Semantic Scholar 第 1 查询即 429 (2026-08-01 起)
  - cron 模式下需要快速切换兜底源

不适用场景:
  - 默认检索路径 (R39 §9 反向证据: arXiv `all:` 模板 RAS+AI 命中 0%)
  - 仅在 OpenAlex 持续 429 + DOI 直查不可用时尝试 (R39 快速收尾 SOP)

历史命中率:
  - R32 (2026-08-16): ti:abs: 结构化模板 4 组 = 17% (3/18)
  - R39 (2026-08-31): all: 宽泛模板 5 组 = 0% (0/15)
  - R52 (2026-08-31): 同 R32 结构化模板 4 组 = 0% (0/12, 第三次复现)
  - R53 (2026-09-01): all: 模板 = 0% (0/12) - 与 R39 同构

决策树 (R39 §9 + R53 §3):
  OpenAlex search 持续 429 (5+ 次)
    ↓ sleep 60s × 4 = 4min 仍 429
    ↓ DOI 直查 /works/doi:xxx 可用?
    ↓   ├─ 是 → 立即收尾, 不切 arXiv (R39 SOP)
    ↓   └─ 否 → 切 arXiv (本脚本, 用 R32 ti:abs: 结构化模板, 不用 all:)
    ↓ arXiv 4 关键词 × 3 篇 → 双条件过滤
    ↓   ├─ 命中 ≥1 → 走 R32 §4 三级摘要 fallback
    ↓   └─ 0 命中 → 写"arXiv 也 0 命中"报告, 立即收尾

用法:
    python3 arXiv-fallback.py
    # 默认运行 R32 §3 的 4 个结构化模板

输出:
    - /tmp/r53_arxiv_candidates.json (候选论文 JSON)
    - stdout: 每组查询的实时结果

环境:
    - Python 3.10+ (urllib.request, xml.etree.ElementTree)
    - 网络访问 export.arxiv.org
    - cron 模式: write_file + terminal 调用 (execute_code 被拦截)

经验法则 (R53 验证):
    - 每组查询间隔 sleep 15s (arXiv API 频率限制)
    - 双条件过滤 (aqua AND ai) 必须有, 否则 100% 非水产命中
    - max_results=3 (再大稀释相关性 + 浪费限流配额)
    - 用 ti:abs: 结构化模板 (R32) 而非 all: 宽泛模板 (R39/R53 0% 命中)
"""

import urllib.request
import urllib.error
import json
import time
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

# arXiv Atom namespace (Atom 1.0 规范)
ARXIV_NS = "{http://www.w3.org/2005/Atom}"

# R32 §3 结构化模板 (R39 反向证据后, all: 模板已废弃)
DEFAULT_QUERIES = [
    'ti:"aquaculture" AND abs:"deep learning" AND abs:"detection"',
    'ti:"fish" AND abs:"behavior" AND abs:"deep learning" AND abs:"aquaculture"',
    'abs:"recirculating aquaculture" AND abs:"machine learning"',
    'ti:"fish detection" AND abs:"deep learning"',
]

# 双条件过滤词表 (§3.5.3 升级版 + R19 扩词)
AQUACULTURE_KEYWORDS = [
    "aquaculture", "aquaponics", "recirculating", "tilapia", "salmon",
    "catfish", "trout", "carp", "shrimp", "prawn", "seaweed",
    "pond", "biofloc", "fish farm", "fish tank",
    "sea bass", "seabream", "fish pond",
]
AI_KEYWORDS = [
    "machine learning", "deep learning", "neural network", "ai",
    "artificial intelligence", "computer vision", "iot", "sensor",
    "prediction", "model", "control", "optimization", "monitoring",
    "detection", "classification", "estimation", "forecasting",
    "lstm", "xgboost", "random forest", "yolo", "transformer",
    "regression",
]


def build_arxiv_url(query: str, max_results: int = 3) -> str:
    """构建 arXiv API 查询 URL."""
    # arXiv API 需要把空格转 + 号, 引号需保留
    encoded = query.replace(" ", "+")
    return (
        f"https://export.arxiv.org/api/query?"
        f"search_query={encoded}&start=0&max_results={max_results}"
        f"&sortBy=submittedDate&sortOrder=descending"
    )


def fetch_arxiv(query: str, out_path: str, timeout: int = 20) -> tuple[bool, str]:
    """单次 arXiv 查询. 返回 (success, message).

    R53 防御式编程:
      - 20s 超时 (实测 30s 不够, 但太长浪费 cron 时间窗)
      - 响应 < 50 bytes 判定为限流 (rate-limited tiny response)
    """
    url = build_arxiv_url(query)
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "mailto:research@yuxintech.com"})
        resp = urllib.request.urlopen(req, timeout=timeout)
        data = resp.read()
        Path(out_path).write_bytes(data)
        if len(data) < 50:
            return False, f"tiny response ({len(data)} bytes), likely rate-limited"
        return True, f"OK ({len(data)} bytes)"
    except urllib.error.HTTPError as e:
        return False, f"HTTP {e.code}: {e.reason}"
    except Exception as e:
        return False, f"{type(e).__name__}: {e}"


def parse_xml(path: str) -> tuple[list[dict], str | None]:
    """解析 arXiv Atom XML. 返回 (papers, error).

    R53 修复: 返回值统一为 tuple, 避免 R53 第 1 次脚本崩溃.
    """
    try:
        tree = ET.parse(path)
        root = tree.getroot()
        papers = []
        for entry in root.findall(f"{ARXIV_NS}entry"):
            # arXiv id 在 <id> 字段, e.g. http://arxiv.org/abs/2409.01148v1
            arxiv_id_full = entry.find(f"{ARXIV_NS}id").text
            arxiv_id = arxiv_id_full.split("/")[-1]  # 去 URL 前缀
            arxiv_id_no_v = arxiv_id.split("v")[0] if "v" in arxiv_id else arxiv_id

            paper = {
                "arxiv_id": arxiv_id_no_v,
                "title": entry.find(f"{ARXIV_NS}title").text.strip(),
                "published": entry.find(f"{ARXIV_NS}published").text,
                "summary": entry.find(f"{ARXIV_NS}summary").text.strip()[:500],
                "authors": [
                    a.find(f"{ARXIV_NS}name").text
                    for a in entry.findall(f"{ARXIV_NS}author")
                ],
            }
            papers.append(paper)
        return papers, None
    except ET.ParseError as e:
        return [], f"XML parse error: {e}"
    except Exception as e:
        return [], f"{type(e).__name__}: {e}"


def is_relevant(paper: dict) -> tuple[bool, str]:
    """双条件过滤 (aqua AND ai). 返回 (pass, reason)."""
    text = (paper["title"] + " " + paper["summary"]).lower()
    has_aqua = any(kw in text for kw in AQUACULTURE_KEYWORDS)
    has_ai = any(kw in text for kw in AI_KEYWORDS)
    if not (has_aqua and has_ai):
        return False, "no_aqua_or_ai"
    return True, "pass"


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--queries":
        queries = sys.argv[2].split("|")
    else:
        queries = DEFAULT_QUERIES

    print(f"=== arXiv 兜底检索 ({len(queries)} 个查询) ===")
    all_papers: list[tuple[str, dict]] = []
    for i, q in enumerate(queries):
        print(f"\n[Query {i + 1}/{len(queries)}] {q}")
        out_path = f"/tmp/r53_arxiv_q{i}.xml"
        ok, msg = fetch_arxiv(q, out_path)
        if not ok:
            print(f"  ❌ fetch failed: {msg}")
            continue
        papers, err = parse_xml(out_path)
        if err:
            print(f"  ❌ parse error: {err}")
            continue
        print(f"  ✅ {len(papers)} papers fetched")
        for p in papers:
            print(f"    - {p['published'][:10]} | {p['title'][:80]}")
        all_papers.extend([(q, p) for p in papers])
        if i < len(queries) - 1:
            print(f"  [sleep 15s for arXiv rate limit]")
            time.sleep(15)

    print(f"\n=== 总计: {len(all_papers)} 篇 ===")
    print("\n=== 双条件过滤 (aqua AND ai) ===")
    seen_ids: set[str] = set()
    candidates: list[tuple[str, dict]] = []
    for q, p in all_papers:
        if p["arxiv_id"] in seen_ids:
            print(f"  [SKIP] duplicate: {p['arxiv_id']}")
            continue
        seen_ids.add(p["arxiv_id"])
        ok, reason = is_relevant(p)
        if not ok:
            print(f"  [SKIP] {reason}: {p['title'][:70]}")
            continue
        candidates.append((q, p))
        print(f"  [CAND] {p['published'][:10]} | {p['title'][:80]}")

    # 保存候选 (R32 §5 arXiv ID 规范: 用 arxiv: 前缀避免与 DOI 库冲突)
    out_json = Path("/tmp/r53_arxiv_candidates.json")
    out_json.write_text(
        json.dumps(
            [
                {
                    "query": q,
                    "arxiv_id": p["arxiv_id"],
                    "doi_form": f"arxiv:{p['arxiv_id']}",  # known_dois.txt 写入规范
                    "title": p["title"],
                    "published": p["published"],
                    "summary_excerpt": p["summary"][:300],
                    "authors": p["authors"][:5],
                }
                for q, p in candidates
            ],
            indent=2,
            ensure_ascii=False,
        )
    )

    print(f"\n📊 候选: {len(candidates)} 篇 → {out_json}")
    print("\n⚠️  决策提醒:")
    print("  - arXiv 命中论文需走 R32 §4 三级摘要 fallback")
    print("  - Crossref 100% 不会命中 (arXiv DOI 在 DataCite, 不在 Crossref)")
    print("  - OpenAlex 倒排索引 80%+ 成功率 (用 doi_oa = '10.48550/arXiv.{id_no_version}')")
    print("  - 命中 0 篇时立即收尾, 不重复执行")


if __name__ == "__main__":
    main()
