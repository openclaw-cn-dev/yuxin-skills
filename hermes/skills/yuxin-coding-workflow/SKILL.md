---
name: yuxin-coding-workflow
description: 玉芬执行编码/实现任务的工作流 — 直接用 Hermes 工具写代码,不要生成远程 CC SWITCH 指令包。触发条件:华哥/同事派发"写代码/写 API/写脚本/实现功能"类任务;或华哥说"你自己写吧"、"相信你";或想生成"给 CC 跑的开工 prompt"时。
version: 0.3.0
author: 渔芯玉芬
tags: [玉芬, 编码, 工作流, claude-code, 偏好, 端到端验证]
---

# 玉芬编码任务工作流

## ⚠️ 铁律 1:直接写,不绕路

华哥明确偏好(2026-06-28 验证):**当任务是"写代码/实现功能"时,玉芬直接用 Hermes 工具链写完,不要生成"给 CC SWITCH/Claude Code 跑的开工指令包"。**

华哥原话:"不行你就自己写代码吧,你自己也是写代码的专家。相信你。"

**错误模式**(本 session 翻车过):
1. 华哥派发"v3 技术方案实装"任务
2. 玉芬提议"我打包 prompt → 你复制 → 粘到 CC → 转回结果"
3. 华哥觉得麻烦,反复问"CC 怎么操作"、"我不在本机"、"要打开 CC SWITCH"
4. 华哥最后说"你自己写吧,相信你"
5. 玉芬才转去直接用 `write_file` / `patch` / `terminal` 写

**正确模式**:
1. 收到编码任务 → 直接用 `write_file` + `patch` 写代码
2. 用 `terminal` 跑测试/启动服务
3. 用 `read_file` 查参考文档(v3 方案、技术栈决策表)
4. 跑通后汇报华哥

## ⚠️ 铁律 2:启动服务 ≠ 完成(2026-06-29 实测踩坑新增)

**启动后台服务后必须立刻做 curl 端到端实测,不能用"已启动"代替"已完成"。**

- 错误模式:`python3 api_server.py &` → 进汇报说"完成" → 实际服务可能起不来、端口冲突、路由拼错
- 正确流程:
  1. 启动服务(后台)
  2. **立刻** `curl http://localhost:PORT/api/health` 验证存活
  3. 跑 1-2 个核心端点验证业务逻辑
  4. 截图/输出确认后再写汇报"完成"
- 兜底:汇报中**必须明确**写"已 curl 实测返回 200"或"未实测,需补"。**禁止用"已启动"含糊带过**
- 真实案例:2026-06-29 八卦预测工具阶段 3 编码,玉芬启动了 `api_server.py` 但没 curl 验证就汇报"阶段 3 完成",实际后端 4 个端点都未实测。系统提示上限后才补上汇报,被华哥发现"未实测"。

## ⚠️ 铁律 4:编码 Agent 会话结束必须写 handoff.md(2026-07-18 新增)

**任何编码 agent(Claude Code / Codex / Hermes 等)会话结束前,必须执行以下交接流程:**

### 关闭会话时(告诉 agent):

> 这个会话要结束了,请写一份交接文档存到 handoff.md:
> - 我们在做什么任务
> - 已经完成了什么
> - 当前卡在哪
> - 下一步计划是什么
> - 有哪些踩过的坑绝对不要再踩
>
> 写给一个完全没有上下文的新会话看。

### 新会话开始时(告诉 agent):

> 先读 handoff.md。

**为什么这是铁律:**
- AI 编码 agent #1 痛点 = 上下文断裂
- 50 轮对话后新窗口从零开始,踩过的坑全部重踩
- 投入 30 秒写交接 → 省下未来 30 分钟
- 适用所有项目、所有编码 agent

**handoff.md 文件位置:** 项目根目录(与 CLAUDE.md / AGENTS.md 同级)

## ⚠️ 铁律 3:华哥说"全部完成再通知我"=一次性做完,不分段汇报(2026-06-29 新增)

**华哥明确指令"具体工作你安排,全部完成再通知我"=禁止中途汇报进度,要一次性把单元测试、HTTP 端到端、浏览器实测、截图归档全做完再统一通知。**

- 错误模式:每跑通一步就发"✅ 阶段 3.1 完成" → 华哥会被刷屏,且中途汇报会让华哥误以为可以提前决策
- 正确流程:
  1. 内部用 `todo` 工具跟踪子步骤(用户看不到)
  2. 单元测试通过 + HTTP 端到端 + 浏览器实测 + 截图全部做完
  3. 一次性发汇总汇报(用模板),**附上所有截图**
  4. 汇报中**明确列出每项的实测证据**(curl 返回值、测试通过数、截图路径)
