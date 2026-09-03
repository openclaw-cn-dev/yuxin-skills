# 可商用字体库

本目录只收录**可免费商用**的字体，供本 skill 出图排版时直接引用。
每套字体都提供原始 `.ttf`（部分含 `.otf`）与 `.woff2`（Web 用，体积约为 ttf 的 40%）。

带 `[wght]` 的是**可变字体**，一个文件覆盖全字重，CSS 里用 `font-variation-settings` 或 `font-weight: 100~900` 调用。

## 中文（`cjk/`）

| 字体 | 文件 | 授权 | 用途 |
|---|---|---|---|
| 思源黑体 Noto Sans SC | `NotoSansSC[wght].ttf` | SIL OFL 1.1 | 正文、UI 首选，字重 100–900 |
| 思源宋体 Noto Serif SC | `NotoSerifSC[wght].ttf` | SIL OFL 1.1 | 标题、中国风、静物海报 |
| 得意黑 Smiley Sans | `SmileySans-Oblique.ttf/.otf` | SIL OFL 1.1 | 标题力量感，自带倾斜，**只用于大字标题** |
| 霞鹜文楷 LXGW WenKai | `LXGWWenKai-Regular.ttf` | SIL OFL 1.1 | 手写感正文、长文案、书信体 |
| 站酷快乐体 | `ZCOOLKuaiLe-Regular.ttf` | SIL OFL 1.1 | 活泼、儿童、促销 |
| 站酷小薇 LOGO 体 | `ZCOOLXiaoWei-Regular.ttf` | SIL OFL 1.1 | 文艺细宋，LOGO/短标题 |
| 站酷庆科黄油体 | `ZCOOLQingKeHuangYou-Regular.ttf` | SIL OFL 1.1 | 圆润厚重，食品/生活类标题 |
| 马善政毛笔楷书 | `MaShanZheng-Regular.ttf` | SIL OFL 1.1 | 书法竖排、节气、宣纸暖白配色 |

## 西文 / 等宽（`latin/`）

| 字体 | 文件 | 授权 |
|---|---|---|
| Inter | `Inter[opsz,wght].ttf` | SIL OFL 1.1 |
| JetBrains Mono | `JetBrainsMono[wght].ttf` | SIL OFL 1.1 |
| Playfair Display | `PlayfairDisplay[wght].ttf` | SIL OFL 1.1 |
| Space Mono | `SpaceMono-Regular/Bold.ttf` | SIL OFL 1.1 |

## ⚠️ 未收录（需手动获取）

以下字体**免费商用但不允许第三方转载分发**，所以不放进本仓库，需要时去官网自行下载：

- **阿里巴巴普惠体** — https://fonts.alibabagroup.com/
- **OPPO Sans** — https://open.oppomobile.com/new/developmentDoc/info?id=13223
- **HarmonyOS Sans** — 华为开发者联盟 HarmonyOS 设计资源

## ❌ 绝对不要用的（需付费授权）

微软雅黑、苹方 PingFang、方正系列、汉仪系列、华康 / 文鼎系列。
**「系统里装了」≠「能商用」**，中文字体侵权是国内营销物料最高频的法律风险。

## Web 引用示例

```css
@font-face {
  font-family: 'Noto Sans SC';
  src: url('assets/fonts/cjk/NotoSansSC[wght].woff2') format('woff2-variations');
  font-weight: 100 900;
  font-display: swap;
}
```

## 授权文本

全部字体均为 SIL Open Font License 1.1，完整条款见 https://openfontlicense.org/ 。
OFL 允许商用、修改、再分发，唯一限制是**不得单独售卖字体本身**，且衍生字体需沿用 OFL。
