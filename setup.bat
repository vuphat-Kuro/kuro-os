@echo off
REM Cai Kuro OS mot lan: venv Python 3.13, thu vien, file .env
cd /d "%~dp0"
where claude >nul 2>&1 || (echo [LOI] Chua co Claude Code. Chay: npm install -g @anthropic-ai/claude-code & pause & exit /b 1)
if not exist ".venv" (
  py -3.13 -m venv .venv || py -3.12 -m venv .venv || (echo [LOI] Can Python 3.12 hoac 3.13 & pause & exit /b 1)
)
.venv\Scripts\python -m pip install -q -r requirements.txt -r requirements-ky-thuat.txt || (echo [LOI] pip install that bai & pause & exit /b 1)
if not exist ".env" copy env.example .env >nul
echo.
echo Xong. Neu chua dang nhap Claude thi chay: claude auth login
echo Chay Kuro: run.bat
pause