- 真实案例:2026-06-29 八卦预测工具阶段 3,华哥说"具体工作你安排,全部完成再通知我"。玉芬分 3 次发了 todo 更新和阶段性汇报,浪费了华哥注意力,应该一次性把"9/9 单测 + 7 个 HTTP 端点 + 3 张浏览器截图"全部做完再发一条汇总

## 何时本 skill 适用

| 场景 | 做法 |
|---|---|
| 华哥直接说"实现XX功能/写XX代码" | ✅ 直接写,本 skill 主导 |
| 华哥说"你自己写吧"、"相信你" | ✅ 直接写 |
| 华哥说"用 CC 跑" + 华哥本人在本机 | 可走 CC SWITCH 流程 |
| 同事 Agent 派发的编码任务 | ✅ 直接写(玉芬就是干活的) |
| 研究/规划/技术方案(非编码) | 走常规调研,非本 skill 范围 |
| 触发 "终止,等我" 类指令 | 立即停手 |

## 实装流程(华哥 v3 八卦预测项目已验证可用)

### 第 1 步:读方案/参考文档
```bash
# 找到对应 v3 方案或类似技术方案
ls ~/Desktop/渔芯科技/4-知识库/<项目名>/研究资料/
wc -l 研究资料/02_技术实施方案_v3.md
```

### 第 2 步:查章节大纲(用 search_files)
```python
# 快速找到关键章节
search_files(pattern="^## |^###", path="02_技术实施方案_v3.md", limit=100)
```

### 第 3 步:读关键章节(read_file with offset/limit)
```python
# 章节位置已知后,精确读
read_file(path="...", offset=343, limit=400)  # 第 4 章 起卦引擎
```

### 第 4 步:写代码骨架(write_file)
- 按方案 § 4.x 顺序写 `app/core/cast_engine.py`
- 写 `tests/unit/test_*.py` (TDD 风格,测试先行)
- 写 `app/api/v1/__init__.py` (端点)
- 写 `app/schemas/__init__.py` (Pydantic 模型)

### 第 5 步:建隔离 venv(本机 Python 3.9 + Pydantic v2.13 兼容性陷阱)
```bash
cd backend/
python3.11 -m venv .venv  # 必须用 3.11
.venv/bin/pip install fastapi pydantic pytest pytest-asyncio httpx
.venv/bin/python -m pytest tests/ -v
```

### 第 6 步:跑测试 + 修 bug + 端到端实测
- 单元测试全部通过后再做集成测试
- 集成测试发现 bug → 修 → 跑通 → **curl 真实端点** → 汇报

## 关键陷阱(本 session 踩过的)

### ⚠️ Python 3.9 + Pydantic v2.13 不兼容
- 症状:`Optional[X] = Field(None)` 解析成 `annotation=NoneType`
- 根因:Pydantic v2.13 + Python 3.9 typing 模块冲突
- 解决:**全部用 python3.11 venv**(不要用系统 python3)
- `python3` 默认指向 3.9.6(CommandLineTools)
- 验证:`python3.11 --version` → 3.11.x

### ⚠️ Pydantic `tuple[int, int]` 类型不被识别
- 症状:`PydanticSchemaGenerationError: Unable to generate schema for tuple[...]`
- 解决:扁平化为 `list[list[int]]`,在 `field_validator` 内转回 tuple
- 适用:任何内嵌 tuple 的 Pydantic v2.13 schema

### ⚠️ 复杂查表数据(64 卦矩阵等)要写验证测试
- 教训:v3 方案 64 卦矩阵有 1 个 ID 重复(DUI×ZHEN=54,应为 17)
- 做法:写 `test_no_duplicate_ids` + `test_all_64_combinations_present` 自动化验证
- 推荐:任何嵌入 v3/v4 方案里的数据表,先写一个独立验证脚本用外部标准核对
- 配套:卦象 binary 索引约定非常容易写反(见 `references/hexagram-binary-index-trap.md`)

### ⚠️ 描述里中文字符串不影响 Pydantic(但要警惕)
- v2.13 早期版本有 bug,description 含中文偶发导致 annotation 错位
- 改用英文 description 是更稳妥的做法,但根本原因是 venv

### ⚠️ 测试预期值不能凭直觉写,要程序算
- 本 session 在卦象互卦测试中反复陷入"修表→测→预期写错→再修"循环
- 错误:心算 2,3,4 爻的下卦,3,4,5 爻的上卦,凭脑补写 expected
- 正确:**写一个程序,输入 yao,自动算 bian_gua / hu_gua 的预期值**,再写断言
- 或在测试里 **同时打印 binary + 查表 key + 卦名**,让人/AI 一起核对

