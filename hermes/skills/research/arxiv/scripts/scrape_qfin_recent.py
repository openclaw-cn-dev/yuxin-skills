#!/usr/bin/env python3
"""Scrape arXiv q-fin/recent listings via HTML (browser-free fallback).

Use this when:
- arXiv API is rate-limited (429) or returns empty (search_query returns 0 for many q-fin terms)
- browser_navigate is unavailable (cron mode)
- You need to enumerate ALL papers in a date range, not just search matches

Usage:
    python scrape_qfin_recent.py                      # default: 100 most recent across all q-fin
    python scrape_qfin_recent.py --days Fri           # only "Fri, 28 Aug 2026" section
    python scrape_qfin_recent.py --show 50            # fetch 50 per page
    python scrape_qfin_recent.py --raw                # dump full chunk HTML to /tmp

Output: list of (arxiv_id, title, subjects) tuples, one block per paper.

Verified 2026-08-28 (#109 宽博士 heartbeat): 20 entries in Fri 28 Aug 2026 chunk extracted
in <1 second, zero browser dependency, zero API quota.

Pitfalls (踩坑):
- arxiv.org/list/q-fin/recent renders 50 entries per page; use ?show=100 to grab all in one shot
- The "Fri, 28 Aug 2026" string appears TWICE on the page: once in the nav-jump list, once in the
  actual <h3> heading. You must match the <h3>Heading</h3> pattern, not the nav link
- Title lives in <div class='list-title mathjax'><span class='descriptor'>Title:</span> TITLE </div>
- Primary subject lives in <span class="primary-subject">SUBJ</span>
- Fallback subject extraction: pattern `class="primary-subject">([^<]+)</span>`
- Date chunk boundaries: find the next <h3> after the start of the section you're keeping
"""
import sys
import re
import urllib.request


def fetch_chunk(target_date_label=None, show=100):
    """Fetch q-fin/recent HTML and return chunk for target_date_label.

    If target_date_label is None, returns the first day's chunk (most recent).
    target_date_label example: 'Fri, 28 Aug 2026'
    """
    url = f"https://arxiv.org/list/q-fin/recent?skip=0&show={show}"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=30) as resp:
        html = resp.read().decode('utf-8', errors='ignore')

    if target_date_label is None:
        # Find first <h3> heading (which is the most recent day)
        m = re.search(r'<h3>([^<]+)</h3>', html)
        if not m:
            return "", ""
        target_date_label = m.group(1).split(' (')[0]  # strip " (showing 20 of 20)"

    start_match = re.search(r'<h3>(' + re.escape(target_date_label) + r'[^<]+)</h3>', html)
    if not start_match:
        return "", target_date_label
    start = start_match.start()
    rest = html[start + 1:]
    next_h3 = re.search(r'<h3>', rest)
    end = start + 1 + next_h3.start() if next_h3 else len(html)
    return html[start:end], target_date_label


def parse_papers(chunk):
    """Parse papers from a date-bounded HTML chunk.

    Returns list of dicts: {arxiv_id, title, subjects, comments}.
    """
    paper_pattern = re.compile(r'<dt>(.*?)</dt>\s*<dd>(.*?)</dd>', re.DOTALL)
    papers = []
    for dt, dd in paper_pattern.findall(chunk):
        id_m = re.search(r'arXiv:(\d{4}\.\d{4,5})', dt)
        if not id_m:
            continue
        arxiv_id = id_m.group(1)
        # Title: <div class='list-title mathjax'><span class='descriptor'>Title:</span> TITLE </div>
        title_m = re.search(
            r'class=\'list-title[^\']*\'>\s*<span[^>]*>Title:</span>\s*(.*?)\s*</div>',
            dd, re.DOTALL)
        title = ""
        if title_m:
            title = re.sub(r'<[^>]+>', '', title_m.group(1)).strip()
            title = re.sub(r'\s+', ' ', title)
        # Primary subject
        subj_m = re.search(r'class="primary-subject">([^<]+)</span>', dd)
        subjects = subj_m.group(1).strip() if subj_m else ""
        # Optional: comments
        comm_m = re.search(r'<span class="descriptor">Comments:</span>\s*(.*?)</div>', dd, re.DOTALL)
        comments = ""
        if comm_m:
            comments = re.sub(r'<[^>]+>', '', comm_m.group(1)).strip()
            comments = re.sub(r'\s+', ' ', comments)
        papers.append({
            'arxiv_id': arxiv_id,
            'title': title or '?',
            'subjects': subjects,
            'comments': comments,
        })
    return papers


def main():
    args = sys.argv[1:]
    target_date = None
    show = 100
    dump_raw = False
    i = 0
    while i < len(args):
        if args[i] == '--days' and i + 1 < len(args):
            target_date = args[i + 1]; i += 2
        elif args[i] == '--show' and i + 1 < len(args):
            show = int(args[i + 1]); i += 2
        elif args[i] == '--raw':
            dump_raw = True; i += 1
        else:
            i += 1

    chunk, label = fetch_chunk(target_date_label=target_date, show=show)
    if dump_raw:
        print(chunk)
        return
    papers = parse_papers(chunk)
    print(f"=== arXiv q-fin/recent — {label} ({len(papers)} entries) ===\n")
    for p in papers:
        print(f"{p['arxiv_id']}: {p['title']}")
        print(f"  Subjects: {p['subjects']}")
        if p['comments']:
            print(f"  Comments: {p['comments'][:120]}")
        print()


if __name__ == '__main__':
    main()