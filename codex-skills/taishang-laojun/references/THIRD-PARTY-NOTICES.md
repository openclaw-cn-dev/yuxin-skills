# Third-Party Notices（第三方声明）

本仓库的部分内容借鉴了以下开源项目的**规则框架**（识别清单/流程结构），已按原作者要求保留版权声明与许可文本。规则框架经中文创作场景适配；不得因改写表达而省略应保留的署名或许可。

---

## 1. Humanizer（英文原版）

- 项目：blader/humanizer（作者 Siqi Chen）
- 地址：https://github.com/blader/humanizer
- 用途：24种 AI 写作痕迹识别框架（skills/taishang-laojun/references/deai-rulebook.md 的识别清单来源之一）
- 许可：MIT License

MIT License 原文（保留）：

```
MIT License

Copyright (c) 2025 Siqi Chen

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## 2. Humanizer-zh（中文版）

- 项目：op7418/Humanizer-zh（作者 op7418）
- 地址：https://github.com/op7418/Humanizer-zh
- 用途：中文语境适配的 24 种 AI 写作模式识别、五步修复流程、常见 AI 词汇警示列表（skills/taishang-laojun/references/deai-rulebook.md 的中文规则与修复流程来源）
- 许可：MIT License（同上，以所附原始版权声明为准）

```
MIT License

Copyright (c) 2026 歸藏

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## 3. 规则的理论依据

- 维基百科社区指南：Signs of AI writing（https://en.wikipedia.org/wiki/Wikipedia:SIGNAI）——24种识别模式的共同理论来源。
- 本仓库在 skills/taishang-laojun/references/deai-rulebook.md 中对识别框架的复述与重写，属于对上述 MIT 项目的衍生使用，分发时应保留适用的版权与许可文本，不能把此说明视为对全部来源和用途的法律判断。

---

## 本仓库自身许可

「太上老君·AI炼丹炉」本体（方法内容、柳爷案例、炼丹炉结构）以 CC BY-NC 4.0 开源，见根目录 LICENSE。

以上两份 MIT 版权行于2026-10-22对照上游 LICENSE 核对。dbskill 的结构借鉴与本仓库许可见根目录 LICENSE、README；私人语料不随技能分发。

## 4. 本轮方法启发（0.4.0）

经历提炼、轻量素材积累与持续复盘的补强，参考了 Dan Koe 的 Turning Your Experiences Into Content、The Content Synthesis System、Iterating Your Content Flow 等课程章节；维护验收思路亦参考且曼 AI 产品课的用户访谈与效果评测内容。参考依据为用户提供的未经人工精校转写，未逐句核对原始音视频。

本轮为结合柳爷方法独立撰写的操作规则，不附课程转写、课件或原模板，不将外部作者经历标成柳爷成果，也不声称获得课程公开分发授权或作者背书。课程启发不等于这些规则已在所有赛道验证有效。

## 5. 去 AI 味规则与检测脚本（0.6.0）

`skills/taishang-laojun/references/deai-rulebook.md` 的“假对比”“伪深度路标”“盖住原稿重说”等检查与修法，`skills/taishang-laojun/scripts/ai_tell_linter.py` 的检测清单，来自柳爷自用的去 AI 味工具，该工具的规则参考了以下 MIT 项目的思路（2026-10-26 核对许可为 MIT）：

- LifelongLazyLearner/qu-ai-wei（Copyright (c) 2026 @LifelongLazyLearner）：https://github.com/LifelongLazyLearner/qu-ai-wei
- Hyacehila/humanizer-zh-next（Copyright (c) 2026 humanizer-zh-next contributors）：https://github.com/Hyacehila/humanizer-zh-next
- meikis/remove-ai-flavor-writing-skill（Copyright (c) 2026 B1lli）：https://github.com/meikis/remove-ai-flavor-writing-skill
- evelynyaxueke/anti-ai-writing-kit-zh（Copyright (c) 2026 Evelyn Ke）：https://github.com/evelynyaxueke/anti-ai-writing-kit-zh
- 以及上文第 1、2 项的 blader/humanizer、op7418/Humanizer-zh。

本仓库借用的是识别思路，规则用炼丹炉自己的语言重写，没有复制上述项目的原文。上述项目均以 MIT License 发布，许可全文与上文第 1 项相同，以各项目所附原始版权声明为准。
