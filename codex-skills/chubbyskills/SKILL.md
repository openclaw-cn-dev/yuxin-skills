---
name: chubbyskills
description: 中文全渠道内容采集知识库 14 件套 — 抖音/B站/小红书/公众号/微博/知乎/X/播客采集转录入库 Markdown 索引检索。entrypoint: chubbyskills（router 根入口，14 子 skill 在子目录，工具链 tools/chubby.py）
---

# Chubby Skills — 中文全渠道内容采集知识库

14 个分体式 skill + 共享 CLI 工具链，把抖音/B站/小红书/公众号/微博/知乎/X/播客的**视频/文章/图文采集为 Markdown 存进本地知识库**，可搜索、可回查来源、可导出资料包交给 Agent。核心链路 Python 标准库**零依赖**。

## 老大 4 业务线映射

| 业务线 | 用哪些 skill |
|---|---|
| **水产养殖自媒体** | douyin-transcribe + bilibili-transcribe（同行视频→文字拆解）/ industry-intelligence-radar（订阅跟踪行业源） |
| **水产美食内容** | xiaohongshu-ingest + wechat-article-ingest（竞品美食图文采集对标） |
| **设备/选股/求职** | weibo-transcribe + x-ingest（舆情+资讯源） |
| **通用知识库** | knowledge-base-management + vault_index 检索 / learning-notes-automation |

## 14 子 skill 索引

| 目录 | 能力 | 依赖 |
|---|---|---|
| douyin-transcribe | 抖音视频→转录→Markdown | funasr 重依赖（缓装） |
| bilibili-transcribe / youtube-transcribe | B站/YouTube 字幕优先 | 仅 yt-dlp |
| tiktok/weibo/zhihu-transcribe | 转录 | funasr 重依赖（缓装） |
| xiaohongshu-ingest | 小红书图文正文 | 零依赖 |
| wechat-article-ingest | 公众号 HTML/PDF→MD | beautifulsoup4（轻） |
| x-ingest | X 推文正文 | 零依赖 |
| podcast-transcribe | 播客 SenseVoice | funasr 重依赖（缓装） |
| industry-intelligence-radar | RSS/Feed 订阅跟踪 | 标准库 |
| knowledge-base-management | 知识库管理+索引 | 标准库 |
| learning-notes-automation | 学习笔记自动化 | 标准库 |
| content-enrich | 内容富化 | — |

**转录系（funasr+torch ≥3GB）按缓装口径**：skill 已装可用文档，重依赖执行环境未装，用转录系前先 pip 装 funasr。B站/YouTube/小红书/X/公众号链路**开箱即用**。

## 快速开始（零依赖链路）

```bash
cd ~/.codex/skills/chubbyskills
# ⚠️ 双坑（1111 实测）：① 必须 -m 形式跑，直跑 tools/chubby.py 撞 Hermes 的 tools 包 ImportError
# ② 采集子进程也 import tools，必须前置 PYTHONPATH（MSYS 下必须 cygpath 转 Windows 路径，裸 $PWD 是 /c/... Windows Python 不认）
export PYTHONPATH="$(cygpath -w "$PWD")"
python -m tools.chubby init --vault <知识库目录>
python -m tools.chubby ingest "https://x.com/..." --no-enrich   # X 推文
python -m tools.chubby ingest "https://xiaohongshu.com/..."     # 小红书图文
python -m tools.chubby search "关键词"
python -m tools.chubby quickstart   # 离线验收流（1111 实测 6/6 全过）
```

## 平台状态（README 实测口径）

- B站/YouTube：稳定（字幕优先仅 yt-dlp）
- 公众号：测试（HTML 需 bs4，PDF 兜底）
- 抖音/TikTok/微博/知乎：测试·重依赖（funasr+ffmpeg）
- X/小红书：手动兜底（零依赖正文）
- 本地文档：稳定（零依赖）

## 依赖

Python 3.11+，核心链路标准库零依赖。转录系 funasr+torch 缓装。MIT License，v0.15.0。