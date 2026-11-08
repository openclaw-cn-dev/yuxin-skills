# 2026-06-07: 抖音视频内容提取的实测

## 背景

老大要小弟找"算力炼丹炉"的抖音视频里提到的 skills。发了两条：
- `https://v.douyin.com/UjEEEkba9ww/` — "给每个自媒体人的宝藏 skills！一年涨粉 50 万"
- `https://v.douyin.com/EWbnt-EHcTs/` — 同样主题

## 试过的方法

### 1. browser_navigate → React shell

```python
browser_navigate("https://v.douyin.com/UjEEEkba9ww/")
# → 重定向到 https://www.douyin.com/video/7628186962435771699
# → snapshot: "视频数据加载中"
# → 视频播放器 <video src=""> 空
```

### 2. document.body.innerText

```javascript
document.body.innerText
// → 只返回页面框架文字：
//   "精选 / 推荐 / 搜索 / 关注 / 朋友 / 我的 / 直播 / 放映厅 / 短剧 / 小游戏"
//   "登录" 按钮
//   底部链接："广告投放 / 用户服务协议 / 隐私政策"
//   推荐视频标题（30 个推荐视频的标题）
// → 缺：目标视频的标题/简介/评论
```

### 3. document.querySelector('video').src

```javascript
// 空字符串
// 抖音用动态 X-Bogus / _signature 签名后才填 src
```

## 结论

- 网页版**未登录**只能看视频播放器框架
- **登录态需要 cookie**（小弟的 browser 没有老大的抖音 cookie）
- **反爬三层**：X-Bogus 签名 / 设备指纹 / 登录态校验
- **自写爬虫 = 不划算**（3-7 天工作量 vs 老大 paste 文字 1 分钟）

## 走 Fallback

最后让老大从 A/B/C 三个选项里选：
- A: 复制视频简介
- B: 截图关键帧
- C: 凭记忆讲重点

老大没选（直接发了下一个任务），所以视频内容**这次没拿到**。下次直接进 fallback 流程。

## 推荐流程（**下次直接这样**）

1. 老大发抖音链接 → 立即给 A/B/C 选项（**不尝试 browser_navigate**）
2. 老大选 A → 拿到简介 → 直接干活
3. 老大选 B → 截图 OCR → 干活
4. 老大选 C → 凭记忆补全 → 干活
