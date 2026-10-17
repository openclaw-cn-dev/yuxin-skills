#!/usr/bin/env python3
"""
cast_cokf_smoke.py — CAST 论文 CoKF cross-asset coupling 冒烟脚本
=============================================================

落地协议:pitfall-N+108(心跳 #N+97 2026-09-16 11:00 沉淀)
参考论文:arXiv 2609.14205 "CAST: Cross-Asset State-Space Trading System for Drawdown Control"

输入数据:boss 持仓的 N 只 ETF/股票 log returns(best via baostock)
输出:
  - L0 cross-asset coupling 短期/长期互相关
  - 每只资产 CoKF 残差 vol proxy (最近 window 日)
  - 短期 vs 长期耦合对比 + 红旗判定

依赖:numpy + baostock(可选,数据可从外部传入)
不需要 pykalman(规避 skbase 软依赖陷阱 pitfall-N+99)
"""

import sys
import numpy as np

try:
    import baostock as bs
    BAOSTOCK_OK = True
except ImportError:
    BAOSTOCK_OK = False


def cokf_run(y, Q_d=1e-5, R_d=1e-3):
    """双/多资产 CoKF — 自写 numpy 版本

    Args:
        y: shape (n, n_assets) log returns
        Q_d: 转移噪声方差(标量,各资产共享)
        R_d: 观测噪声方差(标量,各资产共享)
    Returns:
        states: shape (n, n_assets) 滤波后状态
    """
    n, n_assets = y.shape
    F = np.eye(n_assets); H = np.eye(n_assets)
    Q = np.eye(n_assets) * Q_d; R = np.eye(n_assets) * R_d
    x = y[0].copy(); P = np.eye(n_assets) * 0.01
    states = [x.copy()]
    for z in y[1:]:
        x = F @ x
        P = F @ P @ F.T + Q
        yres = z - H @ x
        S = H @ P @ H.T + R
        K = P @ H.T @ np.linalg.inv(S)
        x = x + K @ yres
        P = (np.eye(n_assets) - K @ H) @ P
        states.append(x.copy())
    return np.array(states)


def cross_asset_coupling(states, y, window=20):
    """计算 CoKF 残差互相关 + 最近 N 日耦合强度

    Args:
        states: cokf_run 输出, shape (n, n_assets)
        y: 原始 log returns, shape (n, n_assets)
        window: 短期窗口(默认 20 日)
    Returns:
        dict with:
          long_term_corr: 全样本残差互相关(n_assets=2 时)
          recent_corr: 最近 window 日残差互相关(n_assets=2 时)
          vol_proxy_recent: 每只资产最近 window 日 vol proxy
          ann_vol_recent: 年化 vol proxy
          coupling_jump: 短期 - 长期 互相关跃升(警告信号)
    """
    resid = y - states
    n_assets = y.shape[1]

    # 全样本互相关(只算 2 资产情形)
    if n_assets == 2:
        long_corr = float(np.corrcoef(resid[:, 0], resid[:, 1])[0, 1])
        recent = resid[-window:]
        recent_corr = float(np.corrcoef(recent[:, 0], recent[:, 1])[0, 1])
    else:
        long_corr = None
        recent_corr = None
        recent = resid[-window:]

    # 每只资产最近 window 日 vol proxy
    vol_proxy = np.sqrt((recent ** 2).mean(axis=0))
    ann_vol = vol_proxy * np.sqrt(252)

    # 耦合跃升
    coupling_jump = (recent_corr - long_corr) if (recent_corr is not None and long_corr is not None) else None

    return {
        'long_term_corr': long_corr,
        'recent_corr': recent_corr,
        'vol_proxy_recent': vol_proxy,
        'ann_vol_recent': ann_vol,
        'coupling_jump': coupling_jump,
    }


