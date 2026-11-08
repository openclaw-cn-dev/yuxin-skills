#!/usr/bin/env python3
"""ollama blob 占用审计：算出"未保留模型"独占的可回收字节数。

用法:
  python3 ollama_blob_audit.py                      # 列出全部 manifest 与独占 blob
  python3 ollama_blob_audit.py --keep 'yuxin-eng-.*' --keep 'qwen3'   # 只把这些当保留集

原理: blob 文件名是 sha256-<hex>，manifest 里 layer digest 写 sha256:<hex>，
必须归一化（去掉两种前缀）后比对，否则全部误判为"未被引用"（2026-09-10 踩坑）。
删除请用 `ollama rm <模型名>`，不要手删 blob 文件。
"""
import argparse, glob, json, os, sys

BASE = os.path.expanduser("~/.ollama/models")

def norm(d: str) -> str:
    return d.replace("sha256:", "").replace("sha256-", "")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--keep", action="append", default=[],
                    help="保留的模型名正则（可多次）")
    args = ap.parse_args()

    import re
    keep_res = [re.compile(p) for p in args.keep]

    manifests = glob.glob(f"{BASE}/manifests/registry.ollama.ai/library/*/*")
    if not manifests:
        sys.exit(f"no manifests under {BASE}")

    keep_digests, total, orphan = set(), 0, 0
    for p in manifests:
        name, tag = p[len(f"{BASE}/manifests/registry.ollama.ai/library/"):].rsplit("/", 1)
        if keep_res and any(r.fullmatch(name) for r in keep_res):
            for l in json.load(open(p))["layers"]:
                keep_digests.add(norm(l["digest"]))

    print(f"{'模型':<45}{'大小':>10}")
    for p in sorted(manifests):
        name = p[len(f"{BASE}/manifests/registry.ollama.ai/library/"):].replace("/", ":")
        sz = sum(l.get("size", 0) for l in json.load(open(p))["layers"])
        print(f"{name:<45}{sz/1e9:>8.1f}G")

    for p in glob.glob(f"{BASE}/blobs/sha256-*"):
        sz = os.path.getsize(p); total += sz
        if norm(os.path.basename(p)) not in keep_digests:
            orphan += sz
    print(f"\nblobs 总量: {total/1e9:.1f}G")
    print(f"保留集外独占(可回收): {orphan/1e9:.1f}G  ← 用 `ollama rm <模型>` 删对应模型")

if __name__ == "__main__":
    main()
