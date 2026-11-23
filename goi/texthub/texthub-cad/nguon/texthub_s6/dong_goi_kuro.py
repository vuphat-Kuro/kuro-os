# -*- coding: utf-8 -*-
"""Dung goi `texthub` cho Kuro tu: kuro/ (goi.json, SKILL.md, script, tai lieu) + dist/ (bundle plugin da dong goi bang dong_goi.ps1)
+ texthub_s5/bridge (pkttc_client.py, pkttc_mcp.py) + package/ (tai lieu).  Dau ra: dist_kuro/texthub/ va dist_kuro/PKTTC-TextHub-Kuro-<phien ban>.zip
Chay:  python dong_goi_kuro.py     (chay dong_goi.ps1 truoc de dist/ moi nhat)"""
import json
import os
import shutil
import sys
import zipfile
from pathlib import Path

W = Path(__file__).resolve().parent
SRC = W / "kuro"
DIST = W / "dist"
OUT = W / "dist_kuro"
ROOT = OUT / "texthub"
SKILL = ROOT / "texthub-cad"
KHO = W.parent.parent / "05-ThuVien" / "06-Kho-Font"   # kho font day du cua may nguon
TEMP = W.parent                                          # 99-Temp: chua texthub_s1, s5, s6, s7

# Ma nguon dua vao goi: (thu muc, cac muc lay). Bo bin, obj, dist, test_live, nhat ky, anh chup.
NGUON = {
    "texthub_s1": ["src", "data", "tests", "build.ps1", "tools/build_charsets.py", "tools/extract_tables.py", "tools/doi_chieu.txt"],
    "texthub_s5": ["src", "tests", "bridge", "build.ps1", "run_tests.ps1", "run_tests_apply.ps1", "run_tests_bridge.ps1",
                   "run_tests_idle.ps1", "trial_copy.ps1", "kuro_mcp_config.json", "HUONG_DAN_KURO.md"],
    "texthub_s6": ["src", "tests", "package", "kuro", "dong_goi.ps1", "dong_goi_kuro.py", "run_tests_package.ps1", "VERSION"],
    "texthub_s7": ["ui/drive.ps1", "ui/uia.ps1"],
}
BAO_CAO = ["texthub_s1/KetQua_S1.md", "texthub_s5/KetQua_S5.md", "texthub_s6/KetQua_S6.md", "texthub_s6/KetQua_Kuro.md", "texthub_s7/KetQua_S7.md"]
_BO = shutil.ignore_patterns("__pycache__", "*.pyc", "bin", "obj", "_backup", "*.log", "*.out.txt", "*.err.txt")


def _xoa(p):
    """rmtree chiu duoc tep chi-doc (kho font co tep chi-doc)."""
    def w(fn, path, _e):
        os.chmod(path, 0o700)
        fn(path)
    shutil.rmtree(str(p), onerror=w)


def chep_nguon(dest):
    for d, items in NGUON.items():
        for it in items:
            src = TEMP / d / it
            if not src.exists():
                sys.exit("Thieu nguon: %s" % src)
            dst = dest / d / it
            dst.parent.mkdir(parents=True, exist_ok=True)
            if src.is_dir():
                shutil.copytree(str(src), str(dst), ignore=_BO)
            else:
                shutil.copy2(str(src), str(dst))
    (dest / "bao_cao").mkdir(parents=True, exist_ok=True)
    for b in BAO_CAO:
        src = TEMP / b
        if src.is_file():
            shutil.copy2(str(src), str(dest / "bao_cao" / src.name))
    shutil.copy2(str(SRC / "NGUON.md"), str(dest / "README.md"))


def main():
    ver = (W / "VERSION").read_text(encoding="utf-8").strip()
    bundle = DIST / "PKTTC.TextHub.bundle"
    if not (bundle / "PackageContents.xml").is_file():
        sys.exit("Thieu dist/PKTTC.TextHub.bundle: chay dong_goi.ps1 truoc.")
    if ver not in (bundle / "PackageContents.xml").read_text(encoding="utf-8"):
        sys.exit("Bundle trong dist/ khong khop VERSION %s: chay lai dong_goi.ps1." % ver)

    if OUT.exists():
        _xoa(OUT)
    shutil.copytree(str(SRC), str(ROOT), ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))

    # goi.json: phien ban theo VERSION
    gj = ROOT / "goi.json"
    d = json.loads(gj.read_text(encoding="utf-8"))
    d["phien_ban"] = ver
    gj.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    # script nong tu texthub_s5/bridge (mot nguon duy nhat)
    for f in ("pkttc_client.py", "pkttc_mcp.py"):
        shutil.copy2(str(W.parent / "texthub_s5" / "bridge" / f), str(SKILL / "scripts" / f))

    # payload: bundle plugin + cai tay + VERSION
    pay = SKILL / "payload"
    shutil.copytree(str(bundle), str(pay / "PKTTC.TextHub.bundle"))
    shutil.copy2(str(DIST / "cai_dat.ps1"), str(pay / "cai_dat.ps1"))
    (pay / "VERSION").write_text(ver + "\n", encoding="utf-8")

    # kho font day du (SHX + TTF, gom ARIALUNI.ttf) de may moi khong thieu font
    if not (KHO / "README.md").is_file():
        sys.exit("Thieu kho font: %s" % KHO)
    shutil.copytree(str(KHO), str(pay / "KhoFont"), ignore=shutil.ignore_patterns("_backup", "__pycache__", "*.pyc"),
                    copy_function=shutil.copyfile)

    # ma nguon
    chep_nguon(SKILL / "nguon")

    # tai lieu
    ref = SKILL / "references"
    ref.mkdir(parents=True, exist_ok=True)
    shutil.copy2(str(W / "package" / "HUONG_DAN_SU_DUNG.md"), str(ref / "HUONG_DAN_SU_DUNG.md"))
    cai = (W / "package" / "HUONG_DAN_CAI_DAT.md").read_text(encoding="utf-8")
    note = ("> Trong goi Kuro, plugin duoc cai bang `python scripts/texthub_setup.py install`. Tai lieu nay mo ta cach cai TAY bang PowerShell "
            "(`payload/cai_dat.ps1`), de dung khi can cai ma khong qua Kuro.\n\n")
    (ref / "CAI_DAT_TAY.md").write_text(note + cai, encoding="utf-8")

    ky = ROOT / "texthub-cad" / "payload" / "KhoFont"
    nf = sum(1 for _ in ky.rglob("*") if _.is_file())
    print("Kho font trong goi: %d tep" % nf)
    zp = OUT / ("PKTTC-TextHub-Kuro-%s.zip" % ver)
    with zipfile.ZipFile(str(zp), "w", zipfile.ZIP_DEFLATED) as z:
        for f in sorted(ROOT.rglob("*")):
            if f.is_file():
                z.write(str(f), str(f.relative_to(OUT)))
    n = sum(1 for _ in ROOT.rglob("*") if _.is_file())
    print("Da dong goi Kuro %s: %s (%d tep, %.1f KB)" % (ver, zp, n, zp.stat().st_size / 1024))


if __name__ == "__main__":
    main()
