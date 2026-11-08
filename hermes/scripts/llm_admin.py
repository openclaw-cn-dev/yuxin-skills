"""网关管理 API（阶段三 H · M6-B）。

配合 `llm_gateway.py` 的 ``/admin/*`` 路由：**只做管理面的读写，不碰转发逻辑**。
所有写操作都是原子替换 + 先备份，且必须带 admin 令牌（见 `llm_auth.require_admin`）。

能力
----
    GET  /admin/status          网关/鉴权/预算/熔断/模型池/今日花费
    GET  /admin/budgets         当前预算配置
    PUT  /admin/budgets         部分更新（字段白名单 + 取值校验）
    GET  /admin/guard           熔断状态文件
    POST /admin/guard/resume    解除当期熔断（等价 llm_alert.py --resume）
    GET  /admin/tokens          令牌列表（只含指纹）
    POST /admin/tokens/issue    签发（明文只在响应里出现一次）
    POST /admin/tokens/revoke   按 client 名或指纹前缀吊销
    GET  /admin/audit?limit=50  最近管理动作

审计：每次写操作追加 `~/.hermes/state/admin_audit.jsonl`（0600）。
审计写失败不影响主操作，但会带上 ``audit_error`` 返回。
"""

from __future__ import annotations

import json
import os
import sqlite3
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import llm_auth  # noqa: E402
import llm_alert  # noqa: E402

HERMES_HOME = Path(os.environ.get("HERMES_HOME", str(Path.home() / ".hermes")))
STATE_DIR = Path(os.environ.get("HERMES_STATE_DIR", str(HERMES_HOME / "state")))
CONFIG_PATH = Path(os.environ.get(
    "LLM_METER_CONFIG", str(STATE_DIR / "meter_config.json")))
GUARD_PATH = Path(os.environ.get(
    "LLM_METER_GUARD", str(STATE_DIR / "meter_guard.json")))
METER_DB = Path(os.environ.get(
    "LLM_METER_DB", str(STATE_DIR / "llm_meter.db")))
AUDIT_PATH = Path(os.environ.get(
    "LLM_ADMIN_AUDIT", str(STATE_DIR / "admin_audit.jsonl")))
POOL_STATE = Path(os.environ.get(
    "LLM_POOL_STATE", str(HERMES_HOME / "scripts" / ".model_quota_state.json")))

AUDIT_MAX = 500          # 文件保留上限（行数），超出自动切片
AUDIT_DEFAULT_LIMIT = 50

# 允许通过 API 修改的配置字段（白名单，其余一律忽略并报错）
BUDGET_FIELDS = ("daily_usd", "monthly_usd", "per_client_daily_usd")
LEVEL_FIELDS = ("l1", "l2", "l3")
CHECK_FIELDS = ("budget", "balance", "unpriced", "error_rate")


class AdminError(Exception):
    """带 HTTP 状态码的业务错误。"""

    def __init__(self, message: str, status: int = 400):
        super().__init__(message)
        self.status = status


# ─── 通用读写 ────────────────────────────────────────────────

def _read_json(path: Path, default: Any) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def _write_json(path: Path, data: Any) -> None:
    """原子写 + 0600。失败抛 OSError 由调用方翻译成 500。"""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    try:
        os.chmod(tmp, 0o600)
    except OSError:
        pass
    tmp.replace(path)


def _backup(path: Path) -> Optional[str]:
    """改前留一份带时间戳的副本（同名 .bak-<ts>），返回路径。"""
    if not path.exists():
        return None
    dest = path.with_name(f"{path.name}.bak-{time.strftime('%Y%m%d-%H%M%S')}")
    try:
        dest.write_bytes(path.read_bytes())
        os.chmod(dest, 0o600)
        return str(dest)
    except OSError:
        return None


# ─── 审计 ────────────────────────────────────────────────────

