---
name: skill-curator-agent
description: 自动巡检 skills — 每天分析当前工作需要哪些 skill，保留有用的，删除没用的。触发词："巡检 skills"、"清理 skill"、"哪些 skill 有用"、"skill 精简"、"skill 增删"、"skill curator"。
---

# Skill Curator Agent（**Skill 巡检官**）

**职责**：每天 6 点自动巡检老大当前工作环境，**决定哪些 skill 保留、哪些删除、哪些新装**。

## 工作流

### 1. 拉当前 skills 列表
```bash
hermes skills list
# 或读 ~/.hermes/skills/*/SKILL.md
```

**补充（2026-06-15 实战）**：跨查 jobs + 状态更稳
```bash
# cron jobs 实际位置（不是 ~/.hermes/jobs.json，是 AppData/Local/hermes/cron/jobs.json）
python -c "
import json
from pathlib import Path
p = Path(r'C:\Users\Administrator\AppData\Local\hermes\cron\jobs.json')
data = json.loads(p.read_text(encoding='utf-8'))
for j in data['jobs']:
    print(j['id'][:8], '|', j['name'], '|', j.get('schedule',{}).get('expr',''), '|', 'enabled' if j.get('enabled') else 'DISABLED', '|', j.get('last_status','—'))
"
# 一行一个 job：id | name | cron | enabled | last_status
```

### 2. 分析老大的当前工作
- 老大常做的关键词：水产 / 小红书 / 抖音 / 飞书 / 视频号 / 知识库 / SD 生图 / cron / 简报
- 老大主要业务线：水产养殖 / 水产美食 / 养殖设备

### 3. 分类决策

**保留**（每天用得到）：
- 水产/抖音/小红书/飞书 业务 skill
- AI 生图 / 内容生产 / 文案 / 去 AI 味
- cron / 简报 / 知识库 / multi-agent
- Hermes 自身 / profile / secret / LLM endpoint

**删除**（明确无关）：
- gbrain 100+ 个 stub（fixture 测试桩，**已验证 2026-06-08 全删 74 个无影响**）
- 创意工具未用的（comic/infographic/manim/ascii-art/excalidraw/p5js）
- 办公工具未用的（notion/linear/airtable/obsidian/google-workspace/powerpoint）
- AI 营销 Hopkins 系列（用 marketing 替代）
- Pokemon 玩游戏、Polymarket 预测市场

**新装**（每天看 GitHub 调研结果）：
- 跑 `daily-skills-research` 任务找候选
- 老大批准后安装
- 装后跑 1 次冒烟测试

### 4. 输出报告

```
🧹 Skill 巡检 - {日期}

📊 当前状态：{总 skill 数} / 保留 X / 删除 Y

✅ 今天保留（高价值）：
- skill 名 | 一句话用途

❌ 今天删除（明确无关）：
- skill 名 | 删除原因

🆕 推荐新装（待老大批准）：
- 仓库名 | 价值

📈 减负：占用减少 X%
```

## 操作规范

- ❌ **绝不擅自装新 skill**（等老大批准）
- ✅ 删除前**列出 5-10 个**给老大看（**不擅自删**）
- ✅ 保留的 skill 要有**实际使用证据**（session 记录 / cron 任务引用）
- ✅ 删除的 skill **记录在 SKILL_DELETED.md**（防回装）

## 反模式

- ❌ "安装可能有用" 的 skill（占空间）
- ❌ 留 gbrain stub 怕"以后能用"（已验证无用）
- ❌ Hopkins 营销子 skill 重复
- ❌ 不查实际使用就删（可能误伤）

## 关键经验（**2026-06-08 验证**）

- **gbrain 100+ stub 全是 fixture 测试桩**——**全删不影响任何功能**
- **Hopkins 营销 3 个子 skill**（curiosity-hook-builder/headline-workshop/service-frame-rewriter）——**用 marketing 替代即可**
- **creative 工具未用**（comic/infographic/manim/ascii-art）——**占空间但老大用不到**
- **办公工具**（notion/linear/obsidian）——**老大用飞书办公**

##实战数据（**2026-06-08 单次清理**）

- **清理前**：173 个 skill
- **清理后**：81 个 skill（**减负53%**）
- **删除总数**：93 个
 -74 个 gbrain stub（academic-verify / brain-ops / capture / eiirp / ...）
 -7 个创意工具（baoyu-comic / manim-video / pokemon-player / ...）
 -5 个办公工具（notion / linear / obsidian / nano-pdf / ocr-and-documents）
 -4 个其他（comfyui / research /18-plugin-onboarding / ...）
 -3 个 Hopkins营销子 skill

- **新装1 个**：skill-curator-agent（本 skill自我循环）

## 🛑 **回流观察（2026-06-10 + 2026-06-15 双验证）**

**6/10 验证**：清理后第 3 天已发现 openclaw 子技能自动回流 —— **94 enabled（11 builtin + 83 local）**——比 6/8 的 81 多 13 个。

**6/15 验证**（**5 天后**）：**97 enabled（13 builtin + 84 local）**——比 6/10 又多 3 个，**增速放缓**（13 个/3 天 → 3 个/5 天）。

**回流来源**：
- `kuaishou-sentiment-dashboard` / `douyin-user-videos` / `抖音运营` / `抖音运营` / `快手直播` / `multi-source-research` / `feishu-toolkit`（openclaw-imports 类）
- 部分已被对应 umbrella 覆盖：douyin-kuaishou-expert / Deep Research / hermes-feishu-gateway

**应对**：
- ❌ **不要每天当惊喜重新删**——是 import / install 自动加回的，删了还会来
- ✅ **在 cron 巡检里持续标记**——**每 30 天批量删一次**比每天删更省事
- ✅ **触发 import 的源头**（`hermes skills install` 命令记录 / source config）才是治本

**关键**：**81 → 94 → 97 不是「清理失败」，是「生态自然增长」**——别把回流当 bug。

**builtin 在涨**：6/10 时 11 builtin → 6/15 时 13 builtin（**Hermes 自身更新加了 2 个 builtin skill**）。**老大没必要管 builtin 增减**——它跟 hermes 版本绑。local 数 = 真正决定生态健康的指标。

##关键：批量删除比单条快

```python
# ❌ 一条条删（慢）
for s in to_delete:
    skill_manage(action="delete", name=s)

# ✅ 用 agent 批量删（loop 一次跑完）
agent_loop_until_done:
    for s in to_delete:
        try: skill_manage(action="delete", name=s)
        except: pass
```

## 与 6 点 cron 集成

本 skill 是 **daily-cron-architecture** 的核心依赖：

```
06:00 cron
  ├─ session_search → 昨日工作总结
  └─ skill-curator-agent → 列出建议删除 5-10 个 + 建议新装 2-3 个
       ↓
  飞书卡片推老大
       ↓
  老大批准后小弟才执行
```

**绝对不擅自装/删**——所有动作等老大在飞书点批准。

## 反模式补丁

- ❌ "占空间不大就留着" → 173→81 已证明减负 53% 不影响任何功能
- ❌ "先删了老大问再说" → 列清单等批准才是标准动作
- ❌ "老版本有需要时再装" → gbrain stub 3 个月没碰过 = 永远不碰
- ❌ "Hopkins 营销子 skill 是营销的核心" → marketing 一个 skill 覆盖全部

## 关联资源

- `references/cleaned_2026_06_08.md` — 实际清理的 93 个 skill 完整清单
- `scripts/audit_skills.py` — 自动分析 skill 使用频率脚本（待添加）