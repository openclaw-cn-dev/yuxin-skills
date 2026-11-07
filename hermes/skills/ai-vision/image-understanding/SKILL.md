---
name: image-understanding
version: 1.0.0
description: 图片理解与解析系统 - OCR文字提取、内容识别、标签生成、场景描述、人脸检测
tags: [ai, vision, ocr, image-recognition, image-captioning, analysis]
author: Hermes Agent
---

# 图片理解与解析系统 (Image Understanding)

让 AI 看懂图片内容、提取文字、识别物体、生成描述。

## 触发条件

- "这张图里有什么"、"帮我看看这张图"
- "提取图片里的文字"、"OCR"
- "给这张图打标签"
- "描述一下这张图片"
- "图里有人吗"、"人脸检测"
- "这张图是什么风格"
- "识别图中的二维码"

---

## 🔍 核心能力

### ✅ 文字提取 (OCR)
- 中英文印刷体识别
- 手写体识别
- 表格识别
- 竖排文字识别
- 支持倾斜、模糊图片

### ✅ 图像内容识别
- 物体检测（人、车、动物、物品...）
- 场景分类（室内、户外、办公室、街道...）
- 自动打标签
- NSFW 内容检测

### ✅ 图像描述
- 一句话概括图片内容
- 详细描述生成
- 中文/英文双语

### ✅ 高级分析
- 人脸检测 + 属性（年龄、性别、情绪）
- 色彩分析（主色调、配色方案）
- 图片质量评估（清晰度、噪点、曝光）
- 二维码/条形码识别

---

## 🚀 快速使用

### 命令行工具

```bash
# 完整分析（OCR + 标签 + 描述）
python image_analyzer.py analyze photo.jpg

# 只提取文字
python image_analyzer.py ocr screenshot.png

# 生成标签
python image_analyzer.py tags photo.jpg --num 10

# 生成图片描述
python image_analyzer.py describe photo.jpg

# 人脸检测
python image_analyzer.py faces group_photo.jpg

# 批量分析文件夹
python image_analyzer.py batch ./photos --output analysis.csv
```

### Python API

```python
from image_analyzer import ImageAnalyzer

analyzer = ImageAnalyzer()

# 完整分析
result = analyzer.analyze("photo.jpg")

print(f"📝 描述: {result.caption}")
print(f"🏷️ 标签: {', '.join(result.tags)}")
print(f"📖 文字: {result.text}")
print(f"👤 人脸: {len(result.faces)} 张")
print(f"🎨 主色: {result.main_colors}")
```

---

## 📝 OCR 文字提取

### 基础用法

```python
text = analyzer.extract_text("screenshot.png")
print(text)
```

### 高级选项

```python
result = analyzer.extract_text("menu.jpg", 
    detail=True,        # 返回位置信息
    lang="ch_sim",      # 中文简体
    table=True          # 尝试识别表格
)

# 带坐标的文字块
for block in result.blocks:
    print(f"[{block.x}, {block.y}] {block.text} (置信度: {block.confidence})")
```

### 支持的语言

| 语言代码 | 说明 |
|---------|------|
| `ch_sim` | 中文简体 |
| `ch_tra` | 中文繁体 |
| `en` | 英文 |
| `ja` | 日文 |
| `ko` | 韩文 |

---

## 🏷️ 图像标签生成

```python
# 生成 5 个标签
tags = analyzer.generate_tags("cat.jpg", num_tags=5)
print(tags)
# ['cat', 'animal', 'pet', 'orange', 'sitting']

# 带置信度
for tag, score in tags_with_scores:
    print(f"{tag}: {score:.2f}")

# 中文标签
tags = analyzer.generate_tags("cat.jpg", lang="zh")
# ['猫', '动物', '宠物', '橘猫', '坐着']
```

---

## 📖 图片描述生成

