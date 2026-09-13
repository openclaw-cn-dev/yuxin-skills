---
name: jtbd-phase3-landing-sop
description: LookForge Phase 3 创意落地的 3 步法 — JTBD 标签注入 + 前端分组视图 + 智能排序（含 v0.2 Schema/Embedding/AB 框架）
license: MIT
metadata:
  author: 渔芯科技
  version: "0.2.0"
  related_skills: [maodou-product, lookforge-jtbd-canvas]
  changelog: "v0.2 升级（2026-09-13 06:00 cron）：实测 RequirementProfile 仅 6 字段缺 JTBD 8 维度，新增 §2 字段扩展 + Embedding 选型 + Redis 轻量 A/B 框架"
---

# JTBD × LookForge Phase 3 落地 SOP v0.2

> 📅 2026-09-13 06:00 v0.2 升级（v0.1 = 2026-09-11 12:00 草稿）
> 👤 毛豆
> 🔗 主 skill：maodou-product
> 📌 v0.1 → v0.2 改动：
>   1. **修正 §五依赖** — 实测 RequirementProfile 只有 6 字段（target_users/core_problems/expected_outcomes/budget/timeline/constraints），缺 JTBD 8 维度
>   2. **新增 §二** Phase 2 JTBD 画像字段扩展 schema（blocker = 不扩字段 Step1 无数据）
>   3. **新增 §3.5** Embedding 选型：复用 ChromaDB ras_knowledge 同款 all-MiniLM-L6-v2
>   4. **新增 §3.6** A/B 框架轻量版（Redis Hash 计数器，免前端框架）
>   5. **新增 §八** 阻塞 vs 非阻塞路径切分
> 📌 起源：evolution report `2026-09-11_12.md §B`
>
> ⚠️ **2026-09-13 升级沉淀（写入 ***SECRET*** v1.3）**：
>   - 跨 profile 升级 SOP 时用 `patch` + `cross_profile=true`，不用 `skill_manage edit`
>   - 多 section 重编号后必须 `grep -E "^## " SKILL.md` 验证唯一性（本升级踩了 2 次重复 §四/§五/§六）

## 一、问题定义

LookForge Phase 3（技能编排）产出 50+ 创意，但用户看不出"哪个创意解决了我的 JTBD 痛点"。

**当前痛点**：
- 创意按"技能维度"展示，50 个创意平铺
- 用户无法判断"哪些对我的真实需求有用"
- Phase 2 输出的"需求画像"（JTBD 8 维度）未与 Phase 3 创意建立映射

## 二、Phase 2 JTBD 画像扩展（v0.2 新增 · 阻塞前置）

### 2.1 现状实测（2026-09-13 06:00 cron）

```python
# backend/app/models/domain.py L184-195
class RequirementProfile(BaseModel):
    """Phase 2 精准需求画像"""
    project_id: str
    target_users: str
    core_problems: list[str]
    expected_outcomes: list[str]
    budget_range: str
    timeline: str
    constraints: list[str]
    additional_notes: str = ""
    diagnosis: Optional["ProductDiagnosis"] = None
```

**缺陷**：只有 6 字段通用画像，没有 JTBD 8 维度（触发事件/进步/当前方案/阻碍/期望/情感/社会/雇用解雇）。

### 2.2 推荐扩展 schema（向后兼容）

```python
from typing import Literal
from pydantic import BaseModel, Field

class JTBDDimension(BaseModel):
    """JTBD 8 维度单条"""
    dim_id: Literal["trigger","progress","current_solution","obstacles",
                    "expected_outcome","emotional","social","hire_fire"]
    content: str = Field(..., min_length=10, description="用户描述 ≥10 字")
    weight: int = Field(0, ge=0, le=10, description="用户标红权重 0-10，0=未标")

class JTBDCanvas(BaseModel):
    """8 维度 JTBD 画像"""
    dimensions: list[JTBDDimension] = Field(..., min_length=8, max_length=8)
    primary_dim: Optional[str] = None  # 用户标红最高的维度 ID

# RequirementProfile 扩展（只追加字段，向后兼容）
class RequirementProfile(BaseModel):
    # ... 原 6 字段保留 ...
    jtbd_canvas: Optional[JTBDCanvas] = None  # ★ v0.2 新增
```

### 2.3 Phase 2 智能追问改造

