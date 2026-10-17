---
name: doubao-image-gen
version: 1.0.0
description: 豆包生图 - 通过火山引擎豆包 API 生成高质量 AI 图像的完整工作流。支持文生图、图生图、批量生成、图像处理。
tags: [ai, vision, image-generation, doubao, 豆包, 生图]
author: Hermes Agent
---

# 豆包生图 (Doubao Image Generation)

通过火山引擎豆包 API 生成高质量 AI 图像的完整工作流。

## 触发条件

- "生成图片"、"生图"、"AI 画图"
- "豆包画图"、"豆包生图"
- "根据这段文字画图"
- "批量生成图片"
- "图生图"、"以图生图"

## 能力范围

✅ **文生图** — 文字描述生成图片
✅ **图生图** — 基于参考图生成变体
✅ **批量生图** — 一次生成多张不同风格
✅ **提示词优化** — 自动优化中文提示词
✅ **图像处理** — 缩放、裁剪、滤镜、拼接

## API 配置

**API 端点**: `https://ark.cn-beijing.volces.com/api/v3/images/generations`
**模型**: `doubao-seedream-5-0-260128`（ImageGeneration，实测已激活可用）
**⚠️ 实测关键参数（2026-08-13 laomo 验证）**:
- 尺寸必须 ≥ 3686400 像素（最小 `2048x2048`），否则返回 400 `image size must be at least 3686400 pixels`
- 鉴权 key 用 `VOLC_ARK_API_KEY`（与 config.yaml `minimax-custom` 同款 ark-d8e74c14-...），**不需要** endpoint_id
- 图生图(i2i) 传 `"image": ["data:image/jpeg;base64,..."]`，可用于老照片修复/上色
- 备选模型（需在 Ark 控制台单独激活）：`***SECRET***`、`doubao-seedream-4-0-20260415`

### 环境变量配置

```bash
# 火山引擎 Ark API Key（已配置于 ~/.hermes/config.yaml）
export VOLC_ARK_API_KEY="ark-..."
```

### 快速开始

```python
from doubao_image import DoubaoImageGen

gen = DoubaoImageGen(api_key="your-key")

# 文生图
result = gen.generate(
    prompt="一只可爱的柯基犬坐在草地上",
    size="1024x1024",
    n=1,
    style="写实"
)

# 保存图片
result.save("corgi.png")
```

## 支持的参数

| 参数 | 可选值 | 默认 | 说明 |
|------|--------|------|------|
| `size` | `512x512`, `1024x1024`, `1024x768`, `768x1024` | `1024x1024` | 图片尺寸 |
| `n` | 1-4 | 1 | 生成数量 |
| `style` | `写实`, `动漫`, `插画`, `水彩`, `油画`, `3D`, `像素`, `赛博朋克`, `国潮` | `写实` | 风格预设 |
| `quality` | `standard`, `hd` | `standard` | 质量 |

## 提示词工程最佳实践

### 黄金公式

```
[主体] + [环境] + [光线] + [视角] + [风格] + [画质]
```

**示例**:
```
一只金毛犬在秋天的公园里奔跑，下午阳光透过树叶洒下，
侧逆光，低角度拍摄，温暖色调，电影质感，8K超高清
```

### 风格关键词库

| 风格 | 关键词 |
|------|--------|
| **摄影** | 8K, RAW照片, 电影质感, 景深, 虚化背景, 徕卡色调 |
| **动漫** | 新海诚风格, 吉卜力, 赛璐璐, 二次元, 插画 |
| **艺术** | 梵高风格, 莫奈印象派, 浮世绘, 水墨画, 国潮 |
| **3D** | Pixar风格, 3D渲染, OC渲染, 体积光 |

## 批量生图工作流

```python
prompts = [
    "春天的樱花大道",
    "夏天的海边日落",
    "秋天的枫叶山林",
    "冬天的雪景小屋"
]

results = gen.generate_batch(prompts, size="1024x768")
for i, r in enumerate(results):
    r.save(f"season_{i}.png")
```

## 图生图

```python
result = gen.image_to_image(
    image_path="reference.png",
    prompt="把这张图改成赛博朋克风格",
    strength=0.7  # 0.0-1.0，越大约偏离原图
)
```

## 图像处理工具

```python
from image_utils import ImageEditor

editor = ImageEditor("input.png")

# 缩放
editor.resize(1920, 1080)

# 裁剪
editor.crop(100, 100, 500, 500)

# 滤镜
editor.filter("grayscale")  # 灰度
editor.filter("sepia")      # 复古
editor.filter("blur")       # 模糊

# 添加文字
editor.add_text("Hello", x=50, y=50, font_size=32, color="#fff")

# 拼接图片
editor.grid(["a.png", "b.png", "c.png", "d.png"], cols=2)

editor.save("output.png")
```

## 常见问题

**Q: 生成的图片不符合预期？**
- 提示词增加更多细节（光线、视角、材质）
- 使用 `style` 参数锁定风格
- 降低 `n` 提高单张质量

**Q: API 调用失败？**
- 检查网络连接（国内不需要代理）
- 确认 API Key 有效且有额度
- 验证图片尺寸是否在支持列表内

**Q: 如何生成商用级图片？**
- 使用 `quality="hd"`
- 提示词增加："商业摄影, 专业灯光, 高对比度"
- 后期增加锐化和色彩校正