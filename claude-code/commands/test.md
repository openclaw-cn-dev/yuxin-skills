# /test — 运行测试套件

运行项目测试，覆盖率报告，**自动修复**常见失败。

## 流程

1. **检测项目类型**
   - `package.json` 存在 → `pnpm test`（或 `npm test`）
   - `pyproject.toml` 或 `requirements.txt` 存在 → `pytest`
   - `Cargo.toml` 存在 → `cargo test`
   - `go.mod` 存在 → `go test ./...`

2. **运行测试**
   ```bash
   <test_cmd> --coverage
   ```

3. **结果分析**
   - 全过：汇报"✅ 全部通过，X 个用例，耗时 Ys"
   - 有失败：列出失败用例 + 错误摘要
   - 覆盖率 < 80%（核心模块）：提醒补测试

4. **可选：自动修复**（仅当 `$ARGUMENTS` 含 "fix"）
   - 简单 import 错误 → 自动改
   - 拼写错误 → 自动改
   - 复杂逻辑错误 → **不**自动改，列出等华哥决策

5. **汇报**
   - 通过/失败数
   - 覆盖率（before / after 对比如有）
   - 耗时
   - 失败用例列表

## 参数

- `$ARGUMENTS`：
  - 空 → 跑全部
  - `fix` → 失败时自动修简单问题
  - `watch` → watch 模式
  - `path/to/test` → 跑指定测试
  - `module` → 只跑某个模块
