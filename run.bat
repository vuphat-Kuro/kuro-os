@echo off
cd /d "%~dp0"
start "" http://127.0.0.1:7788
.venv\Scripts\python server\main.py
pause
