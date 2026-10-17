---
name: minimax-embedding-api
description: "MiniMax 开放平台 Embedding API 调用 — embo1 模型、参数格式、实测可用的请求模板"
version: 1.0.0
author: 玉芬（实测 2026-07-29）
license: MIT
triggers:
  - "minimax embedding"
  - "minimax 向量"
  - "embo1"
  - "minimax 词嵌入"
---

# MiniMax Embedding API（实测版）

## 一句话结论

**TokenPlanUltra 套餐的 embedding 模型是 `embo1`**。API 端点 `/v1/embeddings`（MiniMax 中国站 `https://api.minimaxi.com`），参数格式跟 OpenAI 标准不一样。

---

## 关键差异（vs OpenAI Embeddings API）

| 项 | OpenAI 标准 | MiniMax 实际 |
|---|---|---|
| 端点 | `POST /v1/embeddings` | ✅ 相同 |
| **请求参数** | `input` | ⚠️ **`texts`**（字符串数组） |
| **必填参数** | 无 | ⚠️ **`type`**（`db` / `query`） |
| `group_id` | 不需要 | 不需要 |
| 响应字段 | `data[].embedding` | ⚠️ **`vectors`** |
| `model` 字段 | `text-embedding-3-small` | ⚠️ **`embo1`** |

---

## 正确请求模板

```bash
curl -X POST 'https://api.minimaxi.com/v1/embeddings' \
  -H 'Authorization: Bearer <MINIMAX_API_KEY>' \
  -H 'Content-Type: application/json' \
  -d '{
    "model": "embo1",
    "texts": ["你的文本1", "你的文本2"],
    "type": "db"
  }'
```

**Python**：

```python
import requests
resp = requests.post(
    'https://api.minimaxi.com/v1/embeddings',
    headers={'Authorization': f'Bearer {api_key}'},
    json={
        'model': 'embo1',
        'texts': ['Hello', 'World'],
        'type': 'db'  # 入库用 db，查询用 query
    }
)
data = resp.json()
vectors = data.get('vectors')  # 二维数组，每个元素是一条文本的向量
```

**type 取值**：
- `db` — 把文本写入向量库时（db ingestion）
- `query` — 检索时查询用

---

## 响应示例

```json
{
  "vectors": [
    [0.012, -0.034, 0.567, ...],
    [0.089, 0.123, -0.045, ...]
  ],
  "base_resp": {
    "status_code": 0,
    "status_msg": "success"
  }
}
```

向量维度需实测确认（MiniMax 官方文档未公开）。

---

## 常见错误码

| status_code | 含义 | 处理 |
|---|---|---|
| 0 | 成功 | — |
| 2013 | `invalid params` | 检查 `texts` 是数组、`type` 已填、值合法 |
| 1004 | auth 失败 | 检查 API key 前缀：`sk-cp-` 是订阅，`sk-api-` 是按量 |
| 1002 | 余额不足 | Token Plan Ultra 配额耗尽，去平台充值 |

---

## 注意事项

1. **不要用 OpenAI 格式**：`{"model": "...", "input": "..."}` 会被 MiniMax 拒（缺 `texts` + `type`）
2. **官方文档站**（`platform.minimaxi.com`）**不列 embedding API**，需要从代码层 / 老文档查
3. **向量维度未公开**，实测后存到 RKR 知识库给后续脚本读
4. **跨境问题**：中国站 `api.minimaxi.com` 是 `MiniMax`（minimax.com 全名是 minimaxi.com），国际站是 `api.minimax.chat` / `api.minimax.io`，key 不通用
5. **TypePlanUltra key**（`sk-cp-` 前缀）：实测可访问 embedding（前提是有配额）

---

## 已验证的模型名

| model 名 | 状态 |
|----------|------|
| `embo1` | ✅ **正解**（HTTP 200 不报 unknown model） |
| `MiniMax-Embedding-01` | ✅ API 接受（但内部可能 alias 到 embo1） |
| `minimax-embedding-01` | ✅ 同上 |
| `MiniMax-Text-01` / `minimax-text-01` | ⚠️ 这是对话模型，用作 embedding 会被拒 |

---

## 已验证的端点

| URL | 状态 |
|-----|------|
| `https://api.minimaxi.com/v1/embeddings` | ✅ 中国站主端点 |
| `https://api.minimax.chat/v1/embeddings` | ✅ 国际站（key 通用） |
| `https://api.minimax.io/v1/embeddings` | ❌ 域名已死 |
| `https://api.minimaxi.com/v1/embedding`（单数） | ❌ 404 |

---

## 调试脚本模板

```python
import requests, sys

api_key = sys.argv[1]
text = sys.argv[2] if len(sys.argv) > 2 else "Hello world"

resp = requests.post(
    'https://api.minimaxi.com/v1/embeddings',
    headers={'Authorization': f'Bearer {api_key}'},
    json={'model': 'embo1', 'texts': [text], 'type': 'db'}
)
print(resp.status_code, resp.text[:300])
```

---

## 相关

- `minimax-cn-image-gen` — 豆包/MiniMax 图像生成
- `feishu-publish` — RKR 内容推送
- Hermes Gateway 暂未代理 embedding 路由（仅 chat + claude）

---

**实测时间**：2026-07-29  
**版本**：v1.0.0  
**TODO**：向量维度确认 / type 取值边界 / 批量限制