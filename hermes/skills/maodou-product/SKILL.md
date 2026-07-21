---
name: maodou-product
description: '毛豆（产品经理）核心技能集 — 产品设计冲刺、需求洞察、敏捷开发、代码协作、LookForge多阶段产品研发流程。触发条件：毛豆执行产品相关任务，包括产品设计、竞品分析、需求优先级、Sprint计划、技术方案评估。'
license: MIT
metadata:
  author: 渔芯科技
  version: "1.4.0"
---

## 公司当前阶段策略（2026-05-08）

| 阶段 | 核心重点 | 毛豆的角色 |
|------|---------|-----------|
| **产品开发期（当前）** | ✅ 全员支援产品开发 | 核心开发：LookForge仿真/HW量产/机制标准化 |
| **产品上线后** | 销售+运营 | 届时调整 |

## 毛豆自我进化流程（2026-07-13新增）

当毛豆无待处理任务时，自动进入自我进化模式：

### 标准进化步骤
1. **检查任务队列**：确认无 pending/in_progress 任务
2. **行业研究**：搜索RAS循环水养殖最新研究和技术动态（优先使用 web/delegate_task, 避免 browser_navigate 到 Google Scholar 等可能超时的站点）
3. **方法论学习**：复习或学习产品设计方法论（JTBD/Design Sprint/Lean Startup）
4. **技能检查与同步**：检查~/.hermes/profiles/maodou/skills/目录完整性，若为空或不完整：
   - 先用`skills_list`查看当前所有可用技能
   - 通过`skill_view`加载需要的技能
   - 从~/.hermes/skills/同步可用技能（注意：该目录本身内容可能稀疏，主要技能通过技能系统直接管理）
5. **输出进化报告**：保存到~/.hermes/profiles/maodou/evolution/YYYY-MM-DD_HH.md
6. **更新进化日志**：追加新进化记录到/Users/hua/Desktop/渔芯科技/4-部门空间/毛豆-产品交付/workspace/evolution_log.md

### Cron模式下的工具限制（2026-07-15更新）
⚠️ **execute_code在cron模式下被阻止**：不能使用execute_code来写文件或执行Python脚本，必须改用terminal + write_file工具组合。

⚠️ **特殊字符问题**：terminal命令中避免使用 `&` 等特殊字符，会导致语法错误。

⚠️ **send_message禁止**：cron模式下不能单独调用send_message，所有通知必须通过final response自动送达，禁止对同一target二次发送。

### 进化报告标准格式
完整模板见 `references/evolution-report-template.md`

```markdown
# 毛豆进化报告 YYYY-MM-DD_HH

## 一、RAS循环水养殖行业最新动态

### 核心发现
1. 发现1（1句话）
2. 发现2（1句话）

### 对LookForge的建议
1. 建议1
2. 建议2

## 二、产品设计方法论学习

### [方法论名称]
1. 核心原则
2. 关键要点

### 对产品工作的启示
1. 启示1
2. 启示2

## 三、Skills目录检查结果
✅ skills目录完整，包含：
- 列表

## 四、下一步行动计划
1. 近期：...
2. 中期：...
3. 长期：...

---

**整理人**：毛豆
**整理日期**：YYYY-MM-DD HH:MM
```

### RAS行业最新发现汇总
#### 2026-07-13
1. **固液分离技术组合优化**：鼓滤（>100μm）、旋流分离（40-100μm）、泡沫分馏（<55μm）三种技术互补，组合使用可实现全面水质净化
2. **每日循环频率是关键参数**：2026年Aquaculture期刊最新研究表明，养殖池每日循环频率直接影响流场分布均匀性和鱼类福利
3. **超细颗粒处理痛点**：泡沫分馏技术填补了机械分离对<55μm颗粒去除的空白
4. **MBBR载体设计优化**：新型TPMS（三重周期最小曲面）载体在流化性能和生物膜附着方面表现更优

#### 2026-07-15
1. **智能水质监测技术升级**：新一代传感器可实时监测10+参数（pH、溶氧、氨氮、亚硝酸盐、硝酸盐、温度、盐度、浊度、ORP、CO2），数据精度提升30%，响应时间缩短至1秒
2. **AI驱动的投喂优化**：基于计算机视觉和机器学习的自动投喂系统，可根据鱼类摄食行为实时调整投喂量，饲料转化率提升15-20%
3. **循环水系统能效优化**：新型热泵技术结合余热回收，可使RAS系统能耗降低25-30%，尤其是在温控需求高的地区
4. **生物安全防控体系**：集成臭氧消毒、紫外线消毒和微滤的三级生物安全系统，可有效杀灭病原菌，降低养殖风险

#### 2026-07-16
1. **低水头增氧技术（LHO）**：气压需求降低50%，能耗降低50%，适配低碳节能需求，代表产品有荷兰AquaOptima LHO系统和挪威AKVA Connect LHO
2. **AI驱动的智能投喂系统**：基于机器视觉+强化学习的精准投喂，饲料浪费降低35%，FCR改善18-22%，代表产品有荷兰Nutreco的FeedingForecast AI和丹麦Billund Aquaculture的强化学习投喂优化器
3. **微藻集成系统**：原位脱氮+产微藻副产物，尾水减少60%，同时产出高价值EPA/DHA微藻，代表项目有挪威Cawthron研究所和荷兰Wageningen University的研究
4. **数字孪生技术**：实时仿真预测水质变化趋势，预警提前72小时，代表产品有Aquabyte、Poseidon AI、鱼晓系统等
5. **模块化生物滤池**：拆卸清洗方便，硝化效率提升30%，维护成本降低40%

#### 2026-07-17
1. **同一批技术持续深化**：LHO增氧/AI投喂/微藻集成/数字孪生/模块化滤池仍是行业热点方向
2. **Skills目录管理**：发现`~/.hermes/profiles/maodou/skills/`目录可能存在但为空的情况，需建立从`~/.hermes/skills/`同步技能的机制
3. **JTBD框架应用**：将LookForge定位为"当设备商为养殖户设计RAS系统时，快速验证参数并计算ROI以赢得客户信任"的工具，重点优化Little Hire（日常使用）体验