**当前**：phase2_service.py 5-6 轮基础追问（用户/痛点/预算/时间/约束）。

**升级**：在第 3 轮追问后插入"JTBD 8 维度快速填充卡片"：
- 用 8 张 Tab 卡让用户各写 10-50 字
- 用户可拖动 slider 标红权重（0-10）
- 平均耗时 +3 分钟，转化率 ↓5%（待 A/B 验证）

**工时**：0.5 天（schema + 前端卡片 + API 路由 + 持久化）。

### 2.4 依赖 & Pitfalls

- ✅ Pydantic v2 已支持 `Literal` + `Field(ge/le)`
- ❌ 不要改 RequirementProfile 现有 6 字段（破坏向后兼容）
- ❌ 不要把 JTBD 卡片设为强制（用户跳过则 jtbd_canvas=None，Step 1 跳过整批但前端不报错）

---

## 三、3 步落地法（每步独立可验收）

### 步骤 1：JTBD 标签注入（数据层）

**目标**：为每个创意打上 0-3 个 JTBD 维度标签。

**实现位置**：
- `backend/app/services/jtbd_tagger.py`（新增）
- **前置**：完成 §2 Phase 2 JTBD 字段扩展（否则 `jtbd_canvas=None`，Step 1 跳过整批）

**伪代码**：
```python
async def tag_idea_with_jtbd(idea: Idea, jtbd_canvas: JtbCanvas) -> TaggedIdea:
    """复用 ChromaDB 同款 embedding 模型（见 §3.5）"""
    from sentence_transformers import SentenceTransformer, util
    model = SentenceTransformer("all-MiniLM-L6-v2")  # 384 维
    idea_vec = model.encode(idea.description)
    scores = {}
    for dim in jtbd_canvas.dimensions:
        dim_vec = model.encode(dim.content)
        scores[dim.dim_id] = float(util.cos_sim(idea_vec, dim_vec))
    top_dims = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:3]
    return TaggedIdea(
        idea_id=idea.id,
        jtbd_dimensions=[d for d, s in top_dims if s > 0.5],  # 阈值 0.5
        jtbd_scores=scores,
        primary_jtbd=top_dims[0][0] if top_dims[0][1] > 0.65 else None,
    )
```

**工时**：0.5 天（1 service + 1 unit test）

**验收**：50 个创意每个都至少被打上 1 个 JTBD 标签（标签 0.5 阈值）。

### 3.5 Embedding 模型选型（v0.2 新增）

| 候选 | 维度 | 大小 | CPU 推理 | 优点 | 缺点 |
|---|---|---|---|---|---|
| ✅ **all-MiniLM-L6-v2** | 384 | 80MB | 5ms/句 | **与 ChromaDB `ras_knowledge` 同款**（已加载） | 中文任务建议微调阈值 |
| ❌ OpenAI text-embedding-3-small | 1536 | API | 200ms/句 | 中文好 | 成本 + 网络 + 维度与 ChromaDB 不匹配 |
| ❌ BGE-large-zh-v1.5 | 1024 | 1.3GB | 30ms/句 | 中文 SOTA | 大模型 + 与 ChromaDB 不匹配 |

**结论**：用 all-MiniLM-L6-v2（0 额外依赖，与现有 ChromaDB 栈一致）。

**阈值建议**：
- 标签打标：0.5（cosine similarity）
- 主标签：0.65
- 中文任务微调：0.55 / 0.7（经验值，待 A/B 验证）

### 步骤 2：JTBD 分组视图（前端展示层）

**目标**：用户按 8 维度分组浏览 50+ 创意，而不是平铺。

**实现位置**：`frontend/src/components/Phase3/JTBDGroupView.tsx`（新增）

**组件骨架**：
```tsx
<JTBDGroupView>
  {jtbdDimensions.map(dim => (
    <JTBDGroup key={dim.id} title={dim.name}>
      <IdeaCardList ideas={ideas.filter(i => i.jtbd.includes(dim.id))} />
    </JTBDGroup>
  ))}
</JTBDGroupView>
```

**工时**：1 天（前端组件 + TanStack Query 接入）

**验收标准**：前端 8 维度分组视图可渲染，不影响 Phase 4/5/6/7 数据流。

### 步骤 3：智能推荐排序（用户体验层）

