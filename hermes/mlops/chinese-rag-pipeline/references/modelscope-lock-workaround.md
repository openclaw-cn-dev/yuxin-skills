# modelscope 锁文件绕过详解

## 症状

跑 `from modelscope import snapshot_download` 或者 `HuggingFaceBgeEmbeddings(model_name='AI-ModelScope/bge-large-zh-v1.5')`（隐式触发 download）卡住：

```
Still waiting to acquire lock on C:\Users\Administrator\.cache\modelscope\hub\.lock\AI-ModelScope___bge-large-zh-v1.5 (elapsed: 60.0 seconds)
```

60 秒、120 秒、5 分钟——**一直等**。

## 根因

`modelscope` 在 cache 目录有 `.lock` 文件，**保护模型不被并发下载覆盖**。但：
1. 之前的 Python 进程 SIGKILL / SIGTERM 没释放锁
2. 多个进程同时启动（hermes 多 worker / cron 后台）
3. modelscope 进程崩溃但 lock 文件残留

`rm -rf lock-file` 报 `Device or resource busy`——**因为还有进程在 hold 锁**。

## 解决方案（按推荐度）

### 方案 1：直接传本地路径（最佳）

跳过 `snapshot_download`——**直接告诉 langchain 模型在哪儿**：

```python
# 索引时（rag_setup.py）
BGE_PATH = r"C:\Users\Administrator\.cache\modelscope\AI-ModelScope\bge-large-zh-v1.5"
embeddings = HuggingFaceBgeEmbeddings(
    model_name=BGE_PATH,  # 关键：传本地路径
    model_kwargs={"device": "cpu"},
    encode_kwargs={"normalize_embeddings": True},
)
```

```python
# 查询时（rag_query.py）
embeddings = HuggingFaceBgeEmbeddings(
    model_name=r"C:\Users\Administrator\.cache\modelscope\AI-ModelScope\bge-large-zh-v1.5",
    model_kwargs={"device": "cpu"},
    encode_kwargs={"normalize_embeddings": True},
)
```

**优势**：零网络、零锁、加载 30 秒（从磁盘读 1.3GB）。

### 方案 2：设置 HF_HOME 让 langchain 走 HF cache

```python
import os
os.environ["HF_HOME"] = r"C:\Users\Administrator\.cache\huggingface"
os.environ["HF_HUB_CACHE"] = r"C:\Users\Administrator\.cache\huggingface\hub"
os.environ["SENTENCE_TRANSFORMERS_HOME"] = r"C:\Users\Administrator\.cache\huggingface"
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"
```

然后 `HuggingFaceBgeEmbeddings(model_name='BAAI/bge-large-zh-v1.5')`——**langchain 自动走 HF cache**（**如果模型已下**）。

### 方案 3：等锁自动释放

如果锁文件 1-2 分钟没释放——**说明没进程在 hold**——**但 rm 报 busy**——**说明有进程在用**——**kill 那个进程**：

```bash
# Windows
tasklist | findstr python
taskkill /F /PID <pid>
```

### 方案 4：清锁 + 重启

**不推荐**——`rm -rf .lock` 报 busy 时强行清——**会破坏半下载的模型**——**得重下 1.3GB**——**更慢**。

## 验证模型已下

```bash
ls "C:\Users\Administrator\.cache\modelscope\AI-ModelScope\bge-large-zh-v1.5\"
# 应看到: config.json + pytorch_model.bin + tokenizer.json + ...
```

```bash
ls "C:\Users\Administrator\.cache\huggingface\models--BAAI--bge-large-zh-v1.5\"
# 应看到: blobs/ refs/ snapshots/
```

**没下完就触发 `snapshot_download`**——**带 HF_ENDPOINT 走国内镜像**——**4 分钟下完 2.5GB**。

## 预防

1. **永远不用 `snapshot_download` + `from modelscope import`** 在生产代码
2. **下载阶段手动跑一次**——**进生产代码时只传本地路径**
3. **hermes 多 worker 环境**——**给每个 worker 单独的 `cache_dir`**

## 关键 takeaway

> **生产代码：本地路径 + 不调 download**
> **下载代码：单独脚本 + 走 HF-Mirror**
> **永不混用**
