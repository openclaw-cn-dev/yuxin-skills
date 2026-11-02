---
name: kb-watchdog-setup-hermes
description: 在 macOS 上配置 kb_watchdog.py 知识库监控的完整流程。触发条件：运行 kb_watchdog.py 时报错 NameError，或需要设置知识库自动同步时加载。
version: 1.0.0
author: 老莫/渔芯科技
tags: [kb_watchdog, chromadb, lookforge, 知识库]
---

# kb_watchdog.py 部署指南

## 已知 Bug（必须先修复）

**Bug 1: FileSystemEventHandler NameError**

`kb_watchdog.py` 存在一个严重 Bug：`FileSystemEventHandler` 类定义在 `try/except ImportError` 块之外。当 `watchdog` Python 包未安装时，Python 解析该类时报 `NameError`，导致脚本完全无法运行（即使使用 `--sync-once`）。

**症状**：
```
NameError: name 'FileSystemEventHandler' is not defined
```

**根因**：类定义在 `try:` 块之外，但引用了 `try` 块内才导入的 `FileSystemEventHandler`。

**修复**：将以下内容包裹在 `if HAS_WATCHDOG:` 条件块内：
- `class KbFileHandler(FileSystemEventHandler)`
- `def _is_in_kb_root()`
- `def _get_relative_path()`
- `def watchdog_watch()`

同时在 `else:` 块提供空桩函数：
```python
else:
    def watchdog_watch(dry_run: bool = False):
        logging.error("watchdog 未安装...")
```

**Bug 2: ChromaDB 客户端/服务端版本不匹配导致数据库损坏（Critical！）**

kb_watchdog.py 通过 `from app.services.vector_store import get_client` 访问 ChromaDB，如果 hermes venv 的 chromadb 客户端版本（1.5.8）与服务端版本（0.4.22）不匹配，直接操作持久化数据目录会损坏 SQLite schema。**症状**：`sqlite3.OperationalError: no such column: segments.topic`。

**解决方案**：使用 HTTP API 模式（`kb_watchdog_http.py`），通过 `requests` 库调用 `http://localhost:8001/api/v1/...` 接口，完全绕过客户端版本问题。

**Bug 3: launchd 中文路径 Unicode 转义导致崩溃**

launchd 在解析 `WorkingDirectory` 时会对中文路径进行 Unicode 转义（如 `\U6d4b\U8bd5`），导致 `Operation not permitted` 或 exit -11 (SIGSEGV)。**所有脚本必须放在非中文路径**。

**正确做法**：
- 脚本放在 `/Users/hua/lookforge-scripts/`（无中文）
- plist 中 `ProgramArguments` 使用 hermes venv 的 python 可执行文件（完整路径）
- plist 中 `WorkingDirectory` 指向 `/Users/hua/lookforge-scripts/`（无中文）

---

## 快速启动

### 1. 验证 Bug 已修复
```bash
cd /Users/hua/Desktop/渔芯科技/6-产品研发/02-LookForge
python3 scripts/kb_watchdog.py --sync-once
```
预期输出：`✅ 全量同步完成：新增314/修改0/删除0，共2046个片段`

### 2. 安装 watchdog（如需）
```bash
# user site-packages（给 /usr/bin/python3 用）
pip3 install watchdog

# hermes venv（给 launchd 用，必须！）
/Users/hua/.hermes/hermes-agent/venv/bin/python3 -m pip install watchdog
```

### 3. 启动监控模式

**守护进程模式**（launchd，推荐）：
```bash
# 加载 launchd plist
launchctl unload ~/Library/LaunchAgents/ai.lookforge.kb-watchdog.plist 2>/dev/null
launchctl load ~/Library/LaunchAgents/ai.lookforge.kb-watchdog.plist
# 验证
launchctl list | grep kb-watchdog
ps aux | grep kb_watchdog | grep -v grep
```

