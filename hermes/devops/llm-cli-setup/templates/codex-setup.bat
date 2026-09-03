@echo off
chcp 65001 > nul
setlocal EnableDelayedExpansion

REM ============================================================
REM  Codex CLI 端到端验收脚本 — 双击跑 4 步
REM  1) 验 codex 装好
REM  2) 读 User env 里的 MINIMAX_API_KEY(脱敏显示)
REM  3) 注入本进程 env(batch 不继承 User 级)
REM  4) codex exec 非交互跑最小对话(MiniMax-Text-01 真模型回复 = 通)
REM ============================================================

REM 1) 读 User 级 env
for /f "tokens=*" %%k in ('powershell -NoProfile -Command "[System.Environment]::GetEnvironmentVariable('MINIMAX_API_KEY','User')"') do set "SK=%%k"

echo.
echo === [1/4] codex 版本 ===
codex --version
if errorlevel 1 (
  echo !! codex 没装好,先跑: npm install -g @openai/codex@0.42.0
  pause & exit /b 1
)

echo.
echo === [2/4] 校验 MINIMAX_API_KEY (脱敏显示) ===
if "%SK%"=="" (
  echo !! MINIMAX_API_KEY 没设,先跑:
  echo    powershell -Command "[System.Environment]::SetEnvironmentVariable('MINIMAX_API_KEY','你的sk','User')"
  pause & exit /b 1
)
if "%SK%"=="__PUT_YOUR_MINIMAX_SK_HERE__" (
  echo !! MINIMAX_API_KEY 还是占位符,没换成真 key
  pause & exit /b 1
)
echo Key 前 8: %SK:~0,8%... 后 4: %SK:~-4%

echo.
echo === [3/4] 把 key 注入本 batch 进程 env ===
set "MINIMAX_API_KEY=*** echo env 已就位

echo.
echo === [4/4] 最小对话测试 (codex exec 非交互) ===
codex exec --skip-git-repo-check -m "MiniMax-Text-01" -c model_provider="minimax" "say_hi"
if errorlevel 1 (
  echo !! exec 失败,把上面报错贴给小弟
  pause & exit /b 1
)

echo.
echo === 全部通过 ===
pause
