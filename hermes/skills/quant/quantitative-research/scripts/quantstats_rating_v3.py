#!/usr/bin/env python3
"""
quantstats_rating_v3.py — N+139 v3 三级阈值评级函数
心跳 #N+119 实测沉淀,2026-09-18 04:38

用法:
    import quantstats_rating_v3 as qsr
    stats = qsr.rate(rets, max_dd_threshold=0.30)
    print(f"Sharpe {stats['sharpe']:+.3f} → {stats['rating']} (actionable {stats['actionable_pct']*100:.0f}%)")

依赖: quantstats 0.0.77+, numpy, pandas
"""
import warnings
warnings.filterwarnings('ignore')

import numpy as np
import pandas as pd
import quantstats as qs


def rate(rets: pd.Series, max_dd_severe: float = -0.30) -> dict:
    """
    N+139 v3 三级阈值评级
    
    输入:
        rets: pd.Series 日收益率(可含 NaN,会自动 dropna)
        max_dd_severe: max_dd 严重阈值(默认 -30%),Sharpe<-2.0 + max_dd<threshold → 🚨🚨🚨
    
    输出: dict with keys:
        sharpe: float(round 3)
        sortino: float(round 3)
        max_dd: float(round 2, 百分比形式 如 -36.69)
        ann_vol: float(round 2, 百分比)
        n: int(样本量,>=100 时评级稳态)
        rating: str(🟢/🟡/⚠️/🚨/🚨🚨/🚨🚨🚨)
        actionable_pct: float(0.0/0.25/0.50/0.75,N+139 v3 actionable 触发比例)
        reason: str(评级理由,用于 evolution 报告记录)
    """
    rets = rets.dropna()
    n = len(rets)
    
    # n 不足时降级到 N+136 v1 阈值(沿用 N+139 §7 盲点 1)
    downgrade = n < 100
    
    sharpe = qs.stats.sharpe(rets)
    sortino = qs.stats.sortino(rets)
    max_dd = qs.stats.max_drawdown(rets)  # float 负值
    ann_vol = rets.std() * np.sqrt(252) * 100  # 百分比
    
    if downgrade:
        # n<100 降级 v1 阈值
        if sharpe >= 0.5:
            rating = '🟢'
            actionable = 0.0
            reason = f'n={n}<100 降级 v1: Sharpe 健康'
        elif sharpe >= 0:
            rating = '🟡'
            actionable = 0.0
            reason = f'n={n}<100 降级 v1: Sharpe 关注'
        elif sharpe >= -0.5:
            rating = '⚠️'
            actionable = 0.0  # 降级 v1: 仅观测,不下 actionable
            reason = f'n={n}<100 降级 v1: Sharpe 警告'
        else:
            rating = '🚨'
            actionable = 0.50  # 降级 v1: 减仓 50%(不升级到 🚨🚨)
            reason = f'n={n}<100 降级 v1: Sharpe 危险'
    else:
        # n>=100 走 N+139 v3 三级阈值
        if sharpe >= 0.5:
            rating = '🟢'
            actionable = 0.0
            reason = 'Sharpe ≥+0.50 健康'
        elif sharpe >= 0:
            rating = '🟡'
            actionable = 0.0
            reason = 'Sharpe 0~+0.50 关注'
        elif sharpe >= -0.5:
            rating = '⚠️'
            actionable = 0.25
            reason = 'Sharpe -0.5~0 警告(N+139 新增 actionable 25%)'
        elif sharpe >= -1.0:
            rating = '🚨'
            actionable = 0.50
            reason = 'Sharpe -1.0~-0.5 危险'
        elif sharpe >= -2.0:
            rating = '🚨🚨'
            actionable = 0.50
            reason = 'Sharpe <-1.0(N+139 v3 新增 🚨🚨)'
        else:
            # Sharpe < -2.0
            if max_dd < max_dd_severe:
                rating = '🚨🚨🚨'
                # N+139 v3 补丁:严重度足够单独 actionable,跳过 N+138 ≥2 维度叠加
                actionable = 0.75
                reason = f'Sharpe<-2.0 + max_dd<{max_dd_severe*100:.0f}% 单信号 75% 减仓(N+139 v3 核心补丁)'
            else:
                rating = '🚨🚨🚨'
                actionable = 0.50  # max_dd 不够深,仍走 N+138 ≥2 维度
                reason = 'Sharpe<-2.0 但 max_dd 不够深,需叠加 L0+L3 信号'
    
    return {
        'sharpe': round(sharpe, 3),
        'sortino': round(sortino, 3),
        'max_dd': round(max_dd * 100, 2),
        'ann_vol': round(ann_vol, 2),
        'n': n,
        'rating': rating,
        'actionable_pct': actionable,
        'reason': reason,
        'downgrade': downgrade,
    }


def rate_portfolio(rets_dict: dict, weights: list) -> dict:
    """
    组合 quantstats 评级(N+136 §2 联动:组合分散化救场)
    
    输入:
        rets_dict: dict {code: pd.Series},各 ETF 日收益率
        weights: list[float],对应权重(和为 1)
    
    输出: dict 含 portfolio_sharpe / single_ratings / dispersion_check
    """
    codes = list(rets_dict.keys())
    weights = np.array(weights)
    
    # 单只评级
    single_ratings = {c: rate(rets_dict[c]) for c in codes}
    
    # 组合收益率
    portfolio_rets = sum(weights[i] * rets_dict[c] for i, c in enumerate(codes))
    portfolio_stats = rate(portfolio_rets)
    
    # N+136 联动判定:组合 Sharpe vs 单只 Sharpe 差距
    sharpe_gap = portfolio_stats['sharpe'] - min(r['sharpe'] for r in single_ratings.values())
    
    return {
        'portfolio': portfolio_stats,
        'singles': single_ratings,
        'sharpe_gap': round(sharpe_gap, 3),
        'note': '组合 Sharpe 显著高于单只 → 分散化救场;反之组合救不了'
    }


if __name__ == '__main__':
    # 自检 — 用 #N+119 boss 512710 实测样本特征(模拟)
    print("=== N+139 v3 自检 ===\n")
    
    # 测试 1: boss 512710 实测特征(Sharpe=-2.057, max_dd=-36.69%)
    np.random.seed(42)
    n = 138
    daily_vol = 0.029 / np.sqrt(252)  # ann_vol 29%
    drift = -0.001  # 负 drift
    rets_test = pd.Series(np.random.normal(drift, daily_vol, n))
    # 强制制造一个 -36% 的回撤
    rets_test.iloc[60:65] = -0.08  # 5 日连续大跌
    stats = rate(rets_test)
    print(f"测试 1(512710 模拟): Sharpe {stats['sharpe']} → {stats['rating']} "
          f"actionable {stats['actionable_pct']*100:.0f}%")
    print(f"  理由: {stats['reason']}")
    print(f"  n={stats['n']} downgrade={stats['downgrade']}")
    
    # 测试 2: 边界 Sharpe=-1.0
    rets_test2 = pd.Series(np.random.normal(0, daily_vol, n))
    stats2 = rate(rets_test2)
    print(f"\n测试 2(健康模拟): Sharpe {stats2['sharpe']} → {stats2['rating']} "
          f"actionable {stats2['actionable_pct']*100:.0f}%")
    
    # 测试 3: n<100 降级
    rets_test3 = pd.Series(np.random.normal(0, daily_vol, 80))
    stats3 = rate(rets_test3)
    print(f"\n测试 3(n=80 降级): Sharpe {stats3['sharpe']} → {stats3['rating']} "
          f"actionable {stats3['actionable_pct']*100:.0f}% (downgrade={stats3['downgrade']})")