**目标**：按用户 JTBD 优先级排序创意，首屏看到"最相关"的 10 个。

**实现位置**：`backend/app/services/jtbd_ranker.py`（新增）

```python
async def rank_ideas_by_jtbd(ideas, jtbd_canvas, user_id):
    """用户标红维度加权 + JTBD 匹配度"""
    red_dims = {d.dim_id for d in jtbd_canvas.dimensions if d.weight >= 7}
    return sorted(ideas, key=lambda i: (
        i.primary_jtbd in red_dims,       # 用户标红维度加权
        i.jtbd_scores[i.primary_jtbd],   # 匹配度
        i.popularity,                    # 兜底
    ), reverse=True)
```

**工时**：1 天（算法 + A/B test 入口）

**验收**：智能排序后，前 10 个创意 ≥80% 是用户 JTBD 维度内的（A/B 验证）。

### 3.6 A/B 框架轻量版（v0.2 新增 · 解阻塞）

**问题**：原 SOP 依赖"前端 A/B 测试框架"，但 LookForge 当前未实现（全套要 1 天）。

**轻量方案**：Redis Hash 计数器（5 行代码，免前端框架，0.2 天搞定）

```python
# backend/app/services/ab_tester.py
import hashlib, redis.asyncio as redis

r = redis.from_url("redis://redis:6379/0")  # docker-compose 已有 redis 服务

async def get_variant(user_id: str, test_name: str) -> str:
    """A/B 分桶（同 user 永远同 bucket）"""
    h = int(hashlib.md5(f"{user_id}:{test_name}".encode()).hexdigest(), 16) % 100
    bucket = "A" if h < 50 else "B"
    await r.hincrby(f"ab:{test_name}", bucket, 1)
    return bucket

async def track_metric(test_name, bucket, metric, value=1):
    await r.hincrbyfloat(f"ab:{test_name}:{bucket}:{metric}", "sum", value)
    await r.hincrby(f"ab:{test_name}:{bucket}:{metric}", "count", 1)

# ranker.py 集成示例
variant = await get_variant(user_id, "jtbd_p3_sort_v1")
ideas = await rank_with_strategy(ideas, jtbd_canvas, variant)
# A=纯匹配度排序 / B=标红维度加权排序
await track_metric("jtbd_p3_sort_v1", variant, "ideas_selected", n_selected)
```

**A/B 看数命令**：
```bash
redis-cli HGETALL "ab:jtbd_p3_sort_v1:A:ideas_selected"
redis-cli HGETALL "ab:jtbd_p3_sort_v1:B:ideas_selected"
# 比较两组的 sum/count 比率 = 创意选中率
```

**vs 全套前端框架**：省 0.8 天工时，缺点是无法做"前端 UI A/B"，但 JTBD 排序是后端算法完全够用。

## 四、合计与上线建议

| 步骤 | 工时 | 阻塞 | v0.2 备注 |
|:---:|:---:|:---:|:---|
| ★ 0 Phase 2 字段扩展（§2） | 0.5 天 | **前置** | 不做则 Step 1 `jtbd_canvas=None` 跳过整批 |
| 1 标签注入（§3.1） | 0.5 天 | 依赖 ★ | 复用 ChromaDB 同款 embedding |
| 2 分组视图（§3.2） | 1 天 | 依赖 Step 1 数据 | 前端组件 |
| 3 智能排序 + A/B（§3.3+§3.6） | 1.2 天 | 无 | v0.2 改用 Redis 轻量 A/B（0.2 天） |
| **合计** | **3.2 天** | — | v0.1 是 2.5 天（阻塞未识别） |

**上线节奏建议**：
- **P0 同步**：§2 + §3.1 一起做（2 个 0.5 天）→ 立刻能打标签
- **P1 异步**：§3.2 + §3.3 + §3.6 三步并行（前端/算法/A/B）

## 五、通用模式（迁移到其他 Phase）

**3 步落地法 = "数据标签 → 前端分组 → 智能排序"**，可迁移到：

| 目标 | 数据标签 | 前端分组 | 智能排序 |
|---|---|---|---|
| Phase 1 调研方向卡（已纳入 v1.2 D1）| JTBD 维度 | 8 维度卡片 | 按用户痛点排序 |
| Phase 4 技术文档 | 行业子领域 | 子领域分组 | 按相关性排序 |
| Phase 7 商业模块 | 商业模式组件 | BMC 9 宫格 | 按 ROI 排序 |

