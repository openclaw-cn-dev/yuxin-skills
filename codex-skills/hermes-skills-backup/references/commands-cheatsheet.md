# Codex CLI 命令速查（实测 0.142.5）

## 已验证的命令

```bash
# 版本
codex --version                              # → codex-cli 0.142.5

# 插件管理
codex plugin list                            # 列出所有 marketplace 的插件和安装状态
codex plugin add <name>@<marketplace>        # 安装插件（NOT install）
codex plugin remove <name>@<marketplace>     # 卸载插件
codex plugin marketplace list                # 列出已配置的 marketplace
codex plugin marketplace upgrade             # 升级 Git marketplace（无 --dry-run）

# 不存在的命令（已验证）
# codex plugin install   → 不存在，用 add
# codex config list      → 不存在，直接读 config.toml
# codex plugin marketplace upgrade --dry-run → 不存在
```

## 当前 marketplace（2026-07-13）

| Marketplace | 类型 | 插件数 |
|-------------|------|--------|
| openai-bundled | 内置 | 2 (browser, latex) |
| openai-api-curated | API 精选 | 29 |

## 当前已安装插件（19 个）

browser, superpowers, build-web-apps, build-web-data-visualization, figma, github, circleci, sentry, coderabbit, codex-security, nvidia, render, test-android-apps, temporal, linear, expo, twilio-developer-kit, notion, remotion

## 模型配置

- 模型: deepseek-v4-pro-260425
- Provider: ark_agentplan (火山引擎 ARK)
- wire_api: responses
- base_url: https://ark.cn-beijing.volces.com/api/plan/v3

## Skills 目录（2026-07-13）

- 总计: 37 个（排除 .system/）
- 营销/自媒体: 31 个
- 开发/工程: 6 个
- ⚠️ 开发类 skills 严重不足（6/37 = 16%），建议从 GitHub 补充后端/数据库/测试类 skills