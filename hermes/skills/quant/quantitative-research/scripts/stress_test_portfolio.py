#!/usr/bin/env python3
"""
通用 4 场景压力测试脚本 — ***SECRET*** v1.0

用法:
    python3 stress_test_portfolio.py \\
        --config '{"Bank_ETF_512800": {"weight": 0.1874, "vol": 0.18, "ret": 0.10}, ...}' \\
        --corr path/to/corr.csv \\
        --n-paths 2000 \\
        --n-days 21

或作为模块导入:
    from stress_test_portfolio import stress_test_pipeline
    results = stress_test_pipeline(weights, vols, rets, corr_matrix, scenarios=DEFAULT_SCENARIOS)
"""

import numpy as np
import json
import sys
from dataclasses import dataclass, asdict
from typing import Dict, List


# ============================================
# 4 场景默认配置 (来自心跳 #N+38)
# ============================================

DEFAULT_SCENARIOS = {
    "S1_baseline_neutral": {
        "ret_mult": 1.0, "vol_mult": 1.0, "corr_shock": 0.0,
        "description": "基准中性",
    },
    "S2_global_deleveraging": {
        "ret_mult": 0.5, "vol_mult": 1.4, "corr_shock": 0.30,
        "description": "全球避险 + 流动性紧缩 + 相关性爆炸",
    },
    "S3_policy_stimulus": {
        "ret_mult": 1.4, "vol_mult": 0.9, "corr_shock": -0.10,
        "description": "财政货币双刺激 + 周期领涨",
    },
    "S4_bond_rally_rotation": {
        "ret_mult": 0.8, "vol_mult": 1.1, "corr_shock": -0.15,
        "description": "债市轮动 + 防御独立",
    },
}


# ============================================
# 核心函数
# ============================================

def simulate_scenario(weights, vols, rets, corr_matrix,
                     n_paths=2000, n_days=21, seed=42):
    """Bootstrap Monte Carlo 模拟单场景"""
    rng = np.random.default_rng(seed)
    n_assets = len(weights)
    daily_rets = np.array(rets) / 252
    daily_vols = np.array(vols) / np.sqrt(252)
    cov = np.outer(daily_vols, daily_vols) * corr_matrix
    # 正则化防近奇异
    L = np.linalg.cholesky(cov + np.eye(n_assets) * 1e-8)
    paths = np.ones((n_paths, n_days + 1))
    for t in range(1, n_days + 1):
        z = rng.standard_normal((n_paths, n_assets))
        asset_rets = daily_rets + (L @ z.T).T
        port_ret = asset_rets @ weights
        paths[:, t] = paths[:, t-1] * (1 + port_ret)
    return paths


def stress_metrics(paths):
    """计算 8 个核心指标"""
    final_values = paths[:, -1]
    drawdowns = 1 - paths / np.maximum.accumulate(paths, axis=1)
    port_returns = paths[:, 1:] / paths[:, :-1] - 1
    return {
        "expected_return_pct": round(float(np.mean(final_values - 1) * 100), 2),
        "median_return_pct": round(float(np.median(final_values - 1) * 100), 2),
        "VaR_5_pct": round(float(np.percentile(final_values - 1, 5) * 100), 2),
        "CVaR_5_pct": round(float(np.mean(final_values[final_values <= np.percentile(final_values, 5)] - 1) * 100), 2),
        "max_drawdown_avg_pct": round(float(np.mean(np.max(drawdowns, axis=1)) * 100), 2),
        "max_drawdown_worst_pct": round(float(np.max(np.max(drawdowns, axis=1)) * 100), 2),
        "probability_loss_pct": round(float(np.mean(final_values < 1.0) * 100), 1),
        "sharpe_ratio": round(float(np.mean(port_returns) / (np.std(port_returns) + 1e-8) * np.sqrt(252)), 2),
    }


def apply_corr_shock(corr_matrix, shock):
    """应用相关性冲击（保留对角线=1.0）"""
    n = len(corr_matrix)
    adj = corr_matrix.copy()
    for i in range(n):
        for j in range(n):
            if i != j:
                adj[i, j] = np.clip(adj[i, j] + shock, -0.95, 0.95)
    np.fill_diagonal(adj, 1.0)
    return adj


def stress_test_pipeline(weights, vols, rets, corr_matrix,
                         scenarios=None, n_days=21, n_paths=2000, seed=42):
    """4 场景压力测试完整 pipeline"""
    if scenarios is None:
        scenarios = DEFAULT_SCENARIOS
    results = {}
    for s_name, s_params in scenarios.items():
        adj_rets = np.array(rets) * s_params["ret_mult"]
        adj_vols = np.array(vols) * s_params["vol_mult"]
        adj_corr = apply_corr_shock(corr_matrix, s_params["corr_shock"])
        paths = simulate_scenario(weights, adj_vols, adj_rets, adj_corr,
                                  n_paths=n_paths, n_days=n_days, seed=seed)
        results[s_name] = {
            "description": s_params["description"],
            "metrics": stress_metrics(paths),
        }
    return results


def decision_gate(results):
    """决策门禁：返回 (verdict, details)"""
    avg_sharpe = np.mean([r["metrics"]["sharpe_ratio"] for r in results.values()])
    worst_cvar = min(r["metrics"]["CVaR_5_pct"] for r in results.values())
    worst_dd = max(r["metrics"]["max_drawdown_worst_pct"] for r in results.values())

    if avg_sharpe > 0.5 and worst_cvar > -10 and worst_dd < 20:
        verdict = "✅ DEPLOY_FULL"
        scale = 1.0
    elif avg_sharpe > 0.3:
        verdict = "⚠️ DEPLOY_HALF"
        scale = 0.5
    else:
        verdict = "❌ DELAY"
        scale = 0.0
    return verdict, {
        "avg_sharpe": round(avg_sharpe, 2),
        "worst_cvar_5_pct": round(worst_cvar, 2),
        "worst_max_dd_pct": round(worst_dd, 2),
        "deploy_scale": scale,
    }


# ============================================
# CLI 入口
# ============================================

if __name__ == "__main__":
    # Demo: 8 ETF 案例（来自心跳 #N+38）
    weights = np.array([0.1874, 0.1874, 0.1500, 0.0726, 0.0170, 0.3856])  # 银行/黄金/证券/煤炭/军工/现金
    vols = np.array([0.18, 0.14, 0.28, 0.35, 0.32, 0.01])
    rets = np.array([0.10, 0.07, 0.14, 0.12, 0.10, 0.015])
    corr = np.array([
        [1.00, -0.10,  0.62, -0.34,  0.45,  0.00],
        [-0.10,  1.00,  0.05,  0.15, -0.05,  0.00],
        [0.62,  0.05,  1.00,  0.20,  0.55,  0.00],
        [-0.34, 0.15,  0.20,  1.00,  0.30,  0.00],
        [0.45, -0.05,  0.55,  0.30,  1.00,  0.00],
        [0.00,  0.00,  0.00,  0.00,  0.00,  1.00],
    ])

    results = stress_test_pipeline(weights, vols, rets, corr)
    verdict, details = decision_gate(results)

    print(f"\n=== 决策门禁 ===\n{verdict}")
    print(f"Details: {details}")
    print(f"\n=== 4 场景明细 ===")
    for s, r in results.items():
        print(f"\n{s} ({r['description']}):")
        for k, v in r["metrics"].items():
            print(f"  {k}: {v}")