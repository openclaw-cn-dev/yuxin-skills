# 6 个选股维度算法详解

## 维度 1：涨停 + 异动 + 倍量

**目的**：找近期有赚钱效应的活跃票。

**指标**：
- `zt_20d`: 20 日内涨停次数（`close / prev_close >= 0.095`）
- `max_change_30d`: 30 日内最大涨跌幅 `max(close) / first_close - 1`
- `max_vol_ratio`: 30 日内最大量比 `volume / ma5.shift(1)`

**判定**：三个条件同时满足
- `zt_20d >= 1`
- `max_change_30d >= 0.15` (15%)
- `max_vol_ratio >= 2.0` (倍量)

**Score 公式**：`min(zt_20d * 10, 30) + min(max_change_30d * 100, 50) + min(max_vol_ratio * 5, 30)`

**代码**：

```python
def pick_dim_zt(df, code):
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
```

---

## 维度 2：上升趋势

**目的**：找趋势票，强者恒强。

**指标**：
- `new_high_count`: 30 日内后 15 日 vs 前 15 日，创新高次数
- `high_trend`: 后段高点涨幅 vs 前段高点
- `low_trend`: 后段低点涨幅 vs 前段低点（**不上移 = ≥ 0%**）
- `ma5_above_ma30`: 短期均线在长期均线上方

**判定**：
- 后段 `high.max() > 前段 high.max()` (高位新高)
- 后段 `low.min() >= 前段 low.min()` (低位不上移)
- `new_high_count >= 1`
- `MA5 > MA30`

**Score 公式**：`50 + new_high_count * 10 + (ma5 > ma30) * 20`

**代码**：

```python
def pick_dim_trend(df, code):
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
            'score': 50 + new_high_count * 10 + 20,
            'new_high_count': int(new_high_count),
            'high_trend': round((back['high'].max() / front['high'].max() - 1) * 100, 1),
            'low_trend': round((back['low'].min() / front['low'].min() - 1) * 100, 1),
            'ma5_above_ma30': True,
        }
    return None
```

---

## 维度 3：放量长上影线（最严，老大特别关注）

**目的**：找主力试盘 + 蓄势待发。长期横盘或上涨初期，突发放量上影。

**指标**：
- `shadow_pct`: 上影线长度 / 收盘价 × 100（%）
- `vol_ma20_ratio`: 当日量 / 20 日均量
- `broke_prev_high`: 是否突破前 20 日高点
- `phase`: 横盘 (前 30-60 日振幅 < 30%) / 上涨初期 (最近 10 日涨幅 0-15%)

**判定**：
- `phase` 是 横盘 或 上涨初期
- 最近 20 日内出现 `shadow_pct >= 3%` 的 K 线
- **补充规则**：如果该上影线突破了前 20 日高点 (`broke_prev_high=True`)，**则量必须 > 20 日均量 (`vol_ma20_ratio >= 1.0`)**，否则不命中

**Score 公式**：`50 + shadow_pct * 5 + vol_ma20_ratio * 10`

**代码**：

```python
def pick_dim_shadow(df, code):
    if len(df) < 60: return None
    df = df.copy()
    df['upper_shadow'] = df['high'] - df[['open','close']].max(axis=1)
    df['shadow_pct'] = df['upper_shadow'] / df['close'] * 100
    df['vol_ma20'] = df['volume'].rolling(20).mean()

    # 阶段判定
    front = df.iloc[30:60] if len(df) >= 60 else df.head(30)
    amp = (front['high'].max() - front['low'].min()) / front['low'].min()
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

    # 突破 + 量验证
    idx = df.index[df['date'] == best['date']].tolist()[0]
    prev_max_high = df.iloc[max(0, idx-20):idx]['high'].max() if idx > 0 else 0
    broke_high = best['high'] > prev_max_high
    vol_ratio = best['volume'] / best['vol_ma20'] if best['vol_ma20'] > 0 else 0
    if broke_high and vol_ratio < 1.0: return None  # 老大特别要求的补充规则

    return {
        'code': code, 'dim': '3',
        'score': 50 + best['shadow_pct'] * 5 + vol_ratio * 10,
        'shadow_pct': round(best['shadow_pct'], 2),
        'vol_ma20_ratio': round(vol_ratio, 2),
        'broke_prev_high': broke_high,
        'phase': '横盘' if is_oscillation else '上涨初期',
    }
```

---

## 维度 4：量价齐升突破（占位，下一版实现）

**目的**：找突破关键阻力位 + 量能跟上的票。

**指标**：
- 突破 N 日（默认 20/60/120）新高
- 当日量 ≥ 前 5 日均量 × 2

---

## 维度 5：横盘蓄势（占位，下一版实现）

**目的**：找长期横盘 + 最近放量异动的票。

**指标**：
- 30-60 日振幅 < 30%
- 最近 5 日均量 > 前 30 日均量 × 1.5
- 最近 5 日有 ≥ 1 根中阳线（涨幅 > 3%）

---

## 维度 6：涨停回踩买点（占位，下一版实现）

**目的**：找涨停板后回踩支撑位的"二买"信号。

**指标**：
- 最近 30 日内有过涨停
- 涨停后 3-10 日内
- 最低价 ≤ 涨停日开盘价 × 1.05（回踩到涨停日开盘附近）
- 不破涨停日最低价
