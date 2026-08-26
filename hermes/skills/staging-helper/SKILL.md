---
name: staging-helper
description: 渔芯 Agent 统一资料入站与查询标准 — 玉芬是全公司总负责人(2026-08-03 华哥明确),7 个 agent(毛豆/小宝/老莫/阿福/黑豆/学习助手/宽博士)都是玉芬的执行单元。同事业务结果性报告直接放 ~/rkr_staging/文档库/3-公司项目资料/(工作空间),归档层(1-通用/2-专业/4-360行)走 staging 中转站,所有资料调用走 staging_query.py (RKR API)。触发条件:agent 调研/生成/产出任何 Markdown 资料,或需要从 RKR 知识库调用已入库资料,**或 agent personal zone 内的 workspace/knowledge/ 与 staging 中转站/RKR 索引路径不一致导致审计脚本误判**。
version: 1.4.1
author: 玉芬
tags: [rkr, staging, knowledge-base, 文档中转站, 文档库, agent-标准, 工作空间, 玉芬总负责]
---

# 渔芯 Agent 统一资料入站与查询标准

> 📦 **核心原则**(2026-08-03 华哥明确):
> - **玉芬是全公司总负责人**,向华哥负责。7 个 agent(毛豆/小宝/老莫/阿福/黑豆/学习助手/宽博士)都是**玉芬的执行单元**。
> - **3-公司项目资料/ 是工作空间,不是归档层** — 业务结果性报告直接 `cp/mv/write_file` 放这里(玉芬授权范围)
> - **1-通用知识/ 2-专业知识/ 4-360行项目调研/ 仍是归档层** — 走 staging 中转站,scanner 自动分类
> - **写**:业务结果性报告直接放工作空间(玉芬授权);归档层资料走 `staging_save.py` 中转站
> - **读**:所有 agent 调资料 → 统一调用 `staging_query.py` → RKR API
> - **决策**:5 个同事**无版主决策权**(分类/整理/清理/合并/归档/淘汰权归玉芬)

## 架构(端到端流程)

```
Agent 调研/生成(归档层:1/2/4)
  ↓ staging_save.py
~/rkr_staging/文档中转站/<子目录>/<日期>_<uuid>_<标题>.md
  ↓ RKR local_staging_scanner.py(每 60 秒扫一次)
~/rkr_staging/文档库/<分类>/(自动分类:1-通用知识/2-专业知识/4-360行)
  ↓ RKR process_shared_document(异步向量化 + 知识图谱)
RKR PostgreSQL + pgvector(永久存储)
  ↓ staging_query.py (RKR API)
Agent 调资料(知识检索 / 文档列表 / 关键词搜索)

Agent 调研/生成(工作空间:3-公司项目资料/)
  ↓ 直接 cp / mv / write_file
~/rkr_staging/文档库/3-公司项目资料/<子目录>/  ← 自由操作,新建/修改/移动/删除
```

**关键事实**:
- RKR `DEFAULT_STAGING_DIR = ~/rkr_staging/文档中转站/`(已默认)
- scanner 60 秒扫一次,发现新文件就处理
- 处理完**自动删除中转站原文件**(这是 RKR 设计行为,**正常**)
- 中转站 ≠ 文档库;中转站是 staging,文档库是归档层 + 工作空间两层

## 2 层 + 1 工作空间架构(2026-08-03 华哥明确)

`~/rkr_staging/文档库/` 下面分**两层 + 一个工作空间**,每层有严格的"谁写、谁读"规则:

```
~/rkr_staging/文档库/
├── 1-通用知识/         ← Layer 1:【RKR 归档层,只读】跨领域通识(scanner 分类)
├── 2-专业知识/         ← Layer 1:【RKR 归档层,只读】RAS/水产专业(scanner 分类)
├── 4-360行项目调研/    ← Layer 1:【RKR 归档层,只读】新行业调研占位(scanner 分类)
│
├── 3-公司项目资料/     ← Workspace:【可写工作空间,自由操作】(2026-08-03 华哥明确)
│   ├── 301-智能体/                ← 5 个同事 agent 的 personal zone
│   │   ├── 毛豆-产品交付/
│   │   ├── 小宝-商务运营/
│   │   ├── 老莫-技术运维/
│   │   ├── 阿福-客服/
│   │   ├── 黑-行政财务法务/        (4K 空,待合并)
│   │   └── 黑豆-行政财务法务/
│   ├── 303-竞品库/                ← 毛豆主理
│   ├── 304-公司运营/              ← 16 个子目录(其中 4 个空白待激活)
│   │
│   ├── 302-数据与素材库/          ← 5.7G 共享二进制素材(需协调)
│   ├── antigravity-awesome-skills/   ← GitHub mirror 仓库(RKR 资源)
│   ├── awesome-claude-code/         ← GitHub mirror 仓库(RKR 资源)
│   ├── cad_samples/                 ← CAD 样本(RKR 资源)
│   ├── material_library/            ← 材料库(RKR 资源)
│   ├── mech_drawing/                ← 机械图纸(RKR 资源)
│   └── ... 其他 RKR 资源
│
├── cleaned/            ← RKR 清洗临时 .txt(244 个,**严禁碰**)
└── 通用知识库/         ← RKR 索引库 .md 快照(26686 个,**严禁 ls / 引用文件路径**)
```

**工作空间使用规则(2026-08-03 玉芬统一分配)**:

> 玉芬是全公司总负责人,所有版块管理由玉芬统一决策。7 个 agent 是玉芬的执行单元,各自负责配对版块的日常运营,**版主决策权归玉芬**。

