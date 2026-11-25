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

import json
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

_UI_THEME_FILE = ROOT / "state" / "ui_theme.txt"
_FLOATING_LAYOUT_FILE = ROOT / "state" / "floating_window.json"
_TITLEBAR_PALETTE = {
    "light": {
        "dark": False,
        "bg": "#dfe6f0",
        "caption": 0x00F0E6DF,  # #dfe6f0 (COLORREF 0x00BBGGRR)
        "text": 0x00361B0E,     # #0e1b36
        "border": 0x00E4D2C5,   # #c5d2e4
        "rgb": (223, 230, 240),
    },
    "dark": {
        "dark": True,
        "bg": "#09101c",
        "caption": 0x001C1009,  # #09101c (COLORREF 0x00BBGGRR)
        "text": 0x00FAF0E8,     # #e8f0fa
        "border": 0x004B2F1E,   # #1e2f4b
        "rgb": (9, 16, 28),
    },
}


def _normalize_ui_theme(theme: str | None) -> str:
    return "dark" if str(theme or "").strip().lower() == "dark" else "light"


def _load_saved_ui_theme() -> str:
    try:
        if _UI_THEME_FILE.is_file():
            return _normalize_ui_theme(_UI_THEME_FILE.read_text(encoding="utf-8", errors="ignore"))
    except Exception:
        pass
    return "light"


def _save_ui_theme(theme: str):
    try:
        _UI_THEME_FILE.parent.mkdir(parents=True, exist_ok=True)
        _UI_THEME_FILE.write_text(_normalize_ui_theme(theme), encoding="utf-8")
    except Exception:
        pass


def _get_native_form(window):
    if window is None:
        return None
    native = getattr(window, "native", None)
    if native is not None:
        return native
    try:
        from webview.platforms import winforms
        uid = getattr(window, "uid", None)
        if uid and uid in winforms.BrowserView.instances:
            return winforms.BrowserView.instances[uid]
    except Exception:
        pass
    return None


def _get_window_hwnd(window) -> int:
    native = _get_native_form(window)
    if native is not None:
        try:
            handle = getattr(native, "Handle", None)
            if handle is not None:
                hwnd = int(handle.ToInt64()) if hasattr(handle, "ToInt64") else int(handle.ToInt32())
                if hwnd:
                    return hwnd
        except Exception:
            pass
    if sys.platform != "win32":
        return 0
    try:
        import ctypes
        from ctypes import wintypes
        user32 = ctypes.windll.user32
        target_pid = os.getpid()
        found = [0]

        @ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
        def _enum_cb(hwnd, _lparam):
            if not user32.IsWindowVisible(hwnd):
                return True
            pid = wintypes.DWORD(0)
            user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
            if pid.value == target_pid and user32.GetParent(hwnd) == 0:
                found[0] = int(hwnd)
                return False
            return True

        user32.EnumWindows(_enum_cb, 0)
        return found[0]
    except Exception:
        return 0


