---
name: minimax-vision
description: 使用 MiniMax-M3 直接调用 vision API 处理图片。当 Hermes 内置 vision_analyze 返回 401 时使用。
---

# MiniMax Vision 图片处理

## 何时使用

当 `vision_analyze` 工具返回 401 错误时，使用本技能绕过 Hermes 内置的 vision 工具，直接调用 MiniMax API 处理图片。

用户可以说"用minimax读图"来触发本技能。

**根本原因**：Hermes vision_analyze 对 custom provider 发送请求时，可能使用 Anthropic 风格的 `x-api-key` header 而非 MiniMax 所需的 `Authorization: Bearer` header，导致 401。

## 使用方法

```bash
python3 /tmp/minimax_vision.py "/path/to/image.jpg" "你的问题"
```

图片路径通常来自飞书缓存：`/Users/hua/.hermes/image_cache/img_*.jpg`

## 脚本位置

脚本：`/tmp/minimax_vision.py`

依赖：Python 3 标准库（无需额外安装）

## 工作原理

1. Base64 编码图片
2. 调用 MiniMax `/v1/chat/completions` 端点（OpenAI 兼容）
3. 使用 `Authorization: Bearer` header
4. 模型：`MiniMax-M3`
5. 从 `~/.hermes/.env` 读取 `MINIMAX_API_KEY`

## 注意事项

- 如果 Hermes vision_analyze 恢复正常工作，优先使用内置工具
- MiniMax vision API 对大图片有 base64 长度限制，如遇超限需压缩
- 本脚本与 Hermes 内置 vision 工具独立运行，不经过 Hermes 的 provider 路由

## Hermes vision 工具修复

如果 `vision_analyze` 持续 401 且 API key 验证有效，问题可能在 Hermes 的 `auxiliary.vision` 配置残留。详见 `references/hermes-vision-config-debug.md`。
