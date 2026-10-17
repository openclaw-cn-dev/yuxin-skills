---
name: cad-automation
description: CAD 自动化与 3D 建模。四层架构：理论知识层(标准/材料/设计原则) > 技能层(JSON定义) > 桥接层(FreeCAD/CQ/ezdxf) > CAD引擎。当用户提到出图/建模/技能训练/知识库/制图标准/FreeCAD/CadQuery/EZDXF/训练平台/VibeCAD/vibecad时触发。
---

# CAD 自动化方案

## 战略方向（华哥 2026-08-16 定调）

华哥确认的路线：**不走"AI 直接凭空出图"，而是让 Codex 作为"手"操控真实设计软件**（VibeCAD MCP → FreeCAD / 渲染器），靠「训练 + 海量零件库 + 装配组合」为固定领域（RAS 设备/机械零件）出 CAD 工程图 + 效果图。节奏："重点关注，知识储备成熟后立项开发"。

现状资产已具备：VibeCAD MCP（已装）+ 158 零件库（`yuxin_cad.py` v3.0）+ 14 出图技能。**三个待补缺口**：

1. **效果图/渲染** — 目前只有工程图（STEP/STL/DXF），渲染效果图空白（Blender Cycles / FreeCAD 渲染工作台可控性未验证）
2. **装配组合** — 目前单零件，零件→装配→整机未做（装配约束/配合关系/干涉检查比单件复杂一个量级，是从"工具"到"产品"的关键一跃）
3. **Codex 端到端操控** — 目前"技能 JSON→脚本→FreeCAD"，Codex 直接驱动软件全闭环未打通

想法归档：`~/hermes/ideas/2026-08-16_Codex操控设计软件出CAD图与效果图_想法.md`

## 核心推荐：CadQuery （Python CAD）

```bash
pip install cadquery
```

### 基础用法
```python
import cadquery as cq

# 创建参数化盒子
box = cq.Workplane("XY").box(10, 20, 30)

# 打孔
result = box.faces(">Z").workplane().hole(5, 10)

# 导出
cq.exporters.export(result, "/tmp/model.step")
cq.exporters.export(result, "/tmp/model.stl")
```

### 适用场景
- 参数化零件（改几个参数自动重生成）
- 管道/连接器/支架（渔芯 RAS 设备）
- 批量生成型号变体

## DXF 输出（用于 2D 工程图）

```bash
pip install ezdxf
```

```python
import ezdxf
doc = ezdxf.new("R2010")
msp = doc.modelspace()
msp.add_line((0, 0), (100, 0))
msp.add_circle((50, 50), 20)
doc.saveas("/tmp/drawing.dxf")
```

## 参数化模板模式（HW-001 全套出图实战，2026-08-31 毛豆 cron）

**适用场景**：单设备多规格变体（XCS-100/200/400），客户可验收的 PDF 三视图带标题栏。

**完整模板 + 9 个踩坑 + 验证清单**：见 `references/cadquery-template-pattern.md`
**可运行模板代码**：见 `templates/hw_drum_filter.py`（HW-001 滚筒微滤机 XCS 系列，13 个 CLI 参数）

**单次调用产出（每个规格 7 类文件 = 21 文件/规格）**：
STEP + 8×STL + BOM CSV + params JSON + DXF 三视图 + SVG 三视图 + PDF 三视图带标题栏

**关键踩坑速查**：
- **STL 导出**：`cq.exporters.export(shape, str, exportType="STL")` ✅ —— 不要用 `shape.obj.exportStl()` ❌
- **Assembly.traverse** 返回 `(name, sub_ass)`，`sub.shapes` 才是 Solid list；`assembly.shapes`（无括号）对顶层 add 的零件为空
- **ezdxf SVG 默认暗背景**：必须 `Configuration(background_policy=BackgroundPolicy.WHITE, color_policy=ColorPolicy.BLACK)` 才出白底黑线
- **ezdxf draw_layout 把 viewBox 拉成横条**（~735:1，PNG 几乎全黑） → **放弃 ezdxf PDF，改用 reportlab 直接画三视图 + 标题栏**（每个 view 独立 scale+translate）
- **CadQuery 路径**：cron 沙盒 PYTHONPATH=/Users/hua/.hermes/profiles/maodou/home/Library/Python/3.9/lib/python/site-packages（系统 python3 没装）
- **CadQuery Color 第四参数是 alpha**：`cq.Color(0.7, 0.7, 0.75, 1.0)`
- **Frontend.draw_layout 参数顺序**：`(msp, finalize)` 位置参数，不要 `layout=` 关键字
- **SVGBackend 输出**：用 `backend.get_string(page)` + 自己写文件，不要依赖 recorder 自动输出
- **reportlab 中文**：`pdfmetrics.registerFont(UnicodeCIDFont("STSong-Light"))` 无需 .ttf

