---
name: xiaohongshu-layout-factory
description: 小红书排版工厂，把一张 IP 形象图或一套 IP 素材搭建成可反复调用的专属小红书 3:4 图集排版 Skill。适用于品牌方、IP 持有者和创作者制作 HTML 排版母模板、动作素材包、视觉系统、真实文章 Demo 与 2K 导出流程。当用户说“小红书排版工厂”“做一个我自己 IP 的小红书排版 Skill”“给这个品牌做一套图集排版 Skill”“复刻一套小红书图集 Skill”“xhs skill 工厂”“ip-xhs-builder”或“图集流水线”时使用。默认产物进入 ~/Downloads。
license: MIT
metadata:
  version: "2026.08.23"
  display_name: "小红书排版工厂"
---

# 小红书排版工厂

把"一张 IP 图 → 一套属于自己的小红书图集生成 skill"的完整搭建路径打包成元 skill。用户按引导走完，最后得到一个触发关键词喊一声就能把文章排成 3:4 图集的 Skill。**终点是可反复触发的新 Skill，不是一套图。**

本工厂**自包含**：抠图脚本、图集闸门、字体加载、版面骨架都在本目录，**不依赖其它 Skill**。可以单独分享、单独安装。

## 适用场景

- 品牌方 / IP 持有者 / 创作者想把自有 IP 沉淀成小红书图集生产线（文章进、图集出）
- 已经有同 IP 多动作抠图，想要一条竖版图集产线
- 给客户交付专属排版系统

调性、命名、文案口吻**由 IP 视觉 DNA 和品牌属性反推**：知识博主走笔记感、潮玩走活泼、商务走冷静，接近哪个方向就用哪个方向。

## 使用前选模式（Default / Compact）

触发 skill 后**第一句话先问用户走哪种模式**（默认 Default，用户明确说 Compact / 极简 / 快跑 / 我熟了 才切）：

| 模式 | 适用 | 输出风格 | token 成本 |
|---|---|---|---|
| **Default**（默认） | 首次用 / 想看完整解释 | 每步展开理由、引用 references、写踩坑记录 | 高 |
| **Compact**（极简确认） | 熟悉流程的回头客 | 每步只给"决策点 + 默认选项 + 一句后果"，回 OK 走默认 | 节省 ~60% |

**两种模式都强制保留**：Step 0 四问 / Step 1 底色三档 + 抠图 A/B / Step 1.5 素材闸门 / Step 2b 拍板 / Step 2.5 头像校准 / Step 3 闸门检查 / Step 7 验收 + 导出菜单。Compact 只省"输出文字量"，不省"必经决策点"。

## 工作流（8 步，详细 prompt 见 references/workflow.md）

### Step 0 · 备料对齐

触发后**第一件事**：用 AskUserQuestion 一次问清 4 件事（不要分多轮问）：

1. **IP 形象图路径**（PNG / JPG；没有透明背景 Step 1 处理）
2. **新 Skill 命名 + 触发词**：中文名（如「XX小红书排版」）+ 触发短语 3-5 个，调性按 IP DNA 反推
3. **品牌署名三件**：footer 左侧名字 / host stamp 名字 / 末页 @账号名
4. **素材图集状态（必问，不可省略）**：有没有同 IP 多动作图集？有给绝对路径（≥8 张直接用；<8 张问补齐还是降级）；没有 → Step 1.5 强制生成，规模二选一：**20 张精简包 / 45 张完整包**

四个答案全收到才进 Step 1。

### Step 1 · IP 抠图（如果需要）

先问**底色三档**：透明底（默认推荐）/ 白底 / 指定底色。需要抠图时**必须问用户选 A 或 B**：

- **A · skill 帮抠**：跑本工厂 `assets/cutout.swift`（macOS Vision，14+；失败自动转 B）
  `swift "<本 Skill 目录>/assets/cutout.swift" <输入> <输出>`
- **B · 用户自己抠**：pixian.ai / rembg / PS / 即梦消除背景，抠完回传路径，**期间停住等用户**

### Step 1.5 · 素材图集闸门（没有图集就必须生成）

**硬门槛，不是可选项。**完整 prompt 见 `references/asset-pack.md`：IP 定位卡确认 → 规模二选一（20 精简 / 45 完整）→ 动作清单 + 「图集页面 → 动作」映射表 → 生图通道判断（探测到本机生图能力就直接用，探测不到才问 API / 提示词包二选一）。

