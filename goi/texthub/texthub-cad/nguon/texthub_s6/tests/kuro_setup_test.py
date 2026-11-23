# -*- coding: utf-8 -*-
"""Kiem thu texthub_setup.py cua goi Kuro. Khong dung vao may that: APPDATA/LOCALAPPDATA tro sang thu muc tam, thu muc dich la thu muc tam.
Chay: python kuro_setup_test.py <thu_muc_texthub_da_dong_goi>   (thoat 0 neu dat)"""
import ctypes
import importlib.util
import json
import os
import shutil
import sys
import tempfile
import winreg
from pathlib import Path

pkg = Path(sys.argv[1]).resolve()
tmp = Path(tempfile.mkdtemp(prefix="kuro_setup_test_"))
os.environ["APPDATA"] = str(tmp / "appdata")
os.environ["LOCALAPPDATA"] = str(tmp / "local")
(tmp / "appdata").mkdir()
(tmp / "local").mkdir()

# nap texthub_setup tu BAN SAO trong thu muc tam (de thu sua tep ma khong dong den goi that)
work = tmp / "texthub"
shutil.copytree(str(pkg), str(work))
spec = importlib.util.spec_from_file_location("texthub_setup", str(work / "texthub-cad" / "scripts" / "texthub_setup.py"))
ts = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ts)

_pass = _fail = 0


def check(ok, name, info=""):
    global _pass, _fail
    if ok:
        _pass += 1
        print("  dat  " + name)
    else:
        _fail += 1
        print("  LOI  %s (thuc te: %s)" % (name, info))


FAKE_2020 = [{"series": "R23.1", "nam": 2020, "ten": "AutoCAD 2020 - English", "thu_muc": r"C:\Fake\2020", "co_acad_exe": True}]
FAKE_2023 = [{"series": "R24.2", "nam": 2023, "ten": "AutoCAD 2023 - English", "thu_muc": r"C:\Fake\2023", "co_acad_exe": True}]
FAKE_LT = [{"series": "R24.0", "nam": 2021, "ten": "AutoCAD LT 2021", "thu_muc": r"C:\Fake\LT", "co_acad_exe": True}]
SUP = ts.bundle_info(work / "texthub-cad" / "payload" / "PKTTC.TextHub.bundle")["ho_tro"]
VER = ts.bundle_info(work / "texthub-cad" / "payload" / "PKTTC.TextHub.bundle")["phien_ban"]
target = tmp / "plugins"

print("Doc goi")
check(VER == (work / "texthub-cad" / "payload" / "VERSION").read_text().strip(), "phien ban trong bundle khop payload/VERSION", VER)
check(SUP and SUP[0]["tu"] == "R23.1" and SUP[0]["den"] == "R23.1", "bundle khai ho tro AutoCAD R23.1", SUP)
check(ts.verify_manifest(work / "texthub-cad" / "payload" / "PKTTC.TextHub.bundle") == [], "MANIFEST khop")
check(ts.series_key("R23.1") == (23, 1) and ts.series_key("x") is None, "doc ma ban AutoCAD")
check(ts.ver_key("0.9.1") > ts.ver_key("0.9.0") and ts.ver_key("0.10.0") > ts.ver_key("0.9.1"), "so sanh phien ban theo so (khong theo chuoi)")

print("Ho tro theo ban AutoCAD")
ev = ts.evaluate(FAKE_2020 + FAKE_2023 + FAKE_LT, SUP)
check(ev[0]["ho_tro"] and not ev[0]["ly_do"], "AutoCAD 2020 duoc ho tro")
check(not ev[1]["ho_tro"] and "R24.2" in ev[1]["ly_do"], "AutoCAD 2023 chua ho tro, co ly do", ev[1]["ly_do"])
check(not ev[2]["ho_tro"] and "LT" in ev[2]["ly_do"], "AutoCAD LT khong ho tro", ev[2]["ly_do"])

print("Trang thai")
ts.acad_running = lambda: []
ts.detect_autocad = lambda: []
check(ts.status(str(target))["trang_thai"] == "khong_co_autocad", "may khong co AutoCAD -> khong_co_autocad")
ts.detect_autocad = lambda: list(FAKE_2023)
s = ts.status(str(target))
check(s["trang_thai"] == "khong_ho_tro" and "R24.2" in s["thong_bao"], "chi co AutoCAD 2023 -> khong_ho_tro", s["thong_bao"])
ts.detect_autocad = lambda: list(FAKE_2020)
s = ts.status(str(target))
check(s["trang_thai"] == "chua_cai" and s["goi_y"] == ["install"], "chua cai -> chua_cai, goi y install", (s["trang_thai"], s["goi_y"]))

