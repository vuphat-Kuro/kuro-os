@echo off
REM Cai dat Kuro OS tu dong cho Windows: Tao venv Python, cai thu vien, tao shortcut Desktop
setlocal enabledelayedexpansion
chcp 65001 >nul
cd /d "%~dp0"

echo =====================================================================
echo          CÀI ĐẶT TỰ ĐỘNG TRỢ LÝ KỸ SƯ HẠ TẦNG - KURO OS
echo =====================================================================
echo.

echo [1/5] Kiểm tra môi trường Python trên máy...
set "PY_CMD="

REM Thu tim lenh py launcher
where /q py
if %errorlevel% equ 0 (
  py -3.13 --version >nul 2>&1 && set "PY_CMD=py -3.13"
  if not defined PY_CMD (py -3.12 --version >nul 2>&1 && set "PY_CMD=py -3.12")
  if not defined PY_CMD (py -3.11 --version >nul 2>&1 && set "PY_CMD=py -3.11")
  if not defined PY_CMD (py --version >nul 2>&1 && set "PY_CMD=py")
)

REM Neu khong co py thi thu tim python truc tiep
if not defined PY_CMD (
  where /q python
  if %errorlevel% equ 0 (
    python --version >nul 2>&1 && set "PY_CMD=python"
  )
)

if not defined PY_CMD (
  echo [LỖI] Chưa tìm thấy Python trên máy tính của bạn!
  echo Vui lòng tải Python 3.12 hoặc 3.13 từ https://www.python.org/downloads/
  echo [ĐẶC BIỆT LƯU Ý]: Bắt buộc tích vào ô "Add python.exe to PATH" khi cài đặt.
  echo.
  pause
  exit /b 1
)

echo -> Đang sử dụng lệnh: !PY_CMD!

REM Kiem tra tuy chon Claude Code CLI (khong bat buoc de khong chan nguoi dung)
where /q claude
if %errorlevel% neq 0 (
  echo [Thông tin] Máy tính chưa cài Claude Code CLI.
  echo -> Nếu dùng Claude cá nhân: Cài Node.js từ nodejs.org rồi mở PowerShell gõ: npm install -g @anthropic-ai/claude-code
  echo -> Nếu dùng Antigravity, Gemini, OpenAI, DeepSeek: Bạn có thể bỏ qua bước này.
  echo.
) else (
  echo -> Đã tìm thấy Claude Code CLI.
)

REM [2/5] Tao moi truong ao Python (.venv)
if not exist ".venv\Scripts\python.exe" (
  echo [2/5] Đang khởi tạo môi trường Python ảo (.venv)...
  if exist ".venv" rmdir /s /q .venv
  !PY_CMD! -m venv .venv
  if not exist ".venv\Scripts\python.exe" (
    echo [LỖI] Không tạo được môi trường ảo .venv! Vui lòng kiểm tra quyền thư mục hoặc cài lại Python.
    pause
    exit /b 1
  )
) else (
  echo [2/5] Môi trường Python ảo (.venv) đã sẵn sàng.
)

REM [3/5] Cai dat thu vien
echo [3/5] Đang cài đặt thư viện hệ thống và công cụ tính toán kỹ thuật...
echo (Quá trình này mất khoảng 2-5 phút tùy tốc độ mạng, vui lòng không tắt cửa sổ)...
.venv\Scripts\python -m pip install --disable-pip-version-check --upgrade pip >nul 2>&1
.venv\Scripts\python -m pip install --disable-pip-version-check -r requirements.txt
if %errorlevel% neq 0 (
  echo [Cảnh báo] Một số gói cơ bản cài đặt gặp sự cố, đang thử cài lại các gói Desktop cốt lõi...
  .venv\Scripts\python -m pip install pywebview pywin32 pythonnet psutil fastapi uvicorn httpx pyyaml
)
if exist "requirements-ky-thuat.txt" (
  .venv\Scripts\python -m pip install --disable-pip-version-check -r requirements-ky-thuat.txt
)

REM [4/5] Tao file cau hinh .env neu chua co
echo [4/5] Kiểm tra tệp cấu hình hệ thống...
if not exist ".env" (
  if exist "env.example" (
    copy env.example .env >nul
    echo -> Đã tạo tệp cấu hình .env mặc định.
  )
)

REM [5/5] Tao bieu tuong loi tat tren man hinh chinh Desktop
echo [5/5] Đang tạo biểu tượng lối tắt Kuro OS trên màn hình Desktop...
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0tao-loi-tat.ps1"

echo.
echo =====================================================================
echo 🎉 CÀI ĐẶT HOÀN TẤT THÀNH CÔNG!
echo Hãy nhấp đúp vào biểu tượng KURO OS trên màn hình chính để bắt đầu.
echo =====================================================================
echo.
pause
