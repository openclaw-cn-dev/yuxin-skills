# 风险评分 + 持仓交叉 + 公司研究 实战手册

## 1. 风险评分公式（"哪个风险低"专用）

### 技术分（满分 20）
```python
def technical_score(df, code):
    """df: 60 日 K 线"""
    cur = df['close'].iloc[-1]
    prev_30 = df['close'].iloc[-31]
    recent = df.tail(30)
    change_30d = (cur - prev_30) / prev_30 * 100
    volatility = ((recent['high'].max() - recent['low'].min()) / cur) * 100
    zt_count = 0
    for i in range(1, len(recent)):
        if (recent.iloc[i]['close'] - recent.iloc[i-1]['close']) / recent.iloc[i-1]['close'] >= 0.095:
            zt_count += 1
    max_high = recent['high'].max()
    min_low = recent['low'].min()
    from_high_pct = (cur - max_high) / max_high * 100
    max_drawdown = (min_low - prev_30) / prev_30 * 100
    
    score = 0
    # 振幅
    score += 1 if volatility < 40 else (2 if volatility < 60 else (3 if volatility < 80 else 4))
    # 涨幅
    score += 1 if change_30d < 30 else (2 if change_30d < 60 else (3 if change_30d < 100 else 4))
    # 涨停数
    score += 1 if zt_count == 0 else (2 if zt_count == 1 else (3 if zt_count == 2 else 4))
    # 距高点
    score += 1 if from_high_pct > -5 else (2 if from_high_pct > -15 else (3 if from_high_pct > -25 else 4))
    # 最大回撤
    score += 1 if max_drawdown > -10 else (2 if max_drawdown > -20 else (3 if max_drawdown > -30 else 4))
    return score  # 越低越安全
```

### 资金画像分（满分 16）
```python
def capital_score(df, code):
    cur = df['close'].iloc[-1]
    prev_30 = df['close'].iloc[-31]
    change_30d = (cur - prev_30) / prev_30 * 100
    df['vol_ma5'] = df['volume'].rolling(5).mean()
    df['vol_ratio'] = df['volume'] / df['vol_ma5'].shift(1)
    high_vol_days = (df['vol_ratio'] > 2.0).sum()
    zt_count = 0  # 同上
    recent_vol = df['volume'].tail(5).mean()
    prev_vol = df['volume'].iloc[-10:-5].mean()
    vol_trend = "放大" if recent_vol > prev_vol * 1.3 else ("缩量" if recent_vol < prev_vol * 0.7 else "平稳")
    
    score = 0
    score += 1 if change_30d < 30 else (2 if change_30d < 60 else (3 if change_30d < 100 else 4))
    score += 1 if zt_count == 0 else (2 if zt_count == 1 else (3 if zt_count == 2 else 4))
    score += 1 if high_vol_days <= 1 else (2 if high_vol_days <= 3 else (3 if high_vol_days <= 6 else 4))
    score += 3 if vol_trend == "缩量" else (2 if vol_trend == "平稳" else 1)
    return score
```

### 评级
- 技术分 ≤10 低风险，10-14 中风险，≥14 高风险
- 资金画像分 ≤8 低风险，8-12 中风险，≥12 高风险
- 两分相加总分 ≤18 推荐，18-25 中性，≥25 避开

## 2. 持仓交叉验证（老大 100% 会问的需求）

```python
import pandas as pd
df_all = pd.read_csv(r'C:\Users\Administrator\Desktop\股票\v2_选股结果汇总.csv')

# 老大持仓代码（手工维护或从 持仓.csv 读）
boss_holdings = ['600293', '600301', '600114', '600546', '600909', 
                 '601101', '601869', '603120', '603150', '603002']

# 3 维度全中代码
codes_1 = set(df_all[df_all['dim']==1]['code'])
codes_2 = set(df_all[df_all['dim']==2]['code'])
codes_3 = set(df_all[df_all['dim']==3]['code'])
codes_3d = codes_1 & codes_2 & codes_3

# 交叉
boss_in_top = [c for c in boss_holdings if c in codes_3d]
boss_score = {}
for c in boss_in_top:
    sub = df_all[df_all['code']==c]
    boss_score[c] = sub['score'].sum()

print(f'老大持仓 {len(boss_in_top)}/{len(boss_holdings)} 入榜')
for c, s in sorted(boss_score.items(), key=lambda x: -x[1]):
    name = df_all[df_all['code']==c].iloc[0]['name']
    rank = sorted(boss_score.values(), reverse=True).index(s) + 1
    print(f'  {c} {name}: {s:.1f} 分 (排名 {rank})')
```

## 3. 加严筛选链（3 维度全中 → 58 → 48）

