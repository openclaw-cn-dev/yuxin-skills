---
name: yuxin-ras-topic-miner
description: "渔芯 RAS/水产养殖/AI 行业话题挖掘 — 垂直域选题引擎。触发：cron 每日选题、内容工厂批量产出时调用。"
license: MIT
metadata:
  category: research
  priority: P1
  depends_on: [rkr_reader, rkr-deep-query]
---

# yuxin-ras-topic-miner

渔芯行业话题挖掘引擎。专注于 RAS 水产养殖 / AI / 工厂设备 三大垂直域，**自动发现可写话题**。

## 适用场景

- 每日 cron（8:00）跑一次，输出 5 条候选选题
- 内容运营 agent 启动时初始化选题池
- 热点蹭流（V2 接入热搜 API）

## 工作流（5 步）

### Step 1: 三大域数据源

```
RAS 水产养殖：
  - 农业农村部 RAS 政策
  - 沿海省份补贴文件
  - 行业白皮书（每年发布）
  - 头部企业新闻（通威、海大、渔美康）

AI / Agent：
  - arXiv 每日论文
  - GitHub trending AI 仓库
  - Hugging Face 热门模型
  - 头部公司 blog（OpenAI/Anthropic/Google）

渔芯工厂设备：
  - 设备出货量数据
  - 客户案例库
  - 内部 RKR 素材
```

### Step 2: 关键词模板库
参考 `references/topic_templates.md`：
- 「<补贴政策> + 解读」
- 「<技术名词> + 入门/避坑/对比」
- 「<客户类型> + 案例」
- 「<时间节点> + 趋势预测」

### Step 3: 候选生成（5 条/天）

每条候选包含：
- 标题
- 关键词（3-5 个）
- 数据点（≥ 1 个 RKR 引用）
- 建议平台（公众号/抖音/知乎）
- 优先级（P0/P1/P2）

```json
{
  "topic_id": "tc_20260729_xxx",
  "title": "RAS 循环水养殖补贴新政：广东老板能领多少钱？",
  "keywords": ["RAS", "补贴", "广东", "循环水"],
  "data_points": ["2026 广东农业厅补贴最高 50 万"],
  "suggested_platforms": ["公众号", "抖音"],
  "priority": "P1",
  "source": "ras_industry_news"
}
```

### Step 4: 写入 RKR
调用 `rkr_reader.add_topic_candidate`：
```python
for topic in candidates:
    add_topic_candidate(
        topic=topic["title"],
        source=topic["source"],
        keywords=topic["keywords"],
        priority=topic["priority"],
    )
```

### Step 5: 推送华哥审核
调 `feishu_content_bridge.send_text`：
```
📋 今日 5 条选题候选（请挑选 1-2 条进工厂）：
1. P1 · RAS 循环水养殖补贴新政...
2. P1 · AI Agent 在工厂的真实落地案例...
...
```

## 关键参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| 候选数/天 | 5 | 避免过载 |
| 优先级分布 | P0=0-1, P1=2-3, P2=1-2 | 保证质量 |
| 关键词 | ≥ 3 个 | 利于搜索 |

## 失败模式

| 现象 | 解决 |
|------|------|
| 没有热点 | 用 RKR 内部素材凑数（渔芯项目/客户案例） |
| 选题太泛 | 退回 Step 2 模板，加"广东/江苏/工厂"等限定词 |
| 同质化 | 强制三域各 ≥ 1 条 |

## 相关 Skills

- `yuxin-rkr-deep-query` — 选题确定后查证
- `yuxin-content-factory` — 选题后进工厂
