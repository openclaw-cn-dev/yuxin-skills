"""LLM 用量三级预警（阶段三 H · M3）。

设计口径
--------
- **默认只告警，不熔断**（华哥 D3 拍板：先观察 2 周）。``alarm_only=true`` 时
  本模块只读计量库 + 推送消息，绝不改写模型池状态、绝不拦截请求。
- **冷却**：同一个 ``(alert_key, level)`` 在 ``cooldown_hours`` 内只推一次，
  避免刷屏；级别升级（L1→L2→L3）视为新告警，立即推送。
- **凭证零硬编码**：飞书 app_id/app_secret 只从 ``~/.hermes/.env`` 读取，
  日志与输出里永不打印密钥。
- **只读**：对 ``llm_meter.db`` 只做 SELECT，不写任何计量数据。

告警维度
--------
1. ``daily_budget``   今日总花费 / 日预算
2. ``monthly_budget`` 本月总花费 / 月预算
3. ``client_daily``   单客户端今日花费 / 单客户端日预算
4. ``balance``        后端余额/额度不足（402/403/429 集中出现）
5. ``unpriced``       未定价请求占比过高（看板数字会失真）
6. ``error_rate``     近 1 小时失败率过高（上游不健康）

用法
----
    python3 llm_alert.py                 # 跑一轮检查并按需推送
    python3 llm_alert.py --dry-run       # 只看会推什么，不真发
    python3 llm_alert.py --force         # 忽略冷却（演练用）
    python3 llm_alert.py --json          # 机器可读输出（看板/巡检调用）

环境变量
--------
    LLM_METER_DB      计量库路径（默认 ~/.hermes/state/llm_meter.db）
    LLM_METER_CONFIG  配置文件路径（默认 ~/.hermes/state/meter_config.json）
    LLM_ALERT_STATE   冷却状态路径（默认 ~/.hermes/state/llm_alert_state.json）
"""

from __future__ import annotations

import argparse
import json
import os
import sqlite3
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional

STATE_DIR = Path(os.environ.get("HERMES_STATE_DIR", Path.home() / ".hermes" / "state"))
METER_DB = Path(os.environ.get("LLM_METER_DB", STATE_DIR / "llm_meter.db"))
CONFIG_PATH = Path(os.environ.get("LLM_METER_CONFIG", STATE_DIR / "meter_config.json"))
ALERT_STATE_PATH = Path(os.environ.get("LLM_ALERT_STATE", STATE_DIR / "llm_alert_state.json"))
GUARD_PATH = Path(os.environ.get("LLM_METER_GUARD", STATE_DIR / "meter_guard.json"))
ENV_FILE = Path.home() / ".hermes" / ".env"

LEVELS = ("l1", "l2", "l3")
LEVEL_MARK = {"l1": "🟡", "l2": "🟠", "l3": "🔴"}
LEVEL_NAME = {"l1": "L1 提示", "l2": "L2 警告", "l3": "L3 严重"}

DEFAULT_CONFIG: Dict[str, Any] = {
    # 只告警不熔断；改成 false 需要单独拍板
    "alarm_only": True,
    "budgets": {
        "daily_usd": 10.0,
        "monthly_usd": 200.0,
        "per_client_daily_usd": 5.0,
    },
    "levels": {"l1": 0.5, "l2": 0.8, "l3": 1.0},
    "cooldown_hours": 6,
    "checks": {
        "budget": True,
        "balance": True,
        "unpriced": True,
        "error_rate": True,
    },
    "unpriced_ratio_threshold": 0.2,
    "error_rate_threshold": 0.1,
    "error_rate_window_minutes": 60,
    "balance_window_minutes": 120,
    "feishu": {"enabled": True, "chat_id_env": "FEISHU_HOME_CHANNEL"},
}


# ────────────────────────── 配置 / 状态 ──────────────────────────