**与现有模式互补**：

| 模式 | 适用 |
|------|------|
| `yuxin_cad.py` v3.0（158 件库）| 单零件批量 |
| **本模板（hw_drum_filter.py）** | 单设备多规格变体 + 客户验收 PDF |
| `drawing_agent.py` + skill_library JSON | AI 操控 FreeCAD 实时画图 |

## 与 Hermes 集成思路

### VibeCAD MCP（推荐，2026-08-08 已安装）

VibeCAD v0.9.0 是 FreeCAD 的 AI Agent MCP 连接器，38 个工具，支持 Codex/Claude/WorkBuddy 通过结构化 MCP 调用操控 FreeCAD。安装于 `/Users/hua/VibeCAD/`，CLI: `vibecad`。完整安装/修复/工具分类见 `references/vibecad-mcp.md`，出图验证测试见 `references/vibecad-test-results.md`（3 零件全部通过 ✅）。

## 渔芯零件库（158 零件 + 统一生成引擎 v3.0）

### 统一引擎：`yuxin_cad.py`（v3.0，2026-08-08）

**单入口全品类**，替代旧版 `vibecad_gen.py` 和 `vibecad_ras_gen.py`。加载 10 个 JSON 库文件，按零件类型自动路由到对应 FreeCAD 脚本生成器。

```bash
cd 6-产品研发/34-渔芯社区/parts_library

# 统计 — 查看158零件分布
python3 yuxin_cad.py --stats

# 浏览 — 按品类筛选举例
python3 yuxin_cad.py --list --cat gears      # 只看齿轮
python3 yuxin_cad.py --list --cat ras        # 只看RAS

# 单件
python3 yuxin_cad.py --part GEAR_SPUR_M2Z20
python3 yuxin_cad.py --part HW001_DRUM_FILTER

# 批量
python3 yuxin_cad.py --batch ras             # 全部RAS设备+附件
python3 yuxin_cad.py --batch fasteners        # 全部紧固件
python3 yuxin_cad.py --batch all              # 158件全量出图
```

输出到 `~/Desktop/渔芯CAD图纸_MMDD/`，每件：FCStd + STEP + STL。

### 零件库组成（10个JSON文件，150零件）

| 库文件 | 内容 | 件数 |
|--------|------|------|
| `mechanical/standard_parts.json` | 螺栓(M6-M24)/螺母/垫圈/法兰(DN50-DN200)/轴承/管件/型材 | 39 |
| `mechanical/extended_parts.json` | 齿轮(直齿/斜齿)/弹簧(压缩/拉伸/扭转)/阶梯轴/平键半圆键/O型圈油封/弯头三通变径/球阀闸阀止回蝶阀/离心泵/电机/联轴器/链轮/带轮/带座轴承 | 40 |
| `ras/ras_equipment_v2.json` | 滚筒微滤机/蛋白质分离器/MBBR/曝气器/UV杀菌器/热泵换热器/滴流滤池/纯氧锥/罗茨风机/臭氧发生器/2种养殖水箱/水泵组/控制柜/管道汇流排 | 15 |
| `ras/ras_fittings.json` | UPVC蝶阀球阀止回阀/PVC弯头三通活接大小头/PVC法兰/橡胶软接头/管卡支架/流量计压力表温度溶氧传感器 | 21 |
| `steel/steel_structures.json` | H型钢(6种)/角钢(4种)/C型钢(2种)/圆钢管(3种)/节点(3种)/厂房(2种) | 20 |
| `steel/extended_structures.json` | H型钢(H150/H600)/角钢(L63/L80)/矩形管RHS/Z型钢/C型钢/梁柱刚接/拼接/支撑节点/管桁架/吊车梁/雨棚 | 13 |
| `prompts/drawing_commands.json` | 出图命令模板 v1.0（通用/RAS/钢结构/质检） | 17 |
| `prompts/drawing_commands_v2.json` | 出图命令模板 v2.0（建模/紧固件/管道/装配/工程图/质检/RAS系统/钢结构深化） | 42 |