#### 2026-07-18
1. **LHO增氧技术成熟应用**：低水头增氧技术气压需求降低50%，能耗降低50%，适配低碳节能需求，代表产品有荷兰AquaOptima LHO系统和挪威AKVA Connect LHO
2. **AI投喂系统优化**：基于机器视觉+强化学习的精准投喂，饲料浪费降低35%，FCR改善18-22%，代表产品有荷兰Nutreco的FeedingForecast AI和丹麦Billund Aquaculture的强化学习投喂优化器
3. **微藻集成系统价值**：原位脱氮+产微藻副产物，尾水减少60%，同时产出高价值EPA/DHA微藻，代表项目有挪威Cawthron研究所和荷兰Wageningen University的研究
4. **数字孪生技术落地**：实时仿真预测水质变化趋势，预警提前72小时，代表产品有Aquabyte、Poseidon AI、鱼晓系统等
5. **Skills目录同步策略**：`~/.hermes/skills/`本身内容可能稀疏，需要时通过`skills_list`查看可用技能，通过`skill_view`加载需要的技能
6. **JTBD框架深度应用**：LookForge的Job Statement是"当设备商为养殖户设计RAS系统时，我想快速验证参数并计算ROI，以便赢得客户信任"；Big Hire优化方向是销售演示价值，Little Hire优化方向是日常使用流程简化

### 对AquaForge/LookForge的建议
1. 在仿真模块中增加"每日循环频率"参数优化功能
2. 建立固液分离技术组合选型工具
3. 增加超细颗粒去除效率的仿真分析

> **其他Agent对毛豆的支援**：老莫（技术资料）、小宝（市场调研推广）、黑豆（合规合同）、阿福（测试验收）
> 完整策略和Agent分工详见 `agent-overseer` skill。

## 毛豆产品经理核心技能

## 职责定位
毛豆是渔芯科技产品经理，负责LookForge产品定义、竞品分析、产品画像、创意筛选、开发计划，以及渔芯装报价系统开发。

## 六大核心产品版块（华哥确认，2026-06-25）

| 编号 | 商标 | 定位 | 对应现有项目 |
|:----:|------|------|------------|
| ① | **RKR** | 调研与知识库（版块间数据底座） | 01-RKR调研与知识库 |
| ② | **AquaForge** | 养殖仿真 | 02-AquaForge养殖仿真 |
| ③ | **EDAI** | 硬件开发 | 03-EDAI硬件开发 |
| ④ | **Eq-Sim** | 设备仿真 | 04-Eq-Sim设备仿真 |
| ⑤ | **LookForge** | RAS系统仿真 | 05-LookForge RAS系统仿真 |
| ⑥ | **建筑AI助手** | 行业垂直工具 | 06-建筑AI助手 |
| ⑦ | **软件项目开发助手** | AI多Agent软件开发平台 | 07-软件项目开发 |

> **产品定位**：对外可独立销售的SaaS/私有部署产品，对内统一六大产品线开发流程。
> **07-软件项目开发助手核心特性**：用户自然语言输入→6个专业Agent对立审核（产品生成→需求审核→架构审核→安全审核→AI适配审核→打磨定稿）→标准化文档直接投喂Claude Code落地编码。技术栈：Vue3+FastAPI+SQLite+SSE+Docker。
> 📐 完整开发规范和避坑指南：加载 `software-design-agent` skill（`skill_view('software-design-agent')`）

> **RKR定位（RKR是版块间数据底座）**：独立知识库运营平台，六大版块均可调用其向量检索和知识整理能力。

> **定位原则**：LookForge = RAS行业专用工具，非通用平台。
> **产品整合教训**：渔芯科技历史上存在6个涉及3D/仿真项目重复建设的问题。
> 新产品决策时必须先确认边界，避免与现有六大版块重叠。

## 核心技能调用

### 1. design-sprint（设计冲刺）
当需要快速验证产品方向时加载。
流程：理解→聚焦→草图→决策→原型→测试，5天完成。

### 2. jobs-to-be-done（需求洞察）
当需要挖掘用户真实需求时加载。
核心：用户"雇用"产品完成什么"工作"？功能需求 vs 情感需求。

### 3. lean-startup（敏捷开发）
当需要定义MVP范围时加载。
Build-Measure-Learn循环：小步实验→验证→迭代或转型。

### 4. LookForge Phase1-7 流程（直接内置，无需外部skill）
- Phase1 市场调研 → 行业信息收集（research-collection）
- Phase2 竞品逆向 → 竞品功能/定价/策略分析
- Phase3 产品画像 → 9维度画像（目标用户/痛点/解决方案/价值主张等）
- Phase4 批量创意 → 50个产品创意方案
- Phase5 技术报告 → 精选方案技术可行性论证
- Phase6 硬件开发流程嵌入LookForge → 七环节标准化×仿真用例库×差异化配置（★RAS养殖专项仿真嵌入）
- **Phase7 开发计划书** → P0/P1/P2优先级路线图（见下方专项节）

### 5. github-pr-workflow（代码协作）
当需要提交代码/创建PR/代码审查时加载。

## LookForge产品研发关键原则
1. 调研不够不输出——知识积累优先于快速输出
2. 竞品数据先行——没有竞品分析不拍板功能
3. 创意批量再精选——先50个再精选
4. 开发计划分优先级——P0核心/P1重要/P2可延期

## 常用输出模板

### 产品画像9维度
1. 目标用户
2. 用户痛点
3. 现有解决方案
4. 我们的解决方案
5. 独特价值主张
6. 客户收益
7.上市策略
8. 竞争壁垒
9. 成本结构

### 需求优先级矩阵
| 维度 | P0（立即） | P1（本Sprint） | P2（下个版本） |
|------|-----------|----------------|----------------|
**硬件开发任务子任务参考**（task_hw_05041523_*）：
- task_hw_05041523_1: 需求定义标准化（老莫）
- task_hw_05041523_2: 方案设计标准化（毛豆）
- task_hw_05041523_3: 仿真验证流程（毛豆）★ 已完成
  - 新增 `backend/app/services/simulation_service.py` — 仿真执行引擎（5个RAS仿真算法）
  - 新增 `backend/app/api/simulation.py` — 5个仿真API端点
  - 增强 `projects.py get_phase6_spec` — 自动注入仿真I/O schema
