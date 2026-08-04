---
name: yuxin-team-management
description: |
  渔芯 9-agent 集中管理方法论（2026-08-01 整理）。
  适用场景：华哥需要"重新整理同事 agent 系统文件"、"建集中目录树管理所有同事"、
  或者其他类似"multi-agent 系统的 profiles 散落管理问题"。
  触发条件：用户提到"重新整理 / 集中管理 / 统一视图 / 同事 agent 整理 / 团队管理视图"。
related_skills:
  - multi-agent-local-orchestration   # 协作后端（registry / messages / SOP）
  - hermes-gateway-profile-ops        # runtime / launchd / plist / LLM 路由
  - multi-agent-team-architecture     # 9-profile 拓扑 / 记忆分层
---

# 渔芯 9-Agent 集中管理（2026-08-01 整理）

## 一、问题背景

**散落状态（2026-08-01 之前）：**
- 9 个 agent 各自整套 Hermes 运行时，分布在 `~/.hermes/profiles/<id>/` 8 个独立目录
- 每个 profile 复制了完整 Hermes 运行时（state.db 1-6GB + sessions_archive 80-650MB + skills 27-264 个）
- 元数据散落在 3 个地方：
  - `~/.hermes/profiles/<id>/SOUL.md`（人设，每份 430-750 字节）
  - `~/.hermes/orchestration/agents/<id>.md`（详细档案，3-6KB）
  - `~/.hermes/orchestration/registry.yaml`（注册表 SOT）
- 异常文件：`<NAME>` 错误 launchd 目录、`.env.bak*` 多份历史备份、`config.yaml.bak*` 旧版

**问题：** 8 个同事 Agent 难以一眼看清、状态混乱、清理无标准。

## 二、解决方案：symlink 视图层（不破坏 runtime 隔离）

**核心原则：**
1. **隔离优先**：每个 profile 作为独立 Hermes runtime 隔离单元保留（独立 LLM key、独立飞书 bot、独立 state.db）
2. **集中视图 thin**：`~/yuxin-team/` 只做 symlink + 脚本，不复制任何数据
3. **单一来源**：详细档案统一在 `~/.hermes/orchestration/agents/<id>.md`，profile 内部 SOUL.md 是人设

## 三、最终结构

```
~/yuxin-team/                                     新增集中管理视图
├── README.md                                       总览
├── AGENTS.md                                       9 个 agent 快速索引表
├── registry.yaml → ~/.hermes/orchestration/registry.yaml
├── agents_meta/    → ~/.hermes/orchestration/agents/  (9 个 .md)
├── shared_state/   → ~/.hermes/orchestration/shared_state/
├── sops/           → ~/.hermes/orchestration/sops/  (6 个 SOP)
├── dashboard/      → ~/.hermes/orchestration/dashboard/
├── events/         → ~/.hermes/orchestration/events/
├── reports/        → ~/.hermes/orchestration/reports/
├── logs/                                              (start.sh 启动日志)
├── scripts/                                           管理脚本
│   ├── status.sh                                       状态查看 + --sync 同步 registry
│   ├── start.sh                                        启动 agent gateway
│   ├── stop.sh                                         关闭 agent gateway
│   └── sync_registry.sh                                同步 registry.yaml
└── agents/                                          8 个 agent 各自视图
    └── <id>/
        ├── README.md                                   本 agent 人类视图
        ├── AGENT.md → ~/.hermes/orchestration/agents/<id>.md
        ├── profile/  → ~/.hermes/profiles/<id>/        (Hermes runtime)
        ├── workspace/ → ~/.hermes/orchestration/workspace/<id>/
        └── messages/  → ~/.hermes/orchestration/messages/<id>/  (inbox/outbox)
```

注意：yuxin (玉芬) 是 default profile，它的 SOUL.md 在 `~/.hermes/SOUL.md` 而非 `~/.hermes/profiles/default/SOUL.md`。所以 `~/yuxin-team/agents/yuxin/profile/` symlink 指向 `~/.hermes/` 根目录。

