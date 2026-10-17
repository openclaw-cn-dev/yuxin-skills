"""
SSL bypass 修复 arXiv listing 持续 HTTP 406 问题(pitfall-N+112 + 心跳 #N+99 修复)。

心跳 #N+98 沉淀:7 页 listing 全部 406,即便 6 项 headers(Accept/UA/Accept-Language/
Accept-Encoding/Connection/Upgrade-Insecure-Requests)增强仍被拒。

心跳 #N+99 实测:加 ssl.create_default_context() + check_hostname=False +
verify_mode=CERT_NONE 后 listing 重新可用(53+53+49 = 155 hits,3 页全 200)。

用法:
    python3 /Users/hua/.hermes/profiles/quant/scripts/arxiv_v2_ssl_bypass.py
    # 或内联调用 fetch_arxiv_listing(url) 函数

返回:
    list[str] — arXiv ID 列表,带去重
"""
import urllib.request, re, ssl, sys

SSL_CTX = ssl.create_default_context()
SSL_CTX.check_hostname = False
SSL_CTX.verify_mode = ssl.CERT_NONE

UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
HDRS = {
    'User-Agent': UA,
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
}


def fetch_arxiv_listing(url: str, timeout: int = 20) -> str:
    """带 SSL bypass 的 arXiv listing 拉取。

    Args:
        url: 完整 arXiv listing URL(如 https://arxiv.org/list/q-fin/recent?skip=0&show=50)
        timeout: 总超时秒数

    Returns:
        HTML 字符串;失败抛 RuntimeError
    """
    req = urllib.request.Request(url, headers=HDRS)
    try:
        return urllib.request.urlopen(req, timeout=timeout, context=SSL_CTX).read().decode('utf-8', 'ignore')
    except Exception as e:
        raise RuntimeError(f'arXiv listing {url} failed: {type(e).__name__} {e}')


def extract_arxiv_ids(html: str) -> list[str]:
    """从 arXiv listing HTML 提取 arXiv ID。

    Args:
        html: arXiv listing 页面 HTML

    Returns:
        去重后的 arXiv ID 列表(YYYY.NNNNN 格式)
    """
    ids = re.findall(r'arXiv:(\d{4}\.\d{4,5})', html)
    seen = set()
    return [x for x in ids if not (x in seen or seen.add(x))]


def fetch_arxiv_abs(paper_id: str, timeout: int = 15) -> dict:
    """拉取 arXiv abs 页面的 title/abstract/authors/v1_date。

    Args:
        paper_id: arXiv ID(如 '2609.14205')
        timeout: 总超时秒数

    Returns:
        dict 含 title/abstract/authors/primary_cat/v1_date,失败抛 RuntimeError
    """
    url = f'https://arxiv.org/abs/{paper_id}'
    html = fetch_arxiv_listing(url, timeout=timeout)
    m_t = re.search(r'<h1 class="title[^"]*">\s*<span[^>]*>Title:</span>\s*(.*?)</h1>', html, re.DOTALL)
    m_a = re.search(r'<blockquote class="abstract[^"]*">(.*?)</blockquote>', html, re.DOTALL)
    m_au = re.search(r'<div class="authors">\s*<span[^>]*>Authors:</span>\s*(.*?)</div>', html, re.DOTALL)
    m_dt = re.search(r'<div class="submission-history">.*?<strong>\[v1\]</strong>\s*(.*?)</div>', html, re.DOTALL)
    m_cat = re.search(r'<span class="primary-subject">([^<]+)</span>', html)

    def clean(m):
        if not m: return ''
        return ' '.join(re.sub(r'<[^>]+>', ' ', m.group(1)).split())

    return {
        'id': paper_id,
        'title': clean(m_t),
        'abstract': clean(m_a),
        'authors': clean(m_au),
        'v1_date': clean(m_dt),
        'primary_cat': clean(m_cat),
    }


def scan_qfin_recent(pages: int = 3, page_size: int = 25) -> list[str]:
    """扫 q-fin/recent 前 N 页所有 arXiv ID(SSL bypass 协议)。

    Args:
        pages: 翻几页(每页 25 个)
        page_size: 每页大小

    Returns:
        去重 arXiv ID 列表
    """
    all_ids = []
    for skip in range(0, pages * page_size, page_size):
        url = f'https://arxiv.org/list/q-fin/recent?skip={skip}&show={page_size}'
        try:
            html = fetch_arxiv_listing(url)
            ids = extract_arxiv_ids(html)
            all_ids.extend(ids)
            print(f'skip={skip}: {len(ids)} IDs', file=sys.stderr)
        except RuntimeError as e:
            print(f'skip={skip}: FAIL {e}', file=sys.stderr)
    return list(dict.fromkeys(all_ids))


if __name__ == '__main__':
    import json
    ids = scan_qfin_recent(pages=3)
    print(f'\nTotal unique: {len(ids)}')
    print(json.dumps(ids[:10], indent=2))