**核心思路**：把用户的"心智模型"（JTBD 8 维度 / BMC 9 宫格 / MBBR 工艺）作为创意/文档的"分类轴"。

## 六、依赖与前置（v0.2 修正）

- ✅ `lookforge-jtbd-canvas` v1.4.0 已就绪（待华哥批）
- ✅ Phase 2 智能追问已可产出"需求画像"（基础 6 字段）
- ✅ ChromaDB `ras_knowledge` 已加载 all-MiniLM-L6-v2 384 维向量（2026-05-11 实装）
- ⚠️ **Phase 2 RequirementProfile 缺 JTBD 8 维度字段**（v0.2 §2 实测发现）
  - 不修则 Step 1 `jtbd_canvas=None` 跳过整批
  - 必做：§2 schema 扩展 + 前端卡片
- ⚠️ Step 3 智能排序需 A/B 测试框架（LookForge 当前未实现）
  - v0.2 解法：§3.6 Redis 轻量版（0.2 天，免前端框架）

---

## 七、决策项（待华哥批）

- ★ 是否先做 Phase 2 JTBD 字段扩展（§2，0.5 天）？
- ★ A/B 框架走"轻量 Redis 版（§3.6）"还是"全套前端框架版（1 天）"？
- 是否按"§2 → §3.1 → §3.2+§3.3+§3.6 并行"节奏上线？

---

## 八、Pitfalls（v0.2 强化）

- ❌ 不要跳过 §2 字段扩展直接做 Step 1（数据层 0 维度，整批跳过）
- ❌ 不要用 OpenAI embedding（成本 + 网络 + 与 ChromaDB 维度不匹配）
- ❌ 不要用"创意热度"作为唯一排序依据（忽略用户 JTBD 主观需求）
- ❌ 不要假设所有 JTBD 维度都有 ≥5 个创意（需要做维度稀疏度预检）
- ❌ 不要做"全套前端 A/B 框架"（阻塞 SOP 0.8 天工时，§3.6 Redis 版足够）
- ❌ 不要把 JTBD 8 维度字段设为必填（旧项目无 jtbd_canvas 会破坏）
- ✅ Step 3 智能排序必须做 A/B 验证（Redis 轻量版即可）
- ✅ 复用 ChromaDB 同款 embedding（0 额外依赖）

---

## 九、阻塞 vs 非阻塞路径切分（v0.2 新增 · 配套 cron-self-evolution-patterns）

### 8.1 阻塞路径（必须按顺序）
```
§2 Phase 2 字段扩展 (0.5d)
  └→ §3.1 标签注入 (0.5d)   [依赖 §2 的 jtbd_canvas 字段]
       └→ §3.2 分组视图 (1d)  [依赖 §3.1 的 TaggedIdea 数据]
            └→ §3.3 智能排序 (1d) [依赖 §3.2 的前端数据流]
                 └→ §3.6 A/B (0.2d) [依赖 §3.3 的 ranker hook]
```

### 8.2 非阻塞路径（可并行）

| 任务 | 并行起点 | 并行终点 |
|---|---|---|
| §2 前端卡片 UI 设计 | Day 0 | Day 0.5（与 §3.1 同完成） |
| §3.6 A/B 框架代码 | Day 2 | Day 2.2（与 §3.3 同完成） |
| ChromaDB embedding 预热 | Day 0 | 异步后台，无工时 |

### 8.3 跨 slot 决策交叉引用

- 与 `cron-self-evolution-patterns.md` §阻塞 vs 非阻塞路径 章节配套
- 与 `multi-phase-pipeline` Phase 1→2 状态机互补
- 与 `maodou-product` skill §cron 自我进化模式 互补

---

> 🤖 毛豆 · 2026-09-13 06:00 · JTBD × Phase 3 落地 SOP v0.2
> 📌 v0.1 (2026-09-11 12:00) → v0.2 (2026-09-13 06:00) 主要差异：
>   - 补 Phase 2 schema（发现阻塞）
>   - Embedding 选型（复用 ChromaDB）
>   - Redis 轻量 A/B 框架（解阻塞）
>   - 阻塞/非阻塞路径切分（配套 cron 协议）