## 四、关键操作步骤

### Step 1：清理垃圾
```bash
# 删除 launchd 错误创建的 <NAME> 目录（如有）
rm -rf ~/.hermes/profiles/<NAME>

# 删除所有 profile 的 .env.bak* 旧备份
for p in default afu quant xiaobao zhenglishi maodou laomo heidou; do
  rm -f ~/.hermes/profiles/$p/.env.bak*
  rm -f ~/.hermes/profiles/$p/config.yaml.bak*
done
rm -f ~/.hermes/.env.bak* ~/.hermes/config.yaml.bak*
```

### Step 2：建目录骨架
```bash
TEAM=~/yuxin-team
mkdir -p $TEAM/{agents,shared_state,sops,scripts,workspace,logs}
for id in yuxin maodou laomo afu xiaobao heidou quant zhenglishi; do
  mkdir -p $TEAM/agents/$id
done
```

### Step 3：建 symlink 树（**坑：先 ln -sfn，覆盖空目录**）
```bash
# 共享资源
ln -sfn ~/.hermes/orchestration/shared_state  ~/yuxin-team/shared_state
ln -sfn ~/.hermes/orchestration/sops          ~/yuxin-team/sops
ln -sfn ~/.hermes/orchestration/registry.yaml ~/yuxin-team/registry.yaml
ln -sfn ~/.hermes/orchestration/agents        ~/yuxin-team/agents_meta
ln -sfn ~/.hermes/orchestration/dashboard     ~/yuxin-team/dashboard
ln -sfn ~/.hermes/orchestration/events        ~/yuxin-team/events
ln -sfn ~/.hermes/orchestration/reports       ~/yuxin-team/reports

# 每个 agent
for id in yuxin maodou laomo afu xiaobao heidou quant zhenglishi; do
  AGENT=$TEAM/agents/$id
  # 关键: 如果 AGENT/profile 已存在且不是 symlink，先 rm
  [ -d "$AGENT/profile" ] && [ ! -L "$AGENT/profile" ] && rm -rf "$AGENT/profile"
  [ -d "$AGENT/workspace" ] && [ ! -L "$AGENT/workspace" ] && rm -rf "$AGENT/workspace"
  [ -d "$AGENT/messages" ] && [ ! -L "$AGENT/messages" ] && rm -rf "$AGENT/messages"
  
  # yuxin 指向 ~/.hermes/ 根目录，其他指向 ~/.hermes/profiles/<id>/
  if [ "$id" = "yuxin" ]; then
    ln -sfn ~/.hermes $AGENT/profile
  else
    ln -sfn ~/.hermes/profiles/$id $AGENT/profile
  fi
  ln -sfn ~/.hermes/orchestration/workspace/$id $AGENT/workspace
  ln -sfn ~/.hermes/orchestration/messages/$id $AGENT/messages
  ln -sfn ~/.hermes/orchestration/agents/$id.md $AGENT/AGENT.md
done
```

**坑：`ln -sfn` 不会覆盖已存在的目录（只覆盖 symlink）。必须先 `rm -rf` 空目录。**

### Step 4：生成每个 agent 的 README.md
```python
import yaml, subprocess
with open('/Users/hua/.hermes/orchestration/registry.yaml') as f:
    cfg = yaml.safe_load(f)
# 模板见下方"附录：Python template"
```

**坑：写 heredoc 字符串时，`python3 << EOF`（无引号 EOF）会让 bash 先解释 `$var` 和 `~`！必须用 `python3 << 'PYTHON_END'`（带引号）防 bash 注入。** 完整事件回放 + 修复代码 + 反模式表见 `references/2026-08-01-bash-heredoc-readme-pollution.md`。

### Step 5：管理脚本
放 4 个 sh 脚本到 `~/yuxin-team/scripts/`，所有都用 `chmod +x`。

