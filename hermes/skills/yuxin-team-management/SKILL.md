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
