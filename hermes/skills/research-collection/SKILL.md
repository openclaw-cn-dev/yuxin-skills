---
name: research-collection
description: '渔芯资料收集技能 — 高效搜集行业信息、公司情报、技术资料，整理成结构化报告。触发条件：需要收集行业信息、公司背景、技术文档、竞品资料、市场数据时加载。覆盖渔芯RAS养殖、AI产品、市场调研场景。'
license: MIT
metadata:
  author: 渔芯科技
  version: "1.4.0"
---

# 渔芯资料收集技能

## 职责定位
高效搜集行业信息、公司情报、技术资料，整理成结构化报告。

## 核心工具

### 1. 网络搜索（Web Search）
- 搜索引擎深度抓取
- 行业报告网站
- 学术数据库

### 2. 竞品资料收集
按竞品清单批量搜索：
- 产品功能对比
- 定价策略
- 用户评价
- 公司背景

### 3. 技术文档检索
- 官方文档
- GitHub代码
- 技术博客
- API文档

## 输出格式

### 结构化调研报告
```
# [主题]调研报告

## 1. 核心发现
（3-5条最关键结论）

## 2. 详细信息
### 2.1 [子主题]
### 2.2 [子主题]

## 3. 数据来源
| 来源 | 链接 | 可靠性 |
|------|------|--------|
| XXX | url | 高/中/低 |

## 4. 知识库更新
（存入知识库的关键知识点）
```

## 交付风格：技术报告主动附"大白话版"

华哥在收到术语密度高的调研报告后，多次（最近 2026-09-07 MiniMind 报告）紧跟着要求"用小白能听懂的话解释一下"。规范：

- 交付含较多术语/参数表/英文的技术报告时，结尾**直接附一段"大白话版"**，不等华哥再问
- 大白话版写法：生活化比喻（如"乐高拼飞机""养小孩""3 块钱一杯奶茶钱"）、短句、少表格、先讲"图什么"再讲"是什么"、诚实点出"不能拿来干嘛"
- 与华哥既有偏好并存：正式版仍"结论先行 + 关键数字表"（硬件评估类尤其如此），大白话版放正文末尾作为第二层

## 调研原则
1. 多源交叉验证——不依赖单一来源
2. 优先一手数据——官方文档>媒体报道>道听途说
3. 知识溯源——每条知识标注来源URL
4. 积累优于输出——调研报告存入知识库持续迭代

## GitHub + arXiv 实操 pitfalls（来自 AI 出 3D 模型持续调研，2026-08-29）

### Pitfall 1: GitHub API 的 `size` 字段单位是 **KB**，不是 MB
```bash
# 错误解读：size=796917 → "796KB"
# 正确解读：size=796917 → "796917 KB ≈ 796 MB"
# 陷阱场景：gh-pages 项目页面（README 视频/缩略图）体积动辄上百 MB
```
**正确做法**：报告仓库体积时统一标注 KB 原值，再换算成 MB/GB。不要省略单位。

### Pitfall 2: arXiv API 必须用 `https://` + `-L` 重定向
```bash
# 错误（301 重定向丢 body）：
curl -s "http://export.arxiv.org/api/query?..."   # 0 bytes 空响应

# 正确：
curl -sL "https://export.arxiv.org/api/query?..."  # 200 OK 真实数据
```
HTTP 端点已永久重定向到 HTTPS，不带 `-L` 等于丢 body。所有 cron 必须用 `-L https://`。

### Pitfall 3: GitHub 项目页面与代码仓库可能分离
很多学术论文的开源分两层：
- **主仓**（如 `fraunhoferhhi/KISS-GS`）= gh-pages 项目页面，README 写"carries no source"
- **真代码仓**（如 `w-m/ffsplat`）= 实际 PyTorch 代码，通常通过 README 徽章反向链出去