**status.sh 关键点：**
- yuxin 是 default gateway，命令行是 `gateway run --replace`（不带 `--profile`）
- 其他 agent 是 `gateway run --profile <id> --replace`
- 必须用 `ps -ef | grep -v "\-\-profile"` 区分 yuxin

### Step 6：同步 registry.yaml 的 current_status
```python
def get_gw_status(profile_id):
    if profile_id == 'yuxin':
        for line in ps_output:
            if 'hermes_cli' in line and 'gateway' in line and '--profile' not in line:
                return f'active (PID <pid>)'
        return 'inactive'
    else:
        # pgrep -f "hermes_cli.*gateway.*--profile <id>"
        ...
```

## 五、验证清单

- [ ] 9 个 agent 都能通过 `~/yuxin-team/agents/<id>/SOUL.md` 看到
- [ ] 9 个 agent 都能通过 `~/yuxin-team/agents/<id>/AGENT.md` 看到详细档案
- [ ] `~/yuxin-team/scripts/status.sh` 正确显示所有 8 个 agent 的 gateway 状态
- [ ] `~/yuxin-team/scripts/start.sh <id>` 能启动 gateway
- [ ] `~/yuxin-team/scripts/stop.sh <id>` 能关闭 gateway
- [ ] `registry.yaml` 的 `current_status` 已同步实际状态
- [ ] `~/yuxin-team/` 总大小 < 100KB（因为都是 symlink）
- [ ] 没有旧的 `.env.bak*`/`config.yaml.bak*` 文件
- [ ] 没有 `<NAME>` 错误目录

## 六、不做的事

- ❌ 不合并 profile runtime（state.db / sessions / skills 不能合并）
- ❌ 不改 profile 内部 SOUL.md 为 symlink（runtime 启动时可能不支持）
- ❌ 不 push `~/yuxin-team/` 到 GitHub（含 symlink 不能 git 跟踪）
- ❌ 不动 cron/jobs.json（每个 profile 独立 cron 各自管理）

## 七、附录：Python 模板

```python
import yaml, subprocess

AGENT_TEMPLATE = """# {name} ({aid})

**角色**：{role}  
**平台**：{platform}  
**Gateway**：{gw_status}  
**LLM**：{llm}

## 职责
{responsibilities}

## 关键路径

| 用途 | 路径 |
|------|------|
| 详细档案 | [AGENT.md](AGENT.md) |
| 人设 | [profile/SOUL.md](profile/SOUL.md) |
| ...

## 常用命令

```bash
~/yuxin-team/scripts/status.sh {aid}
~/yuxin-team/scripts/start.sh {aid}
~/yuxin-team/scripts/stop.sh {aid}
```
"""

with open('/path/to/registry.yaml') as f:
    cfg = yaml.safe_load(f)
for a in cfg['agents']:
    if a['id'] == 'wangcai': continue
    if a['id'] == 'yuxin': continue
    md = AGENT_TEMPLATE.format(...)
    with open(f'/Users/hua/yuxin-team/agents/{aid}/README.md', 'w') as f:
        f.write(md)
```

## 八、效果对比

| 维度 | 整理前 | 整理后 |
|------|--------|--------|
| 9 个 agent 管理入口 | 8 个分散目录 + 1 个 registry.yaml | 1 个 `~/yuxin-team/` |
| 状态查看 | `ps -ef \| grep hermes` 手动 | `~/yuxin-team/scripts/status.sh` |
| 启动/关闭 agent | `python3 -m hermes_cli.main gateway run --profile <id> --replace` | `~/yuxin-team/scripts/start.sh <id>` |
| 同步注册表 | 手动编辑 | `~/yuxin-team/scripts/status.sh --sync` |
| 冗余文件 | 32 份 `.env.bak*` + 5 份 `config.yaml.bak*` | 全部清理 |
| 错误目录 | 1 个 `<NAME>` 空目录 | 删除 |

