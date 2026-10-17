---
name: multi-phase-pipeline
description: 多阶段产品开发平台实现方法论——覆盖前后端架构设计、状态管理、API设计模式。适用于 Phase 1调研→Phase 2竞品→Phase 3画像→Phase 4批量创意→Phase 5精选→Phase 6计划书 这类多阶段 AI 产品流水线。
triggers:
  - 多阶段产品开发平台
  - Phase 1 2 3 4 5 6
  - 批量生成后筛选
  - 多阶段 AI 流水线
---

# 多阶段产品开发平台实现方法论

## 适用场景
构建一个 6 阶段 AI 产品流水线：
- Phase 1 全网调研
- Phase 2 竞品逆向工程
- Phase 3 产品画像
- Phase 4 批量创意生成（50个）
- Phase 5 精选 + 详细技术文档
- Phase 6 开发计划书

## 核心架构模式

### 1. 双模式 API 设计（同端点，不同行为）

不要为同一 phase 创建两个端点。用请求体字段决定行为：

```python
# POST /api/projects/{id}/phase3
# 模式A：用户填写画像问卷 → 生成产品画像
# 模式B：用户选择研究方向 → 基于画像生成创意

class Phase3ProfileRequest(BaseModel):
    """模式A：画像提交"""
    industry: str
    description: str
    pain_point: str
    user: str
    price_range: str
    market: str
    channels: str
    advantage: str
    constraint: str
    # ... 更多维度

class Phase3IdeasRequest(BaseModel):
    """模式B：创意选择"""
    directions: list[str]

@router.post("/phase3")
async def run_phase3(project_id: str, request: Request):
    body = await request.json()
    
    # 判断模式
    if "industry" in body or "pain_point" in body:
        # 模式A：产品画像模式
        profile_req = Phase3ProfileRequest(**body)
        return await generate_profile(profile_req)
    elif "directions" in body:
        # 模式B：创意生成模式
        ideas_req = Phase3IdeasRequest(**body)
        return await generate_ideas(ideas_req)
```

### 2. 渐进式状态管理（关键！）

前端 `ideas` 和 `tech_docs` 必须用独立 `useState`，不要从 `data` 派生：

```tsx
// ❌ 错误：从 data 派生，无法支持异步渐进加载
// const ideas = data?.ideas || [];

// ✅ 正确：独立状态，支持分步加载
const [ideas, setIdeas] = useState<CreativeIdea[]>([]);
const [techDocs, setTechDocs] = useState<TechDoc[]>([]);

// ideas 初始为空数组，只有用户点击"批量生成"后才填充
// 这样 Phase 4/5/6 可以独立渲染，不依赖 data 加载
```

### 3. Phase 数据流向

```
Phase3 画像 → ideas(50个) → user筛选(20个) → tech_docs(5个) → dev_plan
              ↓
         独立状态 setIdeas    独立状态 setTechDocs
```

每个 Phase 的输出作为下一个 Phase 的输入，但状态独立管理。

### 4. 批量生成 + 渐进筛选模式

```
Phase4: 批量生成 50 个创意（用户未选择时）
  → ideas 数组 full
  → UI: 卡片列表 + 多选框 + 分类标签

Phase5: 用户手动 50→20→5 筛选
  → 20个精选 → POST /phase5 → LLM 精选 5 个
  → 5个精选 → 各自生成详细技术文档
```

## 后端服务拆分

每个 Phase 对应一个 Service：

```
services/
  research_service.py   # Phase 1+2 调研 + 竞品逆向
  profile_service.py     # Phase 3 产品画像
  idea_service.py        # Phase 4 批量创意
  techdoc_service.py     # Phase 5 技术文档
  plan_service.py        # Phase 6 开发计划
  llm_service.py        # LLM 调用封装
```

Service 之间通过 Domain Model 传递数据，不直接耦合。

## 关键陷阱

1. **不要让后端端点返回空数组时触发额外逻辑** — Phase4 的 `idea_ids=[]` 要特殊处理，用 `default_factory=list` 而非 `min_length=1`

2. **Phase3 画像和 Phase4 创意的 prompt 分离** — 画像 prompt 用 9 维度诊断结构，创意 prompt 用"方向+画像+市场空白"

