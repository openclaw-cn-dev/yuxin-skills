# -*- coding: utf-8 -*-
"""
A 股选股 v2 - 全 A 市场（沪深 5527 只）
3 维度: 涨停+异动+倍量 / 上升趋势 / 放量长上影
已验证 6 线程 + 50ms 限速跑 10 分 17 秒稳，0 封禁。
"""
import akshare as ak
import pandas as pd
import numpy as np
import os
import time
import threading
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

os.makedirs(r'C:\Users\Administrator\Desktop\股票', exist_ok=True)


def get_all_spot():
    print('[1/4] 抓全 A 代码列表...', flush=True)
    df = ak.stock_info_a_code_name()  # 比 stock_zh_a_spot 稳（不解析 demjson）
    print(f'  -> {len(df)} 只股票')
    return df


def get_kline(code, days=60):
    for retry in range(3):
        try:
            sym = f'sh{code}' if code.startswith('6') else f'sz{code}'
            df = ak.stock_zh_a_daily(symbol=sym, adjust='qfq')
            if df is None or len(df) < 30:
                return None
            return df.tail(days).reset_index(drop=True)
        except Exception:
            time.sleep(0.3 * (retry + 1))
    return None


def calc_upper_shadow(row):
    return row['high'] - max(row['open'], row['close'])


def is_limit_up(row, prev_close):
    return (row['close'] - prev_close) / prev_close >= 0.095 if prev_close > 0 else False


def pick_dim1_zt(df, code):
    if len(df) < 30:
        return None
    df = df.copy()
    df['prev_close'] = df['close'].shift(1)
    df['is_zt'] = df.apply(lambda r: is_limit_up(r, r['prev_close']), axis=1)
    df['vol_ma5'] = df['volume'].rolling(5).mean()
    df['vol_ratio'] = df['volume'] / df['vol_ma5'].shift(1)

    has_zt_20 = df['is_zt'].tail(20).any()
    max_change_30 = ((df['close'].tail(30).max() - df['close'].iloc[0]) / df['close'].iloc[0]) if len(df) >= 30 else 0
    has_beiliang = (df['vol_ratio'].tail(30) >= 2.0).any()

    if has_zt_20 and max_change_30 >= 0.15 and has_beiliang:
        return {
            'code': code, 'dim': 1,
            'score': sum([has_zt_20, max_change_30 >= 0.15, has_beiliang]) * 30 + min(max_change_30 * 100, 30),
            'zt_20d': int(df['is_zt'].tail(20).sum()),
            'max_change_30d': round(max_change_30 * 100, 1),
            'max_vol_ratio': round(df['vol_ratio'].tail(30).max(), 1),
        }
    return None


def pick_dim2_trend(df, code):
    if len(df) < 30:
        return None
    front = df.tail(30).head(15)
    back = df.tail(15)
    high_trend = back['high'].max() > front['high'].max()
    low_trend = back['low'].min() >= front['low'].min()
    new_high_count = (back['high'] > front['high'].max()).sum()
    if high_trend and low_trend and new_high_count >= 1:
        ma30 = df['close'].tail(30).mean()
        ma5 = df['close'].tail(5).mean()
        return {
            'code': code, 'dim': 2,
            'score': 50 + new_high_count * 10 + (ma5 > ma30) * 20,
            'new_high_count': int(new_high_count),
            'high_trend': round((back['high'].max() - front['high'].max()) / front['high'].max() * 100, 1),
            'low_trend': round((back['low'].min() - front['low'].min()) / front['low'].min() * 100, 1),
            'ma5_above_ma30': ma5 > ma30,
        }
    return None


