# -*- coding: utf-8 -*-
"""feishu_docx_writer.py — write structured content to a 飞书 docx via the blocks API.

The ONLY working path is:
    POST /open-apis/docx/v1/documents/{doc_id}/blocks/{doc_id}/children
(document_id IS the page block_id; index=-1 appends.)

Usage as a module:
    from feishu_docx_writer import create_doc, append_markdownish

    doc_id = create_doc(token, "My title")
    append_markdownish(token, doc_id, [
        ("h1", "Top heading"),
        ("p",  "Some paragraph."),
        ("bullet", "Item 1"),
        ("callout", "Important note", "🎯"),
    ])

Usage as a CLI:
    python feishu_docx_writer.py <token_cache.json> <title>
    (then type lines, prefix: h1: h2: h3: p: bullet: callout:)
"""
import urllib.request, json, ssl, sys, time


def _call(token, method, path, payload=None, timeout=30):
    url = f"https://open.feishu.cn{path}"
    body = None
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json; charset=utf-8",
    }
    if payload is not None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(url, data=body, method=method, headers=headers)
    ctx = ssl.create_default_context()
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=timeout) as r:
            return json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return {"code": e.code, "msg": e.read().decode("utf-8")}


def create_doc(token, title):
    """Create a new docx. Returns the document_id (also the page block_id)."""
    res = _call(token, "POST", "/open-apis/docx/v1/documents",
                {"title": title})
    if res.get("code") != 0:
        raise RuntimeError(f"create_doc failed: {res}")
    doc_id = res["data"]["document"]["document_id"]
    return doc_id


def _make_block(kind, text, emoji=None):
    """Build a single block dict for the blocks API."""
    if kind == "p":
        return {"block_type": 2,
                "text": {"elements": [{"type": "text_run",
                            "text_run": {"content": text}}]}}
    if kind == "h1":
        return {"block_type": 3,
                "heading1": {"elements": [{"type": "text_run",
                             "text_run": {"content": text}}]}}
    if kind == "h2":
        return {"block_type": 4,
                "heading2": {"elements": [{"type": "text_run",
                             "text_run": {"content": text}}]}}
    if kind == "h3":
        return {"block_type": 5,
                "heading3": {"elements": [{"type": "text_run",
                             "text_run": {"content": text}}]}}
    if kind == "bullet":
        return {"block_type": 12,
                "bullet": {"elements": [{"type": "text_run",
                            "text_run": {"content": text}}]}}
    if kind == "callout":
        return {"block_type": 19,
                "callout": {"elements": [{"type": "text_run",
                             "text_run": {"content": text}}],
                            "emoji": emoji or "💡"}}
    raise ValueError(f"unknown kind: {kind}")


def append_blocks(token, doc_id, blocks, batch_size=30, sleep=0.3):
    """Append an iterable of block dicts in batches. Returns count written."""
    blocks = list(blocks)
    written = 0
    for i in range(0, len(blocks), batch_size):
        batch = blocks[i:i + batch_size]
        path = f"/open-apis/docx/v1/documents/{doc_id}/blocks/{doc_id}/children"
        res = _call(token, "POST", path, {"children": batch, "index": -1})
        if res.get("code") != 0:
            raise RuntimeError(f"append failed at batch {i}: {res}")
        n = len(res.get("data", {}).get("children", []))
        written += n
        time.sleep(sleep)
    return written


def append_markdownish(token, doc_id, items):
    """Append a list of (kind, text[, emoji]) tuples.

    kind in {"p", "h1", "h2", "h3", "bullet", "callout"}
    """
    blocks = [_make_block(*it) for it in items]
    return append_blocks(token, doc_id, blocks)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python feishu_docx_writer.py <token_cache.json> <title>")
        sys.exit(1)
    with open(sys.argv[1], "r", encoding="utf-8") as f:
        token = json.load(f)["tenant_access_token"]
    title = sys.argv[2]
    doc_id = create_doc(token, title)
    print(f"Created doc: https://feishu.cn/docx/{doc_id}")
    print("Now type lines. Prefix with: h1: h2: h3: p: bullet: callout:")
    print("Empty line to finish.")
    items = []
    while True:
        try:
            line = input()
        except EOFError:
            break
        if not line.strip():
            break
        if ":" not in line:
            kind, text = "p", line
        else:
            prefix, text = line.split(":", 1)
            kind = prefix.strip()
        items.append((kind, text.strip()))
    if items:
        n = append_markdownish(token, doc_id, items)
        print(f"Wrote {n} blocks.")
