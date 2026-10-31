#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
chay — Chạy một chuỗi bước đã định nghĩa sẵn trong file .yaml.

Thay vì gõ 6 lệnh mỗi lần làm hồ sơ tháng, viết một lần vào file quy trình
rồi chạy `python chay.py quy-trinh/ho-so-thang.yaml`. Tháng sau chỉ đổi
một dòng ngày tháng.

Cấu trúc file quy trình:

    ten: Hồ sơ nghiệm thu tháng 8
    bien:
      thang: "2026-08"
      goc: D:/DuAn/CauQuangSon
    buoc:
      - ten: Gộp bảng khối lượng các đội
        lenh: xlkit
        tham_so: [gop, --vao, "{goc}/khoi-luong/*.xlsx", --ra, "{goc}/tong-hop-{thang}.xlsx"]

      - ten: Soát lỗi trước khi lập biên bản
        lenh: xlkit
        tham_so: [soat, --vao, "{goc}/tong-hop-{thang}.xlsx", --khoa, "Mã hiệu"]
        bo_qua_loi: false          # lỗi ở bước này thì dừng cả quy trình

      - ten: Sinh biên bản nghiệm thu
        lenh: docgen
        tham_so: [tao, --mau, "{goc}/mau/BB-NT.docx",
                  --du-lieu, "{goc}/tong-hop-{thang}.xlsx",
                  --ra-thu-muc, "{goc}/bien-ban-{thang}", --pdf]

      - ten: Kiểm tra tên file trước khi tải lên CDE
        lenh: iso19650
        tham_so: [kiem-tra, --thu-muc, "{goc}/bien-ban-{thang}", --chan]

      - ten: Tải lên CDE
        lenh: cde
        tham_so: [tai-len, --du-an, "b.xxxx", --thu-muc, "urn:...",
                  --vao, "{goc}/bien-ban-{thang}"]
        hoi_truoc: true            # dừng hỏi trước khi làm việc không lùi được

Cách chạy:
    python chay.py quy-trinh/ho-so-thang.yaml
    python chay.py quy-trinh/ho-so-thang.yaml --thu          # chỉ in ra, không chạy
    python chay.py quy-trinh/ho-so-thang.yaml --bien thang=2026-09
    python chay.py --mau > quy-trinh/moi.yaml                # sinh file mẫu
"""

import argparse
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

import yaml

GOC_SKILLS = Path(__file__).resolve().parents[2]

CONG_CU = {
    "xlkit": GOC_SKILLS / "excel-tu-dong-hoa/scripts/xlkit.py",
    "docgen": GOC_SKILLS / "word-ho-so-tu-dong/scripts/docgen.py",
    "docxkit": GOC_SKILLS / "word-ho-so-tu-dong/scripts/docxkit.py",
    "cde": GOC_SKILLS / "cde-dong-bo/scripts/cde.py",
    "iso19650": GOC_SKILLS / "cde-dong-bo/scripts/iso19650.py",
}

MAU = """\
ten: Tên quy trình
bien:
  thang: "2026-08"
  goc: "D:/DuAn/TenDuAn"
buoc:
  - ten: Gộp bảng khối lượng
    lenh: xlkit
    tham_so: [gop, --vao, "{goc}/khoi-luong/*.xlsx", --ra, "{goc}/tong-hop-{thang}.xlsx"]

  - ten: Soát lỗi
    lenh: xlkit
    tham_so: [soat, --vao, "{goc}/tong-hop-{thang}.xlsx", --khoa, "Mã hiệu"]

  - ten: Sinh biên bản
    lenh: docgen
    tham_so: [tao, --mau, "{goc}/mau/BB-NT.docx", --du-lieu, "{goc}/tong-hop-{thang}.xlsx",
              --ra-thu-muc, "{goc}/bien-ban-{thang}", --ten, "BB-{{So hieu}}.docx"]
