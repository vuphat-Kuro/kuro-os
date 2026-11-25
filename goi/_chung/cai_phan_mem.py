# -*- coding: utf-8 -*-
"""Cai phan mem portable tu GitHub Release cho cac goi trong goi/ (Windows, khong can quyen admin).

Moi goi co script <app>_setup.py goi `chay(CFG)`:
    status | install | uninstall      (in MOT doi tuong JSON, giao thuc cua server/goi.py)
Cach lam: tai ban portable da GHIM phien ban, kiem SHA-256 theo SHA256SUMS.txt cua chinh release do (khong khop = huy),
giai nen (chan Zip Slip) vao %LOCALAPPDATA%\\Programs\\<Ten>. Tai chay NEN (tep lon): install tra ve ngay,
tien do ghi o state/cai-dat/<id>.json, trang thai 'dang_cai' cho toi khi xong. Chu ky .asc cua hang KHONG duoc kiem.
CFG: id, ten, repo, tag, tien_to (tien to ten tep zip), exe (ten exe chinh), cli (exe CLI hoac None), nhan_cai
"""
import hashlib
import json
import os
import platform
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STATE = ROOT / "state" / "cai-dat"
UA = {"User-Agent": "kuro-os-installer"}
FRESH = 90   # giay: tien do khong cap nhat qua ngan nay = tien trinh da chet


def dest_dir(cfg):
    return Path(os.environ.get("LOCALAPPDATA", str(Path.home()))) / "Programs" / cfg["ten"]


def _pf(cfg):
    return STATE / f"{cfg['id']}.json"