```python
# 一句话描述
caption = analyzer.generate_caption("wedding.jpg")
# "一对新婚夫妇在教堂里举行婚礼"

# 详细描述
description = analyzer.generate_caption("wedding.jpg", detailed=True)
"""
这是一张婚礼照片。画面中心是一对新婚夫妇，新郎穿着黑色西装，
新娘穿着白色婚纱。他们站在教堂的祭坛前，背景是彩色玻璃窗。
新娘手捧花束，两人正在交换戒指。光线柔和，气氛温馨浪漫。
"""

# 中英文双语
caption_en = analyzer.generate_caption("wedding.jpg", lang="en")
```

---

## 👤 人脸检测与分析

```python
faces = analyzer.detect_faces("group_photo.jpg")

print(f"检测到 {len(faces)} 张人脸")

for face in faces:
    print(f"""
位置: ({face.x}, {face.y}) 尺寸: {face.width}x{face.height}
年龄估计: {face.age} 岁
性别: {face.gender}
情绪: {face.emotion}
置信度: {face.confidence:.1%}
""")
```

### 人脸属性识别

| 属性 | 说明 |
|------|------|
| `age` | 年龄估计（误差约 ±5 岁） |
| `gender` | 性别（男/女） |
| `emotion` | 情绪（开心/中性/难过/惊讶/生气） |
| `landmarks` | 68 个特征点坐标 |

---

## 🎨 色彩分析

```python
colors = analyzer.analyze_colors("painting.jpg", num_colors=5)

print("图片主色调:")
for color in colors:
    print(f"  RGB({color.r}, {color.g}, {color.b}) - {color.percentage:.1%}")

# 生成配色方案文案
palette = analyzer.get_color_palette("brand_logo.jpg")
print(f"建议配色: {palette.hex_codes}")
```

输出示例：
```
图片主色调:
  RGB(45, 90, 160)  - 32.5% (深蓝)
  RGB(200, 180, 120) - 25.1% (金色)
  RGB(240, 240, 235) - 18.3% (米白)
  RGB(80, 80, 80)    - 14.7% (深灰)
  RGB(180, 60, 50)   - 9.4%  (暗红)
```

---

## 📊 图片质量评估

```python
quality = analyzer.assess_quality("blurry_photo.jpg")

print(f"""
清晰度评分: {quality.sharpness}/100
噪点水平: {quality.noise}/100
曝光正常: {'✅' if quality.exposure == 'normal' else '⚠️'}
是否模糊: {'❌ 模糊' if quality.is_blurry else '✅ 清晰'}
整体评分: {quality.overall}/100
""")
```

---

## 🔲 二维码 / 条形码识别

```python
codes = detector.scan_qr("product_package.jpg")

for code in codes:
    print(f"""
类型: {code.type} (QR_CODE / BARCODE)
内容: {code.data}
位置: ({code.x}, {code.y})
""")
```

---

## 📦 批量分析工作流

```python
# 批量分析整个文件夹
analyzer.batch_analyze(
    input_dir="./photos",
    output_file="analysis.csv",
    tasks=["ocr", "tags", "caption", "faces"],
    num_workers=4  # 多进程加速
)
```

**CSV 输出字段:**

| 字段 | 说明 |
|------|------|
| `filename` | 文件名 |
| `caption` | 图片描述 |
| `tags` | 标签（逗号分隔） |
| `ocr_text` | OCR 提取的文字 |
| `num_faces` | 人脸数量 |
| `main_colors` | 主色调（RGB） |
| `width`, `height` | 图片尺寸 |
| `file_size` | 文件大小 |

---

## 🔧 后端引擎选择

系统支持多种识别后端，可按需切换：

| 后端 | 优点 | 缺点 | 适用场景 |
|------|------|------|---------|
| **EasyOCR** | 免费、本地运行、中文好 | 需下载模型、速度一般 | 离线使用、隐私敏感 |
| **豆包视觉 API** | 准确率高、速度快 | 需要联网、收费 | 批量处理、高质量要求 |
| **PaddleOCR** | 百度开源、表格识别强 | 安装复杂 | 企业级需求 |

```python
# 选择后端
analyzer = ImageAnalyzer(backend="easyocr")  # 本地免费
analyzer = ImageAnalyzer(backend="doubao")   # 豆包 API
```