| Agent | 业务 | 配对版块(玉芬指定) | 写读方式 |
|---|---|---|---|
| **玉芬** | 全公司总负责人 | **所有版块**(统一决策) | 玉芬向华哥负责 |
| 毛豆 | 产品交付 / AI 出 CAD / 3D 工程 | 2-专业知识/(RAS) + 303-竞品库/ + 304/产品研发全链条/ | 报告直接放工作空间;RAS 走中转站 |
| 小宝 | 销售 / 商务运营 / 自媒体 | 304/销售与市场营销/ + 304/市场推广/ | 销售话术/案例直接放工作空间 |
| 老莫 | 技术运维 / 知识库 / 测试 | 老莫 personal zone + freecad-automation/ + 304/客户服务与运维/ | 运维 SOP 直接放;测试报告直接放 |
| 阿福 | 客服 / 演示 / 用户反馈 | 阿福 personal zone + EDAI自动审批测试/ + **4-360行项目调研/(主理)** + 304/客户服务与运维/ | FAQ 直接放;新行业调研走 4-360行 |
| 黑豆 | 行政 / 财务 / 法务 / 合规 | 黑豆 personal zone + 304/法规标准与认证/HR/财务/知识产权/ | 合同/制度直接放;政策走 1-通用知识/ |
| 学习助手 | 资料采集 / 调研 | **1-通用知识/(主理)** + zhenglishi personal zone | 全部走 staging 中转站 |
| 宽博士 | 量化研究 | quant personal zone + 1-通用知识/2.6 量化/ | 量化报告直接放 quant/;方法论走 1-通用知识/2.6 |

**协调冲突规则**:
- 跨 agent 版块冲突(例如毛豆的竞品 vs 小宝的销售话术引用同一竞品)→ **玉芬裁决**
- 5 个同事的产出 → 默认送玉芬审 → 玉芬决定是否合并/淘汰/调整
- 玉芬向华哥负责,华哥只看玉芬的交付

**所有同事都不能动**:
- `1-通用知识/` `2-专业知识/` `4-360行项目调研/`(RKR 归档层,新资料走中转站)
- `cleaned/` `通用知识库/`(RKR 内部产物)
- `es_data/` `minio_data/` `pgdata/` `redis_data/` `rkr_backup.dump`(RKR 基础设施)
- `3-公司项目资料/` 下的 RKR 资源(`antigravity-awesome-skills/` `cad_samples/` `material_library/` `mech_drawing/` 等)

**核心心法(快速对照表)**:

| 触发场景 | 写到哪 | 用什么 |
|---|---|---|
| 写一份"竞品调研" / "行业分析" / "通用知识" / "RAS 专业知识" | Layer 1 中转站 → scanner 自动归类到 `1-通用/` `2-专业/` `4-360行/` | `staging_save.py --source research` |
| 写一份"销售话术" / "客服 SOP" / "技术报告" / "合同模板" / "制度文件" | Workspace `3-公司项目资料/`(直接放) | `cp` / `mv` / `write_file` |
| 写一个**已收敛的专题页**(HW-001 设备页、BP 调研、FAQ 库) | `3-公司项目资料/301-智能体/<agent>/<专题名>/` | `write_file` 直接写(沉淀) |
| 读"养殖池循环水设计"相关资料 | RKR API(从 pgvector 检索) | `staging_query.py search` |
| 调试时审计文档库 | 文件系统(只读,**不写**) | `ls` / `du` |
| 批量 mirror GitHub 仓库 | Layer 1 中转站 `yuxin-skills-YYYYMMDD/` | `sync_yuxin_skills_to_staging.sh` |
| 历史资料(散落在 Desktop/profiles) | Layer 1 中转站 `migration_YYYYMMDD/` | `migrate_agent_artifacts.py --execute` |

## 4 个有效归档目录分类判断(2026-08-03 玉芬固化)

文档库只有 4 个有效顶层目录,任何调研/报告写入前**必须先归类**:

| 顺序 | 判断条件 | 目录 | 类型 | 写入方式 |
|---|---|---|---|---|
| 1 | 渔芯具体业务的**结果性报告**(竞品分析/产品方案/技术报告/合同/SOP/话术/FAQ) | `3-公司项目资料/` | **🟢 工作空间** | `write_file` / `cp` / `mv` 直接放 |
| 2 | 水产养殖 / RAS 专业知识 | `2-专业知识/` | 🟢 归档层 | 走 `staging_save.py` 中转站 |
| 3 | 跨领域通用知识(AI/工程/管理/创意/量化/设计/仿真/OPC/法律/管理/经济/政治/学术) | `1-通用知识/` | 🟢 归档层 | 走 `staging_save.py` 中转站 |
| 4 | 暂时无法确定归属的新行业、新项目调研 | `4-360行项目调研/` | 🟢 归档层 | 走 `staging_save.py` 中转站 |

**判断口诀**(优先级从高到低):
1. **"是渔芯业务的结果性报告吗?"** 是 → 直接放 `3-公司项目资料/` 工作空间(`write_file` / `cp` / `mv`)
2. **"是 RAS / 水产专业知识吗?"** 是 → 走中转站 → `2-专业知识/`
3. **"是跨行业通用方法吗?"** 是 → 走中转站 → `1-通用知识/`
4. **"是新行业探索但暂时无法归类?"** 是 → 走中转站 → `4-360行项目调研/`

**用户硬性约束**(2026-08-03 华哥明示,**仅适用于归档层 1/2/4**):

- ❌ 不能 `cp ~/rkr_staging/文档库/1-通用知识/...md` 拷贝归档层文件出来(归档层是 scanner 产物,不能动)
- ❌ 不能 `mv ~/rkr_staging/文档库/1-通用知识/...md` 移动归档层文件
- ❌ 不能 `rm ~/rkr_staging/文档库/1-通用知识/...md` 删除归档层文件
- ❌ 不能在归档层(1/2/4)子目录下 `write_file` 新建文件(RKR scanner 不会扫这里,索引不上)
- ✅ **可以**在 `3-公司项目资料/` 工作空间下 `write_file` 新建/修改/移动/删除自己负责的子目录
- ✅ 可以 `ls` / `du` / `cat` 读文档库任何子目录(用于审计)
- ✅ 可以 `read_file` 读文档库任何文件(用于理解归档结构)

> ⚠️ **v1.3.0 关键警告**:`3-公司项目资料/` 是**工作空间不是归档层**,直接 write_file 是对的;但**绝不能把 `1-通用知识/` `2-专业知识/` `4-360行项目调研/` 也当作可写工作空间**(常见误读,本 skill v1.0–v1.2 曾混淆)。华哥 2026-08-03 明确:`3-公司项目资料/` 是为同事业务结果性报告准备的"留给大家的工作空间,可以自由操作",归档层仍是 RKR scanner 管理的只读分类层。

## 5 同事 AGENTS.md 下发流程(2026-08-03 玉芬建立)