---
**整理者**：yuxin (玉芬)
**整理时间**：2026-08-01
**整理方式**：华哥授权"按我专家意见处理"

---

## 附录:渔芯三大核心战略 v2(2026-08-03 华哥拍板)

**触发场景**:华哥说"重新全面盘点公司资产,优化整体架构" → 玉芬提出"收敛 11 demo 为 5 主力 + 新增 2 profile(社小+训练师)"建议 → **华哥否决,重新明确战略**。本节固化 8/3 决策,避免下次玉芬再犯"自动收敛"错误。

### 一、战略层(华哥直接拍板的硬性规则)

| 规则 | 含义 | 反例(玉芬踩过的) |
|---|---|---|
| **R1 多产品并行孵化,严禁自动收敛** | "11 demo 都保留独立产品,渔芯社区的产出物" | 玉芬 §5.2 提"收敛为 5 主力" → **否决** |
| **R2 待开发项目 ≠ 内部代号,保留目录** | 灵枢/天枢/v4_concept 都是真实项目待开发,不是空目录 | 玉芬猜测是"内部代号" → **全部猜错** |
| **R3 跨界 demo 可以保留** | 老张有汤方(中医养生)700MB 保留作跨界 demo | 玉芬问"留/弃/独立" → **保留** |
| **R4 项目编号保留旧编号,不重排** | 06/20/23/27 全部保留 | 玉芬提"重排 10/20/30/40" → **未明确否决但默认保留** |
| **R5 战略决策不接受 LLM 自行收敛** | 多产品/多项目/多版本/多分支都是常态,LLM 不要"觉得太乱就合并" | 玉芬 §5.2 的"5 主力"是典型反模式 |

### 二、核心 1 / 核心 2 / 核心 3 三大核心边界

```
核心 1 渔芯产品      →  RAS 循环水设备(硬件 9 大类)
                       5 同事完整服务(毛豆/小宝/阿福/黑豆/老莫)
                       健康度 90% 现金牛,主要优化项目目录裁剪

核心 2 渔芯社区      →  AI/工作流/网站/App(11+ 独立产品)
                       新增 community profile 统一对外品牌+销售+CRM
                       **不干涉各产品内部节奏**(每个产品 owner 自己做主)
                       玉芬/毛豆/老莫/华哥 都是某些产品的 owner

核心 3 训练智能体    →  训练专业领域 agent
                       **不新增 profile**,改为"嵌入式训练"模式
                       每个 agent 在做本职工作时,边干边训练自己领域智能体
                       训练产物汇入 30-渔芯智能体/ 共享仓库
                       玉芬每周审各 agent 训练进度
```

### 三、嵌入式训练模式(华哥原话,玉芬已固化)

> **华哥原话**:"每个同事在工作的同时也在训练与总结,就是我要的专业领域的智能体"

**实操含义**:
- 毛豆(产品交付+3D)→ 训练**产品经理智能体** + **CAD 出图智能体**
- 小宝(销售+自媒体)→ 训练**销售智能体** + **内容运营智能体**
- 阿福(客服)→ 训练**客服智能体**
- 黑豆(行政+财务+法务)→ 训练**合规审查智能体**
- 老莫(知识库+测试)→ 训练**运维智能体** + **知识库整理智能体**
- 宽博士(量化)→ 训练**量化研究智能体**
- 学习助手 → 训练**资料整理智能体**
- 玉芬 → 训练**运营管理智能体**(团队协调 + 自进化)

**训练产物归宿**:`~/6-产品研发/30-渔芯智能体/<agent_name>/<智能体名>/`(不归各 agent personal zone,归共享仓库)

**与 22-出图智能体训练 的关系**:
- 22-出图智能体训练 是核心 3 的**首个标杆产品**(已成熟,2.4GB,69 tests)
- 各 agent 训练自己的智能体时,**复用 22-出图智能体训练 的 self_evolution 框架**(00-公共组件/self_evolution/)
- 未来抽象为通用训练平台:不只服务 CAD,服务所有领域

