# 2026-08-22 Codex 进化巡检 Runbook

## 当日摘要

| 维度 | 结果 |
|---|---|
| Codex CLI | v0.147.0（npm available 0.149.0，**未升级**，待老大拍板） |
| Marketplace | 2 个，均为 local snapshot |
| 本地 skills | 88 → **91**（+3 个新装） |
| doctor | ok（详细未重跑） |
| 今日新增 | **3 个 skill** ：marketing-os / lead-gen-video-script / autoprompt |
| 备份 | commit `157433b` 本地 ✅，**push ❌ 被 GH013 拦**（详见下方） |

## 3 个新装 skill 详情

### marketing-os（⭐263）
- **来源**：`Yuzzyuk/marketing-os`
- **路径结构**：`skills/marketing-os/SKILL.md` + 18 个 `references/*.md`
- **大小**：349K
- **装法**：
  ```bash
  cd /c/Users/Administrator/Desktop/yuxin-skills/sources
  git clone --depth 1 git@github.com:Yuzzyuk/marketing-os.git
  cp -r marketing-os/skills/marketing-os/* /c/Users/Administrator/.codex/skills/marketing-os/
  ```
- **价值**：14 个营销模块（审计/文案/GEO/广告/邮件/社媒/Launch/Positioning/...）覆盖老大 4 业务线
- **老大决策**：直接装（无需审批）

### lead-gen-video-script（⭐13）
- **来源**：`xintu1314/lead-gen-video-script`
- **路径结构**：根目录 `SKILL.md` + `references/{evaluation-rubric,examples,logic-framework}.md` + `agents/`
- **大小**：126K
- **装法**：
  ```bash
  cd /c/Users/Administrator/Desktop/yuxin-skills/sources
  git clone --depth 1 git@github.com:xintu1314/lead-gen-video-script.git
  cp -r lead-gen-video-script/* /c/Users/Administrator/.codex/skills/lead-gen-video-script/
  ```
- **价值**：中文获客视频脚本（高客单成交 + 客户筛选）→ 对接养殖 B 端 / 设备 B 端
- **老大决策**：直接装

### autoprompt（⭐591）
- **来源**：`Spielewoy/autoprompt-skill`
- **路径结构**：`agents/{claude,codex,deepseek,kilo,omp,opencode,prime,reasonix}/` —— **多 agent 适配仓库**
- **大小**：全仓 21M；**`agents/codex/` 仅 523K**
- **装法**（**关键：只装 codex 子目录，不是全仓库**）：
  ```bash
  cd /c/Users/Administrator/Desktop/yuxin-skills/sources
  git clone --depth 1 git@github.com:Spielewoy/autoprompt-skill.git
  cp -r autoprompt-skill/agents/codex/* /c/Users/Administrator/.codex/skills/autoprompt/
  ```
- **陷阱**：
  - ❌ `cp -r agents/codex/` → 多一层 codex/ 目录，`find ~/.codex/skills/autoprompt/SKILL.md` 找不到
  - ❌ 整仓库 `cp -r *` → 把 `tests/` `docs/` `bin/` 全搬过来，污染 Codex skills 索引
  - ✅ `cp -r agents/codex/*` → 干净装
- **价值**：Codex 编排 skill（任务拆 lane + 独立 verify，声称 45% 失败率降低）
- **老大决策**：直接装（codex 子目录）

## sources/ 目录约定（**8-22 立**）

