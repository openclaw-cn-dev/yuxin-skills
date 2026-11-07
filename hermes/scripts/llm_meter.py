"""渔芯 LLM 网关计量模块（阶段三 H · M1/M2）。

设计要点
--------
1. **单一事实源**：所有计量落 ``~/.hermes/state/llm_meter.db``，看板/预警只读此库。
2. **不侵入第三方**：cc-switch 的数据由 ``meter_import.py`` 只读导入（source='cc-switch'），
   本模块从不写 cc-switch 的库。
3. **绝不阻断转发**：所有写入走内存队列 + 后台线程批量落库，任何异常只记日志不抛出。
4. **口径可解释**：token 取自上游真实 usage；拿不到时置 ``token_estimated=1`` 并如实标注。
   价格缺失时 ``total_cost_usd`` 为 NULL、``cost_known=0``，绝不写 0 冒充"免费"。

表结构对齐 cc-switch 的 proxy_request_logs / usage_daily_rollups，额外增加
``client`` / ``project`` 两个维度列（这是 cc-switch 没有、也是本次需求的核心）。
"""

from __future__ import annotations

import hashlib
import json
import os
import queue
import sqlite3
import threading
import time
from pathlib import Path
from typing import Any, Dict, Iterable, Optional, Tuple

HERMES_HOME = Path(os.environ.get("HERMES_HOME", Path.home() / ".hermes"))
STATE_DIR = HERMES_HOME / "state"
DB_PATH = Path(os.environ.get("HIVE_METER_DB", STATE_DIR / "llm_meter.db"))
LOG_PATH = HERMES_HOME / "logs" / "llm_meter.log"

# 身份兜底的映射表：token sha256 前 16 位 → {client, project}
CLIENT_MAP_PATH = STATE_DIR / "meter_clients.json"

# 未知身份时的默认归属（宁可标 unknown，也不瞎猜）
DEFAULT_CLIENT = "unknown"
DEFAULT_PROJECT = "unknown"

_SCHEMA = """
CREATE TABLE IF NOT EXISTS request_log (
    request_id            TEXT PRIMARY KEY,
    client                TEXT NOT NULL DEFAULT 'unknown',
    project               TEXT NOT NULL DEFAULT 'unknown',
    route                 TEXT,
    provider              TEXT,
    backend_name          TEXT,
    model                 TEXT,
    request_model         TEXT,
    input_tokens          INTEGER NOT NULL DEFAULT 0,
    output_tokens         INTEGER NOT NULL DEFAULT 0,
    cache_read_tokens     INTEGER NOT NULL DEFAULT 0,
    cache_creation_tokens INTEGER NOT NULL DEFAULT 0,
    total_cost_usd        REAL,
    cost_known            INTEGER NOT NULL DEFAULT 0,
    latency_ms            INTEGER NOT NULL DEFAULT 0,
    status_code           INTEGER NOT NULL DEFAULT 0,
    is_streaming          INTEGER NOT NULL DEFAULT 0,
    token_estimated       INTEGER NOT NULL DEFAULT 0,
    source                TEXT NOT NULL DEFAULT 'gateway',
    created_at            INTEGER NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_meter_created ON request_log(created_at);
CREATE INDEX IF NOT EXISTS idx_meter_client  ON request_log(client, created_at);
CREATE INDEX IF NOT EXISTS idx_meter_project ON request_log(project, created_at);
CREATE INDEX IF NOT EXISTS idx_meter_model   ON request_log(model, created_at);

CREATE TABLE IF NOT EXISTS daily_rollup (
    date                  TEXT NOT NULL,
    client                TEXT NOT NULL,
    project               TEXT NOT NULL,
    provider              TEXT NOT NULL DEFAULT '',
    model                 TEXT NOT NULL DEFAULT '',
    request_count         INTEGER NOT NULL DEFAULT 0,
    success_count         INTEGER NOT NULL DEFAULT 0,
    input_tokens          INTEGER NOT NULL DEFAULT 0,
    output_tokens         INTEGER NOT NULL DEFAULT 0,
    cache_read_tokens     INTEGER NOT NULL DEFAULT 0,
    cache_creation_tokens INTEGER NOT NULL DEFAULT 0,
    total_cost_usd        REAL NOT NULL DEFAULT 0,
    unpriced_count        INTEGER NOT NULL DEFAULT 0,
    avg_latency_ms        INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (date, client, project, provider, model)
);

CREATE TABLE IF NOT EXISTS model_pricing (
    model_id               TEXT PRIMARY KEY,
    input_per_m            REAL NOT NULL DEFAULT 0,
    output_per_m           REAL NOT NULL DEFAULT 0,
    cache_read_per_m       REAL NOT NULL DEFAULT 0,
    cache_create_per_m     REAL NOT NULL DEFAULT 0,
    currency               TEXT NOT NULL DEFAULT 'USD',
    note                   TEXT,
    updated_at             INTEGER NOT NULL
);

-- 模型别名归一：deepseek-flash → deepseek-v4-flash
CREATE TABLE IF NOT EXISTS model_alias (
    alias        TEXT PRIMARY KEY,
    canonical    TEXT NOT NULL
);
"""

