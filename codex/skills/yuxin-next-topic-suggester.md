---
name: yuxin-next-topic-suggester
description: "渔芯下一选题建议器 — 基于互动数据 + RKR 知识图谱 + 行业热点，建议下一批选题。触发：周报后、cron 每周一选题更新时调用。"
license: MIT
metadata:
  category: feedback
  priority: P1
  depends_on: [engagement-tracker, rkr-deep-query]
---

# yuxin-next-topic-suggester

渔芯下一选题建议器。基于**自进化闭环**：本周数据 → 找规律 → 建议下周选题。

## 适用场景

- 周一数据周报后，自动生成下周 5 条选题
- 月底规划下月内容方向
- 互动数据突增的选题 → 扩写/出姐妹篇

## 工作流（5 步）

### Step 1: 读取互动数据
```python
from content_publisher import get_publish_status
# 最近 7-30 天
records = get_publish_status(limit=100)
# 配合 engagement_log.jsonl
```

### Step 2: 找爆款规律
```python
top_articles = sorted(records, key=lambda r: r["engagement_rate"], reverse=True)[:5]
# 分析：标题模式 / 话题类型 / 配图风格 / 字数
```

常见规律（V1 规则）：
- 「数字 + 痛点 + 解决方案」标题互动率 +30%
- 1500-2000 字公众号完读率最高
- 抖音 30-45s 完播率最佳
- 知乎"反常识"开头 +50% 赞同

### Step 3: 找 RKR 知识图谱空白
```python
from rkr_reader import list_collections
# 哪些集合文档少 → 选题填空
```

### Step 4: 生成 5 条候选
```python
[
  {
    "title": "类似爆款的姐妹篇",
    "pattern": "extending_top_hit",
    "priority": "P0",
    "reasoning": "上周《RAS 补贴新政》互动率 9.2%，扩写《补贴申请流程》"
  },
  ...
]
```

### Step 5: 写入 RKR + 推送
```python
from rkr_reader import add_topic_candidate
for topic in candidates:
    add_topic_candidate(topic=topic["title"], priority=topic["priority"], source="next_topic_suggester")
```

推送华哥：
```
📋 下周 5 条选题建议（基于本周数据）：
P0 · RAS 补贴申请流程（扩写自本周爆款）
P1 · AI Agent 在工厂的真实落地（呼应热点）
...
```

## 关键参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| 候选数 | 5 | 避免过载 |
| 时间窗 | 7 天 | 太长没参考性 |
| 规则权重 | 经验值 | V2 接入 ML 优化 |

## 选题来源类型

1. **extending_top_hit** — 扩写本周爆款（最稳）
2. **gap_in_rkr** — 填补知识库空白
3. **hot_topic** — 蹭行业热点
4. **competitor_followup** — 同行已写渔芯跟进
5. **seasonal** — 季节性/政策时间窗

## 失败模式

| 现象 | 解决 |
|------|------|
| 没有爆款参考 | 用"季节性"+"政策时间窗"兜底 |
| 建议太相似 | 强制 5 种 pattern 各 1 条 |
| 华哥不喜欢 | 收集反馈，调规则权重 |

## 自进化闭环示意

```
选题 → 内容 → 发布 → 数据 → 建议 → 选题
   ↑___________________________↓
```

## 相关 Skills

- `yuxin-engagement-tracker` — 上游数据源
- `yuxin-ras-topic-miner` — 配合做新选题发现
- `yuxin-rkr-deep-query` — 验证选题素材
