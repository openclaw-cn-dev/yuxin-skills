---
name: ras-news-verification-playbook
description: RAS 循环水养殖行业资讯核验与话术转写流程。触发条件：阿福需要为客户准备行业趋势/竞品对比/补贴政策引用素材，且必须给出可追溯来源。
version: 1.0.0
owner: afu
status: active
---

# RAS 行业资讯核验与话术转写

## 触发条件
- 客户问“行业趋势/补贴/竞品/政策”
- 阿福准备“全球 RAS 爆发”之类宏观判断
- 需要为客户话术引用单一企业半年报或政策原文

## 标准流程

1. **优先核验单一来源**：`browser_navigate` The Fish Site（`https://thefishsite.com/search?query=recirculating%20aquaculture`）或 Undercurrent News；避开 Google/Bing/搜狗中文站（cron 环境常被反爬拦截）。
2. **中文资讯走本地库**：先查 `references/ras-industry-2026-july.md` 与 `~/.hermes/skills/aquaculture/ras-aquaculture/references/ras-industry-news-2026.md`；超 12 小时未更新再发起搜索。
3. **记录三件套**：文章标题、发布日期（精确到日）、URL；中文站再加发布机构。
4. **抽取 3 个关键点**：每个点必须可独立验证（数字、合同方、时间），避免泛化。
5. **客服话术改写**：把“全球爆发”改为“某家企业某季度某项业务增长”，并交代边界条件。
6. **写入**：本地 `references/ras-industry-YYYY-MM-DD.md`（日期用核验当日），并在末尾追加采集记录表。

## 话术引用守则

- ✅ “The Fish Site 2026-07-28 报道，BIO-UV 2026H1 营收 €20.1m，服务与售后部门同比 +10%”
- ❌ “全球 RAS 市场在爆发，现在不上车就晚了”
- ✅ “欧盟 2026 年初实施新版 RAS 环保标准要求废水零排放”（引用具体政策文件）
- ❌ “国家在大力支持 RAS”
- ✅ “广东省世行贷款项目工厂化循环水养殖设备补贴最高 70%”（引用江门市农业农村局 2026-07-13 文件）

## 引用边界

- 单一企业数据 ≠ 行业整体增速
- 政策文件必须标注发文机关与发布日期
- 引用前用“听起来/根据……报道/数据显示”等过渡词，避免直接断言
- 数据使用后必须说明口径与时间窗口

## 关联资源

- The Fish Site RAS 频道：`https://thefishsite.com/articles/...`
- 本地参考：`~/.hermes/profiles/afu/skills/productivity/afu-customer-service/references/ras-industry-2026-*.md`
- 共享参考：`~/.hermes/skills/afu-customer-service/references/ras-industry-2026-july.md`
- 行业新闻：`~/.hermes/skills/aquaculture/ras-aquaculture/references/ras-industry-news-2026.md`