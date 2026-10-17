#!/usr/bin/env python3
"""ollama blobs 审计 / 修复 / 安全清理 三合一。

背景（2026-09-10 事故）：按 layers-only 判定孤儿会误删 config blob，
导致全部模型 not found。本脚本三模式的判定都把 config 算进"被引用集合"。

用法：
  python3 ollama_blob_audit_repair.py audit   # 体检：每个模型的 config/layers 是否齐
  python3 ollama_blob_audit_repair.py repair  # 修复：config blob 缺失时重建最小 config + 改写 manifest 指向
  python3 ollama_blob_audit_repair.py clean   # 安全清理：只删「manifest 们完全不再引用」的 blob
                                              #（引用集合 = 所有 manifest 的 config + layers）
先 audit 后再决定 repair / clean。repair 会改写 manifest（含 config.digest/size），
跑之前建议备份 manifests 目录。
"""
import glob
import hashlib
import json
import os
import sys

BASE = os.path.expanduser("~/.ollama/models")
MANIFEST_GLOB = os.path.join(BASE, "manifests", "registry.ollama.ai", "library", "*", "*")
BLOBS = os.path.join(BASE, "blobs")


def norm(digest: str) -> str:
    return digest.replace("sha256:", "").replace("sha256-", "")


def blob_path(digest: str) -> str:
    return os.path.join(BLOBS, f"sha256-{norm(digest)}")


def load_manifests():
    out = []
    for p in sorted(glob.glob(MANIFEST_GLOB)):
        name = p.split("/library/")[1].replace("/", ":")
        try:
            m = json.load(open(p))
        except json.JSONDecodeError as e:
            print(f"  [bad-json] {name}: {e}")
            continue
        out.append((name, p, m))
    return out


def cmd_audit():
    mans = load_manifests()
    problems = 0
    for name, _, m in mans:
        cfg = m.get("config", {})
        ok_cfg = os.path.exists(blob_path(cfg.get("digest", "")))
        missing_layers = [l["digest"] for l in m.get("layers", []) if not os.path.exists(blob_path(l["digest"]))]
        if not ok_cfg or missing_layers:
            problems += 1
            print(f"❌ {name}: config缺={not ok_cfg} layers缺={len(missing_layers)}")
        else:
            print(f"OK {name}")
    print(f"\n{problems} 个模型有问题" if problems else "\n全部健康")


def cmd_repair():
    mans = load_manifests()
    fixed = 0
    for name, path, m in mans:
        cfg = m.get("config", {})
        if os.path.exists(blob_path(cfg.get("digest", ""))):
            continue
        # 最小合法 config（OCI image config 形状）。内容不可伪造原 digest，
        # 所以重建 = 新内容 + 新 digest + 改写 manifest 指向。
        body = json.dumps(
            {"architecture": "amd64", "os": "linux", "rootfs": {"type": "layers", "diff_ids": []}},
            separators=(",", ":"),
        ).encode()
        digest = "sha256:" + hashlib.sha256(body).hexdigest()
        with open(blob_path(digest), "wb") as f:
            f.write(body)
        m["config"] = {
            "mediaType": "application/vnd.docker.container.image.v1+json",
            "digest": digest,
            "size": len(body),
        }
        with open(path, "w") as f:
            json.dump(m, f)
        fixed += 1
        print(f"🔧 已修复 {name} → {digest[:20]}…")
    print(f"\n共修复 {fixed} 个。跑一次 `ollama list` 或 /api/tags 验证可见性。")


def cmd_clean():
    mans = load_manifests()
    referenced = set()
    for _, _, m in mans:
        referenced.add(norm(m["config"]["digest"]))  # 关键：config 也算引用
        for l in m.get("layers", []):
            referenced.add(norm(l["digest"]))
    removed = freed = 0
    for p in glob.glob(os.path.join(BLOBS, "sha256-*")):
        if norm(os.path.basename(p)) not in referenced:
            size = os.path.getsize(p)
            os.remove(p)
            removed += 1
            freed += size
    print(f"已删 {removed} 个孤儿 blob，回收 {freed / 1e9:.1f}G")
    cmd_audit()  # 清完立刻体检，确保没有模型失明


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    {"audit": cmd_audit, "repair": cmd_repair, "clean": cmd_clean}.get(mode, lambda: print("用法: audit|repair|clean"))()
