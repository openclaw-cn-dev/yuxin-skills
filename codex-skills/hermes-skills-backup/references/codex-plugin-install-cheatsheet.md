# Codex 插件安装速查 — 开发类优先

> 用于每天的 codex-daily-evolution 巡检中"该装什么"。

## 一句话原则

老大是**渔芯科技全栈 + 自媒体**，Codex 必须双线支撑：
- **开发线**：跑全栈平台开发（Phase 1 渔芯平台）
- **自媒体线**：辅助内容运营

巡检时优先检查**开发类插件**（老大长期痛点：开发/工程类不足 16%）。

## 必须装的开发类插件（基线）

```bash
# 1. 前端 + 后端全栈开发（核心）
codex plugin add build-web-apps@openai-api-curated
codex plugin add build-web-data-visualization@openai-api-curated

# 2. UI 设计协同
codex plugin add figma@openai-api-curated

# 3. 代码审查 / 自动化
codex plugin add superpowers@openai-api-curated

# 4. GitHub 协同（私有仓库管理）
codex plugin add github@openai-api-curated

# 5. 浏览器自动化
codex plugin add browser@openai-bundled  # 内置，可直接装
```

**装机判定**：`codex plugin list` 看 STATUS 列，有 "not installed" 就装。

## 可选补充插件

| 场景 | 插件 | 用途 |
|---|---|---|
| 部署到云 | `render@openai-api-curated` | 简单云部署 |
| 测试流程 | `test-android-apps@openai-api-curated` | 移动端测试 |
| 安全审计 | `codex-security@openai-api-curated` | 代码漏洞扫描 |
| CI/CD | `circleci@openai-api-curated` | 持续集成 |
| 监控 | `sentry@openai-api-curated` | 错误监控 |
| 团队协作 | `linear@openai-api-curated` `notion@openai-api-curated` | 项目/文档管理 |
| 代码审查 | `coderabbit@openai-api-curated` | 自动 PR 审查 |
| 移动端 | `expo@openai-api-curated` | RN 开发 |
| 视频制作 | `remotion@openai-api-curated` | React 视频 |
| 通讯 | `twilio-developer-kit@openai-api-curated` | SMS/语音 |
| 硬件加速 | `nvidia@openai-api-curated` | GPU 推理 |

## 装完核对（2026-07-13 实测通过）

```bash
codex plugin list | grep "not installed"
# 期望：上面基线 5 个插件都不在 not installed 列表里

codex plugin list | grep "Status" -A 50 | grep -v "not installed"
# 期望：列出已安装插件清单
```

## 装不上 / 装错时的 3 个常见坑

1. **marketplace 不存在**：`codex plugin marketplace list` 先确认 marketplace 配置，再装
2. **plugin name 拼错**：`codex plugin list` 看真实插件名（含 @ 后缀）
3. **依赖缺失**：插件装完后跑一次 `codex plugin list` 看 STATUS 是不是 "installed"，有时依赖冲突会显示已装但功能失效

## 与 SKILL.md 路径的差异

| 技能类型 | 安装路径 | 老大说什么时用 |
|---|---|---|
| Codex 插件 | `codex plugin add <name>@<marketplace>` | "装个 superpowers 技能" |
| Codex skill (SKILL.md) | `~/.codex/skills/<name>/SKILL.md` curl 直拉 | "加个内容创作技能" |
| Hermes skill | `~/AppData/Local/hermes/skills/<category>/<name>/` | Hermes 飞书要用 |

**常见误判**：老大说"加技能" 默认是 **Codex skill**（SKILL.md），只有提到具体工具名（superpowers/figma/github）才走 plugin。