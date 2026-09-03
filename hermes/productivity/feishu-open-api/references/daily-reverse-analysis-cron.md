# Daily reverse-analysis cron pattern (recorded 2026-06-11)

The 8 AM daily "爆款 reverse analysis" cron flow, first run 2026-06-11. Drawn
from the `feishu-bot-push` skill.

## Task structure

```
8:00 cron
  → 抓取 (头条 + 搜狗, 5-8 关键词)
  → 去重 + 4 维度分析
  → 选 3-5 个爆款选题
  → 入 RAG (category="搜索抓取")
  → 推飞书 home channel
  → 失败 → pending 文件降级
```

## File path conventions (老大的桌面)

- 抓取原始: `C:\Users\Administrator\Desktop\知识库\搜索抓取\YYYYMMDD_HHMMSS_<关键词串联>.md`
- 报告输出: `C:\Users\Administrator\Desktop\知识库\daily\YYYY-MM-DD-爆款分析V2.md`
- 推送脚本: `C:\Users\Administrator\Desktop\知识库\feishu_push_bakiku_v2.py`
- 失败备查: `C:\Users\Administrator\Desktop\知识库\feishu_rag_pending.txt`

## 4-dimension analysis framework (老大 required)

| Dimension | Content | Boss requirement |
|---|---|---|
| 标题公式 | 反常识/悬念/数字反差/大厨背书, each with 3 examples | Must split into 4 categories, ≥3 examples each |
| 钩子句 | 开头黄金 3 句 (xxx 就错了/看似简单/老渔民教你) | Must use fixed sentence patterns as examples |
| 选题打分 | Pick 3-5 highest viral potential from today's titles | Must give ⭐⭐⭐⭐⭐ star rating |
| 避坑提示 | Common mistakes 小白会犯 | List 5+ concrete traps |

## 4 维度上报节选示范

```
## 📊 4 维度分析

### 维度 1: 标题公式
- 反常识: "这鱼吃了 30 年才知道, 原来内脏才是宝"
- 悬念: "渔民从不告诉你的 3 个挑鱼秘密"
- 数字反差: "10 块钱的虾 vs 100 块钱的虾, 区别就在这 1 步"
- 大厨背书: "米其林大厨: 我做虾 30 年, 只用这一招"

### 维度 2: 钩子句
- "看似简单的白灼虾, 90% 人都做错了这一步"
- "老渔民教你: 这 3 种虾绝对不能买"
- "家里有娃的注意, 这 5 种海鲜孩子吃了聪明"

### 维度 3: 选题打分 (从今日抓的标题里挑 3-5 个)
- ⭐⭐⭐⭐⭐: "工厂化循环水养虾的真实成本曝光" (数字反差+争议)
- ⭐⭐⭐⭐: "对虾黑脚病高发期, 老养殖户这样防" (痛点+权威)
- ⭐⭐⭐: "这 4 种虾千万别买, 商贩自己都不吃" (避坑+实用)

### 维度 4: 避坑提示
- ❌ 死虾冰冻后看不出, 闻起来有氨味立即扔
- ❌ 虾头发黑=不新鲜, 千万别贪便宜
- ❌ 活虾买回来直接下锅? 错! 先养 30 分钟
- ❌ 虾线不挑? 泥腥味全在里头
- ❌ 冷冻虾解冻用热水? 肉质全毁
```

## Failure degradation (关键)

When 飞书 push returns `230002` (bot not in chat) or any HTTP error:

- ❌ **不要** stop and报错
- ✅ **必须** write full content to `feishu_rag_pending.txt` and continue
- 老大起床后手动复制粘贴，不会丢数据

See `feishu-bot-push` SKILL.md (archived) for the implementation pattern.