当路径 SOP / 工具规范 / agent 工作流发生变更,需要同步到 5 个同事(毛豆/小宝/老莫/阿福/黑豆),**完整流程**:

1. **更新本 skill**(`staging-helper/SKILL.md` + `templates/agent-workspace-sop.md`)
2. **写 5 份 `AGENTS.md`** 到 `~/.hermes/profiles/<agent>/AGENTS.md`(Hermes 启动自动加载,**不在文档库**)
3. **入库规范文档**:`staging_save.py --source yuxin --agent yuxin --tag 工作目录/路径SOP/Agent规范`(60 秒后 scanner 归类)
4. **飞书回执给华哥**:列出 5 份 AGENTS.md 路径 + 入库规范文档路径 + 核心规则摘要

详细模板见 `templates/agent-workspace-sop.md`;rollout 流程的历史决策/坑见 `references/agent-rollout-procedure.md`(2026-08-03 建立)。

**目录全景参考**:见 `references/document-library-layout.md`(2026-08-03 实测)
**agent personal zone 规则**:见 `references/agent-personal-zone.md`

## 使用方法

### 1. 写资料(agent 调研/生成完调用)

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

# Python API(⚠️ `agent=` 必须是顶层 kwarg,不能放 meta 里 — 见陷阱 14)
from staging_save import stage
stage(
    title="养殖池循环水设计调研",
    content="# ... markdown ...",
    source="research",
    agent="maodou",                          # ← 顶层必传,放 meta 里会被静默吞掉
    tags=["养殖池", "循环水"],
)
```

> ⚠️ **常见错误**:把 `agent` 写进 `meta={}` 字典里(`meta={"agent": "maodou", ...}`)。`stage()` 签名里 `agent` 是顶层 kwarg,**写在 meta 里会被静默忽略**,输出 `Agent: default`,文件仍入站但路由失效。详见陷阱 14。

**参数说明**:
- `--title` (必填): 资料标题
- `--content` (必填): Markdown 内容(`@file.md` 从文件读)
- `--source`: research(调研) / generated(生成) / report(报告) / raw(原始) / yuxin(玉芬整理) / findera(寻元)
- `--agent`: agent 名字(默认 `$HERMES_AGENT`)
- `--tag`: 标签(可多次)
- `--meta`: 额外元数据 `key=value`(可多次)

**文件落地格式**:
```
~/rkr_staging/文档中转站/01-调研资料/20260730_180040_b643d516_养殖池循环水设计调研.md
~/rkr_staging/文档中转站/01-调研资料/20260730_180040_b643d516_养殖池循环水设计调研.md.meta.json
```

子目录自动按 source 分类(01-调研资料 / 02-生成内容 / 03-调研报告 / 04-原始资料 / 05-玉芬整理 / 06-寻元采集)。

### 2. 读资料(agent 调资料时调用)

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

**Python API**:
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
| FindEra (寻元) | 域资料采集 | 现有 rkr_sync.py 走 RKR API(**保留**) |

---

## 常见陷阱

### ⚠️ 陷阱 0(v1.3.0 新增):把整个文档库当归档层 — 常见误读

**症状**:agent 看到"文档库"就以为全部是 RKR scanner 自动分类的归档产物,不敢在 `3-公司项目资料/` 下 `write_file`,把所有同事报告都走 staging 中转站。

**根因**:v1.0–v1.2 的 SKILL 把整个 `~/rkr_staging/文档库/` 描述为"只读归档层",没有区分 `3-公司项目资料/`。这是误读 — 华哥 2026-08-03 明确:"3-公司项目资料 是留给大家的工作空间,可以自由操作"。

**正确理解(2 层 + 1 工作空间)**:
- 🟢 **归档层(只读,走中转站)**:`1-通用知识/` `2-专业知识/` `4-360行项目调研/`(RKR scanner 自动分类)
- 🟢 **工作空间(直接 write_file)**:`3-公司项目资料/`(同事放"结果性报告":竞品/产品/技术/合同/SOP/话术/FAQ)

**典型错例**:
```python
# ❌ v1.2 风格的"安全"做法 — 把竞品报告塞中转站(没必要,且会失去 RKR 直接索引)
stage(title="Hydrotech-2026 竞品分析", content=..., source="research", agent="maodou")
# 等 60 秒 → scanner 归类 → 同事想看还要 staging_query.py 搜

# ✅ v1.3.0 正确做法:直接放工作空间
Path("/Users/hua/rkr_staging/文档库/3-公司项目资料/303-竞品库/Hydrotech-2026.md").write_text(content)
# 立刻可读,scanner 会顺便索引(双保险)
```

**速查表**:

| 资料类型 | 正确位置 | 工具 |
|---|---|---|
| 竞品分析报告 | `3-公司项目资料/303-竞品库/` | `write_file` |
| 产品方案 / 技术报告 | `3-公司项目资料/301-智能体/<agent>/` | `write_file` |
| 销售话术 / FAQ | `3-公司项目资料/304-公司运营/销售与市场营销/` | `write_file` |
| 合同模板 / 合规清单 | `3-公司项目资料/301-智能体/heidou/knowledge/` | `write_file` |
| 通用知识调研 | 中转站 → scanner → `1-通用知识/` | `staging_save.py` |
| RAS 专业调研 | 中转站 → scanner → `2-专业知识/` | `staging_save.py` |
| 新行业调研 | 中转站 → scanner → `4-360行项目调研/` | `staging_save.py` |

### ❌ 错误 1: 直接写归档层(1-通用知识/2-专业知识/4-360行)

```python
# ❌ 错误:直接写"通用知识"
Path("~/rkr_staging/文档库/1-通用知识/我的文档.md").write_text(content)
# 问题:scanner 不会扫这里(归档层是 scanner 输出),文档不会被处理/索引
```

```python
# ✅ 正确:写"中转站"让 scanner 自动处理
stage(title="我的文档", content=content, source="research", agent="xxx")

