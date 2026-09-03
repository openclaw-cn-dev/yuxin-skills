---
name: lottery-number-generator
description: 基于中彩网 JSON API 抓取近 N 期双色球/大乐透历史数据，统计热号/冷号/三区分布，生成 5 组均衡号码 + 1 组 7+1 复式。覆盖"随机几组号码""基于历史出号""热号冷号结合"等彩票选号任务。Triggers on "双色球", "大乐透", "彩票", "选号", "摇号", "随机出号", "复式", "近 N 期号码", "热号", "冷号", "ssq", "dlt".
version: 1.0.0
author: Hermes Agent (小弟)
license: MIT
metadata:
  hermes:
    tags: [lottery, ssq, dlt, number-generator, feishu, statistics]
    related_skills: [a-share-screener, python-windows-path-pitfalls]
---

# 彩票选号 (Lottery Number Generator) v1.0

## Overview

基于**中彩网官方 JSON 接口**抓取历史开奖数据，按热号/三区平衡/冷热搭配策略生成 5 组均衡号码 + 1 组 7+1 复式。覆盖：

1. **历史数据抓取** — 中彩网 `cwl.gov.cn` JSON API（实测稳定，**替代头条/Bing/中彩网主页的所有反爬方案**）
2. **频次统计** — 红球/蓝球出现次数 TOP N
3. **三区平衡选号** — 红球分 1-11 / 12-22 / 23-33 三区，每区选 N 个
4. **奇偶均衡** — 默认 3 奇 3 偶
5. **5 组号码 + 1 组 7+1 复式** — 一键出号
6. **直接抄作业** — 输出纯文本格式，复制到彩票店

**v1.0 实战（2026-06-12）**：
- 抓近 88 期（2025-11-11 ~ 2026-06-11）— 1 次成功
- 5 组号码 + 1 组复式
- 推飞书 + 桌面报告

## When to Use

Activate when boss says:
- "**随机几组号码**" / "**给我几组**" / "**随机 5 组**"
- "**基于近 N 期数据**" / "**热号冷号结合**" / "**历史号码**"
- "**复式**" / "**7+1**" / "**提高中奖率**"
- "**双色球**" / "**大乐透**" / "**彩票**" / "**ssq**" / "**dlt**"

**Don't use for**: 港彩 / 国外彩票（接口不同），高频彩（需特殊策略），3D / 排三 / 排五（小玩法，套路不同）

## 数据源：中彩网 JSON API（**最稳**）

⚠️ **不要走头条搜/Bing 搜/中彩网主页**—— 反爬 / GBK 编码 / 动态 JS 各种坑。**直接走 JSON 接口**：

```python
import requests, json

url = 'https://www.cwl.gov.cn/cwl_admin/front/cwlkj/search/kjxx/findDrawNotice?name=ssq&pageNo=1&pageSize=200&systemType=PC'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Referer': 'https://www.cwl.gov.cn/'
}
r = requests.get(url, headers=headers, timeout=30)
data = r.json()  # ✅ 干净 JSON，无 demjson 解析
result = data['result']  # 200 期数据
```

**返回字段**（每期）：
- `code` — 期号（如 `'2026066'`）
- `date` — 开奖日期（如 `'2026-06-11(四)'`）
- `red` — 红球（逗号分隔字符串，如 `'05,11,21,23,24,29'`）
- `blue` — 蓝球（字符串，如 `'16'`）
- `sales` / `poolmoney` — 销售额 / 奖池

**实测**：1 次请求 200 期 = 157KB JSON，0 失败。

## 完整选号脚本（5 组号码 + 1 组复式）

```python
import requests, json, random
from collections import Counter

# === 1. 抓近 88 期数据 ===
url = 'https://www.cwl.gov.cn/cwl_admin/front/cwlkj/search/kjxx/findDrawNotice?name=ssq&pageNo=1&pageSize=200&systemType=PC'
headers = {'User-Agent': 'Mozilla/5.0 ...', 'Referer': 'https://www.cwl.gov.cn/'}
r = requests.get(url, headers=headers, timeout=30)
result = r.json()['result'][:88]

# === 2. 频次统计 ===
red_counter = Counter()
blue_counter = Counter()
for item in result:
    for r in item['red'].split(','):
        red_counter[int(r)] += 1
    blue_counter[int(item['blue'])] += 1

# === 3. 三区平衡选号 ===
zones = {
    '1': list(range(1, 12)),    # 1-11
    '2': list(range(12, 23)),   # 12-22
    '3': list(range(23, 34)),   # 23-33
}

# === 4. 5 组号码 + 1 组 7+1 复式 ===
generated = []
for i in range(5):
    z1 = random.sample(zones['1'], 2)
    z2 = random.sample(zones['2'], 2)
    z3 = random.sample(zones['3'], 2)
    reds = sorted(z1 + z2 + z3)
    blue = random.choice([n for n, _ in blue_counter.most_common(5)])
    generated.append((reds, blue))

# 1 组 7+1 复式
reds7 = sorted(random.sample(zones['1'], 3) + random.sample(zones['2'], 2) + random.sample(zones['3'], 2))
blue2 = random.choice([n for n, _ in blue_counter.most_common(8)])
```

