---
name: yuxin-rkr-deep-query
description: "渔芯 RKR 知识库深度查询 — 替代 Bing 搜索，给内容生成提供事实/数据/案例支撑。触发：需要事实核查、行业数据、案例引用时调用。"
license: MIT
metadata:
  category: research
  priority: P0
  depends_on: [rkr_reader MCP]
---

# yuxin-rkr-deep-query

渔芯 RKR 知识库深度查询。给内容生成（公众号/抖音/知乎）提供事实/数据/案例支撑，**替代 Bing/Google 搜索**。

## 适用场景

- 公众号/知乎写作需要查证数据/案例
- 选题阶段需要找行业素材
- 行业研究/竞品分析

## 工作流（4 步）

### Step 1: 接收查询请求
```python
query: str
n_results: int = 8
collection: str = "ras" | "ai" | "industry" | "default"
min_score: float = 0.6
```

### Step 2: 调用 rkr_reader.search
```python
from rkr_reader import search

results = search(
    query=query,
    n_results=n_results,
    collection=collection,
    min_score=min_score,
)
```

### Step 3: 素材整理
按"事实/数据/案例"分类返回：
- **事实**：行业定义、原理（≥ 1 条）
- **数据**：具体数字、增长率、市场规模（≥ 1 条）
- **案例**：渔芯/同行的实际项目（≥ 1 条）

### Step 4: 写入 RKR（如果新发现）
```python
from rkr_reader import add_topic_candidate
# 如果查询结果不充分，把"待补充素材"加入候选
add_topic_candidate(
    topic="待补充：XX 数据",
    source="content_research",
    priority="P2",
    notes="content_id=xxx 在用",
)
```

## 关键参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| n_results | 8 | 召回数量 |
| min_score | 0.6 | 相似度阈值 |
| collection | 按 query 自动选 | ras/ai/industry/default |

## 集合选择策略

| 查询关键词 | 集合 |
|------------|------|
| 养殖/鱼/水产/RAS | ras |
| AI/Agent/算法/模型 | ai |
| 政策/补贴/市场/趋势 | industry |
| 渔芯/产品/案例 | default |

## 降级策略

- RKR 不可用 → 返回空结果 + warning，不阻塞内容生成
- 召回 < 2 条 → 提示"素材不足，建议加一条 FindEra 调研"
- 命中 `source=fallback_default` → 提醒"RKR 未连接，数据可能不准"

## 相关 Skills

- `yuxin-promoter-wechat` — 写作时调用
- `yuxin-promoter-zhihu` — 必调用（知乎靠数据论证）
- `yuxin-compliance-checker` — 数据引用前用
