---
name: jtbd-phase3-landing-sop
description: LookForge Phase 3 创意落地的 3 步法 — JTBD 标签注入 + 前端分组视图 + 智能排序
license: MIT
metadata:
  author: 渔芯科技
  version: "0.1.0"
  related_skills: [maodou-product, lookforge-jtbd-canvas]
---

# JTBD × LookForge Phase 3 落地 SOP v0.1

> 📅 2026-09-11 12:00 草稿
> 👤 毛豆
> 🔗 主 skill：maodou-product
> 📌 起源：evolution report `2026-09-11_12.md §B`

## 一、问题定义

LookForge Phase 3（技能编排）产出 50+ 创意，但用户看不出"哪个创意解决了我的 JTBD 痛点"。

**当前痛点**：
- 创意按"技能维度"展示，50 个创意平铺
- 用户无法判断"哪些对我的真实需求有用"
- Phase 2 输出的"需求画像"（JTBD 8 维度）未与 Phase 3 创意建立映射

## 二、3 步落地法（每步独立可验收）

### 步骤 1：JTBD 标签注入（数据层）

**目标**：为每个创意打上 0-3 个 JTBD 维度标签。

**实现位置**：`backend/app/services/jtbd_tagger.py`（新增）

**伪代码骨架**：
```python
async def tag_idea_with_jtbd(idea: Idea, jtbd_canvas: JtbCanvas) -> TaggedIdea:
    return TaggedIdea(
        idea_id=idea.id,
        jtbd_dimensions=[
            dim for dim in jtbd_canvas.dimensions
            if cosine_sim(idea.description, dim.description) > 0.65
        ],
        primary_jtbd=max(jtbd_canvas.dimensions,
                         key=lambda d: cosine_sim(idea.description, d.description))
    )
```

**工时**：0.5 天（1 个 service + 1 个 unit test）

**验收标准**：50 个创意每个都至少被打上 1 个 JTBD 标签。

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

**算法骨架**：
```python
async def rank_ideas_by_jtbd(ideas: List[Idea], jtbd_canvas: JtbCanvas) -> List[RankedIdea]:
    """用户标红的维度优先 → JTBD 匹配度 → 创意热度"""
    return sorted(ideas, key=lambda i: (
        i.jtbd_score,                    # 用户 JTBD 匹配度
        i.primary_jtbd in user_red_dims, # 用户标红维度加权
        i.popularity                     # 兜底热度
    ), reverse=True)
```

**工时**：1 天（算法 + A/B test 入口）

**验收标准**：智能排序后，前 10 个创意 ≥80% 是用户 JTBD 维度内的（A/B 验证）。

## 三、合计与上线建议

| 步骤 | 工时 | 阻塞 |
|:---:|:---:|---|
| 1 标签注入 | 0.5 天 | 无 |
| 2 分组视图 | 1 天 | 无 |
| 3 智能排序 | 1 天 | 需前端 A/B 测试框架 |
| **合计** | **2.5 天** | — |

**建议**：与 LookForge v1.2 P0 包（智能推荐 / 复盘闭环）同步上线。

## 四、通用模式（迁移到其他 Phase）

**3 步落地法 = "数据标签 → 前端分组 → 智能排序"**，可迁移到：

| 目标 | 数据标签 | 前端分组 | 智能排序 |
|---|---|---|---|
| Phase 1 调研方向卡（已纳入 v1.2 D1）| JTBD 维度 | 8 维度卡片 | 按用户痛点排序 |
| Phase 4 技术文档 | 行业子领域 | 子领域分组 | 按相关性排序 |
| Phase 7 商业模块 | 商业模式组件 | BMC 9 宫格 | 按 ROI 排序 |

**核心思路**：把用户的"心智模型"（JTBD 8 维度 / BMC 9 宫格 / MBBR 工艺）作为创意/文档的"分类轴"。

## 五、依赖与前置

- ✅ `lookforge-jtbd-canvas` v1.4.0 已就绪（待华哥批）
- ✅ Phase 2 智能追问已可产出"需求画像"（SPEC.md Phase 2.1）
- ⚠️ Step 3 智能排序需 A/B 测试框架（LookForge 当前未实现）

## 六、决策项（待华哥批）

- 是否按"D7 先 → P0 包并行 → JTBD×P3 并行"节奏上线？
- A/B 测试框架由谁负责？（毛豆主力 / 老莫支援 / 团队其他成员）

## 七、Pitfalls

- ❌ 不要跳过 Step 1 数据标签直接做 Step 2 前端分组（前端没有数据可用）
- ❌ 不要用"创意热度"作为唯一排序依据（忽略了用户 JTBD 主观需求）
- ❌ 不要假设所有 JTBD 维度都有 ≥5 个创意（需要做维度稀疏度预检）
- ✅ Step 3 智能排序必须做 A/B 验证（不能凭直觉判断"是不是更相关"）

---

> 🤖 毛豆 · 2026-09-11 12:00 · JTBD × Phase 3 落地 SOP v0.1
> 📌 跨 slot 决策交叉引用：上午 evolution `self-evolution_2026-09-11.md §D.4 D4`（Phase 6 仿真用例 5→12）= 本 SOP 的"创意端类比"