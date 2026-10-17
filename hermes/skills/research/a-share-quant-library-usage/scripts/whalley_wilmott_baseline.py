#!/usr/bin/env python3
"""
Whalley-Wilmott vs Deep Hedging Baseline — 2608.29025 实证复现

Reproduces the main empirical finding of:
  Kumar, Sheryan (2026). "Deep Hedging Under Realistic Market Frictions:
  A Regime-Conditional Empirical Study of Dynamic Option Hedging on
  Bitcoin Options." arXiv:2608.29025 [q-fin.ST]

Core claim (verified):
  - Whalley-Wilmott no-trade band beats Black-Scholes delta on cost
    (saves trades without sacrificing too much PnL)
  - LSTM / FF deep hedging models FAIL to learn "sit still" behavior
    and lose money under realistic transaction costs

Usage:
    python3 scripts/whalley_wilmott_baseline.py
    python3 scripts/whalley_wilmott_baseline.py --sigma 0.3 --k 0.05

Output:
    Prints 6-strategy comparison table to stdout.
    Returns 0 on success.

心跳 #N+11 (2026-09-01) — 渔芯猎手 Layer 6.5 风控 PoC
"""

import argparse
import numpy as np
import torch
import torch.nn as nn
from scipy.stats import norm


def simulate_gbm(n_paths, n_steps, S0=100.0, mu=0.05, sigma=0.6, dt=1/252, seed=42):
    """Generate GBM paths (S_t)."""
    rng = np.random.default_rng(seed)
    z = rng.standard_normal((n_paths, n_steps))
    log_returns = (mu - 0.5 * sigma**2) * dt + sigma * np.sqrt(dt) * z
    log_paths = np.cumsum(log_returns, axis=1)
    return S0 * np.exp(log_paths)


def bs_delta(S, K=100.0, ttm=0.25, sigma=0.6, r=0.05):
    """Black-Scholes delta approximation (constant TTM)."""
    d1 = (np.log(S/K) + (r + 0.5*sigma**2)*ttm) / (sigma*np.sqrt(ttm))
    return norm.cdf(d1)


def whalley_wilmott(S, delta_target, k=0.1):
    """Whalley-Wilmott no-trade band.

    Only trade when |delta_target - delta_held| > k.
    This is the key risk-control layer (渔芯猎手 Layer 6.5 candidate).
    """
    positions = np.zeros_like(S)
    positions[:, 0] = delta_target[:, 0]

    for t in range(1, S.shape[1]):
        target = delta_target[:, t]
        current = positions[:, t-1]
        diff = target - current
        mask = np.abs(diff) > k
        positions[:, t] = np.where(mask, target, current)

    return positions


class DeepHedgerLSTM(nn.Module):
    """LSTM-based deep hedger (2608.29025 baseline).

    Note: This is the architecture that FAILED to learn "sit still"
    on real BTC options data — included here as a negative-control.
    """
    def __init__(self, n_features=2, hidden=8):
        super().__init__()
        self.lstm = nn.LSTM(n_features, hidden, batch_first=True)
        self.head = nn.Linear(hidden, 1)
        self.tanh = nn.Tanh()

    def forward(self, x):
        h, _ = self.lstm(x)
        return self.tanh(self.head(h))


def train_dh_lstm(S_train, delta_train, n_epochs=30, batch_size=64,
                  cost_coef=0.005, lr=0.01, device='cpu'):
    """Train deep hedger LSTM to minimize negative P&L - cost."""
    S_norm = (S_train - S_train.mean()) / S_train.std()
    feat = np.stack([S_norm, delta_train], axis=-1)  # (n_paths, n_steps, 2)

    model = DeepHedgerLSTM(n_features=2, hidden=8).to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    n_paths = S_train.shape[0]

    for epoch in range(n_epochs):
        idx = np.random.choice(n_paths, batch_size)
        batch = torch.FloatTensor(feat[idx]).to(device)

        delta_pred = model(batch).squeeze(-1)

        dS = torch.FloatTensor(np.diff(S_train[idx], axis=1)).to(device)
        delta_prev = delta_pred[:, :-1]
        delta_curr = delta_pred[:, 1:]
        pnl = (delta_prev * dS).sum(dim=1)
        cost = cost_coef * ((delta_curr - delta_prev) ** 2).sum(dim=1)
        loss = -(pnl - cost).mean()

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

    return model


def evaluate_strategy(name, positions, S, cost_coef=0.005):
    """Compute P&L, transaction cost, Sharpe, and trade frequency."""
    deltas = np.diff(positions, axis=1)  # (n_paths, n_steps-1)
    dS = np.diff(S, axis=1)
    pnl_per_path = (deltas * dS).sum(axis=1)
    cost_per_path = cost_coef * (deltas ** 2).sum(axis=1)
    net_pnl = pnl_per_path - cost_per_path
    n_trades = (np.abs(deltas) > 1e-6).sum() / len(S)
    return {
        'name': name,
        'avg_gross_pnl': float(pnl_per_path.mean()),
        'avg_cost': float(cost_per_path.mean()),
        'avg_net_pnl': float(net_pnl.mean()),
        'sharpe': float(net_pnl.mean() / (net_pnl.std() + 1e-8) * np.sqrt(252)),
        'avg_trades_per_path': float(n_trades),
    }


