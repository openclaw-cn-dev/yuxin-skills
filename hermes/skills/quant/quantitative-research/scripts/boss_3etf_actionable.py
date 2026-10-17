"""
boss_3etf_actionable.py — boss 3 ETF actionable 全栈
沿用 pitfall-N+101 (cvxpy MinVol 兜底) + pitfall-N+131 (L0 3 ETF 同板块去重)
       + pitfall-N+136 (双约束合并协议) + pitfall-N+133 (稳定高耦合判定 v2)

用法: python3 scripts/boss_3etf_actionable.py
输出: stdout JSON actionable 报告 + 持久化 /tmp/boss_3etf_latest.json

心跳协议:
  - 工具栈必须 arch/riskfolio/cvxpy 全部可用(沿用 v8 STABLE)
  - 必须先用 check_holdings_factsource.py 找到 holdings.json
  - 不直接修改 holdings.json (boss 决策后再写)
"""
import baostock as bs
import numpy as np
import pandas as pd
import time
import json
import cvxpy as cp
from datetime import datetime


def _fetch_prices(etf_codes, start='2026-04-01', end='2026-09-17'):
    """baostock 拉价格 — 沿用 pitfall #33 (time.sleep(2) 限速)"""
    bs.login()
    prices = {}
    for code, code_bs, name in etf_codes:
        rs = bs.query_history_k_data_plus(
            code_bs, 'date,close',
            start_date=start, end_date=end,
            frequency='d', adjustflag='2')
        rows = []
        while rs.error_code == '0' and rs.next():
            rows.append(rs.get_row_data())
        df = pd.DataFrame(rows, columns=rs.fields)
        df['close'] = pd.to_numeric(df['close'], errors='coerce')
        df = df.dropna(subset=['close'])
        prices[code] = df['close'].values
        time.sleep(2)  # pitfall #33
    bs.logout()
    return prices


def _l0_pairwise(resid_matrix, codes, window=20):
    """L0 CoKF pairwise 残差互相关 — 沿用 pitfall-N+131

    简化: 直接用收益率作为残差 proxy (完整 CoKF 需 Kalman filter,
          见 scripts/cast_cokf_smoke.py)
    """
    corr_full = np.corrcoef(resid_matrix.T)
    corr_recent = np.corrcoef(resid_matrix[-window:].T)
    pair_data = []
    for i in range(len(codes)):
        for j in range(i+1, len(codes)):
            pair_data.append({
                'pair': f'{codes[i]}-{codes[j]}',
                'long_corr': float(corr_full[i, j]),
                'recent_corr': float(corr_recent[i, j]),
                'jump': float(corr_recent[i, j] - corr_full[i, j]),
            })
    max_pair = max(pair_data, key=lambda x: x['recent_corr'])

    # 判定表 (沿用 pitfall-N+131 + N+133 v2)
    if max_pair['recent_corr'] > 0.70 and max_pair['jump'] > 0.05:
        verdict = '🚨🚨 同板块去重 (恶化中)'
    elif max_pair['recent_corr'] > 0.70:
        verdict = '🟡 稳定高耦合 (WATCH)'
    elif max_pair['recent_corr'] > 0.50:
        verdict = '🚨 强红旗'
    elif max_pair['recent_corr'] > 0.30:
        verdict = '⚠️ 红旗'
    else:
        verdict = '🟢 正常'

    return {
        'pair_data': sorted(pair_data, key=lambda x: x['recent_corr'], reverse=True),
        'max_pair': max_pair,
        'mean_long': float(np.mean([p['long_corr'] for p in pair_data])),
        'mean_recent': float(np.mean([p['recent_corr'] for p in pair_data])),
        'mean_jump': float(np.mean([p['jump'] for p in pair_data])),
        'verdict': verdict,
    }


