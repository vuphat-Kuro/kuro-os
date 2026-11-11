@echo off
cd /d "%~dp0"
title Kuro OS
echo ========================================================
echo   KURO OS - TRO LY KY SU HA TANG (WINDOWS DESKTOP APP)
echo ========================================================
echo Dang khoi dong ung dung Kuro OS...
.venv\Scripts\python.exe app_desktop.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Phat hien loi khi khoi chay Desktop App, chuyen sang che do Web...
    start "" http://127.0.0.1:7788
    .venv\Scripts\python.exe server\main.py
    pause
)