# 首批别名：把实际在跑的名字归一到有定价的规范名
_SEED_ALIASES = {
    "deepseek-flash": "deepseek-v4-flash",
    "deepseek-v4.1-flash": "deepseek-v4-flash",
    "deepseek-v4-flash-1017": "deepseek-v4-flash",
    "deepseek-v4-pro-0813": "deepseek-v4-pro",
    "glm-5.3-flash": "glm-5.3-flash",
    "glm-5.3": "glm-5.3",
}


def _now() -> int:
    return int(time.time())


def _log(msg: str) -> None:
    """计量自身日志，绝不抛异常。"""
    try:
        LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(LOG_PATH, "a") as f:
            f.write(f"[{time.strftime('%Y-%m-%dT%H:%M:%S')}] {msg}\n")
    except Exception:
        pass


def connect(db_path: Optional[Path] = None) -> sqlite3.Connection:
    """打开计量库（WAL 模式，读写不互斥）。"""
    path = Path(db_path or DB_PATH)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path), timeout=5)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    return conn


def ensure_schema(conn: Optional[sqlite3.Connection] = None) -> None:
    """建表 + 种子别名。幂等。"""
    own = conn is None
    conn = conn or connect()
    try:
        conn.executescript(_SCHEMA)
        conn.executemany(
            "INSERT OR IGNORE INTO model_alias(alias, canonical) VALUES(?, ?)",
            list(_SEED_ALIASES.items()),
        )
        conn.commit()
    finally:
        if own:
            conn.close()


# ─── 身份解析 ────────────────────────────────────────────────

def _load_client_map() -> Dict[str, Dict[str, str]]:
    try:
        return json.loads(CLIENT_MAP_PATH.read_text())
    except Exception:
        return {}


def _token_fingerprint(headers: Dict[str, str]) -> str:
    """取凭据指纹（sha256 前 16 位）。不存明文 token。"""
    raw = (
        headers.get("authorization")
        or headers.get("x-api-key")
        or headers.get("Authorization")
        or headers.get("X-Api-Key")
        or ""
    )
    if not raw:
        return ""
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def resolve_identity(headers: Dict[str, str], route: str = "") -> Tuple[str, str]:
    """解析调用方身份。

    优先级：显式请求头 > token 指纹映射表 > 按路由兜底 > unknown。
    显式头：``X-LLM-Client`` / ``X-LLM-Project``（大小写不敏感）。
    """
    try:
        h = {k.lower(): v for k, v in (headers or {}).items()}
        client = (h.get("x-llm-client") or "").strip()
        project = (h.get("x-llm-project") or "").strip()

        if not client:
            fp = _token_fingerprint(headers or {})
            if fp:
                mapped = _load_client_map().get(fp)
                if mapped:
                    client = mapped.get("client", "")
                    project = project or mapped.get("project", "")

        if not client:
            # 路由兜底：/anthropic 基本是 Claude Code，/openai 基本是 Codex
            client = {"/anthropic": "claude-code", "/openai": "codex"}.get(route, DEFAULT_CLIENT)

        return (client or DEFAULT_CLIENT, project or DEFAULT_PROJECT)
    except Exception as e:  # noqa: BLE001 - 任何异常都不能影响转发
        _log(f"resolve_identity error: {e}")
        return (DEFAULT_CLIENT, DEFAULT_PROJECT)


# ─── 计价 ────────────────────────────────────────────────────

def canonical_model(conn: sqlite3.Connection, model: str) -> str:
    """别名归一。查不到就原样返回。"""
    if not model:
        return model
    row = conn.execute(
        "SELECT canonical FROM model_alias WHERE alias=?", (model,)
    ).fetchone()
    return row[0] if row else model