def deep_merge(base: Dict[str, Any], over: Dict[str, Any]) -> Dict[str, Any]:
    """递归合并，`over` 覆盖 `base`；不改动入参。"""
    out = dict(base)
    for k, v in (over or {}).items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = deep_merge(out[k], v)
        else:
            out[k] = v
    return out


def load_config(path: Optional[Path] = None) -> Dict[str, Any]:
    """读配置；文件不存在时返回默认值（**不写盘**，避免误建）。"""
    path = Path(path) if path else CONFIG_PATH
    if not path.exists():
        return json.loads(json.dumps(DEFAULT_CONFIG))
    try:
        user_cfg = json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:  # noqa: BLE001
        print(f"WARN: 配置解析失败，改用默认值: {e}", file=sys.stderr)
        return json.loads(json.dumps(DEFAULT_CONFIG))
    return deep_merge(DEFAULT_CONFIG, user_cfg)


def load_alert_state(path: Optional[Path] = None) -> Dict[str, Any]:
    path = Path(path) if path else ALERT_STATE_PATH
    if not path.exists():
        return {"sent": {}}
    try:
        d = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(d.get("sent"), dict):
            d["sent"] = {}
        return d
    except Exception:  # noqa: BLE001
        return {"sent": {}}


def save_alert_state(state: Dict[str, Any], path: Optional[Path] = None) -> None:
    path = Path(path) if path else ALERT_STATE_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(state, ensure_ascii=False, indent=1), encoding="utf-8")
    tmp.replace(path)


# ────────────────────────── 数据查询 ──────────────────────────

def connect(db: Optional[Path] = None) -> sqlite3.Connection:
    db = Path(db) if db else METER_DB
    if not db.exists():
        raise SystemExit(f"找不到计量库: {db}")
    # 只读打开：本模块绝不写计量数据
    conn = sqlite3.connect(f"file:{db}?mode=ro", uri=True, timeout=5)
    conn.row_factory = sqlite3.Row
    return conn


def _today(now: Optional[float] = None) -> str:
    return time.strftime("%Y-%m-%d", time.localtime(now or time.time()))


def _month_prefix(now: Optional[float] = None) -> str:
    return time.strftime("%Y-%m", time.localtime(now or time.time()))


def _day_bounds(day: str) -> tuple[int, int]:
    t = time.mktime(time.strptime(day, "%Y-%m-%d"))
    return int(t), int(t) + 86400


def spend_between(conn: sqlite3.Connection, start: int, end: int) -> Dict[str, Any]:
    row = conn.execute(
        "SELECT COUNT(*) n, COALESCE(SUM(total_cost_usd),0) usd,"
        " COALESCE(SUM(cost_known=0),0) unpriced"
        " FROM request_log WHERE created_at >= ? AND created_at < ?",
        (start, end),
    ).fetchone()
    return {"requests": int(row["n"]), "usd": float(row["usd"]),
            "unpriced": int(row["unpriced"])}


def spend_by_client(conn: sqlite3.Connection, start: int, end: int) -> List[sqlite3.Row]:
    return list(conn.execute(
        "SELECT client, COUNT(*) n, COALESCE(SUM(total_cost_usd),0) usd"
        " FROM request_log WHERE created_at >= ? AND created_at < ?"
        " GROUP BY client ORDER BY usd DESC",
        (start, end),
    ))


def month_spend(conn: sqlite3.Connection, month: str) -> float:
    start = time.mktime(time.strptime(month + "-01", "%Y-%m-%d"))
    # 月末用下月 1 号 00:00 作开区间
    y, m = int(month[:4]), int(month[5:7])
    nxt = time.mktime(time.strptime(f"{y + (m // 12)}-{(m % 12) + 1:02d}-01", "%Y-%m-%d"))
    row = conn.execute(
        "SELECT COALESCE(SUM(total_cost_usd),0) usd FROM request_log"
        " WHERE created_at >= ? AND created_at < ?", (int(start), int(nxt)),
    ).fetchone()
    return float(row["usd"])


