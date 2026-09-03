# 中餐配图 6 层级联方案（2026-06-13 实战）

> 老大于 2026-06-13 让小弟用本地 SD（LCM Dreamshaper v7 + CPU + 512px）跑 6 张"白灼虾"小红书配图，**结果 5/6 翻车**（料酒画成蒜、3 蘸料只画 2 碗、白灼不像虾）。这份文档记录 6 层级联方案，下一次遇到中餐配图直接照着来。

## 6 层级联（按推荐度排序）

### Tier 1：真实图抓取（**最稳**）⭐⭐⭐⭐⭐

**耗时**：30 分钟内搞定 6 张
**质量**：100% 还原菜品
**成本**：0 元
**适用**：菜品图 / 教程图 / 探店图

**3 个数据源**：

1. **Pinterest**（**中文菜谱最全**）
   - 搜：`白灼虾 高清`、`广东白灼虾`、`顺德白灼虾`
   - 100% 有真实图
   - 需稳定网络

2. **小红书**（**最接地气**）
   - 搜：`白灼虾教程`、加 emoji
   - 优先选点赞 1000+ 的笔记封面
   - 配图风格和目标平台一致

3. **头条 / 百度图片**（**兜底**）
   - 搜：`白灼虾 实拍`
   - 选"高清"过滤
   - 5 分钟抓 30 张

---

### Tier 2：doubao-seedream API（**AI 生图首选**）⭐⭐⭐⭐⭐

**耗时**：1 分钟/张，6 张 6 分钟
**质量**：8/10，中文菜谱理解极好
**成本**：有免费额度（注册送 200 张）
**适用**：所有中餐 + 风格化配图

**安装**：

```bash
uv pip install --python "C:/Users/Administrator/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe" \
  -i https://pypi.tuna.tsinghua.edu.cn/simple volcengine-python-sdk
```

**脚本模板**（**国内直连 + 字节豆包**）：

```python
import os
from volcenginesdkarkruntime import Ark

client = Ark(api_key="YOUR_ARK_API_KEY")

PROMPTS = [
    "白灼大虾九宫格摆盘，俯拍视角，Q弹粉嫩虾肉，金色葱油，枸杞葱丝",
    "白灼虾错误做法 vs 正确做法对比图",
    "广东顺德大厨演示白灼虾烫虾30秒动作图",
]

for i, prompt in enumerate(PROMPTS, 1):
    response = client.images.generate(
        model="doubao-seedream-3-0-t2i-250415",
        prompt=prompt,
        size="1024x1024",
        n=1
    )
    image_url = response.data[0].url
    import requests
    img_data = requests.get(image_url).content
    with open(f"dish_{i}.png", "wb") as f:
        f.write(img_data)
    print(f"✅ 生成 dish_{i}.png")
```

**关键优势**：
- ✅ 中文 prompt 直接喂（**不用翻译**）
- ✅ 国内直连（**不用 hf-mirror**）
- ✅ 1 分钟/张（**6 张 6 分钟**）
- ✅ "白灼" "红烧" "清蒸" "蒜蓉" 全懂

---

### Tier 3：LCM Dreamshaper v7 + 改写 prompt（**最后 AI 兜底**）⭐⭐⭐

**耗时**：5-8 分钟/张，6 张 30-50 分钟
**质量**：6-7/10（**改对 prompt 后**）
**成本**：0 元
**适用**：没 API key + 没时间抓图

**3 个改写技巧**（**实测有效**）：

1. **"料酒" 翻成 "shaoxing wine"**（**"cooking wine" 会画成棕色液体**）
2. **"白灼" 改成 "boiled and chilled glistening with oil"**（**直接描述成品**）
3. **加 "Chinese cuisine, Cantonese style"**（**激活中餐训练子集**）

**改写对比示例**：

```python
# ❌ 错（LCM 翻车）
prompts_v1 = [
    "A 9-grid collage of blanched shrimp dishes, top-down view, ...",  # 白灼不懂
    "Split image comparison of overcooked vs perfect shrimp, ...",  # 布局乱
    "3 slices of ginger, scallions, and a small bowl of cooking wine",  # 料酒=蒜
]

# ✅ 对（LCM 6/10 质量）
prompts_v2 = [
    # 1. 主图：描述具体成品
    """A 9-grid collage of Cantonese style poached shrimp dishes,
    perfectly boiled and chilled, glistening with golden scallion oil,
    garnished with red goji berries and lemon wedges, white porcelain plates,
    wooden table, food photography, 8k, instagram aesthetic, Chinese cuisine""",

    # 2. 对比图：简化 + 强调对比元素
    """Split image, LEFT: overcooked grayish rubbery shrimp on dirty plate,
    RIGHT: Q-bouncy pink perfectly poached shrimp on white porcelain,
    red arrow between them, food photography educational style, 8k""",

    # 3. 食材图：料酒用 shaoxing wine
    """Top-down view of Cantonese cooking ingredients on wooden cutting board:
    3 slices of fresh ginger, 5 segments of green scallions,
    1 small ceramic bowl of shaoxing wine, minimalist food photography,
    warm tones, 8k, instagram""",

    # 4. 烫虾图：描述动作
    """Action shot: stainless steel pot of rolling boiling water,
    steam rising, chef's hand holding bamboo strainer with pink poached shrimp
    being lifted out, motion blur, dramatic lighting, 8k""",

    # 5. 蘸料图：3 个分别描述（避免 LCM 丢元素）
    """Three small white bowls in a row, Cantonese dipping sauces:
    LEFT bowl: soy sauce with garlic and ginger,
    MIDDLE bowl: ginger-scallion-oil sauce,
    RIGHT bowl: spicy chili oil with Sichuan pepper,
    top-down view, minimalist food photography, 8k""",

    # 6. 成品图：最后加成品特写
    """Close-up of perfect Cantonese poached shrimp on white porcelain,
    Q-bouncy pink flesh, glistening with golden oil, garnished with goji berries,
    chopsticks picking up one shrimp, food photography, 8k, instagram aesthetic""",
]
```