### RAS 设备 3D 精模（15台）

参数 100% 对齐公司 `ras-aquaculture` 知识库。每台设备具备壳体+法兰接管+支腿/底座+内部结构。

| 模块 | 设备 | 实体建模方式 |
|------|------|-------------|
| 固体过滤 | 滚筒微滤机 | Box壳体 + Cylinder滚筒 + Cut空心 + 法兰接管 |
| 生物过滤 | MBBR滤器 / 滴流滤池 | Box/Cylinder壳体 + 内部布水管 + 曝气盘 |
| 蛋白质分离 | 蛋白质分离器 | Cylinder反应室 + Cone锥顶 + Cup泡沫杯 |
| 增氧 | 微孔曝气器 / 罗茨风机 / 纯氧锥 | Cone锥体 + 双转子 + 消音器 |
| 消毒 | UV杀菌器 / 臭氧发生器 | 水平管道 + 石英套管 + 放电管 |
| 温控 | 热泵换热器 | Cylinder壳体 + 端盖 + 换热管束 |
| 养殖容器 | 养殖水箱 Ø2000/Ø3000 | Cylinder筒体 + Sphere半球底 / Cone锥底 |
| 动力控制 | 水泵组 / 控制柜 / 管道汇流排 | 蜗壳体 + 机柜面板 + 支管阀门 |

引擎架构详情见 `references/parts-library-v3.md`（生成器路由规则、f-string双大括号规则、FreeCAD脚本模板分离模式）。

### 生成器路由规则（`yuxin_cad.py` 中 `get_generator` 函数）

| 检测条件 | 路由到 | 说明 |
|----------|--------|-------------|
| `"fasteners" in cat` | `gen_fastener` | 螺栓/螺母/垫圈 → 六角头+螺杆 |
| `"flanges" in cat` | `gen_flange` | 法兰 → 圆盘+螺栓孔 |
| `"bearings" in cat` | `gen_bearing` | 轴承 → 内外圈+滚珠 |
| `"gears" in cat` | `gen_gear` | 齿轮 → 齿顶圆柱+键槽 |
| `"springs" in cat` | `gen_spring` | 弹簧 → 螺旋管简化 |
| `"shafts" in cat` | `gen_shaft` | 阶梯轴 → 多段圆柱拼接 |
| `"valves" in cat` | `gen_valve` | 阀门 → 阀体+手轮+法兰 |
| `"pipe" in cat or "fittings" in cat` | `gen_pipe_fitting` | 管件 → 弯头/三通/变径 |
| `"HW" or "TANK" in key` | `gen_ras_device` | RAS设备 → 精确实体+接管 |
| `"steel"/H型钢/角钢/C型` | `gen_steel_section` | 型材 → H/角/C/RHS |
| 其他 | `gen_box_generic` | 兜底 → 简单Box |

**所有生成器签名统一为 `gen_xxx(part, key)` 双参数**，key 用于判断设备子类型（如区分 TANK vs HW）。

**快速验证**：
```bash
export PATH="$HOME/.local/bin:$PATH"
uvx --from vibecad python3 -c "
from vibecad.runtime import installer, status
inst = installer.RuntimeInstaller()
print('Ready:', inst.is_ready())
"
```

**自管 FreeCAD CLI 可用**：
```bash
~/Library/Application\ Support/VibeCAD/runtime/mamba/envs/vibecad/bin/freecadcmd --version
# FreeCAD 1.1.0 Revision: 20260325
```

### VibeCAD 安装坑

- **GitHub 不可直连**：git clone 和 curl 到 github.com 均超时/403，用 `ghfast.top` 镜像下载 release tarball
- **`direct_url.json` 缺失**：managed runtime 的 pip install 后 dist-info 缺此文件，`vibecad --freecad` 报 `installed server package identity is invalid`。手动创建修复（脚本见 `references/vibecad-mcp.md`）
- **macOS FreeCAD.app 不被承认**：仅支持 FreeCAD 1.1.3 指纹版，其他版本需用 `vibecad --freecad` 管理运行时（已就绪）
- **FreeCAD GUI 需桌面环境**：`vibecad --freecad` 启动 GUI 需要 macOS 窗口会话，终端/SSH 中会挂起。MCP server 模式（`mcpb_entry.py`）可在无 GUI 下工作