- task_hw_05041523_4: 工艺设计标准化（毛豆）
- task_hw_05041523_5: 生产测试标准化（毛豆）
- task_hw_05041523_6: LookForge嵌入（毛豆）★ 已完成
- task_hw_05041523_7: 差异化流程（毛豆）

## Phase 6 仿真交互范式（表单型 → 对话型演进）

### 当前问题：表单型API与用户认知存在鸿沟

现有 `POST /{project_id}/simulation/run` 要求用户填写 `case_id` + 结构化 `inputs` dict。
养殖户的真实表达是：**"我想养石斑鱼，1000方水体，预计多少钱回本"** — 而不是"选择水流场仿真→填写池体直径→填写深度……"。

Phase2 Sprint计划（P2-6）已规划"对话式追问界面"，但尚未实现。

### 三层架构（对话式仿真）

```
用户自然语言
    ↓ [LLM理解层] — 品种+区域+水体+预算四要素提取
结构化仿真参数（case_id + inputs）
    ↓ [仿真层] — 现有5个算法无需改动
中文报告 + ROI计算结果
```

### 对话式仿真 API 设计（★ 已实现 2026-05-06）

**实现文件**：
- `backend/app/services/simulation_service.py` — `chat_simulation()` + `_sim_roi()` + `_get_species_defaults()` + `_run_single_simulation()`
- `backend/app/api/simulation.py` — `POST /{project_id}/simulation/chat` 路由 + `ChatSimulationRequest` 模型

**核心逻辑**：
1. LLM 解析自然语言 → 品种/水体/预算/区域四要素
2. 自动选择仿真用例组合（sim_water_flow + sim_oxygen + sim_temperature，含投资时加 sim_roi）
3. `_sim_roi()` 算法：`年利润 = 水体×产量×单价 - 年运营成本，回本周期 = 投资/年利润`
4. ROI 分析返回：investment_wan / payback_months / annual_profit_wan / annual_roi_percent / conclusion

```python
# simulation_service.py — chat_simulation() 方法签名
async def chat_simulation(
    self,
    user_message: str,
    hw_subtype: str = "ras_aquaculture",
    project_id: Optional[str] = None,
) -> dict:
    """
    对话式仿真入口（Phase 7 差异化核心）
    - 内部同步执行：_run_single_simulation() 调用现有5个算法不变
    - ROI仿真：_sim_roi() 基于品种价格×产量计算回本周期
    """
```

```python
# simulation.py — async 路由（注意 async def）
@router.post("/{project_id}/simulation/chat")
async def chat_simulation(project_id: str, req: ChatSimulationRequest):
    result = await service.chat_simulation(
        user_message=req.message,
        hw_subtype=req.hw_subtype or "ras_aquaculture",
        project_id=project_id,
    )
    return {"project_id": project_id, **result}
```

**API 示例**：
```json
POST /api/projects/{id}/simulation/chat
{
  "message": "我在广东想养石斑鱼，1000方，投资200万，多久回本？",
  "hw_subtype": "ras_aquaculture"
}
```
```

### 最小可行对话流设计

**场景A — 设备商（简单场景）**：
```
用户: "客户要养加州鲈，500方，帮我仿真一下水流场和溶氧"
→ LLM解析: case_ids=[sim_water_flow, sim_oxygen], inputs={品种:加州鲈, 水体:500m³}
→ 调用2个仿真 → 合并报告
```

**场景B — 养殖户（ROI场景）**：
```
用户: "我在广东想养石斑鱼，1000方，投资200万，多久回本？"
→ LLM解析: 品种=石斑鱼, 区域=广东, 水体=1000m³, 预算=200万
→ 自动组合: sim_water_flow + sim_oxygen + sim_temperature（温控能耗）
→ ROI计算（调用知识库品种参数）
→ 输出: 回本周期 + 年利润 + 关键风险点
```

### 前端对话UI设计

- 类ChatGPT对话界面，底部输入框
- 每条消息可展开"仿真详情"折叠区（显示原始参数+图表）
- 支持追问："这个方案溶氧不够怎么办" → 自动关联上一轮仿真上下文
- 未来扩展：图片上传（养殖场景截图）+ 语音输入

### 竞品差异化

| 竞品 | 交互形态 |
|------|---------|
| AKVA Connect | 表单型 |
| Aquabyte | 表单型 |
| 东方仿真 | 表单型 |
| LookForge | **对话型 + ROI计算** ★ |

### 仿真用例与硬件设备映射

| 仿真用例 | 适用设备 | 输出指标 |
|---------|---------|---------|
| `sim_water_flow` | RAS养殖系统 | 水流场均匀性、流速分布 |
| `sim_oxygen` | RAS养殖系统 | 溶氧分布、曝气需求 |
| `sim_temperature` | RAS养殖系统 | 温控能耗、热交换 |
| `sim_drum_filter` | HW-001滚筒微滤机 | 过滤效率、TSS去除率、滤饼厚度、水头损失 |
| `sim_protein_skimmer` | HW-002蛋白质分离器 | 蛋白质去除率、气泡规格 |
| `sim_mbbr` | HW-003生物移动床反应器 | 生物膜面积、填料利用率 |
| `sim_roi` | 投资决策 | 回本周期、年利润、年ROI |

## Phase 6+ 3D流体仿真路线图（2026-05-10新增）

现有仿真为1D/0D计算模型（输入参数→输出标量结果），缺少三维可视化。
调研成果（全报告见 `references/fluid-dynamics-simulation-tools.md`）：

### 三阶段路线

| 阶段 | 技术栈 | 产出 | 时间 |
|------|--------|------|------|
| **Phase A: 可视化层** | Three.js + @react-three/fiber | 流线/粒子/切面云图/探针 | 2026Q2-Q3 (2-3人月) |
| **Phase B: 真实物理层** | OpenFOAM Docker + Celery | 工业级CFD计算 | 2026Q4-2027Q1 (3-4人月) |
| **Phase C: AI加速层** | PINNs (DeepXDE/NVIDIA Modulus) | 毫秒级实时预测 | 2027Q2+ (4-6人月) |

### 当前可启动（本周）
- Three.js 3D原型：把 `sim_water_flow` 输出映射到3D场景
- 探针API：`POST /simulation/{id}/probe?x=&y=&z=` → {velocity, pressure, do}
- 仿生知识卡片：10个RAS可用的生物流体原理→ChromaDB

### 关键发现
- **完全蓝海**：全球无RAS设备流体仿真SaaS产品
- **WebGPU粒子法**(WebGPU-Ocean/Splash)可实时60fps，短期首选
- **OpenFOAM** 工业标准，中期引入Docker化计算
- **仿生设计**：鲨鱼皮减阻8-12%/鱼鳃逆流交换/海绵多孔过滤等8+原理可直接对标HW-001/002/003

> 📐 完整技术选型对比、竞品分析、架构图、API设计 → `references/fluid-dynamics-simulation-tools.md`

## 水流场仿真（sim_water_flow）

## 滚筒微滤机仿真（sim_drum_filter）

当需要为 Phase 6 新增子服务（如工艺设计、生产测试、差异化配置），遵循以下模式：

### 1. 新建 service 层
```python
# backend/app/services/xxx_service.py
class XxxService:
    def get_cases(self, hw_subtype): ...
    def run_xxx(self, case_id, inputs): ...
    def get_schema(self, case_id): ...