# ✅ 业务结果性报告:直接放工作空间 3-公司项目资料/
Path("~/rkr_staging/文档库/3-公司项目资料/301-智能体/毛豆-产品交付/我的报告.md").write_text(content)
```

### ❌ 错误 2: 写完资料后 60 秒内就检查"文档库"

```bash
# ❌ 错误:写完立刻检查
stage(title="...", content="...")
sleep 5
ls ~/rkr_staging/文档库/  # 还没出现!scanner 每 60 秒扫一次
```

```bash
# ✅ 正确:用 staging_query.py 通过 RKR API 查(不等)
python3 ~/.hermes/scripts/staging_query.py list --lib knowledge --limit 5
```

### ❌ 错误 3: 把 staging_save 的输出文件当"永久"文件

staging_save 写入的文件 60 秒内会被 scanner **删除**(这是 RKR 正常行为)。
要"永久保留"原始内容,请用 `--meta` 写进 .meta.json,或自己备份。

### ❌ 错误 4: 用 `~/rkr_staging/文档库/` 做路径硬编码

- 不同 agent 的 home 路径可能不同
- 用户可能改 rkr_staging 位置
- **永远用 staging_save / staging_query 抽象**

### ⚠️ 陷阱 5: Hermes profile envvar 劫持 `$HOME`(关键)

任何在 Hermes 子 profile(afu/maodou/laomo 等)下启动的脚本,`$HOME` 都会被改写成 `~/.hermes/profiles/<name>/home/`。结果:

```python
# ❌ 错误:脚本以为 home 是 /Users/hua,实际是 ~/.hermes/profiles/afu/home
Path.home() / "rkr_staging"          # → ~/.hermes/profiles/afu/home/rkr_staging(不存在!)
Path("~/rkr_staging/...")            # → ~/.hermes/profiles/afu/home/rkr_staging/...(不存在!)
```

**症状**:`staging_save.py` 写入了一个**根本不存在的**目录,scanner 看不到,`ls` 也找不到。

**修复**(`staging_save.py` v1.0.0 已修):用 `os.path.expanduser("~/rkr_staging/文档中转站")` 仍会错,要硬编码:

```python
STAGING_DIR = Path("/Users/hua/rkr_staging/文档中转站")  # 不要用 Path.home() 或 ~/
```

> 华哥本机是 `/Users/hua`,未来换用户 / 多用户部署时此常量要参数化。

> ⚠️ **2026-08-24 审计复现**:毛豆(08-17)+ 宽博士/量化(08-15)**先后踩同一坑**,都写进了字面量 `~/Desktop/知识库/RAS仿真技术调研/` 目录:
> - 毛豆:`3-公司项目资料/301-智能体/毛豆-产品交付/workspace/~/Desktop/...`(玉芬已清理,移到 `workspace/RAS仿真技术调研/`)
> - 宽博士:`1-公共知识/114-项目开发与调研/8-量化研究/~/Desktop/...`(归档层,待宽博士自修)
> 教训:陷阱 5 的"用绝对路径"SOP 未传达到位,两个 agent 的调研脚本都在用 `~/` 相对路径。**排查方法**:`find ~/rkr_staging/文档库 -type d -name '~'` 可快速定位所有残留字面量 `~` 目录。

### ⚠️ 陷阱 6: 浏览器缓存可能让你以为有某个 RKR 功能

**症状**:用户说"我看到 RKR 有『技能仓库』模块",但代码里**根本没有** —— 浏览器渲染的是旧 dist / 缓存页面。

**诊断**:
```bash
# 1. 直接看 RKR 源码菜单(前 11 个菜单一般是稳定基线)
grep -E 'label:' /Users/hua/6-产品研发/01-RKR知识库/frontend/src/components/layout/Sidebar.tsx

# 2. 看 docker 容器内 frontend 镜像版本
docker exec rkr-frontend cat /app/package.json | python3 -c "import sys,json;print(json.load(sys.stdin).get('version'))"

# 3. 比对源码 git log(看是不是有未提交的本地修改)
cd /Users/hua/6-产品研发/01-RKR知识库 && git status
```

> ⚠️ Vite dev server 模式(5173 端口)会**直接读源码**,所以源码更新即生效;但访问页面走的是缓存(ctrl+shift+R 强制刷新)。

### ⚠️ 陷阱 7: RKR 项目源码路径有两种,Desktop 那个是错的

```bash
# ❌ 错的(CLAUDE.md 提到的,但 iCloud 没同步时是空的)
~/Desktop/渔芯科技/6-产品研发/01-RKR知识库/   # ← 实际不存在或为空