def _read(p):
    try:
        return json.loads(Path(p).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def _write_progress(cfg, d):
    STATE.mkdir(parents=True, exist_ok=True)
    _pf(cfg).write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")


def _roots(cfg):
    """Noi co the co ban cai: thu muc cua Kuro, roi Program Files (ban MSI cai tay)."""
    pf = [os.environ.get(k) for k in ("ProgramFiles", "ProgramFiles(x86)")]
    return [dest_dir(cfg)] + [Path(x) / cfg["ten"] for x in pf if x]


def find_file(cfg, name):
    """Tim exe: thu muc cai cua Kuro, Program Files/<Ten>, cuoi cung PATH."""
    for r in _roots(cfg):
        f = next(r.rglob(name), None) if r.is_dir() else None
        if f:
            return f
    w = shutil.which(name)
    return Path(w) if w else None


def reg_version(cfg):
    """DisplayVersion cua ban cai bang MSI/installer (registry Uninstall), rong neu khong co."""
    try:
        import winreg
        base = "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall"
        for hive, sub in ((winreg.HKEY_LOCAL_MACHINE, base), (winreg.HKEY_LOCAL_MACHINE, base.replace("SOFTWARE", "SOFTWARE\\WOW6432Node")),
                          (winreg.HKEY_CURRENT_USER, base)):
            try:
                with winreg.OpenKey(hive, sub) as k:
                    for i in range(winreg.QueryInfoKey(k)[0]):
                        try:
                            with winreg.OpenKey(k, winreg.EnumKey(k, i)) as e:
                                if str(winreg.QueryValueEx(e, "DisplayName")[0]).strip().lower() == cfg["ten"].lower():
                                    return str(winreg.QueryValueEx(e, "DisplayVersion")[0]).lstrip("vV")
                        except OSError:
                            continue
            except OSError:
                continue
    except ImportError:
        pass
    return ""


def out(d, code=0):
    nhan = {"nhan_cai": cfg_nhan.get("nhan_cai", "Cài đặt"), "nhan_go": cfg_nhan.get("nhan_go", "Gỡ"), "xac_nhan_go": cfg_nhan.get("xac_nhan_go", "")}
    print(json.dumps({**nhan, **d}, ensure_ascii=False))
    sys.exit(code)


cfg_nhan = {}


def installed_version(cfg):
    marker = dest_dir(cfg) / ".kuro-version"
    if marker.is_file():
        return marker.read_text(encoding="utf-8").strip()
    rv = reg_version(cfg)
    if rv:
        return rv
    cli =find_file(cfg, cfg["cli"] or cfg["exe"])
    if cli:
        try:
            r = subprocess.run([str(cli), "--version"], capture_output=True, text=True, timeout=10,
                               creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
            tok = [t for t in (r.stdout or "").split() if t[:1].isdigit() or t[:1] in "vV" and t[1:2].isdigit()]
            if tok:
                return tok[-1].lstrip("vV")
        except (OSError, subprocess.SubprocessError):
            pass
    return "?"


def status(cfg, extra=None):
    prog = _read(_pf(cfg))
    exe = find_file(cfg, cfg["exe"])
    pin = cfg["tag"].lstrip("vV")
    base = {"ok": True, "phien_ban_goi": pin, "goi_y": []}
    if prog and not prog.get("loi") and time.time() - _pf(cfg).stat().st_mtime < FRESH:
        out({**base, "trang_thai": "dang_cai",
             "thong_bao": f"{prog.get('buoc', 'Đang cài')} {prog.get('phan_tram', 0)}%. Bấm \"Làm mới\" để xem tiến độ.", **(extra or {})})
    if prog and prog.get("loi"):
        out({**base, "trang_thai": "loi", "goi_y": ["install"], "thong_bao": "Lần cài trước lỗi: " + prog["loi"]})
    if not exe:
        out({**base, "trang_thai": "chua_cai", "goi_y": ["install"],
             "thong_bao": f"Chưa cài {cfg['ten']}. Sẽ tải bản {cfg['tag']} từ GitHub (có kiểm SHA-256), cài cho riêng bạn, không cần quyền admin.", **(extra or {})})
    ver = installed_version(cfg)
    ngoai = not exe.resolve().is_relative_to(dest_dir(cfg).resolve())   # cai tay (MSI...): khong ep cap nhat
    moi = not ngoai and ver not in ("?", pin)
    out({**base, "trang_thai": "co_ban_moi" if moi else "da_cai", "goi_y": ["install"] if moi else [],
         "cai_dat": {"phien_ban": ver, "duong_dan": str(exe)},
         "thong_bao": f"{cfg['ten']} {ver} có tại {exe.parent}" + (" (cài tay ngoài Kuro)." if ngoai else "."), **(extra or {})})


def _get(url, timeout=30):
    return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout)


def worker(cfg):
    """Chay nen: tai -> kiem hash -> giai nen -> chep vao dest."""
    try:
        arch = "arm64" if platform.machine().upper() in ("ARM64", "AARCH64") else "x64"
        _write_progress(cfg, {"buoc": "Đang tra cứu bản phát hành", "phan_tram": 0})
        rel = json.load(_get(f"https://api.github.com/repos/{cfg['repo']}/releases/tags/{cfg['tag']}"))
        assets = {a["name"]: a for a in rel["assets"]}
        zname = next((n for n in assets if n.startswith(cfg["tien_to"]) and n.endswith(f"windows-{arch}-portable.zip")), None)
        if not zname or "SHA256SUMS.txt" not in assets:
            raise RuntimeError(f"Bản {cfg['tag']} không có tệp portable {arch} hoặc SHA256SUMS.txt.")
        sums = _get(assets["SHA256SUMS.txt"]["browser_download_url"]).read().decode("utf-8", "replace")
        want = next((ln.split()[0].lower() for ln in sums.splitlines() if ln.split()[-1:] == [zname] or ln.split()[-1:] == ["*" + zname]), None)
        if not want:
            raise RuntimeError(f"SHA256SUMS.txt không có dòng cho {zname}: từ chối cài.")
        size = assets[zname]["size"]
        tmp = Path(tempfile.mkdtemp(prefix="kuro-cai-"))
        if shutil.disk_usage(tmp).free < size * 3:
            raise RuntimeError("Không đủ dung lượng trống (cần khoảng 3 lần dung lượng tệp tải).")
        zp, h, got = tmp / zname, hashlib.sha256(), 0
        with _get(assets[zname]["browser_download_url"], 60) as r, open(zp, "wb") as f:
            while chunk := r.read(1 << 20):
                f.write(chunk)
                h.update(chunk)
                got += len(chunk)
                _write_progress(cfg, {"buoc": "Đang tải", "phan_tram": int(got * 90 / size)})
        if h.hexdigest() != want:
            raise RuntimeError("SHA-256 không khớp SHA256SUMS.txt: tệp tải về bị hỏng hoặc bị thay. Đã hủy.")
        _write_progress(cfg, {"buoc": "Đang giải nén", "phan_tram": 92})
        ex = tmp / "x"
        with zipfile.ZipFile(zp) as z:
            for n in z.namelist():
                if not (ex / n).resolve().is_relative_to(ex.resolve()):
                    raise RuntimeError(f"Tệp zip có đường dẫn độc hại: {n}")
            z.extractall(ex)
        main = next(ex.rglob(cfg["exe"]), None)
        if not main:
            raise RuntimeError(f"Không thấy {cfg['exe']} trong gói. Có: " + ", ".join(sorted(p.name for p in ex.rglob("*.exe"))[:8]))
        src, dst = main.parent, dest_dir(cfg)
        if dst.exists():
            shutil.rmtree(dst)   # loi neu app dang chay: bao nguoi dung dong app
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src), str(dst))
        (dst / ".kuro-version").write_text(cfg["tag"].lstrip("vV"), encoding="utf-8")
        shutil.rmtree(tmp, ignore_errors=True)
        _pf(cfg).unlink(missing_ok=True)
    except PermissionError as e:
        _write_progress(cfg, {"loi": f"không ghi/xóa được thư mục cài (đóng {cfg['ten']} nếu đang mở rồi cài lại): {e}"})
    except Exception as e:  # noqa: BLE001 - ghi nguyen nhan cho nguoi dung
        _write_progress(cfg, {"loi": str(e)[:300]})


