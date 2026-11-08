# TODO(tech-debt): 改由 Claude Code/Codex 重写 — 已验证可跑通 boss 2 ETF 仓位反算
"""
Vol Targeting 仓位反算脚本 — 论文 2609.07946 (Boyd) 思路

心跳 #N+56 (18:00) 理论沉淀 + 心跳 #N+59 (22:00) boss 2 ETF 实跑通过
见 evolution/***SECRET***.md
   + evolution/***SECRET***.md

核心思想:
    目标年化 vol → 反算每只仓位上限 (max_pos_pct = target_daily_vol / current_daily_vol)
    实际仓位 vs 上限 → diff → 风控告警 / 加码建议

使用方法:
    python3 scripts/vol_targeting_positions.py
    # 自定义目标 vol:
    python3 scripts/vol_targeting_positions.py --target-vol 0.08

依赖:baostock / arch / pandas / numpy
"""
import argparse, time, warnings
import numpy as np
import pandas as pd
import baostock as bs
from arch import arch_model

warnings.filterwarnings('ignore')

DEFAULT_CODES = ['sh.515220', 'sh.512710']
DEFAULT_NAMES = {'sh.515220': '煤炭ETF国泰', 'sh.512710': '军工龙头ETF'}
# boss 当前持仓 (来自 holdings.json, 2026-09-12 12:50 实测)
ACTUAL = {
    'sh.515220': {'shares': 900, 'cost': 1.092, 'current': 1.292},
    'sh.512710': {'shares': 700, 'cost': 0.643, 'current': 0.640},
}
CASH = 24055

def garch_ann_vol(closes):
    """GJR-GARCH Student-t 当前年化波动率 (pitfall #39 pd.Series)"""
    rets_pct = np.diff(np.log(closes)) * 100
    rets = pd.Series(rets_pct, index=pd.RangeIndex(len(rets_pct)))
    am = arch_model(rets, mean='Constant', vol='GARCH', p=1, o=1, q=1, dist='t')
    res = am.fit(disp='off')
    cur_vol_d = res.conditional_volatility.iloc[-1] / 100
    return float(cur_vol_d * np.sqrt(252))

def fetch_one(code, start='2024-09-01', end='2026-09-12'):
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
    time.sleep(2)
    df = pd.DataFrame(rows, columns=['date', 'close'])
    df['date'] = pd.to_datetime(df['date'])
    df['close'] = df['close'].astype(float)
    return df.set_index('date').sort_index()

def vol_targeted_position(current_daily_vol, total_budget, target_ann_vol=0.10):
    """论文 2609.07946 风格 vol targeting 仓位反算"""
    target_daily_vol = target_ann_vol / np.sqrt(252)
    max_pos_pct = target_daily_vol / current_daily_vol
    max_pos_value = total_budget * max_pos_pct
    return {
        'max_pos_pct': float(max_pos_pct),
        'max_pos_value': float(max_pos_value),
        'cash_buffer_pct': float(1 - max_pos_pct),
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--codes', default=','.join(DEFAULT_CODES))
    parser.add_argument('--target-vol', type=float, default=0.10,
                        help='目标年化 vol,默认 10%(论文 Boyd 长期保守)')
    parser.add_argument('--start', default='2024-09-01')
    parser.add_argument('--end', default='2026-09-12')
    args = parser.parse_args()

    codes = [c.strip() for c in args.codes.split(',')]

    # 总市值 = 持仓市值 + 现金
    pos_value = sum(ACTUAL.get(c, {}).get('shares', 0) * ACTUAL[c]['current']
                    for c in codes if c in ACTUAL)
    total_value = pos_value + CASH
    print(f'总市值 ¥{total_value:.2f} (持仓 ¥{pos_value:.0f} + 现金 ¥{CASH:.0f})')
    print(f'目标年化 vol = {args.target_vol:.1%}\n')

    for code in codes:
        name = DEFAULT_NAMES.get(code, code)
        try:
            df = fetch_one(code, args.start, args.end)
            closes = df['close'].values
        except Exception as e:
            print(f'[{name} {code}] ❌ {e}')
            continue

        ann_vol = garch_ann_vol(closes)
        daily_vol = ann_vol / np.sqrt(252)
        pos_info = vol_targeted_position(daily_vol, total_value, args.target_vol)

        if code in ACTUAL:
            act = ACTUAL[code]
            act_val = act['shares'] * act['current']
            act_pct = act_val / total_value
            diff = act_pct - pos_info['max_pos_pct']
            pnl_pct = (act['current'] - act['cost']) / act['cost'] * 100
            status = '⚠️ 超限' if diff > 0.10 else ('✅ 低于上限' if diff < -0.10 else '✅ 区间内')
        else:
            act = None
            status = '(未在 ACTUAL 中)'

        print(f'【{name} {code}】')
        print(f'  GARCH ann_vol: {ann_vol:.1%} (daily {daily_vol:.2%})')
        print(f'  vol targeting 上限: {pos_info["max_pos_pct"]:.1%} (¥{pos_info["max_pos_value"]:.0f})')
        if act:
            print(f'  实际仓位: {act_pct:.1%} (¥{act_val:.0f}, {act["shares"]}股, PnL {pnl_pct:+.2f}%)')
            print(f'  diff = 实际 - 上限 = {diff:+.1%} {status}')

if __name__ == '__main__':
    main()
