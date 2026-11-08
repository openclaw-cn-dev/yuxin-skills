---
name: advanced-image-workflow
version: 1.0.0
description: 进阶图像工作流 - 批量处理、AI 图片分析、风格迁移、图片增强、数据集构建
tags: [ai, vision, image-processing, batch, workflow, upscale]
author: Hermes Agent
---

# 进阶图像工作流 (Advanced Image Workflow)

针对大量图片的自动化处理、AI 增强、分析和管理的完整工作流。

## 触发条件

- "批量处理图片"、"批量压缩"
- "修复老照片"、"图片增强"
- "给图片打标签"、"图片分类"
- "生成图片缩略图"
- "构建图片数据集"
- "风格迁移"、"把这张图变成 XX 风格"
- "去除图片背景"

---

## 🛠️ 核心能力

### ✅ 批量处理
- 批量缩放 / 裁剪 / 格式转换
- 批量压缩（优化网站加载速度）
- 批量重命名（按日期/尺寸/MD5）
- 批量加水印

### ✅ AI 图像增强
- 超分辨率放大（2x/4x/8x）
- 老照片修复（去划痕、上色）
- 去模糊 / 去噪
- 人像美颜
- HDR 效果

### ✅ 智能分析
- 自动打标签（图像识别）
- NSFW 内容检测
- 色彩分析（主色、配色方案）
- 相似度检测（去重）
- OCR 文字提取

### ✅ 特殊效果
- AI 背景移除
- 风格迁移（参考图风格）
- 图片变线稿
- 色彩迁移

---

## 📦 批量处理工作流

### 场景 1: 网站图片优化

```bash
# 批量压缩 JPG 到 WebP（质量 80）
python image_workflow.py compress --input ./photos --output ./optimized --format webp --quality 80

# 生成响应式图片尺寸集（320w, 640w, 1280w）
python image_workflow.py responsive --input ./hero.jpg --sizes 320,640,1280
```

### 场景 2: 批量重命名 + 分类

```bash
# 按拍摄日期重命名: 2024-07-13_143025.jpg
python image_workflow.py rename --input ./photos --pattern date

# 按 MD5 去重
python image_workflow.py dedup --input ./photos --move-to ./duplicates
```

### 场景 3: 批量加水印

```bash
python image_workflow.py watermark \
  --input ./products \
  --output ./watermarked \
  --text "我的品牌" \
  --position bottom-right \
  --opacity 0.3
```

---

## 🚀 AI 图像增强

### 超分辨率放大

```python
from image_enhancer import ImageEnhancer

enhancer = ImageEnhancer()

# 4 倍放大
result = enhancer.upscale("photo.jpg", scale=4)
result.save("photo_4x.png")

# 批量放大
enhancer.batch_upscale("./photos", scale=2, output="./upscaled")
```

### 老照片修复

```python
# 老照片三件套：去划痕 + 上色 + 增强
result = enhancer
  .open("old_photo.jpg")
  .remove_scratches()
  .colorize()
  .enhance()
  .save("old_photo_restored.png")
```

### 背景移除

```python
# 一键抠图
result = enhancer.remove_background("person.jpg")
result.save("person_no_bg.png")  # 透明背景 PNG
```

---

## 🔍 智能图片分析

### 自动打标签

```python
from image_analyzer import ImageAnalyzer

analyzer = ImageAnalyzer()

# 单张分析
result = analyzer.analyze("cat.jpg")
print(result.tags)       # ['cat', 'animal', 'pet', 'orange', 'sitting']
print(result.colors)     # 主色调: [(200, 150, 50), ...]
print(result.nsfw_score) # 0.0-1.0

# 批量分析并生成 CSV
analyzer.batch_analyze("./dataset", output="tags.csv")
```

### 图片去重

```python
# 找出相似图片并移动到重复文件夹
duplicates = analyzer.find_duplicates("./photos", threshold=0.95)
for group in duplicates:
    print(f"相似组 ({len(group)}张):")
    for path in group:
        print(f"  {path}")
```

### OCR 文字提取

```python
text = analyzer.extract_text("screenshot.png")
print(text)

# 批量提取并保存为文本文件
analyzer.batch_ocr("./screenshots", output="./texts")
```

---

## 🎨 风格迁移与特效

### 图片风格化

```python
from style_transfer import StyleTransfer

st = StyleTransfer()

# 把照片变成梵高星空风格
result = st.transfer(
    content="my_photo.jpg",
    style="vangogh_starry_night.jpg",
    strength=0.8
)
result.save("artistic.jpg")
```

### 内置风格预设

| 预设 | 说明 |
|------|------|
| `anime` | 动漫化（新海诚风格） |
| `oil` | 油画效果 |
| `sketch` | 素描 / 线稿 |
| `watercolor` | 水彩画 |
| `cyberpunk` | 赛博朋克调色 |
| `film` | 电影胶片色调 |