print("Cai")
r = ts.install(str(target))
check(r["ok"] and r["phien_ban"] == VER and (target / "PKTTC.TextHub.bundle" / "PackageContents.xml").is_file(), "cai vao thu muc dich", r)
check(ts.verify_manifest(target / "PKTTC.TextHub.bundle") == [], "tep sau khi cai khop MANIFEST")
s = ts.status(str(target))
check(s["trang_thai"] == "da_cai" and s["cai_dat"]["phien_ban"] == VER, "sau khi cai -> da_cai", s["trang_thai"])
outside = [f for f in tmp.rglob("*") if f.is_file() and not str(f).startswith(str(work)) and not str(f).startswith(str(target))
           and not str(f).startswith(str(tmp / "local" / "PKTTC"))]
check(outside == [], r"cai khong ghi tep nao ngoai thu muc plugin va %LOCALAPPDATA%\PKTTC", outside[:3])

print("Cap nhat va ban cu")
pc = target / "PKTTC.TextHub.bundle" / "PackageContents.xml"
pc.write_text(pc.read_text(encoding="utf-8").replace('AppVersion="%s"' % VER, 'AppVersion="0.0.1"'), encoding="utf-8")
s = ts.status(str(target))
check(s["trang_thai"] == "co_ban_moi" and "install" in s["goi_y"], "da cai ban thap hon -> co_ban_moi", s["trang_thai"])
r = ts.install(str(target))
check(r["ok"] and r["ban_cu"] == "0.0.1" and (target / "PKTTC.TextHub.old").is_dir(), "cap nhat giu ban cu o .old", r)
pc.write_text(pc.read_text(encoding="utf-8").replace('AppVersion="%s"' % VER, 'AppVersion="99.0.0"'), encoding="utf-8")
check(ts.status(str(target))["trang_thai"] == "da_cai_ban_moi_hon", "da cai ban cao hon goi -> da_cai_ban_moi_hon")
ts.install(str(target))

print("An toan khi cai")
# 1. DLL dang bi khoa (nhu AutoCAD dang dung)
dll = target / "PKTTC.TextHub.bundle" / "Contents" / "Windows" / "Pkttc.TextHub.dll"
k32 = ctypes.windll.kernel32
k32.CreateFileW.restype = ctypes.c_void_p
h = k32.CreateFileW(str(dll), 0x80000000, 1, None, 3, 0, None)   # doc, chi cho phep doc chung (khong cho ghi) = giong anh xa DLL
before = ts.verify_manifest(target / "PKTTC.TextHub.bundle")
r = ts.install(str(target))
check((not r["ok"]) and r.get("can_dong_autocad") is True, "DLL dang bi dung -> tu choi, bao dong AutoCAD", r)
check(ts.verify_manifest(target / "PKTTC.TextHub.bundle") == before == [], "tu choi: ban dang cai nguyen ven")
r2 = ts.uninstall(str(target))
check((not r2["ok"]) and r2.get("can_dong_autocad") is True, "go khi DLL dang bi dung -> tu choi", r2)
k32.CloseHandle(ctypes.c_void_p(h))
# 2. goi bi sua
bad_dll = work / "texthub-cad" / "payload" / "PKTTC.TextHub.bundle" / "Contents" / "Windows" / "Pkttc.TextHub.dll"
data = bytearray(bad_dll.read_bytes()); data[100] ^= 0xFF; bad_dll.write_bytes(bytes(data))
r = ts.install(str(target))
check(not r["ok"] and "MANIFEST" in r["thong_bao"], "goi bi sua -> tu choi cai", r)
check(ts.status(str(target))["trang_thai"] == "loi", "goi bi sua -> status bao loi")
data[100] ^= 0xFF; bad_dll.write_bytes(bytes(data))
# 3. loi giua chung -> khoi phuc ban cu
orig = ts.verify_manifest
calls = {"n": 0}


