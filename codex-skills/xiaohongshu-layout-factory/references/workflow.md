# 小红书排版工厂 · 八步工作流详解

每步给可直接执行的 prompt 要点。硬规则见 `universal-rules.md`，骨架见 `card-templates.md`，图集闸门见 `asset-pack.md`，字体见 `fonts.md`，可运行模板在 `assets/template.html`，坑先读 `pitfalls.md`。

## Step 0 · 备料对齐（四问）

用 AskUserQuestion（不可用就文本逐条）一次问清：

1. **IP 形象图路径**：PNG / JPG 都行，底色 Step 1 处理
2. **新 Skill 命名 + 触发词**：中文名 + 触发短语 3-5 个。命名调性按 IP DNA 反推（知识博主走"笔记/小课堂"、潮玩走"图鉴/乐园"、商务走"简报/洞察"）
3. **品牌署名三件**：footer 名字 / host stamp 名字 / 末页 @账号名（三处可以不同，逐一确认）
4. **素材图集状态（必问）**："有没有同 IP 多动作透明抠图 / 表情包文件夹？有给绝对路径，没有直说。"
   - 有 ≥8 张 → 拷路径记录，Step 6 补 catalog
   - 有但 <8 张 → 问补齐（走 Step 1.5 增量生成）还是降级
   - 没有 → Step 1.5 强制生成，先预告规模二选一（20 精简 / 45 完整）

## Step 1 · IP 抠图（如果需要）

1. **底色三档必问**：透明底（默认推荐）/ 白底 / 指定底色，写进 design tokens
2. 图已是目标底 → 跳过
3. 需要抠图必问 A/B：
   - **A · skill 帮抠**：`swift "<本 Skill 目录>/assets/cutout.swift" <输入> <输出>`（macOS Vision，14+；失败自动转 B）
   - **B · 用户自己抠**：pixian.ai / rembg / PS / 即梦消除背景，回传路径前停住等用户

## Step 1.5 · 素材图集闸门

完整 prompt 与定位卡 / 动作清单 / 生图通道 **见 `references/asset-pack.md`**（本工厂自带，不要去读其它 Skill）。页面映射用下表：

| 页面类型 | 推荐动作类 |
|---|---|
| 封面 hero | 最有代表性的工作/展示动作（扛机、举物、打招呼） |
| 观点/清单内容页 | 思考、灯泡、对勾、记笔记 |
| 对比页 | 双物对比、摊手二选一 |
| 数据/上涨页 | 庆祝、欢呼、指向上方 |
| 案例页 | 不放立绘（版面留给插图 + 提示词） |
| 收尾 hero | 比心、挥手、邀请手势 |
| host 头像 | 正面半身挥手/微笑 |

没图集默认生成不再问"要不要"；生图通道先探测本机能力，探测到直接用；用户拒绝生成 → 降级状态写进新 Skill 的 quality-checklist.md；图集未入库且未签收降级 → 不开正式产线。素材包默认输出 `~/Downloads/<主题名>-emoji-pack/`。

## Step 2 · 反推视觉系统 → 对齐 → 锁 tokens

### Step 2a · 建议稿

读 IP 图逐维分析（主色提取 / 明度氛围 / 线条气质 / 装饰母题），按 6 维各给 2-3 候选 + 推荐 + 一句理由：

1. 底色气质 → `--bg-a/b/c` 渐变三段 + hero 双 radial
2. 主色 → `--title` `--accent`
3. 金/点缀色系 → `--gold` `--gold-soft` `--gold-deep` `--pop` `--line`
4. 字体三角色（中文主字体 / 英文衬线 italic / 手写体；加载走 `assets/font-loader.html`，规则见 `fonts.md`）
5. 装饰语言（星点字符组 / chip 形态 / 光晕色 `--glow-a/b`）
6. 主题命名 3 候选

### Step 2b · 对齐拍板（必经）

AskUserQuestion 选模式：**A 逐项确认** / **B 授权智能选**。最终都要用户明确"OK 进下一步"。tokens 落盘 `~/Downloads/<主题名>-xhs-skill-demo/design-tokens.md`。

## Step 2.5 · 头像基准校准（必做，不可跳）

1. host 头像放进 `.host .av`：`width:130%;object-fit:cover;object-position:top center` 起步
2. 渲染任一内容页，PIL 裁右上角放大：`im.crop((640,30,1080,200)).resize((880,340))`
3. 目检两问：脸在圆框正中吗？头顶被切了吗？
4. 不过就微调 `margin-top`（±2-4px）/ `margin-left`（±2%），重渲重检直到通过
5. 实测值写进新 Skill `references/template.html` 的注释（阿真挥手图 = `-4px / -12%`，仅参考不照抄）

