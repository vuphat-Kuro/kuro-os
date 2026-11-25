"""
Kuro OS - Bản Demo Bóng Chat Nổi (Phương án 1: Single Window Morph)
===================================================================
Hoàn toàn độc lập, KHÔNG sửa bất kỳ tệp nào của Kuro OS chính thức.

Tính năng trong bản demo:
1. Chuyển đổi 3 trạng thái trên CÙNG 1 cửa sổ (Full <-> Mini Floating <-> Bong bóng tròn).
2. Luôn nổi trên AutoCAD / Revit / Civil 3D / SolidCraft (HWND_TOPMOST).
3. Phím tắt toàn cục Windows: Alt + K (hoạt động ngay cả khi đang vẽ trong phần mềm khác).
4. Tự làm mờ mượt khi rời chuột (Auto-Dim bằng Win32 WS_EX_LAYERED), rê chuột vào tự rõ 100%
   mà không cần click làm mất focus bản vẽ CAD.
5. Ở chế độ Mini: chỉ hiển thị trao đổi Người dùng <-> Phản hồi AI; log công cụ nền gom gọn
   thành 1 dòng trạng thái mảnh có thể bấm mở rộng.
6. Kéo thả & đổi kích thước gốc Windows (native), nhớ vị trí riêng cho từng chế độ.

Cách chạy:
    .venv\\Scripts\\python.exe examples\\demo_floating_chat.py
"""

from __future__ import annotations

import base64
import ctypes
from ctypes import wintypes
import json
import os
from pathlib import Path
import sys
import threading
import time

os.environ["PYTHONUTF8"] = "1"
os.environ["PYTHONIOENCODING"] = "utf-8"

ROOT = Path(__file__).resolve().parent.parent
STATE_FILE = ROOT / "state" / "demo_floating_layout.json"

import webview

# =============================================================================
# HẰNG SỐ WIN32 API
# =============================================================================
GWL_EXSTYLE = -20
WS_EX_LAYERED = 0x00080000
WS_EX_TOOLWINDOW = 0x00000080
LWA_ALPHA = 0x00000002

HWND_TOPMOST = -1
HWND_NOTOPMOST = -2
SWP_NOSIZE = 0x0001
SWP_NOMOVE = 0x0002
SWP_NOZORDER = 0x0004
SWP_NOACTIVATE = 0x0010
SWP_FRAMECHANGED = 0x0020

WM_NCLBUTTONDOWN = 0x00A1
WM_HOTKEY = 0x0312
WM_QUIT = 0x0012

HTCAPTION = 2
HT_EDGE_MAP = {
    "left": 10,         # HTLEFT
    "right": 11,        # HTRIGHT
    "top": 12,          # HTTOP
    "top-left": 13,     # HTTOPLEFT
    "top-right": 14,    # HTTOPRIGHT
    "bottom": 15,       # HTBOTTOM
    "bottom-left": 16,  # HTBOTTOMLEFT
    "bottom-right": 17, # HTBOTTOMRIGHT
}

MOD_ALT = 0x0001
MOD_NOREPEAT = 0x4000
VK_K = 0x4B
HOTKEY_ID = 0x4B55  # 'KU'

DWMWA_WINDOW_CORNER_PREFERENCE = 33
DWMWCP_DEFAULT = 0
DWMWCP_DONOTROUND = 1
DWMWCP_ROUND = 2


class RECT(ctypes.Structure):
    _fields_ = [
        ("left", ctypes.c_long),
        ("top", ctypes.c_long),
        ("right", ctypes.c_long),
        ("bottom", ctypes.c_long),
    ]


class POINT(ctypes.Structure):
    _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]


def _load_logo_data_uri() -> str:
    """Đọc logo Kuro có sẵn để gắn vào bong bóng tròn."""
    for name in ("kuro_os_128.png", "kuro_logo_128.png", "favicon.png"):
        p = ROOT / "dashboard" / name
        if p.is_file():
            try:
                b64 = base64.b64encode(p.read_bytes()).decode("ascii")
                return f"data:image/png;base64,{b64}"
            except Exception:
                pass
    return ""


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


def _get_hwnd(window) -> int:
    native = _get_native_form(window)
    if native is not None:
        try:
            handle = getattr(native, "Handle", None)
            if handle is not None:
                return int(handle.ToInt64()) if hasattr(handle, "ToInt64") else int(handle.ToInt32())
        except Exception:
            pass
    return 0


def _invoke_ui(window, fn, wait: bool = False):
    """Chạy thao tác WinForms an toàn trên UI thread."""
    native = _get_native_form(window)
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
        print(f"[Demo] Lỗi invoke UI: {e}")