def fetch_baostock(codes, start='2025-01-01', end='2026-09-15'):
    """拉 N 只 ETF/股票最近收盘价,转 log returns 矩阵

    Args:
        codes: list of str, baostock 格式如 'sh.515220'
    Returns:
        log_rets: shape (n, len(codes)) 的 numpy 数组
        dates: pd.DatetimeIndex
    """
    if not BAOSTOCK_OK:
        raise ImportError("baostock not available; provide log_rets directly")

    import pandas as pd
    import time

    lg = bs.login()
    rows = []
    for code in codes:
        rs = bs.query_history_k_data_plus(
            code, 'date,close',
            start_date=start, end_date=end,
            frequency='d', adjustflag='2'
        )
        while rs.error_code == '0' and rs.next():
            rd = rs.get_row_data()
            # pitfall-N+109: rs.next() 可能先返回元数据行,len<2 跳过
            if len(rd) < 2 or rd[1] == '':
                continue
            try:
                rows.append({'code': code, 'date': rd[0], 'close': float(rd[1])})
            except (ValueError, IndexError):
                continue
        time.sleep(2)  # pitfall #33 baostock 限速
    bs.logout()

    df = pd.DataFrame(rows)
    df['date'] = pd.to_datetime(df['date'])
    df = df.pivot(index='date', columns='code', values='close').dropna()
    log_rets = np.log(df / df.shift(1)).dropna().values
    return log_rets, df.index


def run_smoke(codes=None, start='2025-01-01', end='2026-09-15', window=20):
    """主入口:跑完整 CoKF cross-asset coupling 冒烟

    Args:
        codes: list of baostock codes, 默认 boss 持仓 2 ETF
        start/end: 日期范围
        window: 短期窗口
    Returns:
        report dict
    """
    if codes is None:
        codes = ['sh.515220', 'sh.512710']  # boss 默认持仓

    print(f"=== CoKF Cross-Asset Coupling Smoke ===")
    print(f"Codes: {codes}")
    print(f"Period: {start} ~ {end}")
    print(f"Window: {window} days")
    print()

    # 1. 拉数据
    log_rets, dates = fetch_baostock(codes, start, end)
    print(f"n_obs: {log_rets.shape[0]}  n_assets: {log_rets.shape[1]}")
    print(f"date range: {dates[0].date()} ~ {dates[-1].date()}")
    print()

    # 2. CoKF 滤波
    states = cokf_run(log_rets)

    # 3. cross-asset coupling
    report = cross_asset_coupling(states, log_rets, window=window)

    print(f"--- CoKF Residue Coupling ---")
    if report['long_term_corr'] is not None:
        print(f"Long-term corr (all sample): {report['long_term_corr']:+.3f}")
    print(f"Recent  corr ({window}d):      {report['recent_corr']:+.3f}")
    if report['coupling_jump'] is not None:
        print(f"Coupling jump (recent - long): {report['coupling_jump']:+.3f}")
    print()
    print(f"--- CoKF Residue Vol Proxy (recent {window}d) ---")
    for i, code in enumerate(codes):
        print(f"  {code}: vol_proxy={report['vol_proxy_recent'][i]*100:.3f}%/d  ann_vol={report['ann_vol_recent'][i]*100:.2f}%/year")
    print()

    # 4. 红旗判定
    alerts = []
    if report['recent_corr'] is not None:
        if report['recent_corr'] > 0.50:
            alerts.append(f"🚨 短期互相关 {report['recent_corr']:+.3f} > 0.50 — 强红灯,组合减仓预警")
        elif report['recent_corr'] > 0.30:
            alerts.append(f"⚠️ 短期互相关 {report['recent_corr']:+.3f} > 0.30 — 红旗,联合下行风险")
    if report['coupling_jump'] is not None and report['coupling_jump'] > 0.30:
        alerts.append(f"⚠️ 耦合跃升 {report['coupling_jump']:+.3f} > 0.30 — 短期耦合破坏分散化")

    print(f"--- Alerts ---")
    if alerts:
        for a in alerts:
            print(f"  {a}")
    else:
        print(f"  ✅ 短期耦合正常,无红旗")
    print()

    return report


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='CoKF Cross-Asset Coupling Smoke (pitfall-N+108)')
    parser.add_argument('--codes', nargs='+', default=['sh.515220', 'sh.512710'],
                        help='baostock codes list')
    parser.add_argument('--start', default='2025-01-01')
    parser.add_argument('--end', default='2026-09-15')
    parser.add_argument('--window', type=int, default=20)
    args = parser.parse_args()

    try:
        run_smoke(codes=args.codes, start=args.start, end=args.end, window=args.window)
    except Exception as e:
        print(f"❌ SMOKE FAILED: {type(e).__name__}: {e}", file=sys.stderr)
        sys.exit(1)