### 四、新建 community profile(2026-08-03)

**profile 位置**:`~/.hermes/profiles/community/`

**核心职责**:
- 统一对外品牌(logo/VI/品牌故事)
- 统一销售通道(官网/电商/抖音/微信)
- 统一 CRM(飞书多维表格 + 微信支付)
- 月度产品月报 → 玉芬审 → 华哥

**不干涉**:
- ❌ 各产品内部开发节奏
- ❌ 各产品技术选型
- ❌ 各产品定价(除非涉及对外统一价)

**配对的 13 个产品**:
| 产品 | 路径 | 产品 owner |
|---|---|---|
| KnowHow AI 学习平台 | `23-KnowHow知渔/` | 玉芬 |
| 渔芯常驻语音助手 YVA | `21-语音交互/` + `yva-mvp/` | 玉芬 |
| FindEra 知识采集智能体 | `00-FindEra寻元/` | 老莫 |
| GEO Monitor | `25-GEO/` | 玉芬 |
| HG-运营中枢 | `27-HG-运营中枢/` | 玉芬 |
| 应神 RAG | `25-应神/` | 玉芬 |
| 内容运营 Agent | `26-内容运营Agent/` | 玉芬 |
| HG-业务工作台 | `28-HG-业务工作台/` | 玉芬 |
| 老张有汤方(中医养生) | `27-老张有汤方/` | 玉芬 |
| 八卦预测工具(国际版) | `6-产品研发/八卦预测工具-国际版/` | 玉芬 |
| 灵枢 LingShu(待开发) | `20-灵枢LingShu/` | 待定 |
| 天枢 TianShu(待开发) | `24-天枢TianShu/` | 待定 |
| v4_concept(待开发) | `6-产品研发/v4_concept/` | 待定 |

### 五、玉芬下次做战略方案的反思

**反模式**(玉芬 8/3 踩过):
- ❌ **提"5 主力"建议** — 假设华哥想要"少而精",实际华哥想要"多而活"
- ❌ **提"2 个新 profile"** — 假设每个核心需要专属人,实际核心 3 嵌入式训练即可
- ❌ **猜测项目性质** — 灵枢/天枢/v4 被猜成"内部代号",实际都是真实项目
- ❌ **直接重排项目编号** — 没问就提"10/20/30/40 重排",实际华哥要保留

**正模式**:
- ✅ **盘点先行,建议靠后** — 先把现状如实列出来(11 demo,28 项目),让华哥自己决定
- ✅ **疑问前置** — "立刻需要华哥拍板 5 件事" 表格,让华哥填表回答
- ✅ **承认错误立即改** — 华哥否决后,2 小时内把决策 v2 同步到方案,不解释不辩护
- ✅ **"嵌入式训练"等新概念** — 华哥说出来时立刻记到 skill,不发明"训练师 profile" 这种新概念

**下次遇到类似"多产品矩阵设计/项目收敛"任务的正确姿势**:
1. **默认假设:多项目并行为常态,不要主动收敛**
2. **盘点时按"是否要保留"列清单**,而不是按"哪些要合并"列
3. **疑问前置**,把所有需要华哥决策的点列成 1 张表,让华哥按表回答
4. **决策 v2 章节** — 任何"策略类对话"都加 "华哥决策 v2" 章节固化结果

---

## 附录:渔芯三大核心战略 v3(2026-08-03 20:00+ 增补 — 嵌入式训练 + 三层资源 + Dashboard + Token 管理)

**触发场景**:华哥 8/3 20:00 通报**公司第 3 核心 = 各专业领域的智能体团队**。三个新目标:
1. 基础/公共/专业资源分层结构化管理
2. 方便将来蒸馏或复制整个 agent 团队
3. 开发公司运行状态控制面板

