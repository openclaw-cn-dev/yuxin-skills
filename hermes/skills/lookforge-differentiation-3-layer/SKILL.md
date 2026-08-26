---
name: ***SECRET***
description: 'LookForge环节7「差异化路径」的3层规则架构设计方法论 — 把产品系列+客户细分+商业目标映射到 phase_orchestrator 的 skip_stages/weights/key_apis/deliverables。覆盖设备厂/养殖场/投资人/政府 4 类买家 × 渔芯装/RAS/鱼晓/定制 4 个产品系列 × LTV/CAC/NRR 3 个商业目标触发条件。触发条件：华哥/玉芬要求"做差异化"、"产品系列细分"、"客户分层"、设计/扩展 phase_orchestrator._build_differentiation_rules()、为新客户类型配置 LookForge 流程路径。'
license: MIT
metadata:
  author: 渔芯科技
  version: "0.1.0"
---

# LookForge 环节 7「差异化」3 层规则架构

> **来源**：2026-08-26 毛豆自我进化设计，待 Claude Code 实施（工时 ~6h）

## 一、问题背景

`backend/app/orchestrators/phase_orchestrator.py:1592` 的 `_build_differentiation_rules()` 当前只有 4 大产品系列（渔芯装/RAS/鱼晓/定制）的粗粒度规则 ——

```python
"渔芯装系列": {"skip_stages": ["stage_simulation"], "timeline": "4-8周", ...},
"RAS系统": {"skip_stages": [], "timeline": "3-6个月", ...},
"鱼晓系列": {"skip_stages": [], "timeline": "1-3个月", ...},
"定制项目": {"skip_stages": [], "timeline": "按需", ...}
```

**3 个不足**：
1. ❌ 只按"产品系列"分，**未按"客户细分"分**（设备厂/养殖场/投资人/政府 JTBD 完全不同）
2. ❌ skip_stages 是布尔（跳过/不跳过），**缺少权重**（"部分简化" vs "全量做"）
3. ❌ cost_target 只有金额范围，**未与 LTV/CAC/NRR 商业目标联动**

## 二、3 层规则架构

```
Layer 1: 产品系列层（已有，扩展）
  ├─ 渔芯装 / RAS / 鱼晓 / 定制
  └─ 决定 timeline + cost_target + cert_requirements

Layer 2: 客户细分层（核心新增）
  ├─ 设备厂技术总监 / 养殖场主 / 投资人 / 政府监管
  └─ 决定 weights（仿真/工艺/测试/Phase7 权重）+ skip_stages + key_apis

Layer 3: 商业目标层（核心新增）
  ├─ LTV ≥ ¥100k / CAC ≤ ¥5k / NRR ≥ 120% / 首单转付费
  └─ 决定 Phase 7 输出权重 + 报价策略 + SLA
```

## 三、客户细分映射表（Layer 2 核心）

