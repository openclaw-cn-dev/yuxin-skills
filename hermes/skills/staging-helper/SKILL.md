---
name: staging-helper
description: 渔芯 Agent 统一资料入站与查询标准 — 所有 agent 调研/生成资料 → ~/rkr_staging/文档中转站/，调用时走 staging_query.py (RKR API)。触发条件：agent 调研/生成/产出任何 Markdown 资料，或需要从 RKR 知识库调用已入库资料。
version: 1.0.0
author: 玉芬
tags: [rkr, staging, knowledge-base, 文档中转站, 文档库, agent-标准]
---

# 渔芯 Agent 统一资料入站与查询标准

> 📦 **核心原则**：
> - **写**：所有 agent 调研/生成/产出资料 → 统一调用 `staging_save.py` → `~/rkr_staging/文档中转站/`
> - **读**：所有 agent 调用资料 → 统一调用 `staging_query.py` → RKR API
> - **不要**：直接写 `~/rkr_staging/文档库/`（那是 RKR scanner 处理后的产物）
> - **不要**：直接读 `~/rkr_staging/文档库/` 文件系统（应走 RKR API）

---

## 架构（端到端流程）

```
Agent 调研/生成
  ↓ staging_save.py
~/rkr_staging/文档中转站/<子目录>/<日期>_<uuid>_<标题>.md
  ↓ RKR local_staging_scanner.py（每 60 秒扫一次）
~/rkr_staging/文档库/<分类>/（自动分类：通用知识库/01-AI基础理论/...）
  ↓ RKR process_shared_document（异步向量化 + 知识图谱）
RKR PostgreSQL + pgvector（永久存储）
  ↓ staging_query.py (RKR API)
Agent 调资料（知识检索 / 文档列表 / 关键词搜索）
```

**关键事实**：
- RKR `DEFAULT_STAGING_DIR = ~/rkr_staging/文档中转站/`（已默认）
- scanner 60 秒扫一次，发现新文件就处理
- 处理完**自动删除中转站原文件**（这是 RKR 设计行为，**正常**）
- 中转站 ≠ 文档库；中转站是 staging，文档库是永久存储

---

## 使用方法

### 1. 写资料（agent 调研/生成完调用）

```bash
# 命令行
python3 ~/.hermes/scripts/staging_save.py \
  --title "养殖池循环水设计调研" \
  --content "$(cat research.md)" \
  --source research \
  --agent maodou \
  --tag 养殖池 \
  --tag 循环水 \
  --meta "task_id=t-2026-001"

# Python API
from staging_save import stage
stage(
    title="养殖池循环水设计调研",
    content="# ... markdown ...",
    source="research",
    agent="maodou",
    tags=["养殖池", "循环水"],
)
```

**参数说明**：
- `--title` (必填): 资料标题
- `--content` (必填): Markdown 内容（`@file.md` 从文件读）
- `--source`: research(调研) / generated(生成) / report(报告) / raw(原始) / yuxin(玉芬整理) / findera(寻元)
- `--agent`: agent 名字（默认 `$HERMES_AGENT`）
- `--tag`: 标签（可多次）
- `--meta`: 额外元数据 `key=value`（可多次）

**文件落地格式**：
```
~/rkr_staging/文档中转站/01-调研资料/20260730_180040_b643d516_养殖池循环水设计调研.md
~/rkr_staging/文档中转站/01-调研资料/20260730_180040_b643d516_养殖池循环水设计调研.md.meta.json
```

子目录自动按 source 分类（01-调研资料 / 02-生成内容 / 03-调研报告 / 04-原始资料 / 05-玉芬整理 / 06-寻元采集）。

### 2. 读资料（agent 调资料时调用）

```bash
# 文档库总览
python3 ~/.hermes/scripts/staging_query.py stats

# 列出"知识文库"前 20 个
python3 ~/.hermes/scripts/staging_query.py list --lib knowledge --limit 20

# 关键词搜
python3 ~/.hermes/scripts/staging_query.py search --query "养殖池" --limit 10

# 列出所有 RKR 项目
python3 ~/.hermes/scripts/staging_query.py projects
```

**Python API**：
```python
from staging_query import cmd_list, cmd_search, _http, get_token
import json

token = get_token()
# 直接调 RKR API
data = _http("GET", "/api/v1/library/knowledge?search=养殖&page_size=5", token=token)
print(json.dumps(data, ensure_ascii=False, indent=2))
```