本节固化 8/3 增补内容,避免下次玉芬在战略方案里遗漏"分层资源 / Dashboard / Token 管理"。

### 一、核心 3 嵌入式训练 = 边干边训练(华哥原话)

> **华哥原话**:"每个同事在工作的同时也在训练与总结,就是我要的专业领域的智能体"

**与 v2 的关键差异**:
- v2 章节(三) 提到"嵌入式训练"是模糊概念
- v3 明确:**核心 3 = 所有 agent 训练行为的总和**,无独立 profile,产物汇入共享仓库

**每个 agent 训练的智能体**(汇入 `30-渔芯智能体/<agent_name>/`):
| Agent | 训练领域 |
|---|---|
| 毛豆 | 产品经理智能体 + CAD 出图智能体 |
| 小宝 | 销售智能体 + 内容运营智能体 |
| 阿福 | 客服智能体 |
| 黑豆 | 合规审查智能体 |
| 老莫 | 运维智能体 + 知识库整理智能体 |
| 宽博士 | 量化研究智能体 |
| 学习助手 | 资料整理智能体 |
| 玉芬 | 运营管理智能体 |

**关键资源**:复用 `00-公共组件/self_evolution/` 框架(原 22-出图智能体训练 的核心)

### 二、四层资源结构化(L0/L1/L2/L3 — **不是 L1/L2/L3 记忆分层**)

⚠ **命名冲突警告**:已有的 L1/L2/L3 记忆分层(见 multi-agent-team-architecture §l1-l2-l3-memory)是**记忆容量**分层;这里 L0/L1/L2/L3 是**资源归属**分层。两者概念不同,必须区分。

| 层 | 含义 | 物理位置 | 谁改 |
|---|---|---|---|
| **L0 平台基础** | Hermes 平台本身,8 agent 共享 | `~/.hermes/{bin,scripts,config.yaml,.env,plugins,hooks}` | 玉芬 |
| **L1 公共资源** | 跨 agent 复用的 skills/scripts | `~/.hermes/skills/` + `~/.hermes/profiles/_shared/` | 玉芬审,任 agent 推荐 |
| **L2 Agent 基础** | 每个 agent 必有的"骨架" | `~/.hermes/profiles/<agent>/` | 玉芬 |
| **L3 Agent 专业** | 该 agent 自己领域的知识/训练数据 | `~/.hermes/profiles/<agent>/{skills,knowledge,workspace,training_data}/` | Agent 自己 |

**每个 profile 的标准 8 件套**(蒸馏/复制的基本单元):
```
profile.json + AGENTS.md + .env + memory/ + cron/ + launchd + skills/ + workspace/
```

**profile.json schema**(标准元数据):
```json
{"name":"maodou","role":"产品交付/3D","layer":"L3",
 "skills_count":79,"skills_distillable":24,
 "memory_count":15,"cron_count":2,"uptime_days":83,"core":"core1"}
```

### 三、蒸馏 / 复制 / 打包 SOP

**蒸馏(Distillation)** = 抽出通用能力到 L1
- 触发:每周 cron `a09e4917b16e` 玉芬自进化扫描
- 流程:扫描 L3 → 检测 frontmatter 重复 → 玉芬审 → 移到 L1 + 软链
- 预期:421 → 200 skills(削减 50%)

**复制(Replication)** = 整包搬到新机器
- 单元:`<agent>_v<YYYYMMDD>.tar.gz`
- 命令:`tar czf maodou_v20260803.tar.gz -C ~/.hermes/profiles maodou/`
- 还原:解压 + 装 LLM key + 启动 launchd

**团队级蒸馏 v1**(终极目标):
- 8 profiles → 1 个"渔芯 Agent 团队模板" tarball
- 含 L0/L1/L2/L3 四层
- 用途:新员工入职立即可用 8 个 agent

### 四、公司运行状态控制面板(YuXin Dashboard)

**技术栈**:Streamlit(华哥本机已有 `.streamlit/` 配置)
**端口**:8765
**目录**:`~/hermes/dashboard/`

