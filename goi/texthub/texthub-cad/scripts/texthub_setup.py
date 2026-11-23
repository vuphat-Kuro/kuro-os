# -*- coding: utf-8 -*-
"""PKTTC TextHub: kiem tra trang thai, cai, cap nhat, go plugin AutoCAD. Chi dung thu vien chuan cua Python (Windows).

    python texthub_setup.py status                 trang thai (doc, khong ghi gi)
    python texthub_setup.py install [--no-fonts]   cai hoac cap nhat plugin + kho font cho nguoi dung hien tai
    python texthub_setup.py uninstall [--xoa-kho-font]   go plugin (tuy chon: xoa ca kho font do goi cai)
    python texthub_setup.py fonts-install [--font "Arial Unicode MS"]   cai font TrueType tu kho cho nguoi dung hien tai
    python texthub_setup.py fontstore [--set DIR]  xem hoac dat thu muc kho font (%LOCALAPPDATA%\\PKTTC\\fontstore.txt)
Tuy chon chung: --target THU_MUC (chi de thu; mac dinh %APPDATA%\\Autodesk\\ApplicationPlugins).
Kho font cua goi (payload/KhoFont) duoc chep vao %LOCALAPPDATA%\\PKTTC\\KhoFont va them vao fontstore.txt (khong ghi de cau hinh san co).
SHX Unicode (uv-abc.shx, 3T-Unicode.shx, VN_UNI.shx...) nam trong bundle (Contents/Fonts) va tu vao Support File Search Path cua AutoCAD.
Moi lenh in MOT doi tuong JSON (UTF-8) ra stdout; thoat 0 neu lenh thanh cong, 1 neu that bai.
Plugin cai o thu muc cua RIENG nguoi dung, khong can quyen admin. Chi lenh fonts-install ghi registry HKCU (cai font TrueType cho nguoi dung hien tai).
"""
import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

HERE = Path(__file__).resolve().parent
PAYLOAD = HERE.parent / "payload"
KHO_SRC = PAYLOAD / "KhoFont"              # kho font day du di kem goi
BUNDLE = "PKTTC.TextHub.bundle"
KHO_MARKER = ".texthub-khofont"
FONTS_NEEDED = ["Arial Unicode MS"]        # font TrueType dich mac dinh: can co tren may de ve chu Viet dung
FONTS_REG = r"Software\Microsoft\Windows NT\CurrentVersion\Fonts"
FILE_ALIAS = {"arialunicodems": "arialuni"}  # ten ho font chuan hoa -> ten tep chuan hoa
DLL_REL = Path("Contents") / "Windows" / "Pkttc.TextHub.dll"

# Ma ban AutoCAD -> nam (chi de hien thi; ten that doc tu registry). [CAN KIEM TRA voi tung ban]
NAM = {"R22.0": 2018, "R23.0": 2019, "R23.1": 2020, "R24.0": 2021, "R24.1": 2022, "R24.2": 2023, "R24.3": 2024, "R25.0": 2025, "R25.1": 2026}


def default_target():
    return Path(os.environ.get("APPDATA", "")) / "Autodesk" / "ApplicationPlugins"


def series_key(s):
    m = re.fullmatch(r"R?(\d+)\.(\d+)", (s or "").strip())
    return (int(m.group(1)), int(m.group(2))) if m else None


def ver_key(v):
    try:
        return tuple(int(x) for x in re.findall(r"\d+", v or "")[:4])
    except ValueError:
        return ()


# ---------------------------------------------------------------- goi hang
def bundle_info(bundle_dir):
    """Doc PackageContents.xml: phien ban va khoang ban AutoCAD ma moi thanh phan ho tro."""
    x = Path(bundle_dir) / "PackageContents.xml"
    if not x.is_file():
        return None
    root = ET.parse(str(x)).getroot()
    info = {"phien_ban": root.get("AppVersion", ""), "ho_tro": []}
    for comp in root.iter("Components"):
        rr = comp.find("RuntimeRequirements")
        if rr is None:
            continue
        lo, hi = series_key(rr.get("SeriesMin")), series_key(rr.get("SeriesMax"))
        if lo and hi:
            info["ho_tro"].append({"tu": rr.get("SeriesMin"), "den": rr.get("SeriesMax"), "nen_tang": rr.get("Platform", ""),
                                   "dll": [e.get("ModuleName") for e in comp.iter("ComponentEntry")]})
    return info


