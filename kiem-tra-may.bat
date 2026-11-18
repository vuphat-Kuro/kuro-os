@echo off
REM Chi kiem tra may da du Python, Node.js, Git, Claude CLI, Antigravity CLI... chua. Khong cai gi.
chcp 65001 >nul
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0cai-dat-tu-dong.ps1" -ChiKiemTra
echo.
pause
