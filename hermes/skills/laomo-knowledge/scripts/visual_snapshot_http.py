# -*- coding: utf-8 -*-
"""
visual_snapshot_http.py — 轻量视觉回归冒烟探针 (v1.88.76 R746 落库, stdlib 零依赖)

用法:
    python3 visual_snapshot_http.py baseline <url>               # 存基线 (默认 /tmp/visual_baseline.json)
    python3 visual_snapshot_http.py compare  <url>               # 对比基线 (PASS=exit 0 / DRIFT=exit 1)
    python3 visual_snapshot_http.py baseline <url> <path.json>   # 自定义基线路径

原理: 剥离 <script>/<style> 后取文本级 DOM 快照 + 结构特征 (title / 资源引用数 / 文本长度)
做 hash 基线比对。字段: status / title / n_resources / text_hash / text_len。
适合 cron 冒烟与 SPA 部署后基线比对。

局限: 文本 hash 对纯 CSS 视觉变化不敏感; 像素级回归需 Playwright 截图叠加
(环境有 playwright 时可升级)。

R746 实证 (:8006 渔芯·DevPlan):
    baseline -> compare PASS (hash 480db0b6097f95b9)
    本地篡改服务重放 -> DETECTED DRIFT (title/n_resources/text_hash/text_len 4 字段全检出)
"""
import hashlib
import json
import re
import sys
from urllib.request import Request, urlopen

DEFAULT_BASELINE = '/tmp/visual_baseline.json'


def snapshot(url, timeout=10):
    """抓取 URL 并生成文本级 DOM 快照特征 dict。"""
    req = Request(url, headers={'User-Agent': 'laomo-visual-regression/1.0'})
    with urlopen(req, timeout=timeout) as resp:
        html = resp.read().decode('utf-8', errors='replace')
        status = resp.status
    text = re.sub(r'<(script|style)[^>]*>.*?</\1>', ' ', html, flags=re.S | re.I)
    text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    titles = re.findall(r'<title[^>]*>(.*?)</title>', html, flags=re.S | re.I)
    n_links = len(re.findall(r'<(?:script|link|img)\b', html, flags=re.I))
    return {
        'url': url,
        'status': status,
        'title': titles[0].strip() if titles else '',
        'n_resources': n_links,
        'text_hash': hashlib.sha256(text.encode()).hexdigest()[:16],
        'text_len': len(text),
    }


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        raise SystemExit(2)
    mode, url = sys.argv[1], sys.argv[2]
    baseline_path = sys.argv[3] if len(sys.argv) > 3 else DEFAULT_BASELINE
    snap = snapshot(url)
    print('[%s] %s' % (mode, url))
    print('  status=%s title="%s" text_len=%s resources=%s'
          % (snap['status'], snap['title'][:60], snap['text_len'], snap['n_resources']))
    print('  text_hash=%s' % snap['text_hash'])
    if mode == 'baseline':
        with open(baseline_path, 'w') as f:
            json.dump(snap, f, ensure_ascii=False, indent=1)
        print('  baseline saved -> %s' % baseline_path)
    canonical = (mode == 'compare')
    if canonical:
        with open(baseline_path) as f:
            base = json.load(f)
        keys = ('status', 'title', 'n_resources', 'text_hash', 'text_len')
        diffs = [k for k in keys if base.get(k) != snap.get(k)]
        if not diffs:
            print('  RESULT: PASS — 快照与基线一致 (零视觉回归信号)')
        else:
            print('  RESULT: DRIFT — 变化字段: %s' % diffs)
            for k in diffs:
                print('    %s: %s -> %s' % (k, base.get(k), snap.get(k)))
        raise SystemExit(1 if diffs else 0)


if __name__ == '__main__':
    main()
