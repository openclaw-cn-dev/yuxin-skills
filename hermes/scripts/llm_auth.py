"""网关入站鉴权 + 客户端令牌管理（阶段三 H · M5 配置单点化）。

设计要点
--------
1. **库只存指纹**：``~/.hermes/state/llm_tokens.json``（0600）里只有 sha256 前 16 位，
   明文 token 只在 ``issue`` 时打印一次，之后无法找回——泄漏这个文件不等于泄漏 key。
2. **token 即身份**：拿到 token 就同时知道 client/project，不依赖客户端传
   ``X-LLM-Client``（Codex / Hermes 等无头客户端也能被正确归属）。
3. **三档模式**：
   - ``off``     完全不校验（等价改造前）
   - ``warn``    校验但放行，只计数+记日志（**默认**，灰度期用）
   - ``enforce`` 无 token / 错 token 一律 401
   模式取值：环境变量 ``LLM_GW_AUTH`` > 库内 ``mode`` 字段 > 默认 ``warn``。
4. **失败即降级**：读库异常一律当作 ``off``，不能让鉴权把转发搞挂。

CLI
---
    python3 llm_auth.py issue claude-code --project hive
    python3 llm_auth.py list
    python3 llm_auth.py revoke claude-code
    python3 llm_auth.py mode enforce
    python3 llm_auth.py verify <token>
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import secrets
import sys
import time
from pathlib import Path
from typing import Dict, Optional, Tuple

HERMES_HOME = Path(os.environ.get("HERMES_HOME", str(Path.home() / ".hermes")))
STORE_PATH = Path(os.environ.get(
    "LLM_TOKEN_STORE", HERMES_HOME / "state" / "llm_tokens.json"))

MODES = ("off", "warn", "enforce")
DEFAULT_MODE = "warn"
TOKEN_PREFIX = "yxk_"          # 渔芯 key，便于在配置文件里一眼认出
FINGERPRINT_LEN = 16

# 客户端可能用来放凭据的头（小写）。网关转发前必须全部剥掉，绝不透给上游。
CREDENTIAL_HEADERS = ("authorization", "x-api-key", "x-goog-api-key",
                      "api-key", "x-llm-token")

_cache = {"mtime": None, "data": {"version": 1, "mode": DEFAULT_MODE, "tokens": {}}}


# ─── 存储 ─────────────────────────────────────────────────────

def _empty() -> Dict:
    return {"version": 1, "mode": DEFAULT_MODE, "tokens": {}}


def _load() -> Dict:
    """读令牌库（带 mtime 缓存）。任何异常都返回空库，绝不抛。"""
    try:
        st = STORE_PATH.stat()
        if _cache["mtime"] == st.st_mtime:
            return _cache["data"]
        data = json.loads(STORE_PATH.read_text())
        if not isinstance(data, dict):
            raise ValueError("store root must be an object")
        data.setdefault("version", 1)
        data.setdefault("mode", DEFAULT_MODE)
        data.setdefault("tokens", {})
        if not isinstance(data["tokens"], dict):
            data["tokens"] = {}
        _cache["mtime"] = st.st_mtime
        _cache["data"] = data
        return data
    except FileNotFoundError:
        return _empty()
    except Exception:
        return _empty()


def _save(data: Dict) -> None:
    STORE_PATH.parent.mkdir(parents=True, exist_ok=True)
    tmp = STORE_PATH.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2))
    os.chmod(tmp, 0o600)
    tmp.replace(STORE_PATH)
    try:
        os.chmod(STORE_PATH, 0o600)
    except OSError:
        pass
    _cache["mtime"] = None      # 让下次读到新值


# ─── 令牌与指纹 ───────────────────────────────────────────────

def normalize_token(raw: str) -> str:
    """从 Authorization 头值里取出裸 token（去掉 Bearer 前缀与空白）。"""
    if not raw:
        return ""
    t = raw.strip()
    low = t.lower()
    for p in ("bearer ", "token "):
        if low.startswith(p):
            t = t[len(p):].strip()
            break
    return t


def fingerprint(token: str) -> str:
    """令牌指纹：sha256 前 16 位。库里只存这个，不存明文。"""
    if not token:
        return ""
    return hashlib.sha256(token.encode()).hexdigest()[:FINGERPRINT_LEN]


def extract_token(headers) -> str:
    """从请求头取客户端令牌。依次看 Authorization / x-api-key / x-llm-token。"""
    if headers is None:
        return ""
    try:
        low = {k.lower(): v for k, v in dict(headers).items()}
    except Exception:
        return ""
    for name in ("authorization", "x-api-key", "x-llm-token", "api-key"):
        v = low.get(name)
        if v:
            return normalize_token(v)
    return ""


# ─── 鉴权 ────────────────────────────────────────────────────

def mode() -> str:
    """当前鉴权模式：环境变量 > 库内设置 > 默认 warn。"""
    env = (os.environ.get("LLM_GW_AUTH") or "").strip().lower()
    if env in MODES:
        return env
    m = (_load().get("mode") or "").strip().lower()
    return m if m in MODES else DEFAULT_MODE


def set_mode(m: str) -> str:
    m = (m or "").strip().lower()
    if m not in MODES:
        raise ValueError(f"mode 只能是 {MODES}")
    data = _load()
    data["mode"] = m
    _save(data)
    return m


def verify(headers) -> Dict:
    """校验入站请求。

    返回：``{"status": ok|missing|invalid|off, "client": ..., "project": ...,
             "fingerprint": ..., "mode": ...}``

    - ``off``：不校验，直接放行（client/project 为空，交给上层兜底）
    - ``ok``：令牌有效，client/project 取自令牌库
    - ``missing`` / ``invalid``：由调用方按模式决定放行还是 401
    """
    m = mode()
    out = {"status": "off", "client": "", "project": "",
           "fingerprint": "", "mode": m, "admin": False}
    if m == "off":
        return out

    token = extract_token(headers)
    if not token:
        out["status"] = "missing"
        return out

    fp = fingerprint(token)
    out["fingerprint"] = fp
    rec = _load().get("tokens", {}).get(fp)
    if not rec:
        out["status"] = "invalid"
        return out

    out["status"] = "ok"
    out["client"] = rec.get("client", "")
    out["project"] = rec.get("project", "")
    out["admin"] = bool(rec.get("admin"))
    return out


def should_block(v: Dict) -> bool:
    """enforce 模式下，非 ok/off 一律拦。"""
    return v.get("mode") == "enforce" and v.get("status") in ("missing", "invalid")


def require_admin(headers) -> Dict:
    """管理端点鉴权：**与转发鉴权模式无关**，永远要求 admin 令牌。

    返回 ``{"ok", "reason", "client", "fingerprint"}``。令牌库读不到或异常一律
    不通过 —— 写操作宁可拒绝，不可放行。
    """
    token = extract_token(headers)
    if not token:
        return {"ok": False, "reason": "missing_token", "client": "", "fingerprint": ""}
    fp = fingerprint(token)
    try:
        rec = _load().get("tokens", {}).get(fp)
    except Exception:  # noqa: BLE001
        rec = None
    if not rec:
        return {"ok": False, "reason": "invalid_token", "client": "", "fingerprint": fp}
    if not rec.get("admin"):
        return {"ok": False, "reason": "not_admin",
                "client": rec.get("client", ""), "fingerprint": fp}
    return {"ok": True, "reason": "", "client": rec.get("client", ""),
            "fingerprint": fp}


# ─── 令牌管理 ────────────────────────────────────────────────

def issue(client: str, project: str = "", note: str = "", admin: bool = False) -> str:
    """签发新令牌，返回明文（**只此一次**）。

    ``admin=True`` 签发管理令牌（M6）：可调 ``/admin/*`` 写接口，
    普通客户端令牌一律 403。
    """
    client = (client or "").strip()
    if not client:
        raise ValueError("client 不能为空")
    token = TOKEN_PREFIX + secrets.token_hex(24)
    data = _load()
    rec = {
        "client": client,
        "project": (project or "").strip(),
        "note": (note or "").strip(),
        "created_at": int(time.time()),
    }
    if admin:
        rec["admin"] = True
    data.setdefault("tokens", {})[fingerprint(token)] = rec
    _save(data)
    return token


def revoke(selector: str) -> list:
    """按 client 名或指纹前缀吊销。返回被吊销的指纹列表。"""
    selector = (selector or "").strip()
    data = _load()
    tokens = data.get("tokens", {})
    hit = [fp for fp, rec in tokens.items()
           if fp.startswith(selector) or rec.get("client") == selector]
    for fp in hit:
        tokens.pop(fp, None)
    if hit:
        _save(data)
    return hit


def list_tokens() -> list:
    """列出令牌（已掩码，可按 client 过滤）。"""
    rows = []
    for fp, rec in sorted(_load().get("tokens", {}).items(),
                          key=lambda kv: kv[1].get("created_at", 0)):
        rows.append({
            "fingerprint": fp,
            "client": rec.get("client", ""),
            "project": rec.get("project", ""),
            "note": rec.get("note", ""),
            "admin": bool(rec.get("admin")),
            "created_at": rec.get("created_at", 0),
        })
    return rows


def lookup_by_fingerprint(fp: str) -> Optional[Dict]:
    return _load().get("tokens", {}).get(fp)


# ─── CLI ─────────────────────────────────────────────────────

def _fmt_ts(ts: int) -> str:
    try:
        return time.strftime("%Y-%m-%d %H:%M", time.localtime(int(ts)))
    except Exception:
        return "-"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="渔芯 LLM 网关令牌管理")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p_i = sub.add_parser("issue", help="签发令牌（明文只显示一次）")
    p_i.add_argument("client")
    p_i.add_argument("--project", default="")
    p_i.add_argument("--note", default="")
    p_i.add_argument("--admin", action="store_true",
                     help="管理令牌（可调 /admin/* 写接口）")

    sub.add_parser("list", help="列出令牌（已掩码）")

    p_r = sub.add_parser("revoke", help="按 client 名或指纹前缀吊销")
    p_r.add_argument("selector")

    p_m = sub.add_parser("mode", help="查看/设置鉴权模式")
    p_m.add_argument("value", nargs="?", choices=MODES)

    p_v = sub.add_parser("verify", help="自检：校验一个令牌")
    p_v.add_argument("token")

    args = ap.parse_args(argv)

    if args.cmd == "issue":
        token = issue(args.client, args.project, args.note, admin=args.admin)
        print(f"已签发 client={args.client}"
              f"{' project=' + args.project if args.project else ''}"
              f"{' [ADMIN 管理令牌]' if args.admin else ''}")
        print(f"指纹: {fingerprint(token)}")
        print(f"令牌: {token}")
        print("\n⚠️ 明文只显示这一次，请立刻写入客户端配置；库内只存指纹。")
        return 0

    if args.cmd == "list":
        rows = list_tokens()
        cur = mode()
        print(f"鉴权模式: {cur}    令牌数: {len(rows)}    库: {STORE_PATH}")
        if not rows:
            print("（还没有令牌。用 `llm_auth.py issue <client>` 签发）")
            return 0
        print(f"{'指纹':<18}{'客户端':<16}{'项目':<12}{'签发时间':<18}{'类型':<8}备注")
        for r in rows:
            print(f"{r['fingerprint']:<18}{r['client']:<16}"
                  f"{(r['project'] or '-'):<12}{_fmt_ts(r['created_at']):<18}"
                  f"{'ADMIN' if r['admin'] else '客户端':<8}{r['note'] or ''}")
        return 0

    if args.cmd == "revoke":
        hit = revoke(args.selector)
        if not hit:
            print(f"没有匹配的令牌: {args.selector}")
            return 1
        print(f"已吊销 {len(hit)} 个: {', '.join(hit)}")
        return 0

    if args.cmd == "mode":
        if args.value:
            print(f"鉴权模式已设为: {set_mode(args.value)}")
        else:
            print(f"当前鉴权模式: {mode()}")
            print("  off=不校验  warn=校验但放行(默认)  enforce=无效即 401")
        return 0

    if args.cmd == "verify":
        fp = fingerprint(args.token)
        rec = lookup_by_fingerprint(fp)
        if rec:
            print(f"✅ 有效  指纹={fp}  client={rec.get('client')}  "
                  f"project={rec.get('project') or '-'}")
            return 0
        print(f"❌ 无效  指纹={fp}  （库内无此令牌）")
        return 1

    return 2


if __name__ == "__main__":
    sys.exit(main())