- **没有图集默认生成**，不再问"要不要生成"
- **用户明确拒绝** → 新 Skill 的 quality-checklist.md 写明降级状态，交付时提示风险
- 图集未入库且用户未签收降级 → **禁止进 Step 2 之后的正式产线**

### Step 2 · 反推视觉系统 → 对齐讨论 → 锁定 design tokens

#### Step 2a · 出"建议稿"

分析 IP 图后**不直接出最终 token 表**，按 6 个维度各给 2-3 候选 + 推荐项 + 一句理由：① 底色气质（纸感渐变三段）② 主色（标题 + 强调）③ 金/点缀色系（quote 条、chip、高亮块、星点两色）④ 字体调性（中文主字体 + 英文衬线 italic + 手写体；加载规则见 `references/fonts.md`，国内源优先）⑤ 装饰语言（星点字符、chip 形态、光晕色）⑥ 主题命名 3 候选。

#### Step 2b · 对齐讨论（必经，双模式）

用 AskUserQuestion 让用户选：**模式 A 逐项确认**（6 维一项项拍板）或 **模式 B 授权智能选**（按推荐项一次决策，出完整 tokens 草稿让用户过目）。无论 A/B，**用户明确说 OK 才进 Step 2.5**。tokens 存 `~/Downloads/<主题名>-xhs-skill-demo/design-tokens.md`，标明走了哪个模式。

### Step 2.5 · 头像基准校准（必做）

host stamp 圆框裁切必须实测：头像图放进 `.host .av`（`width:130%` + `object-position:top center` 起步）→ 渲染一张内容页 → PIL 裁剪放大右上角目检 → 微调 `margin-top` / `margin-left`（每次 2-4px / 2%）直到**脸落圆框正中、头顶不切** → 实测值写进新 Skill 模板注释。

### Step 3 · 写 demo 图集

**🚫 进 Step 3 前必须通过"素材包硬闸门"三项检查，任何一项未通过 → 回退 Step 1 / 1.5，禁止用单张立绘凑合**：

1. IP 立绘就绪（底色符合 Step 1 选择）
2. 多动作素材包 ≥8 张合格（标准 12+），**每张 PNG 短边 ≥ 1000px**
3. `emoji-catalog.md` 4 维标签写完（文件名即语义的图集可豁免，写明映射规则即可）

**血泪教训**：先用单图凑合出图集、事后补素材回填 = 所有页面尺寸位置重算 + 截图全部重出，整轮工作重做。**绝对禁止"先凑合后补图"**，唯一例外是用户签收降级模式。

通过闸门后：拿用户**一篇真实文章**（不造假内容），读 `references/card-templates.md` 选骨架、`references/universal-rules.md` 拿硬规则、design-tokens.md 拿色板字体，复制 `assets/template.html` 换 :root tokens 写 `build.py`，生成 5-8 页 demo（含案例页则 12-15 页），2x 渲染，`preview.html` 给用户看。demo 目录默认 `~/Downloads/<主题名>-xhs-skill-demo/`。

### Step 4 · 迭代调优

- 用户批注做**最小修改**，只重渲受影响页
- **Step 4.5 逐页体检（demo 出来后默认跑）**：逐页读 PNG 过 `universal-rules.md` 出片自检 13 项 + 防遮挡维度，输出问题清单，用户勾选后再改
- **Step 4.6 反馈沉淀 checkpoint（每轮反馈后必做）**：每翻盘一个决策立刻归档进将要生成的新 Skill 草稿。**只修 demo 不沉淀 = 下次重踩**

### Step 5 · 固化成新 Skill

demo 满意后生成 skill 文件结构，**默认落到下载文件夹**：

```
~/Downloads/<用户起的名字>/
├── SKILL.md
├── references/
│   ├── design-system.md
│   ├── card-templates.md
│   ├── tone-guide.md
│   ├── quality-checklist.md
│   ├── emoji-catalog.md
│   ├── template.html
│   └── case-samples/
└── assets/
    ├── host.png
    ├── cutout.swift          # 从本工厂拷过去，实例也独立可抠图
    └── font-loader.html
```

当前环境如果探测到 agent skills 根目录（`~/.workbuddy/skills` / `~/.claude/skills` / `~/.cursor/skills` / `~/.codex/skills` / `~/.agents/skills`），再**额外拷一份进去**方便立刻触发。交付和分享以 `~/Downloads/<名字>/` 为准，不要写死 Obsidian 或某个用户的笔记库路径。