```bash
export PATH="$HOME/.local/bin:$PATH"
vibecad --freecad  # 启动管理运行时（首次下载 ~2-3GB）
```

```python
# 用户说 "生成一个直径50mm高100mm的圆柱体"
import cadquery as cq
import json

def cad_from_natural_language(description: str):
    # 解析描述（可用 LLM 提取参数）
    # 例如 GPT 提取: {"type": "cylinder", "diameter": 50, "height": 100}
    params = parse_description(description)
    
    if params["type"] == "cylinder":
        result = cq.Workplane("XY").circle(params["diameter"]/2).extrude(params["height"])
    elif params["type"] == "box":
        result = cq.Workplane("XY").box(params["x"], params["y"], params["z"])
    
    cq.exporters.export(result, "/tmp/output.step")
    return "/tmp/output.step"
```

## 限制说明
- SolidWorks COM API 需要 **Windows + SolidWorks 许可证 + pywin32**
- 当前环境是 macOS → 只能用 CadQuery / FreeCAD / OpenSCAD
- **2026-07-08 更新**：旺财（wangcai）已部署在 Windows PC 上，可使用 SolidWorks COM API
  - 详细指南见技能 `wangcai-cad`（GitHub 仓库 yuxin-skills）
  - 旺财的工作流：Codex CLI 生成 CadQuery/SolidWorks 代码 → Hermes 调度执行
- 毛豆和老莫继续在 macOS 上用 CadQuery 做概念验证/参数化设计

## ## 理论知识层（L1）

在技能层之上：告诉 Agent "该画什么、为什么"。4 分类：standards/materials/design/domain。
详见 `references/cad-knowledge-layer.md`。

## 陷阱：不要假完成

说"完成"前必须全链路验证：curl 后端 → curl 代理 → EventSource → DOM 渲染。

### SSE + Vite 代理缓冲陷阱

Vite dev server 默认缓冲代理响应，导致 SSE 事件不实时到达。
**修复**：`vite.config.ts` 中 proxy 加 `configure` 回调，检测 `text/event-stream` 响应头：
```ts
proxy: {
  '/api': {
    target: 'http://127.0.0.1:8002',
    changeOrigin: true,
    configure: (proxy) => {
      proxy.on('proxyRes', (proxyRes) => {
        if (proxyRes.headers['content-type']?.includes('text/event-stream')) {
          proxyRes.headers['cache-control'] = 'no-cache';
        }
      });
    },
  },
},
```

### EventSource 闭包陷阱

SSE 正常完成后会触发 `error` 事件（readyState=0），error 处理器如果闭包捕获了旧的 `liveDone=false`，会覆盖成功状态显示错误。
**修复**：用 `useRef` 而非 `useState` 追踪完成状态：
```ts
const doneRef = useRef(false);
es.addEventListener('error', () => {
  if (!doneRef.current) setError('连接中断');
  es.close();
});
// 在 done 事件中:
doneRef.current = true; setLiveDone(true);
```

### browser_click 不触发 React onClick

自动化工具 `browser_click` 发送原生 DOM click，React 合成事件可能不响应。
**修复**：按钮加 `onMouseDown` 兜底 + 用 `element.click()` 从 console 验证。

### FreeCAD GUI 不在 uvicorn 中打开

macOS GUI 应用需要主线程 NSApplication 事件循环，不能在 uvicorn 后台线程中打开。
**方案**：独立运行 `freecad_gui_bridge.py`（HTTP server on 9876），web 后端 gui=1 时转发到桥接。

### 陷阱：f-string 双大括号（生成 FreeCAD 脚本时）

当用 Python f-string 生成 FreeCAD Python 脚本时，FreeCAD 层面的变量必须用双大括号 `{{var}}` 转义，否则 Python 的 f-string 会尝试在自己的上下文中求值，导致 `NameError`。

**错误示例**（FreeCAD 的 `x` 被 Python 当成自己的变量）：
```python
code = f'''
for x in [0, L-30]:
    cap.Label = f"端盖{'进' if x==0 else '出'}"  # ❌ Python sees {x}
'''
```

**正确示例**（FreeCAD 变量双大括号转义）：
```python
code = f'''
for x in [0, L-30]:
    cap.Label = f"端盖{{'进' if x==0 else '出'}}"  # ✅ double-braced
    pipe = cylinder(f"Cap_{{x}}", r, h, (x, 0, 0))  # ✅ {{x}}
'''
```