```python
df_102 = pd.read_csv(r'C:\Users\Administrator\Desktop\股票\102只3维度全中股_详细.csv')

# 严 1: 破前高 + 量价齐升
f1 = df_102[(df_102['破前高']=='是') & (df_102['量20均比']>1.0)]
print(f'严 1: {len(f1)} 只')

# 严 2: 上影 > 5%
f2 = f1[f1['上影%']>5.0]
print(f'严 2: {len(f2)} 只')

# 报告时**显式列出每档过滤掉了多少只**
# 102 → 58 → 48
```

## 4. 中国公司研究 4 件套（求职类任务）

```python
# 4 个信息源
sources = {
    'BOSS 直聘': f'https://www.zhipin.com/web/geek/job?query={company_name}',
    '爱企查/天眼查': f'https://www.tianyancha.com/search?key={company_name}',
    '头条搜索': f'https://www.toutiao.com/search/?keyword={company_name}+招聘',
    '百度': f'https://www.baidu.com/s?wd={company_name}+怎么样',
}

# 抓取策略（详见 chinese-rag-pipeline）
# 1. 头条搜：拿公司新闻、行业评价（最准）
# 2. BOSS：拿招聘需求、岗位、薪资
# 3. 天眼查：拿法人、股东、风险
# 4. 百度：拿百度百科、贴吧口碑

# 报告模板
report_template = {
    '基本信息': '公司全称/成立时间/注册资本/地址',
    '业务版图': '主营产品/主战场/未来规划',
    '行业背景': '产业链/政策/竞争',
    'BOSS 招聘': '在招岗位/薪资/要求',
    '合规性': '失信/处罚/司法风险',
    '建议': '投资/合作/入职 评级',
}
```

## 5. 求职类任务输出模板（无经验者）

```python
# 老大说"我想做 X 但没经验"
template = {
    '现实': '直接应聘 X 通常被拒（要 1-3 年经验）',
    '3 步走': {
        '第 1 步': {'岗位': 'X 助理/跟单员/运营', '时间': '0-6 月', '薪资': '5-7K'},
        '第 2 步': {'岗位': 'X 业务助理', '时间': '6-12 月', '薪资': '7-9K'},
        '第 3 步': {'岗位': 'X 正式业务', '时间': '1-2 年', '薪资': '8-15K'},
    },
    '5 周速成': ['W1: 基础', 'W2: 产品', 'W3: 场景口语', 'W4: 平台', 'W5: 投 + 面试'],
    '高频面试问题': [
        ('为什么选 X', '行业趋势 + 5-10 年黄金期'),
        ('没经验怎么上手', '5 周速成 + 助理岗切入 + 6 月转岗'),
        ('薪资期望', '5-7K 能接受 + 3 月评估 + 6 月调薪'),
    ],
    '收入预测': '0-6 月 5-7K → 1-3 年 8-15K → 3-5 年 15-30K',
    '4 条硬核建议': [
        '先应聘低门槛岗（跟单/助理/运营）',
        '边投边学（面试就是学习）',
        '先入行（3-5 年后才有议价权）',
        '学 100 句口语就够（别等完美）',
    ],
}

# 文件输出位置
output_dir = r'C:\Users\Administrator\Desktop\公司分析\'
```

## 6. 飞书 home channel 推送模板

```python
# A股选股 报告推送
msg = f'''🎯 A股选股 {date} 报告 (全A 5527 只 跑完 10'17'')

📊 命中汇总:
• 维度1: {len(dim1)} 只
• 维度2: {len(dim2)} 只
• 维度3: {len(dim3)} 只 (TOP50)
• 2+维度: {len(strong)} 只
• 3维度全中: {len(top3)} 只 🔥

🔥 长上影 TOP 5:
1. {top1_code} {top1_name} - {top1_shadow}%
2. {top2_code} {top2_name} - {top2_shadow}%
3. {top3_code} {top3_name} - {top3_shadow}%
4. {top4_code} {top4_name} - {top4_shadow}%
5. {top5_code} {top5_name} - {top5_shadow}%

🚀 3维度全中 ({len(top3)}只): {top3_str}

📁 全部结果: C:\\Users\\Administrator\\Desktop\\股票\\
  v2_维度1/2/3_结果.csv + v2_三维度全中.csv

⚠️ 仅供研究,不构成投资建议'''

# 关键字段（不要漏）：
# 1. 跑批范围 + 耗时
# 2. 各维度命中数
# 3. TOP 5 长上影（老大关注点）
# 4. 3 维度全中前 15（老大持仓交叉会用到）
# 5. 文件路径
# 6. 风险提示（必带）

# 老大持仓交叉（**必带，老大 100% 会问**）
boss_section = f'''
⚡ 老大持仓 {len(boss_in_top)}/{len(boss_holdings)} 入榜:
✅ {boss_code_1} {boss_name_1} ({boss_score_1})
✅ {boss_code_2} {boss_name_2} ({boss_score_2})
...

📈 老大持仓平均分 {avg_score:.1f} (前 30%)'''
```
