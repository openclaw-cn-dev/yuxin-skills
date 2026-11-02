#!/usr/bin/env python3
# TODO(tech-debt): 改由 Claude Code/Codex 重写 — 失败原因: 自写以便 cron 立刻可用
"""
holdings_ma_scan.py — 持仓 ETF 技术面快扫

每日心跳 cron 必跑。读 boss 真实 holdings.json → ifzq 拉 80 日 K 线 → 输出 MA5/20/60 +
排列(BULL/MIXED/BEAR)+ 5d/20d/60d 涨跌幅 + 与持仓浮盈/止损联动信号。

Usage:
    python3 holdings_ma_scan.py
    python3 holdings_ma_scan.py --codes 512800,512710,159940   # 自定义标的
    python3 holdings_ma_scan.py --md                            # 输出 markdown 表格

Reference:
    /Users/hua/.hermes/profiles/quant/skills/quantitative-research/references/holdings-ma-scan-2026-10-13.md

Update: 2026-10-13 创建(心跳自进化轮沉淀)
"""

import json
import re
import sys
import urllib.request
import argparse
from typing import List, Tuple, Optional, Dict

# --- 配置 ---
DEFAULT_HOLDINGS_PATH = "/Users/hua/6-产品研发/渔芯独角兽/00-基本完成/渔芯量化/渔芯量化/06-持仓档案/holdings.json"
KLINE_URL = "http://web.ifzq.gtimg.cn/appstock/app/fqkline/get?param={sym},day,,,80,qfq"
QT_REALTIME_URL = "http://qt.gtimg.cn/q={codes}"
KLINE_HEADERS = {"User-Agent": "Mozilla/5.0", "Referer": "http://gu.qq.com/"}


def http_get(url: str, timeout: int = 10, decode_gbk: bool = False) -> str:
    req = urllib.request.Request(url, headers=KLINE_HEADERS)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        raw = r.read()
    return raw.decode("gbk", errors="replace") if decode_gbk else raw.decode("utf-8", errors="replace")


def get_kline(code: str, count: int = 80) -> List[Tuple[str, float]]:
    """拉 ifzq 前复权日 K,返回 [(date, close), ...]"""
    market = "sh" if code.startswith(("5", "6")) else "sz"
    symbol = f"{market}{code}"
    raw = http_get(KLINE_URL.format(sym=symbol, count=count))
    # ⚠️ 2026-10-13 pitfall: 是 raw JSON,不是 JSONP
    j = json.loads(raw)
    if j.get("code") != 0:
        raise RuntimeError(f"ifzq {code} err: {j.get('code')} {j.get('msg','')}")
    info = j["data"][symbol]
    qfq = info.get("qfqday") or info.get("day") or []
    return [(row[0], float(row[2])) for row in qfq if len(row) >= 3]


def get_realtime_qt(codes: List[str]) -> Dict[str, Dict]:
    """拉腾讯 qt 实时价快照(GBK 编码),返回 {code: {name, cur, prev_close, ...}}"""
    qsyms = []
    for c in codes:
        market = "sh" if c.startswith(("5", "6")) else "sz"
        qsyms.append(f"{market}{c}")
    raw = http_get(QT_REALTIME_URL.format(codes=",".join(qsyms)), decode_gbk=True)
    out = {}
    for line in raw.strip().split(";"):
        if not line.strip():
            continue
        parts = line.split("=", 1)
        if len(parts) != 2:
            continue
        payload = parts[1].strip('"').split("~")
        if len(payload) < 6:
            continue
        out[payload[2]] = {
            "name": payload[1],
            "cur": float(payload[3]),
            "prev_close": float(payload[4]),
            "open": float(payload[5]),
        }
    return out


def calc_ma(closes: List[Tuple[str, float]]) -> Dict:
    """从 [(date, close), ...] 算 MA5/20/60 + 排列 + 5d/20d/60d 涨幅"""
    if not closes:
        return {}
    last_date, last_close = closes[-1]
    n = len(closes)
    ma5 = sum(c for _, c in closes[-5:]) / 5 if n >= 5 else None
    ma20 = sum(c for _, c in closes[-20:]) / 20 if n >= 20 else None
    ma60 = sum(c for _, c in closes[-60:]) / 60 if n >= 60 else None
    pct5 = (last_close / closes[-6][1] - 1) * 100 if n >= 6 else None
    pct20 = (last_close / closes[-21][1] - 1) * 100 if n >= 21 else None
    pct60 = (last_close / closes[-61][1] - 1) * 100 if n >= 61 else None
    align = "?"
    if ma5 and ma20 and ma60:
        if ma5 > ma20 > ma60:
            align = "🟢 BULL多头 MA5>MA20>MA60"
        elif ma5 < ma20 < ma60:
            align = "🔴 BEAR空头 MA5<MA20<MA60"
        else:
            align = "⚪ MIXED缠绕"
    return {
        "last_date": last_date,
        "close": last_close,
        "ma5": ma5, "ma20": ma20, "ma60": ma60,
        "pct5": pct5, "pct20": pct20, "pct60": pct60,
        "align": align,
    }