def _cvxpy_minvol(cov, n, sector_pairs=None, max_sector_weight=0.50):
    """cvxpy MinVol (双约束合并 — 沿用 pitfall-N+101 + N+136)"""
    w = cp.Variable(n)
    constraints = [cp.sum(w) == 1, w >= 0]
    if sector_pairs:
        for i, j in sector_pairs:
            constraints.append(w[i] + w[j] <= max_sector_weight)
    prob = cp.Problem(
        cp.Minimize(cp.quad_form(w, cp.psd_wrap(cov))),
        constraints
    )
    prob.solve(qcp=True)
    if w.value is None:
        return None
    return np.array(w.value).flatten()


def boss_3etf_actionable(
    etf_codes=None,
    sector_pairs=None,
    weights_actual=None,
    start='2026-04-01',
    end='2026-09-17',
    persist_path='/tmp/boss_3etf_latest.json',
):
    """boss 3 ETF actionable 全栈

    Args:
        etf_codes: list of (code_raw, code_bs, name).
                   默认 = boss 当前持仓 (512800/512710/159940)
        sector_pairs: list of (i, j) 同板块索引对.
                      默认 [(0, 2)] = (512800 银行 + 159940 金融地产 同属金融)
        weights_actual: dict {code_raw: weight} 当前真实股票权重.
                        默认 None = 跳过 drift 判定
        start / end: baostock 拉数据日期范围
        persist_path: 持久化 JSON 路径

    Returns:
        dict 含 l0 / minvol / minvol_dual / recommendation / persistence 段
    """
    if etf_codes is None:
        etf_codes = [
            ('512800', 'sh.512800', '银行ETF'),
            ('512710', 'sh.512710', '军工龙头'),
            ('159940', 'sz.159940', '金融地产'),
        ]
    if sector_pairs is None:
        # 默认 (512800 银行, 159940 金融地产) 同板块
        sector_pairs = [(0, 2)]
    codes = [e[0] for e in etf_codes]

    # Step 1: 拉价格
    print(f'[1/4] baostock 拉价格... {len(etf_codes)} ETF, {start} → {end}')
    prices = _fetch_prices(etf_codes, start, end)
    min_n = min(len(p) for p in prices.values())
    R = pd.DataFrame({c: np.diff(np.log(p[-min_n:])) for c, p in zip(codes, prices.values())})

    # Step 2: L0 CoKF pairwise
    print(f'[2/4] L0 CoKF pairwise (n={min_n - 1})...')
    l0 = _l0_pairwise(R.values, codes, window=20)
    print(f'  max_pair: {l0["max_pair"]["pair"]} recent={l0["max_pair"]["recent_corr"]:+.3f} → {l0["verdict"]}')

    # Step 3: cvxpy MinVol (无约束 + 双约束)
    print(f'[3/4] cvxpy MinVol (双约束 sector_pairs={sector_pairs})...')
    cov = R.cov().values * 252
    n = len(codes)
    w_minvol = _cvxpy_minvol(cov, n, sector_pairs=None)
    w_dual = _cvxpy_minvol(cov, n, sector_pairs=sector_pairs, max_sector_weight=0.50)

    # Step 4: actionable
    print(f'[4/4] actionable 合并判定...')
    if w_minvol is not None:
        w_minvol_dict = dict(zip(codes, [float(x) for x in w_minvol]))
    else:
        w_minvol_dict = None
    if w_dual is not None:
        w_dual_dict = dict(zip(codes, [float(x) for x in w_dual]))
    else:
        w_dual_dict = None

    # 判定优先级 (沿用 pitfall-N+136)
    if '🚨🚨' in l0['verdict']:
        recommendation = (
            f'L0 🚨🚨 同板块去重触发 — 拒绝 MinVol 数学最优,'
            f'强制减仓同板块一只 (推荐 {sector_pairs})'
        )
        verdict_global = '🚨🚨'
    elif '🚨' in l0['verdict']:
        recommendation = 'L0 🚨 红旗 — 接受双约束 MinVol,拒绝单约束'
        verdict_global = '🚨'
    elif '⚠️' in l0['verdict']:
        recommendation = 'L0 ⚠️ 红旗 — 双约束 MinVol 优先'
        verdict_global = '⚠️'
    else:
        recommendation = '🟢 L0 正常 — 接受单约束 MinVol'
        verdict_global = '🟢'

    # Drift 判定 (沿用 pitfall-N+123)
    drift_data = []
    if weights_actual:
        target_w = w_dual_dict if (w_dual_dict is not None and '🚨' in l0['verdict']) else w_minvol_dict
        if target_w:
            for c in codes:
                if c in weights_actual:
                    actual = weights_actual[c]
                    opt = target_w[c]
                    drift_pp = abs(actual - opt) * 100
                    flag = '🚨 HIGH' if drift_pp > 20 else '⚠️ MED' if drift_pp > 10 else '🟢 LOW'
                    drift_data.append({
                        'code': c,
                        'actual': actual,
                        'optimal': opt,
                        'drift_pp': drift_pp,
                        'flag': flag,
                    })

    result = {
        'timestamp': datetime.now().isoformat(),
        'codes': codes,
        'sector_pairs': sector_pairs,
        'l0': l0,
        'minvol_single_constraint': w_minvol_dict,
        'minvol_dual_constraint': w_dual_dict,
        'recommendation': recommendation,
        'verdict_global': verdict_global,
        'drift': drift_data,
    }

    # 持久化 (沿用 pitfall-N+115 trend 监测协议)
    if persist_path:
        with open(persist_path, 'w') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f'\n✅ saved to {persist_path}')

    return result


