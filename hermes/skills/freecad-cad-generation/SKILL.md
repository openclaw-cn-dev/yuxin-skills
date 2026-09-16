---
name: freecad-cad-generation
description: AI 驱动的 CAD 工程图自动生成 — LLM 生成 CadQuery/FreeCAD Python 脚本 → 输出 STEP
license: MIT
metadata:
  author: 渔芯科技
  version: "1.1"
---

# freecad-cad-generation

> ⭐ 此 SKILL.md 在 skill_manage 元数据里被覆盖为占位符,原始正文留在 maodou profile 磁盘上。请直接读 `~/.hermes/profiles/maodou/skills/hardware/freecad-cad-generation/SKILL.md` 获取完整内容。

## 📚 References(由 skill_manage 维护)

- `references/hw-batch-pipeline.md` — HW 设备批量出图编排模式(规格库 hw_specs.json + gen_all_hw.py,v1.0,2026-09-14)
- `references/***SECRET***.md` — **CadQuery 不可用时 FreeCAD Part 备份路线**(2026-09-14 HW-002 S + HW-003 L 双复杂度实测 + 完整 worked example + 验收标准 + 复杂度覆盖矩阵)
- `templates/gen_hw_l_complexity_freecad.py` — **HW 设备 L 复杂度几何模板**(矩形箱 + 多部件融合 + 法兰/筛孔阵列,适用 HW-005/006/008/010 等,2026-09-14 HW-003 抽象)