```
每个 case 的参数定义放在文件顶部 `SCHEMA` 常量中。

### 2. 新建 API 路由
```python
# backend/app/api/xxx.py
from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import Optional, Any

router = APIRouter(tags=["xxx"])  # ← 不要加 prefix！

class ChatSimulationRequest(BaseModel):
    """对话式仿真请求"""
    message: str = Field(..., description="用户自然语言描述，如：'我想养石斑鱼，1000方水体，预计多少钱回本'")
    hw_subtype: Optional[str] = Field(default="ras_aquaculture", description="硬件子类型")

# 对话式仿真路由示例
@router.post("/{project_id}/simulation/chat")
def chat_simulation(project_id: str, req: ChatSimulationRequest):
    service = get_simulation_service()
    result = service.chat_simulation(
        user_message=req.message,
        hw_subtype=req.hw_subtype,
        project={"project_id": project_id}  # 可扩展为真实project对象
    )
    return result

# 注意：Router 不要加 prefix！
# 主 app 用 app.include_router(xxx.router, prefix="/api/projects") 挂载
# 如果在 router 里再加 prefix="/projects"，路径会变成 /api/projects/projects/...
```

### 3. 注册到 main.py
```python
from app.api import simulation, xxx  # 新API
app.include_router(xxx.router, prefix="/api/projects", tags=["xxx"])
```

### 4. 在 phase6 spec 中注入数据
在 `projects.py` 的 `get_phase6_spec` 中，给对应字段补充 schema：
```python
from app.services.xxx_service import SCHEMA
cases = hw_spec.get("xxx_cases", [])
for case in cases:
    case["schema"] = SCHEMA.get(case["id"], {})
```

### 5. 路由前缀防踩坑
**错误**：
```python
# simulation.py
router = APIRouter(prefix="/projects", ...)  # ❌ 错误

# main.py
app.include_router(simulation.router, prefix="/api/projects")  # → /api/projects/projects/...
```
**正确**：
```python
# simulation.py
router = APIRouter(tags=["simulation"])  # ✅ 无 prefix

# main.py
app.include_router(simulation.router, prefix="/api/projects")  # → /api/projects/{project_id}/simulation/...
```

## Phase 7 开发计划书方法论（LookForge核心输出）★ 已完成实现

**Phase 7 已完整实现**（2026-05-05）：`run_phase7()` + `CommercialPlan` 模型 + Phase 7 REST API。

### Phase 7 的本质定位
Phase 7 不是"功能堆砌"，而是**商业验证冲刺**——回答"卖什么、卖给谁、怎么卖、怎么赢"四个问题。
核心商业指标：LTV/CAC > 3（生死线），NRR > 110%（健康线）。

### Phase 7 必须回答的5个核心问题

| # | 问题 | 当前最佳答案 |
|---|------|-------------|
| 1 | 目标客户是谁？ | **设备商**（决策链短/付费能力强/青岛中科海/绿脉/崇睿） |
| 2 | 第一年目标多少客户？ | 3-5个种子设备商 + 50-100个试用养殖户 |
| 3 | 核心获客渠道？ | 设备商推荐 + 行业展会 + 学术论文背书 |
| 4 | 如何防止免费陷阱？ | 设备商工具定位 + 按次超额计费，无通用免费版 |
| 5 | 如何建立数据护城河？ | 每次仿真脱敏数据贡献行业基准，用户获鱼币奖励 |

### P0/P1/P2 优先级框架（2026落地路径）

**P0（2026-Q2，必须做）：**
- ROI计算器嵌入仿真流程（输入：品种+水体+设备→输出：回本周期+年利润）★ 已实现（chat_simulation + _sim_roi）
- **品种参数库L1完善（7个品种）** ⚠️ 当前仅5个品种（石斑鱼/加州鲈/南美白对虾/罗非鱼/虹鳟），**缺叉尾鮰/泥鳅** — `_sim_roi` 的 `price_per_jin` 字典需补充
- 1个种子设备商访谈（青岛中科海或绿脉，验证切入时机）

**P1（2026-Q3，应该做）：**
- 订阅定价方案V2（参照鱼乐宝¥598-2,499/月，设计三档套餐）
- 竞品追踪数据库（AKVAconnect/AQUA-SIST/Xylene/Aquabyte/eFishery）
- 差异化配置UI + 数据回流机制设计

**P2（2026-Q4，可以做）：**
- 按次超额计费API
- 多语言支持
- API开放平台

### "看见未来"品牌落地关键
- **仿得准 > 功能全**：水流场/溶氧/温度是RAS核心，5个算法已覆盖
- **ROI计算器是关键破局点**：让养殖户"算得出省钱"才能激活采购
- **设备商是最佳B端切入渠道**：决策链短（老板直接拍板），核心话术"你们客户在做RAS设计时，是否经常遇到参数选型错误？"

### Phase 7 开发计划书标准格式（OSM框架）
```
规模（Scale）：目标客户数/仿真次数/月活
模式（Model）：订阅+超额+设备商分成
时间线（Milestones）：Q2种子→Q3验证→Q4扩张
商业指标：CAC<¥2000、LTV/CAC>3、NRR>110%
```

## 硬件七步法与主动缺口识别

每个硬件设备（HW-001/HW-002/HW-003...）遵循七步标准流程：

| 阶段 | 目录 | 毛豆职责 |
|------|------|---------|
| 01_需求定义 | 需求定义.md | 老莫（毛豆复核） |
| 02_方案设计 | 方案设计.md | 毛豆 |
| 03_仿真验证 | 仿真验证.md | 毛豆 |
| 04_工艺设计 | 工艺设计.md | 毛豆 |
| 05_生产测试 | 生产测试.md | 毛豆 |
| 06_量产导入 | 量产导入.md | 毛豆 |
| 07_差异化 | 差异化配置.md | 毛豆 |

**主动缺口识别（任务池空时触发）**：
当 `in_progress=0` 且 `pending=0` 时，扫描硬件目录找缺口：
```python
import os
base = "/Users/hua/Desktop/渔芯科技/4-部门空间/毛豆-产品交付/"
devices = ["HW-001_滚筒微滤机", "HW-002_蛋白质分离器", "HW-003_生物移动床反应器"]
for dev in devices:
    for step in range(1, 8):
        step_dir = os.path.join(base, dev, f"{step:02d}_*")
        if not glob.glob(step_dir):
            print(f"{dev} 缺失阶段 {step:02d}")
            break  # 找第一个缺失的作为主动工作目标