3. **前端残留旧代码** — 重写 Phase 区块时，容易遗漏旧的状态派生变量（如 `const ideas = data?.ideas || []`），导致与新独立状态冲突

4. **后端重启** — 修改 `app/main.py` 或路由后必须杀掉并重启 uvicorn 进程

5. **Phase 子服务"假阳性 PASS"陷阱**（2026-08-25 实战，HW-001 craft+test 服务）— 见下方 §子服务开发模板 pitfall

## Phase 子服务开发模板（2026-08-25 实战沉淀）

LookForge Phase 6 由 7 个子环节组成（需求/方案/仿真/工艺/测试/差异化/嵌入），每个子环节都可以套用同一模板独立开发。本节给出可复用模板。

### 子服务 5 件套（最小可交付单位）

```
backend/app/services/<name>_service.py   # 业务逻辑（5-8 个 case + 经验公式）
backend/app/api/<name>.py               # FastAPI 路由（5 端点）
backend/app/main.py                     # +2 行 include_router
<reference>                              # 经验公式/标准引用
端到端验证脚本                          # import + 全 case 跑通
```

### Service 层标准结构

```python
# 1. 顶部：SCHEMA 常量（每个 case 的输入参数 + 元数据）
<NAME>_INPUT_SCHEMAS = {
    "case_id_1": {
        "case_id": "case_id_1",
        "name": "用例名称",
        "description": "简短描述",
        "hw_subtypes": ["ras_aquaculture", "industrial_equipment"],
        "related_standard": "GB/T XXXX-XXXX",
        "estimated_hours": 5.0,
        "input_schema": {
            "param_1": {"label": "参数1", "type": "float", "default": X, "range": [lo, hi]},
            "param_2": {"label": "参数2", "type": "select", "options": ["A","B","C"], "default": "A"},
        },
    },
    # ... 4 个以上 case
}

# 2. HW-XXX 设备专项预置（推荐每设备一套）
HW001_<NAME>_PRESETS = {
    "case_id_1": {"param_1": ..., "param_2": ...},  # 真实设备参数
}

# 3. 单例类 + get_<name>_service() 工厂
class <Name>Service:
    def get_cases(self, hw_subtype="ras_aquaculture"): ...
    def get_schema(self, case_id): ...
    def run_<name>(self, case_id, inputs, hw_subtype, project_id): ...
    def _run_<case>(self, inputs): ...  # 每个 case 一个内部方法

def get_<name>_service(): ...  # 单例
```

### API 层标准 5 端点（FastAPI）

```python
router = APIRouter(tags=["<name>"])  # 不要加 prefix！

class Run<Name>Request(BaseModel):
    case_id: str
    hw_subtype: Optional[str] = "ras_aquaculture"
    inputs: dict[str, Any] = Field(default_factory=dict)

@router.post("/{project_id}/<name>/cases")
@router.get("/{project_id}/<name>/schema/{case_id}")
@router.post("/{project_id}/<name>/run")
@router.post("/{project_id}/<name>/chat")    # 关键词路由（无 LLM）
@router.get("/{project_id}/<name>/results")   # 历史（V2 接 PG）
```

**关键**：`router = APIRouter(tags=[...])` **不加** `prefix`。在 `main.py` 加 `app.include_router(router, prefix="/api/projects")`。

### main.py 注册（2 行）

```python
from app.api import craft, test
app.include_router(craft.router, prefix="/api/projects", tags=["工艺设计"])
app.include_router(test.router, prefix="/api/projects", tags=["生产测试"])
```

### Chat 路由关键词模式（无 LLM 依赖）

```python
keyword_map = {
    "case_welding": ["焊接", "weld", "焊缝", "TIG", "氩弧"],
    "case_assembly": ["装配", "assembl", "工序", "工位"],
}
matched_case = next((cid for cid, kws in keyword_map.items() if any(k in msg for k in kws)), None)
```

匹配失败 → 返回 `need_clarification` + `available_cases` 列表让用户选。LLM 复杂解析放 Phase 7。

### 端到端验证脚本（必跑）