**规则**：任何在 FreeCAD 脚本中定义/使用的变量（循环变量 `i`, `x`, `angle` 等），在 Python f-string 中必须写成 `{{var}}`。Python 参数值（如 `{p['壳体外廓L']}`）保持单大括号。print 语句中的 f-string 同样适用：`print(f"DIMS:{{L}}x{{W}}")`。

## 技能库分类（8大类别）

训练平台产出 8 类 Skills，按类别存放于 `skill_library/{category}/`：

| 类别 | 目录 | 说明 | 素材来源 |
|------|------|------|----------|
| bridge | skill_library/bridge/ | 连接不同CAD软件 | API文档 |
| control | skill_library/control/ | 原子操作序列 | 教程视频 |
| operate | skill_library/operate/ | RAS/钢结构完整流程 | 设计案例 |
| rules | skill_library/rules/ | GB/T标准规范 | 标准文档 |
| templates | skill_library/templates/ | 可复用图纸模板 | 模板文件 |
| principles | skill_library/principles/ | 材料属性+设计原则 | 教材/手册 |
| workflows | skill_library/workflows/ | 质检闭环工作流 | 内部流程 |
| analysis | skill_library/analysis/ | 图纸深度解析 | DXF/DWG数据集 |

## 三大库结构

项目目录下三个核心库：
- `material_library/` — 素材库（用户存入 + 系统自动采集），子目录：dxf/video/standards/cases/templates
- `training_database/` — 训练数据库（AI 解析产出），子目录：parsed/pairs/datasets/reports
- `skill_library/` — 技能库（训练最终产出），按 8 类组织

素材采集详情见 `references/material-collection-pipeline.md`。

## 质检闭环 Workflow Skills

Agent 制图必须走闭环，不达标不交付：

```
接收指令 → quality_pre_draw_check  (分析→拆分→选技能→查标准)
         → 执行 control skills 画图
         → quality_post_draw_check (15维评分 → 修正建议)
         → quality_auto_fix_loop   (达标? 交付 : 修正→再检查→循环)
```

3 个 workflow skills 位于 `skill_library/workflows/`：
- `quality_pre_draw_check` — 7步：分析需求→拆分任务→验证输入→选技能→查材料→查标准→生成执行计划
- `quality_post_draw_check` — 6步：评分→图层合规→尺寸完整性→标准合规→修正建议→达标判定
- `quality_auto_fix_loop` — 6步：执行→检查→评估→修正→再检查→循环或交付

评分标准：≥95 优秀直接交付，80-94 合格自动修正，<80 重新执行。

## 毛豆 Agent 集成

毛豆（出图智能体训练师）直接读取 `skill_library/` 学习技能，操控 FreeCAD 执行制图测试。Profile 位于 `~/.hermes/profiles/maodou/`。

## 已训练技能（14个，4类）

| 类别 | 技能 | 步 |
|------|------|----|
| control | freecad_create_box | 4 |
| control | freecad_create_cylinder | 4 |
| control | freecad_create_pipe_joint | 7 |
| rules | gbt_4458_mechanical | 8规则 |
| rules | gb_50017_steel | 7规则 |
| principles | sus304 / q355b / dfm_welding / tolerance_fit | 材料+设计原则 |
| workflows | pre_draw_check / post_draw_check / auto_fix_loop | 质检闭环 |
| operate | ras_aquaculture | RAS设备规范 |

## 技能库团队分发（GitHub 私仓自动同步）

出图训练平台产出的技能需定期同步到公司 GitHub 私仓，供旺财、毛豆等同事学习。

### 同步脚本

脚本位置：`/Users/hua/6-产品研发/22-出图智能体训练/sync_skills_repo.sh`
详见 `references/skill-library-github-sync.md`。

逻辑：每小时 cron → clone/pull `yuxin-skills` → 对比 `skill_library/*.json` → 有变化则 commit + push 到 `drawing-skills/` 子目录。

```
skill_library/ (源)  →  yuxin-skills/drawing-skills/ (目标，GitHub 私仓)
```

关键点：
- 使用 SSH (`git@github.com:openclaw-cn-dev/yuxin-skills.git`)，不依赖 token
- `cmp -s` 做文件级 diff 判断是否需要更新
- README 自动生成，含技能分类目录