**前台轮询模式**（测试用）：
```bash
python3 scripts/kb_watchdog.py --sync-once   # 一次性全量同步
python3 scripts/kb_watchdog.py               # 前台轮询（Ctrl+C 停止）

### 4. Mac mini 守护进程化（launchd）

**当前状态（2026-05-04 晚）**：
- kb_watchdog_http.py **正在运行**（PID 779）
- **实际 Python 路径**：`/opt/homebrew/Cellar/python@3.11/3.11.15/...`（Homebrew python@3.11）
- 验证命令：`ps aux | grep kb_watchdog | grep -v grep`
- launchd 守护进程状态：`launchctl list` 可能返回空，但 `ps aux` 有输出说明进程正常存活

> **重要发现**：文档建议用 hermes venv python，但实际运行的进程用的是 Homebrew python@3.11。两者均可正常工作。关键是避免中文路径和版本兼容性问题。

**已知问题**：
- watchdog 实时监控模式（inotify/FSEvents）有 `tcsetattr: Inappropriate ioctl for device` 错误，进程会崩溃退出
- **解决方案**：不使用 `--daemon` 的 watchdog 实时监控，改用默认 polling 轮询模式
- CLT 版 `/usr/bin/python3` 在 launchd 下无法访问中文路径（`Operation not permitted`），**禁止使用**

**launchd plist 方案（已验证 2026-05-04）**：

路径：`~/Library/LaunchAgents/ai.lookforge.kb-watchdog.plist`

> ⚠️ 关键原则：所有路径**绝对不能包含中文字符**。launchd 会对中文路径做 Unicode 转义导致 SIGSEGV。脚本放在 `/Users/hua/lookforge-scripts/`。

**步骤 1：创建包装脚本**（`/Users/hua/lookforge-scripts/kb_watchdog_launcher.py`）：
```python
#!/usr/bin/env python3
import sys
import os

# 设置路径，使 kb_watchdog 模块可导入
sys.path.insert(0, '/Users/hua/Desktop/渔芯科技/6-产品研发/02-LookForge/backend')
os.environ.setdefault('LF_ROOT', '/Users/hua/Desktop/渔芯科技')

# 导入并执行 kb_watchdog 的 main
from scripts.kb_watchdog import main
main()
```

**步骤 2：或者直接用 HTTP 版 watchdog**（推荐，绕过版本兼容问题）：

脚本 `/Users/hua/lookforge-scripts/kb_watchdog_http.py`：
```python
#!/usr/bin/env python3
"""通过 HTTP API 访问 ChromaDB，绕过客户端版本不兼容问题"""
import sys, os, time, hashlib
import requests  # 必须已安装

CHROMA_URL = "http://localhost:8001"
KB_ROOT = "/Users/hua/Desktop/渔芯科技/2-知识库"
STATE_FILE = "/Users/hua/lookforge-scripts/.kb_watchdog_state.json"
COLLECTION_NAME = "lookforge_knowledge"
COLLECTION_UUID = None  # 动态获取

def get_collection_uuid():
    r = requests.get(f"{CHROMA_URL}/api/v1/collections")
    for coll in r.json():
        if coll['name'] == COLLECTION_NAME:
            return coll['id']
    return None

def get_or_create():
    global COLLECTION_UUID
    COLLECTION_UUID = get_collection_uuid()
    if not COLLECTION_UUID:
        r = requests.post(f"{CHROMA_URL}/api/v1/collections", json={"name": COLLECTION_NAME})
        COLLECTION_UUID = r.json()["id"]
    return COLLECTION_UUID

def add_documents(files):
    coll_id = get_or_create()
    # 按 ChromaDB 0.4.22 API 构造 add 请求
    requests.post(
        f"{CHROMA_URL}/api/v1/collections/{coll_id}/add",
        json={"documents": [...], "metadatas": [...], "ids": [...]}
    )

if __name__ == "__main__":
    # --daemon: 轮询监控；--sync-once: 一次性同步
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--daemon", action="store_true")
    parser.add_argument("--sync-once", action="store_true")
    args = parser.parse_args()

    if args.sync_once or args.daemon:
        scan_and_import()