def recent_failures(conn: sqlite3.Connection, since: int) -> List[sqlite3.Row]:
    return list(conn.execute(
        "SELECT backend_name, provider, status_code, COUNT(*) n FROM request_log"
        " WHERE created_at >= ? AND status_code NOT IN (200, 0)"
        " GROUP BY backend_name, provider, status_code ORDER BY n DESC",
        (since,),
    ))


def window_stats(conn: sqlite3.Connection, since: int) -> Dict[str, int]:
    row = conn.execute(
        "SELECT COUNT(*) n, COALESCE(SUM(status_code NOT IN (200,0)),0) bad"
        " FROM request_log WHERE created_at >= ?", (since,),
    ).fetchone()
    return {"requests": int(row["n"]), "failed": int(row["bad"])}


# ────────────────────────── 告警判定 ──────────────────────────

def _level_for_ratio(ratio: float, cfg: Dict[str, Any]) -> Optional[str]:
    lv = cfg.get("levels") or {}
    hit = None
    for name in LEVELS:            # l1 → l2 → l3，取命中的最高级
        try:
            if ratio >= float(lv.get(name, 9e9)):
                hit = name
        except (TypeError, ValueError):
            continue
    return hit


def _mk(key: str, level: str, title: str, lines: List[str]) -> Dict[str, Any]:
    return {"key": key, "level": level, "title": title, "lines": lines}


def check_budgets(conn: sqlite3.Connection, cfg: Dict[str, Any],
                  now: Optional[float] = None) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    budgets = cfg.get("budgets") or {}
    day = _today(now)
    start, end = _day_bounds(day)

    daily_cap = float(budgets.get("daily_usd") or 0)
    if daily_cap > 0:
        d = spend_between(conn, start, end)
        lvl = _level_for_ratio(d["usd"] / daily_cap, cfg)
        if lvl:
            top = ", ".join(
                f"{r['client']} ${r['usd']:.2f}" for r in spend_by_client(conn, start, end)[:4]
            )
            out.append(_mk(
                f"daily_budget:{day}", lvl,
                f"LLM 日预算已用 {d['usd'] / daily_cap:.0%}",
                [f"今日 ${d['usd']:.2f} / 预算 ${daily_cap:.2f}（{d['requests']} 次请求）",
                 f"客户端：{top or '无'}",
                 "处理：确认是否有会话异常循环或批量任务失控"],
            ))

    monthly_cap = float(budgets.get("monthly_usd") or 0)
    if monthly_cap > 0:
        month = _month_prefix(now)
        spent = month_spend(conn, month)
        lvl = _level_for_ratio(spent / monthly_cap, cfg)
        if lvl:
            out.append(_mk(
                f"monthly_budget:{month}", lvl,
                f"LLM 月预算已用 {spent / monthly_cap:.0%}",
                [f"本月 ${spent:.2f} / 预算 ${monthly_cap:.2f}"],
            ))

    client_cap = float(budgets.get("per_client_daily_usd") or 0)
    if client_cap > 0:
        for r in spend_by_client(conn, start, end):
            lvl = _level_for_ratio(float(r["usd"]) / client_cap, cfg)
            if lvl:
                out.append(_mk(
                    f"client_daily:{day}:{r['client']}", lvl,
                    f"客户端 {r['client']} 今日已用 {float(r['usd']) / client_cap:.0%} 额度",
                    [f"{r['client']} ${float(r['usd']):.2f} / ${client_cap:.2f}"
                     f"（{r['n']} 次请求）"],
                ))
    return out


