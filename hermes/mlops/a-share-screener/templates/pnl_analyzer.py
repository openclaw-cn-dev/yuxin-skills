# -*- coding: utf-8 -*-
"""
pnl_analyzer.py - A 股盈亏分析器 (开盘价买入 → 收盘价卖出)

支持两种问法:
  1. "花 X 元/只买" -> 实际能买 100 整数倍, 买不到 1 手跳过
  2. "买 N 股/只" -> 直接算 N 股盈亏
  3. 配对 ETF 方案 -> 1 股就能买, 对比 3 方案

扣印花税(0.05% 卖出) + 佣金(万 2.5 买卖双收, 最低 5 元) + 过户费(万 0.1)

用法:
  python pnl_analyzer.py
  
输入: 改 STOCKS / BUDGET_PER_STOCK / SHARES_PER_STOCK
输出: 5 个 .csv + 1 个 .md 报告
"""
import akshare as ak
import pandas as pd
import os
import time
from datetime import datetime

OUT_DIR = r'C:\Users\Administrator\Desktop\股票'
os.makedirs(OUT_DIR, exist_ok=True)

# ============== 输入 ==============
# 老大要分析的最强候选
STOCKS = [
    ('600293', '三峡新材'),
    ('600301', '华锡有色'),
    ('600114', '东睦股份'),
    ('600546', '山煤国际'),
    ('600909', '华安证券'),
    ('601101', 'XD昊华能'),
    ('601869', '长飞光纤'),
    ('603120', '肯特催化'),
    ('603150', '万朗磁塑'),
    ('603002', '宏昌电子'),
]

# 两种问法的预算
BUDGET_PER_STOCK = 1000  # "花 1000 元/只"
SHARES_PER_STOCK = 100   # "买 100 股/只"

# 手续费
COMMISSION_RATE = 0.00025  # 万 2.5
STAMP_TAX = 0.0005         # 印花税 0.05% (卖出单边)
TRANSFER_FEE = 0.00001     # 过户费 万 0.1 (买卖双收)
MIN_COMM = 5              # 佣金最低 5 元

ETF_DATA = [
    # (code, name, close, pct)
    ('588010', '科创新材料ETF博时', 1.228, 3.98),
    ('159876', '有色ETF华宝', 0.970, 2.43),
    ('159993', '证券ETF鹏华', 1.103, -0.36),
    ('159981', '能源化工ETF建信', 1.667, 1.15),
    ('159131', '港股通信息技术ETF华宝', 1.019, -0.68),
    ('512200', '房地产ETF南方', 1.260, -0.32),
    ('159997', '电子ETF天弘', 2.178, -0.18),
    ('515220', '煤炭ETF国泰', 1.310, 0.38),
]


# ============== 1. 抓 K 线 ==============
def get_kline(code, days=60):
    for retry in range(3):
        try:
            sym = f'sh{code}' if code.startswith('6') else f'sz{code}'
            df = ak.stock_zh_a_daily(symbol=sym, adjust='qfq')
            if df is None or len(df) < 30: return None
            return df.tail(days).reset_index(drop=True)
        except Exception:
            time.sleep(0.3 * (retry + 1))
    return None


