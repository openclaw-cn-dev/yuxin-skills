---
name: a-share-screener
description: Use when boss asks to screen Chinese A-share stocks by technical patterns — 涨停板 / 异动 / 倍量 / 上升趋势 / 长上影线 / 突破量价齐升 / 横盘 / 板块过滤 / 财务过滤. Builds multi-threaded akshare-based screeners, handles akshare provider quirks, outputs CSV+Markdown, optionally cron-izes for daily 18:00 post-close runs. **Also covers downstream** — P&L analysis (开盘价买入 → 收盘价卖出)、ETF 主题配对、公司基本面查询、长线持仓跟踪、3 维度全中 + 严格过滤 (破前高 + 量价齐升). Triggers on "选股", "涨停", "异动", "倍量", "上影线", "上升趋势", "A股筛选", "A 股选股", "stock picker", "强势股", "长上影线", "技术选股", "ETF 配对", "盈亏分析", "每股 100 股 1000 元", "同时满足", "严格", "要满足所有".
version: 2.1.0
author: Hermes Agent (小弟)
license: MIT
metadata:
  hermes:
    tags: [akshare, stock-screener, a-share, chinese-stocks, technical-analysis, finance, etf, pnl, strict-filter]
    related_skills: [python-windows-path-pitfalls, daily-cron-architecture]
---

# A 股选股 (A-Share Stock Screener) v2.1

## Overview

End-to-end workflow for China A-share stock screening using `akshare` (free, no API key). v2.1 expands from "just pick stocks" to the **full boss workflow**:

1. **3+ dimension technical screen** (涨停+异动+倍量 / 上升趋势 / 放量长上影线)
2. **P&L analysis** (老大花 1000 元/只 或 100 股/只 → 当日盈亏 + 扣手续费)
3. **ETF matching** (把命中的个股映射到对应主题 ETF，1 股就能买)
4. **Company fundamentals** (行业、主营、概念、市值、PE)
5. **Long-term position tracking** (持仓 CSV + 每日 cron 推送)
6. **3 维度全中 + 严格过滤** (破前高 + 量价齐升 — 老板高频变体) [v2.1 新增]

Built and verified 2026-06-12:
- 沪市 2314 只 / 3 维度 → 4'44" (15 线程, 0 失败)
- 全 A 5527 只 / 3 维度 → **10'17"** (6 线程 + 限速, 0 失败) — 102 只 3 维度全中
- **3 维度全中 + 严格过滤** → 58 只 (破前高 + 量/MA20>1.0) → 48 只 (再上影>5%) [v2.1]
- 14 只最强候选 6/11 实战分析 → 赢率 30%，赔率 2.16 倍
- 588010 科创新材料 ETF 5 天走势 → +1.86% / +2.82% / +4.96% 各种场景

## When to Use

Activate when boss says any of:
- **选股类**: "选几只票" / "选股" / "筛股" / "强势股" / "妖股"
- **技术形态**: "涨停" "异动" "倍量" "上升趋势" "长上影" "突破前高" "横盘" "MA5>MA30"
- **量化分析**: "上影线越长越好" / "上影线前 50" / "放量" / "3 个维度综合"
- **严格过滤**: "要同时满足以上全部条件" / "量必须比前面高才行" / "破前高才算"
- **盈亏分析**: "花 1000 元买" / "买 100 股" / "我的盈亏" / "9:30 买入" / "开盘价"
- **ETF 配对**: "最强候选的 ETF" / "主题 ETF" / "588010" / "板块 ETF"
- **基本面**: "是什么概念" / "主营业务" / "行业" / "市值" / "PE"
- **持仓跟踪**: "长线持有" / "我的持仓" / "跟踪" / "建仓"

**Don't use for**: US stocks (yfinance), Hong Kong (akshare 有限), 纯基本面 (本 skill 技术形态为主; 可扩展 PE/ROE), 期权/衍生品

## The 6-Step Boss Workflow

```
Step 1 选股     → Step 2 盈亏分析   → Step 3 ETF 配对 → Step 4 基本面 → Step 5 持仓跟踪 → Step 6 严格过滤
   3 维度       1000 元/只 or 100 股/只    主题匹配        行业+主营      CSV + cron       破前高 + 量齐
   5527 只      扣印花税+佣金+过户费       1507 ETF 池     东方财富 API   每日 21:00       58 只 from 102
```

每步独立但串联：选股结果（`选股结果汇总.csv`）是后续所有步骤的输入。

**Step 6 (严格过滤)** 详见 `references/strict-3d-filter.md`：
- 老板高频要求 "**要同时满足**" → 3 维度 set 交集
- 老板高频要求 "**量必须 > 前面**" → 破前高 + 量/MA20 > 1.0
- 实战 5 个 Python 坑（dim int vs str、code zfill、set 交集、iloc[0] 检查等）

## Related Files

- `references/dimensions.md` — 6 个维度算法详解 (V1)
- `references/quant-analysis.md` — **盈亏分析 + ETF 配对 + 持仓跟踪** (V2 新增)
- `references/akshare-provider-quirks.md` — **7 个坑 + mini_racer crash 修复** (V2 新增)
- `references/akshare-2026-api-quickref.md` — **akshare 各接口反爬降级链 + 东方财富 PageAjax 替代方案** (合并自 finance/akshare-ashare-stock-screener)
- `references/risk-scoring-and-company-research.md` — **风险评分公式 + 持仓交叉验证 + 加严筛选 + 中国公司研究 4 件套 + 求职类任务模板** (合并自 finance/akshare-ashare-stock-screener)
- `references/strict-3d-filter.md` — **3 维度全中 + 严格过滤（破前高 + 量价齐升）+ 5 个 Python 坑** (V2.1 实战追加)
- `templates/stock_picker.py` — 沪市 v1 (15 线程，4'44")
- `templates/stock_picker_v2.py` — **全 A v2 (6 线程 + 限速，10'17")** (V2 新增) — 两版合并自 finance/akshare-ashare-stock-screener
- `templates/pnl_analyzer.py` — **盈亏分析** (1000 元/只 vs 100 股/只 vs ETF) (V2 新增)
- `templates/etf_matcher.py` — **ETF 主题配对** (V2 新增)