# ✅ 真的(华哥手指定)
/Users/hua/6-产品研发/01-RKR知识库/         # ← 全部 RKR 源码 + docker-compose
```

之前踩过坑:`ls ~/Desktop/渔芯科技/6-产品研发/` 看到一堆乱七八糟,真实 RKR 项目在 `/Users/hua/6-产品研发/01-RKR知识库/`。**永远用绝对路径**。

### ⚠️ 陷阱 8: 批量文件系统 mirror ≠ 批量入库;用 API 才稳

**症状**:`rsync` 把 833 个 .md 镜像到 `~/rkr_staging/文档中转站/`,scanner 跑了,但只入库了 ~8 个文档(41642 → 41650)。

**根因**:scanner 对**纯 .md** 文件和**有 .meta.json 配套**的文件处理策略不同:
- 有 `.meta.json` 配套 → 元数据完整 → 顺利入库
- 纯 .md(无元数据)→ 可能入 staging project 后还需 LLM 分类,慢且命中率低

**修复**:
- 单文件 / 少量资料 → 用 `staging_save.py`(自动写 .meta.json)
- 批量大量资料(如 GitHub 全仓库 mirror)→ 用 RKR upload API:
  ```python
  for fmd in files:
      requests.post("http://localhost:8000/api/v1/staging/upload",
          headers={"X-API-Key": "rkr_..."},
          json={"title": ..., "content": fmd.read_text(), "project_id": "a7a325c9-..."})
  ```

### ❌ 错误 9: 业务结果性报告直接放 workspace 而不放 `3-公司项目资料/`(2026-08-03 规则变化)

```python
# ❌ 错误:把"竞品报告"丢到 workspace 当成草稿(2026-08-03 之前习惯)
Path("/Users/hua/rkr_staging/文档库/3-公司项目资料/301-智能体/毛豆-产品交付/workspace/竞品分析/Hydrotech-2026.md").write_text(content)
# 问题 1: 其他 agent(老莫、阿福、小宝)用 staging_query.py 搜不到(workspace 是临时区)
# 问题 2: 同事 agent 之间的知识不可共享
# 问题 3: 这不是"草稿"了,这是"结果性报告",应该放 3-公司项目资料/ 工作空间
```

```python
# ✅ 正确(2026-08-03 起):竞品报告直接放 3-公司项目资料/ 工作空间
Path("/Users/hua/rkr_staging/文档库/3-公司项目资料/303-竞品库/Hydrotech-2026.md").write_text(content)
# 或放到自己 personal zone
Path("/Users/hua/rkr_staging/文档库/3-公司项目资料/301-智能体/毛豆-产品交付/竞品分析/Hydrotech-2026.md").write_text(content)
# 这两份都能被 RKR scanner 顺便索引(虽然不是必需的,主要是工作空间)
```

**判断标准(2026-08-03 新规则)**:
- **业务结果性报告**(竞品分析/产品方案/技术报告/合同/制度/话术/FAQ) → **直接放 `3-公司项目资料/` 工作空间**(`write_file` / `cp` / `mv`)
- **通用知识调研稿 / RAS 专业调研稿 / 新行业调研** → 走 `staging_save.py` 中转站(让 scanner 自动归类到 1-通用/2-专业/4-360行)
- **已收敛的专题页**(`HW-001_滚筒微滤机/`、`BP调研/`、`RAS设备销售/`) → 放 `301-智能体/<agent>/` 下,本身就是工作空间的一部分
- **工具产物**(.json/.csv/.zip/中间计算结果) → 放 `workspace/`,不进 RKR
- **过程稿 / 草稿** → 放 `workspace/`,完成后再决定走中转站还是放工作空间

**快速判断口诀**:
- **"是渔芯业务的结果性报告吗?"** 是 → 放 `3-公司项目资料/` 工作空间
- **"以后要搜得到吗?是归档层知识(1/2/4)吗?"** 是 → 走中转站
- **"还是草稿/工具产物?"** 是 → 放 `workspace/`

**实际踩过的违例**(2026-08-03 扫描发现):
1. `小宝-商务运营/workspace/竞品分析/` 下若干 .md 调研稿 → 孤儿文档
2. `毛豆-产品交付/HW-001_滚筒微滤机/` 等专题页中混有过程稿(应拆出走中转站)
3. `1-通用知识/1.9 大模型/`、`1.9 ai爬虫技术/` 等目录下文件名混乱无 meta.json(早期 agent 直接 `cp` 到文档库遗留)

### ⚠️ 陷阱 10: 不要把 `通用知识库/` 26686 个 .md 或 `cleaned/` 244 个 .txt 当"知识源"

**症状**:agent 想"参考" `~/rkr_staging/文档库/通用知识库/00-总索引.md` 这种文件来引用知识。

**问题**:
- `通用知识库/` 是 RKR 索引库的**导出快照**,每次重建会被覆盖,文件路径不稳定
- `cleaned/` 是 RKR LLM 清洗**中间产物**,下次 RKR 重建会被清空
- 任何 agent 把这些文件的**绝对路径**写进自己的 MEMORY.md / 知识引用 → 重建后全失效

**正确**:
- 引用知识 → 走 `staging_query.py search`(返回的是 RKR 内部 id,稳定)
- 不要把 `~/rkr_staging/文档库/通用知识库/xxx.md` 的路径硬编码到任何长期文件

### ⚠️ 陷阱 11: `302-数据与素材库/` 是二进制仓库,不走 RKR

**说明**:`3D模型/`(3.9G)、`图片/`(893M)、`视频/`(220M)、`工程图纸/`(639M)、`材料库/`(1.6G)、`mech_drawing/`(4.3G) 都是**二进制素材**,RKR 索引不了。

- 写入:直接 `cp` / `mv`(不走 staging)
- 引用:用相对路径(在文档库内部),或对象存储 URL
- **不要**试图把这些目录 mirror 到中转站(9.5G 中转站会被塞爆)

### ⚠️ 陷阱 14(2026-08-26 整理师心跳实测):`stage(agent=...)` 必须是顶层 kwarg,**放进 `meta={}` 里会被静默吞掉**

**症状**:调用 `stage()` 后输出 `Agent: default | Source: research`,而不是你期望的 agent 名。文件**确实入站成功**(中转站有文件、.meta.json 写好),但 agent 字段错了 → scanner 后续的路由/分类规则全失效,文件最终落到默认分类。

**根因(staging_save.py 源码)**:

```python
def stage(
    title: str,
    content: str,
    source: str = "research",
    agent: Optional[str] = None,   # ← 这是顶层 kwarg
    tags: Optional[list] = None,
    subdir: Optional[str] = None,
    meta: Optional[dict] = None,  # ← agent 写进 meta 字典 = 被忽略
):
    if not agent:
        agent = os.environ.get("HERMES_AGENT", "default")  # ← fallback 到 env var 或 default
```

`meta` 字典里的 `"agent": "xxx"` 不会回填到顶层 `agent` 参数,也不会被任何代码读出来 → 静默丢失。

**实测复现(2026-08-26 09:01)**:

```python
# ❌ 错误:agent 写进 meta(静默丢失 → 输出 Agent: default)
result = stage(
    title="...",
    content=...,
    tags=[...],
    meta={"agent": "zhenglishi", "scanner_status": "..."},  # ← agent 字段被忽略
)
# 输出: ✅ 已入站: ... | Agent: default | Source: research