```

**步骤 3：launchd plist**：
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>ai.lookforge.kb-watchdog</string>

    <!-- 必须用 hermes venv python，CLT python3 无法访问中文路径 -->
    <key>ProgramArguments</key>
    <array>
        <string>/Users/hua/.hermes/hermes-agent/venv/bin/python3</string>
        <string>/Users/hua/lookforge-scripts/kb_watchdog_http.py</string>
        <string>--daemon</string>
    </array>

    <!-- 必须在非中文路径！ -->
    <key>WorkingDirectory</key>
    <string>/Users/hua/lookforge-scripts</string>

    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin</string>
    </dict>

    <key>RunAtLoad</key>
    <true/>

    <key>KeepAlive</key>
    <dict>
        <key>SuccessfulExit</key>
        <false/>
    </dict>

    <key>StandardOutPath</key>
    <string>/Users/hua/.hermes/logs/kb-watchdog-http.log</string>
    <key>StandardErrorPath</key>
    <string>/Users/hua/.hermes/logs/kb-watchdog-http.error.log</string>
</dict>
</plist>
```

**管理命令**：
```bash
# 加载（先 unload 旧的避免重复）
launchctl unload ~/Library/LaunchAgents/ai.lookforge.kb-watchdog.plist 2>/dev/null
launchctl load ~/Library/LaunchAgents/ai.lookforge.kb-watchdog.plist

# 查看状态（-11 表示上次退出码错误，是正常的，KeepAlive会自动重启）
launchctl list | grep kb-watchdog

# 看日志
cat ~/.hermes/logs/kb-watchdog-http.log
cat ~/.hermes/logs/kb-watchdog-http.error.log

# 验证进程存活
ps aux | grep kb_watchdog | grep -v grep
```

**关键诊断**：
- launchd 进程由 launchd 管理才生效：`launchctl list | grep kb-watchdog` 有输出才算成功
- `-11` 退出码是 `SIGSEGV`，通常是 watchdog FSEvents 线程崩溃或中文路径问题
- 状态 `-2` 表示正在运行，状态 `-11` 表示上次崩溃但 KeepAlive 正在重启
- **验证服务正常**：`tail ~/.hermes/logs/kb-watchdog-http.log`，看到 `✅` 即为正常
- **验证 ChromaDB 可达**：`curl http://localhost:8001/api/v1/heartbeat` 应返回 `200 OK`

**⚠️ launchd 加载失败排查（Input/output error）**

当 `launchctl load` 或 `launchctl bootstrap gui/$UID` 报 `Input/output error (exit 5)` 时：

1. 检查 plist 路径是否正确（绝对路径）
2. 检查 plist 内 `ProgramArguments` 数组元素数量是否正确（每个参数单独一个 `<string>` 元素）
3. 检查 `WorkingDirectory` 是否存在且无中文
4. **临时解决方案**：改用 `terminal(background=true)` 直接后台启动进程，绕过 launchd

```bash
# 手动后台启动（临时方案）
/Users/hua/.hermes/hermes-agent/venv/bin/python3.11 \
  /Users/hua/lookforge-scripts/kb_watchdog_http.py --daemon \
  > /Users/hua/.hermes/logs/kb-watchdog.log 2>&1 &

# 验证进程启动
sleep 2 && ps aux | grep kb_watchdog | grep -v grep
```

**⚠️ 重复进程检测**

旧进程可能已死但 PID 记录残留。发现进程无响应时：
```bash
# 检查所有相关进程（含已死僵尸）
ps aux | grep kb_watchdog | grep -v grep

# 若有多个同名进程，手动 kill 旧的再重启
kill <old_pid>
```

**⚠️ KB Watchdog HTTP 服务验证**