**排查 SOP**：
```bash
# 1. 抓主仓 README 看是否有"carries no source"声明
curl -sL https://raw.githubusercontent.com/<org>/<repo>/main/README.md | head -20
# 2. 扫描 README 中的 GitHub 徽章链接（shields.io 模式 → 真实仓库名）
# 3. 对真代码仓重跑详情 API + license + size
```

### Pitfall 4: Hugging Face API 在沙箱环境通常不可达（IPv4+UA 都不行）
- `curl https://huggingface.co/api/spaces?search=...` → exit 28 timeout
- **不要反复重试**，直接标"D · 永久放弃"，改走浏览器或归档数据
- cron 自动化场景下，HF 通道视为不存在

### Pitfall 5: arXiv 论文开源追踪有 2-8 周滞后规律
- 论文发布后，开源代码平均 2-8 周内出现（顶级机构/Fraunhofer HHI 通常 < 2 周）
- 监控命令：`curl 'https://api.github.com/search/repositories?q=<PaperName>+in:name,description&sort=updated'`
- **同名陷阱**：搜论文名常碰到无关同名项目（"AquaFlow" = 水处理厂管理），要二次过滤 description

### Pitfall 6: 积累型报告的文件管理惯例
渔芯"AI 出 3D 模型"主题采用**双文件策略**：
1. **累积主文件**（`AI出3D模型研究_<起始日期>.md`）：每次增量都 `cat >>` 追加到末尾（保持文件连续性）
2. **日期归档文件**（`AI出3D模型研究_<本次日期>.md`）：本次飞书交付用，结构精简 + 指向主文件

这样既满足飞书按日期归档，又能在主文件看到完整演进。

**重要**：每一期 cron 都必须检查并 append 到主累积文件。上期漏 append 会在下一期被合并修复（避免历史断裂）。详见 `references/cron-execution-cheatsheet.md` §5。

### Pitfall 7: GitHub Sham-Repository 警惕（2026-08-30 实测）
GitHub 存在一批"占位/SEO/钓鱼"仓库：README 模板化 + 下载链接指向随机命名的 `.zip`（如 `__tests__/Software-hecastotheism.zip`）+ topics 17 个不相关标签。**典型案例**：`JJZ993/vcad`（0⭐ 但当日推送，疑似 spam）。

**SOP**：下载/clone/fork 前先验证 README 下载链接文件名是否与项目名一致 + topics 是否相关 + 创建时间 < 7 天 + 0 stars/forks = 高风险。

详见 `references/cron-execution-cheatsheet.md` §9。

### Pitfall 9: `hermes send` 与 cron auto-delivery 冲突（**2026-08-30 实测**）
当 cron task spec 明确写"**用 send_message 发飞书**"，但 cron 已配置 auto-delivery target（如 `feishu:oc_xxx`）：
- ❌ 直接 `hermes send -t feishu -f /tmp/msg.txt` 会被系统**静默 skip**，回显：
  ```
  Skipped send_message to feishu:oc_xxx. This cron job will already
  auto-deliver its final response to that same target.
  Put the intended user-facing content in your final response instead.
  ```
- ✅ **金标准**：把飞书 DM 汇报直接放在 final response 里（系统自动投递）
- ❌ 不要瞎试 `target` 拼接、换 chat_id、或加 `--subject`（系统层面拦截，不是格式问题）
- **判断口诀**：看到 `Skip send_message to <target>` → 立刻确认 auto-delivery target 与你想发的 target 一致 → 一致就写 final response，不一致才需要 `hermes send`
- **例外**：任务要求"发到**不同**地方"（另一个群/不同 chat）→ 此时 auto-delivery target ≠ 目标 target，`hermes send -t <新 target>` 会**真发**（但 final response 仍会被投递到原 auto-delivery target，二者并存）

详见 `references/cron-execution-cheatsheet.md` §1（玉芬 cron 体系的对应补充）。

### Pitfall 10: GitHub Search API 字段 nullable 守卫（**2026-08-30 实测**）
`api.github.com/search/repositories` 返回的仓库对象里 `license` 和 `description` 都可以是 `None`（不是空 `{}`）：

