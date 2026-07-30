---
name: yuxin-platform-router
description: "渔芯多平台发布路由 — 根据内容类型/优先级/平台特性自动分派发布通道。触发：内容生成完成准备发布时调用。"
license: MIT
metadata:
  category: publish
  priority: P0
  depends_on: [content-publisher MCP]
---

# yuxin-platform-router

渔芯多平台发布路由器。根据内容类型、平台特性、凭证状态，自动选择最佳发布通道。

## 适用场景

- 同一篇内容需要发到多平台（公众号+抖音+知乎+B站+小红书）
- 不同平台用不同发布方式（API/浏览器自动化/人工）
- 凭证未配置时自动降级到「飞书审核 + 人工发」

## 工作流（4 步）

### Step 1: 接收发布请求
```python
{
  "content_id": "wechat_20260729_xxx",
  "title": "...",
  "platforms": ["wechat", "douyin", "zhihu", "bilibili", "xiaohongshu"],
  "content_body": "...",
  "media_paths": [...]
}
```

### Step 2: 平台特性路由表

| 内容类型 | 主推平台 | 协同平台 | 备注 |
|----------|----------|----------|------|
| 行业深度长文 | 公众号 | 知乎 | 知乎是搜索引擎入口 |
| 短视频脚本 | 抖音 | 视频号 | 同源分发 |
| 工程实录 | B站 | 抖音 | B站长尾 + 抖音爆发 |
| 图文种草 | 小红书 | 公众号 | 小红书决策入口 |
| 热点新闻 | 公众号 | 知乎 + 抖音 | 全部上 |

### Step 3: 凭证/通道决策

调用 `content_publisher.list_platforms()`：
- 凭证就绪 → 走真实 API（V2 接入）
- 凭证缺失 → 走 DRY-RUN（写入 `published/` + 飞书审核）

```
平台 → 通道决策
├─ wechat:   DRY-RUN (无凭证)
├─ douyin:   DRY-RUN (无凭证)
├─ zhihu:    DRY-RUN (无凭证)
├─ bilibili: DRY-RUN (无凭证)
└─ xiaohongshu: BROWSER_AUTOMATION (官方无 API)
```

### Step 4: 执行发布
```python
from content_publisher import publish_batch

drafts = []
for platform in platforms:
    drafts.append({
        "platform": platform,
        "title": title,
        "content": content_body,
        "media_paths": media_paths,
    })

result = publish_batch(drafts=drafts, dry_run=False)
# 自动判断：哪些平台凭证就绪走 API，哪些走 DRY-RUN
```

## 关键参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| dry_run | False | False=自动判断凭证 |
| schedule_time | None | 定时发布（V2） |
| fail_strategy | "feishu_review" | 失败时降级到飞书 |

## 多平台协同策略

- **同源不同形**：公众号长文 + 抖音短视频 + 知乎回答 = 同一素材 3 形态
- **时间错峰**：公众号 8:00 发，抖音 12:00 发，知乎 20:00 发（覆盖全天）
- **互相引流**：公众号底部放"抖音号"，抖音视频里说"详细方案见公众号"

## 失败模式

| 现象 | 解决 |
|------|------|
| 全部平台失败 | 检查网络/凭证，日志写 logs/ |
| 单平台失败 | 其他平台继续，该平台写待重试队列 |
| 内容超平台限制 | 自动截断 + 提醒 |

## 相关 Skills

- `yuxin-content-factory` — 上游
- `yuxin-compliance-checker` — 发布前必调