def _apply_windows_titlebar_theme(window, theme: str = "light") -> bool:
    """Đồng bộ màu thanh tiêu đề cửa sổ Windows 10/11 (DWM) theo chế độ Sáng/Tối của Kuro OS."""
    if sys.platform != "win32":
        return False
    norm = _normalize_ui_theme(theme)
    pal = _TITLEBAR_PALETTE[norm]
    hwnd = _get_window_hwnd(window)
    if not hwnd:
        return False
    try:
        import ctypes
        from ctypes import wintypes
        dwmapi = ctypes.windll.dwmapi
        user32 = ctypes.windll.user32

        dwmapi.DwmSetWindowAttribute.argtypes = [
            wintypes.HWND, wintypes.DWORD, ctypes.c_void_p, wintypes.DWORD
        ]
        dwmapi.DwmSetWindowAttribute.restype = ctypes.c_long
        user32.SetWindowPos.argtypes = [
            wintypes.HWND, wintypes.HWND,
            ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, wintypes.UINT
        ]
        user32.SetWindowPos.restype = wintypes.BOOL

        # 1. Bật/tắt chế độ tối cho thanh tiêu đề & bộ nút -, □, × (Win 10 20H1+ & Win 11)
        dark_val = ctypes.c_int(1 if pal["dark"] else 0)
        res = dwmapi.DwmSetWindowAttribute(
            hwnd, 20, ctypes.byref(dark_val), ctypes.sizeof(dark_val)
        )
        if res != 0:
            dwmapi.DwmSetWindowAttribute(
                hwnd, 19, ctypes.byref(dark_val), ctypes.sizeof(dark_val)
            )

        # 2. Đặt chính xác màu nền, màu chữ và màu viền trên Windows 11 (build >= 22000)
        for attr, colorref in ((35, pal["caption"]), (36, pal["text"]), (34, pal["border"])):
            c_val = ctypes.c_uint32(colorref)
            dwmapi.DwmSetWindowAttribute(
                hwnd, attr, ctypes.byref(c_val), ctypes.sizeof(c_val)
            )

        # 3. Đồng bộ màu nền khung WinForms để không bị loang trắng khi kéo giãn cửa sổ
        native = _get_native_form(window)
        if native is not None:
            try:
                import System
                from System.Drawing import Color
                r, g, b = pal["rgb"]
                target_color = Color.FromArgb(r, g, b)

                def _set_bg():
                    try:
                        native.BackColor = target_color
                    except Exception:
                        pass

                if getattr(native, "InvokeRequired", False):
                    native.BeginInvoke(System.Action(_set_bg))
                else:
                    _set_bg()
            except Exception:
                pass

        # 4. Ép vẽ lại khung cửa sổ để thanh tiêu đề đổi màu tức thì
        SWP_NOSIZE = 0x0001
        SWP_NOMOVE = 0x0002
        SWP_NOZORDER = 0x0004
        SWP_NOACTIVATE = 0x0010
        SWP_FRAMECHANGED = 0x0020
        user32.SetWindowPos(
            hwnd, 0, 0, 0, 0, 0,
            SWP_NOSIZE | SWP_NOMOVE | SWP_NOZORDER | SWP_NOACTIVATE | SWP_FRAMECHANGED
        )
        try:
            dwmapi.DwmFlush()
        except Exception:
            pass
        return True
    except Exception as e:
        print(f"[DesktopApi] Không cập nhật được màu thanh tiêu đề: {e}")
        return False