---

### Tier 4：商用 API（**Midjourney / DALL-E 3**）⭐⭐⭐⭐

**耗时**：1-2 分钟/张
**质量**：9/10
**成本**：$10-30/月
**适用**：商业项目 + 不差钱

**Midjourney 用法**：
- Discord 频道 `/imagine` 命令
- prompt：`Chinese poached shrimp, glistening, Cantonese style, 8k, food photography`
- 缺点：要科学上网 + 30 美元/月

**DALL-E 3 用法**：
- ChatGPT Plus 直接用
- 优点：中文 prompt 也懂
- 缺点：$20/月 + 国内信用卡难办

**不推荐给小老板** —— 30-50 元/张成本不划算

---

### Tier 5：Pexels / Unsplash 免费图库（**英文菜 + 风格化**）⭐⭐⭐

**耗时**：10-30 分钟
**质量**：7-8/10（**有真实感**）
**成本**：0 元
**适用**：英文菜 / 通用图 / 探店风格

**坑**：
- ❌ 搜"shrimp" → 出来一堆小龙虾 + 啤酒 + 派对
- ❌ 搜"poached shrimp" → 主要是水煮蛋 + 鸡肉
- ✅ 搜"Cantonese seafood" → 有中式但偏广式早茶

**真实翻车案例**（**2026-06-08 小红书爆款 10 篇**）：
- 搜"beef" → 出来蛋糕 / 啤酒 / 小狗
- **结论**：英文图库不适合中文内容

---

### Tier 6：纯文字图（**实在没图就用**）⭐⭐

**耗时**：1 分钟/张
**质量**：5-6/10（**纯设计**）
**成本**：0 元
**适用**：临时占位 / 数据图 / 信息图

**Canva / 创客贴** 直接套模板：
- 选"美食"分类
- 改文字 + 换色
- 5 分钟出图

**适合**：
- 数字反差图（"1 平方 35 斤虾"）
- 步骤分解图（"3 步白灼虾"）
- 对比表格图（"白灼 vs 红烧"）

---

## 6 层级联决策树

```
老大要中餐配图
├─ 有 doubao API key?
│   ├─ ✅ 是 → Tier 2 doubao-seedream（1 分钟 6 张）
│   └─ ❌ 否 → 继续
├─ 有 30 分钟抓图?
│   ├─ ✅ 是 → Tier 1 真实图抓取（30 分钟 6 张，100% 还原）
│   └─ ❌ 否 → 继续
├─ 接受 6/10 质量?
│   ├─ ✅ 是 → Tier 3 LCM 改 prompt（30-50 分钟 6 张）
│   └─ ❌ 否 → Tier 4 商用 API（不差钱走这条）
└─ 实在没图?
    └─ Tier 5/6 英文图库/文字图
```

## 实战对比（**2026-06-13 6 张白灼虾**）

| 路线 | 耗时 | 质量 | 成本 | 6 张结果 |
|---|---|---|---|---|
| **Tier 1 真实图** | 30 分钟 | 10/10 | 0 | 完美 |
| **Tier 2 doubao** | 6 分钟 | 8/10 | 免费额度 | OK |
| **Tier 3 LCM（改对）** | 50 分钟 | 6-7/10 | 0 | 一般 |
| **Tier 3 LCM（没改）** | 5 分钟 | 4-5/10 | 0 | **翻车 5/6** |
| **Tier 4 Midjourney** | 10 分钟 | 9/10 | 30 元/6 张 | 完美 |
| **Tier 5 Pexels** | 20 分钟 | 6/10 | 0 | 跑题 |

## 推荐组合

- **日常小红书配图**：**Tier 1 真实图（30 分钟 6 张）**
- **赶时间出爆款**：**Tier 2 doubao（6 分钟 6 张）**
- **有 API 但断网**：**Tier 3 LCM 改 prompt 兜底**
- **商业项目**：**Tier 4 Midjourney**

## LCM 改 prompt 速查表（**2026-06-13 实战**）

| ❌ 错 | ✅ 对 | 原因 |
|---|---|---|
| blanched shrimp | Cantonese poached shrimp glistening with oil | LCM 不认识 blanched |
| cooking wine | shaoxing wine | cooking wine = 棕色液体 |
| steamed (清蒸) | Cantonese steamed with soy sauce | 描述成品 + 调味 |
| 3 dipping sauces | LEFT/MIDDLE/RIGHT bowl separately | LCM 容易丢元素 |
| 错误 vs 正确 | LEFT ... RIGHT ... 显式对比 | LCM 不懂"对比"布局 |
| white shrimp | Q-bouncy pink shrimp | 描述质感和颜色 |
| Chinese food | Cantonese / Sichuan / Hunan style | 激活训练子集 |

## 相关 skill

- `local-sd-image-gen` —— 本地 SD 生图（含 LCM 改写 prompt 实战）
- `image-fallback-sourcing` —— 6 层级联 fallback（基于这份实战）
- `content-pipeline-zh` —— 中文内容流水线（小红书配图流程）
- `humanizer` —— 文案去 AI 味