def check_balance(conn: sqlite3.Connection, cfg: Dict[str, Any],
                  now: Optional[float] = None) -> List[Dict[str, Any]]:
    """402/429/403 集中出现 = 后端余额或额度不足（当前 GLM 1113、MiniMax 402 就属这类）。"""
    win = int(cfg.get("balance_window_minutes") or 120) * 60
    since = int((now or time.time()) - win)
    rows = [r for r in recent_failures(conn, since)
            if int(r["status_code"]) in (401, 402, 403, 429)]
    out = []
    for r in rows:
        n = int(r["n"])
        if n < 1:
            continue
        lvl = "l3" if n >= 3 else "l2"
        # backend_name 为 primary/fallback 时用厂商名更可读
        _bname = r["backend_name"]
        name = (_bname if _bname and _bname not in ("primary", "fallback")
                else (r["provider"] or "unknown"))
        out.append(_mk(
            f"balance:{name}:{r['status_code']}", lvl,
            f"后端 {name} 疑似余额/额度不足（HTTP {r['status_code']}）",
            [f"近 {win // 60} 分钟失败 {n} 次，状态 {r['status_code']}",
             "处理：充值或从模型池摘除该后端"],
        ))
    return out


def check_unpriced(conn: sqlite3.Connection, cfg: Dict[str, Any],
                   now: Optional[float] = None) -> List[Dict[str, Any]]:
    start, end = _day_bounds(_today(now))
    d = spend_between(conn, start, end)
    if d["requests"] < 20:
        return []                     # 样本太少，不判
    ratio = d["unpriced"] / d["requests"]
    thr = float(cfg.get("unpriced_ratio_threshold") or 0.2)
    if ratio <= thr:
        return []
    lvl = "l3" if ratio > 0.5 else "l2"
    return [_mk(
        f"unpriced:{_today(now)}", lvl,
        f"未定价请求占比 {ratio:.0%}（看板金额会失真）",
        [f"今日 {d['unpriced']} / {d['requests']} 条无定价",
         "处理：用 meter.set_price 补定价，或确认是否为免费模型"],
    )]


def check_error_rate(conn: sqlite3.Connection, cfg: Dict[str, Any],
                     now: Optional[float] = None) -> List[Dict[str, Any]]:
    win = int(cfg.get("error_rate_window_minutes") or 60) * 60
    since = int((now or time.time()) - win)
    s = window_stats(conn, since)
    if s["requests"] < 10:
        return []
    rate = s["failed"] / s["requests"]
    thr = float(cfg.get("error_rate_threshold") or 0.1)
    if rate <= thr:
        return []
    lvl = "l3" if rate > 0.3 else "l2"
    top = ", ".join(
        f"{r['backend_name'] or r['provider']}:{r['status_code']}×{r['n']}"
        for r in recent_failures(conn, since)[:3]
    )
    return [_mk(
        f"error_rate:{time.strftime('%Y%m%d%H', time.localtime(now or time.time()))}", lvl,
        f"近 {win // 60} 分钟失败率 {rate:.0%}",
        [f"{s['failed']} / {s['requests']} 次失败", f"主要来源：{top}"],
    )]


CHECKS = {
    "budget": check_budgets,
    "balance": check_balance,
    "unpriced": check_unpriced,
    "error_rate": check_error_rate,
}


def run_checks(conn: sqlite3.Connection, cfg: Dict[str, Any],
               now: Optional[float] = None) -> List[Dict[str, Any]]:
    alerts: List[Dict[str, Any]] = []
    enabled = cfg.get("checks") or {}
    for name, fn in CHECKS.items():
        if not enabled.get(name, True):
            continue
        try:
            alerts.extend(fn(conn, cfg, now))
        except Exception as e:  # noqa: BLE001
            print(f"WARN: 检查 {name} 异常: {e}", file=sys.stderr)
    return alerts


# ────────────────────────── 冷却 ──────────────────────────

def filter_by_cooldown(alerts: List[Dict[str, Any]], state: Dict[str, Any],
                       cfg: Dict[str, Any], now: Optional[float] = None,
                       force: bool = False) -> List[Dict[str, Any]]:
    """同一 (key, level) 冷却期内不重复；级别升高立即放行。"""
    if force:
        return alerts
    now = now or time.time()
    cooldown = float(cfg.get("cooldown_hours") or 6) * 3600
    sent = state.setdefault("sent", {})
    out = []
    for a in alerts:
        prev = sent.get(a["key"])
        if prev:
            prev_level = prev.get("level")
            prev_ts = float(prev.get("ts") or 0)
            rank = LEVELS.index(a["level"]) if a["level"] in LEVELS else 0
            prev_rank = LEVELS.index(prev_level) if prev_level in LEVELS else -1
            if now - prev_ts < cooldown and rank <= prev_rank:
                continue
        out.append(a)
    return out


