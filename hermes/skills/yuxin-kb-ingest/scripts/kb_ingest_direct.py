#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""直连 HTTP 写渔芯知识库（MCP kb_ingest 工具未加载时的兜底）。

用法：
  python3 kb_ingest_direct.py <file.md> <domain> [title]
  # domain ∈ aqua/eng/ai/life；title 缺省用文件名（截 300 字）

鉴权：KB_ADMIN_TOKEN（/Users/hua/.hermes/.env 的 KB_ADMIN_TOKEN= 行）。
与 ~/.hermes/scripts/kb_auto_sync.py 的 ingest() 打同一生产库。
成功返回 {"ok":true,"doc_id":"d_...","duplicate":false,"chunks":N,"embedded":true}。
"""
import json, os, sys, urllib.request, urllib.error

API = "https://lookforge.net/v1/admin/ingest"
ENV = "/Users/hua/.hermes/.env"


def load_token():
    try:
        with open(ENV, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith("KB_ADMIN_TOKEN="):
                    return line.split("=", 1)[1].strip().strip('"').strip("'")
    except OSError:
        return ""
    return ""


def main():
    if len(sys.argv) < 3:
        print("用法: kb_ingest_direct.py <file.md> <domain> [title]")
        sys.exit(2)
    path, domain = sys.argv[1], sys.argv[2]
    title = sys.argv[3] if len(sys.argv) > 3 else os.path.splitext(os.path.basename(path))[0][:300]
    token = load_token()
    if not token:
        print("✗ KB_ADMIN_TOKEN 缺失（/Users/hua/.hermes/.env）")
        sys.exit(1)
    with open(path, encoding="utf-8") as f:
        content = f.read()
    payload = {"title": title, "content": content, "domain": domain}
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(API, data=data, method="POST", headers={
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": "Bearer " + token,
    })
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            print(resp.read().decode("utf-8", "replace"))
    except urllib.error.HTTPError as e:
        print("HTTP", e.code, e.read().decode("utf-8", "replace"))
        sys.exit(1)
    except Exception as e:  # noqa: BLE001
        print("ERR", repr(e))
        sys.exit(1)


if __name__ == "__main__":
    main()