---

## 各 agent 接入建议

| Agent | 调研/生成场景 | 接入方式 |
|---|---|---|
| 玉芬 (yuxin) | 整理资料、归档笔记 | staging_save.py `--agent yuxin --source yuxin` |
| 毛豆 (maodou) | 产品调研、技术分析 | staging_save.py `--agent maodou --source research` |
| 阿福 (afu) | 客服话术、答疑资料 | staging_save.py `--agent afu --source generated` |
| 黑豆 (heidou) | 行政文档、合规资料 | staging_save.py `--agent heidou --source report` |
| 老莫 (laomo) | 知识库整理、测试报告 | staging_save.py `--agent laomo --source yuxin` |
| 小宝 (xiaobao) | 销售方法论、内容脚本 | staging_save.py `--agent xiaobao --source generated` |
| 整理师 (zhenglishi) | 华哥知识库整理 | staging_save.py `--agent zhenglishi --source yuxin` |
| 宽博士 (quant) | 量化研究、报告 | staging_save.py `--agent quant --source report` |
| FindEra (寻元) | 域资料采集 | 现有 rkr_sync.py 走 RKR API（**保留**） |

---

## 常见陷阱

### ❌ 错误 1: 直接写 `~/rkr_staging/文档库/`

```python
# ❌ 错误：直接写"文档库"
Path("~/rkr_staging/文档库/我的文档.md").write_text(content)
# 问题：scanner 不会扫这里，文档也不会被处理/索引
```

```python
# ✅ 正确：写"中转站"让 scanner 自动处理
stage(title="我的文档", content=content, source="research", agent="xxx")
```

### ❌ 错误 2: 写完资料后 60 秒内就检查"文档库"

```bash
# ❌ 错误：写完立刻检查
stage(title="...", content="...")
sleep 5
ls ~/rkr_staging/文档库/  # 还没出现！scanner 每 60 秒扫一次
```

```bash
# ✅ 正确：用 staging_query.py 通过 RKR API 查（不等）
python3 ~/.hermes/scripts/staging_query.py list --lib knowledge --limit 5
```

### ❌ 错误 3: 把 staging_save 的输出文件当"永久"文件

staging_save 写入的文件 60 秒内会被 scanner **删除**（这是 RKR 正常行为）。
要"永久保留"原始内容，请用 `--meta` 写进 .meta.json，或自己备份。

### ❌ 错误 4: 用 `~/rkr_staging/文档库/` 做路径硬编码

- 不同 agent 的 home 路径可能不同
- 用户可能改 rkr_staging 位置
- **永远用 staging_save / staging_query 抽象**

### ⚠️ 陷阱 5: Hermes profile envvar 劫持 `$HOME`（关键）

任何在 Hermes 子 profile（afu/maodou/laomo 等）下启动的脚本，`$HOME` 都会被改写成 `~/.hermes/profiles/<name>/home/`。结果：

```python
# ❌ 错误：脚本以为 home 是 /Users/hua，实际是 ~/.hermes/profiles/afu/home
Path.home() / "rkr_staging"          # → ~/.hermes/profiles/afu/home/rkr_staging（不存在！）
Path("~/rkr_staging/...")            # → ~/.hermes/profiles/afu/home/rkr_staging/...（不存在！）
```

**症状**：`staging_save.py` 写入了一个**根本不存在的**目录，scanner 看不到，`ls` 也找不到。

**修复**（`staging_save.py` v1.0.0 已修）：用 `os.path.expanduser("~/rkr_staging/文档中转站")` 仍会错，要硬编码：

```python
STAGING_DIR = Path("/Users/hua/rkr_staging/文档中转站")  # 不要用 Path.home() 或 ~/
```

> 华哥本机是 `/Users/hua`，未来换用户 / 多用户部署时此常量要参数化。

### ⚠️ 陷阱 6: 浏览器缓存可能让你以为有某个 RKR 功能

**症状**：用户说"我看到 RKR 有『技能仓库』模块"，但代码里**根本没有** —— 浏览器渲染的是旧 dist / 缓存页面。

**诊断**：
```bash
# 1. 直接看 RKR 源码菜单（前 11 个菜单一般是稳定基线）
grep -E 'label:' /Users/hua/6-产品研发/01-RKR知识库/frontend/src/components/layout/Sidebar.tsx

# 2. 看 docker 容器内 frontend 镜像版本
docker exec rkr-frontend cat /app/package.json | python3 -c "import sys,json;print(json.load(sys.stdin).get('version'))"

# 3. 比对源码 git log（看是不是有未提交的本地修改）
cd /Users/hua/6-产品研发/01-RKR知识库 && git status
```

