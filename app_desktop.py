"""
Kuro OS - Ứng dụng Desktop chạy trực tiếp trên Windows (Native Windows App)
Sử dụng Microsoft Edge WebView2 (qua pywebview) để hiển thị giao diện mượt mà,
tương tác trực tiếp với hệ điều hành Windows: mở hộp thoại chọn thư mục,
thao tác tệp tin không bị hạn chế bởi cơ chế sandbox của trình duyệt web.
"""

import sys
import os

# Thiết lập UTF-8 toàn cục cho Windows tránh lỗi UnicodeDecodeError cp1252
os.environ["PYTHONUTF8"] = "1"
os.environ["PYTHONIOENCODING"] = "utf-8"

from pathlib import Path

# Thư mục gốc Kuro và thư mục server
ROOT = Path(__file__).resolve().parent
SERVER_DIR = ROOT / "server"
if str(SERVER_DIR) not in sys.path:
    sys.path.insert(0, str(SERVER_DIR))
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Đảm bảo stdout và stderr luôn tồn tại khi chạy dưới pythonw.exe (GUI mode không có console)
# tránh lỗi crash "AttributeError: 'NoneType' object has no attribute 'write'" khi uvicorn/logging ghi log
if sys.stdout is None or sys.stderr is None:
    try:
        log_dir = ROOT / "state"
        log_dir.mkdir(exist_ok=True)
        gui_log = open(log_dir / "desktop.log", "a", encoding="utf-8", buffering=1)
        if sys.stdout is None:
            sys.stdout = gui_log
        if sys.stderr is None:
            sys.stderr = gui_log
    except Exception:
        pass

# Đặt AppUserModelID cho Windows để Taskbar hiển thị đúng Icon Kuro thay vì icon mặc định của Python
if sys.platform == "win32":
    import ctypes
    try:
        myappid = 'kuro.os.infrastructure.assistant.desktop.v1'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    except Exception as e:
        print(f"[Desktop App] Không đặt được AppUserModelID: {e}")

import threading
import time
import urllib.request
import webview

class DesktopApi:
    """Cầu nối API giữa JavaScript giao diện và hệ điều hành Windows."""
    def __init__(self):
        self._window = None

    def set_window(self, window):
        self._window = window

    def is_desktop_app(self) -> bool:
        """Xác nhận đây là ứng dụng Native Desktop."""
        return True

    def choose_folder(self, initial_dir: str = "") -> str:
        """
        Mở trực tiếp hộp thoại chọn thư mục NATIVE của Windows bằng Edge WebView2.
        Không qua Browser Sandbox, không lo deadlock, mượt 100%.
        """
        if not self._window:
            return ""
        try:
            start_dir = initial_dir if initial_dir and os.path.isdir(initial_dir) else ""
            res = self._window.create_file_dialog(
                dialog_type=webview.FOLDER_DIALOG,
                directory=start_dir
            )
            if res and len(res) > 0:
                selected = str(res[0])
                if os.path.isdir(selected):
                    return selected
        except Exception as e:
            print(f"[DesktopApi] Lỗi chọn thư mục: {e}")
        return ""

    def open_in_explorer(self, folder_path: str = ""):
        """Mở thư mục trong Windows Explorer desktop."""
        try:
            p = folder_path if folder_path and os.path.isdir(folder_path) else str(ROOT)
            os.startfile(p)
            return True
        except Exception as e:
            print(f"[DesktopApi] Lỗi mở Explorer: {e}")
            return False

    def get_clipboard_files(self) -> list[str]:
        """Lấy danh sách đường dẫn file từ Clipboard Windows khi người dùng copy file."""
        try:
            from system_clipboard import get_clipboard_files
            return get_clipboard_files()
        except Exception as e:
            print(f"[DesktopApi] Lỗi đọc clipboard: {e}")
            return []


def free_port(port: int = 7788):
    """Giải phóng cổng nếu có tiến trình zombie cũ chiếm giữ."""
    try:
        import subprocess
        cmd = f'netstat -ano | findstr /r /c:":{port} .*LISTENING"'
        out = subprocess.check_output(cmd, shell=True, text=True, encoding="utf-8", errors="ignore")
        for line in out.strip().splitlines():
            parts = line.strip().split()
            if len(parts) >= 5:
                pid = int(parts[-1])
                if pid > 0 and pid != os.getpid():
                    os.system(f"taskkill /PID {pid} /F >nul 2>&1")
    except Exception:
        pass


def is_server_running(url: str = "http://127.0.0.1:7788/health") -> bool:
    try:
        req = urllib.request.urlopen(url, timeout=0.8)
        return req.status == 200
    except Exception:
        return False


def run_fastapi_server():
    """Khởi chạy server uvicorn nền nếu chưa có tiến trình nào chạy."""
    try:
        import uvicorn
        from server.main import app
        # Lắng nghe 0.0.0.0 để điện thoại qua Tailscale/Wi-Fi vẫn kết nối bình thường
        uvicorn.run(app, host="0.0.0.0", port=7788, log_level="warning")
    except BaseException as e:
        import traceback
        try:
            with open(ROOT / "state" / "desktop_server_error.log", "w", encoding="utf-8") as f:
                f.write(traceback.format_exc())
        except Exception:
            pass


def main():
    try:
        # 0. Giải phóng cổng 7788 nếu có tiến trình zombie từ phiên trước
        free_port(7788)
        time.sleep(0.3)

        # 1. Đảm bảo server Kuro OS đang chạy với code mới nhất
        print("[Kuro Desktop] Đang khởi động máy chủ Kuro OS cục bộ...")
        server_thread = threading.Thread(target=run_fastapi_server, daemon=True)
        server_thread.start()
        for _ in range(30):
            time.sleep(0.2)
            if is_server_running():
                break

        # 2. Khởi tạo cầu nối API và Cửa sổ ứng dụng Windows
        api = DesktopApi()
        icon_path = (ROOT / "kuro_logo.ico").resolve()
        icon_str = str(icon_path) if icon_path.is_file() else None

        window = webview.create_window(
            title="Kuro OS - Trợ lý Kỹ sư Hạ tầng",
            url="http://127.0.0.1:7788",
            width=1340,
            height=880,
            min_size=(960, 620),
            text_select=True,
            zoomable=True,
            js_api=api
        )
        api.set_window(window)

        def on_closed():
            # Thoát dứt khoát khi tắt cửa sổ để không để lại tiến trình ma
            os._exit(0)

        window.events.closed += on_closed

        # 3. Khởi chạy cửa sổ ứng dụng Windows Native (Edge WebView2)
        webview.start(
            debug=False,
            icon=icon_str
        )
        os._exit(0)
    except Exception as e:
        import traceback
        err_msg = traceback.format_exc()
        try:
            with open(ROOT / "state" / "desktop_error.log", "a", encoding="utf-8") as f:
                f.write(err_msg + "\n")
        except Exception:
            pass
        if sys.platform == "win32":
            import ctypes
            ctypes.windll.user32.MessageBoxW(0, f"Lỗi khởi chạy Kuro OS:\n{e}\n\nXem chi tiết tại state/desktop_error.log", "Kuro OS Error", 16)
        os._exit(1)


if __name__ == "__main__":
    main()