```python
result = st.apply_preset("my_photo.jpg", "anime")
```

### 色彩迁移

```python
# 把 A 图的配色应用到 B 图上
result = st.transfer_colors(
    source="warm_sunset.jpg",
    target="cold_mountain.jpg"
)
result.save("warm_mountain.jpg")
```

---

## 📊 数据集构建工具

### 构建 AI 训练数据集

```python
from dataset_builder import DatasetBuilder

builder = DatasetBuilder("./raw_images")

# 自动清洗数据集
builder.clean(
  min_size=512,              # 最小尺寸
  remove_duplicates=True,     # 去重
  remove_blurry=True,         # 移除模糊图
  filter_nsfw=True           # 过滤 NSFW
)

# 自动划分训练/验证/测试集
builder.split(
  train_ratio=0.8,
  val_ratio=0.1,
  test_ratio=0.1,
  stratified=True  # 按类别平衡划分
)

# 数据增强（扩充训练集）
builder.augment(
  output="./dataset/train",
  rotations=[-15, 0, 15],
  flips=["horizontal"],
  brightness=[0.8, 1.0, 1.2],
  num_workers=4
)
```

### 自动标注

```python
# 用 CLIP 自动打标签
builder.auto_label(output="labels.csv")

# 导出为 COCO / YOLO 格式
builder.export_coco("dataset.json")
builder.export_yolo("./yolo_labels")
```

---

## ⚡ 性能优化指南

### 批量处理加速

```python
# 使用多进程加速（默认 CPU 核心数）
builder.batch_process(images, num_workers=8)

# 处理 10000 张图时显示进度条
builder.set_progress_bar(True)
```

### 内存优化

```python
# 流式处理，不一次性加载所有图片
builder.streaming = True
builder.batch_size = 32  # 每批处理数量
```

---

## 📋 常用命令速查

```bash
# === 批量处理 ===
dimage compress ./input ./output           # 压缩优化
dimage resize ./input 1920x1080           # 统一尺寸
dimage rename ./input --pattern date      # 按日期重命名
dimage dedup ./input                      # 去重

# === AI 增强 ===
dimage upscale photo.jpg 4x               # 4倍超分
dimage colorize old_bw.jpg                # 黑白上色
dimage remove-bg person.jpg               # 抠图

# === 分析 ===
dimage analyze ./photos                   # 批量分析打标签
dimage ocr ./screenshots                  # 提取文字
dimage duplicates ./photos                # 找重复图片

# === 特效 ===
dimage style photo.jpg --preset anime     # 动漫化
dimage palette photo.jpg                  # 提取配色方案
```

---

## 🔧 安装依赖

```bash
# 基础依赖（必需）
pip install pillow numpy tqdm python-dotenv

# AI 增强（可选，用于超分、抠图等）
pip install opencv-python torch torchvision
pip install rembg  # 背景移除

# 图像分析（可选）
pip install transformers  # CLIP 打标签
pip install easyocr       # OCR 文字识别
pip install scikit-learn  # 相似度计算
```

---

## 最佳实践

### 网站图片优化方案

| 图片类型 | 推荐格式 | 推荐尺寸 | 质量参数 |
|---------|---------|---------|---------|
| Hero 大图 | WebP | 1920px 宽 | 质量 80 |
| 产品图 | WebP / JPG | 1024px 宽 | 质量 85 |
| 缩略图 | WebP | 320px 宽 | 质量 70 |
| PNG 图标 | PNG / WebP | 原尺寸 | 无损 |

### 打印级图片

```bash
# 300 DPI，适合 A4 打印
dimage upscale photo.jpg 4x --output print_ready.tif
```

### 社交媒体优化

```bash
# Instagram 正方形 1080x1080
dimage resize input.jpg 1080x1080 --output instagram.jpg

# Twitter 头图 1500x500
dimage resize header.jpg 1500x500 --crop center
```

## 语音交互系统方法论（curator 合并 2026-10-16 · 原 voice-interaction-system 整档收纳）

完整 4 阶段渐进式语音交互系统实现方法论已合并至 `references/voice-interaction-system/`（原独立 skill，v0.13.0+：火山引擎 ASR + TTS、Whisper fallback、SileroVAD、声纹锁、打断机制、多轮上下文、macOS TCC 麦克风权限、sounddevice；2026-10-16 从 Codex 同步仓完整恢复 23 个文件，为最新版）。当任务涉及「让 Hermes 能听到/念出来」、ASR/TTS 集成、语音唤醒/语音对话 pipeline 时，先读 `references/voice-interaction-system/SKILL.md`，本 skill 自身只覆盖图像/图片工作流（批量处理、AI 图片分析、风格迁移、增强、数据集构建）与豆包生图。