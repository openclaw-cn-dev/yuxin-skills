---
name: ***SECRET***
description: '老莫 cron 论文检索的 OpenAlex 查询策略包 — STRICT/宽泛 双词表过滤、批量查询、DOI 去重、Crossref 二次验证、publication_date 排序技巧、Zenodo/Figshare 假论文辨别。触发条件: 老莫 cron 启用论文检索;运行 OpenAlex/Semantic Scholar/Crossref API 检索 AI×水产养殖相关论文;需要 recall 检索策略词表;已知 DOI 去重需求。'
license: MIT
metadata:
  author: 渔芯科技
  version: "1.4.0"
  parent_skill: laomo-knowledge (default profile)
  changelog: |
    v1.4.0 (2026-09-01 R50)
      - 已知陷阱表新增 1 条:R50 `ai` 子串误命中实证(STRICT_DUAL 23 候选中 60%+ 是 ai 噪声)
      - 警告:`"ai"` 不能作为宽泛 AI 关键词,必须用 STRICT_AI 词表(16 词)或 word boundary `\bai\b`
      - R50 阶段 5 饱和收尾确认(R49+R50 连续 2 轮跨方向 0 净增 → 主动收尾)
    v1.3.0 (2026-09-01 R49)
      - 新增 references/***SECRET***.md
      - 已知陷阱表新增 3 条:Figshare Collection 单信号 DUP、阶段 5 12 查询退出门槛、`[NOT_STORED]` 漂移误报识别
      - 与 §3.1.3 双信号 DUP 形成快速判定 + 完整判定双轨
      - 与 §3.5.4 阶段 5 决策树形成更激进的「12 查询主动收尾」门槛
    v1.2.0 (2026-08-31 R42)
      - 新增 references/***SECRET***.md (R42 cites: filter 必须用 OpenAlex ID 而非 DOI)
      - 已知陷阱表新增 4 条：cites:DOI 报 HTTP 400、math model 误命中、凌晨窗口反例、引用追踪 seed 入库契约
      - 验证流程新增"引用追踪标准序列"子节（4 步：DOI → OpenAlex ID → cites: filter → STRICT 过滤）
      - 配套 reference 文件指针更新
    v1.1.0 (2026-08-31 R41)
      - 新增 references/openalex-budget-exhaustion.md (R41 OpenAlex 全 API budget 耗尽应对 SOP)
      - 已知陷阱表新增 3 条：OpenAlex budget 全耗尽、R40 范式失效、Crossref search 命中率 0%
      - 验证流程新增"失败兜底流程"和"[NOT_STORED] 漂移校验协议"子节
      - 配套 reference 文件指针更新
---

# OpenAlex × 水产养殖论文检索策略

> 老莫 cron 论文检索核心策略包。从 laomo-knowledge §3.5 提取为可独立调用的工具包。
> 配合 `laomo-knowledge` 主 skill 使用。

## 快速开始

```bash
# 默认严格双条件检索 (R20+ 推荐)
python3 /Users/hua/.hermes/skills/***SECRET***/scripts/strict_filter.py \
  "machine learning aquaculture water quality" \
  "deep learning fish disease detection"
