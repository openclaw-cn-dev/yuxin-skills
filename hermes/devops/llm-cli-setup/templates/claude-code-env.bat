@echo off
REM ============================================================
REM Claude Code 环境变量模板
REM 用途：让老大复制后改 4 处占位符，再双击运行（持久化到用户环境）
REM 安全：API Key 由老大自己填，小弟绝不过手
REM 用法：
REM   1) 复制本文件到 C:\Users\Administrator\claude-env.bat
REM   2) 用记事本改 4 个 YOUR_xxx 占位符
REM   3) 双击运行（新开终端后生效）
REM   4) cmd 里 echo %ANTHROPIC_API_KEY% 验证
REM ============================================================

REM --- [1] API Key（必填）---
REM 官方 Anthropic 格式：sk-ant-xxxxxxxx
REM 第三方中转格式：按平台说明，通常 sk- 开头
setx ANTHROPIC_API_KEY "YOUR_API_KEY_HERE"

REM --- [2] base URL（仅接中转时需要，官方留空或注释掉）---
REM 官方不要设这个变量！设了就走中转路径
REM setx ANTHROPIC_BASE_URL "https://api.your-provider.com"

REM --- [3] 中转认证 token（仅接中转时需要）---
REM 某些中转用 ANTHROPIC_AUTH_TOKEN 而不是 ANTHROPIC_API_KEY
REM setx ANTHROPIC_AUTH_TOKEN "YOUR_TOKEN_HERE"

REM --- [4] 模型名（仅接中转时需要，平台控制台查真实名）---
REM 官方不要设！用 claude 默认
REM setx ANTHROPIC_MODEL "claude-xxx"
REM setx ANTHROPIC_SMALL_FAST_MODEL "claude-xxx-haiku"

echo.
echo ============================================
echo  已设置完成，请【新开一个终端】后跑：
echo     claude --version
echo     claude -p "say hi"
echo ============================================
echo.
pause
