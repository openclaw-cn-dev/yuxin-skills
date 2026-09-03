---
name: douyin-content-extraction
description: Extract the spoken or written content of a 抖音 (Douyin / TikTok-China) video — title, caption, on-screen text, mentioned tools/repos/links — when 老大 pastes a 抖音 share link or asks "把视频里的 X 找出来". 抖音 网页版无法直接 parse（反爬 + 动态 X-Bogus 签名 + 未登录只能看 React shell），所以走 4 条 fallback：老大直接 paste 文字、OCR 截图、yt-dlp/抖音 解析站下载、第三方 API。Triggers on "抖音视频内容", "douyin 提取", "抖音 链接", "v.douyin.com", "抖音视频找", "算力炼丹炉", "抖音 抄 skills", "抖音 文案提取".
---

# 抖音视频内容提取

## 🛑 核心限制（2026-06-07 实测）

**小弟的 `browser_navigate` 打开 `v.douyin.com/xxx` 会跳到 `douyin.com/video/{id}`，但拿不到视频内容**：

1. 页面渲染出来是 **React shell** + "视频数据加载中"
2. 视频播放器是 `<video>` 但 `src` 为空（动态 X-Bogus / \_signature 签名）
3. `document.body.innerText` 只返回页面**框架文字**（登录按钮、底部链接、推荐视频标题）
4. **不登录**连真实视频都看不到
5. 小弟的 browser 没有老大的抖音 cookie

**结论**：**直接爬抖音网页 = 死路**。必须走 fallback。

## ✅ 4 条 Fallback（按老大配合成本从低到高）

### Fallback 1：老大 paste 文字（**最快 1 分钟**）

**让老大发**：
- 视频简介（抖音点视频 → 下方"展开"→ 复制）
- 评论区里有人总结的内容
- 老大看完后凭记忆讲几个关键点

**小弟拿到文字** → 直接干活（找 repo、装 skill、写文案）。

### Fallback 2：老大截图 + 小弟 OCR（**2-3 分钟**）

**操作**：
1. 老大在抖音 App 暂停视频
2. 截屏提到 skill 名字、链接、命令的那几帧
3. 发图片给小弟（拖进 Feishu / 微信 DM）
4. 小弟用 `vision_analyze` 读图

**优点**：保留视觉信息（用户名、评论数、关键帧）。
**缺点**：依赖老大手动截。

### Fallback 3：yt-dlp / 第三方解析站下载（**5-10 分钟**）

**工具链**：
```bash
# yt-dlp（最稳，但要最新版）
yt-dlp --cookies-from-browser chrome "https://v.douyin.com/xxx/" -o video.mp4

# 或第三方解析站（不一定稳）
# https://douyin.wtf/
# https://v.douyin-parse.com/
# 复制视频链接 → 解析 → 下载 mp4 → 提取字幕

# 提取音频 → Whisper 转文字
ffmpeg -i video.mp4 -vn -acodec pcm_s16le audio.wav
whisper audio.wav --language zh --model medium
```

**优点**：全自动，不需要老大。
**缺点**：
- yt-dlp 经常被抖音反爬更新打断
- 解析站域名/接口每周失效
- Whisper 中文 ASR 准确率 ~85-95%，专有名词（skill 名 / GitHub repo）容易错

### Fallback 4：第三方 API（**贵但稳**）

- **飞书剪藏**：抖音 → 复制链接 → 飞书剪藏机器人 → 自动转文字（要老大有飞书剪藏权限）
- **Coze / 字节扣子工作流**：上传视频 → 自动提取文案（要注册 + 配工作流）
- **第三方 API**：apitry.com / json-parse 之类的抖音解析服务（按次收费）

### Fallback 5：老大发**关键字** → 小弟 GitHub 反查（**最快路径**）

**症状**：老大只记得视频里讲了一个名字（如 "dbskills"），没给完整 repo / 作者。

**操作**（**实测有效 2026-06-07**）：
```bash
# 老大小弟说了 "dbskills" 3 个字
curl -s "https://api.github.com/search/repositories?q=dbskills" \
  | python -c "import json,sys; d=json.load(sys.stdin); \
      [print(i['full_name'], '|', i.get('stargazers_count',0), '*', i.get('description','')[:80]) \
       for i in d.get('items',[])[:5]]"
# → 输出候选 2-5 个 repo，给老大 A/B/C 选
```

