---
name: python-project-audit
description: 多维度测试与审查 Python 项目（测试/覆盖率/门禁/代码质量/安全/数据完整性），产出分级报告。触发条件：华哥要求"深入分析/多维度测试与审查/审查/审计"某个本地项目，或发布前门禁核查、工程质量体检。
---

# Python 项目多维度测试与审查

对本地 Python 项目做一次端到端工程质量审查，产出分级报告存项目 `docs/`。

## 触发条件

- 华哥说「深入分析本地项目 X」「多维度测试与审查」「审查/审计项目 X」
- 发布前门禁核查、上线就绪评估、工程质量体检

## 七维审查清单（标准流程）

1. **读核心文档** — README / STATUS / CHANGELOG / AGENTS / 技术方案。先掌握项目自述口径、版本单一来源、**已登记偏差**（很多项目在 AGENTS.md 里诚实登记了"未完成的门禁"，审计时要去核实而不是默认相信）。
2. **跑测试套件** — pytest 全量 + 覆盖率。
3. **跑门禁** — ruff / check_version（版本一致性）/ mypy / 覆盖率门禁。
4. **代码架构与质量审查** — 各服务源码全文（不只 diff）。
5. **安全审查** — 注入/密钥/依赖/权限/时序侧信道。
6. **数据完整性审查** — 库计数 vs 文档口径、备份可恢复性、磁盘水位。
7. **生成分级报告** — 存项目 `docs/` 下。

## 关键 Pitfalls（本类任务最易踩、最省时间的坑）

### 1. 覆盖率门禁「幽灵门禁」（最重要）
`pyproject.toml` 里 `[tool.coverage.report] fail_under = 80` 看似有门禁，但两个条件叠加会让它**从未触发**：

- `[tool.coverage.run] source = ["单一包"]` 只统计一个子包，其余服务不进覆盖率口径；
- 测试命令写的是 `pytest -q`（不带 `--cov`），pytest 默认不收集覆盖率。

审计时**必须手动补齐 `--cov`**，用真实覆盖率说话，不要信 pyproject 里配的 fail_under：

```bash
python3 -m pytest services/*/tests \
  --cov=services/a/pkg_a --cov=services/b/pkg_b --cov-report=term-missing 2>&1 | tail -60
```

常见真实结果：写库核心 / 编排核心 / 向量模型封装 0% 覆盖（`load_db.py`、`run.py`、`embedder.py` 这类常没测）。判 FAIL 的阈值是 `TOTAL` 行。

### 2. pytest `-q` 双重静默
pyproject `addopts = "-q"` 已含 `-q`，命令行再传 `-q` 变成 `-qq`，会**吞掉 "137 passed" 汇总行**（只剩 warnings summary）。拿汇总数字时命令行别再加 `-q`，或 `grep -E "passed|failed"`。

### 3. 声明依赖 ≠ 已装依赖
dev 依赖（典型 mypy）常声明在 pyproject 的 optional-dependencies 里却没实际安装（`command not found`）。审计时逐个 import 核实，别默认"声明了=装好了"：

```bash
for mod in mypy ruff pytest pytest_cov psycopg2 fastapi uvicorn transformers torch; do
  python3 -c "import $mod" 2>/dev/null && echo "$mod ✅" || echo "$mod ❌ 未安装"
done
```

### 4. 测试数分布用 grep 而非 --collect-only
`pytest --collect-only -q | tail -1` 常截到 warnings 行而非 "N tests collected"。改用：

```bash
for d in ingest api mcp collect; do
  echo -n "$d: "; grep -rh "def test_" services/$d/tests/ | wc -l
done
```

### 5. RAG 语义判定类代码，mock 审不出真实 LLM 行为漂移（最易漏）
拒答判定/意图识别/语义匹配这类**依赖真实 LLM 输出**的代码，mock 测试（mock 掉 LLM 返回固定字符串）覆盖不了「模型会换同义措辞」这一行为。只看 mock 通过会漏掉契约级缺陷——实测案例：`is_model_refusal()` 用固定短语字面量匹配，mock 下 PASS，真实 LLM 换措辞后漏判 4/5，且正常回答含关键字又误判（**双向缺陷**）。

审查这类代码必须**主仓实跑 + 真实 LLM 网关**：对同一 query 连跑多轮，看判定是否稳定一致；同时验证「漏判」（换措辞漏过）与「误判」（正常回答命中关键字）两个方向。mock/快照只够审结构，不够审语义行为。交叉审查里 PASS 与 PASS-with-findings 的分歧，常常就是「只跑 mock」vs「真 LLM 实跑」的差别。

## 数据完整性核查模式

```bash
# 库计数 vs 文档口径（docker 内 psql，-tAc 纯文本输出）
docker exec <db容器> psql -U postgres -d <库> -tAc \
  "SELECT 'documents_active', count(*) FROM documents WHERE status='active' UNION ALL ..."

# 备份可恢复性（TOC 能解析 = 未损坏）
pg_restore --list <dump> | wc -l

# 磁盘水位
df -h /
```

## 报告规范（华哥偏好，写报告时务必遵守）

- **只审不修**：华哥说「审/审查/看一下」默认**只出结论不修代码**——发现明确 bug 也先报告，改生产代码要等他点头或交给作者。不要主动把「要不要我修」作为主要选项抛出（华哥 11-04 明确纠正过）。
- **结论先行**：顶部给「结论 + 关键数字表」，不长铺垫。
- **问题分级**：🔴 P1 发布阻断 / 🟠 P2 应尽快处理 / 🟡 P3 改进建议。
- 保存到项目 `docs/` 下，命名 `多维度测试与审查报告-<日期>.md`。
- 所有数字来自真实命令输出与数据库实查，不推断、不编造。
- 对照项目自述偏差（如 AGENTS.md §7）说明「无新增隐瞒项」——既诚实又体现对项目规范的理解。

## 关系

- 与 `find-bugs` 互补：`find-bugs` 是 **diff/变更级** 的 bug+安全审查；本技能是 **整项目级** 的工程质量体检（含测试/覆盖率/门禁/数据完整性）。
- 安全维度的深挖可参考 `security-review`。

## 完整命令包

`references/audit-command-bundle.md` 提供一份可直接复制执行的完整审计命令集（本会话实测可用）。