def audit_append(actor: str, fingerprint: str, action: str,
                 target: str = "", result: str = "ok", ip: str = "",
                 detail: Any = None) -> Optional[str]:
    """追加一条审计。返回错误字符串（成功为 None）——绝不抛出。"""
    rec = {
        "ts": int(time.time()),
        "time": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "actor": actor or "",
        "fp": fingerprint or "",
        "action": action,
        "target": target,
        "result": result,
        "ip": ip or "",
    }
    if detail is not None:
        rec["detail"] = detail
    try:
        AUDIT_PATH.parent.mkdir(parents=True, exist_ok=True)
        with AUDIT_PATH.open("a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            f.flush()
            os.fsync(f.fileno())
        try:
            os.chmod(AUDIT_PATH, 0o600)
        except OSError:
            pass
        _trim_audit()
        return None
    except Exception as e:  # noqa: BLE001
        return str(e)


def _trim_audit() -> None:
    """超过 AUDIT_MAX 行时只留最后 AUDIT_MAX 行（低频调用，简单读回即可）。"""
    try:
        if AUDIT_PATH.stat().st_size < 2_000_000:
            return
        lines = AUDIT_PATH.read_text(encoding="utf-8", errors="replace").splitlines()
        if len(lines) <= AUDIT_MAX:
            return
        tmp = AUDIT_PATH.with_suffix(".tmp")
        tmp.write_text("\n".join(lines[-AUDIT_MAX:]) + "\n", encoding="utf-8")
        tmp.replace(AUDIT_PATH)
    except OSError:
        pass


def audit_list(limit: int = AUDIT_DEFAULT_LIMIT) -> List[Dict]:
    """最近 limit 条（新的在前）。文件不存在返回空列表。"""
    limit = max(1, min(int(limit or AUDIT_DEFAULT_LIMIT), 500))
    try:
        lines = AUDIT_PATH.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return []
    out: List[Dict] = []
    for line in reversed(lines[-limit:]):
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return out


# ─── 预算配置 ────────────────────────────────────────────────

def load_config() -> Dict:
    """读预算配置（缺文件用 llm_alert 内置默认值）。"""
    return llm_alert.load_config(CONFIG_PATH if CONFIG_PATH.exists() else None)


def _num(v: Any, name: str, lo: float, hi: float) -> float:
    try:
        f = float(v)
    except (TypeError, ValueError):
        raise AdminError(f"{name} 必须是数字")
    if not (lo <= f <= hi):
        raise AdminError(f"{name} 必须在 [{lo}, {hi}] 之间")
    return f


def update_config(patch: Dict) -> Dict:
    """部分更新预算配置，返回新配置。白名单 + 范围校验，非法即 400。"""
    if not isinstance(patch, dict) or not patch:
        raise AdminError("请求体必须是 JSON 对象")
    cfg = load_config()
    unknown = set(patch) - set(BUDGET_FIELDS) - set(LEVEL_FIELDS) \
        - set(CHECK_FIELDS) - {"alarm_only", "cooldown_hours", "budgets",
                               "levels", "checks"}
    if unknown:
        raise AdminError(f"不支持的字段: {', '.join(sorted(unknown))}")

    budgets = dict(cfg.get("budgets") or {})
    levels = dict(cfg.get("levels") or {})
    checks = dict(cfg.get("checks") or {})

    # 支持扁平（daily_usd）与嵌套（budgets.daily_usd）两种写法
    for src in (patch, patch.get("budgets") or {}):
        for k in BUDGET_FIELDS:
            if k in src:
                budgets[k] = _num(src[k], k, 0.01, 100000)
    for src in (patch, patch.get("levels") or {}):
        for k in LEVEL_FIELDS:
            if k in src:
                levels[k] = _num(src[k], k, 0.05, 1.0)
    for src in (patch, patch.get("checks") or {}):
        for k in CHECK_FIELDS:
            if k in src:
                if not isinstance(src[k], bool):
                    raise AdminError(f"checks.{k} 必须是布尔值")
                checks[k] = src[k]
    if "alarm_only" in patch:
        if not isinstance(patch["alarm_only"], bool):
            raise AdminError("alarm_only 必须是布尔值")
        cfg["alarm_only"] = patch["alarm_only"]
    if "cooldown_hours" in patch:
        cfg["cooldown_hours"] = _num(patch["cooldown_hours"], "cooldown_hours", 0, 168)

    cfg["budgets"] = budgets
    cfg["levels"] = levels
    cfg["checks"] = checks
    backup = _backup(CONFIG_PATH)
    _write_json(CONFIG_PATH, cfg)
    if backup:
        cfg["_backup"] = backup
    return cfg


# ─── 熔断 ────────────────────────────────────────────────────

def guard_state() -> Dict:
    """读熔断状态文件；缺失/损坏按 fail-open 语义返回 enabled=false。"""
    d = _read_json(GUARD_PATH, {})
    if not isinstance(d, dict):
        d = {}
    d.setdefault("enabled", False)
    d.setdefault("blocks", [])
    return d


def resume(keys: Optional[List[str]] = None) -> Dict:
    """解除当期熔断并立刻刷新 meter_guard.json。

    与 `llm_alert.py --resume` 完全同一条路径：把命中的块记进 state["resumed"]，
    再用剩余告警重算 blocks，最后原子写 guard 文件。
    """
    cfg = load_config()
    conn = llm_alert.connect()
    try:
        alerts = llm_alert.run_checks(conn, cfg)
    finally:
        try:
            conn.close()
        except Exception:  # noqa: BLE001
            pass

    state = llm_alert.load_alert_state()
    done = llm_alert.resume_blocks(state, alerts, keys)
    blocks = llm_alert.compute_blocks(alerts, cfg, state)
    llm_alert.prune_resumed(state)
    llm_alert.save_alert_state(state)
    written = llm_alert.write_guard(cfg, blocks)
    return {
        "resumed": done,
        "resumed_count": len(done),
        "blocks": blocks,
        "guard_file": str(written),
    }


# ─── 令牌 ────────────────────────────────────────────────────

def tokens() -> List[Dict]:
    return llm_auth.list_tokens()


def issue_token(client: str, project: str = "", note: str = "",
                admin: bool = False) -> Dict:
    client = (client or "").strip()
    if not client:
        raise AdminError("client 不能为空")
    if len(client) > 64:
        raise AdminError("client 过长（≤64）")
    token = llm_auth.issue(client, project, note, admin=admin)
    return {
        "client": client,
        "project": (project or "").strip(),
        "admin": bool(admin),
        "fingerprint": llm_auth.fingerprint(token),
        "token": token,
        "_warning": "明文只出现这一次，请立刻写入客户端配置",
    }


def revoke_token(selector: str) -> List[str]:
    selector = (selector or "").strip()
    if not selector:
        raise AdminError("selector 不能为空")
    return llm_auth.revoke(selector)


# ─── 状态 ────────────────────────────────────────────────────

def _meter_today() -> Dict:
    """今日花费/条数（只读；库缺失返回 available=false）。"""
    out = {"available": False}
    if not METER_DB.exists():
        return out
    try:
        con = sqlite3.connect(f"file:{METER_DB}?mode=ro", uri=True)
        con.execute("SELECT 1 FROM sqlite_master LIMIT 1")
        lt = time.localtime()
        start = time.mktime((lt.tm_year, lt.tm_mon, lt.tm_mday, 0, 0, 0, 0, 0, -1))
        row = con.execute(
            "SELECT COUNT(*), COALESCE(SUM(total_cost_usd),0), "
            "COALESCE(SUM(cost_known=0),0) FROM request_log WHERE created_at >= ?",
            (int(start),)).fetchone()
        con.close()
        out = {"available": True, "requests": row[0],
               "usd": round(float(row[1]), 8), "unpriced": row[2]}
    except sqlite3.Error:
        pass
    return out


def _pool_blocked() -> List[Dict]:
    """模型池里被硬置黑（余额/鉴权）的后端；读不到返回空。"""
    d = _read_json(POOL_STATE, {})
    out = []
    # 池文件结构因版本而异，逐层容错地找"有 blocked/block_until 的条目"
    stack = [d]
    while stack:
        cur = stack.pop()
        if isinstance(cur, dict):
            if cur.get("blocked") or cur.get("block_until"):
                out.append({k: cur.get(k) for k in
                            ("model", "reason", "blocked_at", "block_until", "unblock_reason")
                            if k in cur})
            stack.extend(cur.values())
        elif isinstance(cur, list):
            stack.extend(cur)
    return out[:20]


def status() -> Dict:
    rows = tokens()
    cfg = load_config()
    g = guard_state()
    return {
        "auth": {
            "mode": llm_auth.mode(),
            "tokens": len(rows),
            "admin_tokens": sum(1 for r in rows if r.get("admin")),
            "store": str(llm_auth.STORE_PATH),
        },
        "budgets": cfg,
        "guard": {
            "enabled": bool(g.get("enabled")),
            "updated_at": g.get("updated_at", 0),
            "blocks": g.get("blocks", []),
            "file": str(GUARD_PATH),
        },
        "meter_today": _meter_today(),
        "blocked_backends": _pool_blocked(),
        "config_file": str(CONFIG_PATH),
        "time": int(time.time()),
    }


# ─── 分发（供网关调用）──────────────────────────────────────

READ_ROUTES = {
    "/admin/status": "status",
    "/admin/budgets": "budgets_get",
    "/admin/guard": "guard_get",
    "/admin/tokens": "tokens_get",
    "/admin/audit": "audit_get",
}


def dispatch(method: str, path: str, query: Dict, body: Optional[bytes],
             actor: str, fingerprint: str, ip: str = "") -> Dict:
    """执行一个管理动作，返回 dict（含 ``_status`` 表示 HTTP 码）。

    鉴权由调用方（网关）先做；这里只负责业务与审计。任何业务错误都转成
    带状态码的 dict，绝不把异常抛给 aiohttp（否则会变成 500 裸错误页）。
    """
    try:
        return _dispatch(method, path, query, body, actor, fingerprint, ip)
    except AdminError as e:
        return {"error": str(e), "_status": e.status}
    except Exception as e:  # noqa: BLE001
        return {"error": f"{type(e).__name__}: {e}", "_status": 500}


def _dispatch(method: str, path: str, query: Dict, body: Optional[bytes],
              actor: str, fingerprint: str, ip: str = "") -> Dict:
    p = path.rstrip("/") or "/admin"

    def ok(data: Dict) -> Dict:
        data["_status"] = 200
        return data

    def write(action: str, target: str, fn, detail_fn=None) -> Dict:
        try:
            res = fn()
        except AdminError as e:
            audit_append(actor, fingerprint, action, target, "error", ip, {"error": str(e)})
            return {"error": str(e), "_status": e.status}
        except Exception as e:  # noqa: BLE001
            audit_append(actor, fingerprint, action, target, "error", ip,
                         {"error": f"{type(e).__name__}: {e}"})
            return {"error": f"{type(e).__name__}: {e}", "_status": 500}
        err = audit_append(actor, fingerprint, action, target, "ok", ip,
                           detail_fn(res) if detail_fn else None)
        if err:
            res["audit_error"] = err
        res["_status"] = 200
        return res

    if method == "GET" and p in ("/admin", "/admin/status"):
        return ok(status())
    if method == "GET" and p == "/admin/budgets":
        return ok({"config": load_config()})
    if method == "PUT" and p == "/admin/budgets":
        patch = _parse_body(body)
        return write("budgets.update", "meter_config.json",
                     lambda: {"config": update_config(patch)},
                     lambda r: {"changed": sorted(patch)})
    if method == "GET" and p == "/admin/guard":
        return ok(guard_state())
    if method == "POST" and p == "/admin/guard/resume":
        payload = _parse_body(body, allow_empty=True)
        keys = payload.get("keys") if isinstance(payload, dict) else None
        if keys is not None and not isinstance(keys, list):
            return {"error": "keys 必须是数组", "_status": 400}
        return write("guard.resume", "meter_guard.json",
                     lambda: resume(keys), lambda r: {"resumed": r.get("resumed", [])})
    if method == "GET" and p == "/admin/tokens":
        return ok({"tokens": tokens()})
    if method == "POST" and p == "/admin/tokens/issue":
        payload = _parse_body(body)
        client = str(payload.get("client") or "")
        res = write("tokens.issue", client,
                    lambda: issue_token(client, payload.get("project", ""),
                                        payload.get("note", ""),
                                        bool(payload.get("admin"))),
                    lambda r: {"fingerprint": r["fingerprint"], "admin": r["admin"]})
        return res
    if method == "POST" and p == "/admin/tokens/revoke":
        payload = _parse_body(body)
        selector = str(payload.get("selector") or "")
        return write("tokens.revoke", selector,
                     lambda: {"revoked": revoke_token(selector)},
                     lambda r: {"revoked": r["revoked"]})
    if method == "GET" and p == "/admin/audit":
        try:
            limit = int((query or {}).get("limit", AUDIT_DEFAULT_LIMIT))
        except (TypeError, ValueError):
            limit = AUDIT_DEFAULT_LIMIT
        return ok({"entries": audit_list(limit), "file": str(AUDIT_PATH)})

    return {"error": f"未知管理端点: {method} {p}", "_status": 404}


def _parse_body(body: Optional[bytes], allow_empty: bool = False) -> Dict:
    if not body:
        if allow_empty:
            return {}
        raise AdminError("请求体为空")
    try:
        data = json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        raise AdminError("请求体不是合法 JSON")
    if not isinstance(data, dict):
        raise AdminError("请求体必须是 JSON 对象")
    return data