### Cron 配置

```bash
hermes cron create \
  --name "🔒 出图技能库同步到 GitHub 私仓" \
  --schedule "every 60m" \
  --prompt "Run: bash /Users/hua/6-产品研发/22-出图智能体训练/sync_skills_repo.sh" \
  --deliver origin
```

### 同事使用

```bash
git clone git@github.com:openclaw-cn-dev/yuxin-skills.git
cd yuxin-skills/drawing-skills/
# 每次开工前
git pull
```

### 陷阱：不要新建仓库

公司已有 `yuxin-skills` 私仓，所有 Agent 技能统一存放。新增技能类别时在仓库内建子目录（如 `drawing-skills/`），**不要新建独立仓库**——避免分散管理。

## 旺财自学指令

让旺财自学出图技能的 prompt：

```
旺财，你的出图技能库在公司私仓：
git clone git@github.com:openclaw-cn-dev/yuxin-skills.git
进去看 drawing-skills/，14个技能 JSON 按分类存放。

每个 JSON 标注 {id, name, tool, inputs, steps, output}。你的工作流：
1. 接到出图任务 → 去 drawing-skills/ 找匹配的 skill
2. 按 inputs 填参数，按 steps 逐步执行（CadQuery/ezdxf/SolidWorks COM）
3. 出图后跑 workflows/ 里的质检流程（画后评测 ≥ 80 分才交付）
4. 输出 STEP + DXF + 质检报告 三件套
5. 训练平台出新 skill 会每小时自动推送到这个仓库，每次开工前先 git pull
```

## 相关资源
- CadQuery GitHub: https://github.com/CadQuery/cadquery
- pythonocc-core: https://github.com/tpaviot/pythonocc-core
- ezdxf: https://github.com/mozman/ezdxf
- wangcai-cad (Windows SolidWorks 指南): GitHub openclaw-cn-dev/yuxin-skills
- **🆕 逆向工程配套**：`references/pdf-reverse-engineering-v0.1.1.md` — 从 PDF 工程图提取设备规格的 v0.1 → v0.1.1 升级 6 步 SOP（覆盖 20% → 95%）。2026-09-04 毛豆 cron 实测 HW-001~008 v241 8 设备。配套 `reverse_extract_v0_1_1.py` 可重跑。

## 技能驱动 CAD 架构（v2 — 当前生产方案）

**核心理念**：不直接生成 DXF，而是 **训练技能 → Agent 学习技能 → 加载技能操控真实 CAD 软件**。用户只需描述需求，Agent 自动选技能、填参数、操控 CAD 出图。

### 架构层次

```
skill_library/*.json    ← 技能定义（JSON格式，声明 inputs/steps/tool)
       ↓
skill_executor.py       ← 加载→解析$param→逐步调用CAD桥接→on_step推送
       ↓
cad_bridge.py           ← FreeCAD/CadQuery/ezdxf 统一桥接（17个原子操作）
       ↓
FreeCAD Python API      ← 实际操控 CAD
       ↓
STEP/STL/FCStd          ← 3D模型输出
```

### 技能定义格式

```json
{
  "id": "freecad_create_pipe_joint",
  "name": "管道连接件", "tool": "freecad",
  "category": "ras_design",
  "inputs": {"pipe_diameter": 110, "pipe_length": 300, "flange_diameter": 200},
  "steps": [
    {"action": "new_document", "params": {"name": "PipeJoint"}},
    {"action": "create_cylinder", "params": {"radius": "$pipe_diameter", "height": "$pipe_length"}},
    {"action": "create_cylinder", "params": {"radius": "$flange_diameter", "height": "$pipe_thickness"}},
    {"action": "fuse", "params": {"obj1": "Pipe", "obj2": "Flange"}},
    {"action": "export", "params": {"obj_name": "PipeJoint", "fmt": "step"}}
  ],
  "output": "step, stl"
}
```

- `id` — 唯一标识，文件名 = `{id}.json`
- `$param` — 变量引用，执行时替换为用户实际输入
- `steps[].action` — 对应 `cad_bridge.py` 中的方法名
- `tool` — `freecad` | `cadquery` | `ezdxf`

### 可用 CAD 原子操作