```

## 词表版本

### STRICT_AI (16 词) — 仅 ML/DL 明确方法名
```python
STRICT_AI = [
    "machine learning", "deep learning", "neural network", "random forest",
    "xgboost", "yolo", "transformer", "lstm", "cnn", "rnn", "gru",
    "computer vision", "reinforcement learning", "svm", "gradient boosting",
    "anomaly detection", "object detection", "segmentation",
]
```

### STRICT_AQUA (14 词) — RAS+海淡水主要养殖种
```python
STRICT_AQUA = [
    "aquaculture", "recirculating", "tilapia", "salmon",
    "catfish", "trout", "carp", "shrimp", "prawn",
    "sea bass", "seabream", "macrobrachium",
    "hatchery", "biofilter",
]
```

### 宽泛 AI_KEYWORDS (14 词,含 model/prediction/sensor)
仅在 STRICT precision 低时启用 (经验:宽泛 precision 通常 <50%)。

## 已知陷阱

| 陷阱 | 模式 | 应对 |
|---|---|---|
| **宽泛过滤污染** | `model`/`prediction`/`modeling` 命中非 ML 论文 | 用 STRICT_AI 替代 |
| **`water quality` 通用词霸榜** | OpenAlex top 5 全是植物病害/遥感水质 | 加 `+ aquaculture` 限定 + STRICT 词表 |
| **`RAS` 缩写污染** | 癌症 RAS 基因/工业 RAS 霸榜 | 用 `recirculating aquaculture system` 全称 |
| **`RAS + aquaculture` 双词** | 经常混入污水处理/数字孪生非水产 | 后过滤层做 aqua+AI 双条件 |
| **`precision feeding` 通用词** | 精准农业/食品工程污染 | 改用 `uneaten feed detection` / `FCR prediction` |
| **Zenodo 假论文** | 占位符作者 + 空 description | §3.1 Zenodo 4 步鉴别法 |
| **Figshare DUP** | `type=other` + 与主论文作者完全一致 | §3.1.3 Figshare 2 强信号 |
| **OpenAlex 503** | "Search cluster recovers from heavy load" | §3.5.11 SOP: 等待 60-90s 重试,503 ≠ 400 ≠ 429 |
| **OpenAlex 400 (filter)** | `filter=publication_year:2024,2025,2026` 错误 | 用 `2024-2026` 范围或 `2024|2025|2026` pipe |
| **OpenAlex publication_date 排序霸榜** | top 5 全是最新 CS 通用论文 | 改用 `sort=relevance_score:desc` |
| **🆕 OpenAlex budget 全耗尽** | `/works?per_page=1` 都返回 429 + `dailyRemainingUsd: 0` | **所有 endpoint 共享 budget pool**——DOI 直查/cites filter 同样 429。详见 `references/openalex-budget-exhaustion.md` |
| **🆕 R40 范式失效** | DOI 直查 + cites: filter 双策略在 budget 耗尽日完全失效 | Crossref `/works/<doi>/reference` 引用追踪兜底（仅拿老论文）|
| **🆕 Crossref search 命中率 0%** | "fish detection deep learning" 返回 PLOS ONE/Kannada/印度农业 | 不推荐为唯一兜底路径，优先引用追踪 |
| **🆕 R42 cites:DOI 报 HTTP 400** | `filter=cites:10.xxxx/yyyy` 直接报 `"is not a valid OpenAlex ID"` | **必须先用 `GET /works/doi:<DOI>` 拿 OpenAlex ID `W...`，再 `filter=cites:W<id>`**。详见 `references/***SECRET***.md` |
| **🆕 R42 数学模型误命中** | `biofilter AI RAS` 命中 `10.64252/ggbzq739` delay differential equation 数学模型（非 ML/AI）| 升级 STRICT_AI 词表：必须命中 `deep learning`/`neural`/`xgboost`/`yolo`/`lstm`/`random forest` 等**强 AI 方法名**；`model`/`prediction`/`monitoring` 单关键词不足 |
| **🆕 R42 凌晨窗口反例** | R32 验证 00:00-06:00 UTC 100% 限流率 → R42 04:04 UTC 7 查询全 200 OK | 凌晨窗口是 cluster 状态随机变量，不应硬性避开；cron 启动先 probe 再决定，不主动切 arXiv 兜底 |
| **🆕 R42 引用追踪 seed 必须入库** | cites: filter 引用的种子论文若不在 known_dois.txt，漂移校验会报"假漂移" | 引用追踪 seed 在本轮进化报告内必须 `cat >> known_dois.txt` 写入（即使 seed 早已是 P0/P1 论文）|
| **🆕 R49 Figshare Collection 单信号 DUP** | DOI `10.6084/m9.figshare.c.*.v\d+` 模式 + OpenAlex `type=other` 即可 100% 判定 DUP | 单信号快速判定，无需 Crossref / Figshare API 二次验证。详见 `references/***SECRET***.md §1` |
| **🆕 R49 阶段 5 12 查询主动收尾** | 跨 4 方向 × 3 关键词 = 12 查询 0 净增 → 立即主动收尾（不必等 2 轮连击）| §3.5.4 阶段 5 决策树的更激进版本。R49 实证 cron 时间节省 30-50%。详见 `references/***SECRET***.md §2` |
| **🆕 R49 `[NOT_STORED]` 漂移误报** | 报告 `❌ FILTER 误命中识别` 表格里的 DOI 被漂移校验脚本误判为新增 | 误命中表格标题统一改用 `[NOT_STORED]` 标记 + Python regex 过滤该标记。详见 `references/***SECRET***.md §3` |
| **🆕 R50 `ai` 子串误命中** | 把 `"ai"` 加入 AI_KEYWORDS 触发大量 `available`/`maintain`/`criteria`/`said`/`pair` 等英文词命中，"纯形态学论文"误入 P0 候选 | **永远不要把 `"ai"` 作为宽泛 AI 关键词**——必须用 word boundary `\bai\b` 或 STRICT_AI 词表（16 词）替代。R50 实证 STRICT_DUAL 过滤 23 个候选中 60%+ 是 `ai` 子串噪声 |

## 验证流程

1. OpenAlex 检索 (本文档脚本)
2. DOI 去重 vs `/Users/hua/.hermes/profiles/laomo/evolution/known_dois.txt`
3. 双条件 STRICT_AI × STRICT_AQUA AND 判定
4. Crossref API 验证:`https://api.crossref.org/works/<DOI>` → 200 OK ✅
5. 重建 OpenAlex 倒排索引摘要 或 DOI redirect HTML 拿摘要
6. Zenodo/Figshare 假论文鉴别 (按 DOI 前缀)
7. 写入 known_dois.txt (按 §3.6 "Write file FIRST, then report" 协议)

### 🆕 失败兜底流程（OpenAlex budget 全耗尽时）

详见 `references/openalex-budget-exhaustion.md`：

1. **探测 `/works?per_page=1`**（5 秒）—— 200 OK 走主路径，429 进入兜底
2. **等待 + 重探**（最多 4 分钟）—— retryAfter > 1800s 直接进兜底
3. **Crossref 兜底三层**：
   - **3a. 引用追踪**（`Crossref /works/<doi>/reference`）—— 拿已知命中论文的 references 做 STRICT 过滤，R41 验证 12/12 真实验证
   - **3b. Crossref search**（命中率 <10%，不推荐唯一兜底）—— "fish" 等通用词去歧义不足
   - **3c. 主动收尾**（推荐）—— 候选不达"2026 新论文"门槛时，按 §3.5.4 阶段 5 标记 [NOT_STORED]

### 🆕 `[NOT_STORED]` 漂移校验协议（R41 实战）

当候选 DOI 不写入 known_dois.txt 时，**报告中必须用 `[NOT_STORED]` 标记每条 DOI**，让漂移校验脚本识别：

```markdown
[NOT_STORED] 10.1016/j.eswa.2023.122194  FishTrack: ... (2024)
```

漂移校验脚本（参见 `references/known_dois_protocol.md` §"报告自洽校验"）：
- 报告中 `[NOT_STORED]` 行的 DOI → **不计入漂移**
- 报告中声称"已入库"的 DOI 不在 known_dois.txt → **计入漂移**

## 配套

- `scripts/strict_filter.py` — 主要 STRICT 双条件过滤脚本
- `references/r20_strict_filter_evidence.md` — R20 实证对比数据
- `references/known_dois_protocol.md` — known_dois.txt 写入契约 (§3.6)
- `references/openalex-budget-exhaustion.md` — R41 OpenAlex 全 API budget 耗尽应对 SOP
- `references/***SECRET***.md` — 🆕 R42 cites: filter 必须用 OpenAlex ID 而非 DOI
- `references/***SECRET***.md` — 🆕 R49 Figshare Collection 单信号 DUP + 阶段 5 12 查询退出门槛 + `[NOT_STORED]` 漂移误报识别

## 🆕 引用追踪标准序列（R42 沉淀，4 步）

cites: filter 是 R40-R42 阶段最稳定的引用追踪方法，但**必须严格按 4 步执行**：

```python
# 步骤1：从已知 P0 seed 论文的 DOI 拿 OpenAlex ID
import urllib.request, urllib.parse, json

SEED_DOI = "10.1016/j.aaf.2022.06.003"  # R33 P0 RAS Review 综述种子
url = f"https://api.openalex.org/works/doi:{urllib.parse.quote(SEED_DOI)}"
data = json.loads(urllib.request.urlopen(url, timeout=20).read())
oa_id = data["id"]  # 形如 "https://openalex.org/W4285045616"

# 步骤2：用 OpenAlex ID (W...) 而非 DOI 做 cites: filter
url = f"https://api.openalex.org/works?filter=cites:{oa_id}&sort=publication_date:desc&per_page=10"
data = json.loads(urllib.request.urlopen(url, timeout=20).read())

# 步骤3：拿候选 DOI + STRICT 双条件过滤
candidates = []
for w in data.get("results", []):
    doi = (w.get("doi") or "").replace("https://doi.org/", "")
    # STRICT_AI × STRICT_AQUA AND 判定（参考 scripts/strict_filter.py）
    if is_relevant_strict(w):  # aqua+ai 双条件
        candidates.append({"doi": doi, "title": w["title"], "fwci": w.get("fwci"), "cited": w.get("cited_by_count")})

# 步骤4：Crossref 验证 + known_dois.txt 去重 + 写入
known = load_known_dois()
fresh = [c for c in candidates if c["doi"] not in known]
# fresh 走 Crossref 200 OK + 摘要重建 + 写入 known_dois.txt 流程
```

### ❌ R42 失败的错误写法（触发 HTTP 400）

```python
# ❌ 用 DOI 直接做 cites: filter（HTTP 400）
url = f"https://api.openalex.org/works?filter=cites:{SEED_DOI}"
# {"error":"Invalid query parameters error.",
#  "message":"'10.1016/j.aaf.2022.06.003' is not a valid OpenAlex ID."}
```

### ✅ 关键约束

- `cites:` 后必须是 OpenAlex ID（形如 `https://openalex.org/W4285045616` 或简写 `W4285045616`）
- DOI 前缀 `10.xxxx/yyyy` **不是 OpenAlex ID**，必须先 `GET /works/doi:<DOI>` 转换
- 与 `cites:` 同类的 filter（如 `cited_by:`）也需 OpenAlex ID

### 引用追踪 seed 入库契约（漂移校验）

如果本轮进化报告引用了某 seed 论文做 cites: filter 追踪（即使 seed 早已是 R33/R40 P0），**该 seed 的 DOI 必须在当轮 known_dois.txt 中**：

- R42 实测：报告引用 `10.1016/j.aaf.2022.06.003`（R33 P0 seed），但 known_dois.txt 缺失 → 漂移校验误报
- 修复：发现 seed 不在 known_dois.txt 时，立即 `cat >> known_dois.txt` 写入
- 漂移校验脚本（Python regex for backticks）会识别 report 引用的所有 DOI 并与 known_dois.txt 对比
