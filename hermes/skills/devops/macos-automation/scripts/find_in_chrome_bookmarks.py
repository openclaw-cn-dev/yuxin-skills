#!/usr/bin/env python3
"""在 Chrome 书签里按关键词查找条目，输出 name / url / 收藏时间。

用途：找回"以前放在哪"的本地文件——用户收藏过某个 file:// 文件时，
书签里留有原始路径，即使文件已删除/移动也能追溯。

用法:
    python3 find_in_chrome_bookmarks.py "配色"          # 搜含"配色"的书签
    python3 find_in_chrome_bookmarks.py                 # 列出全部书签

遍历 ~/Library/Application Support/Google/Chrome/ 下所有 Profile 的 Bookmarks。
- 自动解码 file:// URL 里的中文百分号编码
- date_added 换算成本地时间（Chrome 用 1601-01-01 起的微秒数）
"""
import sys
import json
import glob
import os
import datetime
from urllib.parse import unquote


def walk_bookmarks(node, kw, path=""):
    """递归遍历书签树，yield (path, name, url, date_str)。"""
    if isinstance(node, dict):
        name = node.get("name", "")
        url = node.get("url", "")
        if kw in name or kw in url:
            da = node.get("date_added", 0)
            try:
                ts = int(da) / 1e6 - 11644473600  # 1601 纪元偏移
                dt = datetime.datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")
            except Exception:
                dt = str(da)
            yield path, name, unquote(url), dt
        for v in node.values():
            if isinstance(v, (dict, list)):
                yield from walk_bookmarks(v, kw, path + "/" + name if name else path)
    elif isinstance(node, list):
        for item in node:
            yield from walk_bookmarks(item, kw, path)


def main():
    kw = sys.argv[1] if len(sys.argv) > 1 else ""
    base = os.path.expanduser("~/Library/Application Support/Google/Chrome")
    files = sorted(glob.glob(os.path.join(base, "Profile *", "Bookmarks")))
    files += sorted(glob.glob(os.path.join(base, "Bookmarks")))
    if not files:
        print("未找到 Chrome Bookmarks 文件", file=sys.stderr)
        sys.exit(1)

    seen = 0
    for f in files:
        try:
            data = json.load(open(f, encoding="utf-8"))
        except Exception as e:
            print(f"[跳过] {f}: {e}", file=sys.stderr)
            continue
        profile = os.path.basename(os.path.dirname(f))
        for path, name, url, dt in walk_bookmarks(data.get("roots", {}), kw):
            print(f"[{profile}] 路径: {path}")
            print(f"  NAME: {name}")
            print(f"  URL : {url}")
            print(f"  收藏时间: {dt}")
            print("  ---")
            seen += 1

    if seen == 0:
        print(f'未找到含 "{kw}" 的书签')


if __name__ == "__main__":
    main()