```python
# ❌ 触发 TypeError: 'NoneType' object is not subscriptable
for r in items:
    print(r.get('license', {}).get('spdx_id'))   # license=None 时 crash
    print(r.get('description', '')[:80])         # 也可能 None[:80]

# ✅ 正确写法：显式 None 守卫
for r in items:
    lic = r.get('license') or {}
    spdx = lic.get('spdx_id', 'N/A') if lic else 'N/A'
    desc = (r.get('description') or '')[:80]
    print(f"{spdx} | {desc}")
```

**触发场景**：
- 0⭐ + 新建仓 → 常无 `license` 字段
- search 关键词宽泛（如 `vision-to-cad`）→ description 可能是 SEO 占位符或留 None
- 同名 fork 集合（如多个 `Zero-to-CAD` fork）→ 字段空值比例高

**金标准**：所有 GitHub API 解析，**统一先 `or {}` / `or ''` 守卫，再 `.get(...)` 二次过滤**。批量解析前**先 dry-run 1 个 item** 看字段形状。

### Pitfall 11: 范式跟踪 — vision-to-CAD 头部厂商入场（**2026-08-30**）
`ADSKAILab/Zero-To-CAD-Qwen3-VL-2B`（arXiv:2604.24479）是 Autodesk AI Lab 官方下场的 vision-to-CAD 模型：多视图图像 → 可执行 CAD 程序，**2B 开源小模型 82.1% / IoU 0.747 超过 GPT-5.2 High (72.2% / 0.485)**。

**鱼芯意义**：不能只看 text-to-cad 一条线，**vision-to-cad 是鱼芯最易落地的场景**（现场拍图/PDF → 自动重建 CAD）。HuggingFace 模型权重公开，可本地推理。

**每次 AI-CAD cron 必查**：ADSKAILab/Zero-To-CAD 模型更新（新版 / 训练数据 / 引用数）。详见 `references/cron-execution-cheatsheet.md` §10。

### Pitfall 12: GitHub 组织 404 ≠ 仓库不存在（**2026-09-01 实测**）
跟踪头部厂商时，`api.github.com/orgs/<org>/repos` 可能返回 **404**（组织页面私有/未公开/改名），但仓库本身可能存在且可访问。

**实测案例**：
- `curl https://api.github.com/repos/ADSKAILab/Zero-To-CAD-Qwen3-VL-2B` → 404（仓库名/路径可能不对）
- `curl https://api.github.com/orgs/ADSKAILab/repos` → 404（组织不可达）
- 但 `api.github.com/search/repositories?q=Zero-To-CAD` → 命中 5 个 fork（如 `xuebadi/Zero-to-CAD` ⭐8）

**金标准**：
1. 组织 404 → **不能**判定"官方未公开代码"，可能是命名/权限问题
2. 改用 `search/repositories?q=<ProjectName>` 找 fork 集合（即使⭐个位数也是真实信号）
3. 抓 arXiv 论文摘要页确认官方组织名（论文署名 vs GitHub org 名称可能不同）
4. 记录"组织暂不可达"作为跟踪状态，**不要**在报告中写"项目已死"

详见 `references/cron-execution-cheatsheet.md` §11（待补）。

### Pitfall 13: 并行子代理调研全员超时 → 自研兜底模式（2026-09-06 OPC出海项目实测）
**症状**：delegate_task 派 3 路并行 web 调研子代理，600s 硬超时，各完成 14-24 次 API 调用但**零产出**（文件未落盘）。
**根因**：子代理用慢模型 + 外网请求慢，600s 上限内跑不完"多轮搜索+写文件"全链路。
**兜底 SOP（实测有效）**：
1. 不再重试子代理，玉芬直研：一轮 **2-4 个并行 web_search**（查询词一半中文一半英文，避开纯中文宽泛词——"OPC 一人公司 AI"这类组合会返回垃圾结果，加英文锚词如 "One Person Company"）
2. 关键页用 curl 抓全文（见 Pitfall 14），控制 2-3 个源
3. 直接写分报告 + 总报告，未核实处标[待核实]
**决策口诀**：子代理调研超时一次 → 立即切自研，不再赌第二次 600s。

