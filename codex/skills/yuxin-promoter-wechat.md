---
name: yuxin-promoter-wechat
description: "渔芯科技 微信公众号推广文生成 — 1500-3000 字长文，小宝风格 + 豆包封面。触发：华哥说「公众号」「长文」「深度文」时调用。"
license: MIT
metadata:
  category: content
  priority: P0
  platforms: [wechat]
  depends_on: [rkr-deep-query, platform-router]
---

# yuxin-promoter-wechat

渔芯科技微信公众号推广文生成器。基于 RKR 知识库 + 飞书历史审核数据 + 豆包生图 Prompt 库，自动产出可直接发布的 1500-3000 字深度长文。

## 适用场景

- 渔芯科技新业务（RAS 设备/AI Agent/行业洞察）需要一篇深度科普文引流
- 某个行业话题火了（补贴/政策/技术），需要蹭热度 + 沉淀到公众号
- 周更稳定产出，保持公众号活跃度（V2 接入定时）

## 工作流（7 步）

### Step 1: 接收选题
- 输入：`topic`（必填）、`keywords`（可选）、`style`（默认"小宝风"）
- 来源：
  - 华哥直接指定（飞书 DM）
  - cron 自动从 `topic_candidates.jsonl` 抽取 P0/P1 候选
  - 热点驱动（V2 接入热搜 API）

### Step 2: RKR 知识库调研
调用 `rkr_reader.search()` 查询相关素材：
```python
from rkr_reader import search
results = search(query=topic, n_results=8, collection="ras")
# 取前 3 条高分素材，整理事实/数据/案例
```

### Step 3: 套用小宝风格模板
6 段式结构（1500-3000 字）：
1. 开头（80 字）— 故事化钩子：某老板/某场景/某真实痛点
2. 第一段（200 字）— 反常识/数据冲击
3. 第二段（400 字）— 深度解释（引用 RKR 素材）
4. 第三段（500 字）— 渔芯怎么解决（产品植入）
5. 第四段（200 字）— 行动召唤（扫码/咨询/下载）
6. 结尾（80 字）— 金句收尾

### Step 4: 配图 prompt 生成
输出 3 张图的豆包 prompt：
- 封面图：主题关键词 + 风格（默认"未来感+数据可视化"）
- 内容配图 1：核心概念示意
- 渔芯产品/案例图

保存到 `prompts/wechat_<topic>_<date>.txt`，调用 `doubao-image-gen` skill 生成。

### Step 5: 合规检查
调用 `compliance_checker` 校验：
- 无绝对化用语（《广告法》第 9 条）
- 数据可追溯
- 渔芯产品名出现次数 ≤ 3
- 无敏感词

### Step 6: 输出成稿
保存到 `output/wechat_YYYY-MM-DD_<topic>.md`：

```markdown
# 标题（不超过 28 字，不超过 64 字更好）

**原创 渔芯科技 | YYYY-MM-DD**

---

[正文 6 段式结构]

---

## 📞 联系渔芯

- 官网：https://yuxin-tech.com
- 微信：yuxin_keji
- 电话：400-xxx-xxxx

---

**配图清单**：
1. 封面图：output/wechat_<topic>_cover.png
2. 内容配图：output/wechat_<topic>_fig1.png
3. 渔芯案例：output/wechat_<topic>_fig2.png
```

### Step 7: 推送飞书审核
调用 `feishu_content_bridge.send_draft()`：
```python
from feishu_content_bridge import send_draft
send_draft(draft_path="output/wechat_2026-07-29_MCP.md", platform="公众号")
```

## 关键参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| 字数 | 2000 | 软下限 1500，上限 3000 |
| 风格 | 小宝风 | 故事+数据+反常识 |
| 配图 | 3 张 | 封面+卡片+产品 |
| RKR 引用 | 2-3 条 | 避免堆砌 |
| 渔芯产品植入 | 2 处 | 自然不硬广 |
| CTA | 1 个 | 行动召唤清晰 |

## 验收清单

- [ ] 标题吸引力测试（3 秒内能说出"为什么我要点"）
- [ ] RKR 引用准确（无张冠李戴）
- [ ] 配图全部生成成功
- [ ] 渔芯产品名出现次数 ≤ 3
- [ ] 无绝对化用语（《广告法》第 9 条）
- [ ] CTA 清晰
- [ ] 飞书推送成功（msg_id 记录）

## 失败模式 & 规避

| 现象 | 解决 |
|------|------|
| 选题太专业 | 退回 Step 1，换更通用的关键词 |
| RKR 无相关素材 | 用 `add_topic_candidate` 加入素材请求 |
| 配图生成失败 | 用 `prompts/wechat_cover_fallback.txt` |
| 风格不像小宝 | 加载 `references/xiaobao_style_guide.md` |
| 飞书推送失败 | 落本地 + 写 `logs/publish_error.log` |

## 相关 Skills

- `yuxin-promoter-douyin` — 抖音版（同主题另一形态）
- `yuxin-promoter-zhihu` — 知乎版（深度回答）
- `yuxin-promoter-bilibili` — B站版
- `yuxin-promoter-xiaohongshu` — 小红书版
- `yuxin-rkr-deep-query` — 知识库查询
- `yuxin-platform-router` — 平台路由
- `yuxin-compliance-checker` — 合规审核