def mark_sent(alerts: List[Dict[str, Any]], state: Dict[str, Any],
              now: Optional[float] = None) -> None:
    now = now or time.time()
    sent = state.setdefault("sent", {})
    for a in alerts:
        sent[a["key"]] = {"level": a["level"], "ts": now}


def prune_state(state: Dict[str, Any], days: int = 30,
                now: Optional[float] = None) -> None:
    cutoff = (now or time.time()) - days * 86400
    sent = state.get("sent") or {}
    state["sent"] = {k: v for k, v in sent.items() if float(v.get("ts") or 0) >= cutoff}


# ────────────────────────── 熔断闸门 ──────────────────────────
# alarm_only=false 时，把「L3 级预算类告警」转成熔断块写进 meter_guard.json，
# 网关在转发前读它并直接返回 402。口径：
#   - 只有预算类（日/月/单客户端）达到 L3（≥100%）才熔断；L1/L2 只告警。
#   - 余额不足不熔断：模型池已自动置黑换后端，拦了反而把可用服务全停掉。
#   - 到期自动解除（日→次日 0 点，月→次月 1 日 0 点）。
#   - --resume 可立刻解除当期熔断（记入 state["resumed"]，当期不再重block）。

BLOCKABLE_KINDS = ("daily_budget", "monthly_budget", "client_daily")


def _period_end(key: str, now: Optional[float] = None) -> int:
    """按告警键推算解除时间：日/客户端→次日 0 点，月→次月 1 日 0 点。"""
    now = now or time.time()
    parts = key.split(":")
    kind = parts[0]
    lt = time.localtime(now)
    if kind == "monthly_budget":
        y, m = lt.tm_year, lt.tm_mon
        ny, nm = (y + 1, 1) if m == 12 else (y, m + 1)
        return int(time.mktime((ny, nm, 1, 0, 0, 0, 0, 0, -1)))
    # 日界
    y, m, d = lt.tm_year, lt.tm_mon, lt.tm_mday
    nxt = time.mktime((y, m, d, 0, 0, 0, 0, 0, -1)) + 86400
    t = time.localtime(nxt)
    return int(time.mktime((t.tm_year, t.tm_mon, t.tm_mday, 0, 0, 0, 0, 0, -1)))


def _block_scope(key: str) -> str:
    """client_daily:<date>:<client> → client:<client>；其余 → global。"""
    parts = key.split(":")
    if parts[0] == "client_daily" and len(parts) >= 3:
        return "client:" + ":".join(parts[2:])
    return "global"


def compute_blocks(alerts: List[Dict[str, Any]], cfg: Dict[str, Any],
                   state: Dict[str, Any], now: Optional[float] = None
                   ) -> List[Dict[str, Any]]:
    """从不低于 L3 的预算类告警生成熔断块；alarm_only=true 或已 resume 的不生成。"""
    if cfg.get("alarm_only", True):
        return []
    now = now or time.time()
    resumed = state.get("resumed") or {}
    blocks = []
    for a in alerts:
        key = a["key"]
        kind = key.split(":")[0]
        if kind not in BLOCKABLE_KINDS or a.get("level") != "l3":
            continue
        if key in resumed:
            continue
        blocks.append({
            "key": key,
            "scope": _block_scope(key),
            "level": a["level"],
            "reason": a["title"],
            "since": int(now),
            "expires_at": _period_end(key, now),
        })
    return blocks