def pick_dim3_shadow(df, code):
    if len(df) < 60:
        return None
    df = df.copy()
    df['upper_shadow'] = df.apply(calc_upper_shadow, axis=1)
    df['vol_ma20'] = df['volume'].rolling(20).mean()

    front = df.iloc[30:60] if len(df) >= 60 else df.head(30)
    amp = (front['high'].max() - front['low'].min()) / front['low'].min() if len(front) > 0 else 999
    is_oscillation = amp < 0.30

    recent = df.tail(10)
    recent_change = (recent['close'].iloc[-1] - recent['close'].iloc[0]) / recent['close'].iloc[0] if len(recent) > 1 else 0
    is_early_up = recent_change > 0 and recent_change < 0.15

    if not (is_oscillation or is_early_up):
        return None

    recent20 = df.tail(20).copy()
    recent20['shadow_pct'] = (recent20['upper_shadow'] / recent20['close']) * 100
    long_shadows = recent20[recent20['shadow_pct'] >= 3.0]
    if len(long_shadows) == 0:
        return None
    best = long_shadows.loc[long_shadows['shadow_pct'].idxmax()]

    before_idx = df.index[df['date'] == best['date']].tolist()
    if not before_idx:
        return None
    idx = before_idx[0]
    prev_max_high = df.iloc[max(0, idx-20):idx]['high'].max() if idx > 0 else 0
    broke_high = best['high'] > prev_max_high
    vol_above_ma = best['volume'] / best['vol_ma20'] if best['vol_ma20'] > 0 else 0

    if broke_high and vol_above_ma < 1.0:
        return None

    return {
        'code': code, 'dim': 3,
        'score': 50 + best['shadow_pct'] * 5 + vol_above_ma * 10,
        'shadow_pct': round(best['shadow_pct'], 2),
        'upper_shadow_pct': round(best['upper_shadow'] / best['close'] * 100, 2),
        'vol_ma20_ratio': round(vol_above_ma, 2),
        'broke_prev_high': bool(broke_high),
        'phase': '横盘' if is_oscillation else '上涨初期',
    }


def pick_one(code):
    try:
        df = get_kline(code, days=60)
        if df is None or len(df) < 30:
            return []
        results = []
        for picker in [pick_dim1_zt, pick_dim2_trend, pick_dim3_shadow]:
            r = picker(df, code)
            if r:
                results.append(r)
        return results
    except Exception:
        return []


def main():
    start = time.time()
    print(f'== 启动选股 v2 {datetime.now().strftime("%Y-%m-%d %H:%M")} ==')

    spot = get_all_spot()
    spot.to_csv(r'C:\Users\Administrator\Desktop\股票\全A列表.csv', index=False, encoding='utf-8-sig')

    all_codes = [c for c in spot['code'].tolist() if not c.startswith('bj')]
    print(f'沪深共 {len(all_codes)} 只')

    print(f'[2/4] 多线程筛选 {len(all_codes)} 只（6 线程，限速）...', flush=True)
    all_results = []
    done = 0
    sem = threading.Semaphore(6)  # 关键：6 并发
    def safe_pick(c):
        with sem:
            time.sleep(0.05)  # 关键：50ms sleep
            return pick_one(c)
    with ThreadPoolExecutor(max_workers=6) as ex:
        futures = {ex.submit(safe_pick, c): c for c in all_codes}
        for f in as_completed(futures):
            r = f.result()
            if r:
                all_results.extend(r)
            done += 1
            if done % 200 == 0:
                print(f'  进度 {done}/{len(all_codes)} | 命中 {len(all_results)} | 用时 {time.time()-start:.0f}s', flush=True)

    print(f'[3/4] 整理结果...')
    if not all_results:
        print('无命中')
        return

    df_res = pd.DataFrame(all_results).sort_values(['dim', 'score'], ascending=[True, False])

    code2name = dict(zip(spot['code'], spot['name']))
    df_res['name'] = df_res['code'].map(code2name)

    for dim in [1, 2, 3]:
        sub = df_res[df_res['dim'] == dim]
        print(f'  维度{dim}: {len(sub)} 只')
        sub.to_csv(
            f'C:\\Users\\Administrator\\Desktop\\股票\\v2_维度{dim}_结果.csv',
            index=False, encoding='utf-8-sig'
        )

    dim3 = df_res[df_res['dim'] == 3].sort_values('shadow_pct', ascending=False).head(50)
    dim3.to_csv(r'C:\Users\Administrator\Desktop\股票\v2_维度3_长上影线TOP50.csv', index=False, encoding='utf-8-sig')

    df_res.to_csv(r'C:\Users\Administrator\Desktop\股票\v2_选股结果汇总.csv', index=False, encoding='utf-8-sig')

    # 3 维度全中 - 关键：int 对比不是 str
    codes_1 = set(df_res[df_res['dim']==1]['code'])
    codes_2 = set(df_res[df_res['dim']==2]['code'])
    codes_3 = set(df_res[df_res['dim']==3]['code'])
    codes_3d = codes_1 & codes_2 & codes_3
    print(f'  3 维度同时全中: {len(codes_3d)} 只')
    if codes_3d:
        top3_df = df_res[df_res['code'].isin(codes_3d)][['code', 'dim', 'name']].to_csv(
            r'C:\Users\Administrator\Desktop\股票\v2_三维度全中.csv',
            index=False, encoding='utf-8-sig'
        )

    print(f'[4/4] 完成！总命中 {len(df_res)} 条（去重 {df_res["code"].nunique()} 只）')
    print(f'耗时: {time.time()-start:.0f}s')


if __name__ == '__main__':
    main()
