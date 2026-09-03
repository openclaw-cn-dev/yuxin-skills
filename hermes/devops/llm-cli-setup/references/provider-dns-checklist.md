# 第三方 LLM 平台域名验真清单

装/接第三方 LLM 平台前**必须**先过这一关。本清单收录小弟踩过的 + 老大用过的平台域名，按"是否真实存在"分类。

## 验真脚本（Windows / Git Bash）

```bash
# 把下面的占位符替换成实际平台名，跑一遍
for sub in "" "www." "platform." "api." "console." "developer."; do
  echo "=== ${sub}DOMAIN ==="
  nslookup "${sub}DOMAIN" 2>&1 | grep -E "Address|Name|non-existent" | head -5
  echo
done
```

**判定**：
- 全部解析出 IP → 进配置
- 主域有 IP、子域没 → 问老大具体控制台 URL
- **主域 Non-existent domain** → 🛑 停手，**不要瞎猜 base URL**

## 已验证存在的平台（可直接信）

| 平台 | 控制台域 | API base URL 示例 | 协议 |
|---|---|---|---|
| Anthropic 官方 | console.anthropic.com | https://api.anthropic.com | Anthropic Messages |
| OpenAI 官方 | platform.openai.com | https://api.openai.com/v1 | OpenAI Chat Completions |
| Google AI Studio | aistudio.google.com | https://generativelanguage.googleapis.com/v1beta | Gemini API |
| DeepSeek | platform.deepseek.com | https://api.deepseek.com/v1 | OpenAI 兼容 |
| 智谱 BigModel | open.bigmodel.cn | https://open.bigmodel.cn/api/paas/v4 | OpenAI 兼容 |
| 硅基流动 | cloud.siliconflow.cn | https://api.siliconflow.cn/v1 | OpenAI 兼容 |
| 月之暗面 | platform.moonshot.cn | https://api.moonshot.cn/v1 | OpenAI 兼容 |
| 阿里云百炼 | bailian.console.aliyun.com | https://dashscope.aliyuncs.com/compatible-mode/v1 | OpenAI 兼容 |
| 腾讯混元 | cloud.tencent.com/product/hunyuan | https://api.hunyuan.tencent.com/v3 | OpenAI 兼容 |
| 字节豆包/Doubao | console.volcengine.com | https://ark.cn-beijing.volces.com/api/v3 | OpenAI 兼容 |
| MiniMax（公司名 MiniMax）| platform.minimaxi.com | https://api.minimaxi.com/anthropic 或 `/v1` 视协议 | Anthropic 兼容 / OpenAI 兼容 |

> **重要修正（2026-06 实锤）**：MiniMax 真实控制台域名是 `platform.minimaxi.com`（**末尾是 i，不是 cn**）。
> CC-Switch 官网（`ccswitch.io`）抓的供应商列表里 MiniMax 项明确指向 `https://platform.minimaxi.com`，
> 可信度高于本机 nslookup（截图证实，不只是 DNS 解析）。
> 走 Anthropic 兼容的 base URL 通常是 `https://api.minimaxi.com/anthropic`，模型名在控制台"模型广场"拿（**别用本地叫法如 MiniMax-M3 直接传**）。

## 已验证不存在的拼写（绝对不要用）

| 假域名 | nslookup 结果 | 备注 |
|---|---|---|
| `MiniMax.cn` | Non-existent domain | 主域本身就不存在 |
| `platform.MiniMax.cn` | Non-existent domain | 子域跟着不存在 |
| `www.MiniMax.cn` | Non-existent domain | 同上 |

**反例教训**：老大曾说"用 platform.MiniMax.cn"，小弟信了结果装出哑炮。**永远先 nslookup 验真，再做任何配置。**

**但**：DNS 通 ≠ 名字对。MiniMax 真实域名是 `minimaxi.com`（末尾 i），**不是 `.cn` 也不是 `MiniMax.cn`**。
光看 `platform.minimaxi.com` 能解析 ≠ 老大口中的"那个平台"就是它——必须看官方截图或控制台右上角的真实 URL 来二次确认拼写。

## 域名拼写常见错（自检）

- `MiniMax` / `MiniMax` / `MiniMax` —— MiniMax 真实叫法只有"MiniMax"和"MiniMax"两种
- `OpenAI` 拼成 `openai`、`OpenAi`
- `DeepSeek` 拼成 `deep-seek`
- `siliconflow` vs `siliconFlow` vs `silicon-flow`
- 阿里百炼的 `dashscope.aliyuncs.com`（API 域）和 `bailian.console.aliyun.com`（控制台域）不一样

## 备查工具

```bash
# 备用 DNS 解析（防本地 DNS 污染）
nslookup DOMAIN 8.8.8.8
nslookup DOMAIN 114.114.114.114
nslookup DOMAIN 223.5.5.5

# 多平台对照
curl -sS -o /dev/null -w "HTTP %{http_code}\n" --max-time 8 https://DOMAIN/
```

不同 DNS 给不同结果 → 本地 DNS 被污染，让老大换 DNS 或开 DoH（dns.alidns.com/dns-query）。