class FloatingWindowController:
    """
    Điều khiển chế độ Bóng chat nổi trên cùng 1 cửa sổ Kuro Desktop (Single Window Morph):
    - 3 trạng thái: full <-> mini (370x510 nổi trên CAD) <-> bubble (bong bóng tròn 64x64)
    - Phím tắt toàn cục Windows: Alt + K (hoạt động ngay cả khi đang vẽ trong AutoCAD/Revit)
    - Tự làm mờ mượt khi rời chuột (Auto-Dim bằng Win32 WS_EX_LAYERED), rê chuột vào tự rõ 100%
    """

    GWL_EXSTYLE = -20
    WS_EX_LAYERED = 0x00080000
    LWA_ALPHA = 0x00000002

    HWND_TOPMOST = -1
    SWP_NOSIZE = 0x0001
    SWP_NOMOVE = 0x0002
    SWP_NOACTIVATE = 0x0010
    SWP_FRAMECHANGED = 0x0020

    WM_NCLBUTTONDOWN = 0x00A1
    WM_HOTKEY = 0x0312
    WM_QUIT = 0x0012

    HTCAPTION = 2
    HT_EDGE_MAP = {
        "left": 10,
        "right": 11,
        "top": 12,
        "top-left": 13,
        "top-right": 14,
        "bottom": 15,
        "bottom-left": 16,
        "bottom-right": 17,
    }

    MOD_ALT = 0x0001
    MOD_NOREPEAT = 0x4000
    VK_K = 0x4B
    HOTKEY_ID = 0x4B52  # 'KR'

    DWMWA_WINDOW_CORNER_PREFERENCE = 33
    DWMWCP_DEFAULT = 0
    DWMWCP_DONOTROUND = 1
    DWMWCP_ROUND = 2

    def __init__(self, initial_theme: str = "light"):
        self.window = None
        self.mode = "full"  # full | mini | bubble
        self.theme = _normalize_ui_theme(initial_theme)
        self.auto_dim = True
        self.dim_opacity = 0.72
        self._current_alpha = 255
        self._hwnd = 0
        self._stop_event = threading.Event()
        self._started = False
        self._hotkey_thread_id = 0
        self._last_toggle_ts = 0.0
        self._win32_ready = False
        self._user32 = None
        self._gdi32 = None
        self._dwmapi = None
        self._RECT = None
        self._POINT = None

        if sys.platform == "win32":
            self._init_win32()
        self._layout = self._load_state()

    def _init_win32(self):
        try:
            import ctypes
            from ctypes import wintypes

            class RECT(ctypes.Structure):
                _fields_ = [
                    ("left", ctypes.c_long),
                    ("top", ctypes.c_long),
                    ("right", ctypes.c_long),
                    ("bottom", ctypes.c_long),
                ]

            class POINT(ctypes.Structure):
                _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]

            self._RECT = RECT
            self._POINT = POINT
            u32 = ctypes.windll.user32
            g32 = ctypes.windll.gdi32
            dwm = ctypes.windll.dwmapi

            u32.GetWindowLongW.argtypes = [wintypes.HWND, ctypes.c_int]
            u32.GetWindowLongW.restype = ctypes.c_long
            u32.SetWindowLongW.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_long]
            u32.SetWindowLongW.restype = ctypes.c_long
            u32.SetLayeredWindowAttributes.argtypes = [
                wintypes.HWND, wintypes.COLORREF, wintypes.BYTE, wintypes.DWORD
            ]
            u32.SetLayeredWindowAttributes.restype = wintypes.BOOL
            u32.SetWindowPos.argtypes = [
                wintypes.HWND, wintypes.HWND,
                ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, wintypes.UINT,
            ]
            u32.SetWindowPos.restype = wintypes.BOOL
            u32.GetWindowRect.argtypes = [wintypes.HWND, ctypes.POINTER(RECT)]
            u32.GetWindowRect.restype = wintypes.BOOL
            u32.GetCursorPos.argtypes = [ctypes.POINTER(POINT)]
            u32.GetCursorPos.restype = wintypes.BOOL
            u32.GetForegroundWindow.argtypes = []
            u32.GetForegroundWindow.restype = wintypes.HWND
            u32.GetAncestor.argtypes = [wintypes.HWND, wintypes.UINT]
            u32.GetAncestor.restype = wintypes.HWND
            u32.ReleaseCapture.argtypes = []
            u32.ReleaseCapture.restype = wintypes.BOOL
            u32.SendMessageW.argtypes = [wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]
            u32.SendMessageW.restype = ctypes.c_ssize_t
            u32.PostMessageW.argtypes = [wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]
            u32.PostMessageW.restype = wintypes.BOOL
            u32.SetWindowRgn.argtypes = [wintypes.HWND, wintypes.HRGN, wintypes.BOOL]
            u32.SetWindowRgn.restype = ctypes.c_int
            u32.RegisterHotKey.argtypes = [wintypes.HWND, ctypes.c_int, wintypes.UINT, wintypes.UINT]
            u32.RegisterHotKey.restype = wintypes.BOOL
            u32.UnregisterHotKey.argtypes = [wintypes.HWND, ctypes.c_int]
            u32.UnregisterHotKey.restype = wintypes.BOOL
            u32.PostThreadMessageW.argtypes = [wintypes.DWORD, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]
            u32.PostThreadMessageW.restype = wintypes.BOOL
            u32.SystemParametersInfoW.argtypes = [wintypes.UINT, wintypes.UINT, ctypes.c_void_p, wintypes.UINT]
            u32.SystemParametersInfoW.restype = wintypes.BOOL

            g32.CreateEllipticRgn.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
            g32.CreateEllipticRgn.restype = wintypes.HRGN

            dwm.DwmSetWindowAttribute.argtypes = [
                wintypes.HWND, wintypes.DWORD, ctypes.c_void_p, wintypes.DWORD
            ]
            dwm.DwmSetWindowAttribute.restype = ctypes.c_long

            self._user32 = u32
            self._gdi32 = g32
            self._dwmapi = dwm
            self._win32_ready = True
        except Exception as e:
            print(f"[Floating] Không khởi tạo được Win32 API: {e}")

    def attach(self, window):
        self.window = window

    def set_theme(self, theme: str):
        self.theme = _normalize_ui_theme(theme)

    def _invoke_ui(self, fn, wait: bool = False):
        native = _get_native_form(self.window)
        if native is None:
            return
        try:
            import System
            action = System.Action(fn)
            if getattr(native, "InvokeRequired", False):
                if wait:
                    native.Invoke(action)
                else:
                    native.BeginInvoke(action)
            else:
                fn()
        except Exception as e:
            print(f"[Floating] Lỗi invoke UI: {e}")

    def _get_work_area(self) -> tuple[int, int]:
        if self._win32_ready and self._RECT is not None:
            try:
                import ctypes
                rc = self._RECT()
                if self._user32.SystemParametersInfoW(0x0030, 0, ctypes.byref(rc), 0):
                    w = int(rc.right - rc.left)
                    h = int(rc.bottom - rc.top)
                    if w > 300 and h > 300:
                        return w, h
            except Exception:
                pass
        return 1920, 1040

    def _default_layout(self) -> dict:
        sw, sh = self._get_work_area()
        mini_w, mini_h = 370, 510
        bubble_sz = 64
        full_w = min(1340, max(960, sw - 80))
        full_h = min(880, max(620, sh - 60))
        return {
            "full": {
                "x": max(20, (sw - full_w) // 2),
                "y": max(20, (sh - full_h) // 2),
                "w": full_w,
                "h": full_h,
            },
            "mini": {
                "x": max(20, sw - mini_w - 24),
                "y": max(20, sh - mini_h - 24),
                "w": mini_w,
                "h": mini_h,
            },
            "bubble": {
                "x": max(20, sw - bubble_sz - 28),
                "y": max(20, sh - bubble_sz - 36),
                "w": bubble_sz,
                "h": bubble_sz,
            },
        }

    def _load_state(self) -> dict:
        base = self._default_layout()
        try:
            if _FLOATING_LAYOUT_FILE.is_file():
                saved = json.loads(_FLOATING_LAYOUT_FILE.read_text(encoding="utf-8"))
                for k in ("full", "mini", "bubble"):
                    if isinstance(saved.get(k), dict):
                        base[k].update(saved[k])
                if isinstance(saved.get("auto_dim"), bool):
                    self.auto_dim = saved["auto_dim"]
                if isinstance(saved.get("dim_opacity"), (int, float)):
                    self.dim_opacity = max(0.45, min(1.0, float(saved["dim_opacity"])))
        except Exception:
            pass
        return base

    def _save_state(self):
        try:
            _FLOATING_LAYOUT_FILE.parent.mkdir(parents=True, exist_ok=True)
            payload = {
                "full": self._layout["full"],
                "mini": self._layout["mini"],
                "bubble": self._layout["bubble"],
                "auto_dim": self.auto_dim,
                "dim_opacity": self.dim_opacity,
            }
            _FLOATING_LAYOUT_FILE.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        except Exception:
            pass

    def _snapshot_current_bounds(self):
        native = _get_native_form(self.window)
        if native is None:
            return
        try:
            from System.Windows.Forms import FormWindowState
            if native.WindowState == FormWindowState.Normal:
                b = native.Bounds
                if b.Width >= 50 and b.Height >= 50:
                    self._layout[self.mode] = {
                        "x": int(b.X),
                        "y": int(b.Y),
                        "w": int(b.Width),
                        "h": int(b.Height),
                    }
                    self._save_state()
        except Exception:
            pass

    def _clamp_bounds(self, x: int, y: int, w: int, h: int) -> tuple[int, int, int, int]:
        try:
            from System.Windows.Forms import Screen
            from System.Drawing import Rectangle
            wa = Screen.FromRectangle(Rectangle(int(x), int(y), int(w), int(h))).WorkingArea
            w = max(56, min(int(w), int(wa.Width)))
            h = max(56, min(int(h), int(wa.Height)))
            x = max(int(wa.Left), min(int(x), int(wa.Right) - w))
            y = max(int(wa.Top), min(int(y), int(wa.Bottom) - h))
            return x, y, w, h
        except Exception:
            return int(x), int(y), int(w), int(h)

    def _ensure_layered(self, hwnd: int):
        if not self._win32_ready or not hwnd:
            return
        ex = self._user32.GetWindowLongW(hwnd, self.GWL_EXSTYLE)
        if not (ex & self.WS_EX_LAYERED):
            self._user32.SetWindowLongW(hwnd, self.GWL_EXSTYLE, ex | self.WS_EX_LAYERED)

    def _set_alpha(self, alpha: int):
        """Đặt độ mờ an toàn trên UI thread qua WinForms Form.Opacity (tránh xung đột cross-thread với WebView2)."""
        if not self._win32_ready or self.window is None:
            return
        alpha = max(60, min(255, int(alpha)))
        if alpha == self._current_alpha:
            return
        self._current_alpha = alpha
        op_val = round(alpha / 255.0, 3)

        def _apply_op():
            native = _get_native_form(self.window)
            if native is None:
                return
            try:
                native.Opacity = op_val
            except Exception:
                pass

        self._invoke_ui(_apply_op, wait=False)

    def _set_corner_preference(self, hwnd: int, pref: int):
        if not self._win32_ready or not hwnd:
            return
        try:
            import ctypes
            val = ctypes.c_int(pref)
            self._dwmapi.DwmSetWindowAttribute(
                hwnd, self.DWMWA_WINDOW_CORNER_PREFERENCE, ctypes.byref(val), ctypes.sizeof(val)
            )
        except Exception:
            pass

    def _apply_region(self, hwnd: int, circular: bool):
        if not self._win32_ready or not hwnd:
            return
        try:
            import ctypes
            if circular:
                rc = self._RECT()
                if self._user32.GetWindowRect(hwnd, ctypes.byref(rc)):
                    w = max(1, rc.right - rc.left)
                    h = max(1, rc.bottom - rc.top)
                    rgn = self._gdi32.CreateEllipticRgn(0, 0, w + 1, h + 1)
                    self._user32.SetWindowRgn(hwnd, rgn, True)
            else:
                self._user32.SetWindowRgn(hwnd, 0, True)
        except Exception as e:
            print(f"[Floating] Lỗi áp vùng cửa sổ: {e}")

    def get_state(self) -> dict:
        return {
            "mode": self.mode,
            "auto_dim": self.auto_dim,
            "dim_opacity": self.dim_opacity,
        }

    def set_mode(self, new_mode: str, focus_input: bool = False, notify_js: bool = True) -> dict:
        if not self._win32_ready or self.window is None or new_mode not in ("full", "mini", "bubble"):
            return {"ok": False, "mode": self.mode}

        old_mode = self.mode

        def _apply():
            native = _get_native_form(self.window)
            if native is None:
                return
            from System.Drawing import Point, Size
            from System.Windows.Forms import FormBorderStyle, FormWindowState

            self._snapshot_current_bounds()
            self.mode = new_mode

            if native.WindowState == FormWindowState.Minimized:
                native.WindowState = FormWindowState.Normal

            cfg = self._layout[new_mode]
            if new_mode == "full":
                x, y, w, h = self._clamp_bounds(cfg["x"], cfg["y"], max(960, cfg["w"]), max(620, cfg["h"]))
                native.SuspendLayout()
                native.TopMost = False
                native.FormBorderStyle = FormBorderStyle.Sizable
                native.MinimumSize = Size(960, 620)
                native.Location = Point(x, y)
                native.Size = Size(w, h)
                native.ResumeLayout(True)

                hwnd = _get_window_hwnd(self.window)
                self._hwnd = hwnd or self._hwnd
                self._apply_region(hwnd, circular=False)
                self._set_corner_preference(hwnd, self.DWMWCP_DEFAULT)
                _apply_windows_titlebar_theme(self.window, self.theme)
                self._current_alpha = 255
                try:
                    native.Opacity = 1.0
                except Exception:
                    pass
                native.Activate()

            elif new_mode == "mini":
                x, y, w, h = self._clamp_bounds(cfg["x"], cfg["y"], max(310, cfg["w"]), max(340, cfg["h"]))
                native.SuspendLayout()
                native.WindowState = FormWindowState.Normal
                native.MinimumSize = Size(310, 340)
                native.FormBorderStyle = getattr(FormBorderStyle, "None")
                native.Location = Point(x, y)
                native.Size = Size(w, h)
                native.TopMost = True
                native.ResumeLayout(True)

                hwnd = _get_window_hwnd(self.window)
                self._hwnd = hwnd or self._hwnd
                self._apply_region(hwnd, circular=False)
                self._set_corner_preference(hwnd, self.DWMWCP_ROUND)
                self._user32.SetWindowPos(
                    hwnd, self.HWND_TOPMOST, 0, 0, 0, 0,
                    self.SWP_NOMOVE | self.SWP_NOSIZE | self.SWP_FRAMECHANGED
                )
                self._current_alpha = 255
                try:
                    native.Opacity = 1.0
                except Exception:
                    pass
                if focus_input or old_mode == "bubble":
                    native.Activate()

            elif new_mode == "bubble":
                sz = 64
                x, y, w, h = self._clamp_bounds(cfg["x"], cfg["y"], sz, sz)
                native.SuspendLayout()
                native.WindowState = FormWindowState.Normal
                native.MinimumSize = Size(sz, sz)
                native.FormBorderStyle = getattr(FormBorderStyle, "None")
                native.Location = Point(x, y)
                native.Size = Size(sz, sz)
                native.TopMost = True
                native.ResumeLayout(True)

                hwnd = _get_window_hwnd(self.window)
                self._hwnd = hwnd or self._hwnd
                self._set_corner_preference(hwnd, self.DWMWCP_DONOTROUND)
                self._user32.SetWindowPos(
                    hwnd, self.HWND_TOPMOST, 0, 0, 0, 0,
                    self.SWP_NOMOVE | self.SWP_NOSIZE | self.SWP_NOACTIVATE | self.SWP_FRAMECHANGED
                )
                self._apply_region(hwnd, circular=True)

        self._invoke_ui(_apply, wait=False)

        # Chỉ đẩy evaluate_js (trên thread nền, tuyệt đối không chạy trên UI thread) khi kích từ Hotkey Alt+K
        if notify_js:
            js_focus = "true" if (focus_input and new_mode == "mini") else "false"
            js_code = f"window.__applyKuroFloatingMode && window.__applyKuroFloatingMode({json.dumps(new_mode)}, {js_focus});"

            def _notify_js():
                time.sleep(0.03)
                try:
                    if self.window is not None:
                        self.window.evaluate_js(js_code)
                except Exception:
                    pass

            threading.Thread(target=_notify_js, daemon=True, name="kuro-floating-js-sync").start()
        return {"ok": True, "mode": new_mode}

    def cycle_hotkey_mode(self):
        """Alt + K: full -> mini -> bubble -> mini (tự focus vào ô chat khi bung mini)."""
        now = time.monotonic()
        if now - self._last_toggle_ts < 0.18:
            return
        self._last_toggle_ts = now
        if self.mode == "full":
            self.set_mode("mini", focus_input=True, notify_js=True)
        elif self.mode == "mini":
            self.set_mode("bubble", focus_input=False, notify_js=True)
        else:
            self.set_mode("mini", focus_input=True, notify_js=True)

    def start_drag(self) -> bool:
        if not self._win32_ready or self.mode == "full":
            return False

        def _do():
            hwnd = _get_window_hwnd(self.window)
            if not hwnd:
                return
            self._user32.ReleaseCapture()
            self._user32.PostMessageW(hwnd, self.WM_NCLBUTTONDOWN, self.HTCAPTION, 0)

        self._invoke_ui(_do, wait=False)
        return True

    def start_resize(self, edge: str = "bottom-right") -> bool:
        if not self._win32_ready or self.mode != "mini":
            return False
        ht = self.HT_EDGE_MAP.get(edge, 17)

        def _do():
            hwnd = _get_window_hwnd(self.window)
            if not hwnd:
                return
            self._user32.ReleaseCapture()
            self._user32.PostMessageW(hwnd, self.WM_NCLBUTTONDOWN, ht, 0)

        self._invoke_ui(_do, wait=False)
        return True

    def set_auto_dim(self, enabled: bool, opacity: float | None = None) -> dict:
        self.auto_dim = bool(enabled)
        if opacity is not None:
            self.dim_opacity = max(0.45, min(1.0, float(opacity)))
        self._save_state()
        if not self.auto_dim or self.mode == "full":
            self._set_alpha(255)
        return self.get_state()

    def start_background(self):
        if not self._win32_ready or self._started:
            return
        self._started = True

        # Lấy sẵn HWND và gắn sự kiện ResizeEnd trên UI thread để lưu vị trí sau khi kéo/resize
        def _bind_native():
            self._hwnd = _get_window_hwnd(self.window)
            native = _get_native_form(self.window)
            if native is not None:
                try:
                    def _on_resize_end(_sender, _args):
                        self._snapshot_current_bounds()
                    native.ResizeEnd += _on_resize_end
                except Exception:
                    pass

        self._invoke_ui(_bind_native, wait=False)
        threading.Thread(target=self._hotkey_loop, daemon=True, name="kuro-floating-hotkey").start()
        threading.Thread(target=self._auto_dim_loop, daemon=True, name="kuro-floating-autodim").start()

    def stop_background(self):
        self._stop_event.set()
        if self._win32_ready and self._hotkey_thread_id:
            try:
                self._user32.PostThreadMessageW(self._hotkey_thread_id, self.WM_QUIT, 0, 0)
            except Exception:
                pass

    def _hotkey_loop(self):
        import ctypes
        from ctypes import wintypes
        self._hotkey_thread_id = ctypes.windll.kernel32.GetCurrentThreadId()
        ok = self._user32.RegisterHotKey(None, self.HOTKEY_ID, self.MOD_ALT | self.MOD_NOREPEAT, self.VK_K)
        if not ok:
            print("[Floating] Không đăng ký được phím tắt toàn cục Alt+K (có thể bị phần mềm khác chiếm).")
            return
        msg = wintypes.MSG()
        try:
            while not self._stop_event.is_set():
                ret = self._user32.GetMessageW(ctypes.byref(msg), None, 0, 0)
                if ret <= 0:
                    break
                if msg.message == self.WM_HOTKEY and msg.wParam == self.HOTKEY_ID:
                    self.cycle_hotkey_mode()
        finally:
            try:
                self._user32.UnregisterHotKey(None, self.HOTKEY_ID)
            except Exception:
                pass

    def _auto_dim_loop(self):
        import ctypes
        pt = self._POINT()
        rc = self._RECT()
        while not self._stop_event.is_set():
            time.sleep(0.05)
            if self.window is None:
                continue
            if self.mode == "full" or not self.auto_dim:
                if self._current_alpha != 255:
                    self._set_alpha(255)
                continue

            hwnd = self._hwnd
            if not hwnd:
                continue

            hovered = False
            if self._user32.GetCursorPos(ctypes.byref(pt)) and self._user32.GetWindowRect(hwnd, ctypes.byref(rc)):
                hovered = (rc.left <= pt.x <= rc.right) and (rc.top <= pt.y <= rc.bottom)

            fg = self._user32.GetForegroundWindow()
            focused = bool(fg) and ((fg == hwnd) or (self._user32.GetAncestor(fg, 2) == hwnd))

            if hovered or (focused and self.mode == "mini"):
                target = 255
            else:
                factor = min(0.90, self.dim_opacity + 0.08) if self.mode == "bubble" else self.dim_opacity
                target = int(round(255 * factor))

            cur = self._current_alpha
            if cur != target:
                step = 24
                nxt = target if abs(target - cur) <= step else (cur + step if target > cur else cur - step)
                self._set_alpha(nxt)


class DesktopApi:
    """Cầu nối API giữa JavaScript giao diện và hệ điều hành Windows."""
    def __init__(self, floating: FloatingWindowController | None = None):
        self._window = None
        self._floating = floating

    def set_window(self, window):
        self._window = window
        if self._floating is not None:
            self._floating.attach(window)

    def is_desktop_app(self) -> bool:
        """Xác nhận đây là ứng dụng Native Desktop."""
        return True

    def set_titlebar_theme(self, theme: str = "light") -> bool:
        """Đồng bộ màu thanh tiêu đề Windows native theo giao diện Sáng/Tối."""
        norm = _normalize_ui_theme(theme)
        _save_ui_theme(norm)
        if self._floating is not None:
            self._floating.set_theme(norm)
        return _apply_windows_titlebar_theme(self._window, norm)

    def set_floating_mode(self, mode: str = "full", focus_input: bool = False) -> dict:
        """Chuyển chế độ hiển thị: full | mini | bubble."""
        if self._floating is None:
            return {"ok": False, "mode": "full"}
        return self._floating.set_mode(mode, focus_input=bool(focus_input), notify_js=False)

    def get_floating_state(self) -> dict:
        """Lấy trạng thái bóng chat hiện tại (mode, auto_dim, dim_opacity)."""
        if self._floating is None:
            return {"mode": "full", "auto_dim": True, "dim_opacity": 0.72}
        return self._floating.get_state()

    def start_window_drag(self) -> bool:
        """Kéo di chuyển cửa sổ frameless ở chế độ Mini hoặc Bong bóng."""
        return bool(self._floating and self._floating.start_drag())

    def start_window_resize(self, edge: str = "bottom-right") -> bool:
        """Đổi kích thước cửa sổ ở chế độ Mini."""
        return bool(self._floating and self._floating.start_resize(edge))

    def set_floating_auto_dim(self, enabled: bool = True, opacity: float | None = None) -> dict:
        """Bật/tắt và chỉnh mức tự làm mờ khi rời chuột."""
        if self._floating is None:
            return {"mode": "full", "auto_dim": True, "dim_opacity": 0.72}
        return self._floating.set_auto_dim(enabled, opacity)

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
            target_url = f"{base_url}?theme={_load_saved_ui_theme()}" + (f"&_r={int(time.time() * 1000)}" if hard else "")
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

        initial_theme = _load_saved_ui_theme()
        floating = FloatingWindowController(initial_theme=initial_theme)
        api = DesktopApi(floating=floating)
        icon_path = (ROOT / "kuro_logo.ico").resolve()
        icon_str = str(icon_path) if icon_path.is_file() else None

        window = webview.create_window(
            title="Kuro OS - Trợ lý Kỹ sư Hạ tầng",
            # pywebview chạy chế độ riêng tư (xoá localStorage mỗi lần tắt): báo theme đã lưu qua địa chỉ
            url=f"{app_url}/?theme={initial_theme}",
            width=1340,
            height=880,
            min_size=(960, 620),
            background_color=_TITLEBAR_PALETTE[initial_theme]["bg"],
            text_select=True,
            zoomable=True,
            js_api=api
        )
        api.set_window(window)

        def on_shown():
            theme_now = _load_saved_ui_theme()
            floating.set_theme(theme_now)
            _apply_windows_titlebar_theme(window, theme_now)
            floating.start_background()

        def on_closed():
            # Hủy đăng ký phím tắt toàn cục và thoát dứt khoát khi tắt cửa sổ
            floating.stop_background()
            os._exit(0)

        window.events.shown += on_shown
        window.events.closed += on_closed

        # 3. Khởi chạy cửa sổ ứng dụng Windows Native (Edge WebView2)
        webview.start(
            debug=False,
            icon=icon_str
        )
        floating.stop_background()
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