def verify_manifest(bundle_dir):
    """Kiem SHA-256 moi tep theo MANIFEST.txt. Tra ve danh sach tep sai hoac thieu."""
    bad = []
    mf = Path(bundle_dir) / "MANIFEST.txt"
    if not mf.is_file():
        return ["MANIFEST.txt"]
    for line in mf.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^([0-9A-Fa-f]{64})\s+(.+)$", line)
        if not m:
            continue
        f = Path(bundle_dir) / m.group(2)
        if not f.is_file() or hashlib.sha256(f.read_bytes()).hexdigest().upper() != m.group(1).upper():
            bad.append(m.group(2))
    return bad


# ---------------------------------------------------------------- may nguoi dung
def detect_autocad():
    """Cac ban AutoCAD day du da cai (doc registry HKLM\\SOFTWARE\\Autodesk\\AutoCAD)."""
    found, seen = [], set()
    try:
        import winreg
    except ImportError:
        return found

    def val(k, name):
        try:
            return winreg.QueryValueEx(k, name)[0]
        except OSError:
            return ""

    for view in (winreg.KEY_WOW64_64KEY, winreg.KEY_WOW64_32KEY):
        try:
            root = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Autodesk\AutoCAD", 0, winreg.KEY_READ | view)
        except OSError:
            continue
        i = 0
        while True:
            try:
                series = winreg.EnumKey(root, i)
            except OSError:
                break
            i += 1
            if not series_key(series):
                continue
            try:
                sk = winreg.OpenKey(root, series, 0, winreg.KEY_READ | view)
            except OSError:
                continue
            j = 0
            while True:
                try:
                    prod = winreg.EnumKey(sk, j)
                except OSError:
                    break
                j += 1
                try:
                    pk = winreg.OpenKey(sk, prod, 0, winreg.KEY_READ | view)
                except OSError:
                    continue
                name, loc = val(pk, "ProductName"), val(pk, "AcadLocation")
                if not name or (series, loc) in seen:
                    continue
                seen.add((series, loc))
                found.append({"series": series, "nam": NAM.get(series), "ten": name, "thu_muc": loc,
                              "co_acad_exe": bool(loc) and (Path(loc) / "acad.exe").is_file()})
    return found


def evaluate(cads, support):
    """Gan co ho_tro cho tung ban AutoCAD theo cac thanh phan co trong goi."""
    out = []
    for c in cads:
        k = series_key(c["series"])
        ok = any(series_key(s["tu"]) <= k <= series_key(s["den"]) for s in support)
        ly_do = ""
        if " LT" in (c["ten"] or "") or c["ten"].startswith("AutoCAD LT"):
            ok, ly_do = False, "AutoCAD LT khong nap duoc plugin .NET."
        elif not ok:
            ly_do = "Goi chua co ban dung cho %s (%s); chi ho tro: %s." % (c["series"], c["ten"], ", ".join(s["tu"] + ("" if s["tu"] == s["den"] else "-" + s["den"]) for s in support))
        d = dict(c)
        d["ho_tro"], d["ly_do"] = ok, ly_do
        out.append(d)
    return out


