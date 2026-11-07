"""双账本按日聚合（阶段三 H · M5 后续）。

两个计量库、两份钱：
  - Mac 历史账本  ~/.hermes/state/llm_meter.db      （M1~M5，网关曾在本机跑）
  - ECS 生产账本  /opt/yuxin-llm-gateway/hermes/state/llm_meter.db （2026-11-02 20:34 起）

本脚本**只读、只聚合、绝不写库**，按「日 × 客户端」把两边加到一起看。

    python3 ledger_merge.py                 # 近 7 天，自动拉 ECS 快照
    python3 ledger_merge.py --days 30
    python3 ledger_merge.py --remote /tmp/ecs_meter.db   # 用已有快照，不联网
    python3 ledger_merge.py --json

注意：`cost_known=0` 的行是**未定价**，费用记为 NULL，不是 0 元——单独计数，不并进合计。
"""

from __future__ import annotations

import argparse
import json
import os
import sqlite3
import subprocess
import sys
import tempfile
import time
from collections import defaultdict
from pathlib import Path
from typing import Dict, Iterable, Tuple

HERMES_HOME = Path(os.environ.get("HERMES_HOME", str(Path.home() / ".hermes")))
LOCAL_DB = Path(os.environ.get("LLM_METER_DB", str(HERMES_HOME / "state" / "llm_meter.db")))
ECS_HOST = os.environ.get("LLM_GW_ECS", "root@121.43.127.211")
ECS_HOME = "/opt/yuxin-llm-gateway/hermes"


def _open_ro(path: Path) -> sqlite3.Connection:
    """只读打开；WAL 库缺 -shm 时 mode=ro 会在**首次查询**才报错（connect 是懒的），
    所以必须探一次再决定是否退回普通连接。"""
    try:
        con = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
        con.execute("SELECT 1 FROM sqlite_master LIMIT 1")
        return con
    except sqlite3.OperationalError:
        return sqlite3.connect(str(path))


def _normalize(path: Path) -> None:
    """backup API 出来的副本**仍是 WAL 模式**，但没带 -wal/-shm，只读打开会报
    "unable to open database file"。副本是我们自己的文件，改回 rollback journal 无害。"""
    try:
        con = sqlite3.connect(str(path))
        try:
            con.execute("PRAGMA journal_mode=DELETE")
        finally:
            con.close()
    except sqlite3.Error:
        pass


def fetch_remote(dest: Path) -> Tuple[bool, str]:
    """用 SQLite backup API 在 ECS 上做一致快照再拉回（不能直接 cp WAL 库）。"""
    cmd = (
        "docker exec yuxin-llm-gateway python -c "
        "\"import sqlite3;s=sqlite3.connect('/hermes/state/llm_meter.db');"
        "d=sqlite3.connect('/hermes/state/meter_snapshot.db');s.backup(d);d.close();s.close()\""
    )
    try:
        subprocess.run(["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=10",
                        ECS_HOST, cmd], check=True, capture_output=True, timeout=120)
        subprocess.run(["rsync", "-a", "-e", "ssh -o BatchMode=yes -o ConnectTimeout=10",
                        f"{ECS_HOST}:{ECS_HOME}/state/meter_snapshot.db", str(dest)],
                       check=True, capture_output=True, timeout=120)
        _normalize(dest)
        return True, "已从 ECS 拉取快照"
    except Exception as e:  # noqa: BLE001
        return False, f"拉取 ECS 快照失败（只统计本地）: {e}"


def load(db: Path, since: int, label: str):
    """返回 {(day, client): [条数, 费用, 未定价条数]}。"""
    agg: Dict[Tuple[str, str], list] = defaultdict(lambda: [0, 0.0, 0])
    if not db.exists():
        return agg, 0, 0
    con = _open_ro(db)
    try:
        rows = con.execute(
            "SELECT date(created_at,'unixepoch','+8 hours') d, client, total_cost_usd, cost_known"
            " FROM request_log WHERE created_at >= ?", (since,))
        total = unpriced = 0
        for day, client, cost, known in rows:
            total += 1
            cell = agg[(day or "?", client or "unknown")]
            cell[0] += 1
            if known and cost is not None:
                cell[1] += float(cost)
            else:
                cell[2] += 1
                unpriced += 1
        return agg, total, unpriced
    finally:
        con.close()


def merge(a, b):
    out = defaultdict(lambda: [0, 0.0, 0])
    for agg in (a, b):
        for k, v in agg.items():
            out[k][0] += v[0]
            out[k][1] += v[1]
            out[k][2] += v[2]
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="双账本按日聚合（只读）")
    ap.add_argument("--days", type=int, default=7)
    ap.add_argument("--local", default=str(LOCAL_DB))
    ap.add_argument("--remote", default=None, help="已有 ECS 快照路径；不给则自动拉")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    since = int(time.time()) - args.days * 86400

    tmpdir = None
    if args.remote:
        remote_db = Path(args.remote)
        note = f"远端库: {remote_db}（未联网）"
    else:
        tmpdir = tempfile.mkdtemp(prefix="llm_ledger_")
        remote_db = Path(tmpdir) / "ecs_meter.db"
        ok, note = fetch_remote(remote_db)
        if not ok:
            remote_db = Path("/nonexistent")

    local_agg, ln, lu = load(Path(args.local), since, "local")
    remote_agg, rn, ru = load(remote_db, since, "ecs")
    total = merge(local_agg, remote_agg)

    if args.json:
        print(json.dumps([{"day": d, "client": c, "requests": v[0],
                           "cost_usd": round(v[1], 8), "unpriced": v[2]}
                          for (d, c), v in sorted(total.items())],
                         ensure_ascii=False, indent=2))
        return 0

    print(f"近 {args.days} 天 · 本机历史 {ln} 条 / ECS {rn} 条 · {note}")
    print()
    print(f"{'日期':<12}{'客户端':<14}{'请求':>6}{'费用(USD)':>14}{'未定价':>8}")
    print("-" * 56)
    day_cost: Dict[str, float] = defaultdict(float)
    for (day, client), v in sorted(total.items()):
        print(f"{day:<12}{client:<14}{v[0]:>6}{v[1]:>14.8f}{v[2]:>8}")
        day_cost[day] += v[1]
    print("-" * 56)
    grand = sum(day_cost.values())
    print(f"{'合计':<26}{sum(v[0] for v in total.values()):>6}{grand:>14.8f}"
          f"{sum(v[2] for v in total.values()):>8}")
    if lu or ru:
        print(f"\n⚠️ 未定价 {lu + ru} 条（本机 {lu} / ECS {ru}）：费用为 NULL 不是 0，"
              f"需在 llm_meter 的定价表补价后重算")
    if tmpdir:
        print(f"\n快照留在 {tmpdir}（可删）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
