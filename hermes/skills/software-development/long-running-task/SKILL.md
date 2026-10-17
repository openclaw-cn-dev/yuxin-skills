---
name: long-running-task
description: 处理长时间执行的任务（3 分钟以上）。当用户下达的任务可能耗时超过 2 分钟，Hermes 出现 timeout，或者需要后台静默执行时使用。包含：Hermes terminal tool 的 background+notify_on_complete 模式、timeout 参数调优（180→300+）、asyncio subprocess shell 后台进程模板、nohup 独立进程模式。必须用本 skill 的任务类型：大型编译/测试、多步安装、批量文件处理、远程下载、长时间多步骤 agent 任务。
---

# Long-Running Task Handler

## 适用场景

Hermes Agent 的 terminal 默认 timeout=180 秒，delegate_task 受父会话迭代限制。当用户下达以下类型任务时**必须使用本 skill**：

- 大型代码重构 / 编译 / 测试全量运行（>2分钟）
- 多步骤安装（brew install、pip install large packages）
- 批量文件处理（>50 个文件）
- 远程数据下载/API 批量请求
- 长时间代理任务（飞书群消息批量发送等）

## 核心模式：三步走

### 第一步：预估耗时

```python
# 快速预检任务规模
import os, subprocess
lines = subprocess.run(['wc', '-l', 'target/file.py'], capture_output=True, text=True)
# 如果是大型任务，直接进"异步执行"模式
```

### 第二步：异步执行（不阻塞当前会话）

```python
# 模式 A：terminal background + notify_on_complete
result = terminal(
    command="hermes chat -q '你的任务描述'",
    timeout=600,  # 前台最大600
    background=True,
    notify_on_complete=True
)

# 模式 B：长命令直接 background
result = terminal(
    command="python3 huge_script.py && echo DONE",
    timeout=600,
    background=True,
    notify_on_complete=True
)

# 模式 C：设置 watch_patterns 实时看进度
result = terminal(
    command="python3 build_script.py",
    background=True,
    watch_patterns=["Step", "Progress", "Complete"]
)
```

### 第三步：超时重试

```python
# 如果 terminal timeout 了，用 subprocess 跑更长时间
import asyncio, subprocess
process = await asyncio.create_subprocess_shell(
    command,
    stdout=asyncio.subprocess.PIPE,
    stderr=asyncio.subprocess.PIPE,
)
try:
    stdout, stderr = await asyncio.wait_for(
        process.communicate(), timeout=900  # 15分钟
    )
except asyncio.TimeoutError:
    process.kill()
    return {"error": "timeout", "partial_output": ...}
```

## 配置优化

当有长时间任务需求时，先检查并调优以下配置：

```bash
# 1. terminal timeout (默认180 → 调高到600)
hermes config set terminal.timeout 600

# 2. delegation max_iterations (默认50 → 调高)
hermes config set delegation.max_iterations 120

# 3. 如果常超时，加 Hermes 内置配置
hermes config set agent.max_tool_uses 999  # 已足够
hermes config set agent.max_messages 120   # 给更多轮次
```

## 进阶：Nohup 模式（真正独立进程）

Hermes 进程可能被杀，所以需要完全独立的进程：

```bash
nohup bash -c 'cd /path/to/proj && python3 script.py > /tmp/long_task.log 2>&1' &
echo "PID: $!"
```

然后定时轮询状态：
```bash
tail -5 /tmp/long_task.log
ps -p $PID -o pid,state,%cpu,%mem,etime
```

## 已知陷阱

1. **不要盲目调高 timeout**：600 秒是 foreground 上限，超过必须用 background
2. **background 模式必须设 notify_on_complete**：否则任务静默跑完后你不知道
3. **delegate_task 超时**：子 agent 默认 50 次迭代，如果任务太长它会自动停止——用 `terminal background` 代替
4. **不要在长时间任务中做复杂的上下文**：任务描述越精确越好，子 agent 没你的上下文历史

## 重启/中断后续接（Resume-after-restart，2026-09-04 验证）

华哥的 Mac 可能随时重启，长任务被腰斩后用户会说"继续刚才的任务"。标准续接流程：

1. **重建任务上下文**：`session_search(query=<上一条已发消息的特征词>, sort=newest)` 找到中断会话。锚点消息 + 周边工具调用记录能精确还原"做到哪一步"——不要凭记忆猜进度。
2. **盘点磁盘产物**：重启不丢文件。先 `ls`/读项目目录，已落盘的成品和半成品全部有效，不要重做。重点检查崩溃前正在写的那份文件是否完整（看结尾结构/时间戳）。
3. **进程归零认知**：重启后所有后台进程、codex exec、容器全部消失（`pgrep` 确认），不存在"接着跑"的后台任务——只有"重跑哪一步"的问题。
4. **定位断点 → 只补缺口**：对比"最后一条已交付消息承诺的下一步"与"磁盘上已有的产物"，差什么补什么。从任务起点重做会浪费 token 且可能覆盖已有成果。
5. **汇报结构**：先给"重启损失盘点"表（什么完好/什么断了）→ 已续上的部分 → 剩下需要用户拍板的决策点。让用户一眼看到零损失或明确损失。