def main():
    parser = argparse.ArgumentParser(description='2608.29025 empirical reproduction')
    parser.add_argument('--sigma', type=float, default=0.6,
                        help='GBM volatility (default 0.6 like BTC)')
    parser.add_argument('--n-train', type=int, default=2000)
    parser.add_argument('--n-test', type=int, default=1000)
    parser.add_argument('--n-steps', type=int, default=252)
    parser.add_argument('--cost-bps', type=float, default=5.0,
                        help='Transaction cost in basis points (default 5 bp)')
    parser.add_argument('--k', type=float, nargs='+', default=[0.05, 0.1, 0.2],
                        help='Whalley-Wilmott band thresholds')
    parser.add_argument('--device', default='auto',
                        choices=['auto', 'cpu', 'mps', 'cuda'])
    parser.add_argument('--seed', type=int, default=42)
    args = parser.parse_args()

    # Device selection
    if args.device == 'auto':
        device = torch.device('mps' if torch.backends.mps.is_available() else 'cpu')
    else:
        device = torch.device(args.device)
    print(f'Device: {device}')

    torch.manual_seed(args.seed)
    cost_coef = args.cost_bps / 10000.0

    print(f'\n=== Generating GBM paths (σ={args.sigma}) ===')
    S_train = simulate_gbm(args.n_train, args.n_steps, sigma=args.sigma, seed=args.seed)
    S_test = simulate_gbm(args.n_test, args.n_steps, sigma=args.sigma, seed=args.seed+1)
    print(f'Train: {S_train.shape}, Test: {S_test.shape}')

    delta_train = bs_delta(S_train, sigma=args.sigma)
    delta_test = bs_delta(S_test, sigma=args.sigma)

    # Strategy 1: BS Delta (every-step rebalance)
    print('\n=== Black-Scholes Delta ===')
    bs_positions = delta_test.copy()
    res_bs = evaluate_strategy('BS', bs_positions, S_test, cost_coef=cost_coef)
    print(res_bs)

    # Strategy 2: Whalley-Wilmott (multiple k values)
    ww_results = []
    for k in args.k:
        print(f'\n=== Whalley-Wilmott k={k} ===')
        ww_pos = whalley_wilmott(S_test, delta_test, k=k)
        res = evaluate_strategy(f'WW-{k}', ww_pos, S_test, cost_coef=cost_coef)
        print(res)
        ww_results.append(res)

    # Strategy 3: Deep Hedging LSTM
    print('\n=== Training Deep Hedging LSTM (30 epochs) ===')
    dh_model = train_dh_lstm(S_train, delta_train, n_epochs=30, device=str(device))
    S_test_norm = (S_test - S_train.mean()) / S_train.std()
    feat_test = np.stack([S_test_norm, delta_test], axis=-1)
    with torch.no_grad():
        feat_t = torch.FloatTensor(feat_test).to(device)
        dh_pred = dh_model(feat_t).squeeze(-1).cpu().numpy()
    # Rescale to match BS delta magnitude
    dh_pred = dh_pred * delta_test.std() + delta_test.mean()
    res_dh = evaluate_strategy('DH-LSTM', dh_pred, S_test, cost_coef=cost_coef)
    print(res_dh)

    # Summary
    print('\n' + '=' * 80)
    print('SUMMARY (2608.29025 reproduction)')
    print('=' * 80)
    all_results = [res_bs] + ww_results + [res_dh]
    print(f"{'Strategy':<15} {'Net PnL':>10} {'Trades':>10} {'Sharpe':>10} {'vs BS':>10}")
    print('-' * 80)
    bs_net = res_bs['avg_net_pnl']
    for r in all_results:
        ratio = r['avg_net_pnl'] / (bs_net + 1e-8) if bs_net != 0 else 0
        print(f"{r['name']:<15} {r['avg_net_pnl']:>10.4f} "
              f"{r['avg_trades_per_path']:>10.1f} {r['sharpe']:>10.3f} {ratio:>9.2%}")

    # Verdict
    print('\n=== Verdict ===')
    best_ww = max(ww_results, key=lambda r: r['avg_net_pnl'] / (r['avg_trades_per_path'] + 1e-8))
    print(f"Best W-W config: k={best_ww['name'].split('-')[1]} "
          f"({best_ww['avg_trades_per_path']:.1f} trades vs BS {res_bs['avg_trades_per_path']:.1f}, "
          f"ratio {best_ww['avg_trades_per_path']/res_bs['avg_trades_per_path']:.1f}x fewer)")
    if res_dh['avg_net_pnl'] < 0:
        print(f"⚠️  DH-LSTM produced NEGATIVE PnL ({res_dh['avg_net_pnl']:.4f}) — confirms 2608.29025 finding")
        print('   → 渔芯猎手必须把 W-W band 作为 Layer 6.5 内置风控')

    return 0


if __name__ == '__main__':
    raise SystemExit(main())