@echo off
REM Cai Kuro OS tu dong: kiem tra va cai Python, WebView2, Git, Node.js, Claude Code CLI, Antigravity CLI,
REM roi tao .venv, cai thu vien, .env va bieu tuong Desktop. Toan bo logic nam trong cai-dat-tu-dong.ps1.
REM Them tham so -Codex de cai ca Codex CLI (ChatGPT): setup.bat -Codex
chcp 65001 >nul
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0cai-dat-tu-dong.ps1" %*
if %errorlevel% neq 0 (
  echo.
  echo [LOI] Cai dat chua xong. Doc thong bao phia tren, sua xong chay lai setup.bat.
)
echo.
pause
