"""Hỗ trợ đọc danh sách file từ Windows Clipboard (CF_HDROP).
Tương thích 64-bit và 32-bit Windows, không cần thư viện ngoài.
"""
import os
import sys
import time

def get_clipboard_files() -> list[str]:
    """Đọc danh sách đường dẫn file khi người dùng nhấn Ctrl+C trong Windows Explorer."""
    if sys.platform != "win32":
        return []

    try:
        import ctypes
        from ctypes import wintypes

        user32 = ctypes.windll.user32
        shell32 = ctypes.windll.shell32

        CF_HDROP = 15

        user32.OpenClipboard.argtypes = [wintypes.HWND]
        user32.OpenClipboard.restype = wintypes.BOOL
        user32.CloseClipboard.argtypes = []
        user32.CloseClipboard.restype = wintypes.BOOL
        user32.GetClipboardData.argtypes = [wintypes.UINT]
        user32.GetClipboardData.restype = wintypes.HANDLE

        shell32.DragQueryFileW.argtypes = [wintypes.HANDLE, wintypes.UINT, wintypes.LPWSTR, wintypes.UINT]
        shell32.DragQueryFileW.restype = wintypes.UINT

        # Thử mở Clipboard tối đa 5 lần (tránh xung đột nếu tiến trình khác đang giữ clipboard)
        opened = False
        for _ in range(5):
            if user32.OpenClipboard(None):
                opened = True
                break
            time.sleep(0.02)

        if not opened:
            return []

        try:
            hDrop = user32.GetClipboardData(CF_HDROP)
            if not hDrop:
                return []
            count = shell32.DragQueryFileW(hDrop, 0xFFFFFFFF, None, 0)
            files = []
            for i in range(count):
                buf_len = shell32.DragQueryFileW(hDrop, i, None, 0) + 1
                buf = ctypes.create_unicode_buffer(buf_len)
                shell32.DragQueryFileW(hDrop, i, buf, buf_len)
                val = buf.value
                if val:
                    files.append(val)
            return files
        finally:
            user32.CloseClipboard()
    except Exception as e:
        print(f"[system_clipboard] Lỗi đọc clipboard: {e}")
        return []


if __name__ == "__main__":
    print("Clipboard files:", get_clipboard_files())
