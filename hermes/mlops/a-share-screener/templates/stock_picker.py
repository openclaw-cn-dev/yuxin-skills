# -*- coding: utf-8 -*-
"""
stock_picker.py - A 股 3 维度综合筛选（沪市 2314 只实测 4'44"）

用法:
  pip install akshare pandas -i https://pypi.tuna.tsinghua.edu.cn/simple
  python stock_picker.py

输出:
  C:\Users\Administrator\Desktop\股票\维度1_结果.csv
  C:\Users\Administrator\Desktop\股票\维度2_结果.csv
  C:\Users\Administrator\Desktop\股票\维度3_结果.csv
  C:\Users\Administrator\Desktop\股票\选股结果汇总.csv
  C:\Users\Administrator\Desktop\股票\选股报告_YYYY-MM-DD.md

修改点（按需）:
  - OUT_DIR: 改成你想输出的目录
  - sh_codes 过滤: 加深市/创业板/科创板
  - max_workers: 10-20 调
  - 各 pick_dim_X 阈值: 调严/调松
"""
import akshare as ak
import pandas as pd
import numpy as np
import os
import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

OUT_DIR = r'C:\Users\Administrator\Desktop\股票'
os.makedirs(OUT_DIR, exist_ok=True)


# ============== 1. 拉代码列表 ==============
def get_all_spot():
    """全 A 代码列表（用 code_name 接口，不解析实时行情，更稳）"""
    print('[1/4] 抓全 A 代码列表...', flush=True)
    df = ak.stock_info_a_code_name()
    print(f'  -> {len(df)} 只股票')
    return df


# ============== 2. 单只 K 线 ==============
def get_kline(code, days=60):
    """单只股票 K 线（带 3 次重试）"""
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


# ============== 3. 维度 1：涨停 + 异动 + 倍量 ==============
def pick_dim1_zt(df, code):
    if len(df) < 30: return None
    df = df.copy()
    df['prev_close'] = df['close'].shift(1)
    df['is_zt'] = (df['close'] / df['prev_close'] - 1) >= 0.095
    df['vol_ma5'] = df['volume'].rolling(5).mean()
    df['vol_ratio'] = df['volume'] / df['vol_ma5'].shift(1)

    zt_20d = int(df['is_zt'].tail(20).sum())
    max_change_30d = (df['close'].tail(30).max() / df['close'].iloc[-30] - 1) if len(df) >= 30 else 0
    max_vol_ratio = df['vol_ratio'].tail(30).max()

    if zt_20d >= 1 and max_change_30d >= 0.15 and max_vol_ratio >= 2.0:
        return {
            'code': code, 'dim': '1',
            'score': min(zt_20d*10, 30) + min(max_change_30d*100, 50) + min(max_vol_ratio*5, 30),
            'zt_20d': zt_20d,
            'max_change_30d': round(max_change_30d * 100, 1),
            'max_vol_ratio': round(max_vol_ratio, 1),
        }
    return None


# ============== 4. 维度 2：上升趋势 ==============
def pick_dim2_trend(df, code):
    if len(df) < 30: return None
    front = df.tail(30).head(15)
    back = df.tail(15)
    high_trend = back['high'].max() > front['high'].max()
    low_trend = back['low'].min() >= front['low'].min()
    new_high_count = (back['high'] > front['high'].max()).sum()
    ma5 = df['close'].tail(5).mean()
    ma30 = df['close'].tail(30).mean()

    if high_trend and low_trend and new_high_count >= 1 and ma5 > ma30:
        return {
            'code': code, 'dim': '2',
            'score': 50 + int(new_high_count) * 10 + 20,
            'new_high_count': int(new_high_count),
            'high_trend': round((back['high'].max() / front['high'].max() - 1) * 100, 1),
            'low_trend': round((back['low'].min() / front['low'].min() - 1) * 100, 1),
            'ma5_above_ma30': True,
        }
    return None