```python
# 验证 service 加载 + 全 case 跑通
from app.services.<name>_service import get_<name>_service, HW001_<NAME>_PRESETS
svc = get_<name>_service()
for case_id, preset in HW001_<NAME>_PRESETS.items():
    r = svc.run_<name>(case_id, preset, 'ras_aquaculture', 'test-proj')
    # 断言 status / verdict / 关键字段

# 验证 API 路由注册（不触发 orchestrator）
from app.api.<name> import router
assert len(router.routes) == 5

# 验证 main.py 注册
with open('app/main.py') as f:
    assert '<name>.router' in f.read()
```

### § 子服务 pitfall（HW-001 craft+test 实战 2026-08-25）

**P0 假阳性 PASS**：第一次跑 HW-001 test_service 5 个用例只过 2 个。原因不是算法错，是**预置参数 + 经验公式边界没对齐**：

| 假象 | 真实问题 | 修正方法 |
|------|----------|----------|
| `test_water_tightness` FAIL | 试验压力 0.6MPa / 设计 0.5MPa = 1.20（不在 1.25~1.5 范围）| 改预置 0.625MPa 让 ratio=1.25 |
| `test_noise_vibration` FAIL | 公式 `65 + 10·log₂(P)` 估算 78dB 超 75 限值 | 改公式 `60 + 10·log₁₀(P) - 20·log₁₀(d)` + 负荷系数 |
| `test_lifespan` FAIL | 1000h × 5 加速 = 5000h < 设计 20000h 80% 阈值 | 改预置 3600h → 90% 达成率 |

**教训**：写完经验公式算法后**必须用真实设备预置参数跑一遍端到端**，公式边界（分子对数底数/单位换算/判定阈值）和预置参数都要联合调，不能只调一边。

**自检清单**（每个新子服务必跑）：
1. 用 HW-XXX 真实参数（不是教科书示例）跑 5 个 case
2. PASS 率必须 100%
3. 每个 case 的 verdict/PASS-FAIL 字段都有真实断言
4. chat 路由至少 2 个关键词能匹配上
5. main.py 注册后用 `python3 -c "from app.main import app"` 验证（如果环境缺 key，至少 `ast.parse` 检查 + grep 验证注册）

### 子服务模板引用文件

- [ ] **chat 路由至少 2 个关键词可匹配**

## 跨分支代码考古 — git log 找沉睡代码（2026-09-06 毛豆实战沉淀）

> **触发条件**：用户/任务要求"新增 XXX 模块"，且项目 git 历史中存在同名/类似模块的旧 commit（被废弃或并入其他路径），但**当前 working tree 缺失**。**先考古再写新代码**，可能节省 50%+ 工时。

**反面案例**：原计划重写 LookForge 认证层（JWT + OAuth 三 provider），估算 8h。`git log --oneline` 发现 `e15e2c7a Initial commit` 内有 `backend1/app/auth/`（jwt.py 69 行 + oauth.py 212 行 + User/UserSession model + 4 路由 = **820 行完整模块**）。迁移工作量仅 4.1h（**节省 49%**）。

### 5 步考古 SOP

```bash
# Step 1：列所有 commit，找被废弃的初始版本
git log --oneline -20
# 输出示例：e15e2c7a Initial commit: LookForge backend structure
#          8f16d53e fix(lookforge): P0 止血 4 处 (9/4 cron 漏提交)
#          ... 中间 50+ commits，可能某次合并把 backend1/ 整体删除

# Step 2：用关键词搜相关 commit
git log --all --grep="auth\|jwt\|oauth" --oneline
# 或更宽松：git log --all --grep="auth" --diff-filter=A -- '*.py'

# Step 3：看文件清单 + 行数
git show --stat e15e2c7a | head -50
# 重点看 backend1/ 或 archive/ 或 _deprecated/ 这类被清理目录

# Step 4：评估依赖是否还在 requirements.txt
grep -E "python-jose|passlib|httpx" backend/requirements.txt
# 全部命中 = 零安装成本；缺 1 个 = pip install 5 分钟；缺 ≥3 = 放弃复活

# Step 5：评估兼容性冲突点
# 对比 import 路径 / Settings 字段名 / Base 类位置 / 模型命名
```

