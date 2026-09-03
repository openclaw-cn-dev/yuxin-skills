---
name: grep-ts
description: 在 TypeScript 项目内只读查找符号、路径、定义和调用点。
---

# grep-ts

当用户要求在 TypeScript 代码中查找符号、路径或调用点时触发。

目标：
- 在允许目录内列出文件
- 读取候选 TypeScript 文件
- 汇总匹配结果

执行边界：
- 只读
- 不修改文件
