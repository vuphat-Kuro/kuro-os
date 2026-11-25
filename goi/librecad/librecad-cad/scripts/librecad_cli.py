# -*- coding: utf-8 -*-
"""Dung LibreCAD CLI: doi DXF/DWG sang PDF/PNG/SVG, hoac mo ban ve.

    python librecad_cli.py convert <tep.dxf|dwg> --to pdf|png|svg [--out DIR] [--size 1920x1080]
    python librecad_cli.py open <tep>
In MOT doi tuong JSON. Cu phap LibreCAD (nhanh master): `LibreCAD.exe dxf2pdf|dxf2png|dxf2svg -o <tep> [-r WxH] <vao>`;
DWG dung dwg2pdf/dwg2png/dwg2svg, can ban co DWGSUPPORT. [CAN XAC MINH tren ban LibreCAD dang cai]
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

from librecad_setup import find_exe


def out(d, code=0):
    print(json.dumps(d, ensure_ascii=False))
    sys.exit(code)


def main():
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest="cmd", required=True)
    c = sp.add_parser("convert")
    c.add_argument("tep")
    c.add_argument("--to", choices=["pdf", "png", "svg"], default="pdf")
    c.add_argument("--out", default="")
    c.add_argument("--size", default="")
    sp.add_parser("open").add_argument("tep")
    a = ap.parse_args()

    exe, _ = find_exe()
    src = Path(a.tep).resolve()
    if not exe:
        out({"ok": False, "thong_bao": "Chưa cài LibreCAD. Chạy librecad_setup.py install."}, 1)
    if not src.is_file() or src.suffix.lower() not in (".dxf", ".dwg"):
        out({"ok": False, "thong_bao": f"Không phải tệp DXF/DWG: {src}"}, 1)
    if a.cmd == "open":
        subprocess.Popen([str(exe), str(src)])
        out({"ok": True, "thong_bao": f"Đã mở {src.name} trong LibreCAD."})

    dst = Path(a.out).resolve() if a.out else src.parent
    dst.mkdir(parents=True, exist_ok=True)
    tep_ra = dst / f"{src.stem}.{a.to}"
    cmd = [str(exe), f"{src.suffix[1:].lower()}2{a.to}", "-o", str(tep_ra)]
    if a.size and a.to == "png":
        cmd += ["-r", a.size]
    cmd.append(str(src))
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=120)
    ok = r.returncode == 0 and tep_ra.is_file()
    msg = "Xong." if ok else (r.stderr or r.stdout or f"LibreCAD thoát mã {r.returncode}, không thấy tệp ra.").strip()[-400:]
    out({"ok": ok, "tep_ra": str(tep_ra) if ok else "", "lenh": cmd, "thong_bao": msg}, 0 if ok else 1)


if __name__ == "__main__":
    main()