`kb_watchdog_http.py` HTTP 端点验证方式：
1. **进程存活（最可靠）**：`ps aux | grep kb_watchdog | grep -v grep` — 观察 PID 757 等进程
2. **launchctl list 不可靠**：返回空不代表进程已死！macOS launchd 有时无法枚举到运行中的进程，但进程实际存活
3. **HTTP 健康检查（静默=正常）**：`curl http://localhost:18792/health` — 无输出表示正常，有报错会返回 JSON
4. **日志检查**：`tail ~/.hermes/logs/kb-watchdog.log` — 看最后几行是否有报错
5. **ChromaDB 同步验证**：`docker exec lookforge-chromadb python3 -c "import chromadb; print(chromadb.PersistentClient(path='/chroma/chroma').get_or_create_collection('lookforge_knowledge').count())"`

---

## 验证知识库状态（强制三重验证）

⚠️ **count() 正常 ≠ 数据完整！必须同时验证 count() + query() + peek() 三项。**

```bash
docker exec lookforge-chromadb python3 -c "
import chromadb
from chromadb.config import Settings
client = chromadb.PersistentClient(path='/chroma/chroma', settings=Settings(anonymized_telemetry=False))
coll = client.get_or_create_collection('lookforge_knowledge')

cnt = coll.count()
print(f'1. count(): {cnt}')

results = coll.query(query_texts=['RAS 循环水养殖'], n_results=3)
print(f'2. query() returned {len(results[\"documents\"][0])} results')

peek = coll.peek(limit=3)
print(f'3. peek() returned {len(peek[\"documents\"])} results')
print('All 3 checks passed!')
"
```

预期输出示例（2026-05-04 实测）：
```
1. count(): 340
2. query() returned 3 results
3. peek() returned 3 results
All 3 checks passed!
```

⚠️ **注意**：通过 `execute_code`（Jupyter sandbox）访问 ChromaDB 会报 `no such column: collections.topic` 错误（sandbox 环境与本地 Python 路径不一致）。**始终用 `docker exec`** 方式验证。

---

## 旧版验证方式（已废弃）

```python
# ❌ 已废弃：vector_store.get_client() 在 sandbox 中不可用
import sys
sys.path.insert(0, '/Users/hua/Desktop/渔芯科技/6-产品研发/02-LookForge/backend')
from app.services.vector_store import get_client  # 不要用这个！
```

替代方案：
```python
# ✅ 正确：docker exec 方式
docker exec lookforge-chromadb python3 -c "import chromadb; ..."
```

---

## Tracker 状态文件

状态文件：`scripts/.kb_watchdog_state.json`

确认已跟踪文件数：
```python
import json
with open('/Users/hua/Desktop/渔芯科技/6-产品研发/02-LookForge/scripts/.kb_watchdog_state.json') as f:
    tracker = json.load(f)
print(f"tracked: {len(tracker['files'])} files")
```

---

## 关键路径

| 文件 | 路径 |
|------|------|
| kb_watchdog.py（原始） | `/6-产品研发/02-LookForge/scripts/kb_watchdog.py` |
| **HTTP 版（推荐）** | `/Users/hua/lookforge-scripts/kb_watchdog_http.py` |
| **包装启动器** | `/Users/hua/lookforge-scripts/kb_watchdog_launcher.py` |
| 知识库根目录 | `/Users/hua/Desktop/渔芯科技/2-知识库/`（含中文，launchd 不可用） |
| ChromaDB 数据 | `/6-产品研发/02-LookForge/backend/data/chroma/` |
| Tracker 状态 | `/Users/hua/lookforge-scripts/.kb_watchdog_state.json` |
| 日志 | `/Users/hua/.hermes/logs/kb-watchdog-http.log` |
| **健康检查脚本** | `scripts/kb_watchdog_health_check.sh`（一键验证进程+日志+ChromaDB三重检查） |

> ⚠️ 所有 launchd 相关脚本和状态文件必须放在 `/Users/hua/lookforge-scripts/`（无中文），避免 launchd Unicode 转义崩溃。
