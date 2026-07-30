---
name: yuxin-engagement-tracker
description: "渔芯内容互动数据回流 — 抓取各平台阅读/点赞/评论/转化数据，写入 RKR 知识库。触发：cron 周一数据汇总、单篇发布后跟踪时调用。"
license: MIT
metadata:
  category: feedback
  priority: P1
  depends_on: [content-publisher, rkr_reader]
---

# yuxin-engagement-tracker

渔芯内容互动数据回流器。把各平台的阅读/点赞/评论/转化数据抓回来，写入 RKR 知识库，**形成自进化闭环**。

## 适用场景

- 每日 cron 抓取昨日发布内容数据
- 周一生成数据周报
- 单篇发布后 N 小时跟踪（V2 接入）

## 工作流（5 步）

### Step 1: 列出已发布内容
```python
from content_publisher import get_publish_status
records = get_publish_status(limit=50)
# 过滤昨日发布的
```

### Step 2: 抓取各平台数据

V1 阶段：手工录入（华哥/同事在飞书回复"XX 公众号阅读 800"）
V2 阶段：自动 API 抓取

```python
def fetch_wechat_data(publish_id):
    """微信公众号数据抓取（V2 接入）"""
    # 微信公众平台 API: /datacube/getarticlesummary
    pass

def fetch_douyin_data(publish_id):
    """抖音数据抓取（V2 接入）"""
    pass
```

V1 接收手工数据：
```python
def record_engagement(
    publish_id: str,
    platform: str,
    views: int,
    likes: int,
    comments: int,
    shares: int,
    conversions: int = 0,  # 转化（咨询/下载）
):
    pass
```

### Step 3: 计算核心指标
```
互动率 = (likes + comments + shares) / views × 100%
完读率 = (视频完播 / 播放) × 100%  # 仅抖音/B站
转化率 = conversions / views × 100%
```

### Step 4: 写入 RKR
```python
from rkr_reader import _rkr_post  # V2 接入
# 写入 engagement_log collection
```

V1 写到本地：
```python
# logs/engagement_log.jsonl
{
  "publish_id": "pub_20260729_xxx",
  "platform": "wechat",
  "date": "2026-07-29",
  "views": 800,
  "likes": 35,
  "comments": 12,
  "shares": 8,
  "engagement_rate": 6.875,
  "conversions": 3
}
```

### Step 5: 推送数据报告
周一 10:00 自动汇总推送：
```
📊 本周内容数据周报
公众号：
  - 总阅读 5800
  - 平均互动率 7.2%
  - 最佳文章：《RAS 补贴新政》（阅读 1500）
抖音：
  - 总播放 12000
  - 完播率 45%
  - 最佳视频：《3 步搞定成本计算》
...
```

## 关键参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| 抓取时间 | 每日 22:00 | 抓昨日数据 |
| 周报时间 | 每周一 10:00 | 汇总上周 |
| 转化追踪 | 30 天 | 长尾转化 |

## 关联指标

| 平台 | 重点指标 |
|------|----------|
| 公众号 | 阅读 / 在看 / 转化 |
| 抖音 | 完播率 / 互动率 / 主页访问 |
| 知乎 | 赞同 / 收藏 / 评论质量 |
| B站 | 三连 / 弹幕 / 收藏 |
| 小红书 | 点赞 / 收藏 / 评论数 |

## 失败模式

| 现象 | 解决 |
|------|------|
| API 抓不到 | 降级到手工录入 |
| 数据有延迟 | 加 24h 抓取窗口 |
| 跨平台对比 | 统一计算「互动率」 |

## 相关 Skills

- `yuxin-next-topic-suggester` — 数据喂给选题建议
- `yuxin-content-factory` — 数据反馈到工厂调整
