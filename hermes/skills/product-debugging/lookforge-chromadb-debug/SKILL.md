---
name: lookforge-chromadb-debug
description: 排查 LookForge 项目 ChromaDB 向量数据库问题 — Docker 部署、数据卷挂载、版本兼容性、Schema 迁移、healthcheck 修复。触发条件：ChromaDB RAG 检索异常、Docker 容器数据不同步、知识库 API 超时/无数据。
version: 1.0.0
author: 渔芯科技
tags: [lookforge, chromadb, docker, 知识库, RAG]
---

# LookForge ChromaDB 调试方法论

## 核心架构（已验证）

```
宿主机 ./backend/data/chroma/
├── chroma.sqlite3           # ChromaDB 元数据库
└── ×××××××-.../            # embedding 向量文件

lookforge-chromadb 容器:8001  → ChromaDB HTTP 服务器 (v2 API)
lookforge-backend  容器:8000  → FastAPI + ChromaDB Python 客户端 (同步访问本地文件)
```

**关键路径映射**：
- backend 容器工作目录 `/app` = 宿主机 `./backend` (via `./backend:/app` bind mount)
- backend 的 `chroma_persist_dir = ./data/chroma` → 实际解析为 `/app/data/chroma` = 宿主机 `./backend/data/chroma`
- chromadb 容器数据 `/chroma/chroma/.chroma_db` = 宿主机 `./backend/data/chroma`

## 常见问题与解决方案

### 发现：NumPy 2.2.6 + onnxruntime 1.16.3 不兼容（2026-05-04 解决）

**症状**（分层故障，最难诊断）：
```
curl http://localhost:8001/api/v1/heartbeat        → 200 OK（Go 服务活着）
curl http://localhost:8001/api/v1/collections      → 502 Bad Gateway 或 []
docker exec lookforge-chromadb python3 -c "from chromadb.api.models import Collection"
→ AttributeError: _ARRAY_API not found
```

**根因**：
- 容器内 `numpy 2.2.6` + `onnxruntime 1.16.3`（编译时针对 NumPy 1.x）→ `AttributeError: _ARRAY_API not found`
- ChromaDB Python embedding function (ONNXMiniLM_L6_V2) 依赖 onnxruntime，加载时即崩溃
- Go HTTP 服务层仍响应 heartbeat，但 Python 层已完全失效
- **数据文件本身完好**（chroma.sqlite3 23.8MB + HNSW 目录存在），只是索引层无法访问

**诊断方法**：
```bash
# 1. 检查容器内 NumPy + onnxruntime 版本
docker exec lookforge-chromadb pip3 list | grep -E "numpy|onnx"

# 2. 验证 Go 层 vs Python 层分离
curl http://localhost:8001/api/v1/heartbeat  # 200 = Go 服务活着
curl http://localhost:8001/api/v1/collections # 502/[] = Python 层崩溃

# 3. 容器内直接测试（用 python3，无 curl/wget/ps/ss）
docker exec lookforge-chromadb python3 -c "import onnxruntime; print(onnxruntime.__version__)"
# onnxruntime 1.16.3 → 报错 _ARRAY_API not found
# onnxruntime >=1.20 → 正常

# 4. 检查 HNSW 索引是否损坏（数据文件存在但不可读）
docker exec lookforge-chromadb ls -la /chroma/chroma/
# 期望：chroma.sqlite3 (23MB+) + 多个 HNSW 子目录
```

**正确修复方案**（不是降级numpy！镜像内置会覆盖）：
```bash
# 升级 onnxruntime 到兼容 NumPy 2.x 的版本
docker exec lookforge-chromadb pip3 install "onnxruntime>=1.20"
docker restart lookforge-chromadb

# 验证修复
curl http://localhost:8001/api/v1/collections
# 期望：返回包含 lookforge_knowledge 和 ras_case_study 的列表
```

**⚠️ 重要：docker-compose.yml mount 路径错误也会导致数据丢失！**
```yaml
# 错误：挂载成文件（.chroma_db 是目录名不是文件！），覆盖了整个目录
# 重启后 collections 全空，数据文件被清空！
- ./backend/data/chroma:/chroma/chroma/.chroma_db

# 正确：挂载成目录
- ./backend/data/chroma:/chroma/chroma
```

### 诊断树：count() > 0 但 search() 返回 0（2026-05-04 新发现 + 更新）

**症状**：
```python
coll.count()  # → 337（非0）
coll.query(query_texts=['RAS养殖'], n_results=3)  # → ids=[], distances=[]（空！）
coll.peek(limit=3)  # → TypeError: object of type 'int' has no len()
```

**诊断流程**（分层递进）：

**Step 1：确认 collection 有数据**
```python
coll.count()  # → 非0则数据存在，进入了 metadata 段
```