class FloatingDemoController:
    """Điều khiển chuyển đổi Full <-> Mini <-> Bubble, Auto-Dim và Hotkey Alt+K."""

    def __init__(self):
        self.window = None
        self.mode = "full"  # full | mini | bubble
        self.theme = "light"  # light | dark
        self.auto_dim = True
        self.dim_opacity = 0.72  # 0.45 .. 1.0
        self._current_alpha = 255
        self._stop_event = threading.Event()
        self._hotkey_thread_id = 0
        self._last_toggle_ts = 0.0
        self._user32 = ctypes.windll.user32
        self._gdi32 = ctypes.windll.gdi32
        self._dwmapi = ctypes.windll.dwmapi
        self._setup_win32_types()
        self._layout = self._load_layout()

    def _setup_win32_types(self):
        """Khai báo chuẩn kiểu 64-bit cho các hàm Win32 để tránh cắt cụt HWND/HRGN trên Windows x64."""
        u32 = self._user32
        g32 = self._gdi32
        dwm = self._dwmapi

        u32.GetWindowLongW.argtypes = [wintypes.HWND, ctypes.c_int]
        u32.GetWindowLongW.restype = ctypes.c_long
        u32.SetWindowLongW.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_long]
        u32.SetWindowLongW.restype = ctypes.c_long
        u32.SetLayeredWindowAttributes.argtypes = [wintypes.HWND, wintypes.COLORREF, wintypes.BYTE, wintypes.DWORD]
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

        dwm.DwmSetWindowAttribute.argtypes = [wintypes.HWND, wintypes.DWORD, ctypes.c_void_p, wintypes.DWORD]
        dwm.DwmSetWindowAttribute.restype = ctypes.c_long

    def attach(self, window):
        self.window = window

    # ------------------------------------------------------------------
    # Lưu / khôi phục vị trí từng chế độ
    # ------------------------------------------------------------------
    def _default_layout(self) -> dict:
        sw, sh = self._get_work_area()
        mini_w, mini_h = 370, 510
        bubble_sz = 64
        full_w = min(1180, max(960, sw - 140))
        full_h = min(760, max(620, sh - 100))
        return {
            "full": {
                "x": max(40, (sw - full_w) // 2),
                "y": max(30, (sh - full_h) // 2),
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

    def _load_layout(self) -> dict:
        base = self._default_layout()
        try:
            if STATE_FILE.is_file():
                saved = json.loads(STATE_FILE.read_text(encoding="utf-8"))
                for k in ("full", "mini", "bubble"):
                    if isinstance(saved.get(k), dict):
                        base[k].update(saved[k])
        except Exception:
            pass
        return base

    def _save_layout(self):
        try:
            STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
            STATE_FILE.write_text(json.dumps(self._layout, indent=2), encoding="utf-8")
        except Exception:
            pass

    def _get_work_area(self) -> tuple[int, int]:
        try:
            rc = RECT()
            SPI_GETWORKAREA = 0x0030
            if ctypes.windll.user32.SystemParametersInfoW(SPI_GETWORKAREA, 0, ctypes.byref(rc), 0):
                w = int(rc.right - rc.left)
                h = int(rc.bottom - rc.top)
                if w > 300 and h > 300:
                    return w, h
        except Exception:
            pass
        return 1920, 1040

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
                    self._save_layout()
        except Exception:
            pass

    def _clamp_bounds(self, x: int, y: int, w: int, h: int) -> tuple[int, int, int, int]:
        try:
            from System.Windows.Forms import Screen
            from System.Drawing import Rectangle
            target_rect = Rectangle(int(x), int(y), int(w), int(h))
            wa = Screen.FromRectangle(target_rect).WorkingArea
            w = max(56, min(int(w), int(wa.Width)))
            h = max(56, min(int(h), int(wa.Height)))
            x = max(int(wa.Left), min(int(x), int(wa.Right) - w))
            y = max(int(wa.Top), min(int(y), int(wa.Bottom) - h))
            return x, y, w, h
        except Exception:
            return int(x), int(y), int(w), int(h)

    # ------------------------------------------------------------------
    # Win32 Helpers: Layered Opacity, TopMost, Corner, Bubble Region
    # ------------------------------------------------------------------
    def _ensure_layered(self, hwnd: int):
        if not hwnd:
            return
        ex = self._user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
        if not (ex & WS_EX_LAYERED):
            self._user32.SetWindowLongW(hwnd, GWL_EXSTYLE, ex | WS_EX_LAYERED)

    def _set_alpha(self, alpha: int):
        hwnd = _get_hwnd(self.window)
        if not hwnd:
            return
        alpha = max(60, min(255, int(alpha)))
        if alpha == self._current_alpha:
            return
        self._ensure_layered(hwnd)
        self._user32.SetLayeredWindowAttributes(hwnd, 0, alpha, LWA_ALPHA)
        self._current_alpha = alpha

    def _set_corner_preference(self, hwnd: int, pref: int):
        if not hwnd:
            return
        try:
            val = ctypes.c_int(pref)
            self._dwmapi.DwmSetWindowAttribute(
                hwnd,
                DWMWA_WINDOW_CORNER_PREFERENCE,
                ctypes.byref(val),
                ctypes.sizeof(val),
            )
        except Exception:
            pass

    def _apply_region(self, hwnd: int, circular: bool):
        if not hwnd:
            return
        try:
            if circular:
                rc = RECT()
                if self._user32.GetWindowRect(hwnd, ctypes.byref(rc)):
                    w = max(1, rc.right - rc.left)
                    h = max(1, rc.bottom - rc.top)
                    rgn = self._gdi32.CreateEllipticRgn(0, 0, w + 1, h + 1)
                    self._user32.SetWindowRgn(hwnd, rgn, True)
            else:
                self._user32.SetWindowRgn(hwnd, 0, True)
        except Exception as e:
            print(f"[Demo] Lỗi áp vùng cửa sổ: {e}")

    def _apply_titlebar_theme(self, theme: str):
        hwnd = _get_hwnd(self.window)
        if not hwnd:
            return
        dark = theme == "dark"
        try:
            dark_val = ctypes.c_int(1 if dark else 0)
            self._dwmapi.DwmSetWindowAttribute(hwnd, 20, ctypes.byref(dark_val), ctypes.sizeof(dark_val))
            caption = 0x001C1009 if dark else 0x00F0E6DF
            text = 0x00FAF0E8 if dark else 0x00361B0E
            for attr, col in ((35, caption), (36, text)):
                c_val = ctypes.c_uint32(col)
                self._dwmapi.DwmSetWindowAttribute(hwnd, attr, ctypes.byref(c_val), ctypes.sizeof(c_val))
        except Exception:
            pass

    # ------------------------------------------------------------------
    # Chuyển đổi 3 chế độ trên CÙNG 1 cửa sổ
    # ------------------------------------------------------------------
    def set_mode(self, new_mode: str, focus_input: bool = False) -> dict:
        if new_mode not in ("full", "mini", "bubble"):
            return {"ok": False, "mode": self.mode}

        old_mode = self.mode

        def _apply():
            native = _get_native_form(self.window)
            if native is None:
                return
            from System.Drawing import Point, Size
            from System.Windows.Forms import FormBorderStyle, FormWindowState

            # Lưu vị trí hiện tại trước khi đổi
            self._snapshot_current_bounds()
            self.mode = new_mode

            if native.WindowState == FormWindowState.Minimized:
                native.WindowState = FormWindowState.Normal

            cfg = self._layout[new_mode]
            if new_mode == "full":
                x, y, w, h = self._clamp_bounds(cfg["x"], cfg["y"], cfg["w"], cfg["h"])
                native.SuspendLayout()
                native.TopMost = False
                native.FormBorderStyle = FormBorderStyle.Sizable
                native.MinimumSize = Size(900, 580)
                native.Location = Point(x, y)
                native.Size = Size(w, h)
                native.ResumeLayout(True)

                hwnd = _get_hwnd(self.window)
                self._apply_region(hwnd, circular=False)
                self._set_corner_preference(hwnd, DWMWCP_DEFAULT)
                self._apply_titlebar_theme(self.theme)
                self._set_alpha(255)
                native.Activate()

            elif new_mode == "mini":
                x, y, w, h = self._clamp_bounds(
                    cfg["x"], cfg["y"], max(310, cfg["w"]), max(340, cfg["h"])
                )
                native.SuspendLayout()
                native.WindowState = FormWindowState.Normal
                native.MinimumSize = Size(300, 320)
                native.FormBorderStyle = getattr(FormBorderStyle, "None")
                native.Location = Point(x, y)
                native.Size = Size(w, h)
                native.TopMost = True
                native.ResumeLayout(True)

                hwnd = _get_hwnd(self.window)
                self._apply_region(hwnd, circular=False)
                self._set_corner_preference(hwnd, DWMWCP_ROUND)
                self._user32.SetWindowPos(
                    hwnd, HWND_TOPMOST, 0, 0, 0, 0,
                    SWP_NOMOVE | SWP_NOSIZE | SWP_FRAMECHANGED
                )
                self._set_alpha(255)
                if focus_input or old_mode == "bubble":
                    native.Activate()

            elif new_mode == "bubble":
                # Nếu đang từ mini thu thành bubble, giữ neo gần góc phải trên/dưới của mini nếu chưa từng kéo bubble
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

                hwnd = _get_hwnd(self.window)
                self._set_corner_preference(hwnd, DWMWCP_DONOTROUND)
                self._user32.SetWindowPos(
                    hwnd, HWND_TOPMOST, 0, 0, 0, 0,
                    SWP_NOMOVE | SWP_NOSIZE | SWP_NOACTIVATE | SWP_FRAMECHANGED
                )
                self._apply_region(hwnd, circular=True)

            # Đồng bộ giao diện web bên trong WebView2
            js_focus = "true" if (focus_input and new_mode == "mini") else "false"
            try:
                self.window.evaluate_js(
                    f"window.__applyDemoMode && window.__applyDemoMode({json.dumps(new_mode)}, {js_focus});"
                )
            except Exception:
                pass

        _invoke_ui(self.window, _apply, wait=False)
        return {"ok": True, "mode": new_mode}

    def cycle_hotkey_mode(self):
        """
        Chu trình phím tắt toàn cục Alt + K:
        - full   -> mini   (thu gọn ngay để vẽ CAD)
        - mini   -> bubble (thu thành bóng tròn nhường toàn bộ màn hình CAD)
        - bubble -> mini   (bung khung chat và focus thẳng vào ô nhập)
        """
        now = time.monotonic()
        if now - self._last_toggle_ts < 0.18:
            return
        self._last_toggle_ts = now

        if self.mode == "full":
            self.set_mode("mini", focus_input=True)
        elif self.mode == "mini":
            self.set_mode("bubble", focus_input=False)
        else:
            self.set_mode("mini", focus_input=True)

    # ------------------------------------------------------------------
    # Kéo thả & Resize chuẩn native Windows (không giật lag)
    # ------------------------------------------------------------------
    def start_drag(self) -> bool:
        if self.mode == "full":
            return False

        def _do():
            hwnd = _get_hwnd(self.window)
            if not hwnd:
                return
            self._user32.ReleaseCapture()
            self._user32.SendMessageW(hwnd, WM_NCLBUTTONDOWN, HTCAPTION, 0)
            self._snapshot_current_bounds()

        _invoke_ui(self.window, _do, wait=False)
        return True

    def start_resize(self, edge: str = "bottom-right") -> bool:
        if self.mode != "mini":
            return False
        ht = HT_EDGE_MAP.get(edge, 17)

        def _do():
            hwnd = _get_hwnd(self.window)
            if not hwnd:
                return
            self._user32.ReleaseCapture()
            self._user32.SendMessageW(hwnd, WM_NCLBUTTONDOWN, ht, 0)
            self._snapshot_current_bounds()

        _invoke_ui(self.window, _do, wait=False)
        return True

    def set_auto_dim(self, enabled: bool, opacity: float | None = None) -> dict:
        self.auto_dim = bool(enabled)
        if opacity is not None:
            self.dim_opacity = max(0.45, min(1.0, float(opacity)))
        if not self.auto_dim or self.mode == "full":
            self._set_alpha(255)
        return {"ok": True, "auto_dim": self.auto_dim, "dim_opacity": self.dim_opacity}

    def set_theme(self, theme: str) -> bool:
        self.theme = "dark" if theme == "dark" else "light"
        _invoke_ui(self.window, lambda: self._apply_titlebar_theme(self.theme), wait=False)
        return True

    def close_demo(self):
        self.stop_background()
        os._exit(0)

    # ------------------------------------------------------------------
    # Luồng nền: 1) Global Hotkey Alt + K   2) Auto-Dim theo vị trí chuột
    # ------------------------------------------------------------------
    def start_background(self):
        threading.Thread(target=self._hotkey_loop, daemon=True, name="kuro-demo-hotkey").start()
        threading.Thread(target=self._auto_dim_loop, daemon=True, name="kuro-demo-autodim").start()

    def stop_background(self):
        self._stop_event.set()
        if self._hotkey_thread_id:
            try:
                self._user32.PostThreadMessageW(self._hotkey_thread_id, WM_QUIT, 0, 0)
            except Exception:
                pass

    def _hotkey_loop(self):
        kernel32 = ctypes.windll.kernel32
        self._hotkey_thread_id = kernel32.GetCurrentThreadId()
        ok = self._user32.RegisterHotKey(None, HOTKEY_ID, MOD_ALT | MOD_NOREPEAT, VK_K)
        if not ok:
            print("[Demo] Không đăng ký được phím tắt toàn cục Alt+K (có thể phần mềm khác đang chiếm).")
            return
        msg = wintypes.MSG()
        try:
            while not self._stop_event.is_set():
                ret = self._user32.GetMessageW(ctypes.byref(msg), None, 0, 0)
                if ret <= 0:
                    break
                if msg.message == WM_HOTKEY and msg.wParam == HOTKEY_ID:
                    self.cycle_hotkey_mode()
        finally:
            try:
                self._user32.UnregisterHotKey(None, HOTKEY_ID)
            except Exception:
                pass

    def _auto_dim_loop(self):
        pt = POINT()
        rc = RECT()
        while not self._stop_event.is_set():
            time.sleep(0.05)
            if self.window is None:
                continue
            if self.mode == "full" or not self.auto_dim:
                if self._current_alpha != 255:
                    self._set_alpha(255)
                continue

            hwnd = _get_hwnd(self.window)
            if not hwnd:
                continue

            # Sáng 100% khi chuột đang nằm trên cửa sổ HOẶC cửa sổ đang được focus (đang gõ)
            hovered = False
            if self._user32.GetCursorPos(ctypes.byref(pt)) and self._user32.GetWindowRect(hwnd, ctypes.byref(rc)):
                hovered = (rc.left <= pt.x <= rc.right) and (rc.top <= pt.y <= rc.bottom)

            fg = self._user32.GetForegroundWindow()
            focused = bool(fg) and ((fg == hwnd) or (self._user32.GetAncestor(fg, 2) == hwnd))  # GA_ROOT = 2

            if hovered or (focused and self.mode == "mini"):
                target = 255
            else:
                # Bubble hơi rõ hơn mini một chút để dễ thấy chấm thông báo
                factor = min(0.90, self.dim_opacity + 0.08) if self.mode == "bubble" else self.dim_opacity
                target = int(round(255 * factor))

            # Chuyển mượt (fade) thay vì giật cục
            cur = self._current_alpha
            if cur != target:
                step = 24
                if abs(target - cur) <= step:
                    nxt = target
                else:
                    nxt = cur + step if target > cur else cur - step
                self._set_alpha(nxt)


class DemoApi:
    """Cầu nối JS <-> Python trong bản demo."""

    def __init__(self, ctrl: FloatingDemoController):
        self._ctrl = ctrl

    def set_mode(self, mode: str, focus_input: bool = False):
        return self._ctrl.set_mode(mode, focus_input=focus_input)

    def start_drag(self):
        return self._ctrl.start_drag()

    def start_resize(self, edge: str = "bottom-right"):
        return self._ctrl.start_resize(edge)

    def set_auto_dim(self, enabled: bool, opacity: float | None = None):
        return self._ctrl.set_auto_dim(enabled, opacity)

    def set_theme(self, theme: str):
        return self._ctrl.set_theme(theme)

    def close_demo(self):
        self._ctrl.close_demo()
        return True


def build_html(logo_uri: str) -> str:
    logo_img = (
        f'<img src="{logo_uri}" alt="Kuro" class="logo-img" draggable="false">'
        if logo_uri
        else '<span class="logo-fallback">K</span>'
    )
    return f"""<!doctype html>
<html lang="vi">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Kuro OS - Demo Bóng Chat Nổi</title>
<style>
  :root {{
    --bg: #dfe6f0;
    --surface: #f4f7fb;
    --card: #ffffff;
    --navy: #15264b;
    --navy-mid: #1f3566;
    --accent: #c82822;
    --accent-soft: rgba(200, 40, 34, 0.10);
    --text: #15264b;
    --text-2: #344157;
    --muted: #64748b;
    --line: rgba(21, 38, 75, 0.16);
    --line-hi: rgba(21, 38, 75, 0.30);
    --user-bg: linear-gradient(135deg, #e7f0fc, #dce8fa);
    --user-border: rgba(21, 38, 75, 0.22);
    --bot-bg: #ffffff;
    --pill-bg: #eef3fa;
    --green: #14845f;
    --amber: #b85d0b;
    --shadow: 0 10px 28px rgba(15, 28, 54, 0.18);
    --font: "Segoe UI", system-ui, -apple-system, sans-serif;
  }}

  body.theme-dark {{
    --bg: #09101c;
    --surface: #0f1a2e;
    --card: #132138;
    --navy: #e8f0fa;
    --navy-mid: #c5d6ee;
    --accent: #ef4444;
    --accent-soft: rgba(239, 68, 68, 0.16);
    --text: #e8f0fa;
    --text-2: #b9c9e0;
    --muted: #7f95b5;
    --line: rgba(148, 178, 218, 0.18);
    --line-hi: rgba(148, 178, 218, 0.34);
    --user-bg: linear-gradient(135deg, #1b3257, #172b4b);
    --user-border: rgba(96, 165, 250, 0.30);
    --bot-bg: #122036;
    --pill-bg: rgba(148, 178, 218, 0.12);
    --green: #34d399;
    --amber: #fbbf24;
    --shadow: 0 12px 32px rgba(0, 0, 0, 0.45);
  }}

  * {{ box-sizing: border-box; }}
  html, body {{
    margin: 0; padding: 0; width: 100%; height: 100%;
    font: 13.5px/1.52 var(--font);
    color: var(--text);
    background: var(--bg);
    overflow: hidden;
    user-select: none;
  }}

  /* =====================================================================
     BỐ CỤC CHẾ ĐỘ ĐẦY ĐỦ (MÔ PHỎNG KURO OS)
     ===================================================================== */
  .app-shell {{
    display: flex; width: 100%; height: 100%;
    background: var(--bg);
    position: relative;
  }}

  .sidebar {{
    width: 270px; flex: none; display: flex; flex-direction: column;
    background: var(--surface); border-right: 1px solid var(--line);
    padding: 14px 12px; gap: 12px;
  }}
  .brand {{
    display: flex; align-items: center; gap: 10px; padding: 4px 6px 10px;
    border-bottom: 1px solid var(--line);
  }}
  .brand-logo {{
    width: 40px; height: 40px; border-radius: 50%; background: #15264b;
    display: flex; align-items: center; justify-content: center; overflow: hidden;
    border: 2px solid var(--accent); flex: none;
  }}
  .logo-img {{ width: 100%; height: 100%; object-fit: contain; display: block; }}
  .logo-fallback {{ color: #fff; font-weight: 800; font-size: 18px; }}
  .brand-text b {{ display: block; font-size: 15px; letter-spacing: 0.08em; }}
  .brand-text small {{ color: var(--muted); font-size: 11px; }}

  .side-section-title {{
    font-size: 11px; font-weight: 700; text-transform: uppercase;
    letter-spacing: 0.08em; color: var(--muted); padding: 0 6px;
  }}
  .side-list {{ display: flex; flex-direction: column; gap: 5px; }}
  .side-item {{
    padding: 8px 10px; border-radius: 9px; font-size: 12.5px;
    background: transparent; color: var(--text-2); border: 1px solid transparent;
    display: flex; align-items: center; justify-content: space-between;
  }}
  .side-item.active {{
    background: var(--card); border-color: var(--line); color: var(--text); font-weight: 600;
  }}
  .side-badge {{
    font-size: 10.5px; padding: 2px 7px; border-radius: 99px;
    background: var(--accent-soft); color: var(--accent); font-weight: 600;
  }}

  .demo-guide {{
    margin-top: auto; padding: 10px 11px; border-radius: 10px;
    background: var(--card); border: 1px dashed var(--line-hi);
    font-size: 12px; color: var(--text-2); line-height: 1.5;
  }}
  .demo-guide b {{ color: var(--text); }}
  .kbd {{
    display: inline-block; padding: 1px 6px; border-radius: 5px;
    background: var(--pill-bg); border: 1px solid var(--line);
    font-family: Consolas, monospace; font-size: 11px; font-weight: 700;
  }}

  /* Cột chat chính */
  .main-pane {{
    flex: 1; min-width: 0; display: flex; flex-direction: column;
    background: var(--surface); position: relative;
  }}

  /* Thanh trên cùng ở chế độ Đầy đủ */
  .full-topbar {{
    height: 52px; flex: none; display: flex; align-items: center; justify-content: space-between;
    padding: 0 16px; border-bottom: 1px solid var(--line); background: var(--card);
    gap: 10px;
  }}
  .topbar-left {{ display: flex; align-items: center; gap: 10px; min-width: 0; }}
  .session-dot {{
    width: 9px; height: 9px; border-radius: 50%; background: var(--green); flex: none;
  }}
  .session-dot.busy {{
    background: var(--amber);
    box-shadow: 0 0 0 4px rgba(251, 191, 36, 0.25);
    animation: pulse 1.1s infinite;
  }}
  .topbar-title {{ font-weight: 700; font-size: 14px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
  .topbar-sub {{ font-size: 11.5px; color: var(--muted); }}
  .topbar-actions {{ display: flex; align-items: center; gap: 8px; flex: none; }}

  .btn {{
    border: 1px solid var(--line); background: var(--surface); color: var(--text);
    padding: 6px 11px; border-radius: 8px; font: 600 12.5px/1 var(--font);
    cursor: pointer; display: inline-flex; align-items: center; gap: 6px;
    transition: all 0.14s ease;
  }}
  .btn:hover {{ border-color: var(--line-hi); background: var(--card); }}
  .btn-primary {{
    background: var(--accent); border-color: var(--accent); color: #fff;
  }}
  .btn-primary:hover {{ filter: brightness(1.06); background: var(--accent); color: #fff; }}

  /* Thanh tiêu đề siêu mỏng chỉ hiện ở chế độ MINI */
  .mini-topbar {{
    display: none; height: 36px; flex: none; align-items: center; justify-content: space-between;
    padding: 0 8px 0 10px; gap: 6px;
    background: var(--card); border-bottom: 1px solid var(--line);
    cursor: grab;
  }}
  .mini-topbar:active {{ cursor: grabbing; }}
  .mini-drag-area {{
    flex: 1; min-width: 0; height: 100%; display: flex; align-items: center; gap: 7px;
  }}
  .mini-avatar {{
    width: 20px; height: 20px; border-radius: 50%; overflow: hidden;
    background: #15264b; border: 1.5px solid var(--accent); flex: none;
    display: flex; align-items: center; justify-content: center;
  }}
  .mini-title {{
    font-size: 12px; font-weight: 700; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
  }}
  .mini-controls {{ display: flex; align-items: center; gap: 3px; flex: none; }}
  .icon-btn {{
    width: 25px; height: 25px; border-radius: 6px; border: 1px solid transparent;
    background: transparent; color: var(--text-2); cursor: pointer;
    display: inline-flex; align-items: center; justify-content: center;
    font-size: 12px; font-weight: 700; padding: 0; transition: all 0.12s;
  }}
  .icon-btn:hover {{ background: var(--pill-bg); color: var(--text); border-color: var(--line); }}
  .icon-btn.active {{ background: var(--accent-soft); color: var(--accent); border-color: rgba(200,40,34,0.3); }}
  .opacity-chip {{
    height: 23px; padding: 0 7px; border-radius: 99px; border: 1px solid var(--line);
    background: var(--pill-bg); color: var(--text-2); font-size: 11px; font-weight: 700;
    cursor: pointer; display: inline-flex; align-items: center; gap: 4px;
  }}
  .opacity-chip:hover {{ border-color: var(--line-hi); color: var(--text); }}

  /* Khu vực tin nhắn */
  .chat-scroll {{
    flex: 1; min-height: 0; overflow-y: auto; padding: 14px 16px;
    display: flex; flex-direction: column; gap: 11px;
    user-select: text;
  }}
  .chat-scroll::-webkit-scrollbar {{ width: 5px; }}
  .chat-scroll::-webkit-scrollbar-thumb {{ background: var(--line-hi); border-radius: 4px; }}

  .msg {{ display: flex; flex-direction: column; max-width: 88%; gap: 4px; }}
  .msg.user {{ align-self: flex-end; align-items: flex-end; }}
  .msg.bot {{ align-self: flex-start; align-items: flex-start; max-width: 94%; }}
  .msg-meta {{ font-size: 10.5px; color: var(--muted); padding: 0 4px; font-weight: 600; }}
  .msg-bubble {{
    padding: 9px 12px; border-radius: 13px; border: 1px solid var(--line);
    background: var(--bot-bg); color: var(--text); word-break: break-word;
    box-shadow: 0 1px 2px rgba(15, 28, 54, 0.05);
  }}
  .msg.user .msg-bubble {{
    background: var(--user-bg); border-color: var(--user-border);
    border-bottom-right-radius: 4px;
  }}
  .msg.bot .msg-bubble {{
    border-bottom-left-radius: 4px;
  }}
  .msg-bubble p {{ margin: 0 0 6px; }}
  .msg-bubble p:last-child {{ margin-bottom: 0; }}
  .msg-bubble ul {{ margin: 4px 0 0 18px; padding: 0; }}
  .msg-bubble li {{ margin: 2px 0; }}
  .msg-bubble code {{
    font-family: Consolas, monospace; font-size: 12px;
    padding: 1px 5px; border-radius: 4px; background: var(--pill-bg);
  }}

  /* Dòng tóm tắt bước chạy tool (mặc định thu gọn 1 dòng cực mảnh) */
  .tool-summary {{
    margin-bottom: 6px; border-radius: 7px; background: var(--pill-bg);
    border: 1px solid var(--line); font-size: 11.5px; color: var(--muted);
    overflow: hidden;
  }}
  .tool-summary-head {{
    padding: 4px 8px; cursor: pointer; display: flex; align-items: center;
    justify-content: space-between; gap: 6px; user-select: none;
  }}
  .tool-summary-head:hover {{ color: var(--text); }}
  .tool-summary-body {{
    display: none; padding: 5px 8px 6px; border-top: 1px solid var(--line);
    font-family: Consolas, monospace; font-size: 11px; line-height: 1.45;
    color: var(--text-2); white-space: pre-wrap;
  }}
  .tool-summary.open .tool-summary-body {{ display: block; }}

  /* Thanh gợi ý nhanh (chỉ hiện nhẹ để test demo) */
  .quick-bar {{
    flex: none; display: flex; gap: 6px; padding: 6px 12px 0;
    overflow-x: auto; scrollbar-width: none;
  }}
  .quick-bar::-webkit-scrollbar {{ display: none; }}
  .quick-chip {{
    flex: none; padding: 4px 9px; border-radius: 99px; font-size: 11.5px;
    border: 1px solid var(--line); background: var(--card); color: var(--text-2);
    cursor: pointer; white-space: nowrap;
  }}
  .quick-chip:hover {{ border-color: var(--accent); color: var(--accent); }}

  /* Ô nhập tin nhắn */
  .composer {{
    flex: none; padding: 8px 12px 10px; border-top: 1px solid var(--line);
    background: var(--card); display: flex; align-items: flex-end; gap: 7px;
  }}
  .composer textarea {{
    flex: 1; resize: none; min-height: 36px; max-height: 92px;
    padding: 8px 10px; border-radius: 10px; border: 1px solid var(--line);
    background: var(--surface); color: var(--text); font: 13px/1.4 var(--font);
    outline: none;
  }}
  .composer textarea:focus {{ border-color: var(--accent); }}
  .send-btn {{
    width: 36px; height: 36px; border-radius: 10px; border: none;
    background: var(--accent); color: #fff; cursor: pointer; flex: none;
    display: inline-flex; align-items: center; justify-content: center;
    font-size: 15px; font-weight: 700;
  }}
  .send-btn:hover {{ filter: brightness(1.07); }}
  .send-btn.stop {{ background: #475569; }}

  /* Viền kéo đổi kích thước cho chế độ MINI (frameless) */
  .resize-handle {{ display: none; position: fixed; z-index: 60; }}
  body.mode-mini .resize-handle {{ display: block; }}
  .rh-n {{ top: 0; left: 8px; right: 8px; height: 5px; cursor: ns-resize; }}
  .rh-s {{ bottom: 0; left: 8px; right: 8px; height: 5px; cursor: ns-resize; }}
  .rh-w {{ left: 0; top: 8px; bottom: 8px; width: 5px; cursor: ew-resize; }}
  .rh-e {{ right: 0; top: 8px; bottom: 8px; width: 5px; cursor: ew-resize; }}
  .rh-se {{ right: 0; bottom: 0; width: 14px; height: 14px; cursor: nwse-resize; }}
  .rh-sw {{ left: 0; bottom: 0; width: 12px; height: 12px; cursor: nesw-resize; }}
  .rh-ne {{ right: 0; top: 0; width: 12px; height: 12px; cursor: nesw-resize; }}
  .rh-nw {{ left: 0; top: 0; width: 12px; height: 12px; cursor: nwse-resize; }}

  /* =====================================================================
     CHẾ ĐỘ MINI FLOATING (CHỈ CÒN CHAT NHỎ GỌN)
     ===================================================================== */
  body.mode-mini .sidebar,
  body.mode-mini .full-topbar {{
    display: none !important;
  }}
  body.mode-mini .mini-topbar {{
    display: flex;
  }}
  body.mode-mini .app-shell {{
    border: 1px solid var(--line-hi);
  }}
  body.mode-mini .chat-scroll {{
    padding: 10px 10px 8px; gap: 8px; font-size: 13px;
  }}
  body.mode-mini .msg-meta {{ display: none; }}
  body.mode-mini .msg-bubble {{ padding: 7px 10px; border-radius: 11px; }}
  body.mode-mini .quick-bar {{ padding: 5px 8px 0; }}
  body.mode-mini .composer {{ padding: 7px 8px 8px; }}
  body.mode-mini .composer textarea {{ min-height: 34px; padding: 7px 9px; font-size: 12.5px; }}

  /* =====================================================================
     CHẾ ĐỘ BONG BÓNG TRÒN (64x64)
     ===================================================================== */
  .bubble-view {{
    display: none; width: 100%; height: 100%;
    align-items: center; justify-content: center;
    background: radial-gradient(circle at 30% 25%, #243f75, #122142 75%);
    position: relative; cursor: pointer;
    border-radius: 50%;
    border: 2.5px solid var(--accent);
    overflow: hidden;
  }}
  .bubble-view.busy {{
    border-color: #fbbf24;
    animation: bubblePulse 1.2s infinite;
  }}
  .bubble-inner {{
    width: 44px; height: 44px; border-radius: 50%; overflow: hidden;
    display: flex; align-items: center; justify-content: center;
    pointer-events: none;
  }}
  .bubble-badge {{
    display: none; position: absolute; top: 6px; right: 7px;
    width: 13px; height: 13px; border-radius: 50%;
    background: #ef4444; border: 2px solid #ffffff;
    box-shadow: 0 0 6px rgba(239, 68, 68, 0.8);
  }}
  .bubble-view.unread .bubble-badge {{ display: block; }}

  body.mode-bubble .app-shell,
  body.mode-bubble .resize-handle {{
    display: none !important;
  }}
  body.mode-bubble .bubble-view {{
    display: flex;
  }}

  @keyframes pulse {{
    0%, 100% {{ transform: scale(1); opacity: 1; }}
    50% {{ transform: scale(1.22); opacity: 0.72; }}
  }}
  @keyframes bubblePulse {{
    0%, 100% {{ box-shadow: inset 0 0 0 2px rgba(251, 191, 36, 0.55); }}
    50% {{ box-shadow: inset 0 0 0 6px rgba(251, 191, 36, 0.95); }}
  }}
</style>
</head>
<body class="mode-full">

<!-- GIAO DIỆN FULL & MINI (CHUNG 1 DOM, CHUYỂN TỨC THÌ) -->
<div class="app-shell">
  <aside class="sidebar">
    <div class="brand">
      <div class="brand-logo">{logo_img}</div>
      <div class="brand-text">
        <b>KURO OS</b>
        <small>Demo Bóng Chat Nổi (PA1)</small>
      </div>
    </div>

    <div class="side-section-title">Phiên đang mở</div>
    <div class="side-list">
      <div class="side-item active">
        <span>Dựng hình dầm Super-T</span>
        <span class="side-badge">Live</span>
      </div>
      <div class="side-item">
        <span>Kiểm tra cốt thép trụ T3</span>
      </div>
      <div class="side-item">
        <span>Xuất bản vẽ mặt cắt cống</span>
      </div>
    </div>

    <div class="demo-guide">
      <b>Cách thử nhanh trên máy:</b><br>
      1. Bấm <b>Thu gọn bóng chat</b> hoặc nhấn <span class="kbd">Alt + K</span>.<br>
      2. Mở AutoCAD / Revit / trình duyệt phía sau.<br>
      3. Rời chuột ra ngoài xem khung tự mờ; rê chuột vào tự rõ 100%.<br>
      4. Nhấn <span class="kbd">Alt + K</span> lần nữa để thu thành <b>bong bóng tròn</b>, nhấn tiếp để bung lại.
    </div>
  </aside>

  <main class="main-pane">
    <!-- Topbar cho chế độ Đầy đủ -->
    <header class="full-topbar">
      <div class="topbar-left">
        <span class="session-dot" id="dot-full"></span>
        <div>
          <div class="topbar-title">Dựng hình dầm Super-T - Bản Demo Phương án 1</div>
          <div class="topbar-sub">Nhấn Alt + K bất kỳ lúc nào (kể cả khi đang đứng trong CAD)</div>
        </div>
      </div>
      <div class="topbar-actions">
        <button class="btn" id="btn-theme-full" title="Đổi giao diện Sáng/Tối">Sáng / Tối</button>
        <button class="btn btn-primary" id="btn-to-mini">Thu gọn bóng chat (Alt+K)</button>
      </div>
    </header>

    <!-- Topbar cực mỏng chỉ hiện khi ở chế độ Mini -->
    <header class="mini-topbar" id="mini-topbar">
      <div class="mini-drag-area" id="mini-drag-area" title="Giữ chuột để kéo di chuyển">
        <div class="mini-avatar">{logo_img}</div>
        <span class="session-dot" id="dot-mini"></span>
        <span class="mini-title">Kuro - Dựng hình CAD</span>
      </div>
      <div class="mini-controls">
        <button class="opacity-chip" id="btn-opacity" title="Đổi mức tự làm mờ khi rời chuột (100% = tắt tự mờ)">Mờ 72%</button>
        <button class="icon-btn" id="btn-theme-mini" title="Đổi Sáng / Tối">◐</button>
        <button class="icon-btn" id="btn-to-bubble" title="Thu thành bong bóng tròn (Alt+K / Esc)">○</button>
        <button class="icon-btn" id="btn-to-full" title="Mở rộng về giao diện đầy đủ">⤢</button>
      </div>
    </header>

    <!-- Nội dung trao đổi Người dùng <-> AI -->
    <section class="chat-scroll" id="chat-scroll"></section>

    <!-- Các lệnh mô phỏng nhanh để test streaming và trạng thái bong bóng -->
    <div class="quick-bar">
      <button class="quick-chip" data-prompt="Dựng mặt cắt dầm Super-T L=38.2m và kiểm tra bề rộng bản cánh">⚡ Mô phỏng vẽ dầm Super-T</button>
      <button class="quick-chip" data-prompt="Đổi chiều dày bản bụng thành 160mm rồi cập nhật lại bản vẽ">⚡ Sửa kích thước & cập nhật CAD</button>
      <button class="quick-chip" data-prompt="Tóm tắt khối lượng bê tông và cốt thép dự kiến cho 1 phiến dầm">⚡ Hỏi nhanh khối lượng</button>
    </div>

    <!-- Ô nhập -->
    <div class="composer">
      <textarea id="chat-input" rows="1" placeholder="Nhập lệnh cho Kuro... (Enter để gửi, Alt+K thu gọn)"></textarea>
      <button class="send-btn" id="btn-send" title="Gửi">➤</button>
    </div>
  </main>
</div>

<!-- GIAO DIỆN BONG BÓNG TRÒN 64x64 -->
<div class="bubble-view" id="bubble-view" title="Click: Mở khung chat | Kéo: Di chuyển | Chuột phải: Mở đầy đủ">
  <div class="bubble-inner">{logo_img}</div>
  <span class="bubble-badge"></span>
</div>

<!-- CÁC VIỀN KÉO ĐỔI KÍCH THƯỚC CHO CHẾ ĐỘ MINI -->
<div class="resize-handle rh-n" data-edge="top"></div>
<div class="resize-handle rh-s" data-edge="bottom"></div>
<div class="resize-handle rh-w" data-edge="left"></div>
<div class="resize-handle rh-e" data-edge="right"></div>
<div class="resize-handle rh-nw" data-edge="top-left"></div>
<div class="resize-handle rh-ne" data-edge="top-right"></div>
<div class="resize-handle rh-sw" data-edge="bottom-left"></div>
<div class="resize-handle rh-se" data-edge="bottom-right"></div>

<script>
(function() {{
  const chatScroll = document.getElementById("chat-scroll");
  const chatInput = document.getElementById("chat-input");
  const btnSend = document.getElementById("btn-send");
  const bubbleView = document.getElementById("bubble-view");
  const dotFull = document.getElementById("dot-full");
  const dotMini = document.getElementById("dot-mini");
  const btnOpacity = document.getElementById("btn-opacity");

  let currentMode = "full";
  let currentTheme = "light";
  let isStreaming = false;
  let streamTimer = null;

  const opacityPresets = [
    {{ label: "Mờ 72%", enabled: true, val: 0.72 }},
    {{ label: "Mờ 55%", enabled: true, val: 0.55 }},
    {{ label: "Mờ 86%", enabled: true, val: 0.86 }},
    {{ label: "Rõ 100%", enabled: false, val: 1.0 }},
  ];
  let opacityIdx = 0;

  function api() {{
    return window.pywebview && window.pywebview.api ? window.pywebview.api : null;
  }}

  function setBusy(busy) {{
    isStreaming = busy;
    dotFull.classList.toggle("busy", busy);
    dotMini.classList.toggle("busy", busy);
    bubbleView.classList.toggle("busy", busy);
    btnSend.textContent = busy ? "■" : "➤";
    btnSend.classList.toggle("stop", busy);
    btnSend.title = busy ? "Dừng phản hồi" : "Gửi";
  }}

  window.__applyDemoMode = function(mode, focusInput) {{
    currentMode = mode;
    document.body.classList.remove("mode-full", "mode-mini", "mode-bubble");
    document.body.classList.add("mode-" + mode);
    if (mode !== "bubble") {{
      bubbleView.classList.remove("unread");
      requestAnimationFrame(() => {{
        chatScroll.scrollTop = chatScroll.scrollHeight;
        if (focusInput) chatInput.focus();
      }});
    }}
  }};

  function switchMode(mode, focusInput = false) {{
    const a = api();
    if (a) a.set_mode(mode, !!focusInput);
    else window.__applyDemoMode(mode, focusInput);
  }}

  function toggleTheme() {{
    currentTheme = currentTheme === "light" ? "dark" : "light";
    document.body.classList.toggle("theme-dark", currentTheme === "dark");
    const a = api();
    if (a) a.set_theme(currentTheme);
  }}

  function cycleOpacity() {{
    opacityIdx = (opacityIdx + 1) % opacityPresets.length;
    const p = opacityPresets[opacityIdx];
    btnOpacity.textContent = p.label;
    const a = api();
    if (a) a.set_auto_dim(p.enabled, p.val);
  }}

  // Render tin nhắn sạch (chỉ User <-> AI + 1 dòng tool gọn)
  function appendMessage(role, text, toolLog) {{
    const wrap = document.createElement("div");
    wrap.className = "msg " + role;

    const meta = document.createElement("div");
    meta.className = "msg-meta";
    meta.textContent = role === "user" ? "Bạn" : "Kuro";
    wrap.appendChild(meta);

    const bubble = document.createElement("div");
    bubble.className = "msg-bubble";

    if (role === "bot" && toolLog) {{
      const ts = document.createElement("div");
      ts.className = "tool-summary";
      ts.innerHTML =
        '<div class="tool-summary-head">' +
          '<span class="ts-label">⚙ ' + toolLog.summary + '</span>' +
          '<span>▾</span>' +
        '</div>' +
        '<div class="tool-summary-body">' + toolLog.detail + '</div>';
      ts.querySelector(".tool-summary-head").addEventListener("click", () => {{
        ts.classList.toggle("open");
      }});
      bubble.appendChild(ts);
    }}

    const body = document.createElement("div");
    body.className = "msg-body";
    body.innerHTML = formatSimple(text);
    bubble.appendChild(body);

    wrap.appendChild(bubble);
    chatScroll.appendChild(wrap);
    chatScroll.scrollTop = chatScroll.scrollHeight;
    return {{ wrap, body, bubble }};
  }}

  function formatSimple(str) {{
    const esc = str
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;");
    return esc
      .replace(/`([^`]+)`/g, "<code>$1</code>")
      .replace(/\\*\\*([^*]+)\\*\\*/g, "<b>$1</b>")
      .replace(/\\n/g, "<br>");
  }}

  function stopStreaming() {{
    if (streamTimer) {{
      clearInterval(streamTimer);
      streamTimer = null;
    }}
    setBusy(false);
  }}

  function simulateReply(prompt) {{
    stopStreaming();
    setBusy(true);

    const lower = prompt.toLowerCase();
    let toolInfo = {{
      summary: "Đã kiểm tra ngữ cảnh bản vẽ (2 bước)",
      detail: "[1] read_active_view() -> CAD / 3D Model\\n[2] check_parameters() -> OK (0 cảnh báo)",
    }};
    let fullReply =
      "Mình đã nhận yêu cầu: **" + prompt + "**\\n\\n" +
      "- Trong chế độ **Mini**, khung chat chỉ giữ trao đổi chính để không che vùng vẽ.\\n" +
      "- Bạn có thể rời chuột ra bản vẽ CAD: khung sẽ tự mờ còn **72%**, rê chuột lại tự sáng **100%**.\\n" +
      "- Bấm `Alt + K` bất cứ lúc nào để thu thành bong bóng tròn hoặc bung ra gõ tiếp.";

    if (lower.includes("super-t") || lower.includes("dầm")) {{
      toolInfo = {{
        summary: "Đã dựng hình mặt cắt Super-T (3 bước CAD)",
        detail: "[1] sketch_profile(L=38.2m, H=1.75m, B_top=2.36m)\\n[2] extrude_girder(solid='Dam_SuperT_38m2')\\n[3] verify_clearances() -> Đạt kích thước danh định",
      }};
      fullReply =
        "Đã dựng xong mặt cắt **dầm Super-T (L = 38.2 m)**.\\n" +
        "- Chiều cao dầm `H = 1.75 m`, bề rộng bản mặt cầu `B = 2.36 m`.\\n" +
        "- Bề rộng sườn tiêu chuẩn đã khớp bản vẽ mẫu; bạn kiểm tra trực tiếp trên màn hình CAD phía sau nhé.";
    }} else if (lower.includes("160") || lower.includes("bản bụng") || lower.includes("cập nhật")) {{
      toolInfo = {{
        summary: "Đã cập nhật tham số bản bụng (2 bước)",
        detail: "[1] set_parameter('web_thickness', 160)\\n[2] rebuild_model() -> Thành công (0.4s)",
      }};
      fullReply =
        "Đã đổi chiều dày bản bụng sang `160 mm` và tái tạo khối 3D.\\n" +
        "- Nếu cần xuất mặt cắt 2D sang DWG hoặc kiểm tra lại trọng lượng bản thân, nhắn mình ngay trên khung này.";
    }} else if (lower.includes("khối lượng")) {{
      toolInfo = {{
        summary: "Đã tính nhanh bằng Python (đối chiếu 2 cách)",
        detail: "[1] tinh_python: diện tích tiết diện A = 0.892 m2\\n[2] V_bt = 0.892 * 38.2 = 34.07 m3 (chưa trừ lỗ cáp)",
      }};
      fullReply =
        "Ước tính nhanh cho 1 phiến dầm Super-T `L = 38.2 m` (cần đối chiếu bản vẽ chi tiết đầu dầm):\\n" +
        "- Bê tông C45/C50: khoảng `34.1 m3`.\\n" +
        "- Trọng lượng bản thân: khoảng `85.2 tấn` (với `2.5 T/m3`).";
    }}

    const msg = appendMessage("bot", "Đang xử lý...", {{
      summary: "Đang thực thi lệnh nền...",
      detail: toolInfo.detail,
    }});

    const chunks = fullReply.split(" ");
    let idx = 0;
    let built = "";

    setTimeout(() => {{
      const tsLabel = msg.bubble.querySelector(".ts-label");
      if (tsLabel) tsLabel.textContent = "⚙ " + toolInfo.summary;
      streamTimer = setInterval(() => {{
        if (idx >= chunks.length) {{
          stopStreaming();
          if (currentMode === "bubble") {{
            bubbleView.classList.add("unread");
          }}
          return;
        }}
        built += (idx === 0 ? "" : " ") + chunks[idx++];
        msg.body.innerHTML = formatSimple(built);
        chatScroll.scrollTop = chatScroll.scrollHeight;
      }}, 38);
    }}, 550);
  }}

  function sendCurrentInput() {{
    if (isStreaming) {{
      stopStreaming();
      return;
    }}
    const text = chatInput.value.trim();
    if (!text) return;
    chatInput.value = "";
    chatInput.style.height = "auto";
    appendMessage("user", text);
    simulateReply(text);
  }}

  // Dữ liệu mẫu ban đầu
  appendMessage("user", "Mở chế độ bóng chat gọn để mình vừa theo dõi dựng hình vừa nhắn lệnh nhé.");
  appendMessage(
    "bot",
    "Sẵn sàng! Bạn bấm **Thu gọn bóng chat** ở góc trên hoặc nhấn `Alt + K` để chuyển sang khung nổi trên CAD.\\n\\n" +
    "- Ở chế độ **Mini**: chỉ giữ tin nhắn của bạn và phản hồi của mình; các bước tool nền gom gọn thành 1 dòng xám.\\n" +
    "- Di chuột ra ngoài vùng vẽ CAD để thấy hiệu ứng **tự làm mờ**, rê chuột lại sẽ tự sáng rõ **100%**.",
    {{
      summary: "Đã sẵn sàng chế độ nổi trên CAD (3 tùy chọn)",
      detail: "- TopMost: bật tự động ở Mini & Bong bóng\\n- Auto-Dim: mặc định 72% khi rời chuột\\n- Global Hotkey: Alt + K (Full -> Mini -> Bong bóng -> Mini)",
    }}
  );

  // Sự kiện nút bấm
  document.getElementById("btn-to-mini").addEventListener("click", () => switchMode("mini", true));
  document.getElementById("btn-to-bubble").addEventListener("click", () => switchMode("bubble", false));
  document.getElementById("btn-to-full").addEventListener("click", () => switchMode("full", false));
  document.getElementById("btn-theme-full").addEventListener("click", toggleTheme);
  document.getElementById("btn-theme-mini").addEventListener("click", toggleTheme);
  btnOpacity.addEventListener("click", cycleOpacity);
  btnSend.addEventListener("click", sendCurrentInput);

  document.querySelectorAll(".quick-chip").forEach((chip) => {{
    chip.addEventListener("click", () => {{
      const p = chip.getAttribute("data-prompt");
      if (!p) return;
      appendMessage("user", p);
      simulateReply(p);
    }});
  }});

  chatInput.addEventListener("keydown", (e) => {{
    if (e.key === "Enter" && !e.shiftKey) {{
      e.preventDefault();
      sendCurrentInput();
    }}
  }});
  chatInput.addEventListener("input", () => {{
    chatInput.style.height = "auto";
    chatInput.style.height = Math.min(92, chatInput.scrollHeight) + "px";
  }});

  // Phím Esc khi đang ở Mini -> thu nhanh về bong bóng tròn
  window.addEventListener("keydown", (e) => {{
    if (e.key === "Escape" && currentMode === "mini") {{
      switchMode("bubble", false);
    }}
  }});

  // Kéo di chuyển ở chế độ Mini
  document.getElementById("mini-drag-area").addEventListener("mousedown", (e) => {{
    if (e.button !== 0) return;
    const a = api();
    if (a) a.start_drag();
  }});
  document.getElementById("mini-drag-area").addEventListener("dblclick", () => {{
    switchMode("full", false);
  }});

  // Kéo viền/góc đổi kích thước ở chế độ Mini
  document.querySelectorAll(".resize-handle").forEach((el) => {{
    el.addEventListener("mousedown", (e) => {{
      if (e.button !== 0) return;
      const edge = el.getAttribute("data-edge") || "bottom-right";
      const a = api();
      if (a) a.start_resize(edge);
    }});
  }});

  // Bong bóng tròn: phân biệt Click mở Mini vs Kéo di chuyển + Chuột phải mở Full
  let bubbleDown = null;
  let bubbleDragged = false;
  bubbleView.addEventListener("mousedown", (e) => {{
    if (e.button !== 0) return;
    bubbleDown = {{ x: e.screenX, y: e.screenY }};
    bubbleDragged = false;
  }});
  window.addEventListener("mousemove", (e) => {{
    if (!bubbleDown || bubbleDragged) return;
    const dx = Math.abs(e.screenX - bubbleDown.x);
    const dy = Math.abs(e.screenY - bubbleDown.y);
    if (dx > 5 || dy > 5) {{
      bubbleDragged = true;
      bubbleDown = null;
      const a = api();
      if (a) a.start_drag();
    }}
  }});
  window.addEventListener("mouseup", () => {{
    if (bubbleDown && !bubbleDragged && currentMode === "bubble") {{
      bubbleDown = null;
      switchMode("mini", true);
    }} else {{
      bubbleDown = null;
      bubbleDragged = false;
    }}
  }});
  bubbleView.addEventListener("contextmenu", (e) => {{
    e.preventDefault();
    switchMode("full", false);
  }});
}})();
</script>
</body>
</html>
"""


def main():
    if sys.platform == "win32":
        try:
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("kuro.os.floating.demo.v1")
        except Exception:
            pass

    ctrl = FloatingDemoController()
    api = DemoApi(ctrl)
    html = build_html(_load_logo_data_uri())
    icon_path = (ROOT / "kuro_logo.ico").resolve()
    icon_str = str(icon_path) if icon_path.is_file() else None

    full_cfg = ctrl._layout["full"]
    win = webview.create_window(
        title="Kuro OS - Demo Bóng Chat Nổi (Phương án 1)",
        html=html,
        width=full_cfg["w"],
        height=full_cfg["h"],
        min_size=(900, 580),
        background_color="#dfe6f0",
        text_select=True,
        js_api=api,
    )
    ctrl.attach(win)

    def on_shown():
        ctrl._apply_titlebar_theme("light")
        ctrl.start_background()

    def on_closed():
        ctrl.stop_background()
        os._exit(0)

    win.events.shown += on_shown
    win.events.closed += on_closed

    webview.start(debug=False, icon=icon_str)
    ctrl.stop_background()
    os._exit(0)


if __name__ == "__main__":
    main()
