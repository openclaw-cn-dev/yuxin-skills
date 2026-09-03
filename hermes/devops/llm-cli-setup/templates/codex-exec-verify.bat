@echo off
REM ============================================================
REM  Codex CLI 0.42 最小对话验收 (接第三方 OpenAI 兼容中转)
REM  适用:任何接中转场景,把 MINIMAX_API_KEY / minimax / MiniMax-M3 三个值换掉即可
REM  双击运行,4 步:版本→key 校验→DNS 验→exec 最小对话
REM
REM  关键设计:
REM  - 用 `if not defined` 判 User 级 env,**不要**用 set "X=占位符"再判断(会覆盖)
REM  - 脱敏用 %SK:~0,8% / %SK:~-4%,不显示完整 key
REM  - codex exec 走本进程 env,新开 cmd 后 batch 自动继承 User 级 env
REM ============================================================

chcp 65001 >nul

echo === [1/4] codex 版本 (期望 0.42.x) ===
codex --version
if errorlevel 1 (
  echo !! codex 没装好,跑: npm install -g @openai/codex@0.42.0
  pause
  exit /b 1
)

echo.
echo === [2/4] 校验 User 级 MINIMAX_API_KEY (脱敏显示) ===
REM --- 关键:用 if not defined 检查,绝不能用 set "X=占位符" 再 ==
if not defined MINIMAX_API_KEY (
  echo !! MINIMAX_API_KEY 没设,跑:
  echo    powershell -Command "[Environment]::SetEnvironmentVariable('MINIMAX_API_KEY','你的sk','User')"
  echo    然后【新开一个 cmd】再双击这个 bat
  pause
  exit /b 1
)
echo Key 前 8: %MINIMAX_API_KEY:~0,8%... 后 4: %MINIMAX_API_KEY:~-4%

echo.
echo === [3/4] DNS 验 base_url ===
curl -sS -o nul -w "api.minimaxi.com -> HTTP %%{http_code} (%%{time_total}s)^n" --max-time 8 https://api.minimaxi.com/

echo.
echo === [4/4] 非交互 exec 最小对话 (--skip-git-repo-check 防桌面拒跑) ===
codex exec --skip-git-repo-check -m "MiniMax-M3" -c model_provider="minimax" "say 'hello from minimax' and exit"
if errorlevel 1 (
  echo.
  echo !! exec 失败,把上面报错贴回给小弟
  pause
  exit /b 1
)

echo.
echo === 完成,看到模型回了一句话才算通 ===
pause