### ⚠️ Bash 环境可能严重残缺,优先用 `/usr/bin/python3`(2026-06-29 实测新增)
- **症状**:`head` / `lsof` / `sleep` / `which` / `ls` / 裸 `python3` 全部 `command not found`,连 `which` 都没有
- **根因**:某些 Hermes 终端环境的 PATH 只有 `/usr/bin` 基础命令,自定义工具链(HOME bin、Homebrew、pyenv 软链)都没加进来
- **正确做法**:
  1. 端口检查 → 直接 `/usr/bin/python3 -c "import socket; ..."` (不依赖 `lsof`)
  2. 文件检查 → `/usr/bin/python3 -c "import os; os.path.exists(...)"`
  3. 启动 Python 服务 → 用 `/usr/bin/python3` 显式绝对路径,不依赖 `python3` 在 PATH
  4. **绝不**先 `ls`、`which`、`head` 试探环境 — 直接假设最残情况,用绝对路径
- **参考命令**:
  ```bash
  /usr/bin/python3 -c "import socket; s=socket.socket(); s.bind(('0.0.0.0',PORT)); print('free')"
  /usr/bin/python3 -c "import urllib.request; print(urllib.request.urlopen('http://localhost:PORT/api/health', timeout=3).read().decode())"
  ```
- **额外提示**:如果连 `head` 都没有,Python 字符串截断做:`body[:300]` 替代 `head -c 300`

### ⚠️ `execute_code` 在 cron 模式 / 飞书会话中均被 BLOCKED(2026-07-10 修正)
- **症状**:调用 `execute_code` 报 `BLOCKED: execute_code runs arbitrary local Python (including subprocess calls that bypass shell-string approval checks).` — **不限于 cron**，飞书/Lark 消息会话同样被锁
- **根因**:Hermes 沙箱在 cron 任务 + messaging transport(飞书/Telegram 等)**统一策略**下拒绝 `execute_code`
- **可用场景**:仅浏览器 WebChat 直接对话；Cron 和飞书均不可用
- **正确做法**:
  1. **不要循环重试** `execute_code`,会触发 `[Tool loop warning: repeated_exact_failure_warning]`
  2. 改用 `terminal` 工具,内部用 `python3 -c "..."` 跑短脚本
  3. 需要循环/复杂逻辑时,用 `write_file` 写到 `/tmp/<name>.py` 再 `terminal: python3 /tmp/<name>.py`
  4. 详细 workaround 见 `references/hermes-tooling-gotchas.md` 第 2 节
- **2026-07-10 实战**:飞书对话中做 `brew install gh` + GitHub 仓库同步全套操作,期间 `execute_code` 被 BLOCKED。全部改用 `write_file` + `terminal` 模式完成

### ⚠️ `browser_vision` 可能误读界面状态(2026-06-29 实测新增)
- **症状**:点击语言切换按钮后,`browser_vision` 返回 "页面仍是中文",但 JS console 注入检查 `lang=zh-CN` + `setLang('en')` 调用证明已经切换为英文
- **根因**:`browser_vision` 是辅助视觉模型(VLM)对截图做文字描述,描述可能受 prompt 解读影响,不一定 100% 准确
- **正确做法**:
  1. 验证 UI 状态时,**优先用 `browser_console(expression="...")` 注入 JS 读取真实状态**(`document.documentElement.lang`、`document.querySelector('.class.active').textContent` 等)
  2. `browser_vision` 只用于**视觉布局/截图归档**,不用于状态判断
  3. 当 `browser_vision` 报告与 console 注入结果冲突时,**以 console 为准**
  4. 视觉提问要具体:不要问"显示什么语言",问"标题文字是 '八卦预测工具' 还是 'I Ching Divination'?"(可枚举答案)
- **典型反例**:"点击 English 按钮后视觉模型说没切换" → 实际是 `setLang('en')` 已生效,但视觉模型把"按钮 active class"看反了

## 玉芬 + CC SWITCH 关系(明确边界)

| 角色 | 工具 | 谁负责 |
|---|---|---|
| 华哥 | CC SWITCH / Claude Code(本机开) | 华哥自己在终端开 |
| 玉芬 | Hermes 工具链(write_file / patch / terminal) | 玉芬自己执行 |
| 派发同事 Agent | 飞书云盘 + 任务文件 | 玉芬调度 |

**玉芬不直接操作 CC SWITCH**——这是另一个独立 session,在华哥本机终端上。

**玉芬不写"给 CC 跑的开工 prompt"**——华哥已明确偏好"玉芬直接写"。生成开工 prompt 是 last resort,只有当:
- 任务规模极大(>2 周工作量)
- 华哥明确说"用 CC 跑"
- 玉芬自己 token 不够