| 客户类型 | skip_stages | weights | cost_target | 重点 API | 交付物 |
|---------|-------------|---------|-------------|---------|--------|
| **设备厂技术总监** | 不跳过 | simulation=2.0, craft=1.5, test=1.5 | 50-200万 | /simulation/run, /fluid/calc/* | BOM + 3D模型 + 工艺SOP + 测试报告 |
| **养殖场主** | skip_simulation（用现成模板）| simulation=0.0, craft=1.0, test=1.0 | 1-30万 | /craft/run, /ras/bom | 安装SOP + 维护手册 |
| **投资人** | 不跳过 | phase7=2.0, simulation=1.0 | 100万+ | /phase7 | ROI测算 + LTV/CAC模型 + TAM/SAM |
| **政府监管** | 不跳过 | test=2.0, cert=2.0 | 50-500万 | /test/run, /cert/check | 检测报告 + 环保达标证明 |

## 四、商业目标触发规则（Layer 3）

| 商业目标 | 触发条件 | 差异化动作 |
|---------|---------|-----------|
| **高 LTV** | 单客年消费 ≥ ¥100k | Phase 7 输出 ROI 测算 + 7×24 SLA |
| **低 CAC** | 新客获取成本 ≤ ¥5k | Phase 4 模板化 + Phase 6 套用预置 |
| **高 NRR** | 续约/扩展率 ≥ 120% | 仿真用例持续升级 + AI 训练数据回流 |
| **首单转付费** | 试用期转化 | 限时功能解锁 + LookForge 试用码 |

## 五、建议数据结构

```python
{
  "产品系列层": {  # 已有，扩展 cost_target 数值范围
    "RAS系统": {"timeline": "3-6月", "cert": ["CCC","CE"], "cost_range": [50, 200]}
  },
  "客户细分层": {  # ★ 新增整层
    "设备厂": {
      "weights": {"simulation": 2.0, "craft": 1.5, "test": 1.5},
      "skip_stages": [],
      "key_apis": ["/simulation/run", "/fluid/calc/*"],
      "deliverables": ["BOM", "3D模型", "工艺SOP", "测试报告"]
    },
    "养殖场": {
      "weights": {"craft": 1.0, "test": 1.0},
      "skip_stages": ["stage_simulation"],
      "key_apis": ["/craft/run", "/ras/bom"],
      "deliverables": ["安装SOP", "维护手册"]
    },
    "投资人": {
      "weights": {"phase7": 2.0, "simulation": 1.0},
      "key_apis": ["/phase7"],
      "deliverables": ["ROI测算", "LTV/CAC模型", "TAM/SAM"]
    },
    "政府": {
      "weights": {"test": 2.0, "cert": 2.0},
      "key_apis": ["/test/run", "/cert/check"],
      "deliverables": ["检测报告", "环保达标证明"]
    }
  },
  "商业目标层": {  # ★ 新增整层
    "高LTV": {"trigger": "LTV>=100k", "action": "Phase7_SLA"},
    "低CAC": {"trigger": "CAC<=5k", "action": "模板化Phase4"},
    "高NRR": {"trigger": "NRR>=120%", "action": "AI升级包"}
  }
}
```

## 六、实施清单（Claude Code ~6h）

| # | 任务 | 文件 | 优先级 |
|---|------|------|--------|
| 1 | 重构 `_build_differentiation_rules()` 为 3 层数据结构 | phase_orchestrator.py:1592 | P0 |
| 2 | 新增 `customer_segment` 字段到 Project 模型 | domain.py + db.py | P0 |
| 3 | 新增 `business_target` 字段到 Project 模型 | domain.py + db.py | P0 |
| 4 | 联调：run_phase6 末尾按 customer_segment 调用差异化 API | phase_orchestrator.py:1310 | P0 |
| 5 | 前端 Phase 6 spec 展示客户细分选项 | frontend Phase 6 页面 | P1 |
| 6 | 写 4 类买家各 1 个端到端测试 | tests/ | P1 |

## 七、JTBD 4 类买家 → LookForge API 映射

来自 `evolution/jtbd-yuxinzhuang-framework-v0.1.md`（8/23 已建）：

| 买家类型 | JTBD 核心 | 重点 LookForge API | 备注 |
|---------|-----------|-------------------|------|
| **设备厂技术总监** | "投标现场证明能跑多大规模" | simulation + fluid_engine + craft | weights 2.0 仿真 |
| **养殖场主** | "降 30% 死亡率，不愿买贵硬件" | craft（简版）+ BOM | skip_simulation |
| **投资人** | "量化 RAS 项目 ROI" | phase7 + simulation | phase7 权重 2.0 |
| **政府监管** | "可追溯环保达标证据" | test + cert | test 权重 2.0 |

## 八、行业趋势对齐（2026 年 8 月）

| # | 趋势 | 渔芯装机会 | LookForge 能力映射 |
|---|------|-----------|-------------------|
| 1 | AI 行为监控（CV 早期预警） | HW-012 加装水下摄像头 | Phase 6 仿真 + Phase 3 创意 |
| 2 | Digital Twin 数字孪生 | HW-001~018 设备库升级为实时孪生 | Phase 6 fluid_engine + RAS 设备库 |
| 3 | IoT 实时监测 | 渔芯装设备标配 4G 模组 | Phase 1 + Phase 7 |
| 4 | RAS 专用饲料配方 | SaaS "鱼种→饲料→投喂量" | Phase 2 + ras_species_params |
| 5 | 垂直整合（设备+养殖+销售）| 渔芯装 = "养殖方案商" | Phase 7 商业计划升级 |

## 九、避坑提示

1. **铁律 #1 优先**：本技能是设计方法论，**不写代码**。实施必须走 Claude Code / Codex
3. **weights 是相对值，不是绝对值**：weights 是该买家类型相对其他环节的重要度，跨客户类型才有意义
4. **skip_stages 不是永久跳过**：养殖场主跳过 simulation，但 Phase 7 商业计划应包含仿真结果摘要
5. **cost_target 是参考值**：实际报价按 Phase 7 LTV/CAC 计算后的折扣策略调整
6. **与 Phase 7 联动**：LTV ≥ ¥100k 触发 SLA → Phase 7 需新增 `service_level` 字段

## 十、相关文件

- 设计源：`~/.hermes/profiles/maodou/evolution/2026-08-26_00.md` §五（核心）
- 现有代码：`/Users/hua/6-产品研发/渔芯科技/06-硬件项目开发/backend/app/orchestrators/phase_orchestrator.py:1592`
- JTBD 框架：`~/.hermes/profiles/maodou/evolution/jtbd-yuxinzhuang-framework-v0.1.md`
- 上期报告：`~/.hermes/profiles/maodou/evolution/2026-08-25_16.md`（环节 4-5 工艺+测试完成）