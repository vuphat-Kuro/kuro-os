#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
xlkit — Bộ lệnh xử lý Excel hàng loạt cho hồ sơ xây dựng.

Thiết kế cho bảng Excel thực tế của ngành: tiêu đề nhiều dòng, cột gộp ô,
số viết kiểu Việt Nam (1.234,56), dấu tiếng Việt không thống nhất mã.

Các lệnh:
    gop        Gộp nhiều file/sheet cùng cấu trúc thành một bảng
    tach       Tách một bảng thành nhiều file theo giá trị một cột
    lam-sach   Chuẩn hóa dữ liệu: khoảng trắng, unicode, số, dòng rỗng
    so-sanh    So hai phiên bản bảng theo cột khóa (thêm/bớt/đổi số)
    tong-hop   Nhóm và cộng theo cột (pivot)
    soat       Soát lỗi chất lượng bảng trước khi nộp
    sang-json  Xuất bảng ra JSON để nạp vào app/ERP
    xem        Xem nhanh cấu trúc file: sheet, dòng tiêu đề, tên cột

Chạy `python xlkit.py <lệnh> -h` để xem tham số của từng lệnh.
"""

import argparse
import glob
import json
import re
import sys
import unicodedata
from pathlib import Path

import pandas as pd

# ----------------------------------------------------------------------------
# Tiện ích dùng chung
# ----------------------------------------------------------------------------

SO_VN = re.compile(r"^-?[\d.]+,\d+$")          # 1.234,56
SO_QT = re.compile(r"^-?[\d,]+\.\d+$")          # 1,234.56


def chuan_unicode(s):
    """Đưa chuỗi về NFC. Chữ tiếng Việt gõ từ nguồn khác nhau có thể cùng
    hiện như nhau nhưng khác byte, khiến VLOOKUP và so khớp trượt."""
    if isinstance(s, str):
        return unicodedata.normalize("NFC", s)
    return s


def chuan_khoang_trang(s):
    if isinstance(s, str):
        s = s.replace("\xa0", " ").replace("\u200b", "")
        return re.sub(r"\s+", " ", s).strip()
    return s


def sang_so(v):
    """Đổi chuỗi số kiểu Việt Nam hoặc quốc tế thành float. Không đổi được
    thì trả lại nguyên giá trị — im lặng biến thành 0 là cách làm hỏng bảng
    khối lượng nhanh nhất."""
    if isinstance(v, (int, float)) and not isinstance(v, bool):
        return v
    if not isinstance(v, str):
        return v
    t = chuan_khoang_trang(v).replace(" ", "")
    if not t:
        return None
    if SO_VN.match(t):
        return float(t.replace(".", "").replace(",", "."))
    if SO_QT.match(t):
        return float(t.replace(",", ""))
    t2 = t.replace(",", ".")
    try:
        return float(t2)
    except ValueError:
        return v


def la_so(v):
    """True nếu giá trị đổi được sang số (kể cả chuỗi số kiểu Việt Nam)."""
    return so_hoac_none(v) is not None


def so_hoac_none(v):
    """Trả float nếu giá trị là số (kể cả numpy int64/float64), ngược lại None."""
    if v is None:
        return None
    kq = sang_so(v)
    if isinstance(kq, bool):
        return None
    try:
        if pd.isna(kq):
            return None
    except (TypeError, ValueError):
        pass
    if isinstance(kq, str):
        return None
    try:
        return float(kq)
    except (TypeError, ValueError):
        return None


def do_dong_tieu_de(duong_dan, sheet=0, quet=15):
    """Dò dòng tiêu đề thật của bảng.

    Bảng hồ sơ hay có 3-6 dòng đầu là tên đơn vị, tên công trình, logo.
    Dòng tiêu đề thật là dòng có nhiều ô chữ liền nhau nhất trong vùng quét.
    """
    tho = pd.read_excel(duong_dan, sheet_name=sheet, header=None, nrows=quet)
    diem_tot, dong_tot = -1, 0
    for i in range(len(tho)):
        hang = tho.iloc[i]
        o_chu = sum(1 for v in hang if isinstance(v, str) and v.strip())
        o_day = hang.notna().sum()
        # ưu tiên dòng nhiều ô chữ, ít ô số, và không quá thưa
        diem = o_chu * 2 - (o_day - o_chu)
        if o_day >= 2 and diem > diem_tot:
            diem_tot, dong_tot = diem, i
    return dong_tot


def doc_bang(duong_dan, sheet=0, dong_tieu_de=None, tu_do=True):
    """Đọc một sheet thành DataFrame với tên cột đã chuẩn hóa."""
    if dong_tieu_de is None:
        dong_tieu_de = do_dong_tieu_de(duong_dan, sheet) if tu_do else 0
    df = pd.read_excel(duong_dan, sheet_name=sheet, header=dong_tieu_de)
    df.columns = [
        chuan_khoang_trang(chuan_unicode(str(c))) if not str(c).startswith("Unnamed")
        else f"Cot_{i}"
        for i, c in enumerate(df.columns)
    ]
    df = df.dropna(how="all").reset_index(drop=True)
    return df, dong_tieu_de


def tach_ds(chuoi):
    if not chuoi:
        return []
    return [c.strip() for c in chuoi.split(",") if c.strip()]


def khop_cot(df, ten):
    """Tìm cột theo tên, chấp nhận khác dấu cách/hoa thường."""
    ten_c = chuan_khoang_trang(chuan_unicode(ten)).lower()
    for c in df.columns:
        if chuan_khoang_trang(chuan_unicode(str(c))).lower() == ten_c:
            return c
    raise SystemExit(
        f"❌ Không tìm thấy cột '{ten}'. Các cột có trong bảng:\n   "
        + "\n   ".join(str(c) for c in df.columns)
    )


def ghep_khoa(df, cot):
    """Ghép nhiều cột thành một chuỗi khóa, an toàn với ô rỗng và số."""
    return df[cot].apply(
        lambda r: "|".join(chuan_khoang_trang(str(v)) for v in r), axis=1
    )


def ghi_excel(cac_bang, duong_dan):
    """Ghi một hoặc nhiều DataFrame ra file, tự giãn độ rộng cột."""
    duong_dan = Path(duong_dan)
    duong_dan.parent.mkdir(parents=True, exist_ok=True)
    with pd.ExcelWriter(duong_dan, engine="openpyxl") as w:
        for ten_sheet, df in cac_bang.items():
            ten_sheet = str(ten_sheet)[:31]
            df.to_excel(w, sheet_name=ten_sheet, index=False)
            ws = w.sheets[ten_sheet]
            for i, cot in enumerate(df.columns, start=1):
                rong = max(
                    len(str(cot)),
                    *(len(str(v)) for v in df[cot].head(200).fillna("")),
                ) if len(df) else len(str(cot))
                ws.column_dimensions[
                    ws.cell(row=1, column=i).column_letter
                ].width = min(max(rong + 2, 10), 55)
            ws.freeze_panes = "A2"
    return duong_dan


def mo_rong_duong_dan(mau):
    """Nhận '*.xlsx', một thư mục, hoặc danh sách ngăn cách bởi dấu phẩy."""
    ket_qua = []
    for phan in str(mau).split(","):
        phan = phan.strip().strip('"')
        if not phan:
            continue
        p = Path(phan)
        if p.is_dir():
            ket_qua += sorted(p.glob("*.xls*"))
        elif any(k in phan for k in "*?["):
            ket_qua += sorted(Path(x) for x in glob.glob(phan, recursive=True))
        elif p.exists():
            ket_qua.append(p)
        else:
            print(f"⚠️  Bỏ qua, không tồn tại: {phan}", file=sys.stderr)
    # bỏ file tạm của Excel
    return [p for p in ket_qua if not p.name.startswith("~$")]


# ----------------------------------------------------------------------------
# Lệnh: xem
# ----------------------------------------------------------------------------

def lenh_xem(a):
    for f in mo_rong_duong_dan(a.vao):
        print(f"\n📄 {f.name}")
        xl = pd.ExcelFile(f)
        for sh in xl.sheet_names:
            try:
                df, dtd = doc_bang(f, sh)
            except Exception as e:  # sheet rỗng hoặc lỗi định dạng
                print(f"   • {sh}: (không đọc được — {e})")
                continue
            print(f"   • Sheet '{sh}': tiêu đề ở dòng {dtd + 1}, "
                  f"{len(df)} dòng dữ liệu, {len(df.columns)} cột")
            print(f"     Cột: {', '.join(str(c) for c in df.columns[:12])}"
                  + (" ..." if len(df.columns) > 12 else ""))


# ----------------------------------------------------------------------------
# Lệnh: gop
# ----------------------------------------------------------------------------

def lenh_gop(a):
    files = mo_rong_duong_dan(a.vao)
    if not files:
        raise SystemExit("❌ Không tìm thấy file nào khớp với --vao")

    cac_phan, bao_cao = [], []
    for f in files:
        sheets = pd.ExcelFile(f).sheet_names if a.moi_sheet else [a.sheet]
        for sh in sheets:
            try:
                df, _ = doc_bang(f, sh, a.dong_tieu_de)
            except Exception as e:
                bao_cao.append({"File": f.name, "Sheet": sh, "Số dòng": 0,
                                "Ghi chú": f"Lỗi: {e}"})
                continue
            if df.empty:
                bao_cao.append({"File": f.name, "Sheet": sh, "Số dòng": 0,
                                "Ghi chú": "Rỗng — bỏ qua"})
                continue
            df.insert(0, a.cot_nguon, f.stem)
            if a.moi_sheet:
                df.insert(1, "Sheet nguồn", str(sh))
            cac_phan.append(df)
            bao_cao.append({"File": f.name, "Sheet": str(sh),
                            "Số dòng": len(df), "Ghi chú": ""})

    if not cac_phan:
        raise SystemExit("❌ Không gộp được dòng nào.")

    gop = pd.concat(cac_phan, ignore_index=True, sort=False)

    # cảnh báo lệch cấu trúc — nguyên nhân số 1 khiến bảng gộp sai
    bo_cot = [set(p.columns) for p in cac_phan]
    chung = set.intersection(*bo_cot)
    lech = set.union(*bo_cot) - chung
    if lech:
        print(f"⚠️  {len(lech)} cột chỉ có ở một số file: "
              f"{', '.join(sorted(str(c) for c in lech)[:10])}")
        print("    Các file không cùng mẫu biểu. Kiểm tra trước khi dùng số tổng.")

    ra = ghi_excel({"Gộp": gop, "Nhật ký gộp": pd.DataFrame(bao_cao)}, a.ra)
    print(f"✅ Gộp {len(cac_phan)} bảng → {len(gop)} dòng → {ra}")


# ----------------------------------------------------------------------------
# Lệnh: tach
# ----------------------------------------------------------------------------

def lenh_tach(a):
    f = mo_rong_duong_dan(a.vao)[0]
    df, _ = doc_bang(f, a.sheet, a.dong_tieu_de)
    cot = khop_cot(df, a.theo)
    thu_muc = Path(a.ra_thu_muc)
    thu_muc.mkdir(parents=True, exist_ok=True)

    dem = 0
    khoa_tach = df[cot].map(lambda v: chuan_khoang_trang(str(v)))
    for gia_tri, nhom in df.groupby(khoa_tach):
        if gia_tri in ("nan", "", "None"):
            continue
        ten_an_toan = re.sub(r'[\\/:*?"<>|]', "_", gia_tri)[:80]
        if a.mot_file:
            continue  # xử lý bên dưới
        ghi_excel({"Dữ liệu": nhom.reset_index(drop=True)},
                  thu_muc / f"{a.tien_to}{ten_an_toan}.xlsx")
        dem += 1

    if a.mot_file:
        cac_sheet = {}
        for gia_tri, nhom in df.groupby(khoa_tach):
            if gia_tri in ("nan", "", "None"):
                continue
            ten = re.sub(r'[\\/:*?"<>|\[\]]', "_", gia_tri)[:31] or "Khac"
            cac_sheet[ten] = nhom.reset_index(drop=True)
            dem += 1
        ra = ghi_excel(cac_sheet, thu_muc / f"{a.tien_to}tach-theo-sheet.xlsx")
        print(f"✅ Tách thành {dem} sheet trong {ra}")
    else:
        print(f"✅ Tách thành {dem} file trong {thu_muc}")


# ----------------------------------------------------------------------------
# Lệnh: lam-sach
# ----------------------------------------------------------------------------

def lenh_lam_sach(a):
    f = mo_rong_duong_dan(a.vao)[0]
    df, _ = doc_bang(f, a.sheet, a.dong_tieu_de)
    truoc = len(df)

    df = df.map(chuan_unicode).map(chuan_khoang_trang)
    df = df.replace({"": None})
    df = df.dropna(how="all").reset_index(drop=True)

    cot_so = [khop_cot(df, c) for c in tach_ds(a.cot_so)] if a.cot_so else []
    if not cot_so and a.tu_do_so:
        # cột nào >70% giá trị đổi được sang số thì coi là cột số
        for c in df.columns:
            gt = df[c].dropna()
            if len(gt) == 0:
                continue
            doi_duoc = sum(1 for v in gt if la_so(v))
            if doi_duoc / len(gt) > 0.7:
                cot_so.append(c)

    for c in cot_so:
        df[c] = df[c].map(sang_so)

    if a.bo_trung:
        khoa = [khop_cot(df, c) for c in tach_ds(a.bo_trung)]
        n = len(df)
        df = df.drop_duplicates(subset=khoa).reset_index(drop=True)
        print(f"   Bỏ {n - len(df)} dòng trùng theo {khoa}")

    ra = ghi_excel({"Đã làm sạch": df}, a.ra)
    print(f"✅ {truoc} → {len(df)} dòng. Cột đã đổi sang số: "
          f"{', '.join(str(c) for c in cot_so) or '(không)'}")
    print(f"   → {ra}")


# ----------------------------------------------------------------------------
# Lệnh: so-sanh
# ----------------------------------------------------------------------------

def lenh_so_sanh(a):
    f_cu = mo_rong_duong_dan(a.cu)[0]
    f_moi = mo_rong_duong_dan(a.moi)[0]
    cu, _ = doc_bang(f_cu, a.sheet, a.dong_tieu_de)
    moi, _ = doc_bang(f_moi, a.sheet, a.dong_tieu_de)

    khoa_cu = [khop_cot(cu, c) for c in tach_ds(a.khoa)]
    khoa_moi = [khop_cot(moi, c) for c in tach_ds(a.khoa)]
    so_cu = [khop_cot(cu, c) for c in tach_ds(a.so)] if a.so else []
    so_moi = [khop_cot(moi, c) for c in tach_ds(a.so)] if a.so else []

    for d, cs in ((cu, so_cu), (moi, so_moi)):
        for c in cs:
            d[c] = d[c].map(sang_so)

    cu["_k"] = ghep_khoa(cu, khoa_cu)
    moi["_k"] = ghep_khoa(moi, khoa_moi)

    k_cu, k_moi = set(cu["_k"]), set(moi["_k"])
    them = moi[moi["_k"].isin(k_moi - k_cu)].drop(columns="_k")
    bot = cu[cu["_k"].isin(k_cu - k_moi)].drop(columns="_k")

    doi = []
    cu_idx = cu.set_index("_k")
    moi_idx = moi.set_index("_k")
    for k in sorted(k_cu & k_moi):
        r_cu = cu_idx.loc[k]
        r_moi = moi_idx.loc[k]
        if isinstance(r_cu, pd.DataFrame):
            r_cu = r_cu.iloc[0]
        if isinstance(r_moi, pd.DataFrame):
            r_moi = r_moi.iloc[0]
        for c_cu, c_moi, ten in zip(so_cu, so_moi, tach_ds(a.so)):
            v1, v2 = r_cu[c_cu], r_moi[c_moi]
            if pd.isna(v1) and pd.isna(v2):
                continue
            v1n, v2n = so_hoac_none(v1), so_hoac_none(v2)
            if v1n is not None and v2n is not None:
                if abs(v1n - v2n) <= a.dung_sai:
                    continue
                chenh = v2n - v1n
                pt = (chenh / v1n * 100) if v1n else None
            else:
                if str(v1) == str(v2):
                    continue
                chenh = pt = None
            doi.append({
                "Khóa": k, "Chỉ tiêu": ten,
                "Bản cũ": v1, "Bản mới": v2,
                "Chênh lệch": chenh,
                "Chênh %": round(pt, 2) if pt is not None else None,
            })

    doi_df = pd.DataFrame(doi)
    tom_tat = pd.DataFrame([
        {"Nội dung": "Dòng bản cũ", "Số lượng": len(cu)},
        {"Nội dung": "Dòng bản mới", "Số lượng": len(moi)},
        {"Nội dung": "Thêm mới", "Số lượng": len(them)},
        {"Nội dung": "Bị bỏ", "Số lượng": len(bot)},
        {"Nội dung": "Thay đổi giá trị", "Số lượng": len(doi_df)},
    ])

    ra = ghi_excel({
        "Tóm tắt": tom_tat,
        "Thay đổi": doi_df if len(doi_df) else pd.DataFrame([{"Ghi chú": "Không có thay đổi"}]),
        "Thêm mới": them if len(them) else pd.DataFrame([{"Ghi chú": "Không có"}]),
        "Bị bỏ": bot if len(bot) else pd.DataFrame([{"Ghi chú": "Không có"}]),
    }, a.ra)

    print(f"✅ So sánh xong: +{len(them)} thêm / -{len(bot)} bỏ / "
          f"~{len(doi_df)} thay đổi → {ra}")
    if len(doi_df):
        lon = doi_df[doi_df["Chênh %"].abs() > 10] if "Chênh %" in doi_df else pd.DataFrame()
        if len(lon):
            print(f"⚠️  {len(lon)} dòng lệch quá 10% — cần giải trình khi trình duyệt.")


# ----------------------------------------------------------------------------
# Lệnh: tong-hop
# ----------------------------------------------------------------------------

def lenh_tong_hop(a):
    f = mo_rong_duong_dan(a.vao)[0]
    df, _ = doc_bang(f, a.sheet, a.dong_tieu_de)
    nhom = [khop_cot(df, c) for c in tach_ds(a.nhom)]
    tong = [khop_cot(df, c) for c in tach_ds(a.tong)]
    for c in tong:
        df[c] = df[c].map(sang_so)
        df[c] = pd.to_numeric(df[c], errors="coerce")

    kq = df.groupby(nhom, dropna=False)[tong].sum(numeric_only=True).reset_index()
    kq.insert(len(nhom), "Số dòng", df.groupby(nhom, dropna=False).size().values)

    dong_tong = {c: "" for c in kq.columns}
    dong_tong[nhom[0]] = "TỔNG CỘNG"
    for c in tong + ["Số dòng"]:
        dong_tong[c] = kq[c].sum()
    kq = pd.concat([kq, pd.DataFrame([dong_tong])], ignore_index=True)

    ra = ghi_excel({"Tổng hợp": kq}, a.ra)
    print(f"✅ Tổng hợp {len(df)} dòng → {len(kq) - 1} nhóm → {ra}")


# ----------------------------------------------------------------------------
# Lệnh: soat
# ----------------------------------------------------------------------------

def lenh_soat(a):
    f = mo_rong_duong_dan(a.vao)[0]
    df, dtd = doc_bang(f, a.sheet, a.dong_tieu_de)
    loi = []

    def them(muc, loai, mo_ta, vi_tri=""):
        loi.append({"Mức": muc, "Loại": loai, "Mô tả": mo_ta, "Vị trí": vi_tri})

    # 1. cột trùng tên
    trung_cot = [c for c in df.columns if list(df.columns).count(c) > 1]
    if trung_cot:
        them("Nặng", "Cột trùng tên", f"Cột lặp: {set(trung_cot)}")

    # 2. khóa trùng / rỗng
    if a.khoa:
        khoa = [khop_cot(df, c) for c in tach_ds(a.khoa)]
        k = ghep_khoa(df, khoa)
        trung = k[k.duplicated(keep=False)]
        if len(trung):
            them("Nặng", "Khóa trùng",
                 f"{len(trung)} dòng trùng khóa {khoa}",
                 f"dòng Excel: {', '.join(str(i + dtd + 2) for i in trung.index[:15])}")
        rong = df[df[khoa].isna().any(axis=1)]
        if len(rong):
            them("Nặng", "Khóa rỗng", f"{len(rong)} dòng thiếu khóa",
                 f"dòng Excel: {', '.join(str(i + dtd + 2) for i in rong.index[:15])}")

    # 3. cột số lẫn chữ
    for c in df.columns:
        gt = df[c].dropna()
        if len(gt) < 5:
            continue
        co_phai_so = [la_so(v) for v in gt]
        ty_le = sum(co_phai_so) / len(gt)
        if 0.6 <= ty_le < 1.0:
            xau = gt[[not x for x in co_phai_so]]
            them("Vừa", "Cột số lẫn chữ",
                 f"Cột '{c}': {len(xau)}/{len(gt)} ô không phải số",
                 f"ví dụ: {list(xau.astype(str)[:3])}")

    # 4. số âm ở cột khối lượng / tiền
    for c in df.columns:
        ten = str(c).lower()
        if not any(k in ten for k in ("khối lượng", "kl", "đơn giá", "thành tiền", "số lượng")):
            continue
        s = pd.to_numeric(df[c].map(sang_so), errors="coerce")
        am = s[s < 0]
        if len(am):
            them("Vừa", "Giá trị âm", f"Cột '{c}' có {len(am)} giá trị âm",
                 f"dòng Excel: {', '.join(str(i + dtd + 2) for i in am.index[:10])}")

    # 5. ô rỗng ở cột bắt buộc
    for c in tach_ds(a.bat_buoc):
        cc = khop_cot(df, c)
        thieu = df[df[cc].isna()]
        if len(thieu):
            them("Nặng", "Thiếu dữ liệu bắt buộc",
                 f"Cột '{cc}' trống {len(thieu)} dòng",
                 f"dòng Excel: {', '.join(str(i + dtd + 2) for i in thieu.index[:15])}")

    # 6. khoảng trắng thừa / unicode lệch
    lech_uni = 0
    for c in df.columns:
        for v in df[c].dropna():
            if isinstance(v, str) and (unicodedata.normalize("NFC", v) != v
                                       or v != chuan_khoang_trang(v)):
                lech_uni += 1
    if lech_uni:
        them("Nhẹ", "Chữ chưa chuẩn",
             f"{lech_uni} ô có khoảng trắng thừa hoặc unicode chưa chuẩn NFC — "
             f"sẽ làm VLOOKUP/so khớp trượt. Chạy lệnh 'lam-sach' để sửa.")

    if not loi:
        print(f"✅ {f.name}: không phát hiện lỗi. {len(df)} dòng, "
              f"{len(df.columns)} cột, tiêu đề dòng {dtd + 1}.")
        return

    bang = pd.DataFrame(loi)
    thu_tu = {"Nặng": 0, "Vừa": 1, "Nhẹ": 2}
    bang = bang.sort_values("Mức", key=lambda s: s.map(thu_tu)).reset_index(drop=True)
    print(f"\n📋 Kết quả soát {f.name} ({len(df)} dòng):\n")
    for _, r in bang.iterrows():
        dau = {"Nặng": "🔴", "Vừa": "🟡", "Nhẹ": "⚪"}[r["Mức"]]
        print(f"{dau} [{r['Loại']}] {r['Mô tả']}")
        if r["Vị trí"]:
            print(f"     {r['Vị trí']}")
    if a.ra:
        ra = ghi_excel({"Soát lỗi": bang}, a.ra)
        print(f"\n→ Đã lưu {ra}")
    nang = (bang["Mức"] == "Nặng").sum()
    if nang:
        print(f"\n⚠️  {nang} lỗi mức Nặng — không nên nộp bảng này trước khi sửa.")
        sys.exit(2)


# ----------------------------------------------------------------------------
# Lệnh: sang-json
# ----------------------------------------------------------------------------

def lenh_sang_json(a):
    f = mo_rong_duong_dan(a.vao)[0]
    df, _ = doc_bang(f, a.sheet, a.dong_tieu_de)
    df = df.map(chuan_unicode)
    if a.cot_so:
        for c in tach_ds(a.cot_so):
            cc = khop_cot(df, c)
            df[cc] = pd.to_numeric(df[cc].map(sang_so), errors="coerce")
    if a.doi_ten:
        anh_xa = dict(p.split("=", 1) for p in a.doi_ten.split(",") if "=" in p)
        df = df.rename(columns={khop_cot(df, k): v for k, v in anh_xa.items()})

    ban_ghi = json.loads(df.to_json(orient="records", force_ascii=False))
    ra = Path(a.ra)
    ra.parent.mkdir(parents=True, exist_ok=True)
    ra.write_text(json.dumps(ban_ghi, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"✅ {len(ban_ghi)} bản ghi → {ra}")


# ----------------------------------------------------------------------------
# CLI
# ----------------------------------------------------------------------------

def main():
    p = argparse.ArgumentParser(
        description="xlkit — xử lý Excel hàng loạt cho hồ sơ xây dựng",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    sub = p.add_subparsers(dest="lenh", required=True)

    def chung(sp, co_sheet=True):
        if co_sheet:
            sp.add_argument("--sheet", default=0,
                            help="Tên hoặc số thứ tự sheet (mặc định sheet đầu)")
        sp.add_argument("--dong-tieu-de", type=int, default=None,
                        help="Dòng tiêu đề tính từ 0. Bỏ trống để tự dò.")

    s = sub.add_parser("xem", help="Xem cấu trúc file")
    s.add_argument("--vao", required=True)
    s.set_defaults(func=lenh_xem)

    s = sub.add_parser("gop", help="Gộp nhiều file/sheet thành một bảng")
    s.add_argument("--vao", required=True, help='Ví dụ: "hoso/*.xlsx" hoặc thư mục')
    s.add_argument("--ra", required=True)
    s.add_argument("--cot-nguon", default="Nguồn")
    s.add_argument("--moi-sheet", action="store_true", help="Gộp tất cả sheet của mỗi file")
    chung(s)
    s.set_defaults(func=lenh_gop)

    s = sub.add_parser("tach", help="Tách bảng theo giá trị một cột")
    s.add_argument("--vao", required=True)
    s.add_argument("--theo", required=True, help="Tên cột dùng để tách")
    s.add_argument("--ra-thu-muc", required=True)
    s.add_argument("--tien-to", default="")
    s.add_argument("--mot-file", action="store_true", help="Tách thành nhiều sheet trong 1 file")
    chung(s)
    s.set_defaults(func=lenh_tach)

    s = sub.add_parser("lam-sach", help="Chuẩn hóa dữ liệu")
    s.add_argument("--vao", required=True)
    s.add_argument("--ra", required=True)
    s.add_argument("--cot-so", default="", help="Danh sách cột ép sang số, cách nhau dấu phẩy")
    s.add_argument("--tu-do-so", action="store_true", help="Tự dò cột số")
    s.add_argument("--bo-trung", default="", help="Bỏ dòng trùng theo các cột này")
    chung(s)
    s.set_defaults(func=lenh_lam_sach)

    s = sub.add_parser("so-sanh", help="So hai phiên bản bảng")
    s.add_argument("--cu", required=True)
    s.add_argument("--moi", required=True)
    s.add_argument("--khoa", required=True, help="Cột khóa, ví dụ: 'Mã hiệu'")
    s.add_argument("--so", default="", help="Các cột số cần so, ví dụ: 'Khối lượng,Thành tiền'")
    s.add_argument("--ra", required=True)
    s.add_argument("--dung-sai", type=float, default=0.001)
    chung(s)
    s.set_defaults(func=lenh_so_sanh)

    s = sub.add_parser("tong-hop", help="Nhóm và cộng")
    s.add_argument("--vao", required=True)
    s.add_argument("--nhom", required=True)
    s.add_argument("--tong", required=True)
    s.add_argument("--ra", required=True)
    chung(s)
    s.set_defaults(func=lenh_tong_hop)

    s = sub.add_parser("soat", help="Soát lỗi bảng trước khi nộp")
    s.add_argument("--vao", required=True)
    s.add_argument("--khoa", default="")
    s.add_argument("--bat-buoc", default="", help="Các cột không được để trống")
    s.add_argument("--ra", default="")
    chung(s)
    s.set_defaults(func=lenh_soat)

    s = sub.add_parser("sang-json", help="Xuất JSON để nạp app/ERP")
    s.add_argument("--vao", required=True)
    s.add_argument("--ra", required=True)
    s.add_argument("--cot-so", default="")
    s.add_argument("--doi-ten", default="", help="Đổi tên cột: 'Mã hiệu=ma,Khối lượng=kl'")
    chung(s)
    s.set_defaults(func=lenh_sang_json)

    a = p.parse_args()
    if isinstance(getattr(a, "sheet", 0), str) and a.sheet.isdigit():
        a.sheet = int(a.sheet)
    a.func(a)


if __name__ == "__main__":
    main()
