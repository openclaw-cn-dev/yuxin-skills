# AutoHotkey + RAG 桌面集成实战（2026-06-10 验证）

## 适用场景

老大想按快捷键立刻查 RAG + 推 4 群 + 启停服务——**不用 DM 小弟**。

## 安装

```bash
choco install autohotkey -y
```

默认装在 `C:\Program Files\AutoHotkey\v2\`（v2.0.26）。

## 3 个全局快捷键

| 快捷键 | 功能 |
|---|---|
| **Ctrl+R** | 弹输入框 → 查 RAG → 弹结果 |
| **Ctrl+Shift+R** | 选群 → 输入问题 → 推到对应 4 群 |
| **Ctrl+Alt+R** | 启停 RAG watch 后台服务 |

## 主控脚本完整代码

见 `templates/ahk_rag_master.ahk`。**关键部分**：

```ahk
#Requires AutoHotkey v2.0
#SingleInstance Force
Persistent

; 启动 RAG watch 后台服务
Run('C:\Users\Administrator\AppData\Local\hermes\hermes-agent\venv\Scripts\pythonw.exe "C:\Users\Administrator\Desktop\知识库\feishu_rag_v2.py" --watch --interval 60', , "Hide")

; Ctrl+R - 一键查 RAG
^r:: {
    question := InputBox("请输入 RAG 查询问题:", "小弟 RAG 客服 (Ctrl+R)", "W500 H100")
    if question.Result != "OK" or question.Value = ""
        return
    RunWait('C:\Users\Administrator\AppData\Local\hermes\hermes-agent\venv\Scripts\pythonw.exe -u "C:\Users\Administrator\Desktop\知识库\rag_query_v2.py" "' question.Value '" > "C:\Users\Administrator\Desktop\知识库\last_rag.txt" 2>&1', , "Hide")
    result_text := FileRead("C:\Users\Administrator\Desktop\知识库\last_rag.txt")
    MsgBox("🔍 RAG 查询: " question.Value "`n`n" SubStr(result_text, 1, 2000), "小弟 RAG 结果")
}

; Ctrl+Shift+R - 4 群 RAG 推送
^+r:: {
    group_names := "🦐 美食社|🐟 养殖圈|⚙️ 设备库|🏢 上市公司"
    chosen := ComObjCreate("WScript.Shell").Popup(group_names, 0, "选群推送 RAG", 0x01+0x20)
    if chosen = 0
        return

    groups := Map(
        1, "oc_xxxxx_美食",
        2, "oc_xxxxx_养殖",
        3, "oc_xxxxx_设备",
        4, "oc_xxxxx_公司"
    )

    chat_id := groups[chosen]
    group_name := ["", "🦐 美食社", "🐟 养殖圈", "⚙️ 设备库", "🏢 上市公司"][chosen]

    question := InputBox("要推 " group_name " 的问题:", "4 群 RAG 推送 (Ctrl+Shift+R)", "W500 H100")
    if question.Result != "OK" or question.Value = ""
        return

    RunWait('C:\...\venv\Scripts\pythonw.exe -u "C:\...\rag_query_v2.py" "' question.Value '" > "C:\...\last_rag.txt" 2>&1', , "Hide")
    result_text := FileRead("C:\...\last_rag.txt")

    msg := "🔍 RAG 查询: " question.Value "`n`n" SubStr(result_text, 1, 1500)
    RunWait('hermes send feishu ' chat_id ' --message "' msg '"', , "Hide")

    MsgBox("✅ 已推 " group_name "`n`n问题: " question.Value, "推送成功")
}

; Ctrl+Alt+R - 启停 RAG watch 服务
^!r:: {
    static running := false
    if !running {
        Run('C:\...\venv\Scripts\pythonw.exe "C:\...\feishu_rag_v2.py" --watch --interval 60', , "Hide")
        running := true
        TrayTip "🟢 RAG 服务启动", "watch 模式已开", 1
    } else {
        RunWait("taskkill /F /IM pythonw.exe 2>nul", , "Hide")
        running := false
        TrayTip "🔴 RAG 服务停止", "watch 模式已关", 1
    }
}
```

## 开机自启

把启动器 `.ahk` 放 `%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\`：

```ahk
#Requires AutoHotkey v2.0
Run('"C:\Program Files\AutoHotkey\v2\AutoHotkey64.exe" "C:\Users\Administrator\Desktop\知识库\ahk_rag_master.ahk"', , "Hide")
ExitApp
```

重启电脑后自动跑 RAG 服务 + 快捷键激活。

## 重要警告

### 1. AHK v2 语法

- 用 `#Requires AutoHotkey v2.0`
- 用 `::` 块语法（**v1 已不兼容**）
- v2 默认装在 `C:\Program Files\AutoHotkey\v2\`

### 2. pythonw.exe vs python.exe

- **后台服务用 `pythonw.exe`**（**无窗口**）
- **前台调用用 `python.exe`**

### 3. hermes 进程冲突

- ahk 跑 pythonw.exe 后，hermes 跑 python 脚本会抢 bge 模型
- **避免同时跑**——按需启停（**Ctrl+Alt+R**）

### 4. bge 模型锁

- pythonw.exe 占着 bge 时，hermes 跑 RAG 查询会被卡 60s+
- **解决**：用 Ctrl+Alt+R 停 watch 服务，再让 hermes 跑查询

## 验证清单

跑通后必跑：

```bash
# 1. AHK 主控进程
tasklist | findstr AutoHotkey64

# 2. pythonw.exe watch 服务
tasklist | findstr pythonw

# 3. RAG 库健康
cd "C:\Users\Administrator\Desktop\知识库"
"C:/.../venv/Scripts/python.exe" -c "
import os
os.environ['HF_HOME']='C:/Users/Administrator/.cache/huggingface'
import chromadb
from pathlib import Path
c = chromadb.PersistentClient(path=r'C:\Users\Administrator\Desktop\知识库\chroma_db')
co = c.get_collection('langchain')
print(f'chunks: {co.count()}')
"
```

期望：chunks > 50 = 健康

## 关联资源

- `templates/ahk_rag_master.ahk` —— 主控脚本完整版
- `references/feishu-bot-deployment/feishu-23002-troubleshooting.md` —— 飞书推送错误排查
- `chinese-rag-pipeline` skill —— RAG 索引/查询/健康检查
