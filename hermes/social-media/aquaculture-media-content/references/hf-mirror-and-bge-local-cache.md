# HF-Mirror + bge 模型本地缓存实战

> 适用于：bge / SD / 任何 HuggingFace 模型的国内下载

## HF-Mirror 镜像

**URL**：`https://hf-mirror.com`

**用法**（**4 个环境变量必设**）：
```bash
export HF_ENDPOINT=https://hf-mirror.com
export HF_HOME=C:/Users/Administrator/.cache/huggingface
export HF_HUB_CACHE=C:/Users/Administrator/.cache/huggingface/hub
export SENTENCE_TRANSFORMERS_HOME=C:/Users/Administrator/.cache/huggingface
```

**用途**：
- `huggingface_hub` 库
- `sentence-transformers` 库
- `transformers` 库
- `diffusers` 库
- **所有 HF 库自动走镜像**

## bge-large-zh-v1.5 下载

**ModelScope 路径更稳**（HF-Mirror 偶尔卡大文件）：

```python
from modelscope import snapshot_download
ms_path = snapshot_download(
    "AI-ModelScope/bge-large-zh-v1.5",
    cache_dir="C:/Users/Administrator/.cache/modelscope"
)
# 存到: C:/Users/Administrator/.cache/modelscope/AI-ModelScope/bge-large-zh-v1.5/
```

**大小**：~2.5GB / 下载时间 ~4 分钟（国内镜像）

## 关键陷阱

### 陷阱 1：bge 模型两套缓存目录

| 库 | 默认路径 |
|---|---|
| `modelscope.snapshot_download` | `~/.cache/modelscope/AI-ModelScope/...` |
| `sentence_transformers.SentenceTransformer` | `~/.cache/huggingface/hub/models--...` |
| `transformers.AutoModel` | `~/.cache/huggingface/hub/...` |

**症状**：modelscope 下完了，sentence-transformers 找不到——**卡 90 秒后报网络错**。

**解决**：**别用 `SentenceTransformer('BAAI/xxx')` 字符串**——**直接传本地绝对路径**：

```python
# ✅ 对
m = SentenceTransformer(r'C:\Users\Administrator\.cache\modelscope\AI-ModelScope\bge-large-zh-v1.5')
# ❌ 错（会去 HF hub 找）
m = SentenceTransformer('BAAI/bge-large-zh-v1.5')
```

### 陷阱 2：modelscope snapshot_download 锁

**症状**：`Still waiting to acquire lock on C:\...\.lock\AI-ModelScope___bge-large-zh-v1.5 (elapsed: 60s)`

**原因**：之前 `snapshot_download()` 没正常退出，**锁住模型**。

**解决**：
1. **首选**：用本地路径加载（**别再 snapshot_download**）
2. 杀残留进程：`taskkill /F /IM python.exe`
3. 等 60 秒自动释放

### 陷阱 3：HF-Mirror 卡大文件

**实测**：
- SD 1.5（5GB）—— HF-Mirror ~5 分钟（**OK**）
- bge-large-zh（2.5GB）—— HF-Mirror **有时卡 10+ 分钟**（**改 modelscope**）
- LCM Dreamshaper（2GB）—— HF-Mirror ~3 分钟（**OK**）

**判断标准**：模型 < 2GB 走 HF-Mirror，> 2GB 走 modelscope。

## RAG + 4 群实战

**老大建的 4 群**：
- 🦐 美食社：`oc_c1bf60f8d03aefcbcb18f595e7ef4e19`
- 🐟 养殖圈：`oc_4acad97e312c37674630da282d76ab4b`
- ⚙️ 设备库：`oc_ffaa900080df1c6ddeb7b8107948f013`
- 🏢 上市公司：`oc_c7cf3d684575b89aa290b849e6508fc8`

**RAG 召回精准度**：
- 14 文档 / 69 chunk → 召回不相关（**虾料 Omega-3**）
- 补 22 篇 → 36 文档 / 279 chunk → 召回完美（**对应主题**）
- **结论**：召回精准度 = 知识库密度的唯一变量