# ✅ 正确:agent 作为顶层 kwarg(显式传)
result = stage(
    title="...",
    content=...,
    source="research",
    agent="zhenglishi",          # ← 顶层 kwarg
    subdir="01-调研资料",
    tags=[...],
    meta={"scanner_status": "..."},  # meta 只放额外元数据,不放 agent
)
# 输出: ✅ 已入站: ... | Agent: zhenglishi | Source: research
```

**防御性写法**(`os.environ` 兜底 + 顶层 kwarg 双保险):

```python
import os
os.environ["HERMES_AGENT"] = "zhenglishi"  # 防 cron 启动时没设 env
from staging_save import stage
stage(title=..., content=..., source="research", agent="zhenglishi", ...)
```

**为什么 meta 里还写 agent 字段**:不影响功能(scanner 走顶层 agent),但**方便后续审计/反向追溯**(从 .meta.json 反查当时调用者意图)。保留无害,删除也行。

**与已有陷阱的关系**:
- 陷阱 13(workspace/knowledge 三路径分离):说的是**落盘路径**问题
- 陷阱 14(agent 静默丢失):说的是**调用签名**问题
- 两个都触发"入站成功但行为不对",但前者是文件位置错,后者是文件元数据错

### ⚠️ 陷阱 13: agent personal zone 内的 `workspace/knowledge/` ≠ staging 中转站 ≠ scanner 自动归档目标(2026-08-24 实战)

**症状**:agent 用 `staging_save.py` 写入了一份合同模板 v1.1,scanner 在 60 秒内确实把中转站原文件处理掉了,但**审计脚本 grep 的不是 `3-公司项目资料/301-智能体/<agent>/workspace/knowledge/`**——4 小时后 cron 审计仍报"P0,109 天未修订"。

**根因(三层路径混在一起)**:
1. **staging 中转站** = `~/rkr_staging/文档中转站/02-生成内容/`(60 秒后被 scanner 自动删)
2. **scanner 自动归档目标** = `~/rkr_staging/文档库/3-公司项目资料/301-智能体/<agent>/knowledge/`(业务报告的"标准"落地路径)
3. **agent 个人工作区** = `<profile_home>/workspace/knowledge/` 或 `~/rkr_staging/文档库/3-公司项目资料/301-智能体/<agent>/workspace/knowledge/`(**审计脚本实际访问的路径**——很多合同模板/政策核验脚本 `KNOW_DIR` 都硬编码这里)

**关键事实**:
- staging_save.py **不保证**把文件 mirror 到 agent 的 `workspace/knowledge/`(它是中转站路径,与 agent personal zone 的 workspace 是两个独立目录)
- scanner 自动归档到 `3-公司项目资料/301-智能体/<agent>/knowledge/` 也**不保证**同步到 `<agent>/workspace/knowledge/`
- 审计脚本 `grep -E "关键词" $KNOW_DIR` 通常指向 `workspace/knowledge/`(因为这才是合同模板等"高频访问"资产的真实存放点)
- **staging 写入 ≠ workspace 归档 ≠ audit 脚本可见**——三步互相独立,缺一不可

**反面案例(2026-08-23 20:33 → 08-24 00:35)**:
- 20:33 cron `staging_save` 写入项目合作协议 v1.1 到 `02-生成内容/`(✓)
- 20:33 scanner 处理中转站,自动归档到 `3-公司项目资料/301-智能体/黑豆-行政财务法务/knowledge/`(**可能成功,但路径不同**)
- 20:33-00:35 之间,审计脚本 grep `<agent>/workspace/knowledge/` 仍显示 v1.0(0 命中,109 天)
- 00:35 才手动 `cp 02-生成内容/<v1.1>.md <agent>/workspace/knowledge/<v1.1>.md` 兜底
- **4 小时错配**期间,审计脚本误报"P0 待承接",导致资源错估 + 后续承接优先级判断偏差

**正确做法(写入双路径自检 SOP)**:

```bash
# 1. staging 写入
python3 ~/.hermes/scripts/staging_save.py \
  --title "<标题>" \
  --content @<file>.md \
  --source report --agent <自己>

# 2. ⚠️ 必须再 cp 一份到 workspace/knowledge/(若审计脚本 grep 那里)
cp ~/rkr_staging/文档中转站/02-生成内容/<file>.md \
   ~/rkr_staging/文档库/3-公司项目资料/301-智能体/<agent>/workspace/knowledge/<file>.md

# 3. ⚠️ 必须再 cp 一份到 3-公司项目资料 knowledge/(若其他 agent 要 RKR 索引)
cp ~/rkr_staging/文档中转站/02-生成内容/<file>.md \
   ~/rkr_staging/文档库/3-公司项目资料/301-智能体/<agent>/knowledge/<file>.md

# 4. 双路径落地自检(grep workspace/knowledge/)
grep -c -E "<关键词>" ~/rkr_staging/文档库/3-公司项目资料/301-智能体/<agent>/workspace/knowledge/<file>.md
# 输出 > 0 才算真正落地

# 5. 在 evolution report 明确"双路径落地状态"
# ✅ 02-生成内容 + workspace/knowledge + knowledge 三路径同步
```

**判断标准**:
| 落地路径 | 谁读 | 写入方式 |
|---|---|---|
| `~/rkr_staging/文档中转站/02-生成内容/` | scanner | `staging_save.py`(60 秒后被删) |
| `3-公司项目资料/301-智能体/<agent>/knowledge/` | RKR 索引 + 其他 agent | scanner 自动 / 手动 cp |
| `3-公司项目资料/301-智能体/<agent>/workspace/knowledge/` | **本 agent 审计脚本** | **必须手动 cp** |

**关键纪律**:
- `staging_save.py` 写入 ≠ agent 可在 workspace 看到
- agent 写入后,**必须**同时 cp 到 `workspace/knowledge/`(本 agent 审计路径)
- 如果业务上要让其他 agent 也能搜到,再加 cp 到 `knowledge/`(RKR 索引路径)
- **进化报告必须明确"双路径/三路径落地状态"**,否则下次 cron 无法判断是否漏归档
- `workspace/knowledge/` 是 agent personal zone 的子目录,**不是 RKR 归档层**,直接 cp 不违反 `3-公司项目资料/` 工作空间规则

**例外**:如果该 agent 的审计脚本 `KNOW_DIR` 指向 `3-公司项目资料/301-智能体/<agent>/knowledge/`(而非 `workspace/knowledge/`),则 cp 到那一个即可——**先看审计脚本再决定 cp 哪个**。

### ⚠️ 陷阱 12: `304-公司运营/` 16 个子目录里有 4 个空白(`HR/`、`知识产权/`、`财务/`、`销售/`)

> 补充(2026-08-13)：已新增激活目录 `公司证件/`，营业执照 PDF+JPG 归档于此。公司证件(执照/银行账户/收款码等)统一归 `304-公司运营/公司证件/`，详见 `references/company-certificates-archive.md`。

**状态**:4 个目录是占位空目录,等待激活;`销售/` 与 `销售与市场营销/` 重复。

**规则**:
- 新建运营资料时,先确认目标子目录已激活;未激活的写到 `产品研发全链条/` 或 `B2B工业品营销/` 等"已激活"目录
- 不要往空白目录里写(后续清理时会被判定为"误写")
- 重复目录(`销售/` vs `销售与市场营销/`)一律写带后缀的、已激活的那个

---

## 监控与排错

```bash
# RKR scanner 实时日志
docker logs rkr-staging-pool --tail 50 --follow

