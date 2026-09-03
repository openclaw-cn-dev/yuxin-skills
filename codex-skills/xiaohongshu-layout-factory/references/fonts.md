# 字体加载（国内优先，本 Skill 自带，不依赖其它 Skill）

渲染模板**禁止只挂 Google Fonts CDN**。顺序写死：

1. **国内镜像** `fonts.font.im`（CSS 和字体文件域名都会改写，国内可访问）
2. **备用国内镜像** `fonts.loli.net`
3. **外网兜底** `fonts.googleapis.com`（前两级都失败才走）

实现：复制 `assets/font-loader.html` 进每页 `<head>`（工厂种子模板、实例 template.html、build.py 的 HEAD 都用这一份）。不要自己再写一条 Google Fonts `<link>`。

就绪门仍必带：`html:not(.fonts-ok) body{visibility:hidden}` + `document.fonts.ready` 后加 `.fonts-ok`；渲染命令 `--virtual-time-budget=15000`。

## 默认三款（可商用 SIL OFL）

| 角色 | 字体 | CSS family |
|---|---|---|
| 中文主字体 | 霞鹜文楷 TC | `'LXGW WenKai TC',serif` |
| 英文 / 数字 italic | Fraunces | `'Fraunces',serif` |
| 手写点缀 | Caveat | `'Caveat',cursive` |

换字体：改 `--font-zh / --font-en / --font-hand` 三个 token，并改 `font-loader.html` 里的 `q` 查询串。入仓前核对授权，只收可商用（SIL OFL / 明确免费商用）。单档字重不要合成加粗。

## 可选：本地字体仓（离线 / 完全不走 CDN）

如果用户提供 ttf/otf，放到实例 `assets/fonts/` 后用 `@font-face` 相对路径加载，可跳过 CDN。不强制；默认走上面的三级网络源即可。
