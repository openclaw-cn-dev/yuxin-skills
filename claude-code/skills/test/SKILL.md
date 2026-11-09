---
name: test
description: 运行项目测试(pytest/vitest)并汇报结果(2026-11-07 重建版,原版丢失)
---

# test 测试运行

## 动作
1. 识别项目类型:Python→pytest,JS/TS→vitest/jest
2. 运行:`pytest -x -q`(先快跑)失败再全量;vitest 用 `npx vitest run`
3. 汇报:通过数/失败数/失败原因摘要,不粉饰

## 纪律
- 渔芯规范:新功能必测,覆盖率核心模块 >80%
- 测试命名:`test_<功能>_<场景>_<预期>`