# 中转站现状(看哪些文件还没被处理)
ls -lt ~/rkr_staging/文档中转站/ | head

# 文档库现状
ls -lt ~/rkr_staging/文档库/ | head

# RKR API 健康
python3 ~/.hermes/scripts/staging_query.py stats
```

---

## 历史资料批量迁移(从旧位置 → 中转站)

**场景**:agent 以前生成过资料,散落在 `~/Desktop/渔芯科技/*` 或 `~/.hermes/profiles/<agent>/home/...`,需要统一搬到中转站。

**用 `migrate_agent_artifacts.py`**:

```bash
# Dry run 先看数量
python3 ~/.hermes/scripts/migrate_agent_artifacts.py --dry-run

# 全量执行
python3 ~/.hermes/scripts/migrate_agent_artifacts.py --execute

# 只迁 desktop / 只迁 profiles
python3 ~/.hermes/scripts/migrate_agent_artifacts.py --execute --only desktop
python3 ~/.hermes/scripts/migrate_agent_artifacts.py --execute --only profiles

# 测试用(小批量)
python3 ~/.hermes/scripts/migrate_agent_artifacts.py --execute --limit 100
```

**默认扫描范围 + 排除规则**(详见 `references/migration-rules.md`):

| 来源 | 包含 | 排除 |
|---|---|---|
| `~/Desktop/渔芯科技/` | .md/.json/.pdf/.docx etc. | `00-FindEra寻元/`(**寻元不动**) |
| `~/.hermes/profiles/<agent>/home/` | 同上 | `Library/`、`node_modules/`、`.cache/`、`site-packages/`、`__pycache__/`、`.git/`、`dist/` |
| `~/Desktop/` 顶层 | 同上 | 同上 |

**关键行为**:
- **复制而非移动**(原文件保留)
- 每个 .md 加 `<!-- migration_meta -->` frontmatter(含 `source_path` / `agent` / `migrated_at`)
- 每个文件配套 `.meta.json`(RKR scanner 友好的元数据)
- **路径镜像**:`<原路径相对>` → `migration_<日期>/<来源>/<相对路径>`

**已验证规模**:14,879 文件 / 469 MB / 0 错误(2026-07-30 一次跑完)。

⚠️ **脚本陷阱**(亲历):不要用 `sorted(set(files))`,那会按 ASCII 排序把 `/.hermes/...` (47 < 68 `D`) 排到 `~/Desktop/...` 前面,导致 `--limit N` 截断错乱。**正确做法**:`list(dict.fromkeys(files))` 保留采集顺序(desktop → profiles)。

---

## GitHub 仓库 → 中转站 同步

**场景**:GitHub 上的 `openclaw-cn-dev/yuxin-skills` 仓库(Hermes/Claude/Codex 跨 agent 的 skills)需要 mirror 到 RKR 中转站入库。

**用 `sync_yuxin_skills_to_staging.sh`**:

```bash
# 手动同步一次
~/.hermes/scripts/sync_yuxin_skills_to_staging.sh
```

**行为**:
- `git pull` 增量到 `/tmp/yuxin-skills-sync-cache/`
- `rsync -a --exclude='.git'` mirror 到 `~/rkr_staging/文档中转站/yuxin-skills-YYYYMMDD/`
- 健康检查:文件数 < 600 自动重 mirror(防 scanner 误清)

**已验证规模**:833 文件 / 10MB(claude-code 33 + hermes 230 + codex 14 + drawing-skills 8 skills)。

> 这个 pattern 跟 `codex_self_evolution.py` 里"GitHub sync 到 yuxin-skills/codex/"的 cron 已注册的逻辑是相同的(每小时跑一次 `6dfcbdeac7bf`)。

---

## Cron 自动监控

### 已注册的 cron job

| job_id | schedule | 任务 | 来源 |
|---|---|---|---|
| `6dfcbdeac7bf` | `every 60m` | Codex 配置 → yuxin-skills GitHub 同步 | `codex_github_sync.sh` |
| `955afce881f0` | `0 3 * * 0`(每周日 3:00)| Agent 历史资料 → RKR 中转站(增量) | `migrate_incremental.sh` |
| `e2052c9b44c8` | `0 9 * * 1`(每周一 9:00)| **工作空间每周审计**(3-公司项目资料/ 下 7 天内新增/修改) | `audit_workspace.py`(有变更才发,无变更静默) |

**工作空间审计 cron 设计要点**(`e2052c9b44c8`):

- 跑脚本 `~/.hermes/scripts/audit_workspace.py`(也作为 skill 标准资产放在 `scripts/audit_workspace.py`)
- no_agent=True(纯脚本,LLM 不介入)
- 审计范围:`~/rkr_staging/文档库/3-公司项目资料/` 下,排除 RKR 资源(awesome-*/cad_samples/material_library/mech_drawing 等)+ EDAI 测试 + 个人脚本目录
- 报告输出:每个 agent 写了多少文件 + 文件名清单 + 大小 + 类型分布
- 静默策略:**有变更才发报告,无变更静默**(no_agent 模式下空 stdout → 不发飞书)
- 用途:玉芬每周一 9:00 拿到审计报告后,扫描异常(比如某 agent 突然大量删文件)立即通知华哥

**为什么需要审计**:
- `3-公司项目资料/` 是工作空间(可写),没有 RKR scanner 的天然索引
- 同事写文件没有强制记录,变更不可见
- 每周审计让华哥和玉芬"看见"工作空间的实际变化,异常时立即响应

