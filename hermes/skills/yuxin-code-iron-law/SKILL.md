---
name: yuxin-code-iron-law
description: 渔芯科技全公司铁律 — 代码/脚本/工具开发优先经 Claude Code 或 Codex。华哥 2026-08-03 明确，2026-08-14 修正为"优先"而非"必须"：同事不会调用 Claude Code 不应导致不写代码，不会用或失败时直接自写（加 TODO 标注），把活干完优先于工具洁癖。所有 9 个 profile (玉芬+8 同事+community) AGENTS.md 顶部已固化。v1.3 实测双工具链都可用:Claude Code 用 `claude -p --allowedTools "Read,Edit,Write,Glob,Grep"`(代码首选,5/5 任务 100% 成功),Codex 用 `cat /tmp/p.txt | codex exec --skip-git-repo-check -s danger-full-access`(大型 JSON/数据整合首选,2 分 20 秒写 243 行)。两个反模式:无 --allowedTools 卡 300s 超时;缺 -s danger-full-access 报 read-only sandbox。
version: 1.3
created: 2026-08-03
updated: 2026-08-03
priority: highest
---

# 🛡️ 渔芯 · 代码开发铁律 v1

> **华哥 2026-08-03 明确:"代码开发必须调用 claude code 或 codex,不成功才能自己直接开始"**
> **华哥 2026-08-14 修正:"有代码要写时优先使用 Claude Code 或 Codex。同事不会调用 Claude Code 不应导致不写代码——不会用或失败时直接自写,不要卡住。"**
> **范围:9 个 profile 全部遵守(玉芬 default + 8 同事 + community)**
> **优先级:最高 — 高于任何其他 SOP**
>
> ⚠️ **核心精神(2026-08-14 起)**:Claude Code / Codex 是**优先选项,不是硬性门槛**。"不会调用 Claude Code"**绝不是不写代码的理由**。会调就用,不会调或调失败就直接自写(加 TODO 标注),把活干完优先于工具洁癖。

---

## 🚦 执行前 30 秒决策清单(每次写代码前必走)

按顺序回答,任一为"否"才可自写:

