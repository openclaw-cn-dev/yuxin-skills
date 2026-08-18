#!/usr/bin/env python3
"""增量检测脚本：数据源无更新则静默（exit 0 无输出），有更新则输出提示。
用于调研任务的第一步，避免盲目调研烧 token。

用法:
  python3 incremental_check.py <任务名> arxiv "<arXiv 查询词>"
  python3 incremental_check.py <任务名> rss "<RSS URL>"

状态文件: ~/.hermes/state/incremental/<任务名>.json
"""
import sys, os, json, re, urllib.request, urllib.parse
from datetime import datetime

STATE_DIR = os.path.expanduser('~/.hermes/state/incremental')


def get_arxiv_latest(query):
    url = ('http://export.arxiv.org/api/query?search_query='
           + urllib.parse.quote(query)
           + '&sortBy=submittedDate&sortOrder=descending&max_results=1')
    data = urllib.request.urlopen(url, timeout=30).read().decode('utf-8', errors='ignore')
    m = re.search(r'<published>([^<]+)</published>', data)
    return m.group(1) if m else None


def get_rss_latest(url):
    data = urllib.request.urlopen(url, timeout=30).read().decode('utf-8', errors='ignore')
    m = re.search(r'<pubDate>([^<]+)</pubDate>|<published>([^<]+)</published>', data)
    if m:
        return m.group(1) or m.group(2)
    return None


def main():
    if len(sys.argv) < 3:
        print('用法: incremental_check.py <任务名> <arxiv|rss> <查询词或URL>', file=sys.stderr)
        sys.exit(2)
    task = sys.argv[1]
    kind = sys.argv[2]
    source = sys.argv[3] if len(sys.argv) > 3 else ''

    # 查最新内容时间戳
    try:
        if kind == 'arxiv':
            latest = get_arxiv_latest(source)
        elif kind == 'rss':
            latest = get_rss_latest(source)
        else:
            latest = None
    except Exception:
        # 网络失败等：静默（避免误报触发无意义调研）
        sys.exit(0)

    if not latest:
        sys.exit(0)

    os.makedirs(STATE_DIR, exist_ok=True)
    state_file = os.path.join(STATE_DIR, f'{task}.json')

    prev = None
    if os.path.exists(state_file):
        try:
            prev = json.load(open(state_file)).get('latest')
        except Exception:
            prev = None

    if latest == prev:
        # 无更新 → 静默
        sys.exit(0)

    # 有更新 → 记录 + 输出提示
    json.dump({'latest': latest, 'checked': datetime.now().isoformat()},
              open(state_file, 'w'))
    print(f'🆕 {task} 有新内容（{latest}）')


if __name__ == '__main__':
    main()