def chay(cfg):
    cfg_nhan.update({k: cfg.get(k, "") for k in ("nhan_cai", "nhan_go", "xac_nhan_go")})
    act = sys.argv[1] if len(sys.argv) > 1 else "status"
    if act == "status":
        status(cfg)
    elif act == "_worker":
        worker(cfg)
    elif act == "install":
        p = _read(_pf(cfg))
        if p and not p.get("loi") and time.time() - _pf(cfg).stat().st_mtime < FRESH:
            status(cfg)
        _pf(cfg).unlink(missing_ok=True)
        subprocess.Popen([sys.executable, "-X", "utf8", str(Path(sys.argv[0]).resolve()), "_worker"], close_fds=True,
                         stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                         creationflags=0x00000008 | 0x00000200 | 0x08000000)  # DETACHED | NEW_PROCESS_GROUP | NO_WINDOW
        _write_progress(cfg, {"buoc": "Bắt đầu tải", "phan_tram": 0})
        status(cfg, {"thong_bao": "Đã bắt đầu tải và cài ở chế độ nền (tệp lớn). Bấm \"Làm mới\" để xem tiến độ."})
    elif act == "uninstall":
        d = dest_dir(cfg)
        if d.is_dir():
            try:
                shutil.rmtree(d)
            except OSError as e:
                out({"ok": False, "trang_thai": "loi", "thong_bao": f"Không gỡ được (đóng {cfg['ten']} nếu đang mở): {e}"}, 1)
        _pf(cfg).unlink(missing_ok=True)
        ex = find_file(cfg, cfg["exe"])
        status(cfg, {"thong_bao": f"Bản cài tay tại {ex.parent} không do Kuro cài: gỡ trong Cài đặt Windows." if ex else f"Đã gỡ {cfg['ten']}."})
    else:
        out({"ok": False, "trang_thai": "loi", "thong_bao": f"Hành động không hỗ trợ: {act}"}, 1)


def mcp_chay(cfg, exe_name, args, work_dir_name=None, work_flags=None):
    """Chay MCP stdio: tim exe da cai, truyen thang stdin/stdout. work_flags: cac co tro thu muc lam viec (dung {dir})."""
    exe = find_file(cfg, exe_name)
    if not exe:
        sys.stderr.write(f"Chưa cài {cfg['ten']}. Mở Cài đặt > Plugins của Kuro để cài.\n")
        sys.exit(2)
    cmd = [str(exe), *args]
    if work_dir_name:
        wd = Path(os.environ.get(work_dir_name) or (ROOT / "state" / "cong-viec" / cfg["id"]))
        wd.mkdir(parents=True, exist_ok=True)
        cmd += [x.format(dir=str(wd)) for x in (work_flags or [])]
    sys.exit(subprocess.run(cmd).returncode)