**Pitfall 13-b 细化（2026-09-10 五项目批量调研实测）——超时后别急着全切自研，「查盘 + 限量重派」更省**：
1. **超时 ≠ 零产出**：先 `find <项目目录> -type f -mmin -20` 查部分落盘（实测 3 路里 2 路超时但分别已写 2/3、1/3 文件）。已落盘的不重做
2. **只派「补缺」任务**：goal 写明"已有 X/Y 两份不要动，只补第 Z 份"，不重复花钱
3. **重派必带硬约束**：①工具调用预算（"限用 10-12 次工具调用"）②增量写盘纪律（"每完成一份立即写盘，不要最后一起写"）③搜索预算（"每份只做 2-3 次精准搜索"）。实测同一任务从 600s 超时降到 155-360s 完成；超时根因多是**搜索轮次失控**而非单次调用慢
4. **delegate_task 单次最多 3 个 tasks**（max_concurrent_children=3），5 项目类批量单要拆两批

**Pitfall 15: 子代理写盘核验用时间窗 find，别用文件名 glob（2026-09-10 实测）**
`ls -l <目录>/*2026-09-10*.md` 与 `find -name "*<日期>*" -type f` 在中文路径下连续两次返回空（疑似 NFD 归一化/glob 展开问题），但文件实际在。**可靠核验**：`find "<绝对路径>" -type f -mmin -20`（按修改时间窗扫）再补 `ls -l` 看字节大小。子代理自称"已落盘"永远亲自查盘后才向华哥报完成。

### Pitfall 14: web_extract 后端未配置时的网页全文提取配方（2026-09-06 实测）
**症状**：`web_extract` 报错 "DuckDuckGo (ddgs) is a search-only backend and cannot extract URL content"（extract_backend 只支持 firecrawl/tavily/exa/parallel，未配置时整条路堵死）。
**替代配方**（curl + 标签剥离，一次拿正文前 N 字符）：
```bash
curl -sL --max-time 25 -A "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)" "$URL" | python3 -c "
import sys,re,html
t=sys.stdin.read()
t=re.sub(r'<script[\s\S]*?</script>','',t); t=re.sub(r'<style[\s\S]*?</style>','',t)
t=re.sub(r'<[^>]+>',' ',t); t=html.unescape(t); t=re.sub(r'\s+',' ',t)
print(t[:3500])"
```
**要点**：①UA 必须带，否则部分站点拒 ②一次 2-3 个源足够，全文前 3500 字符已覆盖正文 ③dump 页（如阿里云文章）要先 `find` 定位正文起点再截取，避免抓到整页导航噪音。这是提取配方的固有能力差异，非工具故障；如需整页 Markdown 再考虑配 extract_backend。

## 触发关键词

### GitHub
```bash
curl -s 'https://api.github.com/search/repositories?q={关键词}&sort=stars&order=desc&per_page=15' -o /tmp/gh.json
# 关键字段：stargazers_count / license.spdx_id / pushed_at / topics
```

### arXiv（⚠️ 必须 -L 跟重定向）
```bash
curl -sL 'https://export.arxiv.org/api/query?search_query=all:{关键词}&sortBy=submittedDate&max_results=8' -o /tmp/arxiv.xml
# 不带 -L 会返回 0 bytes（HTTP 301 强制 https）
```

### HuggingFace Spaces（❌ API 永久不可达）
- `https://huggingface.co/api/spaces` 连续多期 cron 返回 0 bytes
- 改用 `web_search 'huggingface.co spaces text-to-cad'` 兜底

详见 `references/cron-execution-cheatsheet.md` 完整命令模板 + 踩坑。

## 鱼芯"路径决策矩阵"框架

开源自技术选型调研时，**Stars × License × 活跃度 × 适配度**四维评分：