## Step 3 · demo 图集

**先过硬闸门三项**（任何一项不过回退 Step 1 / 1.5）：① 立绘就绪 ② 图集 ≥8 张、短边 ≥1000px ③ catalog 或映射规则写完。禁止单图凑合。

通过后：

1. 要用户**一篇真实文章**，完整读，压成页面计划
2. 建目录 `~/Downloads/<主题名>-xhs-skill-demo/`，复制 `assets/template.html`（已含国内优先字体加载）换 :root tokens + 署名，写 `build.py` 生成 `01.html`-`NN.html` + `preview.html`，素材原图 `cp` 进 `assets/`
3. 渲染（2x 保画质；`--virtual-time-budget` **必带**）：

   ```bash
   "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless --disable-gpu \
     --hide-scrollbars --force-device-scale-factor=2 --window-size=1080,1440 \
     --virtual-time-budget=15000 \
     "--screenshot=output/01.png" "file://<绝对路径>/01.html"
   ```

4. `sips` 抽检 2160×2880；标题区拼对照表验字体统一
5. 逐页读 PNG 过出片自检 13 项，打开 `preview.html` 给用户

## Step 4 · 迭代调优

- 每条批注**最小修改**，只重渲受影响页
- **Step 4.5 逐页体检**：字压字 / 线被压 / IP 压字 / 字体回退 / 提示词截断 / 空白区过大
- **Step 4.6 反馈沉淀 checkpoint**：翻盘决策当场归档到新 Skill 草稿

## Step 5 · 固化成新 Skill

默认落盘 `~/Downloads/<名字>/`：

- 新 SKILL.md 骨架可参考 `case-azhen.md` 指向的样板（本机没有该实例就按本工厂 template + universal-rules 从零写）
- 把本工厂的 `assets/cutout.swift` 和 `assets/font-loader.html` **拷进新 Skill**，保证实例单独分享也能抠图、也能加载字体
- 探测到当前 agent 的 skills 根就额外同步一份；没有就不强求
- **案例样板库必做**；页面清单按实际 HTML 核对

## Step 6 · 图集入库 + 智能选图

- 文件名无语义 → Read 逐张识图，写 `emoji-catalog.md` 4 维标签
- 文件名即语义 → catalog 只写映射规则
- 选图优先级：页面类型粗筛 → 关键词 → 情绪 → 回退默认立绘
- 用户拒绝图集 → catalog 也要存在，写明降级

## Step 7 · 验收 + 导出交付

1. 让用户用触发词跑一个测试主题，逐页过出片自检 13 项
2. 检查 `~/Downloads/<名字>/` 完整；交付说明列 skill 名 / 触发词 / 路径 / 文件清单 / 测试图集。**只交 PNG 不算完成**
3. 导出四件套默认也进 `~/Downloads/`

| 选项 | 做法 | 自检 |
|---|---|---|
| ① 2K PNG | 默认已产出，直接交付 `output/` | sips 尺寸 + 字体统一 |
| ② 3x 超清 PNG（3240×4320） | `--force-device-scale-factor=3` 重跑 | 重验字体与尺寸 |
| ③ PDF 合集 | PIL 拼页，保存到 `~/Downloads/<主题名>.pdf` | 翻页无空白页 |
| ④ zip 打包 | `zip -rX ~/Downloads/<主题名>-图集.zip output/`；Skill 本体同理 | 解压抽查 |

---

## Compact 模式速查表

| 步骤 | 必经决策点 | Compact 话术 |
|---|---|---|
| Step 0 | 四问 | 一条消息四个问题 |
| Step 1 | 底色三档 + 抠图 A/B | "透明底+我帮抠，OK？" |
| Step 1.5 | 图集规模 20/45 | "没图集，生成 20 精简还是 45 完整？" |
| Step 2b | tokens 拍板 | 直接给 B 模式草稿，"OK 就往下" |
| Step 2.5 | 头像校准 | 出裁剪放大图，"居中了吗？" |
| Step 3 | 闸门三项 | 一行勾选清单 |
| Step 7 | 验收 | 触发词 + 测试主题一句话 |
| Step 7 | 导出菜单 | "①2K已有 ②3x ③PDF ④zip，勾哪个？都进下载文件夹" |
