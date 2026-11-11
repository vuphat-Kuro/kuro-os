"""
Kuro OS - Ứng dụng Desktop chạy trực tiếp trên Windows (Native Windows App)
Sử dụng Microsoft Edge WebView2 (qua pywebview) để hiển thị giao diện mượt mà,
tương tác trực tiếp với hệ điều hành Windows: mở hộp thoại chọn thư mục,
thao tác tệp tin không bị hạn chế bởi cơ chế sandbox của trình duyệt web.
"""

import sys
import os
from pathlib import Path

# Thư mục gốc Kuro và thư mục server
ROOT = Path(__file__).resolve().parent
SERVER_DIR = ROOT / "server"
if str(SERVER_DIR) not in sys.path:
    sys.path.insert(0, str(SERVER_DIR))
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

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
    except Exception as e:
        print(f"[Desktop Server] Lỗi khởi động server: {e}")


def main():
    # 1. Đảm bảo server Kuro OS đang chạy
    if not is_server_running():
        print("[Kuro Desktop] Đang khởi động máy chủ Kuro OS cục bộ...")
        server_thread = threading.Thread(target=run_fastapi_server, daemon=True)
        server_thread.start()
        # Đợi tối đa 5 giây cho server sẵn sàng
        for _ in range(25):
            time.sleep(0.2)
            if is_server_running():
                break

    # 2. Khởi tạo cầu nối API và Cửa sổ ứng dụng Windows
    api = DesktopApi()
    icon_path = ROOT / "kuro.ico"

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

    # 3. Khởi chạy cửa sổ ứng dụng Windows Native (Edge WebView2)
    webview.start(
        debug=False,
        icon=str(icon_path) if icon_path.is_file() else None
    )


if __name__ == "__main__":
    main()