def compute_cost(
    conn: sqlite3.Connection,
    model: str,
    input_tokens: int,
    output_tokens: int,
    cache_read_tokens: int = 0,
    cache_creation_tokens: int = 0,
) -> Tuple[Optional[float], bool, str]:
    """返回 (费用, 是否已知, 规范模型名)。

    价格缺失返回 (None, False, model)——调用方据此标 cost_known=0，
    **绝不写 0 冒充免费**。
    """
    canon = canonical_model(conn, model)
    row = conn.execute(
        "SELECT input_per_m, output_per_m, cache_read_per_m, cache_create_per_m "
        "FROM model_pricing WHERE model_id=?",
        (canon,),
    ).fetchone()
    if not row:
        row = conn.execute(
            "SELECT input_per_m, output_per_m, cache_read_per_m, cache_create_per_m "
            "FROM model_pricing WHERE model_id=?",
            (model,),
        ).fetchone()
        canon = model if row else canon
    if not row:
        return (None, False, canon)

    in_p, out_p, cr_p, cc_p = row
    cost = (
        input_tokens * in_p
        + output_tokens * out_p
        + cache_read_tokens * cr_p
        + cache_creation_tokens * cc_p
    ) / 1_000_000.0
    return (round(cost, 8), True, canon)


# ─── 记录写入（队列 + 后台批量）────────────────────────────

_queue: "queue.Queue[Dict[str, Any]]" = queue.Queue(maxsize=10000)
_flusher_started = False
_flush_lock = threading.Lock()
_pending = 0            # 已入队但未落盘的条数
_pending_lock = threading.Lock()
_dropped = 0


def _flush_batch(conn: sqlite3.Connection, batch: Iterable[Dict[str, Any]]) -> int:
    """批量写入。返回写入条数。"""
    rows = []
    for e in batch:
        if not e.get("request_id"):
            e["request_id"] = f"gw_{int(time.time()*1000)}_{os.urandom(4).hex()}"
        cost, known, canon = compute_cost(
            conn,
            e.get("model") or "",
            int(e.get("input_tokens") or 0),
            int(e.get("output_tokens") or 0),
            int(e.get("cache_read_tokens") or 0),
            int(e.get("cache_creation_tokens") or 0),
        )
        rows.append((
            e["request_id"], e.get("client", DEFAULT_CLIENT), e.get("project", DEFAULT_PROJECT),
            e.get("route", ""), e.get("provider", ""), e.get("backend_name", ""),
            canon or e.get("model", ""), e.get("request_model", ""),
            int(e.get("input_tokens") or 0), int(e.get("output_tokens") or 0),
            int(e.get("cache_read_tokens") or 0), int(e.get("cache_creation_tokens") or 0),
            cost, 1 if known else 0,
            int(e.get("latency_ms") or 0), int(e.get("status_code") or 0),
            1 if e.get("is_streaming") else 0, 1 if e.get("token_estimated") else 0,
            e.get("source", "gateway"), int(e.get("created_at") or _now()),
        ))
    if not rows:
        return 0
    conn.executemany(
        "INSERT OR IGNORE INTO request_log("
        "request_id, client, project, route, provider, backend_name, model,"
        "request_model, input_tokens, output_tokens, cache_read_tokens,"
        "cache_creation_tokens, total_cost_usd, cost_known, latency_ms,"
        "status_code, is_streaming, token_estimated, source, created_at) VALUES("
        + ",".join(["?"] * 20) + ")", rows,
    )
    conn.commit()
    return len(rows)


def _flusher_loop() -> None:
    """后台线程：有数据就立刻落盘（一次最多 50 条）。

    旧实现会攒满 5 秒才写，导致低流量时段数据长时间停留在内存、
    进程被杀就丢。改为「等第一条（最多 5s）→ 立刻排空队列 → 写」。
    """
    global _dropped, _pending
    conn = None
    while True:
        batch: list = []
        try:
            try:
                batch.append(_queue.get(timeout=5))
            except queue.Empty:
                continue
            while len(batch) < 50:
                try:
                    batch.append(_queue.get_nowait())
                except queue.Empty:
                    break

            if conn is None:
                conn = connect()
                ensure_schema(conn)
            n = _flush_batch(conn, batch)
            with _pending_lock:
                _pending = max(0, _pending - len(batch))
        except Exception as e:  # noqa: BLE001
            _dropped += len(batch)
            with _pending_lock:
                _pending = max(0, _pending - len(batch))
            _log(f"flush error (dropped={_dropped}): {e}")
            try:
                if conn:
                    conn.close()
            except Exception:
                pass
            conn = None
            time.sleep(1)


