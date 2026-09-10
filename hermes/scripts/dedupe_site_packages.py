#!/usr/bin/env python3
"""Profile site-packages 硬链接去重 — 只合并逐字节相同的文件，语义零风险."""
import hashlib
import os
import shutil
import sys
from collections import defaultdict

BASE = "/Users/hua/.hermes/profiles"
PROFILES = ["zhenglishi", "maodou", "quant", "heidou"]
# 以第一个有此文件的 profile 为基准，其余与基准比对
ORDER = ["zhenglishi", "maodou", "quant", "heidou"]

SP = "home/Library/Python/3.9/lib/python/site-packages"


def md5(path):
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    # 1. 收集四个 profile 的所有相对路径 -> 绝对路径列表
    path_map = defaultdict(list)
    for p in PROFILES:
        root = f"{BASE}/{p}/{SP}"
        if not os.path.isdir(root):
            print(f"[跳过] {root} 不存在")
            continue
        for dirpath, dirnames, filenames in os.walk(root):
            for fn in filenames:
                full = os.path.join(dirpath, fn)
                if os.path.islink(full):
                    continue
                rel = os.path.relpath(full, f"{BASE}/{p}")
                path_map[rel].append(full)

    print(f"共 {len(path_map)} 个相对路径，其中多副本: "
          f"{sum(1 for v in path_map.values() if len(v) > 1)}")

    saved = 0
    linked = 0
    skipped_diff = 0
    for rel, paths in path_map.items():
        if len(paths) < 2:
            continue
        # 按ORDER排序，第一个存在的为基准
        paths.sort(key=lambda x: ORDER.index(x.split("/")[4]) if x.split("/")[4] in ORDER else 99)
        base_path = paths[0]
        base_size = os.path.getsize(base_path)
        # 只对大文件做(>64KB，小文件省不了多少)
        if base_size < 65536:
            continue
        try:
            base_md5 = md5(base_path)
        except OSError:
            continue
        for cand in paths[1:]:
            if not os.path.exists(cand):
                continue
            if os.path.getsize(cand) != base_size:
                skipped_diff += 1
                continue
            # 快速预检: inode已相同
            if os.path.samefile(base_path, cand):
                continue
            try:
                if md5(cand) != base_md5:
                    skipped_diff += 1
                    continue
                # 内容相同 -> 原子替换为硬链接
                tmp = cand + ".hl_tmp"
                os.link(base_path, tmp)
                os.replace(tmp, cand)
                saved += base_size
                linked += 1
            except OSError as e:
                print(f"[错误] {cand}: {e}", file=sys.stderr)
    print(f"硬链接 {linked} 个文件，节省 {saved/1073741824:.2f} GB，"
          f"内容不同跳过 {skipped_diff} 个")


if __name__ == "__main__":
    main()
