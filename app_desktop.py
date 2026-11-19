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

# Đảm bảo stdout và stderr luôn tồn tại và dùng UTF-8 (tránh crash UnicodeEncodeError cp1252 trên Windows)
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
for _stream in (sys.stdout, sys.stderr):
    try:
        if _stream and hasattr(_stream, "reconfigure"):
            _stream.reconfigure(encoding="utf-8", errors="replace")
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

# Nạp an toàn pywebview, tự động cài đặt nếu môi trường thiếu thư viện
webview = None
try:
    import webview
except ImportError:
    try:
        import subprocess
        print("[Desktop App] Đang bổ sung gói pywebview cho ứng dụng Desktop...")
        py_exe = sys.executable
        no_win = getattr(subprocess, "CREATE_NO_WINDOW", 0)
        subprocess.run([py_exe, "-m", "pip", "install", "pywebview", "pywin32", "pythonnet"], check=False, creationflags=no_win)
        import webview
    except Exception as e:
        print(f"[Desktop App] Không nạp được pywebview: {e}")
        webview = None

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

    def reload_app(self, hard: bool = True) -> bool:
        """Tải lại giao diện ngay trên cửa sổ Kuro Desktop (Ctrl+F5 / F5 / Ctrl+R) không cần tắt mở lại app."""
        if not self._window:
            return False
        try:
            import config
            port = getattr(config, "PORT", 7788)
            base_url = f"http://127.0.0.1:{port}/"
            target_url = f"{base_url}?_r={int(time.time() * 1000)}" if hard else base_url
            self._window.load_url(target_url)
            return True
        except Exception as e:
            print(f"[DesktopApi] Lỗi tải lại cửa sổ: {e}")
            return False


def _read_kuro_port() -> int:
    """Đọc KURO_PORT từ môi trường hoặc .env (mặc định 7788)."""
    val = os.getenv("KURO_PORT", "").strip()
    if not val:
        env_file = ROOT / ".env"
        if env_file.is_file():
            try:
                for line in env_file.read_text(encoding="utf-8", errors="replace").splitlines():
                    s = line.strip()
                    if s.startswith("KURO_PORT="):
                        val = s.split("=", 1)[1].strip().strip('"').strip("'")
                        break
            except Exception:
                pass
    try:
        return int(val) if val else 7788
    except ValueError:
        return 7788


def _is_port_free(port: int) -> bool:
    import socket
    for host in ("127.0.0.1", "0.0.0.0"):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.bind((host, port))
        except OSError:
            return False
        finally:
            s.close()
    return True


def free_port(port: int = 7788, wait_s: float = 6.0):
    """Giải phóng cổng nếu có tiến trình cũ chiếm giữ và đợi cổng thực sự được nhả (tránh WinError 10048)."""
    try:
        import subprocess
        no_win = getattr(subprocess, "CREATE_NO_WINDOW", 0)
        pids: set[int] = set()
        # Ưu tiên psutil nếu có, ổn định hơn netstat trên mọi bản Windows
        try:
            import psutil
            for conn in psutil.net_connections(kind="tcp"):
                if conn.laddr and conn.laddr.port == port and conn.status == psutil.CONN_LISTEN and conn.pid:
                    if conn.pid != os.getpid():
                        pids.add(conn.pid)
        except Exception:
            pass
        if not pids:
            cmd = f'netstat -ano | findstr /r /c:":{port} .*LISTENING"'
            out = subprocess.check_output(cmd, shell=True, text=True, encoding="utf-8", errors="ignore", creationflags=no_win)
            for line in out.strip().splitlines():
                parts = line.strip().split()
                if len(parts) >= 5 and parts[-1].isdigit():
                    pid = int(parts[-1])
                    if pid > 0 and pid != os.getpid():
                        pids.add(pid)
        for pid in pids:
            subprocess.run(["taskkill", "/PID", str(pid), "/T", "/F"], capture_output=True, creationflags=no_win)
    except Exception:
        pass

    deadline = time.time() + wait_s
    while time.time() < deadline:
        if _is_port_free(port):
            return
        time.sleep(0.2)


# Opener bỏ qua HTTP Proxy của Windows khi gọi localhost (tránh lỗi trên máy công ty bật proxy/VPN)
_LOCAL_OPENER = urllib.request.build_opener(urllib.request.ProxyHandler({}))


def is_server_running(port: int = 7788) -> bool:
    url = f"http://127.0.0.1:{port}/health"
    try:
        with _LOCAL_OPENER.open(url, timeout=1.0) as req:
            return req.status == 200
    except Exception:
        return False


