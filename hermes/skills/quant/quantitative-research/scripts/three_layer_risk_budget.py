# TODO(tech-debt): 改由 Claude Code/Codex 重写 — 已验证可跑通 boss 2 ETF 全链路
"""
三层 Risk Budget 可重跑脚本 — boss 当前 2 ETF 实战验证版

心跳 #N+59 (2026-09-12 22:50) 实跑通过,见 evolution/***SECRET***.md

使用方法:
    python3 scripts/three_layer_risk_budget.py
    # 或指定持仓:
    python3 scripts/three_layer_risk_budget.py --codes sh.515220,sh.512710

依赖:baostock / ruptures / hmmlearn / arch / pandas / numpy
"""
import time, sys, argparse, warnings
import numpy as np
import pandas as pd

warnings.filterwarnings('ignore')

import baostock as bs
import ruptures as rpt
from hmmlearn.hmm import GaussianHMM
from arch import arch_model

DEFAULT_CODES = ['sh.515220', 'sh.512710']
DEFAULT_NAMES = {'sh.515220': '煤炭ETF国泰', 'sh.512710': '军工龙头ETF'}
START = '2024-09-01'
END = '2026-09-12'

# ---------------- L2 安全版 (pitfall-43 沉淀) ----------------
def l2_hmmlearn_safe(closes, min_n=200):
    """L2 安全版 — 样本不足自动降级"""
    log_ret = np.diff(np.log(closes)).reshape(-1, 1)
    n_obs = len(log_ret)
    if n_obs < min_n:
        return {
            'current_state': -1, 'current_label': '样本不足',
            'state_frac': 1.0, 'small_sample_warning': True,
            'note': f'样本 {n_obs}d < {min_n},跳过 2-state,决策只用 L1+L3',
            'usable': False,
        }
    log_ret_w = np.clip(log_ret, -0.02, 0.02)
    try:
        hmm = GaussianHMM(n_components=2, covariance_type='diag',
                          n_iter=300, random_state=42)
        hmm.fit(log_ret_w)
        states = hmm.predict(log_ret_w)
        frac = np.bincount(states, minlength=2) / len(states)
        if frac.min() < 0.05:
            return {
                'current_state': -1, 'current_label': '退化',
                'state_frac': float(frac.max()),
                'small_sample_warning': True,
                'note': f'state 1 frac={frac.min():.1%} < 5%,仍不可信',
                'usable': False,
            }
        means = hmm.means_.flatten()
        # state 0 = 较低 mean = 常态
        state_label_map = {0: '常态', 1: '异常'} if means[0] < means[1] else {1: '常态', 0: '异常'}
        cur_state = int(states[-1])
        return {
            'current_state': cur_state,
            'current_label': state_label_map[cur_state],
            'state_frac': float(frac[cur_state]),
            'small_sample_warning': False,
            'note': '', 'usable': True,
        }
    except Exception as e:
        return {'current_state': -1, 'current_label': 'err',
                'state_frac': 0.0, 'small_sample_warning': True,
                'note': str(e)[:80], 'usable': False}

# ---------------- L1 ruptures (pitfall-42 BIC penalty) ----------------
def l1_ruptures(closes):
    n = len(closes)
    pen = np.log(n) * np.var(closes)
    algo = rpt.Pelt(model='rbf', min_size=20, jump=5).fit(closes)
    bkps = algo.predict(pen=pen)
    return [b for b in bkps if b < n]

# ---------------- L3 GJR-GARCH (pitfall-39 pd.Series) ----------------
def l3_garch(closes):
    rets_pct = np.diff(np.log(closes)) * 100
    rets = pd.Series(rets_pct, index=pd.RangeIndex(len(rets_pct)))
    am = arch_model(rets, mean='Constant', vol='GARCH', p=1, o=1, q=1, dist='t')
    res = am.fit(disp='off')
    p = res.params
    alpha, beta, gamma = p['alpha[1]'], p['beta[1]'], p['gamma[1]']
    persistence = alpha + beta + gamma / 2
    half_life = -np.log(2) / np.log(persistence) if persistence < 1 else float('inf')
    cur_vol_d = res.conditional_volatility.iloc[-1] / 100
    cur_vol_ann = cur_vol_d * np.sqrt(252)
    return {
        'persistence': float(persistence),
        'half_life_d': float(half_life),
        'daily_vol': float(cur_vol_d),
        'ann_vol': float(cur_vol_ann),
        'VaR95': float(-1.645 * cur_vol_d),
    }

