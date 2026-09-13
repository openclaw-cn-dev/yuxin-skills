# -*- coding: utf-8 -*-
"""
老莫 OpenAlex RAS 文献检索统一入口 (R426 Pitfall #66 防御 a)

Pitfall #66: OpenAlex /works?search= query 未 URL-encode 触发 InvalidURL
防御: query 必走 urllib.parse.quote()；filter 段保持原样（逗号分隔 key:value）

用法:
    from openalex_search import openalex_search
    results = openalex_search(
        'recirculating aquaculture system AND (machine learning OR water quality)',
        filter_str='type:article,language:en',
        per_page=10,
        from_date='2024-01-01'
    )
    for r in results:
        print(r['doi'], '|', r['title'])

依赖: 仅 Python stdlib（json, urllib, time）
"""

import json
from urllib.request import urlopen, Request
from urllib.parse import quote
import time


def openalex_search(
    query: str,
    filter_str: str = '',
    per_page: int = 10,
    from_date: str = '2024-01-01',
    timeout: int = 30,
    sleep_seconds: float = 1.0,
) -> list:
    """
    老莫 R<n> OpenAlex RAS 文献检索统一入口

    Args:
        query: 检索词，支持 AND/OR/NOT/括号/引号短语
        filter_str: filter 段（逗号分隔 key:value），如 'type:article,language:en'
        per_page: 返回条数（建议 ≤ 50 避免被限流）
        from_date: 起始日期 YYYY-MM-DD
        timeout: urlopen 超时秒数
        sleep_seconds: 调用后等待秒数（防限流，Pitfall #3 防御）

    Returns:
        候选论文列表 [{'doi', 'title', 'cited_by_count', 'publication_date', 'type'}, ...]
    """
    base = 'https://api.openalex.org/works'
    search_encoded = quote(query)  # Pitfall #66 防御 a —— 必走 quote()

    # filter 段拼接（防御 b：保持原样逗号分隔）
    parts = []
    if filter_str:
        parts.append(filter_str)
    if from_date:
        parts.append(f'from_publication_date:{from_date}')
    filter_part = ','.join(parts) if parts else ''
    filter_query = f'&filter={filter_part}' if filter_part else ''

    url = (
        f'{base}?search={search_encoded}'
        f'{filter_query}'
        f'&per_page={per_page}'
        f'&mailto=laomo@yuxin.ai'  # Pitfall #3 防御 —— polite pool
    )

    req = Request(url, headers={'User-Agent': 'laomo/1.0 (mailto:laomo@yuxin.ai)'})

    # Pitfall #66 防御 d —— try/except InvalidURL 探针
    try:
        data = json.loads(urlopen(req, timeout=timeout).read())
    except Exception as e:
        print(f'❌ OpenAlex 调用失败: {type(e).__name__}: {e}')
        print(f'   URL: {url[:150]}...')
        raise

    results = []
    for w in data.get('results', []):
        if w.get('doi') and w.get('title'):
            results.append({
                'doi': w['doi'],
                'title': w['title'],
                'cited_by_count': w.get('cited_by_count', 0),
                'publication_date': w.get('publication_date'),
                'type': w.get('type'),
                'openalex_id': w.get('id'),
            })

    # Pitfall #3 防御 —— 调用后等待，避免高频触发 429
    time.sleep(sleep_seconds)

    return results


def crossref_verify(doi: str, timeout: int = 20) -> dict:
    """
    R175 防御 4 必做：Crossref 二次验证真标题
    （Pitfall #66 配套防御 —— OpenAlex abstract 命中不能信，必须 Crossref 拉真标题）

    Args:
        doi: Digital Object Identifier
        timeout: urlopen 超时秒数

    Returns:
        Crossref message dict，含 'title', 'type', 'published' 等字段
    """
    safe = doi.replace('/', '_').replace('.', '_')
    url = f'https://api.crossref.org/works/{doi}'
    req = Request(url, headers={'User-Agent': 'laomo/1.0 (mailto:laomo@yuxin.ai)'})

    # 写文件不用 curl | python3（触发 tirith）
    import os
    cache_path = f'/tmp/cr_{safe}.json'
    with urlopen(req, timeout=timeout) as resp:
        with open(cache_path, 'wb') as f:
            f.write(resp.read())

    with open(cache_path) as f:
        data = json.load(f)

    os.remove(cache_path)
    return data.get('message', {})


def is_ras_paper(crossref_msg: dict) -> bool:
    """
    R175 防御 4 必做：Crossref message 判断是否真 RAS 论文
    """
    if crossref_msg.get('type') != 'journal-article':
        return False
    title = (crossref_msg.get('title') or [''])[0].lower()
    abstract = (crossref_msg.get('abstract') or '').lower()
    haystack = title + ' ' + abstract
    ras_keywords = [
        'aquaculture', 'recirculat', 'ras',
        'fish', 'shrimp', 'tilapia', 'trout', 'salmon',
        'ammonia', 'nitrit', 'nitrogen', 'dissolved oxygen',
        'biofilter', 'biofloc', 'water quality',
    ]
    return any(kw in haystack for kw in ras_keywords)


if __name__ == '__main__':
    # R426 实战 demo
    print('=== R426 OpenAlex RAS 文献检索 demo ===')
    results = openalex_search(
        'recirculating aquaculture system AND (machine learning OR water quality)',
        filter_str='type:article,language:en',
        per_page=5,
        from_date='2024-01-01',
    )
    print(f'OpenAlex 候选: {len(results)} 条')
    for r in results[:5]:
        print(f'  - {r["doi"]} | cited={r["cited_by_count"]} | {r["title"][:60]}')

    print()
    print('=== R175 防御 4 必做: Crossref 二次验证 ===')
    verified = []
    for r in results[:5]:
        try:
            msg = crossref_verify(r['doi'])
            ras_ok = is_ras_paper(msg)
            true_title = (msg.get('title') or [''])[0][:60]
            print(f'  {"✅" if ras_ok else "❌"} {r["doi"]}')
            print(f'     真标题: {true_title}')
            if ras_ok:
                verified.append({**r, 'true_title': true_title})
        except Exception as e:
            print(f'  ⚠️ {r["doi"]}: {e}')
    print(f'\n最终入库候选 (journal-article + RAS keyword): {len(verified)}/{len(results)}')