**必须自带案例样板库**：把 Step 3-4 跑通的 demo 图集打包成自包含单文件案例网页存进 `references/case-samples/`。页面清单必须按实际产出核对。

### Step 6 · 图集入库 + 智能选图

写 `emoji-catalog.md` 4 维标签 + 选图优先级（页面类型粗筛 → 关键词 → 情绪 → 回退默认立绘）。**"同套图不重复"只是弱偏好**，场景匹配永远优先。

### Step 7 · 验收 + 导出交付

- 用户用触发词跑一个测试主题，输出过出片自检 13 项
- 检查 `~/Downloads/<名字>/` 完整落盘；若已同步运行库也列路径。交付说明列 skill 名 / 触发词 / 安装路径 / 文件清单 / 测试图集路径。**只给 PNG 不算完成**

#### 导出四件套（用户要求"导出"时，必经决策点）

**先用 AskUserQuestion 出菜单**：① **2K PNG**（默认已产出）② **3x 超清 PNG** ③ **PDF 合集** ④ **zip 打包**（图集 zip / 新 Skill 压缩包，默认也放到 `~/Downloads/`）。命令见 `references/workflow.md` Step 7。

## 硬规则（写死在每个实例里，全文见 references/universal-rules.md）

- **比例只做 3:4**：CSS 画布 1080×1440
- **渲染一律 2x 输出 2160×2880**；**素材零压缩**
- **零投影**：全页禁止 box-shadow / drop-shadow
- **字体国内优先**：用 `assets/font-loader.html`，禁止只挂 Google Fonts
- **60px 安全边距**；透明容器 + 1.5px 细线
- **总-分-总**：封面 hero → 内容页（host stamp）→ 收尾 hero
- **笔记体文案**；标题内数字英文不加空格；案例页提示词放完整全文
- 无页码、水印、logo、日期；无破折号；禁用「不是X，而是Y」
- **z-index**：装饰 1 / 线框 2 / IP 立绘 3 / 文字 4 / host stamp 5
- **每次反复都要把决策固化进 references**
- **素材图集闸门**：没图集先过定位卡生成入库

## 跨 Agent 适配

- AskUserQuestion 不可用就文本逐条问，决策点一个不能省
- 产出默认 `~/Downloads/`；运行库按当前环境探测，探测不到就只留 Downloads
- `cutout.swift` 只在 macOS 14+ 可用，其它系统走"用户自己抠"
- 无头 Chrome 路径按系统探测；`~` 展开为当前 HOME，不写死用户名
- 生图通道探测跨 agent 天然成立，都没有就走提示词包模式

## 边界

- **小红书排版**：本工厂思路的一个已落地实例（阿真自用视觉）。有就当样板看，没有不影响本工厂运行
- **其它 PPT / 讲义工厂**：16:9 deck 是另一条产线，本工厂不调用、不要求安装
- **xiaohongshu-note-images**：纯生图笔记，不是 HTML 排版
- **xhs-web-layout**：已归档旧版网页工具，只有用户点名才碰

## 触发示例

> "做一个我自己 IP 的小红书排版 Skill，IP 图在 ~/Downloads/myip.png"
> → Step 0 四问 → 抠图 → 图集闸门 → tokens 对齐 → 头像校准 → demo → 固化到 ~/Downloads

> "小红书排版工厂"
> → 先 Step 0 问 4 件事

## 默认输出路径

全部默认进下载文件夹，不写死笔记库：

- 中间产物（design-tokens / demo）→ `~/Downloads/<主题名>-xhs-skill-demo/`
- 动作素材包 → `~/Downloads/<主题名>-emoji-pack/`
- 最终 skill → `~/Downloads/<用户起的名字>/`（探测到运行库再额外同步一份）
- 跑出来的图集 → `~/Downloads/<日期-主题>-小红书排版/`

## 参考资料

- `references/workflow.md`：7 步详细 prompt
- `references/asset-pack.md`：图集闸门 / 定位卡 / 动作清单 / 生图通道（自带）
- `references/fonts.md`：字体国内优先加载规则
- `references/universal-rules.md`：跨 IP 硬规则 + 出片自检 13 项
- `references/card-templates.md`：4 类页面骨架
- `references/pitfalls.md`：避坑指南
- `references/case-azhen.md`：阿真「小红书排版」成功样板（有则参考，无则跳过）
- `assets/template.html`：token 化种子模板
- `assets/font-loader.html`：字体三级加载
- `assets/cutout.swift`：macOS Vision 抠图