"""


def thay_bien(v, bien):
    if isinstance(v, str):
        # chỉ thay {ten_bien}, giữ nguyên {{...}} là chỗ trống của mẫu Word
        cho = v.replace("{{", "\x01").replace("}}", "\x02")
        for k, gt in bien.items():
            cho = cho.replace("{" + k + "}", str(gt))
        return cho.replace("\x01", "{{").replace("\x02", "}}")
    if isinstance(v, list):
        return [thay_bien(x, bien) for x in v]
    if isinstance(v, dict):
        return {k: thay_bien(x, bien) for k, x in v.items()}
    return v


def chay_buoc(buoc, bien, thu):
    ten = buoc.get("ten", buoc.get("lenh", "(không tên)"))
    lenh = buoc.get("lenh")
    tham_so = [str(x) for x in thay_bien(buoc.get("tham_so", []), bien)]

    if lenh in CONG_CU:
        cong_cu = CONG_CU[lenh]
        if not cong_cu.exists():
            return False, f"không tìm thấy công cụ {cong_cu}"
        day_du = [sys.executable, str(cong_cu)] + tham_so
    elif lenh == "shell":
        day_du = tham_so
    else:
        return False, (f"không biết lệnh '{lenh}'. "
                       f"Dùng một trong: {', '.join(CONG_CU)} hoặc 'shell'")

    print(f"\n▶ {ten}")
    print(f"  $ {' '.join(day_du[1:] if lenh != 'shell' else day_du)}")
    if thu:
        return True, "(chạy thử)"

    if buoc.get("hoi_truoc"):
        tra_loi = input("  Bước này thay đổi dữ liệu trên máy chủ. Chạy? [y/N] ")
        if tra_loi.strip().lower() not in ("y", "yes", "c", "co", "có"):
            return True, "người dùng bỏ qua"

    bat_dau = time.time()
    kq = subprocess.run(day_du, shell=(lenh == "shell"),
                        capture_output=True, text=True, encoding="utf-8")
    giay = time.time() - bat_dau
    for dong in (kq.stdout or "").rstrip().splitlines():
        print(f"  │ {dong}")
    if kq.returncode != 0:
        for dong in (kq.stderr or "").rstrip().splitlines()[-12:]:
            print(f"  ! {dong}")
        return False, f"mã lỗi {kq.returncode} sau {giay:.1f}s"
    return True, f"{giay:.1f}s"


def main():
    p = argparse.ArgumentParser(
        description="chay — chạy chuỗi bước xử lý hồ sơ theo file .yaml",
        formatter_class=argparse.RawDescriptionHelpFormatter, epilog=__doc__)
    p.add_argument("quy_trinh", nargs="?", help="File .yaml mô tả quy trình")
    p.add_argument("--thu", action="store_true", help="In ra các lệnh, không chạy thật")
    p.add_argument("--bien", action="append", default=[],
                   help="Đè biến, ví dụ --bien thang=2026-09")
    p.add_argument("--mau", action="store_true", help="In ra file quy trình mẫu")
    p.add_argument("--tu-buoc", type=int, default=1, help="Bắt đầu từ bước thứ mấy")
    a = p.parse_args()

    if a.mau:
        print(MAU)
        return
    if not a.quy_trinh:
        p.error("cần chỉ ra file .yaml, hoặc dùng --mau để sinh file mẫu")

    qt = yaml.safe_load(Path(a.quy_trinh).read_text(encoding="utf-8"))
    bien = dict(qt.get("bien", {}))
    bien.setdefault("hom_nay", datetime.now().strftime("%Y-%m-%d"))
    for cap in a.bien:
        if "=" in cap:
            k, v = cap.split("=", 1)
            bien[k.strip()] = v.strip()

    cac_buoc = qt.get("buoc", [])
    print(f"═══ {qt.get('ten', Path(a.quy_trinh).stem)} — {len(cac_buoc)} bước ═══")
    if bien:
        print("Biến: " + ", ".join(f"{k}={v}" for k, v in bien.items()))
    if a.thu:
        print("(CHẠY THỬ — không có gì bị thay đổi)")

    ket_qua, that_bai = [], 0
    for i, b in enumerate(cac_buoc, 1):
        if i < a.tu_buoc:
            print(f"\n⏭  Bỏ qua bước {i}: {b.get('ten', '')}")
            continue
        ok, tin = chay_buoc(b, bien, a.thu)
        ket_qua.append((i, b.get("ten", ""), ok, tin))
        print(f"  {'✅' if ok else '❌'} {tin}")
        if not ok:
            that_bai += 1
            if not b.get("bo_qua_loi"):
                print(f"\n⛔ Dừng ở bước {i}. Sửa xong chạy lại từ bước này:")
                print(f"   python chay.py {a.quy_trinh} --tu-buoc {i}")
                break

    print("\n═══ Kết quả ═══")
    for i, ten, ok, tin in ket_qua:
        print(f"  {i}. {'✅' if ok else '❌'} {ten} — {tin}")
    if that_bai:
        sys.exit(1)


if __name__ == "__main__":
    main()