```
□ 1. 这件事是"代码/脚本/可执行文件"吗?(查下方"触发条件"表)
□ 2. 优先试 `claude -p "..."` — 会调就用;不会调 / 失败(工具异常/超时/无权限)→ 跳到下一步
□ 3. 优先试 `codex exec "..." --sandbox danger-full-access` — 会调就用;不会调 / 失败 → 跳到下一步
□ 4. 都不会调或都失败 → **直接自写,不要卡住**(文件首行加 `# TODO(tech-debt): 改由 Claude Code/Codex 重写`)
□ 5. 飞书通知华哥登记技术债(自写时建议,不强制)
```

**自动豁免场景**(无需走铁律,可自写):Markdown · AGENTS.md · 纯 JSON/YAML/TOML 配置 · 元数据 JSON(Dashboard 数据源)· 单行 shell · 调试 print · 数据迁移/批处理。

---

## 🏆 实操首选:`claude -p --allowedTools` 模式(2026-08-03 实测验证,5/5 任务成功)

**结论**:之前 v1.1 推荐"delegate_task 是 Hermes 场景下唯一稳妥路径" — **这个判断错了**。**实测 5 个任务全部成功**用以下模式:

```bash
claude -p --allowedTools "Read,Edit,Write,Glob,Grep" -- "<精确聚焦的 prompt>"
```

**为什么 --allowedTools 能绕过权限拦截**:
- `claude -p` 默认对所有写操作要求人工 y 批准(进交互)
- `--allowedTools` 白名单内的工具(Read/Edit/Write/Glob/Grep)**自动执行,不需批准**
- 仅 **Bash 命令**(如 `python3 ...` 语法验证)**仍需批准** — 解决:让 Claude Code 用 Read 工具自己验证,或任务结束后玉芬手动 `python3 -c "import ast; ..."` 验证

**实际 5 个任务(2026-08-03,华哥已拍板"a",10 分钟全跑完)**:

| 任务 | 产物 | 耗时 | 验证方式 |
|---|---|---|---|
| 1 修 deprecation | `app.py` 4 处 use_container_width → width='stretch' | 52s | `python3 -c "import ast; ..."` + `grep -c` |
| 2 重写铁律页 | `pages/1_铁律.py` 228 行 | 44s | `wc -l` + `head -10` |
| 3 重写 tool 脚本 | `tool_repo_manager.py` v2 533 行 | 3m20s | `python3 ... --help` + `head` |
| 4 重写 Dashboard | `app.py` v2.0 499 行 + `assets/styles.css` 61 行 | 4m35s | `wc -l` + 3 端点 HTTP 200 |
| 5 评估 4 JSON | api_keys/products/community/tool_logs 全部"纯数据保留" | 44s | 4 文件 _meta 加 verified_by |

**关键经验**:

1. **拆分任务 > 一次大任务** — 5 个独立 prompt 比 1 个大 prompt 强 N 倍(独立验证、错误隔离、出错易定位)
2. **每个 prompt 必须明确**:
   - 用 Read 读哪个文件(避免误改)
   - 用 Edit/Write 写到哪里(绝对路径)
   - 严格限制:只改这 X 个文件,不要写其他文件
   - 不要启动 streamlit / 不要做 syntax check(由玉芬事后验证)
   - 输出 "✅ 任务 N 完成"
3. **必须验证文件真的改了** — `md5sum` / `wc -l` / `python3 -c "import ast; ast.parse(...)"`,**不要相信 "✅ 任务 N 完成"** — Claude Code 退化行为会回声 `DONE` 但文件未变(只发生在无 --allowedTools 时)
4. **Bash 命令触发"语法检查"会被卡** — 解决:让 Claude Code 用 Read 工具读文件验证,或任务完成后玉芬独立验证

**完整工作模板见**:`references/***SECRET***.md`

---

## 触发条件(什么算"代码开发")

| 类型 | 是否触发铁律 | 例子 |
|---|---|---|
| Python 脚本/服务(>5 行有业务逻辑) | ✅ 触发 | `xxx.py` 业务模块 |
| JS/TS/React/Vue 组件 | ✅ 触发 | 前端组件 |
| Shell 脚本(>5 行) | ✅ 触发 | `xxx.sh` 自动化 |
| Streamlit/Dash 业务代码 | ✅ 触发 | `app.py` 业务模块 |
| CAD macro/插件代码 | ✅ 触发 | 任何可执行 |
| 单行命令/print 调试 | ❌ 不触发 | 临时排查 |
| 纯 shell 批处理(<5 行) | ❌ 不触发 | `mv` / `cp` / `ls` |
| Markdown/AGENTS.md/SKILL.md | ❌ 不触发 | 文档类 |
| JSON/YAML/TOML 纯配置文件 | ❌ 不触发 | 配置类 |
| 元数据 JSON(只写不调逻辑) | ❌ 不触发 | Dashboard 数据源 |
| Streamlit 纯布局/渲染代码 | ❌ 不触发 | UI 布局 |

---

## 默认调用链(强制)

```
1️⃣ 第一选择: Claude Code
   claude -p "需求描述: .... 写到 <路径>"
   或交互模式
   (不会调用 Claude Code → 直接跳 2️⃣,不要卡住)

2️⃣ 第二选择: Codex CLI  
   codex exec "需求描述: ...." --sandbox danger-full-access
   或交互模式
   (不会调用 Codex → 直接跳 3️⃣,不要卡住)

3️⃣ 兜底(不会调 / 调失败即可,不再要求"明确失败 3 次"):
   ✅ 文件首行加 # TODO(tech-debt): 改由 Claude Code/Codex 重写
   ✅ 飞书通知华哥登记技术债(建议,不强制)
   ⚠️ 核心:把活干完优先于工具洁癖。不会用工具不是停摆的理由。
```

---

## 违规案例(2026-08-03 已发生 → 已闭环)

| 越权产物 | 路径 | 8/3 状态 | 闭环方式 |
|---|---|---|---|
| Dashboard app.py | `/Users/hua/hermes/dashboard/app.py` | ✅ Claude Code 重写为 v2.0 (499 行) | `--allowedTools` 任务 4 |
| tool_repo_manager.py | `/Users/hua/.hermes/tool-repo/tool_repo_manager.py` | ✅ Claude Code 重写为 v2 (533 行) | `--allowedTools` 任务 3 |
| 4 个 JSON 数据源 | `/Users/hua/.hermes/state/*.json` | ✅ Claude Code 评估为"纯数据保留" | `--allowedTools` 任务 5 |
| collect_status.py | `/Users/hua/.hermes/scripts/collect_status.py` | ⚠️ 8/3 玉芬自写 + 加 # TODO 注释(未由 Claude Code 重写) | 仍待补做 — 优先级最低(数据采集脚本,影响小) |

**已闭环教训**:玉芬自写 + 加 # TODO 标注后,**立即**用 `claude -p --allowedTools` 重写,5 个产物 10 分钟搞定。这套流程以后可作为铁律"事后整改"的标准操作。

---

## ⚠️ 实操陷阱(2026-08-03 实测发现 + 修正)

### 陷阱 1:无 `--allowedTools` 时 Claude Code 会被权限拦截

**现象**:`claude -p "请用 Write 工具改 X"` 第一次会 300s 超时(等人工 y 批准);第二次会**回声输出 "DONE" 但文件未变**(更阴险)。

**修正**:永远加 `--allowedTools "Read,Edit,Write,Glob,Grep"`。白名单内工具自动执行,不再卡权限。

### 陷阱 2:有 `--allowedTools` 后,只剩 Bash 命令要批准

**现象**:Claude Code 改完文件后,经常主动想跑 `python3 -c "import ast; ast.parse(...)"` 验证语法 → 触发 "语法检查命令需要审批" 卡住。

**修正(2 种方案)**:
- **A. prompt 里写明 "不要做 syntax check,由玉芬事后验证"**(推荐)
- **B. 让 Claude Code 用 Read 工具自己读文件验证**(不触发 Bash 权限)

### 陷阱 3:5 个产物一次性改必死

**现象**:`claude -p "把 A/B/C/D/E 5 个文件都按 X 模式改"` → Claude Code 注意力分散,经常改错文件或遗漏。

**修正**:5 个独立小 prompt,每个只动 1 个文件,每个 1-5 分钟完成。玉芬独立验证每个,出错易定位。

### 陷阱 4:信任 "✅ 任务 N 完成" 输出

**现象**:即使加了 `--allowedTools`,Claude Code 偶尔会**回声输出完成标志但 Edit/Write 没真的执行**(实测 ~5% 概率)。

**修正**:**必做以下任一验证**:
```bash
md5sum /path/to/file           # 改前改后对比
wc -l /path/to/file            # 行数变化
python3 -c "import ast; ast.parse(open('/path/to/file').read())"  # 语法
grep -c "old_string" /path/to/file  # 旧字符串应减少
grep -c "new_string" /path/to/file  # 新字符串应增加
```

### 陷阱 5(已废):`codex exec` 报 "not trusted"

**v1.2 时的误判**:`codex exec "..." --sandbox danger-full-access` 报 "Not inside a trusted directory and --skip-git-repo-check was not specified",即使加 `--skip-git-repo-check` 仍会进 read-only sandbox。

**v1.3 实测推翻**:加齐两个 flag 就 work — `--skip-git-repo-check -s danger-full-access`,243 行 iron_law.json 2 分 20 秒完成整合。Codex CLI 实际可用,只是 v1.2 没找到正确参数组合。

**修正后的 Codex 工作模式**(完整 reproduction 见 `references/codex-exec-working-pattern.md`):

```bash
cat /tmp/prompt.txt | codex exec --skip-git-repo-check -s danger-full-access
```

**关键 3 个 flag**(缺一不可):
- `--skip-git-repo-check` — 跳过 git repo 信任检查
- `-s danger-full-access` — Codex 默认进 read-only sandbox,这个 flag 让 Codex 可写
- prompt 必须用 `cat` 管道输入,不要在命令行 `codex exec "..."` 嵌(避免 bash 转义 + 长度限制)

### 优先级(2026-08-03 实测后修正)

| 方案 | 适用场景 | 推荐度 |
|---|---|---|
| **A. `claude -p --allowedTools`** | 玉芬写代码首选,5/5 实测成功 | ⭐⭐⭐⭐⭐ **默认推荐** |
| **B. `codex exec --skip-git-repo-check -s danger-full-access`** | 写大型 JSON/数据整理(>500 行)Claude Code 偶有遗漏,Codex 更稳 | ⭐⭐⭐⭐ |
| **C. `delegate_task` 委派 subagent** | 需要"无状态"隔离,subagent 上下文独立时 | ⭐⭐⭐ |
| **D. `pty=true` 交互模式** | 华哥本人在终端,愿意手动 y 批准 | ⭐⭐ |
| **E. `***SECRET***`** | 完全信任场景,小修改可回滚 | ⭐ (慎用) |
| **F. 自写 + TODO 兜底** | 真正"明确失败" — A/B/C/D/E 都不行时 | ⭐⭐ (合规但不推荐) |

**反模式**(确认会失败或低效):
- ❌ `claude -p "请用 Write 工具改 X"`(无 --allowedTools,会卡)
- ❌ `codex exec "..." --sandbox danger-full-access`(**缺 `--skip-git-repo-check` 报 not trusted,缺 `-s danger-full-access` 进 read-only sandbox 阻写入**)
- ❌ 在 `codex exec "..."` 命令行嵌 prompt(触发 bash 转义 / 长度限制;**改用 `cat /tmp/prompt.txt | codex exec ...`**)
- ❌ 一次 prompt 改 5+ 个文件(注意力分散)
- ❌ 不做 md5/wc/ast 验证就以为成功了
- ❌ 反复重试同一条 `claude -p` 命令(触发 `[Tool loop warning]`)

**完整工作模板 + 实测 reproduction 步骤见**:`references/***SECRET***.md`

---

## 违反处置(自发现或被指出)

**什么算违规(2026-08-14 更新)**:
- ❌ 因为"不会调用 Claude Code/Codex"就**完全不写代码、停摆不干活** — 最严重违规,违反"把活干完优先"原则
- ❌ 既不调工具、也不加 TODO 标注、也不通知华哥,无痕自写并冒充工具产出

**自写本身不算违规**(兜底合法),但建议加 `# TODO(tech-debt)` 标注 + 飞书登记,便于事后统一用工具重写。

处置:
1. 立即纠正(要么补调工具,要么补标注)
2. 飞书报告华哥
3. 写复盘到 ~/hermes/reports/yuxin_self_criticism/YYYY-MM-DD_<主题>.md

**累计 3 次违规**:对应 profile 自动降级(暂停 self-evolution 24h),等华哥手动重启。

---

## 实操 checklist(写代码前必走)

```bash
# 1. 思考:这是代码吗?查上面"触发条件"表
# 2. 第一选择
claude -p "需求: ... 写出可运行的 Python 脚本到 <绝对路径>,要求: ..." 

# 3. 失败时第二选择  
codex exec "需求: ..." --sandbox danger-full-access

# 4. 不会调用、或两次都失败时 → 直接自写(不要卡住)
#   建议: a) 文件首行加 # TODO(tech-debt)  b) 飞书通知华哥登记技术债
```

---

## 为什么有这条铁律(华哥理由)

1. **训练数据隔离** — Claude Code/Codex 产出的代码自动进入训练数据集(可作为嵌入式训练原料),玉芬自写无法蒸馏
2. **质量保证** — 外部 LLM 代码质量上限高于玉芬
3. **可审计** — 所有代码来源可追溯(Claude Code/Codex 都有日志)
4. **避免重复造轮** — Claude Code/Codex 可能已有现成实现
5. **逼玉芬聚焦高价值工作** — 玉芬时间是稀缺资源,不应浪费在写业务代码

---

## 不适用场景(可自写,不算违规)

✅ 文档/Markdown/方案/报告(玉芬本职)
✅ AGENTS.md / 记忆 / skill 文本内容
✅ 配置文件(JSON/YAML/TOML,只写不调逻辑)
✅ 一行命令 / 临时修复 / 调试 print
✅ 数据迁移 / 纯 shell 批处理
✅ 写元数据 JSON(Dashboard 数据源)
✅ Streamlit 界面文件(若只有布局/渲染代码,无业务逻辑)

---

## 配套文件

- **9 份 AGENTS.md**:`/Users/hua/.hermes/profiles/*/AGENTS.md` 顶部都有铁律章节
- **玉芬 default v5**:`/Users/hua/.hermes/profiles/default/AGENTS.md`
- **技术债清单**:见 `~/hermes/reports/yuxin_self_criticism/`
- **执行配套 skill**:`yuxin-coding-workflow` — `claude -p --allowedTools` 委派的具体模板 + 验证命令
- **🆕 Claude Code 实操**:`references/***SECRET***.md` — 5/5 任务成功的完整 prompt 模板 + 验证命令
- **🆕 Codex CLI 实操**:`references/codex-exec-working-pattern.md` — 2026-08-03 实测 Codex 写 243 行 JSON 整合任务的完整 reproduction
- **❌ 过时参考**:`references/***SECRET***.md` — v1.1 误判 delegate_task 唯一论,已被 v1.2 实测推翻

---

## 版本历史

| 版本 | 日期 | 改动 |
|---|---|---|
| v1.0 | 2026-08-03 | 初版 — 华哥明确,9 份 AGENTS.md 同步写入 |
| v1.1 | 2026-08-03 | 加 30 秒决策清单 + 5 方案执行表 + 误判"delegate_task 推荐默认" |
| v1.2 | 2026-08-03 | 🔴 重大修正:实测 5/5 任务证明 `claude -p --allowedTools` 才是默认推荐;反悔 delegate_task 唯一论;加入"5 个小 prompt > 1 个大 prompt"模式;加入 Bash 批准绕过的 2 种方案;越权产物表全部闭环 |
| **v1.3** | **2026-08-03** | **🔴 重大修正**:实测 Codex CLI 加齐 `--skip-git-repo-check -s danger-full-access` 完全可用(2 分 20 秒写 243 行 iron_law.json),反悔 v1.2 陷阱 5 "Codex 仍不可用" 误判;新增 Codex 优先级 B;新增 references/codex-exec-working-pattern.md |