def flaky(d):
    calls["n"] += 1
    return ["Contents/Windows/Pkttc.TextHub.dll"] if calls["n"] == 2 else orig(d)   # lan 1: kiem goi truoc khi cai; lan 2: kiem sau khi chep


ts.verify_manifest = flaky
r = ts.install(str(target))
ts.verify_manifest = orig
check((not r["ok"]) and "khoi phuc" in r["thong_bao"] and orig(target / "PKTTC.TextHub.bundle") == [], "loi sau khi chep -> khoi phuc ban cu nguyen ven", r)

print("Goi day du: SHX Unicode trong bundle, kho font")
bun = work / "texthub-cad" / "payload" / "PKTTC.TextHub.bundle"
pcx = (bun / "PackageContents.xml").read_text(encoding="utf-8")
check('SupportPath="./Contents/Fonts"' in pcx, "PackageContents khai SupportPath ./Contents/Fonts")
for fn in ("uv-abc.shx", "3T-Unicode.shx", "VN_UNI.shx"):
    check((bun / "Contents" / "Fonts" / fn).is_file(), "bundle co SHX Unicode " + fn)
man = (bun / "MANIFEST.txt").read_text(encoding="utf-8")
check(("Contents" + os.sep + "Fonts" + os.sep + "uv-abc.shx") in man, "MANIFEST gom SHX Unicode")
for fn in ("README.md", "_danh_sach.csv", "SHX", "TTF"):
    check((work / "texthub-cad" / "payload" / "KhoFont" / fn).exists(), "payload/KhoFont co " + fn)
check(ts.find_font_file("Arial Unicode MS", [str(ts.KHO_SRC)]) is not None and ts.find_font_file("Arial Unicode MS", [str(ts.KHO_SRC)]).stat().st_size > 20_000_000,
      "tim thay ARIALUNI.ttf trong kho di kem (ten ho Arial Unicode MS)")
check((work / "texthub-cad" / "nguon" / "texthub_s5" / "src" / "Db" / "Plan.cs").is_file() and (work / "CHANGELOG.md").is_file(), "goi co ma nguon va CHANGELOG")
gj = json.loads((work / "goi.json").read_text(encoding="utf-8"))
check(gj["phien_ban"] == VER and gj["skill"] == "texthub-cad" and (work / gj["skill"] / "SKILL.md").is_file(), "goi.json khop phien ban va thu muc skill", gj.get("phien_ban"))

kd = tmp / "local" / "PKTTC" / "KhoFont"
check((kd / ts.KHO_MARKER).is_file() and (kd / "TTF").is_dir() and (kd / "SHX").is_dir(), r"install da chep kho font vao %LOCALAPPDATA%\PKTTC\KhoFont")
n_goi = ts.khofont_goi()["so_tep"]
check(ts.khofont_da_cai()["da_cai"] and ts.khofont_da_cai()["so_tep"] == n_goi, "so tep kho font da cai bang so tep trong goi", (ts.khofont_da_cai()["so_tep"], n_goi))
fl = ts.fontstore_cfg().read_text(encoding="utf-8").splitlines()
check(fl.count(str(kd)) == 1, "fontstore.txt co dung 1 dong kho font", fl)
r = ts.install_khofont()
check(r["ok"] and r["da_chep"] == 0 and r["da_co"] == n_goi and not r["them_vao_fontstore"], "chay lai: khong chep lai, khong them dong trung", r)
(kd / "TTF" / "tep_cua_nguoi_dung.ttf").write_bytes(b"x")
ts.install_khofont()
check((kd / "TTF" / "tep_cua_nguoi_dung.ttf").is_file(), "chep kho font khong xoa tep nguoi dung them")
# fontstore.txt co san: giu nguyen dong cu, them dong moi o cuoi
KHO_CU = r"D:\KhoCuaToi"
ts.fontstore_cfg().write_text("# cua toi\n" + KHO_CU + "\n", encoding="utf-8")
ts.append_fontstore(kd)
check(ts.fontstore_cfg().read_text(encoding="utf-8").splitlines() == ["# cua toi", KHO_CU, str(kd)], "fontstore.txt co san: giu dong cu, them o cuoi")
# --no-fonts
r = ts.install(str(tmp / "plugins_nf"), with_fonts=False, khofont_dir=str(tmp / "khong_chep"))
check(r["ok"] and not (tmp / "khong_chep").exists(), "install --no-fonts khong chep kho font")
shutil.rmtree(str(tmp / "plugins_nf"), ignore_errors=True)

