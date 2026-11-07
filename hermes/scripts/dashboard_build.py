"""看板合并库构建（阶段三 H · M6-A）。

问题：Hive 看板读的是 sidecar 所在机的 `~/.hermes/state/llm_meter.db`，
而生产网关 2026-11-02 起跑在 ECS —— 本机库只剩历史，看板会"看起来正常但停更"。

做法：每小时拉一次 ECS 一致快照，与本机历史账合并成**只读看板库**
`~/.hermes/state/meter_dashboard.db`，整库重建 + 原子替换。schema 与网关
`request_log` 完全一致（sidecar 只读它，不需要写权限）。

    python3 dashboard_build.py               # 拉 ECS + 重建（默认）
    python3 dashboard_build.py --no-pull     # 只用已有快照（离线/演练）
    python3 dashboard_build.py --out /tmp/x.db --local /tmp/y.db --json

退出码：0 成功；1 重建失败（旧库保留不动）。
"""

from __future__ import annotations

import argparse
import json
import os
import sqlite3
import sys
import tempfile
import time
from pathlib import Path
from typing import Dict, Optional

# 允许直接 `python3 meter/dashboard_build.py` 运行
sys.path.insert(0, str(Path(__file__).resolve().parent))

HERMES_HOME = Path(os.environ.get("HERMES_HOME", str(Path.home() / ".hermes")))
STATE = HERMES_HOME / "state"
LOCAL_DB = Path(os.environ.get("LLM_METER_DB", str(STATE / "llm_meter.db")))
OUT_DB = Path(os.environ.get("LLM_DASHBOARD_DB", str(STATE / "meter_dashboard.db")))
ECS_SNAPSHOT = Path(os.environ.get("LLM_ECS_SNAPSHOT", str(STATE / "ecs_meter.db")))

DDL = """
CREATE TABLE request_log (
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
CREATE INDEX idx_meter_created ON request_log(created_at);
CREATE INDEX idx_meter_client  ON request_log(client, created_at);
CREATE INDEX idx_meter_project ON request_log(project, created_at);
CREATE TABLE meta (k TEXT PRIMARY KEY, v TEXT NOT NULL);
"""

COLS = ("request_id, client, project, route, provider, backend_name, model, "
        "request_model, input_tokens, output_tokens, cache_read_tokens, "
        "cache_creation_tokens, total_cost_usd, cost_known, latency_ms, "
        "status_code, is_streaming, token_estimated, source, created_at")


def _attach(con: sqlite3.Connection, path: Path, alias: str) -> bool:
    """只读挂载（库不存在返回 False）。mode=ro 避免给源库建 -wal/-shm。

    WAL 库缺 `-shm` 时 mode=ro 会失败（常见于刚拉回来的 ECS 快照），
    退一步用普通挂载——我们只 SELECT，不会写源库。
    """
    if not path.exists():
        return False
    for spec in (f"file:{path}?mode=ro", str(path)):
        try:
            con.execute(f"ATTACH DATABASE ? AS {alias}", (spec,))
            return True
        except sqlite3.Error:
            continue
    return False


def build(local: Path, remote: Optional[Path], out: Path) -> Dict:
    """整库重建并原子替换，返回统计。失败抛异常，旧库不受影响。"""
    out.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=".dashboard_", suffix=".db", dir=str(out.parent))
    os.close(fd)
    tmp = Path(tmp_name)
    stat = {"built_at": int(time.time()), "local_rows": 0, "remote_rows": 0,
            "sources": [], "out": str(out)}
    try:
        con = sqlite3.connect(str(tmp), uri=True)
        try:
            con.executescript(DDL)
            con.execute("INSERT INTO meta(k,v) VALUES('built_at',?)",
                        (time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime()),))
            have_l = _attach(con, local, "loc")
            have_r = bool(remote) and _attach(con, remote, "rem")

            if have_l:
                n = con.execute(
                    f"INSERT OR IGNORE INTO request_log ({COLS}) "
                    f"SELECT {COLS} FROM loc.request_log").rowcount
                stat["local_rows"] = max(n, 0)
                stat["sources"].append({"name": "local", "path": str(local),
                                        "rows": stat["local_rows"], "ok": True})
            else:
                stat["sources"].append({"name": "local", "path": str(local),
                                        "rows": 0, "ok": False})
            if have_r:
                n = con.execute(
                    f"INSERT OR IGNORE INTO request_log ({COLS}) "
                    f"SELECT {COLS} FROM rem.request_log").rowcount
                stat["remote_rows"] = max(n, 0)
                stat["sources"].append({"name": "ecs", "path": str(remote),
                                        "rows": stat["remote_rows"], "ok": True})
            elif remote:
                stat["sources"].append({"name": "ecs", "path": str(remote),
                                        "rows": 0, "ok": False})

            stat["total_rows"] = con.execute(
                "SELECT COUNT(*) FROM request_log").fetchone()[0]
            con.execute("INSERT OR REPLACE INTO meta(k,v) VALUES('total_rows',?)",
                        (str(stat["total_rows"]),))
            con.execute("INSERT OR REPLACE INTO meta(k,v) VALUES('sources',?)",
                        (json.dumps(stat["sources"], ensure_ascii=False),))
            con.commit()
        finally:
            con.close()
        os.chmod(tmp, 0o600)
        os.replace(tmp, out)          # 原子替换：读方永远看到完整库
        return stat
    except Exception:
        try:
            tmp.unlink(missing_ok=True)
        except OSError:
            pass
        raise


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="构建看板合并库（本机历史 + ECS 生产）")
    ap.add_argument("--local", default=str(LOCAL_DB))
    ap.add_argument("--remote", default=str(ECS_SNAPSHOT), help="ECS 快照落点")
    ap.add_argument("--out", default=str(OUT_DB))
    ap.add_argument("--no-pull", action="store_true", help="不联网，只用已有快照")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    note = "未拉取（--no-pull）"
    if not args.no_pull:
        from ledger_merge import fetch_remote
        ok, note = fetch_remote(Path(args.remote))

    try:
        stat = build(Path(args.local), Path(args.remote), Path(args.out))
    except Exception as e:  # noqa: BLE001
        print(f"❌ 看板库重建失败（旧库保留）：{e}", file=sys.stderr)
        return 1
    stat["pull"] = note
    stat["pull_ok"] = note.startswith("已从 ECS")

    if args.json:
        print(json.dumps(stat, ensure_ascii=False, indent=1))
    else:
        print(f"看板库: {stat['out']}")
        print(f"  本机 {stat['local_rows']} 条 / ECS {stat['remote_rows']} 条 "
              f"/ 合计 {stat['total_rows']} 条")
        print(f"  ECS 快照: {note}")
        if not stat["pull_ok"] and not args.no_pull:
            print("  ⚠️ 只含本机历史，ECS 增量未并入")
    return 0


if __name__ == "__main__":
    sys.exit(main())
