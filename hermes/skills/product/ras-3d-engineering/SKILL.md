---
name: ras-3d-engineering
description: 渔芯 RAS 3D 工程技能库 — Three.js 坐标系统、模型缩放、管道连接器系统的共享规范。触发条件：设计/实现/修改 3D 场景、模型加载、坐标映射、管道连接、连接点计算。
category: product
---

# RAS 3D 工程技能库

本技能库覆盖渔芯 RAS 项目中所有 3D 场景共享的工程规范。包括两大子领域：

## 子技能

### 1. 管道连接器系统 (`ras-3d-piping-connectors`)
完整覆盖渔芯 RAS CAD 的三维管道连接器设计。

**触发条件**：设计/实现/修改 3D 场景中的连接点、管道连接器、Face-Snapping 机制、管道渲染。

**核心内容**：
- Face-Snapping 连接点设计（左/右/前/后面贴合）
- 颜色编码：`in=蓝`, `out=绿`, `drain/sludge=红`, `air=黄`
- 连接点位置计算（含旋转矩阵）
- 管道数据流：startConnecting → completeConnection → calculatePipeComponents
- 管道反应式跟随设备移动（从设备实时计算，不静态存储坐标）
- 配件库（16种：弯头/三通/四通/阀门/法兰/变径/堵头等）
- 断管插入连接件（breakPipeAtFitting）
- 双模式自动布管（设备连接点直连 / 路径节点方式）
- FittingPropertyPanel 旋转轴向系统（X/Y/Z 轴独立旋转）
- 管道选中 → PipePropertyPanel 调管径

**关键陷阱**：
- GLB 模型遮挡连接点：须用 edgeOffset + 透明点击区域 + renderOrder=10 三重保护
- 连接器必须单几何体渲染（mergeGeometries + mergeVertices）
- SCALE_3D 必须统一用 0.01（不能用 0.001）
- 坐标映射：`设备Y(深)→Three.js Z`，`设备Z(高)→Three.js Y(向上)`
- 配件延长管端口偏移量必须用 `getFittingSurfaceRadius(type, diameter)` 计算
- 弯头延长管管径用 torus tube 半径 `r*0.8`，不能用通用 `r*0.85`
- 管道标高（Z轴）：ConnectionPoint 必须传 `{x, y, z}` 含标高，calculatePipeComponents 必须含 Z 轴长度分量

**详细文档**：`references/***SECRET***.md`（已从原技能迁移）

### 2. 模型自动缩放 (`threejs-model-auto-scale`)
GLB/GLTF 模型加载后自动匹配目标尺寸的通用技术。

**触发条件**：Three.js 加载外部模型需要匹配真实世界尺寸、产品配置器、CAD布局工具等。

**核心内容**：
- `Box3.setFromObject()` 计算世界空间包围盒
- 统一缩放（uniform scale）保持模型比例
- React-Three-Fiber 生命周期：`useState` 而非 `useRef` 作为 effect 依赖
- 模型缓存（Cache original, clone on retrieval）
- Draco decoder URL 配置

**坐标规范**（与 ras-3d-piping-connectors 完全一致）：

| 轴 | Three.js | 设备维度 |
|----|----------|---------|
| X | Right | Width（宽） |
| **Y** | **Up** | **Height（高）** |
| Z | Forward | Depth（深） |

```
targetDimensions = [width, height, depth]  // Three.js: X=宽, Y=高↑, Z=深
sy = modelSize.y > eps ? target[2] / modelSize.y : 1  // target[2] = height
sz = modelSize.z > eps ? target[1] / modelSize.z : 1  // target[1] = depth
```

**详细文档**：`references/***SECRET***.md`（已从原技能迁移）

---

## 共享规范

### SCALE_3D 统一常量

所有 3D 渲染组件必须使用 `SCALE_3D = 0.01`（1mm = 0.01 Three.js 单位）。不可使用 0.001。

### 坐标映射表

| 概念 | 设备(mm) | Three.js 单位 | 公式 |
|------|---------|-------------|------|
| 宽 | width | X | `worldX = width * 0.01` |
| 高 | height | Y (向上) | `worldY = height * 0.01` |
| 深 | depth | Z | `worldZ = depth * 0.01` |
| 位置X | x | X | `posX = x * 0.01` |
| 位置Y | y | Z | `posZ = y * 0.01` |
| 标高Z | z | Y (向上) | `posY = z * 0.01` |

### 设备坐标 ↔ Three.js 坐标

```
设备坐标: X=宽, Y=深, Z=高(向上)
Three.js: X=宽, Y=高(向上), Z=深
```

⚠️ **关键陷阱**：设备 Y(深) → Three.js Z，设备 Z(高) → Three.js Y(向上)。混淆这两个轴是最常见的 bug 来源。

### 模型自动缩放坐标映射（alternative convention）

当使用 `target = [width, depth, height]`（设备顺序：宽、深、高）时：

```typescript
sy = modelSize.y > eps ? target[2] / modelSize.y : 1  // target[2] = height
sz = modelSize.z > eps ? target[1] / modelSize.z : 1  // target[1] = depth
```

两种约定混用会产生错误的缩放结果。项目中统一使用 `target = [width, height, depth]`（Three.js 顺序）。

### React-Three-Fiber 生命周期规范

- 使用 `useState` 而非 `useRef` 作为 `useEffect` 依赖项
- Refs 不会触发重新渲染，模型加载后必须 setState 触发
- 缓存原始模型场景，`clone()` 用于每次渲染避免状态污染
