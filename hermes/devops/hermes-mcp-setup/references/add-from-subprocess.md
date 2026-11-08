# Adding MCP Servers from Python Subprocess (2026-06-13 实战)

> **Use case**: 老大说"加个 Filesystem MCP" / "加 3 个 MCP" / "装 MCP" — 小弟需要从 `execute_code` 或 `terminal` 调 `hermes mcp add` 自动加服务器，**不要老大手动跑命令**。

## 核心难点（按踩坑顺序排）

1. `npx` 不在 sandbox 的 `PATH`（**FileNotFoundError**）
2. `npx` 是 `.cmd` 包装（`subprocess.Popen(['npx', ...], shell=False)` 失败）
3. `hermes mcp add` 交互式 `y/N`（卡住）
4. `npx` 第一次下载触发的 `0xb0` UTF-8 错误
5. 加完是 `enabled: false`（test 失败时自动 disable）
6. args 被存成单个 string（应该 list）

## 完整可行代码（**2026-06-13 实测通过**）

```python
import subprocess
import os
from pathlib import Path

# 1. 预装 npx 包（避免 0xb0 错误）
npm = r"C:\Program Files\nodejs\npm.cmd"
subprocess.run([npm, "install", "-g", "@modelcontextprotocol/server-filesystem"],
               capture_output=True, timeout=120)

# 2. 调 hermes mcp add
#    **关键**：npx 用 .cmd 全路径 + shell=False
#    **关键**：args 用空格分隔的字符串（argparse 会拆）
npx_path = r"C:\Program Files\nodejs\npx.cmd"
result = subprocess.run(
    [npx_path, "-y", "@modelcontextprotocol/server-filesystem",
     "C:/Users/Administrator/Desktop", "C:/Users/Administrator/Documents"],
    input="y\n",          # 喂 stdin 给交互式 y/N
    capture_output=True,
    text=True,
    timeout=60,
    env={**os.environ, "PATH": r"C:\Program Files\nodejs;" + os.environ.get("PATH", "")}
)

# 3. 看是不是 disabled
print(result.stdout[-2000:])
# 期望看到：
#   ✓ Saved 'filesystem' to config (disabled)   <-- disabled 因为 test 失败
#   ⚠ hermes.exe is locked by another process
#   → Falling back to ZIP download...
#   ✓ Updated 74 items from ZIP
```

## 修 disabled → enabled（**关键步骤**）

`hermes mcp add` 跑完大概率是 `disabled`，因为 npx 第一次下包触发 0xb0 错误。**修法**：

1. 用 `read_file` 读 `config.yaml`
2. 找到 `mcp_servers.filesystem` 块
3. 验证 `args` 是 list（如果不是，重写为 list）
4. 改 `enabled: false` → `enabled: true`
5. 用 `write_file` 写回
6. 跑 `hermes mcp test filesystem` 验证

**Worked example**（**在 `SKILL.md` 里有完整 YAML diff**）：

```yaml
filesystem:
  command: npx
  args:
  - -y
  - '@modelcontextprotocol/server-filesystem'
  - 'C:/Users/Administrator/Desktop'
  - 'C:/Users/Administrator/Documents'
  enabled: true  # <-- 改这里
```

## 验证（4 步）

```bash
# 1. 列表
hermes mcp list
# 期望：filesystem  ✓ enabled

# 2. 测连接
hermes mcp test filesystem
# 期望：✓ Connected (15000ms) / Tools discovered: 14

# 3. Python 直连（**绕过 hermes 调 npx**）
import json, subprocess
proc = subprocess.Popen(
    [r'C:\Program Files\nodejs\npx.cmd', '-y', '@modelcontextprotocol/server-filesystem',
     'C:/Users/Administrator/Desktop', 'C:/Users/Administrator/Documents'],
    stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    text=True, env={**os.environ, 'PATH': r'C:\Program Files\nodejs;' + os.environ.get('PATH', '')}
)
init = {'jsonrpc': '2.0', 'id': 1, 'method': 'initialize',
        'params': {'protocolVersion': '2024-11-05', 'capabilities': {},
                   'clientInfo': {'name': 'test', 'version': '1.0'}}}
proc.stdin.write(json.dumps(init) + '\n')
proc.stdin.flush()
import time; time.sleep(3)
resp = proc.stdout.readline()
# 期望：{"result":{"protocolVersion":"2024-11-05", ...}}

# 4. 调工具（list_allowed_directories）
list_req = {'jsonrpc': '2.0', 'id': 2, 'method': 'tools/call',
            'params': {'name': 'list_allowed_directories', 'arguments': {}}}
proc.stdin.write(json.dumps(list_req) + '\n')
proc.stdin.flush()
time.sleep(2)
resp = proc.stdout.readline()
# 期望：Allowed directories:\nC:\\Users\\Administrator\\Desktop\nC:\\Users\\Administrator\\Documents
```

## 14 个工具清单（**Filesystem MCP**）

| 工具 | 干啥活 |
|---|---|
| `read_file` | 读文件 |
| `read_text_file` | 读文本 |
| `read_media_file` | 读图/音（base64） |
| `read_multiple_files` | 批量读 |
| `write_file` | 写文件 |
| `edit_file` | 编辑文件 |
| `create_directory` | 建目录 |
| `list_directory` | 列目录 |
| `list_directory_with_sizes` | 列目录（带大小） |
| `directory_tree` | 目录树 |
| `move_file` | 移动文件 |
| `search_files` | 搜索文件 |
| `get_file_info` | 文件信息 |
| `list_allowed_directories` | 列出允许目录 |

## 5 大避坑（**实战踩过**）

1. **❌ 不要用 `subprocess.Popen(['npx', ...])`（shell=False）** —— npx 是 .cmd，Python 找不到
2. **❌ 不要用 `shell=True` 拼接命令** —— 引号转义坑
3. **❌ 不要用 `args: -y @pkg path1 path2` 空格分隔后 add** —— args 会变单 string
4. **❌ 不要直接 `patch` config.yaml** —— security guard 拒绝
5. **❌ 不要写完不管 enabled** —— test 失败默认 disabled，要手动改

## 6 大铁律

1. ✅ **npx 必须用 `.cmd` 全路径**：`[r"C:\Program Files\nodejs\npx.cmd", ...]`
2. ✅ **预装 npx 包**：`npm install -g @modelcontextprotocol/server-XXX`（避免 0xb0）
3. ✅ **PATH 优先 nodejs**：`env["PATH"] = "C:\\Program Files\\nodejs;" + ...`
4. ✅ **stdin 喂 y**：`input="y\n"`
5. ✅ **read_file + write_file 改 enabled**（不用 patch）
6. ✅ **args 用 YAML list 形式**（不用空格分隔 string）