def _ensure_flusher() -> None:
    global _flusher_started
    with _flush_lock:
        if _flusher_started:
            return
        threading.Thread(target=_flusher_loop, daemon=True, name="llm-meter-flusher").start()
        _flusher_started = True


def record(entry: Dict[str, Any]) -> None:
    """记录一次调用。绝不抛出、绝不阻塞。"""
    global _pending
    try:
        _ensure_flusher()
        _queue.put_nowait(entry)
        with _pending_lock:
            _pending += 1
    except queue.Full:
        global _dropped
        _dropped += 1
    except Exception as e:  # noqa: BLE001
        _log(f"record error: {e}")


def pending() -> int:
    """尚未落盘的条数（测试/健康检查用）。"""
    with _pending_lock:
        return _pending


def flush_now(timeout: float = 5.0) -> int:
    """测试/退出时强制落盘，返回本次直接写入的条数。"""
    global _pending
    try:
        deadline = time.time() + timeout
        while time.time() < deadline and pending() > 0:
            time.sleep(0.02)
        conn = connect()
        ensure_schema(conn)
        batch = []
        while True:
            try:
                batch.append(_queue.get_nowait())
            except queue.Empty:
                break
        n = _flush_batch(conn, batch) if batch else 0
        if n:
            with _pending_lock:
                _pending = max(0, _pending - n)
        conn.close()
        return n
    except Exception as e:  # noqa: BLE001
        _log(f"flush_now error: {e}")
        return 0


# ─── 从上游响应体提取 usage ────────────────────────────────

def usage_from_json(payload: bytes) -> Dict[str, int]:
    """从 OpenAI / Anthropic 风格的响应 JSON 提取 token。

    返回统一口径：input/output/cache_read/cache_creation。
    """
    out = {"input_tokens": 0, "output_tokens": 0,
           "cache_read_tokens": 0, "cache_creation_tokens": 0}
    try:
        data = json.loads(payload or b"{}")
    except Exception:
        return out
    u = data.get("usage") or {}
    # OpenAI 风格
    out["input_tokens"] = int(u.get("prompt_tokens") or u.get("input_tokens") or 0)
    out["output_tokens"] = int(u.get("completion_tokens") or u.get("output_tokens") or 0)
    # Anthropic 风格
    out["cache_read_tokens"] = int(u.get("cache_read_input_tokens") or 0)
    out["cache_creation_tokens"] = int(u.get("cache_creation_input_tokens") or 0)
    # OpenAI 的 prompt_tokens_details.cached_tokens
    details = u.get("prompt_tokens_details") or {}
    if not out["cache_read_tokens"] and details.get("cached_tokens"):
        out["cache_read_tokens"] = int(details["cached_tokens"])
    return out


def normalize_usage(u: Dict[str, Any]) -> Dict[str, int]:
    """把 SSE 里拿到的 usage 字典归一（OpenAI 或 Anthropic 口径）。"""
    if not u:
        return {"input_tokens": 0, "output_tokens": 0,
                "cache_read_tokens": 0, "cache_creation_tokens": 0}
    return {
        "input_tokens": int(u.get("prompt_tokens") or u.get("input_tokens") or 0),
        "output_tokens": int(u.get("completion_tokens") or u.get("output_tokens") or 0),
        "cache_read_tokens": int(u.get("cache_read_input_tokens")
                                 or (u.get("prompt_tokens_details") or {}).get("cached_tokens") or 0),
        "cache_creation_tokens": int(u.get("cache_creation_input_tokens") or 0),
    }


# ─── 日汇总（M2）────────────────────────────────────────────

def rollup_date(conn: sqlite3.Connection, date: str) -> int:
    """把某日（本地时区 YYYY-MM-DD）的明细汇总进 daily_rollup。幂等。"""
    conn.execute("DELETE FROM daily_rollup WHERE date=?", (date,))
    conn.execute(
        """
        INSERT INTO daily_rollup
            (date, client, project, provider, model, request_count, success_count,
             input_tokens, output_tokens, cache_read_tokens, cache_creation_tokens,
             total_cost_usd, unpriced_count, avg_latency_ms)
        SELECT
            date(created_at, 'unixepoch', 'localtime'),
            client, project, COALESCE(provider,''), COALESCE(model,''),
            COUNT(*),
            SUM(CASE WHEN status_code BETWEEN 200 AND 299 THEN 1 ELSE 0 END),
            SUM(input_tokens), SUM(output_tokens),
            SUM(cache_read_tokens), SUM(cache_creation_tokens),
            COALESCE(SUM(total_cost_usd), 0),
            SUM(CASE WHEN cost_known=0 THEN 1 ELSE 0 END),
            CAST(AVG(latency_ms) AS INTEGER)
        FROM request_log
        WHERE date(created_at, 'unixepoch', 'localtime') = ?
        GROUP BY date(created_at, 'unixepoch', 'localtime'), client, project,
                 COALESCE(provider,''), COALESCE(model,'')
        """,
        (date,),
    )
    conn.commit()
    row = conn.execute("SELECT COUNT(*) FROM daily_rollup WHERE date=?", (date,)).fetchone()
    return int(row[0])


