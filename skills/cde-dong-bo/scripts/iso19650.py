#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
iso19650 — Đặt tên, kiểm tra và lập bảng đăng ký hồ sơ theo ISO 19650.

Tên file sai quy ước là nguyên nhân số một khiến hồ sơ bị trả về từ CDE và
khiến không ai tìm được bản mới nhất. Công cụ này kiểm tra trước khi tải lên.

Quy ước mặc định (theo ISO 19650-2, sửa được bằng --mau):
    <Dự án>-<Đơn vị>-<Khu>-<Cao độ>-<Loại>-<Bộ môn>-<Số hiệu>[-<Trạng thái>][-<Rev>]
    VD:  HCMTLMT-A2Z-KM12-ZZ-DR-C-0001-S3-P01.pdf

Các lệnh:
    kiem-tra   Soát tên file trong thư mục theo quy ước
    dat-ten    Sinh tên chuẩn từ bảng Excel các trường
    doi-ten    Đổi tên hàng loạt theo bảng ánh xạ (có chế độ chạy thử)
    dang-ky    Quét thư mục, xuất bảng đăng ký tài liệu ra Excel
    ma-tran    Sinh khung ma trận trách nhiệm thông tin (bộ môn × giai đoạn)
"""

import argparse
import hashlib
import re
from datetime import datetime
from pathlib import Path

import pandas as pd

# Trường mặc định của quy ước tên. Sửa qua --mau nếu dự án dùng quy ước riêng.
TRUONG_MAC_DINH = ["Dự án", "Đơn vị", "Khu", "Cao độ", "Loại", "Bộ môn", "Số hiệu"]

MA_TRANG_THAI = {
    "S0": "Bản khởi tạo — chưa dùng được",
    "S1": "Phát hành để phối hợp",
    "S2": "Phát hành để tham khảo",
    "S3": "Phát hành để duyệt nội bộ",
    "S4": "Phát hành để chủ đầu tư phê duyệt",
    "S6": "Phát hành để đấu thầu / PIM",
    "S7": "Phát hành cho AIM (bàn giao)",
    "A":  "Đã duyệt — dùng thi công",
    "B":  "Duyệt có điều kiện",
    "CR": "Bị trả lại, làm lại",
}

MA_LOAI = {
    "DR": "Bản vẽ (drawing)", "M3": "Mô hình 3D", "M2": "Mô hình 2D",
    "SP": "Chỉ dẫn kỹ thuật", "SH": "Bảng biểu (schedule)", "RP": "Báo cáo",
    "CA": "Tính toán", "PP": "Trình chiếu", "MI": "Biên bản họp",
    "CO": "Thư từ, công văn", "PH": "Ảnh hiện trường",
}


def tach_ten(ten, so_truong):
    goc = Path(ten).stem
    return goc.split("-")


def lenh_kiem_tra(a):
    truong = [t.strip() for t in a.mau.split("-")] if a.mau else TRUONG_MAC_DINH
    thu_muc = Path(a.thu_muc)
    files = [p for p in thu_muc.rglob("*") if p.is_file()
             and not p.name.startswith("~$")]
    if a.duoi:
        duoi = {d.strip().lower().lstrip(".") for d in a.duoi.split(",")}
        files = [p for p in files if p.suffix.lower().lstrip(".") in duoi]

    hang = []
    for f in files:
        phan = tach_ten(f.name, len(truong))
        loi = []
        if len(phan) < len(truong):
            loi.append(f"thiếu {len(truong) - len(phan)} trường")
        if " " in f.stem:
            loi.append("có dấu cách")
        if re.search(r"[àáâãèéêìíòóôõùúăđĩũơưăạảấầẩẫậ]", f.stem, re.IGNORECASE):
            loi.append("có dấu tiếng Việt")
        if "__" in f.stem or f.stem.endswith("-"):
            loi.append("dấu phân cách thừa")

        trang_thai = rev = ""
        if len(phan) > len(truong):
            du = phan[len(truong):]
            for x in du:
                if x.upper() in MA_TRANG_THAI:
                    trang_thai = x.upper()
                elif re.fullmatch(r"[PC]?\d{2}", x, re.IGNORECASE) or \
                     re.fullmatch(r"[A-Z]\d{2}", x):
                    rev = x.upper()
        if a.bat_buoc_trang_thai and not trang_thai:
            loi.append("thiếu mã trạng thái (S0..S7/A/B)")

        ban_ghi = {"Tên file": f.name,
                   "Thư mục": str(f.parent.relative_to(thu_muc)) or ".",
                   "Đạt": "✔" if not loi else "✘",
                   "Lỗi": "; ".join(loi),
                   "Trạng thái": trang_thai,
                   "Rev": rev,
                   "Sửa lúc": datetime.fromtimestamp(f.stat().st_mtime)
                                      .strftime("%Y-%m-%d %H:%M"),
                   "Dung lượng (MB)": round(f.stat().st_size / 1e6, 2)}
        for i, t in enumerate(truong):
            ban_ghi[t] = phan[i] if i < len(phan) else ""
        hang.append(ban_ghi)

    df = pd.DataFrame(hang)
    if df.empty:
        raise SystemExit("❌ Không tìm thấy file nào.")
    dat = (df["Đạt"] == "✔").sum()
    print(f"📋 {len(df)} file: {dat} đạt / {len(df) - dat} sai quy ước")
    sai = df[df["Đạt"] == "✘"]
    for _, r in sai.head(25).iterrows():
        print(f"   ✘ {r['Tên file']} — {r['Lỗi']}")
    if len(sai) > 25:
        print(f"   ... và {len(sai) - 25} file nữa")

    # trùng số hiệu nhưng khác rev — dấu hiệu có hai bản cùng tồn tại
    if "Số hiệu" in df.columns:
        nhom = df[df["Số hiệu"] != ""].groupby("Số hiệu").size()
        trung = nhom[nhom > 1]
        if len(trung):
            print(f"\n⚠️  {len(trung)} số hiệu xuất hiện nhiều lần "
                  f"— kiểm tra xem có bản cũ chưa gỡ không:")
            for so, n in list(trung.items())[:10]:
                print(f"      {so}: {n} file")

    if a.ra:
        p = Path(a.ra)
        p.parent.mkdir(parents=True, exist_ok=True)
        with pd.ExcelWriter(p, engine="openpyxl") as w:
            df.to_excel(w, sheet_name="Kiểm tra tên", index=False)
            if len(sai):
                sai.to_excel(w, sheet_name="File sai", index=False)
        print(f"→ {p}")
    if len(sai) and a.chan:
        raise SystemExit(2)


def lenh_dat_ten(a):
    df = pd.read_excel(a.vao, dtype=str).fillna("")
    truong = [t.strip() for t in a.mau.split("-")] if a.mau else TRUONG_MAC_DINH
    thieu = [t for t in truong if t not in df.columns]
    if thieu:
        raise SystemExit(f"❌ File Excel thiếu cột: {', '.join(thieu)}\n"
                         f"   Các cột đang có: {', '.join(df.columns)}")

    def khong_dau(s):
        import unicodedata
        s = unicodedata.normalize("NFD", str(s))
        s = "".join(c for c in s if unicodedata.category(c) != "Mn")
        return s.replace("đ", "d").replace("Đ", "D")

    ten = []
    for _, r in df.iterrows():
        phan = [khong_dau(str(r[t]).strip().replace(" ", "")) or "ZZ" for t in truong]
        if "Trạng thái" in df.columns and str(r["Trạng thái"]).strip():
            phan.append(str(r["Trạng thái"]).strip().upper())
        if "Rev" in df.columns and str(r["Rev"]).strip():
            phan.append(str(r["Rev"]).strip().upper())
        duoi = str(r.get("Đuôi", "")).strip().lstrip(".")
        ten.append("-".join(phan) + (f".{duoi}" if duoi else ""))

    df.insert(0, "Tên chuẩn", ten)
    trung = df["Tên chuẩn"].duplicated(keep=False)
    if trung.any():
        print(f"⚠️  {trung.sum()} tên bị trùng nhau — kiểm tra cột Số hiệu.")

    p = Path(a.ra)
    p.parent.mkdir(parents=True, exist_ok=True)
    df.to_excel(p, index=False)
    print(f"✅ Sinh {len(df)} tên chuẩn → {p}")
    for t in ten[:5]:
        print(f"   {t}")


def lenh_doi_ten(a):
    b = pd.read_excel(a.bang, dtype=str).fillna("")
    cot = list(b.columns)[:2]
    thu_muc = Path(a.thu_muc)
    dem, thieu, dung = 0, [], []
    for _, r in b.iterrows():
        cu, moi = str(r[cot[0]]).strip(), str(r[cot[1]]).strip()
        if not cu or not moi:
            continue
        f_cu = thu_muc / cu
        f_moi = thu_muc / re.sub(r'[\\/:*?"<>|]', "_", moi)
        if not f_cu.exists():
            thieu.append(cu)
            continue
        if f_moi.exists() and f_moi != f_cu:
            dung.append(moi)
            continue
        if a.thu:
            print(f"   {cu}  →  {f_moi.name}")
        else:
            f_cu.rename(f_moi)
        dem += 1
    print(f"{'🔎 Chạy thử: ' if a.thu else '✅ '}{dem} file "
          f"{'sẽ được' if a.thu else 'đã'} đổi tên")
    if thieu:
        print(f"⚠️  Không tìm thấy {len(thieu)} file: {', '.join(thieu[:8])}")
    if dung:
        print(f"⚠️  Bỏ qua {len(dung)} file vì tên đích đã tồn tại: {', '.join(dung[:5])}")


def lenh_dang_ky(a):
    thu_muc = Path(a.thu_muc)
    hang = []
    for f in sorted(thu_muc.rglob("*")):
        if not f.is_file() or f.name.startswith("~$"):
            continue
        h = ""
        if a.ma_bam:
            bam = hashlib.md5()
            with open(f, "rb") as fh:
                for khoi in iter(lambda: fh.read(1 << 20), b""):
                    bam.update(khoi)
            h = bam.hexdigest()[:12]
        hang.append({
            "STT": len(hang) + 1,
            "Tên file": f.name,
            "Thư mục": str(f.parent.relative_to(thu_muc)) or ".",
            "Đuôi": f.suffix.lower().lstrip("."),
            "Dung lượng (MB)": round(f.stat().st_size / 1e6, 3),
            "Sửa lúc": datetime.fromtimestamp(f.stat().st_mtime).strftime("%Y-%m-%d %H:%M"),
            "Mã kiểm tra": h,
        })
    df = pd.DataFrame(hang)
    if df.empty:
        raise SystemExit("❌ Thư mục rỗng.")
    p = Path(a.ra)
    p.parent.mkdir(parents=True, exist_ok=True)
    with pd.ExcelWriter(p, engine="openpyxl") as w:
        df.to_excel(w, sheet_name="Đăng ký tài liệu", index=False)
        tk = df.groupby("Đuôi").agg(**{
            "Số file": ("STT", "count"),
            "Tổng MB": ("Dung lượng (MB)", "sum")}).reset_index()
        tk.to_excel(w, sheet_name="Thống kê", index=False)
    print(f"✅ {len(df)} tài liệu, {df['Dung lượng (MB)'].sum():.1f} MB → {p}")
    if a.ma_bam:
        trung = df[df["Mã kiểm tra"].duplicated(keep=False) & (df["Mã kiểm tra"] != "")]
        if len(trung):
            print(f"⚠️  {len(trung)} file trùng nội dung (khác tên, cùng ruột) "
                  f"— nên gỡ bớt trước khi tải lên CDE.")


def lenh_ma_tran(a):
    bo_mon = [x.strip() for x in a.bo_mon.split(",") if x.strip()]
    giai_doan = [x.strip() for x in a.giai_doan.split(",") if x.strip()]
    hang = [{"Bộ môn": bm, **{gd: "" for gd in giai_doan}} for bm in bo_mon]
    df = pd.DataFrame(hang)
    p = Path(a.ra)
    p.parent.mkdir(parents=True, exist_ok=True)
    with pd.ExcelWriter(p, engine="openpyxl") as w:
        df.to_excel(w, sheet_name="Ma trận LOD-LOI", index=False)
        pd.DataFrame([{"Mã": k, "Nghĩa": v} for k, v in MA_TRANG_THAI.items()]) \
            .to_excel(w, sheet_name="Mã trạng thái", index=False)
        pd.DataFrame([{"Mã": k, "Nghĩa": v} for k, v in MA_LOAI.items()]) \
            .to_excel(w, sheet_name="Mã loại tài liệu", index=False)
    print(f"✅ Khung ma trận {len(bo_mon)} bộ môn × {len(giai_doan)} giai đoạn → {p}")
    print("   Điền LOD/LOI vào từng ô, kèm ai chịu trách nhiệm cấp thông tin.")


def main():
    p = argparse.ArgumentParser(
        description="iso19650 — đặt tên & kiểm tra hồ sơ theo ISO 19650",
        formatter_class=argparse.RawDescriptionHelpFormatter, epilog=__doc__)
    sub = p.add_subparsers(dest="lenh", required=True)

    s = sub.add_parser("kiem-tra", help="Soát tên file theo quy ước")
    s.add_argument("--thu-muc", required=True)
    s.add_argument("--mau", default="", help="Danh sách trường cách nhau dấu '-'")
    s.add_argument("--duoi", default="", help="Chỉ soát các đuôi này, VD: pdf,dwg,rvt")
    s.add_argument("--bat-buoc-trang-thai", action="store_true")
    s.add_argument("--chan", action="store_true", help="Thoát lỗi nếu có file sai")
    s.add_argument("--ra", default="")
    s.set_defaults(func=lenh_kiem_tra)

    s = sub.add_parser("dat-ten", help="Sinh tên chuẩn từ bảng Excel")
    s.add_argument("--vao", required=True)
    s.add_argument("--ra", required=True)
    s.add_argument("--mau", default="")
    s.set_defaults(func=lenh_dat_ten)

    s = sub.add_parser("doi-ten", help="Đổi tên hàng loạt theo bảng")
    s.add_argument("--thu-muc", required=True)
    s.add_argument("--bang", required=True, help="Excel 2 cột: tên cũ | tên mới")
    s.add_argument("--thu", action="store_true")
    s.set_defaults(func=lenh_doi_ten)

    s = sub.add_parser("dang-ky", help="Quét thư mục → bảng đăng ký tài liệu")
    s.add_argument("--thu-muc", required=True)
    s.add_argument("--ra", required=True)
    s.add_argument("--ma-bam", action="store_true", help="Tính mã kiểm tra để dò file trùng ruột")
    s.set_defaults(func=lenh_dang_ky)

    s = sub.add_parser("ma-tran", help="Sinh khung ma trận trách nhiệm thông tin")
    s.add_argument("--bo-mon", default="Cầu,Đường,Thoát nước,ATGT,Điện chiếu sáng,Địa kỹ thuật")
    s.add_argument("--giai-doan", default="Thiết kế cơ sở,TKKT,TKBVTC,Thi công,Hoàn công")
    s.add_argument("--ra", required=True)
    s.set_defaults(func=lenh_ma_tran)

    a = p.parse_args()
    a.func(a)


if __name__ == "__main__":
    main()