> ⚠️ Vite dev server 模式（5173 端口）会**直接读源码**，所以源码更新即生效；但访问页面走的是缓存（ctrl+shift+R 强制刷新）。

### ⚠️ 陷阱 7: RKR 项目源码路径有两种，Desktop 那个是错的

```bash
# ❌ 错的（CLAUDE.md 提到的，但 iCloud 没同步时是空的）
~/Desktop/渔芯科技/6-产品研发/01-RKR知识库/   # ← 实际不存在或为空

# ✅ 真的（华哥手指定）
/Users/hua/6-产品研发/01-RKR知识库/         # ← 全部 RKR 源码 + docker-compose
```

之前踩过坑：`ls ~/Desktop/渔芯科技/6-产品研发/` 看到一堆乱七八糟，真实 RKR 项目在 `/Users/hua/6-产品研发/01-RKR知识库/`。**永远用绝对路径**。

### ⚠️ 陷阱 8: 批量文件系统 mirror ≠ 批量入库；用 API 才稳

**症状**：`rsync` 把 833 个 .md 镜像到 `~/rkr_staging/文档中转站/`，scanner 跑了，但只入库了 ~8 个文档（41642 → 41650）。

**根因**：scanner 对**纯 .md** 文件和**有 .meta.json 配套**的文件处理策略不同：
- 有 `.meta.json` 配套 → 元数据完整 → 顺利入库
- 纯 .md（无元数据）→ 可能入 staging project 后还需 LLM 分类，慢且命中率低

**修复**：
- 单文件 / 少量资料 → 用 `staging_save.py`（自动写 .meta.json）
- 批量大量资料（如 GitHub 全仓库 mirror）→ 用 RKR upload API：
  ```python
  for fmd in files:
      requests.post("http://localhost:8000/api/v1/staging/upload",
          headers={"X-API-Key": "rkr_..."},
          json={"title": ..., "content": fmd.read_text(), "project_id": "a7a325c9-..."})
  ```

---

## 监控与排错

```bash
# RKR scanner 实时日志
docker logs rkr-staging-pool --tail 50 --follow

# 中转站现状（看哪些文件还没被处理）
ls -lt ~/rkr_staging/文档中转站/ | head

# 文档库现状
ls -lt ~/rkr_staging/文档库/ | head

# RKR API 健康
python3 ~/.hermes/scripts/staging_query.py stats
```

---

## 历史资料批量迁移（从旧位置 → 中转站）

**场景**：agent 以前生成过资料，散落在 `~/Desktop/渔芯科技/*` 或 `~/.hermes/profiles/<agent>/home/...`，需要统一搬到中转站。

**用 `migrate_agent_artifacts.py`**：

```bash
# Dry run 先看数量
python3 ~/.hermes/scripts/migrate_agent_artifacts.py --dry-run

# 全量执行
python3 ~/.hermes/scripts/migrate_agent_artifacts.py --execute

# 只迁 desktop / 只迁 profiles
python3 ~/.hermes/scripts/migrate_agent_artifacts.py --execute --only desktop
python3 ~/.hermes/scripts/migrate_agent_artifacts.py --execute --only profiles

# 测试用（小批量）
python3 ~/.hermes/scripts/migrate_agent_artifacts.py --execute --limit 100
```

**默认扫描范围 + 排除规则**（详见 `references/migration-rules.md`）：

| 来源 | 包含 | 排除 |
|---|---|---|
| `~/Desktop/渔芯科技/` | .md/.json/.pdf/.docx etc. | `00-FindEra寻元/`（**寻元不动**） |
| `~/.hermes/profiles/<agent>/home/` | 同上 | `Library/`、`node_modules/`、`.cache/`、`site-packages/`、`__pycache__/`、`.git/`、`dist/` |
| `~/Desktop/` 顶层 | 同上 | 同上 |

**关键行为**：
- **复制而非移动**（原文件保留）
- 每个 .md 加 `<!-- migration_meta -->` frontmatter（含 `source_path` / `agent` / `migrated_at`）
- 每个文件配套 `.meta.json`（RKR scanner 友好的元数据）
- **路径镜像**：`<原路径相对>` → `migration_<日期>/<来源>/<相对路径>`

