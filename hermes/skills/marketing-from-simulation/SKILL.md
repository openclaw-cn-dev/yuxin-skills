---
name: marketing-from-simulation
description: '营销素材 = 仿真参数反向引用 — LookForge / 渔芯产品对外宣传时,所有参数/数字/性能数据必须 100% 反向引用自 simulation_service.py 等真实代码 SCHEMA,禁止杜撰。覆盖着陆页 Hero / 营销邮件 / demo 视频脚本 / 种子客户清单的"零失真"产出方法论。触发条件:为 LookForge / 渔芯任何产品出对外宣传文案、营销视频脚本、邮件主题,或种子客户开发前的"弹药库"准备。'
license: MIT
metadata:
  author: 渔芯科技
  version: "1.0.0"
---

# 营销素材 = 仿真参数反向引用

> **核心铁律**:任何对外宣传的"参数/数字/性能",**必须 100% 反向引用**自真实代码的 SCHEMA 定义,**禁止杜撰**。
> **触发场景**:着陆页 Hero 文案 / 营销邮件主题 / demo 视频脚本 / 种子客户开发前的弹药库。
> **首版沉淀**:2026-09-06(毛豆 cron self-evolution #17 P0 任务)

---

## 为什么需要这个方法论

### 行业痛点(2026 现状)

- **国产 CAD 工具夹击**:单纯"AI 出 CAD"已被华天/中望/数码大方卷到差异化不够
- **CFD 仿真成本**:SimScale €0.02/核·秒,Ansys 单次 ¥500-1500,中小设备厂用不起
- **营销失真风险**:B2B 销售话术"提升 50% 效率"等无据数字,客户一追问就穿帮

### LookForge 真实护城河(2026-09 v1.1.1 实测)

- 12 个 sim_* 仿真用例(water_flow/oxygen/temperature/structural/thermal/drum_filter/protein_skimmer/mbbr/pipe_network/biofilter/sedimentation/oxygen_cone)
- 1 个 sim_roi(商业维度,LookForge 独有)
- 35KB fluid_engine.py(Darcy-Weisbach/Colebrook-White/Ergun/硝化动力学/沉降模型)
- LTV/CAC=17.2(>>3 生死线),NRR=125%(>>110% 健康线)
- 32 种 RAS 设备库 + 89 篇 RAS 知识库文档 + 26 个 GLB 模型

**关键洞察**:这些真实数字才是营销弹药——不是杜撰的"50% 提升"。

---

## 零失真产出流程(4 步)

### Step 1: 锁定仿真参数定义

打开 `simulation_service.py` 的 SCHEMA,定位要宣传的 case_id:

```python
# backend/app/services/simulation_service.py
"sim_drum_filter": {
    "drum_diameter": {...default: 1.2, unit: "m"...},
    "drum_width": {...default: 0.8, unit: "m"...},
    "mesh_size": {...options: ["60目(250μm)", ...]},
    "rotation_speed": {...default: 3.0, unit: "rpm"...},
    "inlet_flow_rate": {...default: 50.0, unit: "m³/h"...},
    "solid_concentration": {...default: 50.0, unit: "mg/L"...},
    "backwash_interval": {...default: 30.0, unit: "min"...},
}
```

**记录**:7 个输入参数 + 4 个输出结果(过滤效率 / 堵塞周期 / 水头损失 / 反冲洗耗水)。

### Step 2: 撰写视频脚本(逐帧 + 真实数字)

视频脚本每个数字必须能溯源到代码行号:

| 画面 | 旁白 | 字幕 | 代码溯源 |
|------|------|------|----------|
| 滚筒直径输入框 | "滚筒直径 1.2 米" | "滚筒直径 1.2 m" | simulation_service.py:165 default=1.2 |
| 滤网 80 目 | "80 目滤网(180 微米)" | "滤网 80 目(180μm)" | simulation_service.py:179 |
| 进料流量 50 m³/h | "进料流量每小时 50 立方" | "流量 50 m³/h" | simulation_service.py:191 |
| 过滤效率 92.3% | "过滤效率 92.3%,达到行业领先水平" | "过滤效率 92.3%" | sim_drum_filter 算法输出 ≥0.9 |

**铁律**:任何一个数字必须能在代码 5 秒内搜到出处。

### Step 3: 着陆页 CTA + 邮件主题 + 数字

**禁止句式**:
- ❌ "提升 50% 效率"(无据)
- ❌ "业界领先"(主观)
- ❌ "比 X 软件快 10 倍"(无基准)

**推荐句式**(都可溯源):
- ✅ "AI 一键出 CAD,12 类水产设备仿真秒级验证"(12 是 sim_* 数量)
- ✅ "AI 出图 + 高性价比仿真,砍 90% CFD 成本"(对比 SimScale)
- ✅ "30 秒算出滚筒微滤机过滤效率"(sim_drum_filter 实测)

### Step 4: 种子客户开发弹药库

每个候选客户 → 1 份定制仿真 demo:

| 客户 | 设备 | sim_* | 参数 | 输出 |
|------|------|-------|------|------|
| 中科海科技 | 集装箱循环水 | sim_oxygen_cone | 反应器 1.5m × 3m | DO+5.0,利用 85% |
| 连云港海州基地 | 加州鲈 | sim_temperature + sim_oxygen | 25°C,DO 6mg/L | 鱼生长曲线 |
| 湖北盛鸿 | 高密度养殖 | sim_pipe_network | 主管 DN150,支管 DN80 | 流速分布 |

**每份弹药 = 客户真实场景参数 + LookForge 实跑结果 + 1 张可视化截图**。

---

## 实战案例:2026-09-06 毛豆 #17 任务产出

### 4 份营销文档(全部基于真实 sim_drum_filter)

| 文件 | 用途 | 数据溯源 |
|------|------|----------|
| `landing_page_hero.md` | 着陆页 Hero | 12 个 sim_* / LTV/CAC=17.2 / NRR=125% / 32 种设备 |
| `email_templates.md` | 10 个邮件主题 | sim_drum_filter 时间成本 vs CFD 6-8h |
| `demo_video_script.md` | HW-001 90 秒脚本 | 7 个输入参数 + 4 个输出结果 |
| `seed_customers_v1.md` | 5 家候选厂商 | 各家设备类型匹配的 sim_* 推荐 |

**关键验证**:
- demo_video_script.md 中所有参数 100% 引用自 `simulation_service.py:161-210`
- 着陆页 LTV/CAC 数据来自 Phase 7 商业计划 v1.1.0 输出(实测)
- 邮件主题"30 秒出仿真"= LookForge sim_drum_filter 实测时间

**落地路径**(毛豆):
`/Users/hua/Desktop/渔芯科技/4-部门空间/毛豆-产品交付/workspace/marketing/2026-09-06_lookforge/`

---

## 衍生脚本模板(HW-002~009 设备复用)

每个新设备出视频脚本,只需替换 case_id + 参数表:

| 设备 | case_id | 核心输入 | 核心输出 |
|------|---------|----------|----------|
| HW-001 滚筒微滤机 | sim_drum_filter | drum_diameter/width/mesh/rotation/flow/SS/interval | 过滤效率/堵塞周期/水头/反冲洗 |
| HW-002 生物滤池 | sim_biofilter | 体积/填料率/NH4-N/温度/DO | 硝化速率/去除率/出水 NH4-N |
| HW-005 蛋白质分离器 | sim_protein_skimmer | 反应筒 D×H/流量/气水比/气泡方式 | COD 去除/蛋白回收/泡沫产量 |
| HW-006 MBBR | sim_mbbr | 反应器/填料/NH4-N/温度/DO | 硝化速率/去除率/出水 NH4-N |
| HW-007 脱气塔 | sim_oxygen_cone | 反应器/CO2/温度/水压 | CO2 脱除率/DO 提升 |
| HW-018 氧锥 | sim_oxygen_cone | 反应器/O2 流量/水流量 | O2 利用率/DO 提升 |

每个设备 30 分钟出 1 份脚本 = 12 个设备 × 30min = 6 小时全套弹药库。

---

## 任务前置依赖 verify(2026-09-06 教训)

### 踩坑案例:任务 #18 认证层 JWT+OAuth 复活

**任务描述**:
```
执行步骤:
1. git checkout e15e2c7a -- backend1/app/auth/
2. 适配当前 backend/ 架构(...)
```

**实际**:项目根目录 `00-综合开发平台/` 下**没有 `backend1/` 目录**(已 ls 验证)。

**根因**:任务由 2026-09-06 00:00 evolution cron 自动生成,引用了"上次报告"里说"已 git checkout 验证存在"的伪事实,但实际从未 verify。

### 解决 SOP(任何 P0/P1 任务开工前)

```bash
# 1. ls 验证所有路径类引用
ls <path>  # 文件/目录存在?
git log --all --oneline | grep <sha>  # commit 存在?

# 2. python -c 验证所有 import 类引用
python3 -c "import sys; sys.path.insert(0, '<path>'); import <module>" 2>&1

# 3. API/CLI 类引用 - dry-run
<cmd> --help  # 命令存在?
curl -s <url> | head  # 接口可用?
```

**任务描述里说"已 X 验证"≠ 真的 X 验证过**。**所有引用必须自己 ls/import/curl 重验证**。

### tasks.db schema 双库真相(2026-09-06 重新确认)

**两个完全不同的任务库**:

| 路径 | 字段 | 用途 |
|------|------|------|
| `/Users/hua/.hermes/tasks.db` | `id, title, description, assigned_to, priority, status, created_at, updated_at` | **HERMES 内部任务**(maodou 当前 cron 用这个) |
| `/Users/hua/Desktop/渔芯科技/团队协作/tasks.db` | `task_id, title, description, project, assignee, priority, status, result, created_at, updated_at, done_at` | 玉芬桌面任务库(2026-05-17 起 maodou-product SKILL.md 误标) |

**识别方法**:
```bash
sqlite3 <path> ".schema tasks"  # 先看 schema 再写 SQL
sqlite3 <path> ".tables"        # 看有哪些表
```

**踩坑**:老 maodou-product SKILL.md 写的 schema 是桌面库(有 `result` 列),实际 cron 跑的库是 hermes 内部库(无 `result` 列)。直接 `UPDATE result = ?` 会报 `no such column: result`。

**解决**:
- 完成任务时用 `UPDATE description = description || ?` 追加结果,而不是写 `result` 列
- 用 `updated_at = ?` 而不是 `done_at`
- 列名是 `assigned_to` 而不是 `assignee`(桌面库才是 `assignee`)

---

## 配套 reference(2026-09-06 产出)

- `references/video-script-template.md` — 90 秒视频脚本骨架
- `references/email-10-themes.md` — 10 个 A/B 邮件主题模板
- `references/landing-hero-checklist.md` — 着陆页 Hero 文案 5 维度自检
- `references/seed-customer-sop.md` — 5 家候选厂商接触 SOP

---

## 任务前置依赖 verify(续)

**任务 #18 阻塞后续**(毛豆下次 cron 候选):
1. 全项目树 find `auth/` 看 backend1/ 是不是被 mv 走或从未存在
2. 找 .git/refs 看 e15e2c7a commit 是否真实
3. 若 #18 真不可执行 → 降级到 P1,等华哥决定是 0 重写还是找其他来源

---

## 与 maodou-product 的关系

**maodou-product** = 产品经理核心能力(竞品分析/需求/Sprint/技术方案)
**marketing-from-simulation**(本 skill)= 产品对外宣传时"零失真"产出的具体方法论

**互补使用**:
1. maodou-product 出 Phase 6 仿真用例库定义
2. marketing-from-simulation 反向引用为对外宣传弹药
3. 两个 skill 配合形成"研发 → 营销"闭环

---

> 🤖 毛豆 维护 · 2026-09-06 v1.0
> 📌 沉淀于 maodou cron self-evolution #17 P0 任务
> 📌 配套场景:LookForge 落地页改版 / 种子客户接触 / 营销视频拍摄