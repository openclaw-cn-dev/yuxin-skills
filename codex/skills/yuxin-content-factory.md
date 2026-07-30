---
name: yuxin-content-factory
description: "渔芯内容工厂总入口 — 编排 5 步流程（选题→创作→审核→发布→反馈）。触发：cron 每日 9:00、手动触发、华哥说「跑一遍工厂」时调用。"
license: MIT
metadata:
  category: factory
  priority: P0
  depends_on: [ras-topic-miner, promoter-*, compliance-checker, platform-router, feishu-content-bridge]
---

# yuxin-content-factory

渔芯内容工厂总入口。编排 5 步流程，**一键产出每日公众号+抖音+知乎+B站+小红书全套内容**。

## 适用场景

- cron 每日 9:00 自动跑（生成昨日选题的内容）
- 手动触发（华哥说"今天跑一遍工厂"）
- 跨项目复用（任何有 RKR 知识库的产品都可用）

## 5 步流程图

```
[Step 1 选题] ← yuxin-ras-topic-miner
   ↓ 输出：1-2 条今日选题 (drafts/today_pick.json)
[Step 2 创作] ← yuxin-promoter-{wechat,douyin,zhihu,bilibili,xiaohongshu}
   ↓ 输出：output/{platform}_{date}_{topic}.md
[Step 3 审核] ← yuxin-compliance-checker
   ↓ 输出：合规分 ≥ 90 才进入下一步
[Step 4 发布] ← yuxin-platform-router + content-publisher MCP
   ↓ 输出：published/* + 飞书审核
[Step 5 反馈] ← yuxin-engagement-tracker (V2)
   ↓ 输出：数据回流 RKR
```

## 工作流

### Step 1: 选题
```bash
python3 scripts/ras_topic_miner.py --count 2 --priority P0,P1
# 写入 drafts/today_pick.json
```

### Step 2: 创作
按平台分别生成：
- 公众号（2000 字长文） — `yuxin-promoter-wechat`
- 抖音（45s 脚本）— `yuxin-promoter-douyin`
- 知乎（1500 字回答）— `yuxin-promoter-zhihu`
- B站（动态/专栏）— `yuxin-promoter-bilibili`
- 小红书（300 字 + 9 图）— `yuxin-promoter-xiaohongshu`

V1 阶段：只跑公众号 + 抖音（最高 ROI）

### Step 3: 合规审核
```python
from yuxin_compliance_checker import check
for platform in ["wechat", "douyin"]:
    result = check(content=output[platform])
    if not result["passed"]:
        log(f"❌ {platform} 不合规: {result['issues']}")
        continue
```

### Step 4: 多平台发布
```python
from content_publisher import publish_batch

drafts = [
    {"platform": "wechat", "title": ..., "content": ...},
    {"platform": "douyin", "title": ..., "content": ...},
]
result = publish_batch(drafts=drafts)
# 自动判断凭证：DRY-RUN 或真实 API
```

### Step 5: 飞书推送审核
```python
from feishu_content_bridge import send_review_card

send_review_card(
    title="渔芯内容工厂 · YYYY-MM-DD 待审核",
    items=[
        {"platform": "公众号", "title": "...", "path": "output/wechat_..."},
        {"platform": "抖音", "title": "...", "path": "output/douyin_..."},
    ],
    summary="✅ 合规分 ≥ 90，已就绪发布",
)
```

## 关键参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| 选题数 | 2 | 不超载 |
| 平台范围 | 公众号+抖音 | V1，V2 加 知乎+B站+小红书 |
| 合规分阈值 | 90 | 低于此分打回 |
| 发布模式 | auto | auto=DRY-RUN + 飞书审核 |

## 输出清单

```
output/
├── wechat_2026-07-29_<topic>.md
├── douyin_2026-07-29_<topic>.md
├── (V2: zhihu_, bilibili_, xiaohongshu_)
└── (V2: 配图)

published/
├── pub_20260729_xxx_wechat.md  # DRY-RUN 占位
└── pub_20260729_xxx_douyin.md

logs/
├── factory_2026-07-29.log
└── publish_log.jsonl
```

## 一键运行

```bash
# 全自动跑一遍
bash scripts/run_factory.sh

# dry-run（只生成不推送）
bash scripts/run_factory.sh --dry-run

# 指定选题
bash scripts/run_factory.sh --topic "RAS 补贴新政"

# 指定平台
bash scripts/run_factory.sh --platforms wechat,douyin
```

## 失败模式

| 现象 | 解决 |
|------|------|
| 选题失败 | 用昨天的候选兜底 |
| 创作超时 | 单平台超时 5 分钟，标 fail |
| 合规不通过 | 标 fail 不推送，记入下次复盘 |
| 飞书推送失败 | 落本地 + 飞书失败日志 |

## 相关 Skills

- 全部 `yuxin-promoter-*` （5 个）
- 全部 `yuxin-research-*` （2 个）
- 全部 `yuxin-publish-*` （2 个）
- 全部 `yuxin-feedback-*` （2 个）
