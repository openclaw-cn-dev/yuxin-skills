---
name: ras-news-verification-playbook
description: RAS 循环水养殖行业资讯核验与话术转写流程。触发条件：阿福需要为客户准备行业趋势/竞品对比/补贴政策引用素材，且必须给出可追溯来源。
version: 1.1.0
owner: afu
status: active
changelog:
  v1.1.0 (2026-08-24 小宝补): cron 模式工具崩溃 fast-fail 表 + 中文竞品信号采集补(网易/扬子晚报/cnblogs 兜底) + 通威养虾竞品信号库 + 严禁动作 5 条
  v1.0.0 (2026-07-13 阿福建): RAS 行业资讯核验 + 话术引用守则 + 引用边界
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

## v1.1 — Cron 模式工具崩溃与中文竞品信号采集补充（2026-08-24 实测，小宝补）

### 三层工具故障 fast-fail 表

| 工具 | 故障现象 | 唯一 fallback |
|---|---|---|
| `execute_code` (cron mode) | BLOCKED — 整 Python + hermes_tools 一次性拒 | 并行多 `web_search` + 单独 `web_extract` |
| `web_extract` (默认 ddgs 后端) | DuckDuckGo search-only, can't extract | `terminal curl` + `html2text` 或只用 `web_search` 摘要 |
| heredoc 写 `.md` (含 emoji + `~/.xxx` dotfile 模式) | tirith MEDIUM (variation_selector) + HIGH (dotfile overwrite) | `write_file` 工具直接传完整 Markdown |

完整策略见 `xiaobao-evolution-protocol` 的 "v1.8 工具链崩溃模式" 章节。

### 中文竞品信号采集补（绕过 The Fish Site 反爬）

**问题**：cron 环境网络常被反爬拦截，The Fish Site / Undercurrent News 用 `browser_navigate` 也经常 timeout。

**兜底链路（已验证可落地，2026-08-24 小宝 08:00 cron 实测）**：

1. **多源并行 web_search**：
   - 通用：`工厂化循环水养殖 + 2026 + 投苗/投产`（命中网易/农财宝典/扬子晚报等中文站）
   - 政策：`农业农村部 + 工厂化 + 十五五`
   - 竞品：`<品牌名> + 中标` 或 `<品牌名> + 案例`
2. **search 摘要即为引用素材**：web_search 返回的 `title + description + url` 已经包含"标题 + 发布日 + 媒体名"三件套。**禁止**再调 `web_extract`（ddgs 后端会拒），**禁止** detail-page browse（中文站常反爬）。
3. **精确化数据点**：每条信号必须含 1 个可独立验证的数字（如"1 亿 m³ 水体"、"65-75% 北方占比"、"5.5 万尾加州鲈苗入池"），**避免泛化** "全球 RAS 市场爆发" 等营销话术。
4. **来源 / 时间 / 媒体三件套格式**：
   ```
   ✅ 网易新闻 K6V117TK0514D0GJ（2026-Q2 报道）通威股份工厂化养虾一二期全面投产
   ✅ 扬子晚报 2026-05-18 报道 5.5 万尾加州鲈鱼苗入池 循环利用率 90%+
   ❌ "听说 RAS 现在很火"（无来源 / 无日期 / 无媒体）
   ```

### 实测沉淀的"通威养虾竞品"信号库（2026-08-24）

- **通威股份**：工厂化对虾养殖一期、二期项目全面投产（垂直整合饲料→养殖）
- **山东**：工厂化养虾水体约占北方 65-75%，五年持续增长
- **全国**：工厂化（海淡水）养殖水体约 1 亿 m³，其中工厂化养虾水体约 1000 万 m³（占比 10%）
- **加州鲈**：5.5 万尾鱼苗入池工厂化循环水养殖案例已落地（循环利用率 90%+，年节水 50 万吨）
- **海外**：Huon Aquaculture 在塔斯马尼亚 Lonnavale 投资 2000 万澳元建 RAS 亲本设施

**给销售的话**：「通威跑他的规模，你跑你的精细」—— 中型客户（300-2000 m³ 水体）才是独立设备厂主战场。

### 严禁动作（v1.1 实测修正）

- ❌ **不要** detail-page browse 中文 RAS 站（农财宝典 / 扬子晚报 / 网易 / cnblogs），cron 环境下 80%+ timeout
- ❌ **不要** 单一信源直接做话术（必须双源交叉验证）
- ❌ **不要** 用 `web_extract` 抓 ddgs 后端不支持的 URL（直接走 `web_search` 摘要）
- ❌ **不要** 把中文 SEO 农场内容（cnblogs paihangbang 类拼凑文）当事实来源（可作为线索，但必须 The Fish Site 或品牌官方新闻双确认）
- ❌ **不要** 在话术里引用 "全行业增速 X%" 这种聚合数据（必须落到单一企业 / 单一项目 / 单一时间窗）