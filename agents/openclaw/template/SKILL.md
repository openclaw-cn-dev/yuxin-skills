---
name: openclaw-template
description: OpenClaw AI 网关配置模板 — API 路由与多 Provider 管理
version: 2.0.0
tags: [template, onboarding, openclaw, gateway]
---

# OpenClaw AI 网关模板

## 使用场景
当需要配置或更新 OpenClaw AI 网关（路由 LLM API 请求）时使用。

## 角色定位
OpenClaw 是**AI API 网关**，负责:
- LLM API 路由（火山引擎 / minimax / OpenAI）
- 多 Provider 负载均衡
- API Key 管理
- 请求日志/监控

## 配置

OpenClaw 配置在 `~/.config/openclaw/config.yaml`：

```yaml
# ~/.config/openclaw/config.yaml

# API 端点
port: 8080
host: "127.0.0.1"

# LLM Providers
providers:
  volcengine:
    api_key: "${VOLC_API_KEY}"
    base_url: "https://ark.cn-beijing.volces.com/api/plan/v3"
    
  minimax:
    api_key: "${MINIMAX_CN_API_KEY}"
    base_url: "https://api.minimaxi.com"

# 路由规则
routes:
  - path: "/v1/chat/completions"
    provider: volcengine
    model: deepseek-v4-flash-260425
```

## 管理命令

```bash
# 启动
openclaw serve

# 验证
curl http://127.0.0.1:8080/v1/health

# 查看状态
openclaw status
```
