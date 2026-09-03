# AutoHotkey 桌面控制实战（Windows）

> 适用于：Windows 上想用快捷键触发命令/查 RAG/推飞书/启停服务

## 安装

```bash
# ✅ 推荐：chocolatey 装（自动管理员 + 静默）
choco install autohotkey -y
```

**位置**：`C:\Program Files\AutoHotkey\v2\`

**主程序**：
- v2：`C:\Program Files\AutoHotkey\v2\AutoHotkey64.exe`
- v2 UIA 版：`AutoHotkey64_UIA.exe`（支持 UI Automation）

## 踩坑记录

### 坑 1：`/S` 静默参数会卡 GUI

**症状**：
```bash
ahk-install.exe /S
# 卡 30 秒不退，进程残留
```

**原因**：AutoHotkey 安装器 `/S` 静默参数在 Windows 上行为不一致。

**解决**：
- ✅ **用 choco**（自动管理）—— **首选**
- ⚠️ 直接下 exe 双击手动装

### 坑 2：v1 和 v2 语法不兼容

**v1 语法**（**已过时**）：
```ahk
^r::
    MsgBox, Hello
    return
```

**v2 语法**（**当前标准**）：
```ahk
#Requires AutoHotkey v2.0
^r:: {
    MsgBox("Hello")
}
```

**关键差异**：
- 头加 `#Requires AutoHotkey v2.0`
- `::` 后面用 `{ ... }` 块
- 函数用 `MsgBox("text")` 不是 `MsgBox, text`
- **混用 v1 语法 = 跑不起来**

### 坑 3：pythonw.exe vs python.exe

| 场景 | 进程 |
|---|---|
| **后台服务**（无窗口）| `pythonw.exe` |
| **前台调试**（看输出）| `python.exe` |

```ahk
; 后台跑 RAG watch
Run('C:\...\venv\Scripts\pythonw.exe "C:\...\feishu_rag_v2.py" --watch', , "Hide")
```

## 3 个实战快捷键模板

### 1. 一键查 RAG（Ctrl+R）

```ahk
#Requires AutoHotkey v2.0
^r:: {
    question := InputBox("请输入 RAG 查询问题:", "小弟 RAG 客服 (Ctrl+R)", "W500 H100")
    if question.Result != "OK" or question.Value = ""
        return

    RunWait('C:\...\venv\Scripts\pythonw.exe -u "C:\...\rag_query_v2.py" "' question.Value '" > "C:\...\last_rag.txt" 2>&1', , "Hide")

    result_text := FileRead("C:\...\last_rag.txt")
    MsgBox("🔍 RAG 查询: " question.Value "`n`n" SubStr(result_text, 1, 2000), "小弟 RAG 结果")
}
```

### 2. 4 群 RAG 推送（Ctrl+Shift+R）

```ahk
#Requires AutoHotkey v2.0
^+r:: {
    chosen := ComObjCreate("WScript.Shell").Popup("🦐 美食社|🐟 养殖圈|⚙️ 设备库|🏢 上市公司", 0, "选群推送 RAG", 0x01+0x20)
    if chosen = 0
        return

    groups := Map(
        1, "oc_c1bf60f8d03aefcbcb18f595e7ef4e19",
        2, "oc_4acad97e312c37674630da282d76ab4b",
        3, "oc_ffaa900080df1c6ddeb7b8107948f013",
        4, "oc_c7cf3d684575b89aa290b849e6508fc8"
    )
    chat_id := groups[chosen]
    group_name := ["", "🦐 美食社", "🐟 养殖圈", "⚙️ 设备库", "🏢 上市公司"][chosen]

    question := InputBox("要推 " group_name " 的问题:", "4 群 RAG 推送 (Ctrl+Shift+R)", "W500 H100")
    if question.Result != "OK" or question.Value = ""
        return

    ; 查 RAG + 推飞书
    RunWait('C:\...\venv\Scripts\pythonw.exe -u "C:\...\rag_query_v2.py" "' question.Value '" > "C:\...\last_rag.txt" 2>&1', , "Hide")
    result_text := FileRead("C:\...\last_rag.txt")
    msg := "🔍 RAG 查询: " question.Value "`n`n" SubStr(result_text, 1, 1500)
    RunWait('hermes send feishu ' chat_id ' --message "' msg '"', , "Hide")

    MsgBox("✅ 已推 " group_name "`n`n问题: " question.Value, "推送成功")
}
```

### 3. 启停服务（Ctrl+Alt+R）

```ahk
#Requires AutoHotkey v2.0
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

**目标**：`%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\`

**创建启动器 .ahk**：
```ahk
#Requires AutoHotkey v2.0
#SingleInstance Force
Run('"C:\Program Files\AutoHotkey\v2\AutoHotkey64.exe" "C:\...\ahk_rag_master.ahk"', , "Hide")
ExitApp
```

**重启电脑后**：自动跑主控脚本 + 3 快捷键 + RAG 服务。

## 重要警告

- **hermes 进程冲突**：ahk 跑 pythonw.exe 后，hermes 跑 python 脚本会抢 bge 模型——**避免同时跑**
- **脚本调试**：用 `python.exe`（带窗口）→ 跑通改 `pythonw.exe`（无窗口）
- **快捷键冲突**：Ctrl+R 可能撞 IDE—— 改 Win+R / Alt+R
