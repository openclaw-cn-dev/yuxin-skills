#!/usr/bin/env python3
"""
four_layer_risk_budget.py — 渔芯猎手 4 层 Risk Budget 全链路 (心跳 #N+58 沉淀)

四层分工:
  L1 事件 — ruptures Pelt (BIC penalty, pitfall #42)
  L2 状态 — hmmlearn GaussianHMM (winsorize ±5%, pitfall #34)
  L3 波动 — GJR-GARCH Student-t (pd.Series 输入, pitfall #39)
  L4 价格 — pykalman 一维 KF (EM-fit Q/R, pitfall #N+57 + N+58)

实战验证: boss 2 ETF (515220 煤炭 + 512710 军工龙头) 2026-09-12
- L1: 双 ETF 末断点同 2026-08-10 (regime shift 共现)
- L2: 168d × 2 ETF 全部失效 → 降级为 monitor (pitfall #41)
- L3: 515220 ann_vol 36.16% / 512710 ann_vol 29.68% (高频,日级重平衡)
- L4: 双 ETF |z| < 0.5 → 价格层稳定

Usage:
    # 默认跑 boss 当前 2 ETF
    python3 scripts/four_layer_risk_budget.py

    # 自定义 ETF 列表
    python3 scripts/four_layer_risk_budget.py --codes sh.518880,sz.159945

    # 自定义时间窗口
    python3 scripts/four_layer_risk_budget.py --start 2024-09-01 --end 2026-09-11
"""

import argparse
import json
import sys
import time
import warnings

warnings.filterwarnings("ignore")

# === pitfall-N+58 patch: monkey-patch importlib.metadata.version ===
# pykalman 0.10.2 → skbase 0.12.6 → utils/_numpy.py soft-dep 查 numpy>=2
# 时扫所有包撞未装的 backports.asyncio.runner → PackageNotFoundError
# → 整个 import 链失败。修复: import pykalman 之前必须先 monkey-patch。
import importlib.metadata

_orig_version = importlib.metadata.version


def _safe_version(name):
    try:
        return _orig_version(name)
    except importlib.metadata.PackageNotFoundError:
        return "0.0.0"


importlib.metadata.version = _safe_version
# === patch end ===

import numpy as np
import pandas as pd
import baostock as bs
from arch import arch_model
import ruptures as rpt
from hmmlearn.hmm import GaussianHMM
from pykalman import KalmanFilter

DEFAULT_CODES = ["sh.515220", "sh.512710"]  # boss 当前 2 ETF
DEFAULT_START = "2025-03-01"  # ≈ 6 个月窗口(boss 当前持仓 < 200d)
DEFAULT_END = "2026-09-11"


def fetch_closes(code_full, start, end):
    """拉日线收盘价 (pitfall #32 #33 #36)"""
    bs.login()
    rs = bs.query_history_k_data_plus(
        code_full,
        "date,close",
        start_date=start,
        end_date=end,
        frequency="d",
        adjustflag="2",
    )
    rows = []
    while rs.error_code == "0" and rs.next():
        rows.append(rs.get_row_data())
    bs.logout()
    time.sleep(2)  # pitfall #33

    df = pd.DataFrame(rows, columns=["date", "close"])
    df["close"] = df["close"].astype(float)
    df["date"] = pd.to_datetime(df["date"])
    df.set_index("date", inplace=True)
    return df


def layer1_ruptures(df):
    """L1 事件 — ruptures Pelt + BIC penalty (pitfall #42)"""
    closes = df["close"].values
    algo = rpt.Pelt(model="rbf", min_size=20, jump=5).fit(closes)
    pen = np.log(len(closes)) * np.var(closes)
    bkps = algo.predict(pen=pen)
    if bkps and bkps[-1] == len(closes):
        bkps = bkps[:-1]
    last_bk_date = str(df.index[bkps[-1] - 1].date()) if bkps else None
    return {"n_bkps": len(bkps), "bkps": bkps, "last_bk_date": last_bk_date}


def layer2_hmmlearn(df):
    """L2 状态 — GaussianHMM + winsorize ±5% (pitfall #34 #41)"""
    log_rets = np.log(df["close"] / df["close"].shift(1)).dropna()
    log_rets_w = np.clip(log_rets, -0.05, 0.05).values.reshape(-1, 1)
    n_sample = len(log_rets_w)
    hmm = GaussianHMM(
        n_components=2, covariance_type="diag", n_iter=300, random_state=42
    )
    hmm.fit(log_rets_w)
    states = hmm.predict(log_rets_w)
    fracs = [(states == i).sum() / len(states) for i in range(2)]
    return {
        "n_sample": n_sample,
        "cur_state": int(states[-1]),
        "fracs": fracs,
        "outlier_warning": any(f < 0.05 for f in fracs),
        "tiny_sample_warning": n_sample < 200,
    }