**已验证规模**：14,879 文件 / 469 MB / 0 错误（2026-07-30 一次跑完）。

⚠️ **脚本陷阱**（亲历）：不要用 `sorted(set(files))`，那会按 ASCII 排序把 `/.hermes/...` (47 < 68 `D`) 排到 `~/Desktop/...` 前面，导致 `--limit N` 截断错乱。**正确做法**：`list(dict.fromkeys(files))` 保留采集顺序（desktop → profiles）。

---

## GitHub 仓库 → 中转站 同步

**场景**：GitHub 上的 `openclaw-cn-dev/yuxin-skills` 仓库（Hermes/Claude/Codex 跨 agent 的 skills）需要 mirror 到 RKR 中转站入库。

**用 `sync_yuxin_skills_to_staging.sh`**：

```bash
# 手动同步一次
~/.hermes/scripts/sync_yuxin_skills_to_staging.sh
```

**行为**：
- `git pull` 增量到 `/tmp/yuxin-skills-sync-cache/`
- `rsync -a --exclude='.git'` mirror 到 `~/rkr_staging/文档中转站/yuxin-skills-YYYYMMDD/`
- 健康检查：文件数 < 600 自动重 mirror（防 scanner 误清）

**已验证规模**：833 文件 / 10MB（claude-code 33 + hermes 230 + codex 14 + drawing-skills 8 skills）。

> 这个 pattern 跟 `codex_self_evolution.py` 里"GitHub sync 到 yuxin-skills/codex/"的 cron 已注册的逻辑是相同的（每小时跑一次 `6dfcbdeac7bf`）。

---

## Cron 自动监控

### 已注册的 cron job

| job_id | schedule | 任务 | 来源 |
|---|---|---|---|
| `6dfcbdeac7bf` | `every 60m` | Codex 配置 → yuxin-skills GitHub 同步 | `codex_github_sync.sh` |
| `955afce881f0` | `0 3 * * 0`（每周日 3:00）| Agent 历史资料 → RKR 中转站（增量） | `migrate_incremental.sh` |

**增量迁移 cron 细节**：
- 调 `migrate_incremental.sh`（wrapper bash）→ 调 `python3 migrate_agent_artifacts.py --incremental --execute`
- manifest 跟踪：`~/.hermes/state/migration_manifest.json`（用 `mtime + size` 做 key）
- 日志：`~/.hermes/logs/migrate_incremental_cron.log`
- 触发时检查 7 个 agent profile + `~/Desktop/渔芯科技/` 的资料类文件
- **不动寻元**（`00-FindEra寻元/` 排除）+ **不开发项目**（开发项目代码不在扫描范围内）

### 注册新 cron 的模板

```bash
# 注册 hourly 轻量 sync（已有 cron 可复用）
cronjob action=list  # 看现有 job
# 类似 6dfcbdeac7bf / 955afce881f0 的 wrapper pattern（`script=` 传相对路径，no_agent=True）
```

---

## 关联

- **RKR 项目根**: `/Users/hua/6-产品研发/01-RKR知识库/`
- **RKR staging 监听**: `backend/app/tasks/local_staging_scanner.py`（每 60 秒扫一次，自动入库 + 删原文件）
- **RKR staging 配置**: `backend/app/services/staging_config.py` (`DEFAULT_STAGING_DIR = ~/rkr_staging/文档中转站`)
- **现有 RKR API 集成参考**: `~/.hermes/skills/research-collection/references/findera-rkr-pipeline.md`
- **FindEra 保留 API 模式**: 走 `POST /api/v1/staging/upload` (X-API-Key) — **不要让寻元改走 staging 文件系统**

## References（本目录下）

- `references/scanner-architecture.md` — RKR scanner 详细时序、配置来源、故障行为
- `references/migration-rules.md` — `migrate_agent_artifacts.py` 完整扫描/排除规则表
- `references/findera-exception.md` — 为什么 FindEra 不走 staging 文件系统
- `references/hermes-profile-env-pitfall.md` — `$HOME` 被 Hermes profile 改写的陷阱 + 修复

---

> 🤖 玉芬维护 · 2026-07-30 · v1.1.0
> 📌 适用 agent: 玉芬/毛豆/阿福/黑豆/老莫/小宝/整理师/宽博士 + 任何新 agent
> 🆕 v1.1.0: 加入批量迁移 + GitHub 同步 + cron 模式 + 4 个 references