| 评估项 | 鱼芯默认偏好 |
|--------|--------------|
| License | MIT > Apache-2.0 > NOASSERTION(需法务) > GPL/AGPL(剔除) |
| 活跃度 | 日更 > 周更 > 月更 > 停滞(剔除) |
| Stars | 仅作参考，不作核心标准（30 天新项目可能暴涨） |
| 适配度 | 鱼芯业务场景（RAS 设备/制造工艺/参数库）匹配度 |

**输出格式**：决策矩阵表 + v1/v2 版本号管理（路径 B v2.0 表达"经过 1 轮迭代"）。

## Cron 模式汇报陷阱

任务指令里**明确写** "用 send_message 发飞书" **不等于** 必须调 `hermes send`。
系统会按 auto-delivery target 是否与你发送的 target 一致决定是否拦截：

- **auto-delivery target == 你要发的 target** → 直接写 final response（系统自动投递），调 `hermes send` 会被 skip（见 Pitfall 9）
- **auto-delivery target ≠ 你要发的 target**（如 cron 默认发 DM、任务要求发群）→ `hermes send -t <新 target>` 真发，final response 也会被投递 = **双投递**
- **任务说"只汇报/输出"没明确 send** → 靠 final response auto-delivery，**不调用 send**

判断口诀详见 Pitfall 9；详见 `references/cron-execution-cheatsheet.md` §1。

### Pitfall 13: web_extract 后端可能只配了搜索（2026-09-06 实测）
`web_extract` 返回 `{"success": false, "error": "...(ddgs) is a search-only backend and cannot extract URL content. Set web.extract_backend to firecrawl, tavily, exa, or parallel."}` 时不要反复重试，直接走 curl 抓取 + 正则剥标签的兜底配方（10 行搞定，还能用 `[:N]` 控制回传体量省 token）：

```bash
curl -sL --max-time 25 -A "Mozilla/5.0" "<url>" | python3 -c "
import sys,re,html
t=sys.stdin.read()
t=re.sub(r'<script[\s\S]*?</script>','',t); t=re.sub(r'<style[\s\S]*?</style>','',t)
t=re.sub(r'<[^>]+>',' ',t); t=html.unescape(t); t=re.sub(r'\s+',' ',t)
print(t[:3500])"
```

注意：这不是"web_extract 坏了"——是 extract_backend 配置问题，可由用户改配置根治；在未改配置前，以上配方是稳定替代。深读 1-2 个关键页足够，不要对搜索结果逐条 curl（token 纪律）。

## 触发关键词
"调研"、"收集"、"搜索"、"竞品分析"、"行业报告"、"技术资料"、"情报"、"市场数据"、"资料整理"

## 适用场景
- LookForge Phase1 市场调研
- 竞品动态跟踪
- 供应商背景调查
- 技术选型调研
- 行业趋势分析
- AI 出 CAD 图等垂直技术追踪（GitHub 热门 + arXiv 学术双线）

## 华哥口头立项 SOP（"新增调研项目：X" 类指令，2026-09-06 固化）

1. **语义验证**：华哥指令常带缩写代号（如 OPC），先 1 次 web_search 验证通行语义再动手，不反问（OPC=One Person Company 一人公司，非工业 OPC UA）
2. **立项**：建 `~/6-产品研发/渔芯独角兽/01-开发中/研-<主题>/`（研-前缀=调研中，区别于 app-/卖-/学-），写 INDEX.md（定义/研究框架/产出规划/进度）
3. **调研执行 → 汇总**：总报告命名 `00-总报告.md`（一句话结论先行+行动建议+来源）；分报告放 `02-调研/`
4. **入库**：staging_save.py 必须用绝对路径 `/Users/hua/.hermes/scripts/` 调用且只收 `--title/--content/--source/--agent/--target`（无 --tag）；保存后检查输出路径是否被劫持到 profile home，是则手动 cp 到 `/Users/hua/rkr_staging/文档中转站/01-调研资料/` 并手写 `.md.meta.json`（详见 staging-helper 陷阱5 v1.5+）
5. **飞书汇报**：结论先行+关键数字+建议+文件路径+**编号待定夺项**
6. **数字批复语式**：华哥回"1"=执行第①项；"2 顺序进行"=对应项批准且按序推进。批复后直接落地，不重复确认

