"""cc-switch → llm_meter 增量归集器（阶段三 H · M2）。

原则
----
- **只读** cc-switch 库（``file:...?mode=ro``），绝不写它。
- 幂等：以 ``ccs:<request_id>`` 为主键，重复导入直接 IGNORE。
- 计价走 llm_meter 的定价表（cc-switch 自己的 cost 字段大量为 0，不可信）。
- 不搬运任何密钥：providers.settings_config 里含明文 token，本脚本只取 name。

用法
----
    python3 meter_import.py              # 增量导入 + 重算受影响的日汇总
    python3 meter_import.py --full       # 全量重扫（幂等，耗时约数秒）
    python3 meter_import.py --stats      # 只看统计，不写库
"""

from __future__ import annotations

import argparse
import os
import sqlite3
import sys
import time
from pathlib import Path
from typing import Dict, List, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent))
import llm_meter as meter  # noqa: E402

CCS_DB = Path(os.environ.get("CC_SWITCH_DB", Path.home() / ".cc-switch" / "cc-switch.db"))

# app_type → 调用方身份。未命中的按原名记录，便于日后补映射。
APP_TYPE_CLIENT = {
    "claude": "claude-code",
    "claude-desktop": "claude-desktop",
    "codex": "codex",
    "gemini": "gemini-cli",
}


def open_source() -> sqlite3.Connection:
    """只读打开 cc-switch。"""
    if not CCS_DB.exists():
        raise SystemExit(f"找不到 cc-switch 库: {CCS_DB}")
    uri = f"file:{CCS_DB}?mode=ro"
    conn = sqlite3.connect(uri, uri=True, timeout=5)
    conn.row_factory = sqlite3.Row
    return conn


def provider_names(src: sqlite3.Connection) -> Dict[Tuple[str, str], str]:
    """(id, app_type) → 展示名。"""
    out: Dict[Tuple[str, str], str] = {}
    try:
        for r in src.execute("SELECT id, app_type, name FROM providers"):
            out[(r["id"], r["app_type"])] = r["name"]
    except Exception as e:  # noqa: BLE001
        print(f"WARN: 读取 providers 失败（不影响主流程）: {e}", file=sys.stderr)
    return out


def gateway_provider_ids(src: sqlite3.Connection) -> set:
    """cc-switch 里指向本网关的 provider id。

    这些请求是「客户端 → cc-switch 代理 → 渔芯网关」，网关自己已经计过一次；
    再从这里导入就会**双算**。M5 配置收口后必然出现，必须在源头过滤。
    """
    gw = os.environ.get("LLM_GW_BASE", "http://127.0.0.1:18888").rstrip("/")
    out = set()
    try:
        for r in src.execute("SELECT id, settings_config FROM providers"):
            cfg = r["settings_config"] or ""
            if isinstance(cfg, (bytes, bytearray)):
                cfg = cfg.decode("utf-8", "replace")
            if gw in cfg:
                out.add(r["id"])
    except Exception as e:  # noqa: BLE001
        print(f"WARN: 识别网关 provider 失败（可能重复计数）: {e}", file=sys.stderr)
    return out


def fetch_rows(src: sqlite3.Connection, since: int,
               skip_providers: set = frozenset()) -> List[sqlite3.Row]:
    rows = list(src.execute(
        """
        SELECT request_id, provider_id, app_type, model, request_model,
               input_tokens, output_tokens, cache_read_tokens, cache_creation_tokens,
               latency_ms, status_code, is_streaming, created_at
        FROM proxy_request_logs
        WHERE created_at > ?
        ORDER BY created_at
        """,
        (since,),
    ))
    if skip_providers:
        rows = [r for r in rows if r["provider_id"] not in skip_providers]
    return rows