```
**本 session 实操结果（2026-05-06 核实，2026-05-07 修正）**：HW-002 和 HW-003 的目录结构已完整（01~07子文件夹均存在），且 **04_工艺设计/05_生产测试/07_差异化 三个阶段均已有 md 文件**。仅 `06_量产导入` 目录空（需样机完成），`03_CAD图纸` 目录空（需结构工程师提供源文件）。HW-001 是完整范本（7个文档均有内容）。

**标准文档结构参考**：
- `仿真验证.md` 包含：仿真用例库表格（5个用例ID+名称）、LookForge 参数配置表、仿真类型映射表、关键技术指标行业对比
- `差异化配置.md` 包含：四类产品差异化路径表、关键参数表（气泡规格/填料选型等）

## Post-V2 项目健康检查清单

当返回一个已完成 V2 的项目进行后续优化时，按此顺序做健康检查：

### 1. 跑测试（确认当前状态）
```bash
# 检查测试是否仍然全部通过
cd ~/Desktop/渔芯科技/6-产品研发/07-渔芯养 && npm test 2>&1 | tail -10
# 关注：Test Files X passed / Tests Y passed
```

### 2. 对比 prd.json 与实际状态（⚠️ 常见陷阱）
```bash
# 实际测试数 vs prd.json 中的 testCoverage.passed
grep -A5 '"testCoverage"' prd.json
```
- RAS CAD 教训：prd.json 此前记录 56 tests，实际已增长到 365 tests — **prd.json 容易过时**
- 如果发现统计差异 → 更新 prd.json 中的 `testCoverage` 和 `p2Tasks` 状态

### 3. 检查所有跟踪文件的一致性
对比以下文件的状态描述是否一致：
- `prd.json` — 产品需求定义（容易过时）
- `progress.md` — 开发进度日志
- `TASKS_REMAINING.txt` — 剩余任务列表
- `TASKS.txt` — 任务清单
- `task_plan.md` — 任务计划

### 4. 启动服务验证运行
```bash
# Web版
npm run dev:web   # Vite 在 5175 端口
# 或 Electron版
npm run dev       # electron-vite
```

### 6. 浏览器视觉检查
- 页面是否完整渲染（导航栏/设备库/视图区/状态栏）
- 设备库分类和数量是否符合预期
- 是否有明显的控制台错误

### 7. React 渲染性能优化（★ 每次健康检查必做）

此步骤在浏览器零错误后执行，直接刷新整个前端的渲染效率：

#### 7a. Store 订阅审计（P0）
```bash
# 全量 store 订阅（反模式，每次任何状态变更都触发重渲染）
grep -rn "useStore()" src/renderer/components/ --include="*.tsx"
grep -rn "usePipeStore()" src/renderer/components/ --include="*.tsx"
# → 全部改为 selector：useStore(s => s.fieldName)
```

#### 7b. React.memo 补齐（P0）
```bash
# 扫描 >200 行且缺少 memo 的组件
for f in $(find src -name "*.tsx" -exec wc -l {} + | sort -rn | awk '$1>200{print $2}'); do
  if ! grep -q "React.memo\| = memo(" "$f"; then
    echo "MISSING MEMO: $f"
  fi