**Step 2：检查 HNSW 向量段是否有数据（关键！）**
```bash
docker exec lookforge-chromadb python3 -c "
  import sqlite3
  conn = sqlite3.connect('/chroma/chroma/chroma.sqlite3')
  c = conn.cursor()
  c.execute('SELECT id, type, scope FROM segments')
  segs = c.fetchall()
  for sid, stype, sscope in segs:
      c.execute('SELECT COUNT(*) FROM embeddings WHERE segment_id = ?', (sid,))
      cnt = c.fetchone()[0]
      print(f'{sid[:8]}: type={stype.split(\"/\")[-1]}, embeddings={cnt}')
  conn.close()"
# 典型输出：
# 典型输出（HNSW bug）：
# 6edcae97: type=hnsw-local-persisted, embeddings=0    ← 向量段断层！
# 89015540: type=sqlite (metadata), embeddings=337    ← metadata 正常

# 典型输出（seq_id BLOB bug）：
# hnsw_segment: type=hnsw-local-persisted, embeddings=337  ← 向量段正常（不是0！）
# sqlite_segment: type=sqlite (metadata), embeddings=337    ← metadata段正常

**关键区分**：
- embeddings=0 in HNSW段 → HNSW索引断层（数据未写入向量段）
- embeddings>0 但 query() 返回空 + get()/peek() TypeError → seq_id BLOB 损坏（见 1h）

**Step 3：检查 HNSW data 文件大小（验证向量是否实际写入）**
```bash
docker exec lookforge-chromadb ls -la /chroma/chroma/*/data_level0.bin
# 如果 > 100KB 说明向量数据写入了文件，但索引映射丢失
# 如果 = 0 则数据完全丢失
```

**Step 4：检查 embedding_metadata 表（验证文本内容完整性）**
```bash
docker exec lookforge-chromadb python3 -c "
  import sqlite3
  conn = sqlite3.connect('/chroma/chroma/chroma.sqlite3')
  c = conn.cursor()
  c.execute('SELECT COUNT(*) FROM embedding_metadata WHERE key=\"chroma:document\"')
  print('docs in metadata:', c.fetchone()[0])
  c.execute('SELECT key, string_value FROM embedding_metadata WHERE id=1 LIMIT 5')
  for row in c.fetchall():
      print(f'  {row[0]}: {str(row[1])[:60]}')
  conn.close()"
```

**Step 5：检查 seq_id 类型（seq_id BLOB 损坏诊断）**
```bash
docker exec lookforge-chromadb python3 -c "
import sqlite3
conn = sqlite3.connect('/chroma/chroma/chroma.sqlite3')
c = conn.cursor()
c.execute('SELECT seq_id FROM embeddings LIMIT 3')
for row in c.fetchall():
    val = row[0]
    print(f'type={type(val).__name__}, is_bytes={isinstance(val, bytes)}')
conn.close()"
# type=int, is_bytes=False → seq_id BLOB 损坏！应改为 type=bytes, is_bytes=True
```

**⚠️ 注意**：从宿主机直接用 `chromadb.PersistentClient(path=...)` 访问 Docker 数据目录前，先确认版本匹配（宿主机 chromadb ≥1.0，容器内 0.4.x），版本不匹配会破坏 schema。

**重建知识库**（当数据损坏无法修复时）：
```bash
# 1. 删除损坏的 collection
cd /path/to/02-LookForge
python3 -c "
import sys
sys.path.insert(0, '$(pwd)')
from app.services.vector_store import vector_store
coll = vector_store.get_collection('lookforge_knowledge')
vector_store.chroma_client.delete_collection('lookforge_knowledge')
print('deleted')
"

# 2. 重新导入（用 import_folder 或批量导入脚本）
python3 backend/scripts/import_knowledge_base.py
# 或
python3 -c "
import sys; sys.path.insert(0, '$(pwd)')
from vector_store import import_folder
import_folder('2-知识库/')
"

# 3. 验证
python3 -c "
import chromadb
client = chromadb.PersistentClient(path='./backend/data/chroma')
coll = client.get_collection('lookforge_knowledge')
print('count:', coll.count())
r = coll.query(query_texts=['测试'], n_results=3)
print('search results:', len(r['ids'][0]) if r['ids'] else 0)
"
```

**预防**：
- 定期检查 HNSW 目录大小（正常应 > 1MB）
- ChromaDB 初始化失败（schema 问题）会连锁导致数据丢失，发现问题尽早处理

### 1e. REST API 替代方案（MCP 不可用时的生产方案）

当 MCP Server 无法在目标环境运行时（如 hermes-agent venv NumPy 2.x 限制），REST API 是成熟的生产替代方案：

```python
# lookforge_kb_server.py — FastAPI 封装 vector_store
# 运行：python3 lookforge_kb_server.py --port 8866

from fastapi import FastAPI, Query
from pydantic import BaseModel
import sys, chromadb
sys.path.insert(0, '/path/to/02-LookForge/backend')
from app.services.vector_store import vector_store

app = FastAPI()

class SearchRequest(BaseModel):
    query: str
    n_results: int = 5
    category: str = None

@app.get("/health")
def health(): return {"status": "ok"}

@app.get("/collections")
def list_collections():
    return {"collections": [c.name for c in vector_store.chroma_client.list_collections()]}

@app.post("/search")
def search(req: SearchRequest):
    results = vector_store.search_similar(
        req.query, n_results=req.n_results,
        category=req.category
    )
    return {"results": results}

@app.post("/import_folder")
def import_folder(path: str = Query(...)):
    count = vector_store.import_folder(path)
    return {"imported": count}
```

**验证**：
```bash
curl http://127.0.0.1:8866/health
curl "http://127.0.0.1:8866/search?query=循环水养殖&n_results=3"
curl -X POST "http://127.0.0.1:8866/import_folder?path=/path/to/knowledge"
```

**与 MCP 对比**：
| 方面 | MCP Server | REST API |
|------|-----------|----------|
| 调用方式 | stdio / 工具调用 | HTTP / curl |
| 集成复杂度 | 高（需 SDK 兼容） | 低（任何 HTTP 客户端）|
| hermes 集成 | 原生（工具调用） | subagent + terminal(curl) |
| NumPy 兼容性 | 需 NumPy 1.x | 无要求（直接调用）|

**容器内诊断工具限制**：只有 `python3` 可用，无 curl/wget/ss/ps。

### 1b. vector_store API 正确用法（重要！）

`vector_store.py` 导出的是**函数**而非**类**，不能用 `VectorStore()` 实例化：

```python
# ✅ 正确：直接导入函数（需要先 chdir 到 backend 目录）
import sys, os
sys.path.insert(0, '/path/to/02-LookForge/backend/app/services')
os.chdir('/path/to/02-LookForge/backend')
from vector_store import search_similar, add_documents, import_folder, list_collections
results = search_similar('关键词', n_results=5)

# ❌ 错误：尝试实例化不存在的类
from vector_store import VectorStore  # ImportError: cannot import name 'VectorStore'
vs = VectorStore()  # 不会工作
```

可用函数及签名（2026-05-04 验证）：

```python
# import_folder — 批量导入文件夹，返回 {'files': N, 'chunks': N, 'imported': N, 'errors': []}
import_folder(
    folder_path: Union[str, pathlib.Path],   # ✅ 目录或文件路径
    category: str = 'other',                  # metadata category 标签
    recursive: bool = True,                   # 是否递归子目录
    extensions: tuple[str, ...] = ('.md', '.txt', '.markdown'),  # 只导入这些扩展名
    batch_size: int = 500
)
# ⚠️ 注意：没有 collection_name 参数！collection_name 已在模块内硬编码为 COLLECTION_NAME
# 正确用法示例：
from app.services.vector_store import import_folder
import_folder('/path/to/知识库/RAS系统', category='ras_system')

# search_similar — 语义检索
search_similar(query: str, n_results: int = 5, category: str = None) -> list[dict]

# add_documents — 添加单个文档
add_documents(content: str, source: str, category: str = 'other', doc_id: str = None) -> bool

# list_collections — 列出所有 collection
list_collections() -> list[str]

# get_or_create_collection — 获取或创建 collection
get_or_create_collection(name: str = COLLECTION_NAME)
```

❌ 常见错误：

```python
# 错误1：尝试导入不存在的类
from vector_store import VectorStore  # ImportError

# 错误2：import_folder 不接受 collection_name 参数
import_folder('/path', collection_name='some_collection')  # TypeError

# 错误3：import_folder 只接受 folder_path（目录或.md文件）
import_folder('/path/to/single_file.md', ...)  # 文件不存在时报错

# ✅ 正确方式
from vector_store import import_folder
import_folder(folder_path='/path/to/知识库/RAS系统', category='ras_system')
```

**如果在独立脚本中必须从宿主机访问**，用 `subprocess` 调用 docker exec：
```python
import subprocess
result = subprocess.run([
    'docker', 'exec', 'lookforge-chromadb', 'python3', '-c', '''
import chromadb
client = chromadb.PersistentClient(path='/chroma/chroma')
col = client.get_or_create_collection('lookforge_knowledge')
results = col.query(query_texts=[%r], n_results=5)
print(len(results.get('documents', [[]])[0]))
''' % query, ...
], capture_output=True, text=True)
```

**预防**：
- 永远不要用宿主机的高版本 chromadb 客户端直接 `PersistentClient(path=.../data/chroma)` 访问 Docker 的数据目录
- 如果脚本报错 `no such column: collections.topic`，说明 schema 已损坏，需要重建（见 1c 节）

### 1c. lookforge-backend / 本地 Mac segfault（NumPy 冲突连锁反应）

**症状**：
- `docker exec lookforge-backend python3 -c "from app.services.vector_store import search_similar..."` → exit 139 (segfault)
- 本地 `hermes-agent/venv/bin/python3` 执行 `from app.services.vector_store import search_similar` → segfault

**根因**：
- backend 容器内 chromadb 1.5.8（HTTP 客户端）+ 本地 chromadb 客户端
- 连接 `lookforge-chromadb` 容器的 HTTP API
- embedding function 在客户端 Python 侧执行时崩溃（NumPy 2.2.6 + onnxruntime 不兼容）
- 这是同一 NumPy 问题的连锁反应

**修复**：修复 lookforge-chromadb 容器的 NumPy 问题后，segfault 自动解除

---

### ⚠️ CRITICAL: Overlay FS vs Bind Mount — 数据丢失根因（2026-05-06 新发现）

**灾难场景**：ChromaDB 容器运行中，`PersistentClient` 写入 `/chroma/chroma/` 时数据进入 overlay 文件系统（ephemeral），而非 host bind mount。容器重启后 overlay 丢失，host 挂载卷仍为旧/空文件。

**今日事故实录**：
- 2026-05-06 08:44 心跳检查发现 ChromaDB 所有 collection 丢失
- 容器内 `/chroma/chroma/chroma.sqlite3` 147KB（旧文件）
- 实际应有 31MB（从备份恢复验证）
- 根因：容器运行中 `PersistentClient` 写 overlay，Docker Desktop bind mount 未正确同步

**症状**：
```
容器内 /chroma/chroma/chroma.sqlite3  → 147KB（overlay 看到的旧文件）
宿主机 ./backend/data/chroma/chroma/     → 实际持久化数据（可能旧/空）
```

**验证命令**：
```bash
# 容器内看到的文件大小（运行中）
docker exec lookforge-chromadb stat -c "%s" /chroma/chroma/chroma.sqlite3
# 期望：31137792（31MB），如果只有 147456 → 数据丢失！

# Host 上实际文件大小
ls -la /Users/hua/Desktop/渔芯科技/6-产品研发/02-LookForge/backend/app/data/chroma/chroma/chroma.sqlite3
# 如果远小于容器内大小 → overlay vs bind mount 问题！
```

**如何确认写入目标**：
```bash
# 1. 容器内 df -h 检查挂载
docker exec lookforge-chromadb df -h | grep chroma
# 输出示例：
# overlay  ... /chroma/chroma   ← 这是 overlay（tmpfs， ephemeral）
# /run/host_mark/Users ... /chroma/chroma/chroma  ← 这是 host bind mount（持久化）

# 2. 如果 /chroma/chroma 是 overlay 且没有 host_mark 挂载 → 所有写入都是临时的！
docker exec lookforge-chromadb cat /proc/mounts | grep chroma
```

**⚠️ Docker Desktop 的 bind mount 特殊行为**：
- Docker Desktop on macOS 将 host 路径映射到 `/run/host_mark/Users/...`
- 容器内看到的 `/chroma/chroma` 可能是 overlay，未正确绑定到 host 目录
- **必须用 `df -h` + `cat /proc/mounts` 确认哪个文件系统是持久的**

**正确修复方案**：

**方案A（推荐）：确认 bind mount 正常工作后重启容器**
```bash
# Step 1: 停止容器（重要！停止后才能安全操作持久层）
docker stop lookforge-chromadb

# Step 2: 从备份恢复（docker cp 只在容器停止时有效！）
docker cp /path/to/backups/chroma_20260504.sqlite3 \
       lookforge-chromadb:/chroma/chroma/chroma.sqlite3

# Step 3: 验证文件大小
docker exec lookforge-chromadb stat -c "%s" /chroma/chroma/chroma.sqlite3
# 期望：31137792

# Step 4: 重启
docker start lookforge-chromadb
sleep 5

# Step 5: 验证数据（三项全绿）
docker exec lookforge-chromadb python3 -c "
import os, chromadb, json
from chromadb.config import Settings
os.chdir('/chroma')
client = chromadb.PersistentClient(path='chroma', settings=Settings(anonymized_telemetry=False))
cols = client.list_collections()
print(json.dumps([{'name': n.name, 'count': n.count()} for n in cols]))
"
# 期望：lookforge_knowledge ≥ 300, competitor_analysis ≥ 100
```

**⚠️ docker cp 关键约束（必须遵守！）**：
- `docker cp <host> <container>:<path>` → **容器必须在 STOPPED 状态**
- 容器 RUNNING 时 `docker cp` 报 "container is not running" 或静默失败
- `docker cp <container>:<path> <host>` → 从 RUNNING 容器复制文件可以工作

**方案B：重建 bind mount 配置**
如果 bind mount 配置错误导致 overlay 被使用，需要修改 docker-compose.yml：

```yaml
# docker-compose.yml — chromadb 服务
chromadb:
  volumes:
    # 确保正确挂载 host 目录（不是文件挂载！）
    - ./backend/data/chroma:/chroma/chroma  # ← 必须是目录挂载
  # 如果之前用了文件挂载（如 ./xxx:/chroma/chroma/.chroma_db），删除并重建
```

**预防检查清单（每次心跳必须执行）**：
```bash
# Step 1: 确认 bind mount 实际挂载到持久化存储
docker exec lookforge-chromadb df -h | grep -E "(chroma|/run/host_mark)"

# Step 2: 交叉验证文件大小
CONTAINER_SIZE=$(docker exec lookforge-chromadb stat -c "%s" /chroma/chroma/chroma.sqlite3 2>/dev/null || echo "0")
HOST_SIZE=$(ls -la ./backend/data/chroma/chroma/chroma.sqlite3 2>/dev/null | awk '{print $5}')
echo "Container: $CONTAINER_SIZE, Host: $HOST_SIZE"
if [ "$CONTAINER_SIZE" != "$HOST_SIZE" ] && [ "$CONTAINER_SIZE" != "0" ]; then
    echo "🔴 SIZE MISMATCH — 数据可能写入 overlay！立即检查！"
fi

# Step 3: 验证 ChromaDB 数据完整性（三项必须全绿）
docker exec lookforge-chromadb python3 -c "
import os, chromadb, json
from chromadb.config import Settings
os.chdir('/chroma')
client = chromadb.PersistentClient(path='chroma', settings=Settings(anonymized_telemetry=False))
cols = client.list_collections()
print(json.dumps([{'name': n.name, 'count': n.count()} for n in cols]))
"
```

### 1c. docker-compose 数据卷配置（2026-05-04 纠正）

**实际情况**：
```yaml
# docker-compose.yml — chromadb 服务
chromadb:
  volumes:
    - ./backend/data/chroma:/chroma/chroma  # ✅ 正确：目录挂载
    # 错误写法：./backend/data/chroma:/chroma/chroma/.chroma_db（挂载成文件！）

# backend 服务（通过 ./backend:/app mount 已覆盖 /app，额外挂载 chroma）
backend:
  volumes:
    - ./backend:/app
    - ./backend/data/chroma:/app/data/chroma  # 与 chromadb 共享同一份数据
```

**关键路径映射**：
- chromadb 容器内 `/chroma/chroma/` = 宿主机 `./backend/data/chroma/`
- backend 容器内 `/app/data/chroma/` = 宿主机 `./backend/data/chroma/`
- **两容器共享完全相同的数据文件**

### 1. ChromaDB numpy 2.x 兼容性故障（最常见根因，2026-05-02 新发现）

**症状**：容器 `lookforge-chromadb` 持续 restart loop，状态 `unhealthy`。日志含：
```
AttributeError: `np.float_` was removed in the NumPy 2.0 release. Use `np.float64` instead.
```

**原因**：
- `chromadb/chroma:0.4.22` 镜像内置 Python 环境使用 numpy 2.x
- chromadb 0.4.x 系列依赖已废弃的 `np.float_` 等 API，与 numpy 2.0+ 不兼容
- `chromadb/chroma:latest` 同样受影响

**⚠️ 关键陷阱：容器内 pip install 被 OOM kill**
```bash
# ❌ 这样做会被 kill（exit 137），无法持久化
docker exec lookforge-chromadb pip install "numpy<2.0"
# 错误：Killed — 容器内存限制导致 pip 下载时被 OOM Killer 终止
```

**正确修复路径**：

**方案A（推荐）— 修改 Dockerfile/requirements.txt 并重建镜像**：
在 `backend/` 目录的 Dockerfile 中加入 numpy 版本锁定：
```dockerfile
RUN pip install "numpy<2.0"
```
然后重建：
```bash
cd /path/to/02-LookForge
docker-compose build backend  # 或只重建需要修复的服务
docker-compose up -d chromadb
```

**方案B — 尝试最新版本**：
有些 chromadb 版本已修复 numpy 兼容性问题。修改 docker-compose.yml：
```yaml
# chromadb 镜像 tag 尝试 latest 或已知兼容版本
image: chromadb/chroma:latest
```
然后 `docker-compose up -d chromadb --force-recreate`

### 1b. 绕过容器的应急数据导入（host Python SDK）

当 ChromaDB 容器无法启动时，可以用 host Python 直接操作持久化数据：

**场景**：容器 down，但数据文件完好，需要导入新数据

```python
# host_python_import.py — 在宿主机执行，不依赖容器
import chromadb
from chromadb.config import Settings

# 使用 PersistentClient 直接访问数据目录
data_path = "/Users/hua/Desktop/渔芯科技/6-产品研发/02-LookForge/backend/data/chroma"
client = chromadb.PersistentClient(path=data_path)

# 获取或创建 collection
collection = client.get_or_create_collection("lookforge_knowledge")

# 添加数据（示例）
collection.add(
    documents=["文档内容..."],
    metadatas=[{"source": "ras_cases", "category": "aquaculture"}],
    ids=["unique_id_001"]
)
print(f"Collection count: {collection.count()}")
```

**验证 collection 存在**：
```python
import chromadb
client = chromadb.PersistentClient(path="./backend/data/chroma")
coll = client.get_collection("lookforge_knowledge")
print(coll.count())
```

### 1c. 版本不匹配导致 Schema 损坏（Critical — 会导致数据不可逆损坏！）

**症状**：
```
chroma.db.utils.WrappedReadOnlyDBError: database or disk is full
sqlite3.OperationalError: no such column: segments.topic
```
或 `AttributeError: _ARRAY_API not found`（NumPy 问题连锁反应）

**根因（2026-05-04 新发现）**：

ChromaDB **客户端版本**（1.5.8）和**服务端版本**（0.4.22）严重不匹配时，如果客户端直接操作持久化数据目录（而非通过 HTTP API），会**修改底层 SQLite schema**，导致服务端无法识别：

- 客户端 1.5.8 曾直接访问 `/chroma/chroma` 持久化目录
- 客户端写入的 schema 新增了服务端 0.4.22 不存在的列（如 `segments.topic`）
- 服务端重启或重新连接时报 `no such column` 错误
- **数据文件本身可能完好，但 schema 已损坏，无法通过修补恢复**

**排查步骤**：
```bash
# 1. 检查容器内 ChromaDB Python 库版本
docker exec lookforge-chromadb pip3 list 2>/dev/null | grep chromadb
# 预期：0.4.x（如 0.4.22）

# 2. 检查宿主机或容器内 ChromaDB Python 客户端版本
pip3 show chromadb 2>/dev/null | grep Version
# 或
hermes-agent/venv/bin/python3 -c "import chromadb; print(chromadb.__version__)"

# 3. 检查数据库 schema 是否损坏
docker exec lookforge-chromadb python3 -c "
import sqlite3
conn = sqlite3.connect('/chroma/chroma/chroma.sqlite3')
try:
    conn.execute('SELECT topic FROM segments LIMIT 1')
    print('schema OK')
except Exception as e:
    print('schema broken:', e)
conn.close()
"

# 4. 检查数据文件是否存在（与 schema 损坏分开判断）
docker exec lookforge-chromadb ls -la /chroma/chroma/
# 预期：chroma.sqlite3 (20MB+) + HNSW 子目录
```

**正确修复方案**：

> ⚠️ 如果 schema 已损坏，ALTER TABLE 无法回退版本差异，**必须重建容器和数据目录**。

```bash
cd /path/to/02-LookForge

# 步骤1：停止所有容器（避免继续写入损坏的数据）
docker-compose stop backend chromadb

# 步骤2：删除损坏的持久化数据（schema 已损坏，数据不可恢复）
# 先确认数据已备份或可重新导入
rm -rf ./backend/data/chroma/*

# 步骤3：重新创建并启动 chromadb 容器（会初始化新的空数据库）
docker-compose up -d chromadb

# 步骤4：等待容器就绪
sleep 10
curl http://localhost:8001/api/v1/heartbeat

# 步骤5：验证新数据库可用
curl http://localhost:8001/api/v1/collections
# 预期：[]（全新空数据库）

# 步骤6：重新导入知识库数据
python3 /path/to/import_knowledge_base.py

# 步骤7：启动 backend
docker-compose up -d backend
```

**预防措施**：

1. **永远不要用高版本客户端（≥1.0）直接访问低版本服务（≤0.4）的持久化数据目录**。访问前确认版本匹配。
2. 如果必须从宿主机操作 ChromaD 数据，使用 HTTP API（端口 8001）而非 PersistentClient 直接挂载路径。
- 定期备份 `./backend/data/chroma/` 目录（备份的是完整数据库快照，而非增量）。

**⚠️ macOS IPv6 localhost 问题（2026-05-06）**：

当从宿主机测试 ChromaDB HTTP API（端口 8001）时，`localhost` 可能解析到 IPv6 `::1`，导致连接问题：
```bash
# ❌ 可能失败（IPv6）
curl http://localhost:8001/api/v1/collections

# ✅ 始终可用
curl http://127.0.0.1:8001/api/v1/collections
```

同样适用于 backend 端口 8000：
```bash
curl http://127.0.0.1:8000/api/health   # ✅
curl http://localhost:8000/api/health    # ❌ 可能 reset
```

**错误修复思路（仅在 schema 轻微损坏时尝试，不保证有效）**：
```python
# ⚠️ 仅作为最后手段，不保证有效
import sqlite3
db_path = "/path/to/chroma.sqlite3"
conn = sqlite3.connect(db_path)
for table_col in [("segments", "topic", "TEXT DEFAULT 'default'"),
                  ("collections", "topic", "TEXT DEFAULT 'default'")]:
    table, col, dtype = table_col
    try:
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {col} {dtype}")
        conn.commit()
        print(f"Added '{col}' column to '{table}'")
    except Exception as e:
        print(f"Table '{table}': {e}")
conn.close()
```

### 2. Docker 数据卷挂载冲突（最常见！）

**症状**：`/api/knowledge/stats` 返回 0 条，但文件系统有数据；或不同容器看到不同数据

**原因**：
- `./backend:/app` bind mount 覆盖了容器内 `/app` 目录
- backend 和 chromadb 使用不同的 named volume 或 bind mount 指向不同路径
- 多个 volume 挂载到同一容器内路径，后挂载的覆盖前面的

**排查命令**：
```bash
# 检查容器内实际数据
docker exec lookforge-chromadb ls -la /chroma/chroma/.chroma_db/
docker exec lookforge-backend ls -la /app/data/chroma/
# 检查宿主机原始数据
ls -la /Users/hua/Desktop/渔芯科技/6-产品研发/02-LookForge/backend/data/chroma/
```

**正确配置**：
```yaml
# chromadb 服务
volumes:
  - ./backend/data/chroma:/chroma/chroma/.chroma_db

# backend 服务（通过 ./backend:/app mount 已覆盖 /app，额外挂载 chroma）
volumes:
  - ./backend:/app
  - ./backend/data/chroma:/app/data/chroma  # 确保与 chromadb 同一份数据
```

**不要**在 docker-compose 顶部声明 `chromadb` named volume，这会导致容器使用隔离的空 volume。

### 2. Healthcheck 失败（容器内无 wget）

**症状**：`lookforge-chromadb is unhealthy`（持续），但服务正常运行（heartbeat API 正常返回）

**原因**：`chromadb/chroma:0.4.22-numpy2fixed` 镜像内**没有 wget、curl**（只有 `/bin/sh` 和 `/usr/local/bin/python3`）。healthcheck 配置用了 `wget -q --spider ...` 永远失败。

**正确修复**（保留 `service_healthy`，修 healthcheck 命令）：

```yaml
# docker-compose.yml — chromadb 服务
chromadb:
  image: chromadb/chroma:0.4.22-numpy2fixed
  mem_limit: 2g  # 防止 OOM
  healthcheck:
    test: ["CMD-SHELL", "python3 -c \"import urllib.request; urllib.request.urlopen('http://localhost:8000/api/v1/heartbeat')\""]
    interval: 30s
    timeout: 10s
    retries: 3
    start_period: 30s

# backend depends_on 应使用 service_healthy（不是 service_started！）
backend:
  depends_on:
    chromadb:
      condition: service_healthy  # ✅ 等待 chromadb 真正就绪后再启动
```

**验证命令**：
```bash
# 确认容器内有 python3（健康检查的唯一可用工具）
docker exec lookforge-chromadb which python3
# 输出：/usr/local/bin/python3

# 手动测试 heartbeat（用 python3）
docker exec lookforge-chromadb python3 -c "import urllib.request; print(urllib.request.urlopen('http://localhost:8000/api/v1/heartbeat').read())"

# 重启后检查状态
docker-compose -f docker-compose.yml up -d chromadb
# 等待30秒后应为 (healthy)
docker ps | grep chromadb
```

**❌ 错误修复**（降级方案，会丢失健康检查保护）：
```yaml
# 不要这样做！改用 service_started 意味着 backend 不等 chromadb 就启动
chromadb:
  condition: service_started  # ❌ 会导致 backend 启动时 chromadb 还未就绪
```

### 2b. ChromaDB 502 Bad Gateway vs 正常响应

**关键区分**：
- **容器正常运行** → `docker exec lookforge-chromadb python3 -c "..."` 内部 HTTP 请求成功（返回 JSON）
- **宿主机访问端口 8001** → 502 Bad Gateway（Docker 代理层问题）
- **容器完全 down** → 连接被拒绝（`Connection refused`）

**502 的可能原因**：
1. ChromaDB 进程存在但未监听预期端口（检查：`docker exec lookforge-chromadb ps aux | grep chroma`）
2. health check 返回非 200 导致 Docker 代理降级
3. 容器进程 panic 后重启中（查看 `docker logs lookforge-chromadb`）

**诊断命令**：
```bash
# 检查容器内进程
docker exec lookforge-chromadb ps aux

# 检查容器内 HTTP 响应（直接执行 Python）
docker exec lookforge-chromadb python3 -c "
import urllib.request
r = urllib.request.urlopen('http://localhost:8000/api/v1/version', timeout=5)
print('OK:', r.read())
"

# 从宿主机访问（会经过 Docker proxy）
curl http://localhost:8001/api/v1/version  # 502 = 容器问题，非网络层
```

### 3. FastAPI Body() 路由 Bug（POST /api/knowledge/query 422）

**症状**：`POST /api/knowledge/query` 返回 422，`{"detail":[{"type":"string_type","loc":["body"],"msg":"Input should be a valid string","input":{"query":"...","top_k":3}}]}`

**原因**：FastAPI 的 `query: str = Body(...)` 不会自动将 JSON body 解析为字段，而是把整个 body 当 string 传给 query 参数

**正确修复**：使用 Pydantic 模型作为请求体：
```python
from pydantic import BaseModel

class QueryRequest(BaseModel):
    query: str
    top_k: int = 5
    category: Optional[str] = None
    source: Optional[str] = None
    project_id: Optional[str] = None

@router.post("/query")
async def query_knowledge(request: QueryRequest) -> dict:
    results = collection.query(
        query_texts=[request.query],
        n_results=request.top_k,
        ...
    )
```

❌ 错误写法（`query: str = Body(...)` 仍然422）：
```python
async def query_knowledge(query: str = Body(...), top_k: int = 5, ...)  # 422!
```

### 3a. FastAPI 参数装饰选错：缺 `Query()` 装饰（仿真 API 静默 fallback 默认值 — 2026-09-05 实测）

**症状**：
```bash
# POST /api/projects/test/simulation/cases
curl -X POST -H "Content-Type: application/json" \
  -d '{"hw_subtype":"consumer_electronics"}'
# 期望：返回 5 个 generic 仿真用例
# 实际：返回 8 个 ras_aquaculture 用例 + hw_subtype='ras_aquaculture'
```

**鉴别诊断**：
| 调用方式 | 期望 | 实际 | 说明 |
|---------|------|------|------|
| `?hw_subtype=consumer_electronics` (query) | 5 个 generic | ✅ 5 个 generic | query 参数正常 |
| `{"hw_subtype":"consumer_electronics"}` (body) | 5 个 generic | ❌ 8 个 RAS（fallback 默认值） | body 参数未装饰，FastAPI 校验失败静默吞掉 |

**根因**：`def get_simulation_cases(project_id, hw_subtype=None)` 没声明 `Query`，FastAPI 收到 JSON body 时校验失败 → 静默 fallback 到默认 `None` → 服务层用默认 `"ras_aquaculture"`。

**正确修复**：
```python
# ❌ 错误
from fastapi import APIRouter
@router.post("/{project_id}/simulation/cases")
def get_simulation_cases(project_id: str, hw_subtype: Optional[str] = None):
    ...

# ✅ 正确
from fastapi import APIRouter, Query
@router.post("/{project_id}/simulation/cases")
def get_simulation_cases(
    project_id: str,
    hw_subtype: Optional[str] = Query(default=None, description="..."),
):
    ...
```

**排查口诀**：
- 看到 endpoint 接受"筛选用"的标量参数（hw_subtype/category/filter/status）但**没有** `Query()` / `Body()` / Pydantic model 装饰 → 100% 中招
- 客户端 `curl -d '{"key":"val"}'`（body）和 `curl '?key=val'`（query）结果不一致 → **典型症状**

**验证三连**（修完必跑）：
```bash
# 1. query 参数传非默认值（应返回对应子类型）
curl -X POST 'http://host/api/projects/test/simulation/cases?hw_subtype=consumer_electronics'
# 期望：hw_subtype=consumer_electronics, cases 数 = generic（5）

# 2. 不传参数（应返回默认 ras_aquaculture）
curl -X POST 'http://host/api/projects/test/simulation/cases'
# 期望：hw_subtype=ras_aquaculture, cases 数 = RAS（8）

# 3. 重启 backend 容器后再测
docker restart lookforge-backend && sleep 5
curl -X POST 'http://host/api/projects/test/simulation/cases?hw_subtype=consumer_electronics'
```

**教训**：
- "默认值硬编码"这种表象 bug **经常是 FastAPI 参数声明 bug**
- 调试时**先 curl 测真实行为**，别只看函数签名
- 修完必须重启容器（`docker restart`），改代码不会热更新

chromadb:0.4.22 镜像内有 wget，支持 v1 API 健康检查：
```yaml
healthcheck:
  test: ["CMD-SHELL", "wget -q --spider http://localhost:8000/api/v1/heartbeat || exit 1"]
  interval: 10s
  timeout: 5s
  retries: 5
```

**注意**：`chromadb:latest`（最新版本）的 healthcheck 需要使用 v2 端点：
```yaml
healthcheck:
  test: ["CMD-SHELL", "wget -q --spider http://localhost:8000/api/v2/heartbeat || exit 1"]
```

版本不同，API 端点不同！0.4.22 用 v1，latest 用 v2。

### 1d. ChromaDB 存储架构（2026-05-04 确认）

**结论**：lookforge-chromadb 和 lookforge-backend 通过 bind mount 共享同一数据目录，数据已同步。

| 实例 | 类型 | 路径/端口 | 说明 |
|------|------|-----------|------|
| lookforge-chromadb | HTTP服务 | 端口8001 | 容器内 `/chroma/chroma/` |
| 后端 PersistentClient | Python客户端 | 容器内 `/app/data/chroma` | 与 chromadb 共享数据 |

**验证**：
```bash
# 内部 API（容器内）
docker exec lookforge-chromadb python3 -c \
  "import urllib.request, json; data=urllib.request.urlopen('http://localhost:8000/api/v1/collections'); print(json.loads(data.read()))"

# 外部 API（宿主机 curl，端口8001）
curl http://localhost:8001/api/v1/collections
# 两者应返回相同的 collection 列表
```

### 4. FastAPI Async Endpoint 同步阻塞

**症状**：`POST /api/knowledge/query` 超时（60s），但直接 Python 调用 ChromaDB 正常

**原因**：ChromaDB Python 客户端是同步的，在 async endpoint 中调用会阻塞事件循环

**临时方案**：增加超时时间，或用 `asyncio.to_thread()` 包装同步调用

### 5. Backend 容器 `depends_on` 链

```
lookforge-backend depends_on:
  - lookforge-chromadb (depends_on: condition: service_healthy)
  - lookforge-db
  - lookforge-redis
```

chromadb 必须 healthcheck 通过 backend 才能启动。

### 6. `collection.get()` 的 `include` 参数不含 `distances`

**症状**：`{"error":"Expected include item to be one of embeddings, documents, metadatas, uris, data, got distances"}`

**原因**：`distances` 是 `collection.query()` 的有效参数，但 **不是** `collection.get()` 的有效参数

**排查**：在 `knowledge.py` 中搜索 `collection.get(` 或 `collection.get(` 附近的 `include` 参数

**修复**：从 `collection.get()` 的 `include` 列表中移除 `distances`：
```python
# ❌ 错误
results = collection.get(where=where, include=["documents", "metadatas", "distances"])

# ✅ 正确（collection.get 不返回 distances）
results = collection.get(where=where, include=["documents", "metadatas"])
```

**注意**：如果需要距离信息，改用 `collection.query()` 而不是 `collection.get()`。

### 1f. ChromaDB 0.4.22 metadata 查询（SQLite 直连 + embedding_metadata 表结构 2026-05-04）

**ChromaDB 0.4.22 存储结构**：

ChromaDB 0.4.x 的数据分为两个存储区域：
1. **embeddings 主表**：`(id, segment_id, embedding_id, seq_id, created_at)` — 不含 metadata
2. **embedding_metadata 表**：`(id, key, string_value, int_value, float_value, bool_value)` — key-value 格式存储所有 metadata

```sql
-- embedding_metadata 表结构
(id INTEGER, key TEXT, string_value TEXT, int_value INTEGER, float_value REAL, bool_value INTEGER)
-- 一条 embedding 记录在 embedding_metadata 中有多行（每个 metadata key 一行）
-- embedding_id=1 的记录：key='category', key='source', key='doc_name', key='section'
```

**可靠查询方法：SQLite 直连**（绕过 Python API bug）：
```bash
docker exec lookforge-chromadb python3 -c "
import sqlite3
conn = sqlite3.connect('/chroma/chroma/chroma.sqlite3')
c = conn.cursor()

# 总片段数
c.execute('SELECT COUNT(*) FROM embeddings')
print('Total embeddings:', c.fetchone()[0])

# category 分布
c.execute('''
    SELECT em.string_value, COUNT(*) as cnt
    FROM embedding_metadata em
    WHERE em.key = \"category\"
    GROUP BY em.string_value
    ORDER BY cnt DESC
''')
print('Category distribution:')
for row in c.fetchall():
    print(f'  {row[0]}: {row[1]}')

# source 分布（提取顶级目录）
c.execute('''
    SELECT em.string_value
    FROM embedding_metadata em
    WHERE em.key = \"source\"
''')
from collections import Counter
dirs = Counter()
for (path,) in c.fetchall():
    parts = path.split('/')
    dirs[parts[1] if len(parts) >= 2 else '(无)'] += 1
print('Top-level directory distribution:')
for d, cnt in dirs.most_common():
    print(f'  {d}: {cnt}')

conn.close()
"
```

**批量 UPDATE 修复 category**（见 1g 节）。

### 1g. CATEGORY_MAP 映射失效导致所有记录 category='other'（2026-05-04 新发现）

**症状**：
```sql
-- 所有 337 条记录的 category metadata 值都是 'other'
SELECT string_value, COUNT(*) FROM embedding_metadata WHERE key='category' GROUP BY string_value;
-- → category=other: 337
```

**根因**：Phase1 初始导入时 `CATEGORY_MAP` 未生效，所有文件都被标记为 `category='other'`。

**影响**：向量检索时无法按 `category` 过滤，削弱了知识库的分类检索能力。

**已验证修复方案（SQLite UPDATE 批量修复）**：

ChromaDB 0.4.x 的 metadata 存储在 `embedding_metadata` key-value 表（不是主表）：
```sql
-- embedding_metadata 表结构
(id INTEGER, key TEXT, string_value TEXT, int_value INTEGER, float_value REAL, bool_value INTEGER)
-- key='category' → string_value='other'
-- key='source' → string_value='2-知识库/水产养殖深库/xxx.md'
```

**修复脚本**（通过 `docker exec` 执行）：
```python
import sqlite3

DIR_MAP = {
    "水产养殖深库": "aquaculture_deep",
    "RAS系统": "ras_system",
    "水产养殖": "aquaculture",
    "市场行情": "market",
    "设备知识库": "equipment",
    "设备资料": "equipment",
    "鱼晓一号": "yuxiao",
    "鱼乐宝RAS数字孪生平台": "yulebao",
    "建筑AI": "construction_ai",
    "研究": "research",
    "养殖案例": "case_study",
    "创意建议": "idea",
    "用户服务": "user_service",
    "竞品分析": "competitor",
    "其它": "other",
}

conn = sqlite3.connect("/chroma/chroma/chroma.sqlite3")
c = conn.cursor()

# JOIN embeddings 和 embedding_metadata，按 source 路径提取顶级目录映射到 category
c.execute("""
    SELECT e.id, em.string_value
    FROM embeddings e
    JOIN embedding_metadata em ON e.id = em.id AND em.key = 'source'
""")
rows = c.fetchall()

updated = 0
for emb_id, source in rows:
    parts = source.split("/")
    top_dir = parts[1] if len(parts) >= 2 else None
    new_cat = DIR_MAP.get(top_dir)
    if new_cat is None:
        continue
    c.execute("UPDATE embedding_metadata SET string_value = ? WHERE id = ? AND key = 'category'",
              (new_cat, emb_id))
    updated += 1

conn.commit()
print(f"Updated: {updated}")
conn.close()
```

**修复结果**（2026-05-04 验证）：
- Updated: 315, Skipped: 22
- 新分布：aquaculture_deep:115, ras_system:28, aquaculture:20, research:11, construction_ai:9, equipment:8, market:6, yuxiao:6, yulebao:3, user_service:3, case_study:2, idea:1, other:125

**后续**：建议同时修复 `import_knowledge_base.py` 的 `SKIP_DIRS` 逻辑，确保 `os.walk` 遍历子目录时也跳过 `_archive`、`memory`、`设备3d建模库` 等目录。

### 1h. ChromaDB 0.4.x seq_id BLOB 损坏 — count()>0 但 query() 返回空（2026-05-04 新发现）

**症状**（分层故障，最难诊断）：
```python
coll.count()  # → 338（非0，数据存在 ✅）
coll.query(query_texts=['循环水养殖'], n_results=3)  # → ids=[], distances=[]（永远空 ❌）
coll.peek(limit=3)  # → 正常返回数据 ✅
coll.get(ids=['xxx'])  # → TypeError: object of type 'int' has no len() ❌
```

**根因**：`embeddings.seq_id` 列类型声明为 BLOB，但实际存储的是 Python `int`（1, 2, 3...）。ChromaDB 0.4.x 的 `_decode_seq_id()` 对 BLOB 调用 `len()`，而 `int` 没有 `len()` 方法：
```python
# ChromaDB 0.4.x 内部代码（约）：
def _decode_seq_id(raw):
    if isinstance(raw, bytes):
        return struct.unpack('>Q', raw)[0]  # 期望 BLOB
    return raw  # int 直接返回？不，会对 bytes 调用 len()
# 实际：对 BLOB 调用 len(int_value) → TypeError
```

**诊断流程**（分层递进）：

**Step 1：确认 collection 有数据**
```python
coll.count()  # 非0 → 数据存在，进入 metadata 段
```

**Step 2：确认向量数据存在（HNSW 段）**
```bash
docker exec lookforge-chromadb python3 -c "
import sqlite3
conn = sqlite3.connect('/chroma/chroma/chroma.sqlite3')
c = conn.cursor()
c.execute('SELECT id, type, scope FROM segments')
segs = c.fetchall()
for sid, stype, sscope in segs:
    c.execute('SELECT COUNT(*) FROM embeddings WHERE segment_id = ?', (sid,))
    cnt = c.fetchone()[0]
    print(f'{sid[:8]}: type={stype.split(\"/\")[-1]}, embeddings={cnt}')
conn.close()"
# 期望输出：
# hnsw_segment: type=hnsw-local-persisted, embeddings=338  ← 向量段正常
# sqlite_segment: type=sqlite (metadata), embeddings=338  ← metadata段正常
```

**Step 3：检查 seq_id 实际类型**
```bash
docker exec lookforge-chromadb python3 -c "
import sqlite3, struct
conn = sqlite3.connect('/chroma/chroma/chroma.sqlite3')
c = conn.cursor()
c.execute('SELECT seq_id FROM embeddings LIMIT 5')
for row in c.fetchall():
    val = row[0]
    print(f'type={type(val).__name__}, value={val}, is_bytes={isinstance(val, bytes)}')
conn.close()"
# 症状输出：
# type=int, value=1, is_bytes=False  ← 应该是 bytes！
# type=int, value=2, is_bytes=False
```

**修复方案（两步修复）**：

**Step 1：修复 seq_id 格式**（`scripts/fix_seq_id.py`）
```python
# 将所有 seq_id 从 Python int 转为8字节 big-endian BLOB
import sqlite3, struct

conn = sqlite3.connect('/chroma/chroma/chroma.sqlite3')
c = conn.cursor()

# 读取所有 seq_id
c.execute('SELECT rowid, seq_id FROM embeddings')
rows = c.fetchall()

fixed = 0
for rowid, seq_id_val in rows:
    if isinstance(seq_id_val, int):
        # int → 8字节 big-endian BLOB
        packed = struct.pack('>Q', seq_id_val)
        c.execute('UPDATE embeddings SET seq_id = ? WHERE rowid = ?', (packed, rowid))
        fixed += 1

conn.commit()
print(f'Fixed: {fixed}')
conn.close()
```

**Step 2：重建 collection（关键！必须做！）**

修复 seq_id 后 query() 仍然不工作——因为旧 collection **没有 embedding function**。没有 embedding function 的 collection 不存储 query embeddings，所以 query() 永远返回空。必须重建：

```python
# scripts/rebuild_collection.py
import chromadb
from chromadb.config import Settings
from chromadb.utils.embedding_functions import DefaultEmbeddingFunction

# 1. 用 Docker 内 Python 连接（版本匹配）
client = chromadb.PersistentClient(
    path='/chroma/chroma',
    settings=Settings(anonymized_telemetry=False)
)

# 2. 提取旧 collection 数据
old_coll = client.get_collection('lookforge_knowledge')
data = old_coll.peek(limit=10000)  # peek 不走 _decode_seq_id，正常工作
print(f'Peeked: {len(data[\"ids\"])} items')

# 3. 删除旧 collection
client.delete_collection('lookforge_knowledge')
print('Deleted old collection')

# 4. 创建新 collection（带 DefaultEmbeddingFunction）
new_coll = client.create_collection(
    'lookforge_knowledge',
    embedding_function=DefaultEmbeddingFunction()
)
print('Created new collection with DefaultEmbeddingFunction')

# 5. 批量添加数据
batch_size = 100
for i in range(0, len(data['ids']), batch_size):
    batch = {k: v[i:i+batch_size] for k, v in data.items()}
    new_coll.add(**batch)
print(f'Added {len(data["ids"])} items in {(len(data["ids"])+batch_size-1)//batch_size} batches')

# 6. 验证
print('count:', new_coll.count())
r = new_coll.query(query_texts=['循环水养殖'], n_results=3)
print('query results:', len(r['ids'][0]) if r['ids'] else 0)
```

**验证修复**：
```bash
# 用 hermes venv 测试（连接 Docker ChromaDB）
cd /path/to/02-LookForge/backend
/Users/hua/.hermes/hermes-agent/venv/bin/python3 -c "
import sys
sys.path.insert(0, '$(pwd)')
from app.services.vector_store import search_similar
results = search_similar('循环水养殖', n_results=3)
for r in results:
    print(f'  [{r[\"distance\"]:.4f}] {r[\"content\"][:60]}...')
"
# 期望：3条结果，metadata 完整
```

**预防**：
- 这个 bug 可能由某次非正常关闭（容器 kill、OOM）触发
- 定期用 `SELECT seq_id FROM embeddings LIMIT 1` 检查 seq_id 类型是否为 bytes

### 1i. 旧 collection 缺少 embedding function（2026-05-04 新发现）

**症状**：seq_id 修复后 `query()` 仍返回空

**根因**：Phase1 早期创建的 collection 使用了手动 import，没有配置 embedding function。ChromaDB 的 embedding function 用于：
1. **添加数据时**：将文本转为向量
2. **查询时**：将 query 字符串转为向量

没有 embedding function 的 collection：
- ✅ `add()` 可以添加已有向量（外部计算好）
- ❌ `query()` 无法将 query 字符串转为向量 → 永远返回空

**诊断**：
```bash
docker exec lookforge-chromadb python3 -c "
import chromadb
client = chromadb.PersistentClient(path='/chroma/chroma')
coll = client.get_collection('lookforge_knowledge')
print('embedding_function:', coll._embedding_function)
# 输出 None → 没有 embedding function
"
```

**处理**：见 1h 的 rebuild_collection.py

### 1e. 两个存储后端的数据不同步（已过时）

> ⚠️ 2026-05-04 确认：docker-compose bind mount 使两容器共享数据，此问题已不存在。

### 7. 两个存储后端的数据不同步（已过时，仅作历史参考）

> ⚠️ 此条已过时。lookforge-chromadb 和 lookforge-backend 通过 `./backend/data/chroma` bind mount 共享数据，不会不同步。保留仅作历史参考。

**历史症状**：`/api/knowledge/stats` 返回 0 条，但 ChromaDB HTTP 服务 (localhost:8001) 有数据；反之亦然

**历史原因**：LookForge 曾有两个独立的 ChromaDB 实例（HTTP 服务 vs 本地 SQLite）

**对齐策略**（已实现）：确保两个服务指向同一份数据（docker-compose bind mount）

## 调试流程

```
1. curl http://localhost:8000/api/knowledge/stats  # 快速检查 API 响应
2. docker ps  # 确认容器状态（backend 应为 Up，chromadb 应为 Up）
3. docker exec lookforge-backend pip show chromadb | grep Version  # 确认客户端版本 ≥1.0.0
4. docker exec lookforge-backend ls /app/data/chroma/  # 检查容器内数据
5. ls -la /path/to/project/backend/data/chroma/  # 对比宿主机数据
6. # 如果 schema 报错（segments.topic），执行版本修复：编辑 requirements.txt → chromadb>=1.0.0 → rebuild
7. # 如果 include 报错（distances），检查 knowledge.py 的 collection.get() include 参数
8. # 如果数据不一致，确认是两个存储后端不同步问题（见 7）
9. docker-compose down && docker-compose up -d --build
10. 等待 10s 后 curl http://localhost:8001/api/v2/heartbeat  # 验证 chromadb HTTP
11. curl http://localhost:8000/api/knowledge/stats  # 验证 backend
```

## 验证命令（SQLite 直连优先）

**⚠️ API 500 但 triple validation 正常：Segment Metadata 损坏（2026-05-06 新发现）**

当 ChromaDB triple validation（count/peek/query）全部正常，但 API `/api/knowledge/*` 返回 500 错误时，问题不在数据层，而在 **segment metadata 编码损坏**：

```bash
# ✅ triple validation（数据层）— 正常
docker exec lookforge-chromadb python3 -c "
import os, chromadb
from chromadb.config import Settings
os.chdir('/chroma')
client = chromadb.PersistentClient(path='chroma', settings=Settings(anonymized_telemetry=False))
for n in client.list_collections():
    c = client.get_collection(n.name)
    print(f'{n.name}: count={c.count()}')
"
# → lookforge_knowledge: 342, competitor_analysis: 13 ✅

# ❌ API 层 — 500 错误
curl http://127.0.0.1:8000/api/knowledge/stats
# → {"detail":"Error executing plan: Error sending backfill request to compactor..."}

# ❌ API 层 — 500 错误
curl -X POST http://127.0.0.1:8000/api/knowledge/query \
  -H "Content-Type: application/json" \
  -d '{"query":"RAS养殖", "top_k":3}'
# → 同上错误
```

**根因**：query plan/compactor 在读取 segment metadata 时，BLOB 列被误读为 INTEGER 类型。不是 `upsert()` 元数据覆盖问题。

**修复方案**：
1. `delete_collection()` + `create_collection()` + `add()` 重建（推荐）
2. 或 ChromaDB compact 操作修复 segment metadata

---

## 新发现：Segment Metadata 类型不兼容（u64/BLOB）— query() 失败但 count() 正常（2026-05-07）

**症状**：
```
Error reading from metadata segment reader: mismatched types;
Rust type `u64` (as SQL type `INTEGER`) is not compatible with SQL type `BLOB`
```

**影响**：知识库 `query()` 接口不可用（/api/knowledge/query 报错），但 `count()` 和 `peek()` 仍正常返回数据。

**与 seq_id BLOB 损坏的区别**：
| 特征 | seq_id BLOB 损坏（1h） | u64/BLOB segment 错误（此条） |
|------|--------------------|---------------------------|
| `count()` | 非0 | 非0 |
| `peek()` | TypeError | 正常 |
| `query()` | 返回空 | 报错（type mismatch） |
| 根因 | seq_id 列存了 int 而非 bytes | segment metadata 列类型声明与实际不符 |
| 涉及表 | embeddings.seq_id | segments / embedding_metadata |

**诊断**：
```bash
# 在 chromadb 容器内验证各 collection 状态
docker exec -i lookforge-chromadb python3 << 'PYEOF'
import os, chromadb, json
from chromadb.config import Settings
os.chdir('/chroma')
client = chromadb.PersistentClient(path='chroma', settings=Settings(anonymized_telemetry=False))
for coll in client.list_collections():
    c = client.get_collection(coll.name)
    print(f"Collection: {c.name}, count: {c.count()}")
    try:
        r = c.query(query_texts=["test"], n_results=1)
        print(f"  query: OK ({len(r.get('documents',[[]])[0])} results)")
    except Exception as e:
        print(f"  query: FAIL -> {e}")
PYEOF

# 检查 segments 表结构
docker exec lookforge-chromadb python3 -c "
import sqlite3
conn = sqlite3.connect('/chroma/chroma/chroma.sqlite3')
c = conn.cursor()
c.execute('SELECT id, type, scope FROM segments LIMIT 5')
for row in c.fetchall():
    print(row)
# 检查 embeddings 表结构
c.execute('PRAGMA table_info(embeddings)')
for row in c.fetchall():
    print('embeddings col:', row)
conn.close()
"
```

**修复方案**：
```bash
# 方案A（推荐）：重建 collection
# 1. 在容器内 peek() 导出所有数据
docker exec -i lookforge-chromadb python3 << 'PYEOF'
import os, chromadb, json
from chromadb.config import Settings
os.chdir('/chroma')
client = chromadb.PersistentClient(path='chroma', settings=Settings(anonymized_telemetry=False))

collections = ['lookforge_knowledge', 'competitor_analysis']
for name in collections:
    try:
        old = client.get_collection(name)
        data = old.peek(limit=100000)
        print(f"=== {name} ===")
        print(json.dumps({'ids': data['ids'], 'metadatas': data['metadatas'], 'documents': data['documents'][:3]}))
        print(f"Total: {len(data['ids'])}")
    except Exception as e:
        print(f"{name}: {e}")
PYEOF

# 方案B：如果数据量大，考虑备份后重建（参考 1h节的 rebuild_collection.py）
```

**数据文件路径**（已确认）：
- 容器内：`/chroma/chroma/chroma.sqlite3`（31MB，主数据库）
- 旧文件：`/chroma/chroma.sqlite3`（147KB，遗留，不要用）

---

```bash
# ✅ 第一步：SQLite 直连（最可靠，绕过 Python API bug）
docker exec lookforge-chromadb python3 -c "
import sqlite3
conn = sqlite3.connect('/chroma/chroma/chroma.sqlite3')
c = conn.cursor()
c.execute('SELECT COUNT(*) FROM embeddings')
print('Total:', c.fetchone()[0])
c.execute('SELECT name, id FROM collections')
for row in c.fetchall(): print('Collection:', row[0], 'UUID:', row[1])
c.execute('SELECT key, COUNT(*) FROM embedding_metadata GROUP BY key')
for row in c.fetchall(): print(f'  {row[0]}: {row[1]}')
conn.close()"

# ChromaDB v2 API 健康检查
curl http://localhost:8001/api/v2/heartbeat

# 知识库统计（实际路径是 /api/knowledge/，不是 /api/v1/knowledge/！）
curl http://localhost:8000/api/knowledge/stats

# 语义检索
curl -X POST http://localhost:8000/api/knowledge/query \
  -H "Content-Type: application/json" \
  -d '{"query":"建筑结构设计", "top_k":3}'

# 按source过滤检索
curl -X POST http://localhost:8000/api/knowledge/query \
  -H "Content-Type: application/json" \
  -d '{"query":"建筑AI", "top_k":3, "source":"building_ai_knowledge"}'

# 直接用Python验证（API超时/失败时的备用验证方法）
cd /path/to/02-LookForge && python3 -c "
import chromadb
client = chromadb.PersistentClient(path='./backend/data/chroma')
coll = client.get_or_create_collection('lookforge_knowledge')
print('Total:', coll.count())
r = coll.query(query_texts=['查询词'], n_results=3, include=['documents','metadatas','distances'])
for i,doc_id in enumerate(r['ids'][0]):
    print(f'  [{r[\"distances\"][0][i]:.4f}] {r[\"documents\"][0][i][:80]}...')
"
```

## 重要纠正（2026-05-01）

### API路径纠正
- ❌ 错误：`/api/v1/knowledge/*`（CLAUDE.md中记录错误）
- ✅ 正确：`/api/knowledge/*`（来自main.py: `app.include_router(knowledge.router, prefix="/api/knowledge", ...)`）

### ChromaDB HTTP API v2 的Collection路径格式
v2 API要求CRN格式，不能直接用collection名：
```bash
# ❌ 错误（InvalidArgumentError: CRN must be in format <tenant>:<database>:<collection_name>）
curl http://localhost:8001/api/v2/collections/lookforge_knowledge

# ✅ 正确格式
curl http://localhost:8001/api/v2/collections/DefaultTenant:lookforge:lookforge_knowledge
```

### 两个存储后端的实际关系（纠正）
docker-compose配置下，backend和chromadb容器挂载**同一宿主机目录**（`./backend/data/chroma`），因此：
- ✅ 它们看到**完全相同的SQLite数据文件**
- ✅ HTTP API能读到PersistentClient写入的数据（因为指向同一文件）
- ✅ 之前的"两个独立存储"描述不准确——数据通过bind mount已同步

验证：宿主机直接用Python客户端读取，结果与HTTP API一致（146条数据，collection名`lookforge_knowledge`）。

### ChromaDB healthcheck问题
- 症状：`lookforge-chromadb is unhealthy`（持续）
- 但服务正常运行（`/api/v2/heartbeat` 返回正常）
- 原因：healthcheck配置使用了可能不支持的wget选项
- 影响：无（backend通过 `condition: service_started` 启动，不依赖healthcheck）
- 处理：已知问题，暂不修复

## 批量导入知识库数据

导入脚本位置：
```
/Users/hua/Desktop/渔芯科技/6-产品研发/02-LookForge/backend/import_building_ai_knowledge.py
```

用法：
```bash
cd /path/to/backend
python3 import_building_ai_knowledge.py
```

脚本特点：
- 基于内容 hash 做 doc_id（幂等，不会重复导入）
- 按 markdown 标题分章节，每章节800字符+100重叠分块
- 支持 category/source/metadata 元数据标记
- 重复运行只追加新文档，不覆盖已有数据

## 已知环境

- ChromaDB Python 客户端版本：1.5.8
- ChromaDB Docker 镜像：chromadb/chroma:latest
- embedding 模型：sentence-transformers/all-MiniLM-L6-v2
- 项目路径：`/Users/hua/Desktop/渔芯科技/6-产品研发/02-LookForge/`
- 宿主机数据目录：`./backend/data/chroma/`
- ChromaDB HTTP 端口：8001
- Backend API 端口：8000