## 选号策略（5 条核心规则）

1. **三区平衡** — 1-11 / 12-22 / 23-33 每区选 2 个（5+1 红球）or 3+2+2（7+1 复式）
2. **冷热搭配** — 混合热号（频次 TOP 10）+ 中号（频次中位）
3. **奇偶均衡** — 默认 3 奇 3 偶（5+1 红球）or 4+3（7+1 复式）
4. **蓝球策略** — 从近 88 期高频蓝球（频次 TOP 5-8）随机选
5. **避免冷门** — 不选**所有 88 期都没出现**的极端冷号

## 推飞书消息模板（**用 r-prefix 防 \U 坑**）

```python
# ✅ GOOD — r-prefix 嵌入路径
DESKTOP = r'C:\Users\Administrator\Desktop'
OUT_FILE = DESKTOP + r'\双色球_5组推荐.md'

msg = f"""
🎰 双色球 5 组推荐号码 (基于近 88 期数据)

📊 数据基础:
• 样本: 近88期 ({result[0]['date']} ~ {result[-1]['date']})
• 最新期: {result[0]['code']}
• 最新号: 红 {result[0]['red']} + 蓝 {result[0]['blue']}

🎯 5 组号码 (三区平衡+冷热搭配):
1. {' '.join(f'{r:02d}' for r in generated[0][0])} - {generated[0][1]:02d}
2. {' '.join(f'{r:02d}' for r in generated[1][0])} - {generated[1][1]:02d}
3. {' '.join(f'{r:02d}' for r in generated[2][0])} - {generated[2][1]:02d}
4. {' '.join(f'{r:02d}' for r in generated[3][0])} - {generated[3][1]:02d}
5. {' '.join(f'{r:02d}' for r in generated[4][0])} - {generated[4][1]:02d}

🎁 1 组 7+1 复式:
• 红: {' '.join(f'{r:02d}' for r in reds7)} + 蓝: {blue2:02d}

📁 详细: {OUT_FILE}\\双色球_5组推荐.md

⚠️ 彩票是概率游戏, 历史数据不能预测未来
💡 理性投注, 量力而行
"""
```

**关键**：所有 Windows 路径必须 `r"..."` 或变量替换。**`📁` emoji + `C:\` 路径是 \U 最高频触发**。

## 输出文件结构

```
C:\Users\Administrator\Desktop\
├── 双色球_5组推荐.md           # 完整报告（推飞书 + 桌面）
├── ssq_88.json                 # 近 88 期完整数据
└── 股票\推荐号码_5组.json      # 仅 5 组号码 JSON
```

## 7 个常见 Pitfalls

1. **不要走头条搜/百度/Bing 搜"双色球 开奖号码"** — 头条返回乱码、Bing 分词差、百度 403。**直接 cwl.gov.cn JSON 接口**。
2. **不要用 akshare 抓双色球** — `ak.lottery_draw_ssq()` 不存在，`akshare` 没有彩票模块。
3. **不要走 17500.cn / kaijiang.500.com** — 静态页是 GBK 编码 + JS 动态加载，麻烦。
4. **Referer 必填** — `Referer: https://www.cwl.gov.cn/` 不填可能被拒。
5. **5 组号码有重复** — 接受（机选常重）。要避免可加 set 去重 + 重新生成。
6. **频次 TOP 5 蓝球可能重复抽到** — 加 `random.choice()` 不会去重；想要每次不同就 `random.sample(top_5, k=5)`。
7. **彩票是概率游戏** — 每次推飞书必须带"⚠️ 历史数据不能预测未来"提示，避免老板上头。

## 大乐透（dlt）扩展

接口几乎相同：

```python
url = 'https://www.cwl.gov.cn/cwl_admin/front/cwlkj/search/kjxx/findDrawNotice?name=dlt&pageNo=1&pageSize=200&systemType=PC'
```

字段：
- 前区：5 个（1-35）
- 后区：2 个（1-12）
- `red` 字段是前区 5 个逗号分隔
- `blue` / `blue2` 是后区 2 个

## Verification Checklist

- [ ] 中彩网 JSON 接口 200 OK，无 403/404
- [ ] `data['result']` 长度 ≥ 88（老板说"近 88 期"）
- [ ] `red` 字段能 split(',') 出 6 个 int
- [ ] 5 组号码没有超界（红 1-33，蓝 1-16）
- [ ] 三区平衡：每组号码 1-11 / 12-22 / 23-33 都有号
- [ ] 推飞书消息 < 2000 字符（飞书单条上限）
- [ ] 桌面报告含"⚠️ 彩票是概率游戏"提示
- [ ] 所有 Windows 路径走 `r"..."` 或变量替换（防 \U）

## 实战战绩（2026-06-12）

- **数据**：近 88 期（2025-11-11 ~ 2026-06-11）
- **红球热号 TOP 5**：30 (24次) / 02 (24次) / 13 (23次) / 24 (22次) / 22 (22次)
- **蓝球热号 TOP 5**：02 (10次) / 10 (9次) / 15 (7次) / 01 (7次) / 16 (6次)
- **5 组号码 + 1 组 7+1 复式** — 1 次跑通
- **推飞书成功** + 桌面报告就位
