# -*- coding: utf-8 -*-
"""Goi mot phuong thuc cua cong TextHub trong AutoCAD dang mo (khong can MCP). Chi dung thu vien chuan.

    python texthub_cad.py ping
    python texthub_cad.py scan --json {"items":"flagged","limit":50}
    python texthub_cad.py plan.create --json {"fontMap":{".VnAvantH":"Arial Unicode MS"}}
    python texthub_cad.py plan.apply --json {"planId":"...","note":"Doi chu cu sang Unicode"} --timeout 300
    python texthub_cad.py plan.create --json-file tham_so.json      (khuyen dung: tranh loi dau nhay tren dong lenh Windows)
    echo {"limit":5} | python texthub_cad.py scan --json -           (doc JSON tu stdin)

Phuong thuc: ping, scan, fonts, plan.create, plan.get, plan.apply, fontsub.plan, fontsub.apply, purge.plan, purge.apply, shutdown.
In MOT doi tuong JSON ra stdout. Thoat 0 neu thanh cong; 2 neu loi (kem "goi_y").
Cac phuong thuc GHI (plan.apply, fontsub.apply, purge.apply) CHO nguoi dung bam Yes/No trong AutoCAD: dat --timeout lon.
Cong chi mo khi nguoi dung go PKTEXTBRIDGE (hoac bam "Mo cong Kuro" trong bang PKTEXTUI, the Tro ly).
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pkttc_client import BridgeError, Client, find_bridges  # noqa: E402

METHODS = ["ping", "scan", "fonts", "plan.create", "plan.get", "plan.apply", "fontsub.plan", "fontsub.apply", "purge.plan", "purge.apply", "shutdown"]
WRITES = {"plan.apply", "fontsub.apply", "purge.apply"}


def out(obj, code):
    sys.stdout.buffer.write((json.dumps(obj, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))
    return code


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("phuong_thuc", choices=METHODS)
    ap.add_argument("--json", dest="params", default="{}", help="tham so dang JSON; '-' = doc tu stdin")
    ap.add_argument("--json-file", dest="params_file", default=None, help="tep JSON chua tham so (UTF-8); uu tien hon --json")
    ap.add_argument("--timeout", type=int, default=0, help="giay cho tra loi (mac dinh 120; phuong thuc ghi 600)")
    ap.add_argument("--pipe", default=None, help="ten pipe (mac dinh: cong moi nhat dang mo)")
    ap.add_argument("--client", default="Kuro")
    a = ap.parse_args(argv)
    try:
        if a.params_file:
            raw = Path(a.params_file).read_text(encoding="utf-8-sig")
        elif a.params == "-":
            raw = sys.stdin.buffer.read().decode("utf-8-sig")
        else:
            raw = a.params
        params = json.loads(raw)
        if not isinstance(params, dict):
            raise ValueError("phai la doi tuong JSON")
    except (ValueError, OSError) as e:
        return out({"loi": "tham_so", "thong_bao": "Tham so --json khong hop le: %s" % e}, 2)
    timeout = a.timeout or (600 if a.phuong_thuc in WRITES else 120)
    try:
        c = Client(pipe=a.pipe, client_name=a.client)
        return out(c.call(a.phuong_thuc, params, timeout=timeout), 0)
    except BridgeError as e:
        goi_y = ""
        if e.code in ("no-bridge", "connect"):
            goi_y = "Cong chua mo. Nho nguoi dung trong AutoCAD (mo dung ban ve can lam) go PKTEXTBRIDGE roi go yes, hoac mo bang PKTEXTUI, the Tro ly, bam Mo cong Kuro."
        elif e.code == -32004:
            goi_y = "Ma ke hoach khong ton tai (da ap dung, da het han hoac cong da khoi dong lai). Lap lai ke hoach."
        return out({"loi": e.code, "thong_bao": e.message, "goi_y": goi_y, "cong_dang_mo": [b.get("pipe") for b in find_bridges()]}, 2)
    except TimeoutError as e:
        return out({"loi": "het_gio", "thong_bao": str(e), "goi_y": "Nguoi dung chua tra loi hop thoai Yes/No trong AutoCAD. Khong goi lai tu dong."}, 2)


if __name__ == "__main__":
    sys.exit(main())