def load_holdings(path: str = DEFAULT_HOLDINGS_PATH) -> List[Dict]:
    with open(path, "r", encoding="utf-8") as f:
        d = json.load(f)
    return d.get("holdings", [])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--codes", default=None, help="逗号分隔 ETF 代码,默认从 holdings.json 读")
    ap.add_argument("--holdings", default=DEFAULT_HOLDINGS_PATH)
    ap.add_argument("--md", action="store_true", help="输出 markdown 表格")
    args = ap.parse_args()

    # 1. 决定标的列表
    holdings_map = {}
    if args.codes:
        codes = [c.strip() for c in args.codes.split(",")]
    else:
        try:
            hl = load_holdings(args.holdings)
            codes = [h["code"].replace(".SH", "").replace(".SZ", "") for h in hl]
            holdings_map = {h["code"].replace(".SH", "").replace(".SZ", ""): h for h in hl}
        except Exception as e:
            print(f"⚠️ 读 holdings.json 失败 ({e}),fallback 到空持仓", file=sys.stderr)
            codes = []

    if not codes:
        print("无标的,退出"); sys.exit(1)

    # 2. 拉 K 线
    results = {}
    for code in codes:
        try:
            closes = get_kline(code, 80)
            results[code] = calc_ma(closes)
        except Exception as e:
            results[code] = {"error": str(e)}

    # 3. 拉实时价(交叉验证)
    try:
        qt = get_realtime_qt(codes)
    except Exception as e:
        qt = {}
        print(f"⚠️ qt 实时价失败: {e}", file=sys.stderr)

    # 4. 输出
    if args.md:
        print("| ETF | 收盘 | MA5 | MA20 | MA60 | 5d | 20d | 60d | 排列 | 信号 |")
        print("|---|---|---|---|---|---|---|---|---|---|")
        for code in codes:
            r = results.get(code, {})
            if "error" in r:
                print(f"| {code} | err | - | - | - | - | - | - | - | {r['error']} |")
                continue
            qt_cur = qt.get(code, {}).get("cur")
            cur = qt_cur if qt_cur else r["close"]
            ma5 = r["ma5"]; ma20 = r["ma20"]; ma60 = r["ma60"]
            signal = []
            if r["close"] > ma5: signal.append(">MA5")
            if r["close"] > ma20: signal.append(">MA20")
            if r["close"] > ma60: signal.append(">MA60")
            sig_str = ",".join(signal) if signal else "全部<MA"
            print(f"| {code} | {cur:.3f} | {ma5:.3f} | {ma20:.3f} | {ma60:.3f} | "
                  f"{r['pct5']:+.2f}% | {r['pct20']:+.2f}% | {r['pct60']:+.2f}% | "
                  f"{r['align']} | {sig_str} |")
    else:
        for code in codes:
            r = results.get(code, {})
            if "error" in r:
                print(f"❌ {code}: {r['error']}")
                continue
            qt_cur = qt.get(code, {}).get("cur")
            cur = qt_cur if qt_cur else r["close"]
            print(f"\n=== {code} {qt.get(code, {}).get('name', '')} ===")
            print(f"  last: {r['last_date']}  close={cur:.3f}")
            print(f"  MA5={r['ma5']:.3f} MA20={r['ma20']:.3f} MA60={r['ma60']:.3f}")
            print(f"  5d={r['pct5']:+.2f}% 20d={r['pct20']:+.2f}% 60d={r['pct60']:+.2f}%")
            print(f"  align: {r['align']}")
            if code in holdings_map:
                h = holdings_map[code]
                pnl = h.get("floating_pnl_pct", 0) * 100
                print(f"  持仓: {h['shares']}股 @ ¥{h['cost']:.3f}  浮盈 {pnl:+.2f}%")


if __name__ == "__main__":
    main()