# ============== 5. 维度 3：放量长上影线 ==============
def pick_dim3_shadow(df, code):
    if len(df) < 60: return None
    df = df.copy()
    df['upper_shadow'] = df['high'] - df[['open','close']].max(axis=1)
    df['shadow_pct'] = df['upper_shadow'] / df['close'] * 100
    df['vol_ma20'] = df['volume'].rolling(20).mean()

    # 阶段判定
    front = df.iloc[30:60] if len(df) >= 60 else df.head(30)
    amp = (front['high'].max() - front['low'].min()) / front['low'].min() if len(front) > 0 else 999
    is_oscillation = amp < 0.30
    recent = df.tail(10)
    recent_change = (recent['close'].iloc[-1] / recent['close'].iloc[0] - 1) if len(recent) > 1 else 0
    is_early_up = 0 < recent_change < 0.15
    if not (is_oscillation or is_early_up): return None

    # 找最长上影
    recent20 = df.tail(20)
    long_shadows = recent20[recent20['shadow_pct'] >= 3.0]
    if len(long_shadows) == 0: return None
    best = long_shadows.loc[long_shadows['shadow_pct'].idxmax()]

    # 老大特别要求：突破前高时，量必须 > 前面
    idx_list = df.index[df['date'] == best['date']].tolist()
    if not idx_list: return None
    idx = idx_list[0]
    prev_max_high = df.iloc[max(0, idx-20):idx]['high'].max() if idx > 0 else 0
    broke_high = best['high'] > prev_max_high
    vol_ratio = best['volume'] / best['vol_ma20'] if best['vol_ma20'] > 0 else 0
    if broke_high and vol_ratio < 1.0: return None

    return {
        'code': code, 'dim': '3',
        'score': 50 + best['shadow_pct'] * 5 + vol_ratio * 10,
        'shadow_pct': round(best['shadow_pct'], 2),
        'vol_ma20_ratio': round(vol_ratio, 2),
        'broke_prev_high': bool(broke_high),
        'phase': '横盘' if is_oscillation else '上涨初期',
    }


# ============== 6. 主循环 ==============
def pick_one(code):
    try:
        df = get_kline(code, days=60)
        if df is None or len(df) < 30:
            return []
        results = []
        for r in [pick_dim1_zt(df, code), pick_dim2_trend(df, code), pick_dim3_shadow(df, code)]:
            if r:
                results.append(r)
        return results
    except Exception:
        return []


def main():
    start = time.time()
    print(f'== 启动选股 {datetime.now().strftime("%Y-%m-%d %H:%M")} ==')

    spot = get_all_spot()
    spot.to_csv(os.path.join(OUT_DIR, '全A列表.csv'), index=False, encoding='utf-8-sig')

    # 沪市过滤（要加深市/创业板就把 startswith 改一下）
    sh_codes = [c for c in spot['code'].tolist() if c.startswith('6')]
    print(f'沪市共 {len(sh_codes)} 只')

    print(f'[2/4] 多线程筛选 {len(sh_codes)} 只（15 线程）...', flush=True)
    all_results = []
    done = 0
    with ThreadPoolExecutor(max_workers=15) as ex:
        futures = {ex.submit(pick_one, c): c for c in sh_codes}
        for f in as_completed(futures):
            r = f.result()
            if r:
                all_results.extend(r)
            done += 1
            if done % 200 == 0:
                print(f'  进度 {done}/{len(sh_codes)} | 命中 {len(all_results)} | 用时 {time.time()-start:.0f}s', flush=True)

    if not all_results:
        print('无命中')
        return

    print(f'[3/4] 整理结果...')
    df_res = pd.DataFrame(all_results)
    df_res = df_res.sort_values(['dim', 'score'], ascending=[True, False])

    code2name = dict(zip(spot['code'], spot['name']))
    df_res['name'] = df_res['code'].map(code2name)

    # 关联股票名后重排列
    cols = ['code', 'name', 'dim', 'score'] + [c for c in df_res.columns if c not in ['code', 'name', 'dim', 'score']]
    df_res = df_res[cols]

    for dim in ['1', '2', '3']:
        sub = df_res[df_res['dim'] == dim]
        print(f'  维度{dim}: {len(sub)} 只')
        sub.to_csv(os.path.join(OUT_DIR, f'维度{dim}_结果.csv'), index=False, encoding='utf-8-sig')

    dim3 = df_res[df_res['dim'] == '3'].sort_values('shadow_pct', ascending=False).head(50)
    dim3.to_csv(os.path.join(OUT_DIR, '维度3_长上影线TOP50.csv'), index=False, encoding='utf-8-sig')

    df_res.to_csv(os.path.join(OUT_DIR, '选股结果汇总.csv'), index=False, encoding='utf-8-sig')

    print(f'[4/4] 完成！总命中 {len(df_res)} 条（去重股票 {df_res["code"].nunique()} 只）')
    print(f'耗时: {time.time()-start:.0f}s')
    print(f'输出: {OUT_DIR}')


if __name__ == '__main__':
    main()