`C:\Users\Administrator\Desktop\yuxin-skills\sources\` 作为 **git clone 中转站**：

- ✅ 临时 clone 全仓进去（`sources/<repo>/`）
- ✅ cp 出要的子目录到 `codex-skills/<skill-name>/`
- ❌ **不直接 commit sources/**（嵌套 git 仓，commit 不到 yuxin-skills）
- ✅ 装完 1 个 skill 就 `rm -rf sources/<repo>` 清掉，避免长期占磁盘

**实际状态**：8-22 只剩空目录（3 次 clone + 删都干净）。

## AGENTS.md 处理

未 patch。理由：
- skill 总数 88 → 91（+3）触发"总数变化"例外 → 本应 patch
- **但 8-22 时间紧（push 被拦后转兜底）**，漏了 patch AGENTS.md
- 8-23 cron 第一件事补 patch AGENTS.md

## 老大决策待办

| 优先级 | 待办 | 触发命令 |
|---|---|---|
| 🟢 高 | GitHub unblock 推送 | 老大去 https://github.com/openclaw-cn-dev/yuxin-skills/security/secret-scanning/unblock-secret/3IFX4i7tiRBZbxN7FN10EgvrOXU → 点 "Allow this secret" → 回话"推"，下次 cron 自动 push |
| 🟡 中 | Hermes v0.20.5 升级 | 手动 `hermes update`（不在 cron 跑） |
| 🟡 中 | Codex 0.149.0 升级 | 手动 `npm i -g @openai/codex@0.149.0` |
| ⚪ 低 | 2 个 CAD skill 评估（DSH_SW + cad-ai-renderer）| 老大说"试" → 走 sources/ 流程 clone + 装 |

## 关键实测命令

### 1. 装多 agent 仓库只取 codex 子目录
```bash
# 1) clone 全仓（21M 但只要 5 秒）
cd /c/Users/Administrator/Desktop/yuxin-skills/sources
git clone --depth 1 git@github.com:Spielewoy/autoprompt-skill.git

# 2) 看 agents/ 结构
ls autoprompt-skill/agents/
# claude/  codex/  deepseek/  kilo/  omp/  opencode/  prime/  reasonix/

# 3) 只 cp codex/（**注意 * 不是 /**）
cp -r autoprompt-skill/agents/codex/* /c/Users/Administrator/.codex/skills/autoprompt/

# 4) 验
ls /c/Users/Administrator/.codex/skills/autoprompt/SKILL.md
wc -l /c/Users/Administrator/.codex/skills/autoprompt/SKILL.md
# 120 行（不是 0 = 装上了）
```

### 2. 推 yuxin-skills 撞 GH013
```bash
cd /c/Users/Administrator/Desktop/yuxin-skills
git pull --rebase origin main
# Rebasing (1/14)... (14/14) Successfully rebased

git push origin main
# ! [remote rejected] main -> main (fetch first)

git pull --rebase origin main  # 拉远端领先 commit（**含历史 secret**）
git push origin main
# ! [remote rejected] main -> main (push declined due to repository rule violations)
#   —— Lark Application Secret ————————
#     locations:
#       - commit: 31cfbb91d74ea353d02a838a5d677f2848ad67f8   ← 远端历史 commit
#         path: hermes/daily-cron-architecture/scripts/feishu_push.py:8

# 看完整 unblock URL
git push origin main 2>&1 | grep "https://github.com"
# https://github.com/openclaw-cn-dev/yuxin-skills/security/secret-scanning/unblock-secret/3IFX4i7tiRBZbxN7FN10EgvrOXU
```

### 3. 验本地 commit 干净（push 前 5 秒）
```bash
cd /c/Users/Administrator/Desktop/yuxin-skills

# 1) AppSecret 字面量扫描
git grep -nE "naW3ji6n5RMDhWTOjTPIudCRWCZ6djmn" 2>/dev/null
# 期望：空

# 2) cli_aaa AppID 字面量扫描（**注意 12-18 字符之间**）
git grep -nE "cli_aaa[a-z0-9]{12,18}" 2>/dev/null
# 期望：空

# 3) HEAD 内容预览（确认 commit 真干净）
git show HEAD:codex-skills/marketing-os/SKILL.md | head -3
```

## 踩坑 / Pitfall

1. **多 agent 仓库只装 codex 子目录**——整仓 21M 是浪费 99% 磁盘
2. **`sources/` 中转目录**——不要直接 commit 到 yuxin-skills（嵌套 git 仓）
3. **`git pull --rebase` 会拉远端历史脏 commit**——导致本地 HEAD 干净但 push 仍撞 GH013
4. **`git reset --soft origin/main` 不解决 GH013 历史脏 commit**——只重置本地 HEAD，远端历史 secret 仍在
5. **AGENTS.md 当日漏 patch**——下个 cron 优先补

## 下次 cron 任务清单

1. 跑 `git push origin main` 自动重试 → 老大手动 unblock 后应能 push
2. 如未 unblock → 跳过 push，日报继续抛 URL
3. 补 patch AGENTS.md（8-22 漏了）
4. 跑 `find ~/.codex/skills -name SKILL.md | wc -l` → 应 = 91（88 + 3）
5. 数字 vs 今日对比 → 触发 AGENTS.md patch 决策