def seed_pricing(conn: sqlite3.Connection) -> int:
    """写入/刷新已知定价。已存在的模型不覆盖（允许人工调价）。"""
    now = _now()
    # 来源：cc-switch model_pricing 实测值（USD / 百万 token）
    seeds = [
        ("deepseek-v4-flash", 0.14, 0.28, 0.014, 0.0, "DeepSeek V4.1-Flash 缓存命中折扣"),
        ("deepseek-v4-pro", 0.435, 0.87, 0.0435, 0.0, "DeepSeek V4-Pro"),
        ("deepseek-v3.2", 0.28, 0.42, 0.0, 0.0, ""),
        ("deepseek-v3.1", 0.55, 1.67, 0.0, 0.0, ""),
        ("deepseek-chat", 0.27, 1.10, 0.0, 0.0, "旧名，已停用"),
        ("claude-opus-4-8", 5.0, 25.0, 0.5, 6.25, ""),
        ("claude-sonnet-4-6", 3.0, 15.0, 0.3, 3.75, ""),
        ("claude-haiku-4-5", 1.0, 5.0, 0.1, 1.25, ""),
        # Z.AI 海外站官方价（USD/M）。国内站为 0.8/2.8 元，本表统一折美元口径。
        ("glm-5.3-flash", 0.15, 0.50, 0.03, 0.0, "智谱 GLM-5.3-Flash（Z.AI USD）"),
        # MiniMax 价取自 cc-switch 实测表
        ("minimax-m2.7", 0.30, 1.20, 0.0, 0.0, ""),
        ("minimax-m2.5", 0.12, 0.95, 0.0, 0.0, ""),
    ]
    n = 0
    for mid, i, o, cr, cc, note in seeds:
        cur = conn.execute(
            "INSERT OR IGNORE INTO model_pricing"
            "(model_id, input_per_m, output_per_m, cache_read_per_m, cache_create_per_m,"
            " currency, note, updated_at) VALUES(?,?,?,?,?,'USD',?,?)",
            (mid, i, o, cr, cc, note, now),
        )
        n += cur.rowcount
    conn.commit()
    return n


def set_price(conn: sqlite3.Connection, model_id: str, input_per_m: float,
              output_per_m: float, cache_read_per_m: float = 0.0,
              cache_create_per_m: float = 0.0, currency: str = "USD",
              note: str = "") -> None:
    """人工补充/修正定价（看板显示"未定价"时用这个补）。"""
    conn.execute(
        "INSERT INTO model_pricing VALUES(?,?,?,?,?,?,?,?) "
        "ON CONFLICT(model_id) DO UPDATE SET "
        "input_per_m=excluded.input_per_m, output_per_m=excluded.output_per_m, "
        "cache_read_per_m=excluded.cache_read_per_m, "
        "cache_create_per_m=excluded.cache_create_per_m, "
        "currency=excluded.currency, note=excluded.note, updated_at=excluded.updated_at",
        (model_id, input_per_m, output_per_m, cache_read_per_m, cache_create_per_m,
         currency, note, _now()),
    )
    conn.commit()


if __name__ == "__main__":  # 手工初始化：python3 llm_meter.py init
    import sys
    cmd = sys.argv[1] if len(sys.argv) > 1 else "init"
    if cmd == "init":
        c = connect()
        ensure_schema(c)
        added = seed_pricing(c)
        c.close()
        print(f"OK db={DB_PATH} 新增定价 {added} 条")
    elif cmd == "rollup":
        c = connect()
        ensure_schema(c)
        d = sys.argv[2] if len(sys.argv) > 2 else time.strftime("%Y-%m-%d")
        print(f"rolled up {d}: {rollup_date(c, d)} 组")
        c.close()
