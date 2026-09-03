@echo off
REM ============================================================
REM  启动 Codex CLI TUI — Windows 资源管理器双击入口
REM  委托给 启动codex.ps1(后者走 PowerShell API,不被 env 渲染坑吞)
REM  原因:.ps1 在 Windows 默认双击进记事本,必须 bat 入口
REM ============================================================
chcp 65001 > nul
powershell -NoProfile -ExecutionPolicy Bypass -File "C:\Users\Administrator\Desktop\启动codex.ps1"
if errorlevel 1 (
  echo.
  echo !! 启动失败,把上面报错贴给小弟
  pause
)