def acad_running():
    try:
        r = subprocess.run(["tasklist", "/FI", "IMAGENAME eq acad.exe", "/FO", "CSV", "/NH"], capture_output=True, text=True, timeout=20,
                           creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        return [int(m.group(1)) for m in re.finditer(r'"acad\.exe","(\d+)"', r.stdout, re.I)]
    except (OSError, subprocess.SubprocessError):
        return []


def dll_locked(bundle_dir):
    p = Path(bundle_dir) / DLL_REL
    if not p.is_file():
        return False
    try:
        with open(str(p), "r+b"):
            return False
    except PermissionError:
        return True
    except OSError:
        return False


def fontstore_state():
    cfg = Path(os.environ.get("LOCALAPPDATA", "")) / "PKTTC" / "fontstore.txt"
    roots = []
    if cfg.is_file():
        for line in cfg.read_text(encoding="utf-8", errors="replace").splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                roots.append(line)
    return {"cau_hinh": str(cfg), "thu_muc": roots, "ton_tai": [r for r in roots if Path(r).is_dir()]}


def bridges():
    try:
        sys.path.insert(0, str(HERE))
        from pkttc_client import find_bridges
        return [{"pid": b.get("pid"), "pipe": b.get("pipe"), "ban_ve": b.get("drawing")} for b in find_bridges()]
    except Exception:  # noqa: BLE001
        return []


# ---------------------------------------------------------------- kho font va font TrueType
def _rmtree(p):
    """Xoa thu muc ke ca tep chi-doc (kho font co tep chi-doc: rmtree thuong bo sot tren Windows)."""
    def _w(fn, path, _exc):
        try:
            os.chmod(path, 0o700)
            fn(path)
        except OSError:
            pass
    shutil.rmtree(str(p), onerror=_w)


def default_khofont_dir():
    return Path(os.environ.get("LOCALAPPDATA", "")) / "PKTTC" / "KhoFont"


def fontstore_cfg():
    return Path(os.environ.get("LOCALAPPDATA", "")) / "PKTTC" / "fontstore.txt"


def _norm(s):
    return "".join(c for c in s.lower() if c not in ". -_")


def khofont_goi():
    """Kho font di kem goi: so tep va dung luong."""
    if not KHO_SRC.is_dir():
        return {"co": False, "so_tep": 0}
    files = [f for f in KHO_SRC.rglob("*") if f.is_file()]
    return {"co": True, "so_tep": len(files), "mb": round(sum(f.stat().st_size for f in files) / 1e6, 1)}


def khofont_da_cai(dest=None):
    d = Path(dest) if dest else default_khofont_dir()
    mk = d / KHO_MARKER
    info = {"thu_muc": str(d), "da_cai": mk.is_file(), "phien_ban": "", "so_tep": 0}
    if mk.is_file():
        try:
            info["phien_ban"] = json.loads(mk.read_text(encoding="utf-8")).get("phien_ban", "")
        except ValueError:
            pass
        info["so_tep"] = sum(1 for f in d.rglob("*") if f.is_file() and f.name != KHO_MARKER)
    return info


def append_fontstore(dest):
    """Them thu muc kho vao fontstore.txt neu chua co; KHONG ghi de, khong doi thu tu cac dong san co (thu muc dau thang khi trung ten tep)."""
    cfg = fontstore_cfg()
    cfg.parent.mkdir(parents=True, exist_ok=True)
    want = str(Path(dest)).rstrip("\\/").lower()
    lines = cfg.read_text(encoding="utf-8", errors="replace").splitlines() if cfg.is_file() else []
    have = [l.strip().rstrip("\\/").lower() for l in lines if l.strip() and not l.strip().startswith("#")]
    if want in have:
        return False
    if not lines:
        lines = ["# Kho font cua phong (PKTTC TextHub). Moi dong mot thu muc; dong bat dau bang # la ghi chu.",
                 "# Thu muc dung truoc thang khi trung ten tep."]
    lines.append(str(Path(dest)))
    cfg.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return True


def install_khofont(dest=None):
    """Chep kho font cua goi vao may nguoi dung. Khong xoa, khong ghi de tep da co (cung dung luong thi bo qua)."""
    if not KHO_SRC.is_dir():
        return {"ok": False, "thong_bao": "Goi khong co kho font (payload/KhoFont)."}
    d = Path(dest) if dest else default_khofont_dir()
    copied = skipped = 0
    for f in sorted(KHO_SRC.rglob("*")):
        if not f.is_file():
            continue
        t = d / f.relative_to(KHO_SRC)
        if t.is_file() and t.stat().st_size == f.stat().st_size:
            skipped += 1
            continue
        t.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(str(f), str(t))      # khong chep thuoc tinh chi-doc cua tep nguon
        copied += 1
    pv = bundle_info(PAYLOAD / BUNDLE)
    (d / KHO_MARKER).write_text(json.dumps({"phien_ban": pv["phien_ban"] if pv else "", "nguon": "goi texthub"}), encoding="utf-8")
    added = append_fontstore(d)
    return {"ok": True, "thu_muc": str(d), "da_chep": copied, "da_co": skipped, "them_vao_fontstore": added}


def font_installed(name, reg_key=FONTS_REG):
    """Font TrueType da cai tren may chua (HKLM va HKCU, theo ten hien thi trong registry)."""
    try:
        import winreg
    except ImportError:
        return False
    for hive in (winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER):
        try:
            k = winreg.OpenKey(hive, reg_key, 0, winreg.KEY_READ)
        except OSError:
            continue
        i = 0
        while True:
            try:
                v = winreg.EnumValue(k, i)[0]
            except OSError:
                break
            i += 1
            if v.lower().startswith(name.lower()):
                return True
    return False


def find_font_file(name, dirs):
    """Tim tep TrueType theo ten ho font trong cac thu muc kho (co bi danh cho ten tep khac ten ho)."""
    key = FILE_ALIAS.get(_norm(name), _norm(name))
    for d in dirs:
        d = Path(d)
        if not d.is_dir():
            continue
        for f in d.rglob("*"):
            if f.is_file() and f.suffix.lower() in (".ttf", ".otf") and _norm(f.stem) == key:
                return f
    return None


def store_dirs():
    cfg = fontstore_cfg()
    dirs = []
    if cfg.is_file():
        for line in cfg.read_text(encoding="utf-8", errors="replace").splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                dirs.append(line)
    for d in (default_khofont_dir(), KHO_SRC):
        if str(d) not in dirs:
            dirs.append(str(d))
    return dirs


def fonts_status():
    dirs = store_dirs()
    out = []
    for n in FONTS_NEEDED:
        f = find_font_file(n, dirs)
        out.append({"ten": n, "da_cai": font_installed(n), "co_trong_kho": bool(f), "tep_trong_kho": str(f) if f else ""})
    return out


def fonts_install(names=None, fonts_dir=None, reg_key=FONTS_REG, dirs=None):
    """Cai font TrueType tu kho cho NGUOI DUNG HIEN TAI: chep vao %LOCALAPPDATA%\\Microsoft\\Windows\\Fonts va ghi HKCU (khong can admin).
    Can mo lai AutoCAD de nhan font moi."""
    import winreg
    names = names or FONTS_NEEDED
    fd = Path(fonts_dir) if fonts_dir else Path(os.environ.get("LOCALAPPDATA", "")) / "Microsoft" / "Windows" / "Fonts"
    res = []
    for n in names:
        if font_installed(n, reg_key):
            res.append({"ten": n, "ket_qua": "da_co"})
            continue
        f = find_font_file(n, dirs or store_dirs())
        if not f:
            res.append({"ten": n, "ket_qua": "khong_co_trong_kho"})
            continue
        fd.mkdir(parents=True, exist_ok=True)
        dst = fd / f.name
        shutil.copy2(str(f), str(dst))
        k = winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, reg_key, 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(k, n + " (TrueType)", 0, winreg.REG_SZ, str(dst))
        winreg.CloseKey(k)
        res.append({"ten": n, "ket_qua": "da_cai", "tep": str(dst)})
    ok = all(r["ket_qua"] in ("da_co", "da_cai") for r in res)
    return {"ok": ok, "font": res, "thong_bao": ("Da cai xong. Mo lai AutoCAD de nhan font moi." if ok else "Co font khong cai duoc (khong co trong kho).")}


# ---------------------------------------------------------------- lenh
def status(target):
    pay = bundle_info(PAYLOAD / BUNDLE)
    res = {"cong_cu": "PKTTC TextHub", "id": "texthub", "phien_ban_goi": pay["phien_ban"] if pay else "", "trang_thai": "loi",
           "thong_bao": "", "goi_y": []}
    if not pay:
        res["thong_bao"] = "Goi hong: khong thay payload\\%s." % BUNDLE
        return res
    bad = verify_manifest(PAYLOAD / BUNDLE)
    res["ho_tro_series"] = pay["ho_tro"]
    cads = evaluate(detect_autocad(), pay["ho_tro"])
    res["autocad"] = cads
    inst_dir = Path(target) / BUNDLE
    inst = bundle_info(inst_dir)
    res["cai_dat"] = {"thu_muc": str(inst_dir), "phien_ban": inst["phien_ban"] if inst else "", "co_ban_cu_de_hoan_tac": (Path(target) / "PKTTC.TextHub.old").exists()}
    pids = acad_running()
    locked = dll_locked(inst_dir) if inst else False
    res["autocad_dang_chay"] = pids
    res["dll_dang_bi_dung"] = locked
    res["kho_font"] = fontstore_state()
    res["kho_font_goi"] = khofont_goi()
    res["kho_font_da_cai"] = khofont_da_cai()
    res["font_can_thiet"] = fonts_status()
    res["cong_kuro_dang_mo"] = bridges()
    if bad:
        res["thong_bao"] = "Goi bi sua hoac thieu tep (MANIFEST khong khop): " + ", ".join(bad)
        return res
    sup = [c for c in cads if c["ho_tro"]]
    if not cads:
        res["trang_thai"], res["thong_bao"] = "khong_co_autocad", "Khong thay AutoCAD day du tren may nay."
    elif not sup:
        res["trang_thai"] = "khong_ho_tro"
        res["thong_bao"] = "Cac ban AutoCAD tren may chua duoc goi ho tro: " + "; ".join(c["ly_do"] for c in cads if c["ly_do"])
    elif not inst:
        res["trang_thai"], res["thong_bao"] = "chua_cai", "Chua cai plugin vao AutoCAD."
        res["goi_y"].append("install")
    else:
        a, b = ver_key(inst["phien_ban"]), ver_key(pay["phien_ban"])
        if a < b:
            res["trang_thai"], res["thong_bao"] = "co_ban_moi", "Da cai %s, goi co ban %s." % (inst["phien_ban"], pay["phien_ban"])
            res["goi_y"].append("install")
        elif a == b:
            res["trang_thai"], res["thong_bao"] = "da_cai", "Da cai ban %s." % inst["phien_ban"]
        else:
            res["trang_thai"], res["thong_bao"] = "da_cai_ban_moi_hon", "May dang co ban %s moi hon goi (%s)." % (inst["phien_ban"], pay["phien_ban"])
    if res["goi_y"] and (pids and locked):
        res["can_dong_autocad_de_cai"] = True
        res["thong_bao"] += " AutoCAD dang mo va dang dung plugin: luu va dong AutoCAD roi moi cai duoc."
    if res["trang_thai"] in ("da_cai", "co_ban_moi"):
        if res["kho_font_goi"]["co"] and not res["kho_font_da_cai"]["da_cai"]:
            res["goi_y"].append("install")          # cai lai de chep kho font cua goi
        elif not res["kho_font"]["ton_tai"]:
            res["goi_y"].append("fontstore")
        if any(f["co_trong_kho"] and not f["da_cai"] for f in res["font_can_thiet"]):
            res["goi_y"].append("fonts-install")
    res["goi_y"] = list(dict.fromkeys(res["goi_y"]))
    return res


def install(target, with_fonts=True, khofont_dir=None):
    pay = bundle_info(PAYLOAD / BUNDLE)
    if not pay:
        return {"ok": False, "thong_bao": "Goi hong: khong thay payload."}
    bad = verify_manifest(PAYLOAD / BUNDLE)
    if bad:
        return {"ok": False, "thong_bao": "Goi bi sua hoac thieu tep (MANIFEST khong khop): " + ", ".join(bad)}
    cads = evaluate(detect_autocad(), pay["ho_tro"])
    if not any(c["ho_tro"] for c in cads) and Path(target) == default_target():
        return {"ok": False, "thong_bao": "Khong co ban AutoCAD nao duoc ho tro tren may. " + " ".join(c["ly_do"] for c in cads if c["ly_do"])}
    target = Path(target)
    dst, old = target / BUNDLE, target / "PKTTC.TextHub.old"
    cur = bundle_info(dst)
    if cur and dll_locked(dst):
        return {"ok": False, "can_dong_autocad": True, "thong_bao": "AutoCAD dang dung TextHub. Luu va dong AutoCAD roi cai lai."}
    target.mkdir(parents=True, exist_ok=True)
    moved = False
    try:
        if old.exists():
            _rmtree(old)
        if dst.exists():
            dst.rename(old)
            moved = True
        shutil.copytree(str(PAYLOAD / BUNDLE), str(dst))
        bad2 = verify_manifest(dst)
        if bad2:
            raise RuntimeError("Tep sau khi chep khong khop: " + ", ".join(bad2))
    except Exception as e:  # noqa: BLE001
        _rmtree(dst)
        if moved and old.exists():
            old.rename(dst)
        return {"ok": False, "thong_bao": "Loi khi cai: %s%s" % (e, ". Da khoi phuc ban cu." if moved else "")}
    out = {"ok": True, "phien_ban": pay["phien_ban"], "ban_cu": cur["phien_ban"] if cur else "", "thu_muc": str(dst),
           "thong_bao": "Da cai TextHub %s. Mo lai AutoCAD de plugin tu nap (go PKTEXTABOUT de kiem tra)." % pay["phien_ban"]}
    if with_fonts and KHO_SRC.is_dir():
        try:
            out["kho_font"] = install_khofont(khofont_dir)
        except OSError as e:
            out["kho_font"] = {"ok": False, "thong_bao": "Khong chep duoc kho font: %s" % e}
            out["thong_bao"] += " Kho font chua chep duoc, chay lai install hoac chep tay payload/KhoFont."
    fonts_thieu = [f["ten"] for f in fonts_status() if not f["da_cai"]]
    if fonts_thieu:
        out["font_chua_cai"] = fonts_thieu
        out["thong_bao"] += " Font TrueType chua co tren may: %s (chay fonts-install, hoac cai tu bang PKTEXTUI)." % ", ".join(fonts_thieu)
    return out


def uninstall(target, xoa_kho_font=False, khofont_dir=None):
    target = Path(target)
    dst, old = target / BUNDLE, target / "PKTTC.TextHub.old"
    if not dst.exists() and not old.exists():
        return {"ok": True, "thong_bao": "Chua cai, khong co gi de go."}
    if dst.exists() and dll_locked(dst):
        return {"ok": False, "can_dong_autocad": True, "thong_bao": "AutoCAD dang dung TextHub. Dong AutoCAD roi go."}
    _rmtree(dst)
    _rmtree(old)
    note = "Da go TextHub. Giu lai: kho font, cau hinh kho font, nhat ky cong, ban sao luu ban ve (_backup)."
    if xoa_kho_font:
        kd = Path(khofont_dir) if khofont_dir else default_khofont_dir()
        if (kd / KHO_MARKER).is_file():       # chi xoa kho do goi nay cai
            _rmtree(kd)
            note = "Da go TextHub va kho font do goi cai. Giu lai: cau hinh fontstore.txt (tro thu muc da xoa, khong anh huong), nhat ky cong, ban sao luu ban ve."
        else:
            note += " Khong xoa kho font vi khong phai kho do goi cai."
    return {"ok": not dst.exists(), "thong_bao": note}


def fontstore(set_dir):
    st = fontstore_state()
    if set_dir is None:
        return {"ok": True, **st}
    d = Path(set_dir)
    if not d.is_dir():
        return {"ok": False, "thong_bao": "Thu muc khong ton tai: %s" % set_dir}
    cfg = Path(st["cau_hinh"])
    cfg.parent.mkdir(parents=True, exist_ok=True)
    cfg.write_text("# Kho font (PKTTC TextHub). Moi dong mot thu muc; dong bat dau bang # la ghi chu.\n" + str(d) + "\n", encoding="utf-8")
    return {"ok": True, "thong_bao": "Da dat kho font: %s" % d, **fontstore_state()}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("lenh", choices=["status", "install", "uninstall", "fontstore", "fonts-install"])
    ap.add_argument("--target", default=str(default_target()))
    ap.add_argument("--set", dest="set_dir", default=None)
    ap.add_argument("--no-fonts", action="store_true", help="install: khong chep kho font")
    ap.add_argument("--khofont-dir", default=None, help="thu muc dich kho font (mac dinh thu muc PKTTC\\KhoFont trong %%LOCALAPPDATA%%)")
    ap.add_argument("--xoa-kho-font", action="store_true", help="uninstall: xoa ca kho font do goi cai")
    ap.add_argument("--font", action="append", default=None, help="fonts-install: ten ho font TrueType (lap lai duoc)")
    a = ap.parse_args(argv)
    if a.lenh == "status":
        r = status(a.target)
    elif a.lenh == "install":
        r = install(a.target, with_fonts=not a.no_fonts, khofont_dir=a.khofont_dir)
    elif a.lenh == "uninstall":
        r = uninstall(a.target, xoa_kho_font=a.xoa_kho_font, khofont_dir=a.khofont_dir)
    elif a.lenh == "fonts-install":
        r = fonts_install(a.font)
    else:
        r = fontstore(a.set_dir)
    sys.stdout.buffer.write((json.dumps(r, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))
    return 0 if r.get("ok", r.get("trang_thai") != "loi") else 1


if __name__ == "__main__":
    sys.exit(main())