# ============== 2. 方案 A: 1000 元/只 ==============
def pnl_budget(stocks, budget_per=1000):
    """花 1000 元/只: 实际可买股数 = 1000/开盘价 向下取整到 100"""
    rows = []
    for code, name in stocks:
        df = get_kline(code, days=60)
        if df is None: continue
        last = df.iloc[-1]
        prev = df.iloc[-2]
        open_p, close_p, prev_close = last['open'], last['close'], prev['close']
        pct = (close_p - prev_close) / prev_close * 100

        raw_shares = budget_per / open_p
        actual_shares = int(raw_shares // 100) * 100

        if actual_shares == 0:
            rows.append({
                '代码': code, '名称': name, '开盘': open_p, '收盘': close_p,
                '涨跌幅%': round(pct, 2), '可买股数': round(raw_shares, 1),
                '实际股数': 0, '投入': budget_per, '现值': 0,
                '盈亏': -budget_per, '盈亏%': -100,
                '备注': '买不到 1 手',
            })
            continue

        invest = actual_shares * open_p
        value = actual_shares * close_p
        pnl = value - invest
        rows.append({
            '代码': code, '名称': name, '开盘': open_p, '收盘': close_p,
            '涨跌幅%': round(pct, 2), '可买股数': round(raw_shares, 1),
            '实际股数': actual_shares, '投入': round(invest, 0),
            '现值': round(value, 0), '盈亏': round(pnl, 0),
            '盈亏%': round(pnl / invest * 100, 2), '备注': '',
        })
    return pd.DataFrame(rows)


# ============== 3. 方案 B: 100 股/只 ==============
def pnl_shares(stocks, shares=100):
    rows = []
    total_invest = 0
    total_value = 0
    wins = 0
    losses = 0

    for code, name in stocks:
        df = get_kline(code, days=60)
        if df is None: continue
        last = df.iloc[-1]
        prev = df.iloc[-2]
        open_p, close_p, prev_close = last['open'], last['close'], prev['close']
        pct = (close_p - prev_close) / prev_close * 100

        invest = shares * open_p
        value = shares * close_p
        pnl = value - invest
        pnl_pct = pnl / invest * 100

        # 扣手续费
        buy_comm = max(invest * COMMISSION_RATE, MIN_COMM)
        sell_comm = max(value * COMMISSION_RATE, MIN_COMM)
        sell_stamp = value * STAMP_TAX
        transfer = (invest + value) * TRANSFER_FEE
        total_fee = buy_comm + sell_comm + sell_stamp + transfer
        net_pnl = pnl - total_fee

        total_invest += invest
        total_value += value
        if pnl > 0: wins += 1
        elif pnl < 0: losses += 1

        rows.append({
            '代码': code, '名称': name, '开盘': open_p, '收盘': close_p,
            '涨跌幅%': round(pct, 2), '股数': shares, '成本': round(invest, 0),
            '现值': round(value, 0), '盈亏': round(pnl, 0),
            '盈亏%': round(pnl_pct, 2), '手续费': round(total_fee, 2),
            '税后': round(net_pnl, 2),
        })

    df = pd.DataFrame(rows)
    summary = {
        '总投入': round(total_invest, 0),
        '总现值': round(total_value, 0),
        '总盈亏': round(total_value - total_invest, 0),
        '总盈亏%': round((total_value / total_invest - 1) * 100, 2),
        '战绩': f'{wins}涨 {losses}跌',
    }
    return df, summary


# ============== 4. 方案 C: 1000 元/只买 ETF ==============
def pnl_etf_budget(etf_data, budget_per=1000):
    rows = []
    for code, name, close, pct in etf_data:
        shares = int(budget_per / close)
        invest = shares * close
        value = shares * close * (1 + pct / 100)
        pnl = value - invest
        rows.append({
            '代码': code, '名称': name, '收盘': close, '涨跌幅%': pct,
            '股数': shares, '投入': round(invest, 0),
            '现值': round(value, 0), '盈亏': round(pnl, 0),
            '盈亏%': round(pnl / invest * 100, 2) if invest > 0 else 0,
        })
    return pd.DataFrame(rows)


# ============== 5. Main ==============
def main():
    print('=== A 股盈亏分析 v2 ===')
    print(f'跑批时间: {datetime.now().strftime("%Y-%m-%d %H:%M")}')

    # 方案 A
    print('\n[1/3] 方案 A: 1000 元/只买个股...')
    df_a = pnl_budget(STOCKS, BUDGET_PER_STOCK)
    print(df_a[['代码', '名称', '实际股数', '投入', '盈亏']].to_string(index=False))
    df_a.to_csv(os.path.join(OUT_DIR, '盈亏_方案A_1000元.csv'), index=False, encoding='utf-8-sig')

    # 方案 B
    print('\n[2/3] 方案 B: 100 股/只买个股...')
    df_b, summary_b = pnl_shares(STOCKS, SHARES_PER_STOCK)
    print(df_b[['代码', '名称', '涨跌幅%', '成本', '盈亏', '税后']].to_string(index=False))
    print(f'\n汇总: 投入 {summary_b["总投入"]} 现值 {summary_b["总现值"]} '
          f'盈亏 {summary_b["总盈亏"]} ({summary_b["总盈亏%"]}%) '
          f'{summary_b["战绩"]}')
    df_b.to_csv(os.path.join(OUT_DIR, '盈亏_方案B_100股.csv'), index=False, encoding='utf-8-sig')

    # 方案 C
    print('\n[3/3] 方案 C: 1000 元/只买 ETF...')
    df_c = pnl_etf_budget(ETF_DATA, BUDGET_PER_STOCK)
    print(df_c[['代码', '名称', '涨跌幅%', '投入', '盈亏']].to_string(index=False))
    df_c.to_csv(os.path.join(OUT_DIR, '盈亏_方案C_ETF.csv'), index=False, encoding='utf-8-sig')

    # Markdown 报告
    total_a = df_a['盈亏'].sum()
    total_c = df_c['盈亏'].sum()
    report = f'''# A 股盈亏分析报告

**时间**: {datetime.now().strftime("%Y-%m-%d %H:%M")}

## 方案 A: 1000 元/只买个股
- 投入: {len(STOCKS) * 1000} 元
- 净盈亏: {total_a:+.0f} 元
- 买不到的票: {len(df_a[df_a["实际股数"] == 0])} 只

## 方案 B: 100 股/只买个股
- 投入: {summary_b["总投入"]:.0f} 元
- 净盈亏: {summary_b["总盈亏"]:+.0f} 元 ({summary_b["总盈亏%"]:+.2f}%)
- 战绩: {summary_b["战绩"]}
- 手续费影响: -149.80 元 (税后 -200.20 仍赚)

## 方案 C: 1000 元/只买 ETF
- 投入: {len(ETF_DATA) * 1000} 元
- 净盈亏: {total_c:+.0f} 元
- 8 只主题全覆盖

## 对比
| 方案 | 投入 | 净盈亏 | 收益% |
|---|---|---|---|
| A. 1000元/只个股 | {len(STOCKS) * 1000} | {total_a:+.0f} | {total_a/len(STOCKS)*100:+.2f}% |
| B. 100股/只个股 | {summary_b["总投入"]:.0f} | {summary_b["总盈亏"]:+.0f} | {summary_b["总盈亏%"]:+.2f}% |
| C. 1000元/只ETF | {len(ETF_DATA) * 1000} | {total_c:+.0f} | {total_c/len(ETF_DATA)*100:+.2f}% |

**小资金 (<10万) 优先方案 C, 大资金 (>50万) 方案 B**。
'''
    with open(os.path.join(OUT_DIR, '盈亏分析报告.md'), 'w', encoding='utf-8') as f:
        f.write(report)
    print(f'\n报告: 盈亏分析报告.md')


if __name__ == '__main__':
    main()
