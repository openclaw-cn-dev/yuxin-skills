# A 股选股 - 3 维度全中 + 严格过滤（实战变体）

**来源**：2026-06-12 沪市 v1 + 全 A v2 实战后追加。

## 常见老板变体

老板在 v1/v2 跑完后，会进一步要求：

| 变体 | 描述 | 代码模式 |
|---|---|---|
| **3 维度全中** | 同时满足 3 维度 | `codes_3d = set1 & set2 & set3` |
| **3 维度全中 + 严格过滤** | 破前高 + 量/MA20 > 1.0 | 再加 2 个 mask |
| **综合分 TOP N** | 3 个维度分相加排 | `df['总综合分'] = r1.score + r2.score + r3.score` |
| **特定阶段** | 只看"上涨初期"或"横盘" | `df = df[df['phase'] == '上涨初期']` |
| **特定涨幅** | 30 日涨幅 < 100% | `df = df[df['max_change_30d'] < 100]` |

## 严格过滤（破前高 + 量价齐升）

老板原话（6/12 第三次跑）：
> "上影线突破前高时，量必须比前面高才行 **要同时满足以上全部条件的**"

```python
# 3 维度全中
codes_1 = set(df_all[df_all['dim'] == 1]['code'])
codes_2 = set(df_all[df_all['dim'] == 2]['code'])
codes_3 = set(df_all[df_all['dim'] == 3]['code'])
codes_3d = codes_1 & codes_2 & codes_3  # 102 只

# 严格条件：破前高 + 量/MA20 > 1.0
# ⚠️ 注意：df_all 里 dim 和 code 都是 int（不是 str），要保持一致
filtered = []
for code in codes_3d:
    sub = df_all[df_all['code'] == code]
    r1 = sub[sub['dim'] == 1]
    r2 = sub[sub['dim'] == 2]
    r3 = sub[sub['dim'] == 3]
    if len(r1) == 0 or len(r2) == 0 or len(r3) == 0:
        continue
    r1, r2, r3 = r1.iloc[0], r2.iloc[0], r3.iloc[0]

    if r3['broke_prev_high'] and r3['vol_ma20_ratio'] > 1.0:
        filtered.append({
            '代码': str(code).zfill(6),  # ⚠️ 转 str + zfill 保证 6 位
            '名称': r1['name'],
            '总综合分': round(r1['score'] + r2['score'] + r3['score'], 1),
            '涨停数': int(r1['zt_20d']),
            '30日涨幅%': r1['max_change_30d'],
            '上影%': r3['shadow_pct'],
            '量/20均': r3['vol_ma20_ratio'],
            '破前高': '是',
            '阶段': r3['phase'],
        })

df = pd.DataFrame(filtered).sort_values('总综合分', ascending=False).reset_index(drop=True)
```

**实测**：102 只 → 58 只 (破前高) → 48 只 (再上影% > 5%)

## ⚠️ 5 个 Python 坑（本次实战踩到）

### 1. `dim` 和 `code` 在 df_all 里是 int，不是 str

```python
# 错误写法（用 '1'、'2'、'3' 字符串）
codes_1 = set(df_all[df_all['dim'] == '1']['code'])  # → 0 只!

# 正确（用 int 1/2/3）
codes_1 = set(df_all[df_all['dim'] == 1]['code'])  # → 625 只
```

**Debug 套路**：跑筛选前 `print(df_all['dim'].dtype)` 和 `print(df_all['dim'].unique())` 确认类型。

### 2. 3 维度全中筛选 = set 交集

不能直接 `df_all.groupby('code').size() == 3`，因为这只表示同一只票有 3 个维度的记录，但维度值可能重复。

```python
# 正确：分别取每维度的 code set，再 & 交集
codes_3d = (set(df_all[df_all['dim']==1]['code'])
            & set(df_all[df_all['dim']==2]['code'])
            & set(df_all[df_all['dim']==3]['code']))
```

### 3. code 一定要 `str(code).zfill(6)`

akshare 返回的 code 是 int（如 `000636`），`str()` 出来变 `'636'`，**少了前导 0**。`zfill(6)` 补回 `000636`。

### 4. `[r1, r2, r3] = sub[mask].iloc[0]` 之前要 `len > 0` 检查

否则 `iloc[0]` 抛 IndexError。

### 5. set 交集得到的是 int（不是 str）—— 跟 `df['code']`（pandas 自动转）能比，但跟 `str(int_code).zfill(6)` 拿到的 str 不一致

如果老板要查具体股票 = `str(int_code).zfill(6)` 重新转换。

## 综合分 TOP 20 模板

```python
# 加总综合分
df['总综合分'] = (
    df.groupby('code')['score']
    .transform(lambda s: s.sum() if len(s) == 3 else 0)
)
df = df[df['总综合分'] > 0].drop_duplicates('code').sort_values('总综合分', ascending=False)
```

或更稳：

```python
scores = {}
for code in codes_3d:
    sub = df_all[df_all['code'] == code]
    total = sub['score'].sum()
    scores[code] = total
sorted_codes = sorted(scores.items(), key=lambda x: x[1], reverse=True)
```

## 实战效果（2026-06-12）

| 阶段 | 数量 |
|---|---|
| 沪市 v1 跑完 | 14 只 3 维度全中 |
| 全 A v2 跑完 | 102 只 3 维度全中 |
| 加严格过滤（破前高 + 量>1.0）| 58 只 |
| 再加上影 > 5% | 48 只 |
| 老板持仓 10 只 | 全部在 102 只里 |
| 老大持仓平均综合分 | **367.9**（前 30%）|

## 跑批输出文件命名

| 文件 | 内容 |
|---|---|
| `v2_三维度全中.csv` | 102 只基础 |
| `v2_三维度全中_严格过滤.csv` | 58 只加严 |
| `102只3维度全中股_详细.csv` | 102 只 + 11 列详情 |
| `102只加严筛选_破前高+量齐.csv` | 58 只加严详情 |

## 老板的"严格条件"用词（沟通模板）

老板会反复说："**要同时满足以上全部条件的**" / "**量必须比前面高才行**" / "**破前高的才算**"——

- 听到 "**同时满足**" → set 交集
- 听到 "**量必须 > X**" → 2 个 mask 一起加
- 听到 "**才算 / 不算**" → 严格过滤，不是 OR 是 AND