def write_guard(cfg: Dict[str, Any], blocks: List[Dict[str, Any]],
                now: Optional[float] = None, path: Optional[Path] = None) -> Path:
    """写熔断状态文件（网关唯一读取源）。alarm_only=true 时写 enabled=false。"""
    path = Path(path) if path else GUARD_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "enabled": not cfg.get("alarm_only", True),
        "updated_at": int(now or time.time()),
        "blocks": blocks if not cfg.get("alarm_only", True) else [],
    }
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")
    tmp.replace(path)
    return path


def resume_blocks(state: Dict[str, Any], alerts: List[Dict[str, Any]],
                  keys: Optional[List[str]] = None,
                  now: Optional[float] = None) -> List[str]:
    """当期解除熔断：把命中的块记进 state["resumed"]，返回被解除的键。"""
    now = now or time.time()
    resumed = state.setdefault("resumed", {})
    want = set(keys or [])
    done = []
    for a in alerts:
        key = a["key"]
        if key.split(":")[0] not in BLOCKABLE_KINDS:
            continue
        if want and key not in want:
            continue
        resumed[key] = now
        done.append(key)
    return done


def prune_resumed(state: Dict[str, Any], days: int = 40,
                  now: Optional[float] = None) -> None:
    cutoff = (now or time.time()) - days * 86400
    r = state.get("resumed") or {}
    state["resumed"] = {k: v for k, v in r.items() if float(v or 0) >= cutoff}


# ────────────────────────── 飞书 ──────────────────────────

def _read_env(path: Path = ENV_FILE) -> Dict[str, str]:
    """极简 .env 解析：只取 KEY=VALUE，忽略注释与空行。"""
    out: Dict[str, str] = {}
    if not path.exists():
        return out
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        out[k.strip()] = v.strip().strip('"').strip("'")
    return out


def send_feishu(text: str, cfg: Dict[str, Any]) -> Dict[str, Any]:
    """发飞书文本消息。凭证只从 ~/.hermes/.env 读，绝不硬编码、绝不打印。"""
    fcfg = cfg.get("feishu") or {}
    if not fcfg.get("enabled", True):
        return {"ok": False, "skipped": "feishu disabled"}
    env = _read_env()
    app_id = env.get("FEISHU_APP_ID") or os.environ.get("FEISHU_APP_ID", "")
    app_secret = env.get("FEISHU_APP_SECRET") or os.environ.get("FEISHU_APP_SECRET", "")
    chat_id = env.get(fcfg.get("chat_id_env", "FEISHU_HOME_CHANNEL"), "")
    if not (app_id and app_secret and chat_id):
        return {"ok": False, "skipped": "缺少飞书凭证或 chat_id"}

    base = env.get("FEISHU_DOMAIN", "feishu") or "feishu"
    host = "https://open.larksuite.com" if base.startswith("lark") else "https://open.feishu.cn"
    try:
        req = urllib.request.Request(
            f"{host}/open-apis/auth/v3/tenant_access_token/internal",
            data=json.dumps({"app_id": app_id, "app_secret": app_secret}).encode(),
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=10) as r:
            tok = json.loads(r.read())
        if tok.get("code") != 0:
            return {"ok": False, "error": f"取 token 失败 code={tok.get('code')}"}
        token = tok["tenant_access_token"]

        payload = {"receive_id": chat_id, "msg_type": "text",
                   "content": json.dumps({"text": text}, ensure_ascii=False)}
        req2 = urllib.request.Request(
            f"{host}/open-apis/im/v1/messages?receive_id_type=chat_id",
            data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json",
                     "Authorization": f"Bearer {token}"},
        )
        with urllib.request.urlopen(req2, timeout=10) as r:
            res = json.loads(r.read())
        return {"ok": res.get("code") == 0, "code": res.get("code")}
    except urllib.error.URLError as e:
        return {"ok": False, "error": f"网络错误: {e.reason}"}
    except Exception as e:  # noqa: BLE001
        return {"ok": False, "error": str(e)[:120]}


