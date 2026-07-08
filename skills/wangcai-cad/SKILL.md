---
name: wangcai-cad
description: 旺财 AI CAD/SolidWorks 出图技能 — 在 Windows 上用 AI 自动生成 CAD 图纸和 3D 模型
version: 1.0.0
author: 渔芯科技
tags: [旺财, CAD, SolidWorks, Windows, 3D建模]
trigger: 用户要求出 CAD 图、画 SolidWorks 模型、生成 DXF、设计 3D 零件
---

# 旺财 CAD 出图技能

## ⚠️ 核心原则
- 参数化优先：所有几何尺寸从参数表读取，不要硬编码
- 输出三件套：STEP (3D交换) + STL (3D打印) + DXF (2D图纸)
- 验证必做：几何体积/边长 > 0, STEP 文件可被 FreeCAD 反读
- 颜色编码：进水蓝 / 出水绿 / 排污红 / 进气黄 (RGB: 0,0,255 / 0,200,0 / 200,0,0 / 255,200,0)

## Windows 特有工具链

### 1. SolidWorks COM API (Windows 独有)
```python
import win32com.client
import pythoncom

# 初始化 COM (每个线程必须)
pythoncom.CoInitialize()
sw = win32com.client.Dispatch("SldWorks.Application")
sw.Visible = True  # 可见模式

# 打开已有文件
doc = sw.OpenDoc6(r"C:\path\to\part.SLDPRT", 1, 0, "", 0, 0)

# 获取零件/装配体
part = sw.ActiveDoc

# 导出为 STEP
part.ExportToStep(r"C:\output\model.step")

# 导出为 DXF
part.ExportToDWG2(r"C:\output\model.dxf", "", 0)

# 释放 COM
pythoncom.CoUninitialize()
```

### 2. CadQuery (参数化建模, 跨平台)
```python
import cadquery as cq

# 渔芯 v4 移动箱主舱模板
def v4_enclosure(L=600, W=400, H=300, T=5):
    """参数: 长L, 宽W, 高H, 壁厚T"""
    box = cq.Workplane("XY").box(L, W, H)
    shell = box.faces(">Z").shell(T)
    
    # 进水口 (蓝色)
    inlet = (cq.Workplane("XY")
             .faces(">Z").workhole(50, depth=5)
             .faces(">Z").circle(25).extrude(-30))
    
    # 出水口 (绿色) 
    outlet = (cq.Workplane("XY")
              .faces(">Z").translate((150, 0, 0))
              .circle(20).extrude(-30))
    
    return shell.cut(inlet).cut(outlet)

# 导出
result = v4_enclosure()
cq.exporters.export(result, '/tmp/v4_enclosure.step')
cq.exporters.export(result, '/tmp/v4_enclosure.stl')
```

### 3. ezdxf (DXF 二维图纸)
```python
import ezdxf
from ezdxf.math import Vec2

doc = ezdxf.new("R2010")
msp = doc.modelspace()

# 绘制矩形
msp.add_lwpolyline([(0,0), (600,0), (600,400), (0,400), (0,0)])

# 标注 (配合毛豆的 DXF 模板风格)
msp.add_text("进水口 DN50", height=10).set_pos((100, 450))
msp.add_text("出水口 DN40", height=10).set_pos((300, 450))

doc.saveas('/tmp/v4_2d.dxf')
```

## 从毛豆继承的 DXF 模板
所有毛豆已完成的 DXF 图纸存放在 `yuxin-skills/references/maodou-dxf-outputs/`:
- HW-001_v241_agent.dxf — 滚筒微滤机
- HW-002_v241_agent.dxf — 蛋白质分离器
- 等 8 个 DXF + 8 个 PDF

**使用方式**: 作为设计参考, 修改尺寸参数生成新图纸

## 渔芯设备参数库
| 设备 | 型号 | 主要尺寸 | 连接口规格 |
|------|------|---------|-----------|
| 滚筒微滤机 | HW-001 | 1200×600×800 | 进水DN80/出水DN100/排污DN50 |
| 蛋白质分离器 | HW-002 | 800×800×1500 | 进水DN50/出水DN65/排污DN40 |
| 生物移动床反应器 | HW-003 | 2000×1000×1200 | 进水DN100/出水DN100/排污DN50 |

## 出图验证 (任何 AI 出图后必做)

```bash
# 1. 几何验证 — 体积 > 0, 边数合理
# 用 CadQuery 自带的 val()
model = cq.importers.importStep('/tmp/output.step')
print(f"体积: {model.val().Volume}, 面数: {len(model.val().Faces)}")

# 2. STEP 文件验证
import os
size = os.path.getsize('/tmp/output.step')
assert size > 0, "STEP 文件为空!"
print(f"STEP 文件大小: {size} bytes")

# 3. DXF 验证
import ezdxf
doc = ezdxf.readfile('/tmp/output.dxf')
print(f"DXF 实体数: {len(doc.modelspace())}")
```

## 已知陷阱
1. **SolidWorks COM 单线程**: COM 调用必须在同一线程, `win32com.client.Dispatch` 不能在 subagent 中跨线程使用
2. **路径反斜杠**: Windows 路径用 raw string `r"C:\path"` 或正斜杠 `C:/path`
3. **Codex CLI 生成 CAD 代码**: 让 Codex 生成 CadQuery/SolidWorks 脚本, Hermes 执行并验证
4. **SolidWorks 需要 GUI 许可**: 服务器/远程桌面场景可能无法启动 SW, 需用 CadQuery 替代