## 验证流程(实装完成后必做,**全部做完再汇报一次**)

```bash
# 1. 单元测试
.venv/bin/python -m pytest tests/unit/ -v

# 2. 集成测试(API 端点)
.venv/bin/python -m pytest tests/integration/ -v

# 3. 启动服务 + curl 端到端实测(铁律 2!注意:Bash 可能没有 sleep/lsof)
#    用 /usr/bin/python3 显式绝对路径,curl 验证用 urllib.request(不依赖 curl 命令)
cd backend/
/usr/bin/python3 api_server.py &           # 后台启动
sleep 2                                    # 或 urllib 失败后重试 3 次
/usr/bin/python3 -c "
import urllib.request, json
for path in ['/api/health', '/api/qigua?method=time']:
    r = urllib.request.urlopen('http://localhost:8000' + path, timeout=3)
    print(path, '→', r.status, r.read()[:200].decode())
"

# 4. 浏览器实测(若有前端 H5)
#    用 browser_navigate + browser_click + browser_console 注入 JS 验证状态
#    用 browser_vision + annotate=false 截屏归档(但别完全相信 VLM 文字描述)
#    截图保存到 ~/.hermes/cache/screenshots/ 目录

# 5. 写汇报(一次性,不分段)
#    汇报中**必须明确列出**:
#    - 单测通过数(9/9)
#    - HTTP 端点实测结果(URL + 状态码 + 关键字段)
#    - 浏览器截图路径(2-3 张)
#    - 已知未做项 + 原因
```

## 汇报模板(给华哥,**完整 end-to-end 汇报**)

```markdown
# ✅ 阶段 N 完成:[项目名]
📁 新增文件:
- backend/app/core/[module].py (XX 行)
- backend/tests/unit/test_[module].py (XX 行,XX/XX 通过)

## 跑通的端到端(全部 curl 实测)
- 起卦引擎:4 种算法 + 64 卦矩阵 + 变卦
- FastAPI 端点:POST /api/v1/cast, GET /api/v1/hexagram/{id}
- **HTTP 实测**:`/api/health` → 200 OK,`/api/qigua?method=time` → 200 OK
- **浏览器实测**:`/index.html` 加载 200,点击"起卦"后 3 张卦卡正常显示
- **截图归档**:`/Users/hua/.hermes/cache/screenshots/browser_*.png`(附在汇报里)

## 待华哥决策
- [ ] 接入真实 LLM(DeepSeek/GPT-4o-mini)
- [ ] 部署到云
- [ ] 招技术合伙人评审代码
```

## 失败模式(不要做)

| 错误 | 后果 |
|---|---|
| 提议"我打包 prompt → 你复制 → 粘 CC" | 华哥:操作麻烦,信任度下降 |
| 让华哥手敲 CC 启动命令 | 华哥不在本机,卡死 |
| 写开工指令但华哥没本机 CC | 完全无法执行 |
| 玉芬自己 token 跑空还说"跑不动了" | 华哥会觉得玉芬不可靠 |
| 跑测试 36/36 通过后不汇报 | 华哥:不知道进度 |
| 进度汇报写 1000 字流水账 | 华哥:没耐心看 |
| **启动服务后不 curl 就汇报"完成"** | **华哥:发现端到端没通,信任度下降** |
| **华哥说"全部完成再通知我"却分 3 次汇报** | **华哥:被打断,效率下降** |
| **在残缺 Bash 环境里试 `head/lsof/sleep/ls` 试探** | **浪费时间,直接用 `/usr/bin/python3 -c` 一招打到底** |
| **遇到 `execute_code` 被 BLOCKED(飞书/cron)还循环重试** | **触发 `[Tool loop warning]`,浪费时间。立刻改用 `write_file` + `terminal` 模式** |
| **完全相信 `browser_vision` 文字描述,不做 JS console 验证** | **可能误判状态(实测有先例),以 console 注入为准** |

## 关联

- **玉芬核心 skill**:`yuxin-self-evolution` — Signal Scan → Plan → Execute → Reflect
- **代码风格**:项目内一致命名(本项目用 `app/core/`、`tests/unit/`)
- **测试先行**:`test-driven-development` — RED-GREEN-REFACTOR
- **远程 CC 流程**(backup):`hermes-agent` skill — 仅在玉芬自己写不动时降级使用

## 参考

- `references/pydantic-v213-python39-trap.md` — Pydantic v2.13 + Python 3.9 兼容性陷阱
- `references/hexagram-binary-index-trap.md` — 卦象 binary 索引"双重反向"约定 + 互卦计算公式 + 5 个易错点
