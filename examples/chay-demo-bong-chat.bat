@echo off
cd /d "%~dp0\.."
if exist ".venv\Scripts\pythonw.exe" (
    start "" ".venv\Scripts\pythonw.exe" "examples\demo_floating_chat.py"
) else (
    ".venv\Scripts\python.exe" "examples\demo_floating_chat.py"
)