## 定位升级 SOP（华哥中途定调"完全独立项目/拿出去分享"类指令，2026-09-11 AI法典实测固化）

已立项的调研项目，华哥追加一句"这将会是一个完全独立的项目，会成为独角兽拿出去跟其它分享"——这是**产出标准升级信号**，不是表态回应。正确动作：当日重构交付体系四件套，直接落地不反问：

1. **总纲改造**（项目 README）：新增"项目定位"节，引用华哥原话+日期，写明三层标准：
   - ① 主体内容中立通用——以行业通用主体书写（如"AI 服务提供者"），不预设读者是渔芯
   - ② 对外可发布质量——每条结论必须有法规条款号/真实案例支撑，出处链接可访问并注明检索日期，查不到明确写"暂未查到"不凑数
   - ③ 内部适用标记（如"渔芯是否涉及"列）降级为附加层——整份文档抽掉该列仍完整成立
2. **新增对外发布目录**（如 `04-对外发布版/`）：合订本入口 README + 版本号（v0.1 起，内容变动递增）+ 署名（渔芯科技（Yuxin）· 独角兽研究）+ 每份文档头部免责声明（"公开法规与公开案例的整理研究，不构成法律意见"类）
3. **执行手册/cron-prompt 同步纪律**：把"中立视角书写、链接真实可访问、对外成立标准"写进每轮执行纪律段——cron 每轮重读手册即自动按新标准执行，无需改 cron job 本身
4. **终局产物双轨制**：对外=合订本（分享载体），对内=自家产品/业务对照清单（衍生应用）。两者从同一调研产出派生（剥离内部列即得对外版），不做两份重复劳动

**Pitfall**：
- 对外版 ≠ 内部版删两行。中立化涉及表格列、案例选择、措辞主体的重写——执行手册里要写明"剥离内部标记后中立化重写"，不能只写"同步一份"
- 对外文档缺版本号或免责声明就拿不出手——这两样是发布最低配置，建目录当天就写进合订本模板
- 定位升级后"为什么做"第一理由要换成外部价值（如"没人把各领域禁区整合成可执行负面清单——这是空白，也是对外分享的价值点"），内部需求退居第 2/3 条

## 华哥"XX 加入轮换"指令 SOP（2026-09-07 P62 工程施工工作台实操固化）

轮换池真源 = `/Users/hua/rkr_staging/文档库/4-360行项目调研/调研项目清单.md` 的**项目行尾标记**（"未加入 cron 轮换(按 PITFALL #26)"= 闸门；新项目默认不轮换，等华哥明示）。执行四步：

1. **清单行尾标记翻"✅ 已加入"**——patch 锚点必须带足上下文（多行共享同一尾格式，防误伤兄弟项目行）
2. **update 三个 daily-research cron prompt 硬编码计数**：`~/.hermes/profiles/zhenglishi/cron/jobs.json`（daily-research-daytime / night / report-22，python json load/edit/dump，**先备份**；v1.7 时代遗留"27 个项目"过时计数是 59-64 号卡轮换的根因之一）
3. **项目 INDEX.md 状态同步**（"未加入"→"已加入"）+ **清单更新记录加版本行**（vN.N 格式）
4. 验证：三个 cron prompt 无过时计数残留；远端轮换执行者还有全局主控 `a5f2061c110c`（动态读清单，无需改）

