#!/usr/bin/env python3
"""
staging_query.py — 渔芯 Agent 统一资料查询工具
=================================================
所有 agent **调用资料时统一从 RKR API 读**（不走文件系统）。

RKR 后端默认监听 :8000，提供两类入口：

1. 文档库（已入库文档）
   GET /api/v1/library/stats                  - 各 libType 概况
   GET /api/v1/library/{libType}?page=1       - 列出文档
   GET /api/v1/projects/{id}/documents        - 按项目列文档

2. 知识检索（语义搜索 + 关键词）
   POST /api/v1/search/query                  - 全文 + 向量混合检索
   GET  /api/v1/library/{libType}?search=...  - 按 libType 关键词搜

认证：JWT（用 admin/RKR 账号登录拿 token）
       或  X-API-Key（用于外部 agent）

用法：
    # 1. 列出"知识文库"前 20 个
    python3 ~/.hermes/scripts/staging_query.py list --lib knowledge --limit 20

    # 2. 搜文档
    python3 ~/.hermes/scripts/staging_query.py search \
        --query "养殖池 循环水" --lib knowledge --limit 10

    # 3. 拉所有项目
    python3 ~/.hermes/scripts/staging_query.py projects
"""

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Optional

# ── 全局配置 ──────────────────────────────────────────────
RKR_BASE = os.environ.get("RKR_BASE", "http://localhost:8000")
RKR_EMAIL = os.environ.get("RKR_EMAIL", "admin@rkr-platform.com")
RKR_PASSWORD = os.environ.get("RKR_PASSWORD", "Admin@2026!rkr")
TOKEN_CACHE = Path(os.path.expanduser("~/.hermes/.rkr_token"))


def _http(method: str, path: str, data: Optional[dict] = None,
          token: Optional[str] = None, timeout: int = 30) -> dict:
    """统一 HTTP 调用。"""
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(
        f"{RKR_BASE}{path}", data=body, method=method, headers=headers,
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        try:
            err_body = json.loads(e.read().decode())
        except Exception:
            err_body = {"error": str(e)}
        return {"error": err_body, "status": e.code}


def get_token() -> str:
    """登录拿 token（带缓存）。"""
    if TOKEN_CACHE.exists():
        cached = TOKEN_CACHE.read_text().strip()
        if cached:
            return cached

    resp = _http("POST", "/api/v1/auth/login", {
        "email": RKR_EMAIL, "password": RKR_PASSWORD,
    })
    token = resp.get("access_token", "")
    if not token:
        print(f"❌ 登录失败: {resp}", file=sys.stderr)
        sys.exit(1)
    TOKEN_CACHE.parent.mkdir(parents=True, exist_ok=True)
    TOKEN_CACHE.write_text(token)
    return token


# ── 命令 1: list 列出文档 ──────────────────────────────────
def cmd_list(args):
    token = get_token()
    params = {"page": args.page, "page_size": args.limit}
    if args.search:
        params["search"] = args.search
    qs = urllib.parse.urlencode(params)
    data = _http("GET", f"/api/v1/library/{args.lib}?{qs}", token=token)
    docs = data.get("documents", [])
    total = data.get("total", 0)
    print(f"📚 libType={args.lib} | total={total} | showing {len(docs)}")
    for d in docs:
        title = d.get("title") or d.get("filename", "?")
        print(f"  [{d.get('id','')[:8]}] {title[:80]}")
    return data


# ── 命令 2: search 关键词搜 ──────────────────────────────
def cmd_search(args):
    """search 复用 list 端点（GET /api/v1/library/{libType}?search=...）"""
    token = get_token()
    params = {"page": 1, "page_size": args.limit, "search": args.query}
    qs = urllib.parse.urlencode(params)
    data = _http("GET", f"/api/v1/library/{args.lib}?{qs}", token=token)
    docs = data.get("documents", [])
    print(f"🔍 query={args.query!r} | lib={args.lib} | {len(docs)} hits")
    for d in docs[:args.limit]:
        title = d.get("title") or d.get("filename", "?")
        print(f"  [{d.get('id','')[:8]}] {title[:80]}")
    return data


# ── 命令 3: projects 列出项目 ──────────────────────────────
def cmd_projects(args):
    token = get_token()
    data = _http("GET", f"/api/v1/projects?limit={args.limit}", token=token)
    projects = data.get("projects", [])
    print(f"📂 总项目数: {data.get('total', '?')}")
    for p in projects:
        name = p.get("name", "?")
        docs = p.get("document_count", "?")
        print(f"  [{p.get('id','')[:8]}] {name:30s} | docs={docs}")
    return data


# ── 命令 4: stats 各 libType 概况 ──────────────────────────
def cmd_stats(args):
    token = get_token()
    data = _http("GET", "/api/v1/library/stats", token=token)
    libs = data.get("libraries", [])
    for lib in libs:
        n = lib.get("count", 0)
        size_mb = (lib.get("size_bytes", 0) or 0) / 1024 / 1024
        print(f"  {lib.get('name','?'):20s} | {n:>6} 文档 | {size_mb:.1f} MB")
    return data


# ── 主入口 ──────────────────────────────────────────────
def main():
    p = argparse.ArgumentParser(
        description="渔芯 Agent 统一资料查询工具（从 RKR API 读）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    # list
    pl = sub.add_parser("list", help="列出某 libType 的文档")
    pl.add_argument("--lib", default="knowledge", help="libType (默认: knowledge)")
    pl.add_argument("--limit", type=int, default=20)
    pl.add_argument("--page", type=int, default=1)
    pl.add_argument("--search", help="关键词过滤")
    pl.set_defaults(func=cmd_list)

    # search
    ps = sub.add_parser("search", help="语义搜索")
    ps.add_argument("--query", "-q", required=True)
    ps.add_argument("--lib", default="knowledge")
    ps.add_argument("--limit", type=int, default=10)
    ps.set_defaults(func=cmd_search)

    # projects
    pp = sub.add_parser("projects", help="列出所有项目")
    pp.add_argument("--limit", type=int, default=50)
    pp.set_defaults(func=cmd_projects)

    # stats
    pst = sub.add_parser("stats", help="文档库总览")
    pst.set_defaults(func=cmd_stats)

    args = p.parse_args()
    data = args.func(args)
    if args.cmd in ("search", "list") and args.query if hasattr(args, "query") else False:
        pass
    if not sys.stdout.isatty():
        print(json.dumps(data, ensure_ascii=False, indent=2)[:2000])


if __name__ == "__main__":
    main()