def layer3_garch(df):
    """L3 波动 — GJR-GARCH Student-t (pd.Series + DatetimeIndex, pitfall #39)"""
    log_rets_pct = np.log(df["close"] / df["close"].shift(1)).dropna() * 100
    log_rets_pct.index = df.index[1:]
    res = arch_model(
        log_rets_pct, mean="Constant", vol="GARCH", p=1, o=1, q=1, dist="t"
    ).fit(disp="off")
    omega = res.params["omega"]
    alpha = res.params["alpha[1]"]
    beta = res.params["beta[1]"]
    gamma = res.params["gamma[1]"]
    persistence = alpha + beta + gamma / 2
    half_life = (
        -np.log(2) / np.log(persistence) if persistence < 1 else float("inf")
    )
    cur_vol_daily = res.conditional_volatility.iloc[-1] / 100
    cur_vol_ann = cur_vol_daily * np.sqrt(252)
    return {
        "persistence": float(persistence),
        "half_life_d": float(half_life),
        "cur_vol_daily": float(cur_vol_daily),
        "cur_vol_ann": float(cur_vol_ann),
        "VaR95": float(-1.645 * cur_vol_daily),
    }


def layer4_pykalman(df):
    """L4 价格 — KalmanFilter + monkey-patched import + ndarray shape 修正"""
    closes = df["close"].values
    kf = KalmanFilter(
        transition_matrices=[1],
        observation_matrices=[1],
        initial_state_mean=closes[0],
        initial_state_covariance=1,
    )
    kf = kf.em(closes, n_iter=20)  # pitfall-N+57: 必须 EM 拟合 Q/R
    state_means, state_covs = kf.filter(closes)
    last_price = float(closes[-1])
    # pitfall-N+58: ndarray shape 修正
    last_smooth = float(np.atleast_1d(state_means[-1])[0])
    smooth_std = float(np.sqrt(np.atleast_2d(state_covs[-1])[0, 0]))
    z_score = (last_price - last_smooth) / smooth_std if smooth_std > 0 else 0.0
    dev_pct = (last_smooth - last_price) / last_price * 100
    return {
        "last_price": last_price,
        "smooth_price": last_smooth,
        "smooth_std": smooth_std,
        "z_score": float(z_score),
        "dev_pct": float(dev_pct),
    }


def joint_decision(L1, L2, L3, L4):
    """四层联合决策表"""
    has_break = L1["n_bkps"] > 0
    cur_state = L2["cur_state"]
    high_vol = L3["cur_vol_ann"] > 0.25
    z_signal = abs(L4["z_score"]) > 2

    if has_break and cur_state == 1 and high_vol:
        action = "🔴 防御+减仓"
    elif not has_break and cur_state == 0 and not high_vol:
        action = "🟢 加码"
    elif not has_break and cur_state == 0 and high_vol:
        action = "🟡 维持+观察"
    elif has_break and cur_state == 0:
        action = "🟡 谨慎加码"
    else:
        action = "🟠 减仓预警"
    return {
        "L1_break": has_break,
        "L2_state": cur_state,
        "L3_high_vol": high_vol,
        "L4_z_signal": z_signal,
        "action": action,
    }


def run_one(code_full, start, end):
    code = code_full.split(".")[1]
    print(f"\n{'=' * 60}\n[{code_full}] 四层 Risk Budget\n{'=' * 60}")
    df = fetch_closes(code_full, start, end)
    print(f"  数据: {len(df)}d, {df.index[0].date()} ~ {df.index[-1].date()}")

    L1 = layer1_ruptures(df)
    print(f"  L1 ruptures: {L1['n_bkps']} 断点, 末断点 {L1['last_bk_date']}")

    L2 = layer2_hmmlearn(df)
    print(
        f"  L2 hmmlearn: state={L2['cur_state']} fracs={L2['fracs']} "
        f"tiny_warn={L2['tiny_sample_warning']}"
    )

    L3 = layer3_garch(df)
    print(
        f"  L3 GJR-GARCH: half-life={L3['half_life_d']:.2f}d "
        f"ann_vol={L3['cur_vol_ann'] * 100:.2f}% VaR95={L3['VaR95'] * 100:.3f}%"
    )

    L4 = layer4_pykalman(df)
    print(
        f"  L4 pykalman: price={L4['last_price']:.4f} "
        f"smooth={L4['smooth_price']:.4f} z={L4['z_score']:.3f}"
    )

    decision = joint_decision(L1, L2, L3, L4)
    print(f"  → {decision['action']}")

    return {"L1": L1, "L2": L2, "L3": L3, "L4": L4, "decision": decision}


def main():
    parser = argparse.ArgumentParser(description="渔芯猎手 4 层 Risk Budget")
    parser.add_argument(
        "--codes",
        default=",".join(DEFAULT_CODES),
        help=f"ETF 代码逗号分隔 (默认 {','.join(DEFAULT_CODES)})",
    )
    parser.add_argument("--start", default=DEFAULT_START)
    parser.add_argument("--end", default=DEFAULT_END)
    parser.add_argument("--out", default=None, help="结果 JSON 输出路径")
    args = parser.parse_args()

    codes = [c.strip() for c in args.codes.split(",")]
    results = {}
    for code_full in codes:
        results[code_full] = run_one(code_full, args.start, args.end)

    print(f"\n{'=' * 60}\n四层联合决策汇总\n{'=' * 60}")
    for code_full, r in results.items():
        d = r["decision"]
        print(
            f"  {code_full}: {d['action']} "
            f"(L1_break={d['L1_break']} L2_state={d['L2_state']} "
            f"L3_high_vol={d['L3_high_vol']} L4_z={r['L4']['z_score']:.2f})"
        )

    if args.out:
        with open(args.out, "w") as f:
            json.dump(results, f, indent=2, default=str)
        print(f"\n✅ 结果保存到 {args.out}")
    else:
        print("\n(用 --out <path.json> 保存结果)")


if __name__ == "__main__":
    main()