提示：夜间跳过式滚动会自动覆盖无近期笔记的新入池项目（**当晚即产出**）；白天深度版按序轮到。未获批兄弟项目（如 59/60/61/63/64）保持"未加入"标记不动。
7. **字母选项批复语式**（2026-09-07 实例："1-c,2-b,3-是"）：出待定夺项时**每项给出可映射的选项标签**（路线用 A/B/C，二选一标注 a/b 或直接写"选 X 还是 Y"）；批复时逐项映射：`1-c`=第①项选 C、`2-b`=第②项选 b（按该题选项序或语义对应，如 1.7B/4B 题的"b"=4B）、`3-是`=第③项批准。**解析结果在汇报中写明"按此解读执行"+透明列出对应表**，给华哥纠错机会但不设问等待；歧义项（无明确选项标签的）按语义就近解析并在汇报标注。同日补充指令（如"暂不开源"）立即覆盖早前批复并回写方案文档
7. **批量批复语式**（2026-09-07 固化）：华哥一句"需拍板项目全选'是'"= 同意**当时所有**挂起的待拍板/待定夺清单（常跨多个项目/agent）。处理：session_search 扫全部"待您拍板/待华哥定夺/等您拍板"清单 → 全部按"同意"落地并逐项目登记批复原文（INDEX §行动项 / 总报告定夺节 / 同步清单§八）→ 汇报列出已批清单全文供抽查否决；需选项的项取方案默认值并单独标注，不反向追问；涉对外实体动作（备案提交/付费注册）只批到"启动准备"，实体动作前再回报
8. **报告可读性分层**（2026-09-07 固化）：给华哥的技术分析报告正文可保留专业细节与表格，但必须自带 3-5 句"大白话版"（比喻、零术语、结论先行）——华哥典型追问"用小白能听懂的话解释一下"，主动分层别等追问
9. **轮换指令**：华哥说「XX 号项目加入调研轮换，继续深化」→ 按 `references/360hang-rotation-ops.md` 四步流程执行（清单行尾标记是闸门 + 3 个 daily-research cron 硬编码同步 + 项目 INDEX 状态 + 更新记录版本行）

## 调研执行模式选择：子代理并行 vs 直研（2026-09-06 实测）

- delegate_task 批量 web 调研子代理有 **600s 硬超时**：3 路并行各 14-24 次 API 调用全部 timeout 且**零落盘**（慢模型/慢外网下高发）
- 若仍派子代理：必须限定"最多 N 次 web_search，**先落盘再补充**"，让子代理写文件而非把全文塞 final summary
- **fallback 直研模式**（实测有效，2 轮搞定）：每轮 3-4 个 web_search 并行一批发 → 挑 1-2 个关键页 `curl -sL` + python 正则剥标签抽正文 → 自己写报告。上下文可控、交叉验证自己把关
- web_extract 不可用/未配 extract_backend 时的 curl 抓取法：见 `references/***SECRET***.md` §5

## References 增补

- `references/kepu-2026-09-10-dispatch-log.md` — 「主要丰富以下项目资料」批量补研 SOP（2026-09-10 五项目 15 份实测）：①查盘先行（find -mmin 定位资料最薄项目+读各项目 README/INDEX 摸现状）②分身 prompt 四要素（现状上下文 / 落盘绝对路径 / 每份 ≤100 行+来源链接 / 工具调用预算+增量写盘纪律）③**按维度去重**——同一项目不同批次补不同维度（技术 vs 商业），写明"不重复已有 X"防重复建设 ④中文项目名目录的 find 落盘核验法 ⑤超时查盘补缺流程实例（3 次重派全成功）

- `references/***SECRET***.md` — OPC（一人公司）出海知识库快照：已验证单人公司案例收入表、GEO 工具竞品定价与空档、MoR 收款路径、中国生态、whois 域名批量查重 one-liner、CitedLens landing 模板指针

- `references/***SECRET***.md` — 渔芯 01-开发中 项目池现状快照（五批补研后的资料厚度分布、华哥口头指令的项目简称↔目录名映射如「OPC出海」=研-AI时代OPC出海、富资料项目如工程施工大模型 34G 的构成），下次"丰富 XX 项目资料"类指令先查此表避免重新扫描全盘