---

## 💡 使用场景

### 场景 1: 截图文字提取

```bash
# 提取微信截图里的文字
python image_analyzer.py ocr wechat_screenshot.png | pbcopy
```

### 场景 2: 照片管理打标签

```bash
# 批量给相册打标签，生成可搜索的索引
python image_analyzer.py batch ./vacation_photos --output photo_index.csv
```

### 场景 3: 老照片整理

```bash
# 检测老照片中的人脸，标注人物
python image_analyzer.py faces ./old_photos --output faces.json
```

### 场景 4: 文档数字化

```bash
# 识别手写笔记并转为文本
python image_analyzer.py ocr handwritten_note.jpg --lang ch_sim --detail
```

### 场景 5: 内容审核

```bash
# 检测 NSFW 内容
result = analyzer.detect_nsfw("image.jpg")
if result.is_nsfw:
    print(f"⚠️ 检测到敏感内容: {result.category} ({result.score:.1%})")
```

---

## ⚡ 性能优化

### 批量处理加速

```python
# 启用 GPU（如果有）
analyzer.use_gpu = True

# 多进程处理
analyzer.batch_analyze("./dataset", num_workers=8)
```

### 内存优化

```python
# 小图模式（加快处理速度）
analyzer.set_max_image_size(1024)  # 超过 1024px 先缩小再处理
```

---

## 📦 安装依赖

```bash
# 基础 OCR（推荐，中文好）
pip install easyocr

# 图像处理
pip install pillow numpy opencv-python

# 二维码识别
pip install pyzbar

# 豆包视觉 API（可选，更高准确率）
pip install volcengine
```

---

## 🔍 命令速查表

```bash
# 完整分析
python image_analyzer.py analyze photo.jpg

# 提取文字
python image_analyzer.py ocr screenshot.png

# 生成标签
python image_analyzer.py tags photo.jpg --num 10

# 生成描述
python image_analyzer.py describe photo.jpg

# 人脸检测
python image_analyzer.py faces group.jpg

# 色彩分析
python image_analyzer.py colors logo.jpg

# 扫描二维码
python image_analyzer.py qr product.jpg

# 质量评估
python image_analyzer.py quality blurry.jpg

# 批量分析
python image_analyzer.py batch ./photos --output result.csv
```

---

## ⚠️ 已知问题与解决方案

### ❌ OCR 模型下载失败（中国防火墙问题）

**Problem:** EasyOCR 首次运行时会从 GitHub 下载约 100MB 的模型文件，在中国大陆可能因防火墙导致下载失败：
```
http.client.RemoteDisconnected: Remote end closed connection without response
```

**解决方案：**

1. **领域知识回退** - 对于 AI 知识卡片项目，直接使用已知的 T 编号映射表（见 `batch-file-renaming` 技能），无需 OCR 即可重命名。

2. **手动下载模型** - 从国内镜像下载模型文件到 `~/.EasyOCR/model/` 目录。

3. **切换引擎** - 使用其他 OCR 引擎：
   - PaddleOCR（百度开源，国内访问好）
   - Tesseract（需 `brew install tesseract`）
   - 火山引擎豆包视觉 API（在线）

4. **本地预加载** - 在网络好的环境先运行一次下载模型，之后可离线使用。

### 提高 OCR 准确率

1. ✅ **图片预处理**：先裁剪到文字区域
2. ✅ **提高分辨率**：低于 300 DPI 的文字识别率下降
3. ✅ **校正倾斜**：倾斜超过 15 度会严重影响识别
4. ✅ **去除背景**：纯色背景比复杂背景识别率高 30%

```python
# 自动预处理
result = analyzer.ocr("blurry_text.jpg", preprocess=True)
```

### 标签生成调优

```python
# 通用标签（默认）
analyzer.generate_tags(img, style="general")

# 艺术风格标签（绘画、摄影）
analyzer.generate_tags(img, style="art")

# 电商产品标签
analyzer.generate_tags(img, style="ecommerce")
```