_SERVER_ERROR: str | None = None


def run_fastapi_server():
    """Khởi chạy server uvicorn nền và ghi nhận lỗi nếu không khởi động được."""
    global _SERVER_ERROR
    try:
        import uvicorn
        from server.main import app
        import config   # cùng module server.main đã nạp
        # Mặc định chỉ máy này; bật cho điện thoại ở hộp /remote (KURO_HOST=0.0.0.0), điện thoại cần mã ghép trong QR
        uvicorn.run(app, host=config.HOST, port=config.PORT, log_level="warning")
    except BaseException as e:
        import traceback
        tb = traceback.format_exc()
        _SERVER_ERROR = f"{type(e).__name__}: {e}\n\n{tb}"
        try:
            (ROOT / "state").mkdir(parents=True, exist_ok=True)
            with open(ROOT / "state" / "desktop_server_error.log", "w", encoding="utf-8") as f:
                f.write(tb)
        except Exception:
            pass


def main():
    try:
        # Ẩn console của tiến trình con (claude...) và gom chúng vào job: tắt Kuro Desktop thì cả cây con tắt theo
        try:
            import winproc
            winproc.an_cua_so()
            winproc.gop_tien_trinh_con()
        except Exception as e:
            print(f"[Kuro Desktop] Bỏ qua winproc: {e}")

        port = _read_kuro_port()
        app_url = f"http://127.0.0.1:{port}"

        # 0. Giải phóng cổng nếu có tiến trình cũ chiếm giữ và chờ nhả cổng hoàn toàn
        free_port(port)

        # 1. Đảm bảo server Kuro OS đang chạy với code mới nhất (chờ tối đa 30s cho máy yếu / quét Defender sau cập nhật)
        print(f"[Kuro Desktop] Đang khởi động máy chủ Kuro OS cục bộ (cổng {port})...")
        server_thread = threading.Thread(target=run_fastapi_server, daemon=True)
        server_thread.start()
        ready = False
        for _ in range(150):
            if _SERVER_ERROR:
                break
            time.sleep(0.2)
            if is_server_running(port):
                ready = True
                break

        if not ready:
            detail = (_SERVER_ERROR or f"Máy chủ cục bộ không phản hồi tại {app_url} sau 30 giây.").strip()
            short_detail = detail.splitlines()[0] if _SERVER_ERROR else detail
            if "No module named" in detail or "python-multipart" in detail:
                hint = "\n\nGợi ý khắc phục: Chạy lại tệp cap-nhat.bat hoặc setup.bat để cài đủ thư viện Python."
            elif "10048" in detail:
                hint = f"\n\nGợi ý khắc phục: Cổng {port} đang bị ứng dụng khác chiếm giữ. Chạy tat-kuro.bat rồi mở lại."
            else:
                hint = "\n\nXem chi tiết tại tệp state\\desktop_server_error.log, hoặc chạy cap-nhat.bat / run-app.bat để xem log."
            if sys.platform == "win32":
                import ctypes
                ctypes.windll.user32.MessageBoxW(
                    0,
                    f"Kuro OS chưa khởi động được máy chủ cục bộ:\n\n{short_detail}{hint}",
                    "Kuro OS - Lỗi khởi động máy chủ",
                    16
                )
            os._exit(1)

        # 2. Khởi tạo cầu nối API và Cửa sổ ứng dụng Windows
        if webview is None:
            print("[Kuro Desktop] Mở giao diện trên trình duyệt web...")
            import webbrowser
            webbrowser.open(app_url)
            if sys.platform == "win32":
                import ctypes
                try:
                    ctypes.windll.user32.MessageBoxW(
                        0,
                        "Kuro OS đã khởi động máy chủ thành công và mở trên trình duyệt web.\n\n"
                        "Để hiển thị dưới dạng cửa sổ ứng dụng Windows chuyên dụng, bạn hãy nhấp đúp chạy lại tệp setup.bat nhé.",
                        "Kuro OS Desktop",
                        64
                    )
                except Exception:
                    pass
            while True:
                time.sleep(1)

        api = DesktopApi()
        icon_path = (ROOT / "kuro_logo.ico").resolve()
        icon_str = str(icon_path) if icon_path.is_file() else None

        window = webview.create_window(
            title="Kuro OS - Trợ lý Kỹ sư Hạ tầng",
            url=app_url,
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