# ---------------- 决策 v2 (兼容 L2 降级) ----------------
def action_decide_v2(l1_has_break, l2_result, l3_ann_vol, vol_threshold=0.25):
    if not l2_result.get('usable', False):
        if l1_has_break and l3_ann_vol > vol_threshold:
            return '谨慎防御(断点+vol高,L2 不可用)'
        if l1_has_break and l3_ann_vol <= vol_threshold:
            return '加码(断点+vol低,L2 不可用)'
        if not l1_has_break and l3_ann_vol > vol_threshold:
            return '减仓预警(vol突破,L2 不可用)'
        return '加码(稳定期+低vol,L2 不可用)'
    state = l2_result['current_label']
    if l1_has_break and state == '异常' and l3_ann_vol > vol_threshold:
        return '防御+减仓(三层一致)'
    if l1_has_break and state == '常态':
        return '谨慎加码'
    if not l1_has_break and state == '异常' and l3_ann_vol > vol_threshold:
        return '减仓预警'
    if not l1_has_break and state == '常态' and l3_ann_vol <= vol_threshold:
        return '加码'
    return '维持+观察'

# ---------------- baostock 拉数 (pitfall #32/#33/#36) ----------------
def fetch_one(code, start=START, end=END):
    bs.login()
    rs = bs.query_history_k_data_plus(
        code, 'date,close',
        start_date=start, end_date=end,
        frequency='d', adjustflag='2'
    )
    rows = []
    while rs.error_code == '0' and rs.next():
        rows.append(rs.get_row_data())
    bs.logout()
    time.sleep(2)  # pitfall #33
    df = pd.DataFrame(rows, columns=['date', 'close'])
    df['date'] = pd.to_datetime(df['date'])
    df['close'] = df['close'].astype(float)
    return df.set_index('date').sort_index()

# ---------------- main ----------------
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--codes', default=','.join(DEFAULT_CODES),
                        help='逗号分隔 ETF 代码,默认 boss 当前 2 ETF')
    parser.add_argument('--start', default=START)
    parser.add_argument('--end', default=END)
    args = parser.parse_args()

    codes = [c.strip() for c in args.codes.split(',')]
    print(f'=== 三层 Risk Budget | {args.start} ~ {args.end} | {time.strftime("%Y-%m-%d %H:%M")} ===\n')

    for code in codes:
        name = DEFAULT_NAMES.get(code, code)
        try:
            df = fetch_one(code, args.start, args.end)
        except Exception as e:
            print(f'[{name} {code}] ❌ 拉数失败: {e}')
            continue
        if len(df) < 60:
            print(f'[{name} {code}] ❌ 样本不足 60d')
            continue

        closes = df['close'].values
        dates = df.index
        n = len(closes)
        last_close = closes[-1]

        bkps = l1_ruptures(closes)
        l2 = l2_hmmlearn_safe(closes)
        l3 = l3_garch(closes)
        action = action_decide_v2(len(bkps) > 0, l2, l3['ann_vol'])

        print(f'【{name} {code}】 n={n} | 最新 ¥{last_close:.4f} ({dates[-1].date()})')
        print(f'  L1 ruptures: {len(bkps)} 断点 (BIC penalty ✓)')
        print(f'  L2 hmmlearn: usable={l2["usable"]} label={l2["current_label"]} '
              f'frac={l2["state_frac"]:.1%} {l2["note"]}')
        print(f'  L3 GARCH: ann_vol={l3["ann_vol"]:.1%} VaR95={l3["VaR95"]:.2%} '
              f'half_life={l3["half_life_d"]:.1f}d persistence={l3["persistence"]:.3f}')
        print(f'  >>> 渔芯猎手动作: {action}\n')

if __name__ == '__main__':
    main()