**增量迁移 cron 细节**:
- 调 `migrate_incremental.sh`(wrapper bash)→ 调 `python3 migrate_agent_artifacts.py --incremental --execute`
- manifest 跟踪:`~/.hermes/state/migration_manifest.json`(用 `mtime + size` 做 key)
- 日志:`~/.hermes/logs/migrate_incremental_cron.log`
- 触发时检查 7 个 agent profile + `~/Desktop/渔芯科技/` 的资料类文件
- **不动寻元**(`00-FindEra寻元/` 排除)+ **不开发项目**(开发项目代码不在扫描范围内)

### 注册新 cron 的模板

```bash
# 注册 hourly 轻量 sync(已有 cron 可复用)
cronjob action=list  # 看现有 job
# 类似 6dfcbdeac7bf / 955afce881f0 的 wrapper pattern(`script=` 传相对路径,no_agent=True)
```

---

## 关联

- **RKR 项目根**: `/Users/hua/6-产品研发/01-RKR知识库/`
- **RKR staging 监听**: `backend/app/tasks/local_staging_scanner.py`(每 60 秒扫一次,自动入库 + 删原文件)
- **RKR staging 配置**: `backend/app/services/staging_config.py` (`DEFAULT_STAGING_DIR = ~/rkr_staging/文档中转站`)
- **现有 RKR API 集成参考**: `~/.hermes/skills/research-collection/references/findera-rkr-pipeline.md`
- **FindEra 保留 API 模式**: 走 `POST /api/v1/staging/upload` (X-API-Key) — **不要让寻元改走 staging 文件系统**

## References(本目录下)

- `references/***SECRET***.md` — **v1.4.1 新增**:agent personal zone 内 `workspace/knowledge/` 与 staging 中转站、scanner 归档目标的**三路径分离**实战教训 + 强制三路径同步 SOP(2026-08-24 实战:08-23 项目合作 v1.1 漏归档 4h)
- `references/huage-idea-recording.md` — 华哥想法记录与归档工作流（5要素结构 + staging_save.py --tag 想法 + 飞书回执三段式 + 记忆同步）
- `references/scanner-architecture.md` — RKR scanner 详细时序、配置来源、故障行为
- `references/company-certificates-archive.md` — 公司证件(营业执照等)归档位置 + 证件文件真实存放处(微信接收文件,非"素材图片") + 扫描件 pdftoppm→vision 读取技巧(2026-08-13 建立)
- `references/migration-rules.md` — `migrate_agent_artifacts.py` 完整扫描/排除规则表
- `references/findera-exception.md` — 为什么 FindEra 不走 staging 文件系统
- `references/hermes-profile-env-pitfall.md` — `$HOME` 被 Hermes profile 改写的陷阱 + 修复
- `references/document-library-layout.md` — `~/rkr_staging/` 三层目录树与各子目录职责(2026-08-03 实测)
- `references/agent-personal-zone.md` — 5 个同事 agent 在 `301-智能体/<name>/` 下的 personal zone 规范
- `references/agent-rollout-procedure.md` — 5 同事 AGENTS.md 下发流程 + 已知坑 + 各 agent 业务特殊说明(2026-08-03 建立)
- `references/***SECRET***.md` — 5 个 agent 工作空间归位操作手册 v2:4 类归位决策(A 保留/B 走中转/C 清理/D 留最新)+ 各 agent 任务清单 + 严禁清单(2026-08-03 玉芬固化,基于 5 个 personal zone 扫描结果)

## Templates

- `templates/agent-workspace-sop.md` — 给 5 个同事 AGENTS.md / TOOLS.md 用的"路径 SOP"模板(可直接复制粘贴)
- `templates/task-dispatch-to-agent.md` — 5 个同事"任务派发"模板,放在 `3-公司项目资料/301-智能体/<agent>/` 根目录,让同事下次启动看到任务清单(2026-08-03 玉芬建立,基于 v2 归位任务派发)

## Scripts

- `scripts/audit_workspace.py` — 工作空间每周审计脚本:扫描 `3-公司项目资料/` 7 天内新增/修改文件,按 agent 分组,生成 markdown 报告(有变更才输出,no_agent=True 静默模式)。配套 cron job_id `e2052c9b44c8`(每周一 9:00)

---

> 🤖 玉芬维护 · 2026-08-24 · v1.4.1
> 📌 适用 agent: 玉芬/毛豆/阿福/黑豆/老莫/小宝/整理师/宽博士 + 任何新 agent
> 🆕 v1.4.1: **新增陷阱 13** —— `agent personal zone 内 workspace/knowledge/` 与 staging 中转站、scanner 归档目标 是**三个独立路径**;staging_save 写入不等于 workspace 可见,审计脚本 grep 的 KNOW_DIR 通常是 workspace/knowledge/,必须手动 cp 兜底。实战案例:08-23 20:33 项目合作 v1.1 staging 写入但 4h 内审计脚本仍报 P0(误判),08-24 00:35 才补 cp。配套"双路径/三路径落地自检 SOP"写入进化报告模板。
> 🆕 v1.4.0: 微调 — 补 `references/agent-rollout-procedure.md`(5 同事 AGENTS.md 下发流程 + 已知坑);新增 cron `e2052c9b44c8`(工作空间每周审计);新增 `scripts/audit_workspace.py`(审计脚本);新增 `templates/task-dispatch-to-agent.md`(任务派发模板)
> 🆕 v1.3.0: **关键架构澄清** — `3-公司项目资料/` 是**可写工作空间**(华哥 2026-08-03 明确,留给同事放"结果性报告"),而 `1-通用知识/` `2-专业知识/` `4-360行项目调研/` 仍是 RKR 归档层(只读,新资料走中转站让 scanner 自动入)。v1.0–v1.2 把整个文档库当作只读归档层是误读,现已修正。配套更新:核心心法段、"2 层 + 1 工作空间"架构段、错误 1 / 错误 9 重写、"用户硬性约束"改为"仅适用于归档层"、5 同事 AGENTS.md 全部按 v2 重下发、staging_save.py SOP 拆为 A(业务报告走工作空间)/B(归档资料走中转站)两类。
> 🆕 v1.2.0: 新增"3 层架构(写/读/个人)"心法 + pitfall 9/10/11/12 + 2 references + 1 template
> 📝 v1.1.0: 批量迁移 + GitHub 同步 + cron 模式 + 4 个 references
> 📝 v1.0.0: 初版,写/读双路径 + 8 个常见陷阱