def format_alerts(alerts: List[Dict[str, Any]], cfg: Dict[str, Any]) -> str:
    head = "⚠️ LLM 用量预警" + ("（观察期 · 只告警不熔断）" if cfg.get("alarm_only", True)
                              else "（熔断已开 · L3 预算超限将拒绝请求）")
    blocks = []
    for a in alerts:
        mark = LEVEL_MARK.get(a["level"], "•")
        blocks.append(
            f"{mark} [{LEVEL_NAME.get(a['level'], a['level'])}] {a['title']}\n"
            + "\n".join(f"  · {ln}" for ln in a["lines"])
        )
    return head + "\n\n" + "\n\n".join(blocks)


# ────────────────────────── CLI ──────────────────────────

def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="LLM 用量三级预警")
    ap.add_argument("--dry-run", action="store_true", help="只输出不推送")
    ap.add_argument("--force", action="store_true", help="忽略冷却（演练用）")
    ap.add_argument("--json", action="store_true", help="机器可读输出")
    ap.add_argument("--config", default=None, help="配置文件路径")
    ap.add_argument("--no-state", action="store_true", help="不读写冷却状态")
    ap.add_argument("--resume", nargs="?", const="*", default=None,
                    metavar="KEY", help="解除当期熔断（省略值 = 全部解除）")
    args = ap.parse_args(argv)

    cfg = load_config(Path(args.config) if args.config else None)
    conn = connect()
    alerts = run_checks(conn, cfg)
    conn.close()

    state = load_alert_state() if not args.no_state else {"sent": {}, "resumed": {}}

    # ── 熔断解除（--resume）──
    if args.resume is not None:
        keys = None if args.resume in ("*", "") else [args.resume]
        done = resume_blocks(state, alerts, keys)
        blocks = compute_blocks(alerts, cfg, state)
        if not args.dry_run:
            prune_resumed(state)
            if not args.no_state:
                save_alert_state(state)
            gp = write_guard(cfg, blocks)
            print(f"已解除当期熔断 {len(done)} 项：{', '.join(done) or '无'}")
            print(f"熔断状态文件已刷新: {gp}（当前生效块 {len(blocks)} 个）")
        else:
            print(f"[演练] 将解除 {len(done)} 项：{', '.join(done) or '无'}")
        return 0

    due = filter_by_cooldown(alerts, state, cfg, force=args.force)
    blocks = compute_blocks(alerts, cfg, state)

    result: Dict[str, Any] = {
        "checked_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "alarm_only": bool(cfg.get("alarm_only", True)),
        "total_alerts": len(alerts),
        "due_alerts": len(due),
        "alerts": alerts,
        "due": [a["key"] for a in due],
        "guard_blocks": blocks,
        "pushed": None,
    }

    if due and not args.dry_run:
        text = format_alerts(due, cfg)
        sent = send_feishu(text, cfg)
        result["pushed"] = sent
        if sent.get("ok"):
            mark_sent(due, state)
            prune_state(state)
            if not args.no_state:
                save_alert_state(state)

    # 熔断状态文件每轮都刷新（演练不写）：开关一关，网关下一轮即恢复放行
    if not args.dry_run:
        result["guard_file"] = str(write_guard(cfg, blocks))

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=1))
    else:
        print(f"[{result['checked_at']}] 命中 {len(alerts)} 条，待推 {len(due)} 条"
              f"（{'只告警不熔断' if result['alarm_only'] else '熔断已开'}）")
        for a in due:
            print(f"  {LEVEL_MARK.get(a['level'], '•')} {a['key']} — {a['title']}")
        if blocks:
            print(f"  ⛔ 熔断生效 {len(blocks)} 项：" +
                  ", ".join(f"{b['key']}({b['scope']})" for b in blocks))
        if args.dry_run and due:
            print("--- 将推送的内容 ---")
            print(format_alerts(due, cfg))
        if result["pushed"] is not None:
            print(f"推送结果: {result['pushed']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