### 兼容性冲突矩阵（4 类常见冲突）

| # | 冲突 | backend1 (老分支) | backend (现分支) | 处理 |
|---|------|-----------------|-----------------|------|
| 1 | Settings 字段大小写 | `JWT_SECRET_KEY`（大写）| `secret_key`（小写）| 改为小写统一风格 |
| 2 | Base 引用路径 | `from app.db.database import Base` | `from app.core.database import Base` | 改 import |
| 3 | ORM 模型缺失 | backend1 有 User 表 | 现 backend 无 User | 在 `models/db.py` 末尾新增 |
| 4 | metadata 保留字 | `metadata_` Python / `metadata` DB | backend 已用 `extra_data` JSON | 统一用 `extra_data` |

### 7 步迁移模板（按依赖顺序）

| Step | 动作 | 工时（认证层实例） |
|------|------|---------------------|
| 1 | 配置扩展（Settings 加新字段）| 0.5h |
| 2 | 纯函数模块移植（jwt.py）| 0.5h |
| 3 | 第三方集成移植（oauth.py）| 1.0h |
| 4 | ORM 模型补齐 + alembic migration | 0.5h |
| 5 | Pydantic Schemas（独立文件）| 0.5h |
| 6 | FastAPI Router（4 路由）| 1.0h |
| 7 | main.py include_router（1 行）| 0.1h |
| **合计** | | **4.1h** |

### 适用 vs 不适用判断

**适用**：
- ✅ 旧 commit 完整模块（>= 100 行）
- ✅ 依赖已在现 requirements.txt
- ✅ 接口边界清晰（model + schema + service + router 分离）
- ✅ 不需要新功能，纯复活

**不适用**：
- ❌ 旧代码本身有 BUG（不要复活，要重写）
- ❌ 旧代码依赖的服务已下线（如 v1 API 已废弃）
- ❌ 跨大版本兼容（Python 2→3、React 16→18，太多坑）

### 回滚预案（每步 git 锚点）

| 风险 | 回滚命令 |
|------|----------|
| 单文件 BUG | `git checkout HEAD -- backend/app/auth/jwt.py` |
| Alembic 失败 | `alembic downgrade -1` |
| main.py 启动失败 | `git checkout HEAD -- backend/app/main.py` |

回滚耗时 < 5 分钟（每步都有 git 锚点 = 安全感）。

### 配合 Cron 自进化的接力执行

迁移计划可拆为多个 cron 时段：

| cron | 动作 | 工时 |
|------|------|------|
| 04:00 | 考古 + 写迁移计划 markdown | 0.5h |
| 06:00 | Step 1（配置扩展）| 0.5h |
| 08:00 | Step 2-3（核心模块移植）| 1.5h |
| 10:00 | Step 4（ORM 补齐）| 0.5h |
| 12:00 | Step 5-6（schemas + router）| 1.5h |
| 14:00 | Step 7（挂载 + 集成测试）| 0.5h |
| **合计** | | **5h** |

**对比一次性做完**：分阶段 cron 接力允许中途回滚 + 监督 cron 自动 claim/start，避免"写一半被迫中断"。

详见 `references/***SECRET***.md`（LookForge 认证层复活完整案例 820 行 + 7 步 SOP + 兼容性矩阵 + cron 接力表）。

## 验证清单

- [ ] Phase 3 问卷 9 维度字段完整（industry/description/pain_point/user/price_range/market/channels/advantage/constraint）
- [ ] Phase 4 支持空 `idea_ids` 批量生成 50 个
- [ ] `ideas` 和 `tech_docs` 是独立 useState，不从 data 派生
- [ ] PhaseNav 组件与 `currentPhase` 状态同步
- [ ] 后端修改后杀掉旧进程并重启
- [ ] 前端 `npm run build` 无 TypeScript 错误
- [ ] **Phase 子服务 5 件套完整**（service + api + main.py 注册 + 端到端验证 + HW-XXX 预置）
- [ ] **子服务 PASS 率 100%**（用真实设备预置参数，不是教科书示例）
- [ ] **chat 路由至少 2 个关键词可匹配**