print("Cai font TrueType")
ts.font_installed.__defaults__   # ham dung duoc
KEY = r"Software\PKTTC_TextHub_Test\Fonts"
fake_store = tmp / "kho_gia"
(fake_store / "TTF").mkdir(parents=True)
(fake_store / "TTF" / "ARIALUNI.ttf").write_bytes(b"giaTTF" * 10)
fdir = tmp / "fonts_user"
try:
    check(not ts.font_installed("Arial Unicode MS", KEY), "khoa thu chua co font")
    r = ts.fonts_install(["Arial Unicode MS"], fonts_dir=str(fdir), reg_key=KEY, dirs=[str(fake_store)])
    check(r["ok"] and (fdir / "ARIALUNI.ttf").is_file() and r["font"][0]["ket_qua"] == "da_cai", "cai font: chep tep va bao da_cai", r)
    k = winreg.OpenKey(winreg.HKEY_CURRENT_USER, KEY)
    val = winreg.QueryValueEx(k, "Arial Unicode MS (TrueType)")[0]
    check(val == str(fdir / "ARIALUNI.ttf"), "cai font: ghi dung gia tri HKCU", val)
    check(ts.font_installed("Arial Unicode MS", KEY), "font_installed thay font vua cai")
    r = ts.fonts_install(["Arial Unicode MS"], fonts_dir=str(fdir), reg_key=KEY, dirs=[str(fake_store)])
    check(r["ok"] and r["font"][0]["ket_qua"] == "da_co", "cai lan hai: da_co, khong lam lai", r)
    r = ts.fonts_install(["Font Khong Co"], fonts_dir=str(fdir), reg_key=KEY, dirs=[str(fake_store)])
    check((not r["ok"]) and r["font"][0]["ket_qua"] == "khong_co_trong_kho", "font khong co trong kho -> bao ro, khong loi", r)
finally:
    for sub in (KEY, r"Software\PKTTC_TextHub_Test"):
        try:
            winreg.DeleteKey(winreg.HKEY_CURRENT_USER, sub)
        except OSError:
            pass
check(not ts.font_installed("Arial Unicode MS", KEY), "da don khoa registry thu")
real = ts.status(str(target))
check(isinstance(real["font_can_thiet"], list) and real["font_can_thiet"][0]["ten"] == "Arial Unicode MS" and real["kho_font_da_cai"]["da_cai"]
      and real["kho_font_goi"]["co"], "status co kho_font_goi, kho_font_da_cai, font_can_thiet")

print("Go va kho font")
r = ts.uninstall(str(target), xoa_kho_font=True)
check(r["ok"] and not kd.exists(), "go --xoa-kho-font: xoa kho do goi cai", r)
kd2 = tmp / "kho_nguoi_dung"
kd2.mkdir()
(kd2 / "a.ttf").write_bytes(b"x")
ts.install(str(target), with_fonts=False)
r = ts.uninstall(str(target), xoa_kho_font=True, khofont_dir=str(kd2))
check(r["ok"] and (kd2 / "a.ttf").is_file() and "khong phai kho do goi cai" in r["thong_bao"], "go --xoa-kho-font: khong dong vao thu muc khong co dau cua goi", r)
r = ts.install(str(target), with_fonts=False)
r = ts.uninstall(str(target))
check(r["ok"] and not (target / "PKTTC.TextHub.bundle").exists() and not (target / "PKTTC.TextHub.old").exists(), "go: xoa bundle va .old", r)
check(ts.uninstall(str(target))["ok"], "go lan hai: bao chua cai, khong loi")
ts.fontstore_cfg().unlink()
fs = ts.fontstore(None)
check(fs["thu_muc"] == [] and not fs["ton_tai"], "chua cau hinh kho font")
store = tmp / "kho"
store.mkdir()
fs = ts.fontstore(str(store))
check(fs["ok"] and fs["ton_tai"] == [str(store)], "dat kho font", fs)
check(not ts.fontstore(str(tmp / "khong_co"))["ok"], "dat kho font tro thu muc khong ton tai -> loi")

shutil.rmtree(str(tmp), ignore_errors=True)
print("\nDat: %d  Loi: %d" % (_pass, _fail))
sys.exit(0 if _fail == 0 else 1)
