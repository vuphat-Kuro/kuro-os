"""Xử lý tiến trình con trên Windows cho Kuro (không làm gì trên hệ khác).

- an_cua_so(): mọi tiến trình con mặc định chạy KHÔNG hiện cửa sổ console. Kuro Desktop chạy bằng pythonw (không có
  console) nên claude/agy/codex do SDK mở sẽ bị Windows cấp console mới, hiện cửa sổ đen mỗi lượt chat.
- gop_tien_trinh_con(): gom tiến trình này và mọi tiến trình con (claude, MCP, script tính) vào một Job Object
  "tắt khi đóng". Tắt Kuro bằng cách nào (đóng cửa sổ, os._exit, taskkill) thì cả cây con chết theo, không mồ côi.
"""
import subprocess
import sys

CREATE_NO_WINDOW = 0x08000000
CREATE_BREAKAWAY_FROM_JOB = 0x01000000
CREATE_NEW_CONSOLE = 0x00000010
DETACHED_PROCESS = 0x00000008
_job = None   # giữ handle sống đến hết đời tiến trình; đóng handle = Windows giết cả job


def an_cua_so() -> None:
    if sys.platform != "win32" or getattr(subprocess.Popen, "_kuro_an_cua_so", False):
        return
    goc = subprocess.Popen.__init__

    def init(self, *a, **kw):
        co = kw.get("creationflags") or 0
        # Chỗ nào cố ý mở console thật (đăng nhập CLI: CREATE_NEW_CONSOLE) hoặc tách rời (DETACHED) thì giữ nguyên;
        # cờ khác (vd CREATE_BREAKAWAY_FROM_JOB, NEW_PROCESS_GROUP) vẫn phải ẩn cửa sổ
        if not co & (CREATE_NEW_CONSOLE | DETACHED_PROCESS):
            kw["creationflags"] = co | CREATE_NO_WINDOW
        goc(self, *a, **kw)

    subprocess.Popen.__init__ = init
    subprocess.Popen._kuro_an_cua_so = True


def gop_tien_trinh_con() -> None:
    global _job
    if sys.platform != "win32" or _job:
        return
    import ctypes
    from ctypes import wintypes
    k = ctypes.WinDLL("kernel32", use_last_error=True)
    k.CreateJobObjectW.restype = wintypes.HANDLE
    k.CreateJobObjectW.argtypes = [wintypes.LPVOID, wintypes.LPCWSTR]
    k.SetInformationJobObject.argtypes = [wintypes.HANDLE, ctypes.c_int, wintypes.LPVOID, wintypes.DWORD]
    k.AssignProcessToJobObject.argtypes = [wintypes.HANDLE, wintypes.HANDLE]
    k.GetCurrentProcess.restype = wintypes.HANDLE

    class Basic(ctypes.Structure):
        _fields_ = [("PerProcessUserTimeLimit", ctypes.c_int64), ("PerJobUserTimeLimit", ctypes.c_int64),
                    ("LimitFlags", wintypes.DWORD), ("MinimumWorkingSetSize", ctypes.c_size_t),
                    ("MaximumWorkingSetSize", ctypes.c_size_t), ("ActiveProcessLimit", wintypes.DWORD),
                    ("Affinity", ctypes.c_size_t), ("PriorityClass", wintypes.DWORD),
                    ("SchedulingClass", wintypes.DWORD)]

    class Io(ctypes.Structure):
        _fields_ = [(n, ctypes.c_uint64) for n in ("r", "w", "o", "rb", "wb", "ob")]

    class Ext(ctypes.Structure):
        _fields_ = [("Basic", Basic), ("Io", Io), ("ProcessMemoryLimit", ctypes.c_size_t),
                    ("JobMemoryLimit", ctypes.c_size_t), ("PeakProcessMemoryUsed", ctypes.c_size_t),
                    ("PeakJobMemoryUsed", ctypes.c_size_t)]

    h = k.CreateJobObjectW(None, None)
    if not h:
        return
    info = Ext()
    # 0x2000 = KILL_ON_JOB_CLOSE; 0x800 = BREAKAWAY_OK (cho bộ cập nhật tách ra, xem popen_tach_roi)
    info.Basic.LimitFlags = 0x2000 | 0x800
    if k.SetInformationJobObject(h, 9, ctypes.byref(info), ctypes.sizeof(info)) and \
            k.AssignProcessToJobObject(h, k.GetCurrentProcess()):
        _job = h


def popen_tach_roi(args, **kw):
    """Mở tiến trình PHẢI sống sau khi Kuro tắt (bộ cập nhật khởi động lại Kuro): tách khỏi job nếu được."""
    if sys.platform == "win32":
        try:
            return subprocess.Popen(args, **{**kw, "creationflags": kw.get("creationflags", 0) | CREATE_BREAKAWAY_FROM_JOB})
        except OSError:   # job ngoài không cho tách
            pass
    return subprocess.Popen(args, **kw)