**搜索词变体表**（老大可能说的"半截"关键字）：

| 老大说 | GitHub 搜 |
|---|---|
| "dbskills" / "数据库 skill" | `dbskills`、`db-skills+ai`、`dbskills+database` |
| "gstack" / "g 站" | `gstack+skill`、`gstack+openclaw` |
| "gbrain" / "g 脑" | `gbrain+agent`、`gbrain+second-brain` |
| "awesome X" | `awesome-hermes-agent`、`awesome-claude-skills` |
| "self-evolution" / "自进化" | `hermes-agent-self-evolution`（NousResearch 官方） |
| "文案诊断" / "copy audit" | `copy-audit+skill`、`copywriting+diagnose+skill` |
| "抖音 skill" | `douyin+skill`、`short-video+agent` |

**优势**：
- 老大配合成本**最低**（1-2 个字就行）
- 小弟**不用看视频**就定位到具体 repo
- **准确率**比 OCR 高（视频里字小/一闪而过容易漏）

**注意**：搜出来 2-5 个候选时，**必须给老大选**（A/B/C），不要自己拍板。**老大记得哪个 = 真的**。

## 🎯 给老大的标准回复模板

当老大发抖音链接但小弟拿不到内容时：

```
# 🛑 抖音视频小弟读不到（反爬严）
# 老大帮 1 件事：
🅰️ 复制视频简介（抖音 → 视频 → 展开 → 复制）
🅱️ 截图关键帧（提到 skill / 链接 / 命令的几张）
🅲️ 老大凭记忆讲几个重点（要装的 skill 名 / GitHub 仓库）
# 老大随便给点信息，小弟就开干。
```

## 🔧 找 skill/工具的 3 个技巧

如果视频里讲的是 **自媒体人宝藏 skills** 这类内容，可以这样配合：

1. **搜索视频标题/简介的关键字**（如"自媒体 skills"）：
   ```bash
   curl -s "https://api.github.com/search/repositories?q=自媒体+skill" | head
   curl -s "https://api.github.com/search/repositories?q=creator+agent+skill" | head
   ```

2. **在 skills.sh / clawhub / hermes hub 搜**：
   ```bash
   hermes skills search douyin
   hermes skills search short-video
   hermes skills search 自媒体
   ```
   （注意：hub 搜索经常超时 → 走 GitHub API 兜底）

3. **看视频作者的其他内容**（如果作者 ID 已知）：
   ```python
   # 用 douyin-user-videos skill
   # 拿到作者主页 → 看所有视频标题 → 找到同主题视频 → 重复提取
   ```

## 📌 反爬技术备忘（**仅供了解，不实际绕过**）

抖音反爬三层：
1. **X-Bogus / \_signature 签名**：每次请求带动态签名，由 JS 生成
2. **设备指纹 + 行为检测**：headless browser 一看就知
3. **登录态校验**：核心 API 必须登录态 cookie

**结论**：自写爬虫**不划算**，第三方工具 / 老大配合 / 第三方 API 才是正道。

## 📁 相关 skill

- **`media/youtube-content`** — YouTube 视频转写（比抖音好做，有官方 transcript）
- **`openclaw-imports/douyin-hot-trend`** — 抖音**热榜数据**（不是单视频内容）
- **`openclaw-imports/douyin-user-videos`** — 抖音博主**视频列表**（不是单视频内容）
- **`openclaw-imports/douyin-kuaishou-expert`** — 抖音/快手**内容创作**（不是提取）

## 📌 实战流程图

```
老大发抖音链接
   ↓
browser_navigate → 拿到 React shell
   ↓
document.body.innerText → 只有框架文字
   ↓
判断：失败
   ↓
给老大 3 个 fallback (A/B/C)
   ↓
老大选 → 拿到文字/截图/视频文件
   ↓
小弟干活（找 skill / 装 / 写文案）
```

## 📁 参考文件

- `references/2026-06-07-douyin-extraction-fail.md` — 2026-06-07 实测失败现场（"算力炼丹炉"两条视频链接的尝试记录），含 `browser_navigate` / `innerText` / `<video>.src` 三种尝试的真实输出。