def print_actionable(result):
    """打印 actionable 卡片"""
    l0 = result['l0']
    print('\n' + '=' * 60)
    print(f'## boss 3 ETF actionable — {result["timestamp"]}')
    print('=' * 60)
    print(f'\n### L0 CoKF pairwise (window=20)')
    for p in l0['pair_data']:
        print(f'  {p["pair"]:18s} long={p["long_corr"]:+.3f}  '
              f'recent={p["recent_corr"]:+.3f}  jump={p["jump"]:+.3f}')
    print(f'\n  → {l0["verdict"]}')

    print(f'\n### cvxpy MinVol (无约束)')
    for c, w in (result['minvol_single_constraint'] or {}).items():
        print(f'  {c}: {w:.1%}')

    print(f'\n### cvxpy MinVol (双约束 sector_pairs={result["sector_pairs"]})')
    for c, w in (result['minvol_dual_constraint'] or {}).items():
        print(f'  {c}: {w:.1%}')

    if result['drift']:
        print(f'\n### weight drift')
        for d in result['drift']:
            print(f'  {d["code"]}: actual {d["actual"]:.1%} vs '
                  f'opt {d["optimal"]:.1%} → drift {d["drift_pp"]:.1f}pp {d["flag"]}')

    print(f'\n### recommendation')
    print(f'  {result["recommendation"]}')
    print(f'  verdict_global: {result["verdict_global"]}')
    print('=' * 60)


if __name__ == '__main__':
    import sys
    weights = None
    if len(sys.argv) > 1:
        # 用法: python3 boss_3etf_actionable.py <holdings.json>
        with open(sys.argv[1]) as f:
            holdings = json.load(f)
        arr = holdings.get('holdings_current_estimated', [])
            # 沿用 pitfall-N+128 (code 字段带 .SH/.SZ 后缀)
        code_map = {'512800.SH': '512800', '512710.SH': '512710', '159940.SZ': '159940'}
        total_mv = 0
        mv_dict = {}
        for h in arr:
            code_short = code_map.get(h.get('code', ''), h.get('code', '').split('.')[0])
            mv = h.get('shares', 0) * h.get('latest_close', 0)
            mv_dict[code_short] = mv
            total_mv += mv
        if total_mv > 0:
            weights = {c: mv / total_mv for c, mv in mv_dict.items()}
            print(f'loaded weights from {sys.argv[1]}: {weights}')

    result = boss_3etf_actionable(weights_actual=weights)
    print_actionable(result)