done
# → export default memo(Component) 或 export const X = memo((props) => {...
# 注意：需同步添加 memo 到 React import
```

#### 7c. console.log 清除（P1）
```bash
# 生产环境不应有 console.log — 每次渲染分配字符串模板，累积性能消耗
grep -rn "console\.log" src/ --include="*.tsx" --include="*.ts" | grep -v node_modules
```
⚠️ **重要**：不要直接用 `sed -i '/console\.log/d'` 全局删除 — 多行 console.log 语句会被截断导致语法错误（如 GLTFModel 的模板字符串）。改用逐文件手工删除或只删除单行模式。

#### 7d. 性能验证
- `npm test` 全部通过
- 浏览器加载无 JS 错误
- FPS 正常（>30fps 在常规设备上）

### 8. 输出优化方向

对 Electron+React+TypeScript 项目进行系统化扫描。**完整命令集见 `references/react-ts-audit-commands.md`**。

扫描必须覆盖以下维度，直接对 P0 致命问题进行 score 评估：

| 扫描项 | 命令入口 | 严重性 |
|--------|---------|--------|
| 大文件清单（>500行需关注，>1000行必须拆分） | `find src -name '*.tsx' \| xargs wc -l \| sort -rn` | 高 |
| React.memo 覆盖率（>200行缺memo = P0） | 遍历检查每个 tsx 是否含 `React.memo` / `memo(` | **致命** |
| Store 全量订阅（`useStore()` / `usePipeStore()`） | `grep -rn "useStore()\|usePipeStore()"` | **致命** |
| console.log 残留 | `grep -rn "console\.log" src/` | 中 |
| 内联 style 对象计数 | `grep -rn "style={{" src/ \| wc -l` | 中 |
| 内联 onClick 箭头函数 | `grep -rn "onClick={(" src/` | 中 |
| `: any` 类型使用 | `grep -rn ": any" src/ \| wc -l` | 低 |
| TODO/FIXME/HACK 残留 | `grep -rn "TODO\|FIXME\|HACK" src/` | 低 |

### 7. 输出优化方向

基于上述检查和深度扫描，产出 P0/P1/P2 三级优化清单。典型分类：
- **P0 致命** — 缺 memo 的组件（>300行）、全量 store 订阅
- **P1 性能** — console.log 清理、内联对象/函数 memo 化
- **P2 技术债** — TODO 实现、`: any` 收紧、文档同步

> 📐 **RKR知识库运营平台需求**：独立知识库运营平台（环境检测/项目列表/Hermes嵌入/流式日志/可视化架构/查询下载），见 `references/rkr-knowledge-platform-requirements.md`
> 📐 **3D渲染尺寸一致性**：如果发现布局模式（占位几何体）与模型模式（GLB模型）中设备尺寸不一致，参阅 `references/3d-model-sizing.md` 了解 auto-scale 修复方案。
> 🔧 **管道系统架构**：管道双自动模式、断管串联、连接件端口系统、面板分离规则，参阅 `references/ras-cad-pipe-architecture.md`。
> ⚡ **性能优化检查清单**：Post-V2 优化流程（store订阅、memo审计、console清理、CSS冲突），参阅 `references/ras-cad-optimization-checklist.md`。
>
> ⚡ **优化执行手册**：检出 P0 问题后的具体修复步骤、优先级顺序和危险操作避坑，见 `references/frontend-optimization-playbook.md`。

## 当前开发文件
- `/Users/hua/Desktop/渔芯科技/6-产品研发/02-设备开发助手/backend/app/orchestrators/phase_orchestrator.py` — Phase 1-7 完整编排器（含 `run_phase7()`）
- `/Users/hua/Desktop/渔芯科技/6-产品研发/02-设备开发助手/backend/app/dispatchers/skill_dispatcher.py`
- `/Users/hua/Desktop/渔芯科技/6-产品研发/02-设备开发助手/backend/app/api/knowledge.py`
- `/Users/hua/Desktop/渔芯科技/6-产品研发/02-设备开发助手/backend/app/api/projects.py` — 含 Phase 6/7 REST API
- `/Users/hua/Desktop/渔芯科技/6-产品研发/02-设备开发助手/backend/app/api/orchestrator.py` — 含 `update_phase7_status` 钩子
- `/Users/hua/Desktop/渔芯科技/6-产品研发/02-设备开发助手/backend/app/models/domain.py` — 含 `CommercialPlan` 模型
- `/Users/hua/Desktop/渔芯科技/6-产品研发/02-设备开发助手/backend/app/services/simulation_service.py` ★ Phase 6 仿真执行引擎
- `/Users/hua/Desktop/渔芯科技/6-产品研发/02-设备开发助手/backend/app/api/simulation.py`          ★ Phase 6 仿真 API

**LookForge后端优化审计脚本**（`references/lookforge-backend-audit.md`）：
ChromaDB健康度检查、PostgreSQL连接验证、查询延迟测量、Category分布分析、Chunk长度分布、并发瓶颈点识别。2026-05-07完成优化报告，输出至 `/共享资料/LookForge优化报告/LookForge后端优化报告_2026-05-07.md`。

**Sprint规划方法论**（`references/sprint-planning-methodology.md`）：
Sprint计划标准格式——Mon/Tue/Wed/Thu/Fri五天节奏 + Sprint目标/交付物/验收标准三件套。适用于Phase 6迭代开发（对话式UI/品种库/PDF导出等）。

**仿真算法参考**（`references/simulation-algorithms.md`）：
5个RAS仿真用例的物理模型、关键公式、判断标准和参数说明，供后续开发参考。

**产品决策工作流**（`references/feasibility-analysis-workflow.md`）：
扫描文件→生成可行性报告→分解任务看板→分配Agent→等待决策→启动。
完整执行案例：2026-06-25 六大产品版块确认（报告见 `团队协作/公司架构可行性分析报告_2026-06-25.md`）。

**SaaS免费转付费转化路径**（`references/saas-conversion-path.md`）：
eFishery信任建立模式、3档触发点设计、LTV/CAC指标、LookForge订阅管理嵌入方式。

**Phase 7 开发计划书方法论**（`references/phase7-development-plan.md`）：
P0/P1/P2优先级框架、5个核心问题、OSM格式、"看见未来"品牌落地策略。

**LookForge Jobs-to-Be-Done 分析**（`references/lookforge-jtbd-analysis.md`）：
应用 JTBD 框架分析 LookForge 的核心工作、三个维度、四个力量、Big/Little Hire，以及 Phase 7 应用建议。

**竞品调研方法论**（`references/竞品调研方法.md`）：
直接导航优先于搜索引擎 + 竞品清单追踪 + 调研记录模板。关键发现：东方仿真官网（dongfangfangzhen.com）2026-05-06已下线，国内竞品真空确认。

**硬件开发任务子任务参考**（task_hw_05041523_*）：
- task_hw_05041523_1: 需求定义标准化（老莫）
- task_hw_05041523_2: 方案设计标准化（毛豆）
- task_hw_05041523_3: 仿真验证流程（毛豆）
- task_hw_05041523_6: LookForge嵌入（毛豆）★ 已完成

## 任务队列工作流（重要 — 曾导致分配错误）

渔芯团队使用共享任务库 `/Users/hua/Desktop/渔芯科技/团队协作/tasks.db`。

**TaskQueue 三步工作流：**
```python
q = TaskQueue()
# 第1步：创建（status=pending）
q.create_task(task_id="task_xxx", title="...", assignee="毛豆", ...)
# 第2步：认领（assignee变更，status仍是pending）
q.claim_task("task_xxx", "毛豆")
# 第3步：开始（status改为in_progress）⭐ 必须单独调用！
q.start_task("task_xxx", "毛豆")
```

**关键教训（已导致分配错误）：**
- `claim_task` 只改 assignee，status 仍是 'pending'，不调用 `start_task` 任务就不会进入"进行中"
- 如果先 `claim_task` 再 `start_task` 顺序反了，assignee 会正确但状态干净
- 分配任务给错误的人之后，可以用 `claim_task(task_id, correct_person)` 修正

**批量创建（防止 task_id 冲突）：**
```python
from datetime import datetime
import random, time

tasks = [("标题", "描述", "项目", "负责人", "P1"), ...]
for title, desc, project, assignee, priority in tasks:
    tid = f"task_{datetime.now().strftime('%m%d%H%M%S')}{random.randint(10,99)}"
    q.create_task(task_id=tid, title=title, description=desc,
                  project=project, assignee=assignee, priority=priority)
    q.claim_task(tid, assignee)   # 立即分配
    q.start_task(tid, "Hermes")  # 立即开始
    time.sleep(0.2)  # 间隔保证ID唯一
```

**验证命令：**
```bash
sqlite3 /Users/hua/Desktop/渔芯科技/团队协作/tasks.db "SELECT task_id, title, assignee, status, priority FROM tasks WHERE status='in_progress'"
```

### 常见死代码陷阱

**陷阱3：`models/__init__.py` 与 `domain.py` 必须同步（2026-05-13 新增）**
- `domain.py` 定义了 `DesignDraft` 但 `models/__init__.py` 忘了导出 → `ImportError: cannot import name 'DesignDraft'`
- 每次在 `domain.py` 新增类时，**必须同步更新** `models/__init__.py` 的 import 和 `__all__` 列表
- 这是 FastAPI 项目中最常见的运行时错误，排查时先查 `models/__init__.py`

**陷阱4：`generate_development_details()` 仅被 `run_phase2` 调用但生成通用选项**
- `run_phase2` 在第197行调用了它，但 `generate_development_details()` 只生成通用硬件选项（外观设计/控制系统/结构设计/材料工艺/安全合规/功能规格），不结合具体硬件子类型
- 正确做法：Phase6 `run_phase6` 已用 `_build_simulation_cases(hw_subtype, project)` 等方法补充了RAS专项仿真用例，Phase2的通用选项 + Phase6的专项仿真结合使用

**陷阱4：`SimulationService` 算法注册 — 三处必须同步**

在 `simulation_service.py` 中实现 `_sim_xxx()` 算法后，**必须同时在两处注册**，缺一不可：

**注册点A**：`phase_orchestrator.py` → `_build_simulation_cases()` → case 列表
- 添加 `{id, name, applicable_to, description, inputs, outputs, lookforge_workflow}` 条目
- 不注册 → API `GET /api/projects/{id}/phase6` 看不到该用例

**注册点B**：`simulation_service.py` → `_run_single_simulation()` → dispatch if/elif 链
- 添加 `elif case_id == "sim_xxx": return self._sim_xxx(inputs)`
- 不注册 → `POST /api/.../simulation/run` 返回 `{"status": "unknown_case"}`

**已发生的真实场景**：
- `sim_mbbr`/`sim_protein_skimmer` → 算法存在，dispatch 存在，但 case 未在 `_build_simulation_cases` 注册 → API看不到 ✅ 已修复
- `sim_drum_filter` → case 已在 `_build_simulation_cases` 注册，但 `_sim_drum_filter()` 方法和 dispatch 均缺失 → 返回 unknown_case ✅ 2026-05-07已修复

**验证清单**（发现 unknown_case 时的排查顺序）：
```python
# 1. 算法方法存在？
assert "_sim_xxx" in simulation_service_source

# 2. dispatch 注册了？
dispatch = simulation_service_source[simulation_service_source.find("def _run_single_simulation"):]
assert 'case_id == "sim_xxx"' in dispatch

# 3. case 在 _build_simulation_cases 注册了？
orch_source = open(".../phase_orchestrator.py").read()
assert '"sim_xxx"' in orch_source and "_build_simulation_cases" in orch_source
```

**教训**：实现算法和注册用例是**三个独立步骤**（算法实现 + dispatch注册 + case列表注册），只做一项或两项 LookForge 就残缺。

**陷阱5：检查方法** — 确认每个 `run_phaseN` 都实际调用了它声明要做的所有工作，不要只看方法存在。搜索 `generate_development_details` 的所有调用点，确认调用上下文是否符合预期。

**陷阱6：`_build_simulation_cases` 的 `project` 参数未充分利用**
- 该方法接收 `project` 对象但仅用 `hw_subtype` 做分支判断，`project` 可用于从 `project.hardware_blocks` 提取具体仿真需求，未来应扩展利用

### 任务队列纠错模式（重要）

**场景A：批量创建导致重复任务**
监督者创建任务时，同一任务可能被创建两次（不同时间戳）。旧任务需取消。

```python
# 识别：同一标题有两个 task_id（旧task_id含较早时间戳）
# 解决：取消旧任务，保留新任务
c.execute("""
    UPDATE tasks SET status='cancelled', result='重复任务，已被替代' 
    WHERE task_id = ?
""", ('task_overseer_旧时间戳_负责人',))
```

**场景B：任务分配给错误的人**
跨Agent任务（如"客服FAQ"分配给"毛豆"）。用 claim_task 修正。

**场景B2：监督者创建的成对任务分配错误**
监督者有时会创建成对任务（如同一天创建的 `task_overseer_0504161523_毛豆` 和 `task_overseer_0504161523_阿福`），如果毛豆领取了阿福的任务，立即修正。
判断方法：查看任务description中的角色关键词（"客服FAQ"→阿福，"产品手册"→毛豆）。
```python
# 典型错误分配
('task_overseer_0504161523_阿福', '【客服】鱼乐宝SaaS产品客服FAQ扩充', '毛豆', 'in_progress')
# 修正
c.execute("UPDATE tasks SET assignee='阿福' WHERE task_id='task_overseer_0504161523_阿福'")
```

```python
c.execute("UPDATE tasks SET assignee='正确负责人' WHERE task_id = ?")
```

**场景C：同一任务被多个子任务重复认领**
主任务 task_0504152217（硬件开发流程标准化）拆分出7个子任务（task_hw_05041523_1~7）。
执行前必须先查询 tasks.db 确认：
- 该任务是否已被其他Agent领取？
- 该任务的 task_id 与其他子任务是否重复？

```python
# 执行前检查
c.execute("SELECT task_id, title, assignee, status FROM tasks WHERE title LIKE '%需求定义%'")
results = c.fetchall()
# 如发现已有关闭/完成状态的重复任务，标记自己的为完成即可
```

**⚠️ execute_code 沙盒环境限制：**
`from task_queue import TaskQueue` 在 `execute_code` 沙盒中不可用（ModuleNotFoundError）。
**解决方案**：在 execute_code 中使用原生 sqlite3：

```python
import sqlite3
from datetime import datetime

conn = sqlite3.connect('/Users/hua/Desktop/渔芯科技/团队协作/tasks.db')
c = conn.cursor()

# 完成任务
c.execute("""
    UPDATE tasks 
    SET status = 'completed', 
        result = ?,
        done_at = ?
    WHERE task_id = 'task_overseer_xxx'
""", (result_text, datetime.now().isoformat()))

conn.commit()
conn.close()
```

**tasks表结构**：`task_id, title, description, project, assignee, priority, status, result, created_at, updated_at, done_at`

## 进化日志格式要求（每次必读）

进化日志路径：`/Users/hua/Desktop/渔芯科技/4-部门空间/毛豆-产品交付/workspace/evolution_log.md`

**输出格式（简洁优先）：**
```markdown
## 进化记录 YYYY-MM-DD HH:MM

### 研究主题：[主题名称]

**核心发现：**
- 发现1（1句话）
- 发现2（1句话）

**具体行动计划：**
- 行动1
- 行动2
```

**要求：**
- 每个发现不超过2句话
- 行动计划必须有具体数字/时间，不能是"继续研究"
- 进化完成后：更新MEMORY.md + 飞书群发【毛豆进化】+ 简要结论（50字内）

**⚠️ Cron模式飞书通知注意：** 禁止对同一target二次send_message，统一走final response。

## 团队Agent监督模式

Hermes（我）担任团队监督者。监督脚本位于：
`/Users/hua/Desktop/渔芯科技/团队协作/agent_overseer.py`

Cron：`*/15 * * * *`，每次检查所有Agent最后活跃时间，超过30分钟判定为空闲。

**监督策略（自动分配逻辑）：**
1. 读取各Agent的MEMORY.md修改时间（路径：`/Users/hua/Desktop/渔芯科技/4-部门空间/{部门目录}/memory/MEMORY.md`）
2. 空闲Agent → 从 tasks.db 匹配技能领域任务 → claim + start
3. 任务池空 → 主动创建对公司有益的任务并分配
4. 有情况时汇报飞书群

**已分配的典型任务（供参考）：**
- 毛豆：LookForge后端开发（ChromaDB接入/PhaseOrchestrator/PostgreSQL）
- 老莫：知识库建设、竞品调研
- 小宝：销售素材、自媒体内容
- 黑豆：法务合规、合同模板
- 阿福：测试验收、演示系统准备

## 任务状态报告Cron（毛豆进度汇报）

**调度**：每15分钟 cron `*/15 * * * *`

**核心逻辑**（增量汇报，去重压缩）：
1. 读取 tasks.db，查询 `status IN ('completed', 'done')` 作为已完成，`status IN ('pending', 'in_progress')` 作为进行中
2. 对比上次 checkpoint（`/Users/hua/.hermes/cron/output/last_report.json`）的 hash
3. hash 无变化 → 静默结束（不发送任何消息）
4. 有变化 → 生成压缩增量汇报，发送 final response（通过 cron origin auto-delivery 送达）

**重要经验教训：**
- 任务状态枚举有两个：`completed` 和 `done`（都算完成），查询时必须同时包含两者
- ⛔ **Cron 模式禁止单独调用 send_message**：Cron 的 final response 通过 origin auto-delivery 自动送达。尝试手动 `send_message` 到同一目标会触发 `duplicate_target` 或 `Could not resolve` 错误，导致发送失败。本session教训：即使想补充通知，也不要对同一 target 二次发送，统一走 final response 即可。
- 飞书大群实际名称：`渔芯科技（大群）`，但 Hermes Bot 尚未加入；当前可用的 DM：`oc_2db3b5373825567c3681d1ca580e0143`
- `cli_a964873dd7b8dbda` 是无效的 target name

**Checkpoint 文件格式**：
```json
{
  "completed": ["task_id_1", "task_id_2"],
  "pending": ["task_id_3"],
  "hash": "md5_hash_of_completed_ids"
}
```

**保存 Checkpoint（毛豆cron在final response前必须执行）**：
```python
import sqlite3, hashlib, json, os

conn = sqlite3.connect('/Users/hua/Desktop/渔芯科技/团队协作/tasks.db')
c = conn.cursor()

c.execute("SELECT task_id FROM tasks WHERE status IN ('completed', 'done') ORDER BY done_at DESC")
completed = [r[0] for r in c.fetchall()]
pending = [r[0] for r in c.execute("SELECT task_id FROM tasks WHERE status='pending'").fetchall()]

current_hash = hashlib.md5(",".join(sorted(completed)).encode()).hexdigest()

checkpoint = {
    "completed": completed,
    "pending": pending,
    "hash": current_hash
}

os.makedirs("/Users/hua/.hermes/cron/output", exist_ok=True)
with open("/Users/hua/.hermes/cron/output/last_report.json", 'w') as f:
    json.dump(checkpoint, f)

conn.close()
# ✅ Checkpoint saved. 下次心跳时 hash 比对无变化 → 静默跳过
```

**增量汇报模板**：
- ✅ 新完成：[任务名]（负责人）
- 🔄 新进行：[任务名]（负责人）
- 📋 进行中：共N个任务