| action | tool | 说明 |
|--------|------|------|
| `new_document` | freecad | 新建文档 |
| `create_box/cylinder/sphere/cone/torus` | freecad | 基础体创建 |
| `fuse` / `cut` | freecad | 布尔操作 |
| `export` | freecad | 导出 STEP/STL/FCStd |
| `cq_create_box` | cadquery | CadQuery 方体 |
| `dxf_new/add_rect/save` | ezdxf | 2D DXF 操作 |

### 技能执行 SSE 流

```python
# 后端 — 通过 Queue+Thread 桥接同步执行与异步 SSE
executor = SkillExecutor(tool="freecad", on_step=lambda s: queue.put(s))
executor.execute("freecad_create_pipe_joint", {"pipe_diameter": 55}, output_dir)
```

### 训练管线

```
素材上传(DXF/视频) → AI解析 → 生成技能定义JSON → 保存到skill_library
→ Agent学习 → 执行验证 → 评分 → 入库
```

详见 `references/cad-skill-system.md`。

**关键可复用模式：**

1. **自进化 improvement_hints 反馈循环** — Agent 生成图纸 → 评分 → 分析薄弱规则 → 生成 hints dict → 注入下一迭代 Agent。适用于任何"生成→评估→优化"场景。
2. **多领域 step 编号陷阱** — 当不同领域有不同数量的子操作时，必须先数清步骤数再分配槽位，否则会出现 step 编号冲突。
3. **工具操作型 Agent 设计** — 每个 Agent 动作对应工程师真实操作（tool_draw_rect、tool_draw_bolt_group 等），日志完整可审计。这种模式比一次性生成整个文件的"黑盒"方式更适合工程场景。
4. **SSE 实时画图流 — 工具操作型 Agent 的正确架构**

**核心原则**：智能体必须逐个调用工具（`tool_draw_rect`、`tool_draw_line` 等），每调一个工具就推送一个事件。用户要看到的是智能体操控工具的**过程**，而不是黑盒等待最终结果。

**实现模式（Python 后端）：**

```python
# ① 给 Agent 加 step_callback — 每完成一步立刻回调
class DrawingAgent:
    def __init__(self, device_id, step_callback=None):
        self.step_callback = step_callback

    def log_step(self, step, name, status, details=None):
        result = {"step": step, "name": name, "status": status, "details": details}
        if self.step_callback:
            self.step_callback(result)  # ← 实时推送
        return result

# ② SSE 端点用 Queue + Thread 桥接同步 Agent 与异步 FastAPI
from queue import Queue
from threading import Thread

def _sync_worker(queue, device_id):
    def on_step(info): queue.put({"type": "step", ...})
    agent = DrawingAgent(device_id, step_callback=on_step)
    agent.run_full_flow(output_path)
    queue.put({"type": "done", ...})

async def _stream(queue):
    loop = asyncio.get_event_loop()
    while True:
        item = await loop.run_in_executor(None, queue.get, True, 0.5)
        yield f"data: {json.dumps(item)}\n\n"
        if item["type"] in ("done", "error"): break

@router.get("/live/draw")
async def live_draw(device_id: str = Query(...)):
    queue = Queue()
    Thread(target=_sync_worker, args=(queue, device_id), daemon=True).start()
    return StreamingResponse(_stream(queue), media_type="text/event-stream")
```

**前端（React）**：用浏览器原生 `EventSource` API，`useRef` 防闭包陷阱（详见 `react-vite-patterns` §7）。

**反模式**：先跑完 `run_full_flow` 拿到所有 steps，再 `await asyncio.sleep(0.15)` 逐条 yield — 这是假流式，用户看不到真实过程。

## 工具实施层指针：VibeCAD + FreeCAD（curator 合并 2026-10-16 · 原 vibecad-freecad 整档收纳）

本 skill 是 CAD 方法论/战略层；VibeCAD + FreeCAD 的工具级实操已合并至 `references/vibecad-freecad/`（原独立 skill；现 SKILL.md 为 2026-09-12 v1.3 快照恢复版 + RECOVERY 恢复说明——原包 14 个支持文件中 7 个 references 与 4 个 templates/scripts 因整理工具链误删损毁，待按恢复说明考古重建；其「DXF 质量评分器」「Part.export 导出坑」两主题在本 skill 已吸收章节另有覆盖）。出图执行问题先读 `references/vibecad-freecad/SKILL.md`；本 skill 出的参数化模板与零件库决策在那边落地。
