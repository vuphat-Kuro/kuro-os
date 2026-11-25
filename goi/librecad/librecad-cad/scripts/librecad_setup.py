# -*- coding: utf-8 -*-
"""LibreCAD: kiem tra, cai, go tren may bang winget. Chi dung thu vien chuan (Windows).

    python librecad_setup.py status | install | uninstall
Moi lenh in MOT doi tuong JSON (UTF-8); thoat 0 neu thanh cong. Giao thuc giong texthub_setup.py (server/goi.py goi).
"""
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

WINGET_ID = "LibreCAD.LibreCAD"
NHAN = {"nhan_cai": "Cài LibreCAD (winget)", "nhan_go": "Gỡ LibreCAD",
        "xac_nhan_go": "Gỡ LibreCAD khỏi máy tính này? (bản vẽ của bạn không bị xóa)"}
UNINSTALL = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"


def find_exe():
    """Tim LibreCAD.exe va phien ban: registry Uninstall truoc, roi Program Files, roi PATH."""
    ver, loc = "", ""
    try:
        import winreg
        for hive, sub in ((winreg.HKEY_LOCAL_MACHINE, UNINSTALL),
                          (winreg.HKEY_LOCAL_MACHINE, UNINSTALL.replace("SOFTWARE", r"SOFTWARE\WOW6432Node")),
                          (winreg.HKEY_CURRENT_USER, UNINSTALL)):
            try:
                with winreg.OpenKey(hive, sub) as k:
                    for i in range(winreg.QueryInfoKey(k)[0]):
                        try:
                            with winreg.OpenKey(k, winreg.EnumKey(k, i)) as s:
                                if str(winreg.QueryValueEx(s, "DisplayName")[0]).lower().startswith("librecad"):
                                    ver = ver or str(winreg.QueryValueEx(s, "DisplayVersion")[0])
                                    try:
                                        loc = loc or str(winreg.QueryValueEx(s, "InstallLocation")[0])
                                    except OSError:
                                        pass
                        except OSError:
                            continue
            except OSError:
                continue
    except ImportError:
        pass
    cands = [Path(loc) / "LibreCAD.exe"] if loc else []
    for env in ("ProgramFiles", "ProgramFiles(x86)", "LOCALAPPDATA"):
        if os.environ.get(env):
            cands.append(Path(os.environ[env]) / "LibreCAD" / "LibreCAD.exe")
    w = shutil.which("librecad")
    if w:
        cands.append(Path(w))
    return next((c for c in cands if c.is_file()), None), ver


def out(d, code=0):
    print(json.dumps({**NHAN, **d}, ensure_ascii=False))
    sys.exit(code)


def winget(args, timeout=170):
    w = shutil.which("winget")
    if not w:
        out({"ok": False, "trang_thai": "loi", "thong_bao": "Máy không có winget. Tải LibreCAD thủ công tại https://librecad.org/ rồi cài."}, 1)
    try:
        r = subprocess.run([w, *args, "-e", "--id", WINGET_ID, "--silent", "--accept-source-agreements"],
                           capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=timeout,
                           creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    except subprocess.TimeoutExpired:
        out({"ok": False, "trang_thai": "loi", "thong_bao": "winget quá thời gian (có thể đang chờ hộp thoại quyền quản trị). Thử lại hoặc cài thủ công."}, 1)
    return r.returncode, ((r.stdout + r.stderr).strip().splitlines() or [""])[-1]


def status(extra=None):
    exe, ver = find_exe()
    d = {"ok": True, "trang_thai": "da_cai" if exe else "chua_cai", "goi_y": [] if exe else ["install"]}
    if exe:
        d["cai_dat"] = {"phien_ban": ver or "?", "duong_dan": str(exe)}
        d["thong_bao"] = f"LibreCAD {ver} có tại {exe}."
    else:
        d["thong_bao"] = "Chưa cài LibreCAD. Bấm cài (dùng winget, có thể hiện hộp thoại quyền quản trị)."
    out({**d, **(extra or {})})


def main():
    act = sys.argv[1] if len(sys.argv) > 1 else "status"
    if act == "status":
        status()
    elif act == "install":
        rc, tail = winget(["install"])
        if not find_exe()[0]:
            out({"ok": False, "trang_thai": "loi", "thong_bao": f"winget mã {rc}: {tail}"}, 1)
        status({"thong_bao": "Đã cài LibreCAD."})
    elif act == "uninstall":
        rc, tail = winget(["uninstall"])
        if find_exe()[0]:
            out({"ok": False, "trang_thai": "loi", "thong_bao": f"winget mã {rc}: {tail}"}, 1)
        status({"thong_bao": "Đã gỡ LibreCAD."})
    else:
        out({"ok": False, "trang_thai": "loi", "thong_bao": f"Hành động không hỗ trợ: {act}"}, 1)


if __name__ == "__main__":
    main()
