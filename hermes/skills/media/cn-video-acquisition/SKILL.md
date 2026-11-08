---
name: cn-video-acquisition
description: 国内平台视频采集与调研（YouTube 不可用环境）— B 站批量搜索下载（yt-dlp bilisearch，MP4）+ 抖音 feed 自动采集调研（无头浏览器拦截 API 免登录 → 下载 → whisper 口播转写 + 关键帧多模态分析 → 调研笔记）。触发条件：要批量下载 B 站视频/MV/卡拉OK、要在抖音找视频做调研/竞品分析/内容参考、维护 33-抖音自动调研 项目。
---

# 国内平台视频采集与调研（类级）

YouTube 不可用的国内网络环境下，从 B 站 / 抖音获取视频素材的两条链路。2026-09-02 curator 合并：原 2 个独立 skill 整档收纳于 `references/`。

## 链路路由

| 场景 | 读什么 | 要点 |
|---|---|---|
| B 站批量下载 | `references/bilibili-video-download/` | yt-dlp `bilisearch` 批量搜索 + 下载 MP4；适合 MV / 卡拉OK / 教程批量采集；含 scripts/ |
| 抖音调研采集 | `references/douyin-video-research/` | 无头浏览器刷 feed 拦截 API 免登录拿视频 → 下载 → whisper 口播转写 + 关键帧拼图多模态分析 → 调研笔记素材 |

## 使用纪律

- 只要下载素材走 B 站链路；要"内容理解/竞品分析"走抖音链路（转写+关键帧是它的增量价值）。
- 批量任务注意磁盘占用（配合磁盘清理 skill 的分级审批纪律），下载完成即归档，不留临时双份。