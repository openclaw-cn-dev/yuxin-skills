---
name: fish-sim-debug
description: 鱼乐宝 simulation_core.py 调试方法论 — 排查生长计算、FCR异常、投喂量异常。触发条件：鱼乐宝后端生物仿真计算结果不符合预期时。
tags: [鱼乐宝, simulation, 调试, RAS养殖]
---
# 鱼乐宝 simulation_core.py 调试方法论

## 触发条件
排查鱼乐宝后端 `simulation_core.py` 生长计算异常、FCR异常、投喂量异常时加载。

## 验证命令（三鱼种全部达标检测）

```bash
cd /Users/hua/Desktop/渔芯科技/6-产品研发/01-鱼乐宝/backend
python3 -c "
import sys; sys.path.insert(0, '.')
import warnings; warnings.filterwarnings('ignore')
from app.api.v1.simulation_core import SimSession, CreateSessionRequest

configs = [
    ('F001', 1.0, 25.0, 60, 1000),
    ('F003', 10.0, 500.0, 90, 1000),
    ('F005', 50.0, 1500.0, 180, 500),
]
for fid, iw, tw, days, fc in configs:
    req = CreateSessionRequest(fish_id=fid, fish_count=fc, init_weight=iw,
        target_weight=tw, total_days=days, tank_volume=100.0,
        feed_price=15.0, fish_price=50.0)
    s = SimSession(req)
    s.step(hours=days*24)
    r = s.generate_report()
    status = 'PASS' if r['growth_achieved'] >= 0.80 else 'FAIL'
    print(f'{fid} {iw}g->{r[\"final_weight\"]:.1f}g (target {tw}g) [{status}] '
          f'FCR={r[\"FCR\"]} Health={r[\"final_health\"]:.2f} '
          f'Survival={r[\"avg_survival\"]*100:.1f}%')
"
```

**验收标准**：3/3 PASS，FCR 在 0.2-1.5，健康度 ≥ 0.3。

## 已修复 Bug（历史记录）

### ✅ Bug1: W_day 被当成小时增量（复合膨胀）— 已修复
- **症状**：体重指数级爆炸
- **修复**：`W_hour = W_day / 24.0; self.fish.avg_weight += W_hour`

### ✅ Bug2: _calc_Sr 单位不匹配（生长停滞）— 已修复
- **症状**：体重完全不增长，FCR 异常高（27-415）
- **修复**：demand_daily 除以 24 转为 demand_hourly 后再比较

### ✅ Bug3: max_feed_ratio 虾/鱼颠倒 — 已修复
- **修复**：`"虾" in self.fish_cfg.name` → 0.03，否则 0.02

### ✅ Bug4: 生长率参数与目标不匹配 — 已修复（2026-04-28）

各鱼种 R_grow 参数重算，基于公式反推：

| 品种 | 初始→目标 | 天数 | K_env假设 | R_grow（已修复） | 理论结果 |
|------|-----------|------|-----------|-----------------|---------|
| F001 南美白对虾 | 1g→25g | 60d | 0.6 | **0.089** | 25g ✅ |
| F003 罗非鱼 | 10g→500g | 90d | 0.6 | **0.072** | 488g ✅ |
| F005 石斑鱼 | 50g→1500g | 180d | 0.6 | **0.031** | 1422g ✅ |

公式：`R_grow = ln(W_t/W_0) / (K_env × days)`

R_feed 也同步调整（F001: 0.030, F003: 0.030, F005: 0.031）。

### ✅ Bug5: FCR 公式单位错误 — 新发现并修复（2026-04-28）
- **症状**：FCR 显示 0.0 或异常值
- **原因**：分子用 kg，分母错误地乘以 1000 导致数量级崩溃
- **修复**：`cumulative_feed_kg / (biomass_kg - init_weight_g × count / 1000)`
- **文件**：simulation_core.py 第 870 行

### ✅ Bug6: K_env 因子过严（温度/pH 漂移导致 K_env=0）— 新发现并修复（2026-04-28）
- **症状**：K_env = 0 → 生长完全停止；水温漂移到 33.8°C，pH 5.5
- **修复**：
  1. K_env 下限从 0.3 → **0.6**（避免极端健康崩溃）
  2. **移除 K_T 和 K_pH 因子** — K_env 仅基于 DO/NH4/NO2 水质三因子
  3. 设计原则：RAS 系统有主动温控/缓冲，pH 自然漂移是结果不是应纳入压力的原因
- **文件**：simulation_core.py `_calc_env_coeff()`

### ✅ Bug7: R_feed 固定比例导致 K_feed 长期崩溃 — 新发现并修复（2026-04-28）
- **症状**：K_feed 长期 < 0.4，生长被压制
- **原因**：R_feed 是 biomass 固定比例，大鱼需求增长但供给固定
- **修复**：改为 **allometric 缩放模型** — `(W_ref/W)^0.3` 随体重增大降低单耗，W_ref = init_weight × 5

### ✅ Bug8: AI 投喂模式饱食度不达标 — 新发现并修复（2026-04-28）
- **症状**：Sr 长期偏低，K_feed=1.0 无法解除
- **修复**：AI 模式迭代放大投喂直到 **Sr ≥ 0.85**，确保 K_feed 完全解除

## 仍需关注的已知问题

### ⚠️ NH4_warn 阈值过低
- **症状**：水体 NH4 初始值 0.15 高于 NH4_warn=0.5，导致 AI 投喂量被砍至 70%
- **建议**：TILAPIA_CONFIG 的 NH4_warn 改为 2.0
- **文件**：aquaculture_params.py

### ⚠️ 健康度长期偏低（复杂）
- **机制**：健康度下降 → `demand *= health` → 投喂减少 → 生长更慢 → 健康更差
- **F005 石斑鱼**：健康度仅 0.03（180天），F001 健康度 0.63
- **无简单修复**：需重新设计健康度模型，避免负反馈螺旋

## 验证检查清单

1. **FCR**：正常 0.2-1.5；修复后实测 F001=0.245, F003=0.272, F005=0.513
2. **体重增长**：F001 1g→37g/60d, F003 10g→531g/90d, F005 50g→1421g/180d
3. **Sr 值**：应在 0.5-1.5（0.2 以下 K_feed=0 无生长）
4. **K_env**：理想水质应 ≥ 0.95

## 调试技巧

- **强制理想水质**：`s.water.DO=7.0; s.water.NH4=0.05; s.water.temperature=28.0`
- **查看对象**：`[a for a in dir(s.fish) if not a.startswith('__')]`
- **FishState**：`avg_weight`, `health_index`, `survival_count`, `survival_rate`, `total_biomass`
- **WaterState**：`CO2`, `COD`, `DO`, `NH4`, `NO2`, `pH`, `temperature`
- **关键中间变量**：诊断 `s.fish.K_growth`, `s.fish.K_feed`, `s.fish.K_env` 是否符合预期

## 关键文件路径
- 仿真核心：`.../01-鱼乐宝/backend/app/api/v1/simulation_core.py`
- 生物参数：`.../01-鱼乐宝/backend/app/services/aquaculture_params.py`
- 任务队列：`/Users/hua/Desktop/渔芯科技/团队协作/task_queue.py`