**5 大模块**(8 agent × 4 维度 = 32 数据点):
1. **📊 8 Agent 总览** — skills/cron/uptime 一屏
2. **💰 Token 用量**(今日) — 每 agent vs 预算,超 80% 飞书告警
3. **📚 Skills 健康度** — L1/L3 数量、7 天未修改、可蒸馏候选
4. **🧠 Memory 健康度** — 44 memory 大小/最后访问
5. **⏰ Cron 状态** — 51 任务 ok/err + 下次运行倒计时

**飞书推送**:每日 9 点巡视 + 每周一 8 点周报 + 24h 未活动/token 超 80%/cron err 连续 3 次告警

### 五、大模型分配与 Token 管理(2026-08-03 20:30 增补)

**4 个模型池**:
| 模型池 | 模型 | Key | 用途 |
|---|---|---|---|
| minimax 主 | MiniMax-M3 | `sk-cp-...`(包月) | 日常对话、调研、生成 |
| deepseek-cn 兜底 | deepseek-v4-pro | `sk-960...` | minimax 限额时 fallback |
| ollama-coder 本地 | qwen2.5-coder:7b | ollama | 离线兜底 |
| 火山 Ark 豆包 | doubao-seed-2-0-code 等 | `ark-18d7...` | 代码生成、图片、视频 |

**Per-Agent 日预算**(合计 5.7M tokens/天):玉芬 800K + 毛豆 1.2M + 小宝 600K + 阿福 600K + 黑豆 400K + 老莫 800K + 宽博士 400K + 学习助手 400K + community 500K

**Key 单源化**(消除 54 个 .env 副本):
- 抽到 `~/.hermes/secrets/.env.common`
- 8 个 profile .env 改成 `source ~/.hermes/secrets/.env.common`

**Fallback 链**:`minimax → deepseek-cn → ollama-coder`(触发时静默 + 后台日志,Dashboard 显示)

**token_usage_alert cron**(每日 23:00):`python3 ~/.hermes/scripts/token_usage.py --today --per-agent`,超 80% 飞书告警

### 六、本次会话(8/3)产生的 4 份方案文件

| 方案 | 路径 |
|---|---|
| 同事工作目录与调研存储 | `~/hermes/ideas/2026-08-03_同事工作目录与调研存储方案.md` |
| 公司整体架构优化 | `~/hermes/ideas/2026-08-03_公司整体架构优化方案.md` |
| 按三大核心重组 | `~/hermes/ideas/2026-08-03_按三大核心重组方案.md` |
| 核心 3 嵌入式训练+分层+Dashboard | `~/hermes/ideas/2026-08-03_核心3嵌入式训练_分层资源_控制面板.md` |

### 七、玉芬下次做战略方案 v4 的反思

**新增反模式**(8/3 20:00+ 出现):
- ❌ **没有把"分层资源 / Dashboard / Token 管理"作为战略层面** — 当成技术细节,应该跟三大核心并列
- ❌ **章节编号错位** — 8/3 19:45 增补 §④ 时忘了把原 §④ Dashboard 改成 §⑤ → patch 修过,但应该一次性想好章节

**正模式**:
- ✅ **战略 v3 章节** — 任何"策略类对话"都加 "华哥决策 v3/v4" 章节固化结果
- ✅ **L0/L1/L2/L3 资源分层**(区别于 L1/L2/L3 记忆) — 每次提到时必须明示
- ✅ **3 个数字用 1 张表**(8 agent × 4 模型池 × 5.7M tokens/天)
- ✅ **每份方案 = 1 write_file 骨架 + N 个 patch 追加**(见 hermes-stream-safe-writing skill)

---

**整理者**:yuxin (玉芬)
**整理时间**:2026-08-01(初版)+ 2026-08-03 19:45(决策 v2 附录)+ 2026-08-03 20:30(决策 v3 附录)
