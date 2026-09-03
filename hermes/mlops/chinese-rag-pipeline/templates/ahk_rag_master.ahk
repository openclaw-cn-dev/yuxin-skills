#Requires AutoHotkey v2.0
; ============================================================================
; 🐟 小弟 RAG 快捷键主控脚本（完整版）
; 开机自启 + 3 个全局快捷键
; 用法: 双击运行 / 放 %APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\
; ============================================================================

#SingleInstance Force
Persistent

; 启动 RAG watch 后台服务
Run('C:\Users\Administrator\AppData\Local\hermes\hermes-agent\venv\Scripts\pythonw.exe "C:\Users\Administrator\Desktop\知识库\feishu_rag_v2.py" --watch --interval 60', , "Hide")

; ----------------------------------------------------------------------------
; 快捷键 1: Ctrl+R - 一键查 RAG
; ----------------------------------------------------------------------------
^r:: {
    question := InputBox("请输入 RAG 查询问题:", "小弟 RAG 客服 (Ctrl+R)", "W500 H100")
    if question.Result != "OK" or question.Value = ""
        return

    ; 写查询到文件 → python 跑 → 读结果
    RunWait('C:\Users\Administrator\AppData\Local\hermes\hermes-agent\venv\Scripts\pythonw.exe -u "C:\Users\Administrator\Desktop\知识库\rag_query_v2.py" "' question.Value '" > "C:\Users\Administrator\Desktop\知识库\last_rag.txt" 2>&1', , "Hide")

    result_text := FileRead("C:\Users\Administrator\Desktop\知识库\last_rag.txt")
    MsgBox("🔍 RAG 查询: " question.Value "`n`n" SubStr(result_text, 1, 2000), "小弟 RAG 结果")
}

; ----------------------------------------------------------------------------
; 快捷键 2: Ctrl+Shift+R - 4 群 RAG 推送
; ----------------------------------------------------------------------------
^+r:: {
    ; 选群
    group_names := "🦐 美食社|🐟 养殖圈|⚙️ 设备库|🏢 上市公司"
    chosen := ComObjCreate("WScript.Shell").Popup(group_names, 0, "选群推送 RAG", 0x01+0x20)
    if chosen = 0
        return

    groups := Map(
        1, "oc_c1bf60f8d03aefcbcb18f595e7ef4e19",  ; 美食
        2, "oc_4acad97e312c37674630da282d76ab4b",  ; 养殖
        3, "oc_ffaa900080df1c6ddeb7b8107948f013",  ; 设备
        4, "oc_c7cf3d684575b89aa290b849e6508fc8"   ; 公司
    )

    chat_id := groups[chosen]
    group_name := ["", "🦐 美食社", "🐟 养殖圈", "⚙️ 设备库", "🏢 上市公司"][chosen]

    question := InputBox("要推 " group_name " 的问题:", "4 群 RAG 推送 (Ctrl+Shift+R)", "W500 H100")
    if question.Result != "OK" or question.Value = ""
        return

    ; 查 RAG
    RunWait('C:\Users\Administrator\AppData\Local\hermes\hermes-agent\venv\Scripts\pythonw.exe -u "C:\Users\Administrator\Desktop\知识库\rag_query_v2.py" "' question.Value '" > "C:\Users\Administrator\Desktop\知识库\last_rag.txt" 2>&1', , "Hide")
    result_text := FileRead("C:\Users\Administrator\Desktop\知识库\last_rag.txt")

    ; 推飞书
    msg := "🔍 RAG 查询: " question.Value "`n`n" SubStr(result_text, 1, 1500)
    RunWait('hermes send feishu ' chat_id ' --message "' msg '"', , "Hide")

    MsgBox("✅ 已推 " group_name "`n`n问题: " question.Value, "推送成功")
}

; ----------------------------------------------------------------------------
; 快捷键 3: Ctrl+Alt+R - 启停 RAG 服务
; ----------------------------------------------------------------------------
^!r:: {
    static running := false
    if !running {
        Run('C:\Users\Administrator\AppData\Local\hermes\hermes-agent\venv\Scripts\pythonw.exe "C:\Users\Administrator\Desktop\知识库\feishu_rag_v2.py" --watch --interval 60', , "Hide")
        running := true
        TrayTip "🟢 RAG 服务启动", "watch 模式已开", 1
    } else {
        RunWait("taskkill /F /IM pythonw.exe 2>nul", , "Hide")
        running := false
        TrayTip "🔴 RAG 服务停止", "watch 模式已关", 1
    }
}

; ----------------------------------------------------------------------------
; 启动提示
; ----------------------------------------------------------------------------
TrayTip "🐟 小弟 RAG 服务", "已启动 + 开机自启`n`n快捷键:`n• Ctrl+R 查 RAG`n• Ctrl+Shift+R 推 4 群`n• Ctrl+Alt+R 启停服务", 3
SoundBeep 1500, 100
SoundBeep 2000, 100