def import_rows(dst: sqlite3.Connection, rows: List[sqlite3.Row],
                names: Dict[Tuple[str, str], str]) -> Tuple[int, int]:
    """返回 (读取条数, 实际新增条数)。"""
    inserted = 0
    now = int(time.time())
    for r in rows:
        rid = f"ccs:{r['request_id']}"
        client = APP_TYPE_CLIENT.get(r["app_type"], r["app_type"] or meter.DEFAULT_CLIENT)
        provider = names.get((r["provider_id"], r["app_type"]), r["provider_id"] or "")
        model = r["model"] or ""
        cost, known, canon = meter.compute_cost(
            dst, model, int(r["input_tokens"] or 0), int(r["output_tokens"] or 0),
            int(r["cache_read_tokens"] or 0), int(r["cache_creation_tokens"] or 0),
        )
        cur = dst.execute(
            "INSERT OR IGNORE INTO request_log("
            "request_id, client, project, route, provider, backend_name, model,"
            "request_model, input_tokens, output_tokens, cache_read_tokens,"
            "cache_creation_tokens, total_cost_usd, cost_known, latency_ms,"
            "status_code, is_streaming, token_estimated, source, created_at) "
            "VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (rid, client, meter.DEFAULT_PROJECT, f"cc-switch/{r['app_type']}",
             provider, "", canon or model, r["request_model"] or "",
             int(r["input_tokens"] or 0), int(r["output_tokens"] or 0),
             int(r["cache_read_tokens"] or 0), int(r["cache_creation_tokens"] or 0),
             cost, 1 if known else 0, int(r["latency_ms"] or 0),
             int(r["status_code"] or 0), 1 if r["is_streaming"] else 0, 0,
             "cc-switch", int(r["created_at"] or now)),
        )
        inserted += cur.rowcount
    dst.commit()
    return len(rows), inserted


def high_watermark(dst: sqlite3.Connection) -> int:
    row = dst.execute(
        "SELECT MAX(created_at) FROM request_log WHERE source='cc-switch'"
    ).fetchone()
    return int(row[0] or 0)


def rollup_dates(dst: sqlite3.Connection, rows: List[sqlite3.Row]) -> int:
    dates = {time.strftime("%Y-%m-%d", time.localtime(int(r["created_at"] or 0))) for r in rows}
    n = 0
    for d in sorted(dates):
        meter.rollup_date(dst, d)
        n += 1
    return n


def main() -> int:
    ap = argparse.ArgumentParser(description="cc-switch → llm_meter 增量归集")
    ap.add_argument("--full", action="store_true", help="全量重扫（幂等）")
    ap.add_argument("--stats", action="store_true", help="只统计不写库")
    args = ap.parse_args()

    src = open_source()
    dst = meter.connect()
    meter.ensure_schema(dst)
    meter.seed_pricing(dst)

    since = 0 if args.full else high_watermark(dst)
    skip = gateway_provider_ids(src)
    rows = fetch_rows(src, since, skip)
    names = provider_names(src)
    if skip:
        print(f"跳过 {len(skip)} 个网关 provider 的请求（避免双算）: {', '.join(sorted(skip))}")

    if args.stats:
        print(f"cc-switch 库: {CCS_DB}")
        print(f"待导入: {len(rows)} 条（since={since}）")
        total = dst.execute("SELECT COUNT(*) FROM request_log WHERE source='cc-switch'").fetchone()[0]
        print(f"已导入: {total} 条")
        src.close(); dst.close()
        return 0

    read_n, ins_n = import_rows(dst, rows, names)
    days = rollup_dates(dst, rows) if rows else 0
    total = dst.execute("SELECT COUNT(*) FROM request_log WHERE source='cc-switch'").fetchone()[0]
    unpriced = dst.execute(
        "SELECT COUNT(*) FROM request_log WHERE source='cc-switch' AND cost_known=0"
    ).fetchone()[0]
    src.close(); dst.close()

    print(f"读取 {read_n} 条，新增 {ins_n} 条，重算 {days} 天汇总")
    print(f"库内 cc-switch 累计 {total} 条，其中未定价 {unpriced} 条")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
