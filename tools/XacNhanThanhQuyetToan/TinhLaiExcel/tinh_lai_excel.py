# -*- coding: utf-8 -*-
"""
tinh_lai_excel.py - Kiểm tra công thức Excel bằng chính Excel 365 (COM), không dùng LibreOffice.

Làm gì:
  1. Đọc file .xlsx bằng openpyxl: liệt kê ô công thức và số lưu sẵn (cached value).
  2. Copy file sang 99-Temp (không động vào file gốc), mở bằng Excel 365 ẩn, CalculateFull.
  3. Với mỗi ô công thức: báo lỗi nếu ra #DIV/0!, #NAME?, #REF!, #VALUE!, #N/A, #NUM!, #NULL!;
     so với số lưu sẵn (nếu có) - lệch quá dung sai thì báo.
  4. (Tùy chọn) Sửa ô đầu vào rồi tính lại, in giá trị các ô cần theo dõi (vd. ô kết luận),
     để chứng minh công thức "sống".
  5. Đóng Excel KHÔNG lưu. Mã thoát 0 = đạt, 1 = có lỗi, 2 = lỗi chạy script.

Cách chạy:
  python tinh_lai_excel.py <file.xlsx>
  python tinh_lai_excel.py <file.xlsx> --doc "Sheet1!B48" --sua "Sheet1!D10=1.0" --doc "Sheet1!B48"
    (--doc trước --sua: đọc trước khi sửa; --doc sau --sua: đọc sau khi sửa; xử lý theo thứ tự)

Yêu cầu: Windows + Microsoft Excel 365, Python có openpyxl, pywin32.
"""
import argparse
import os
import shutil
import sys
from datetime import datetime

# ===== THAM SỐ =====
# Xác định thư mục tạm linh hoạt theo Second Brain QLDA
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CURR = SCRIPT_DIR
QLDA_DIR = None
while CURR and os.path.dirname(CURR) != CURR:
    if os.path.basename(CURR) == "QLDA":
        QLDA_DIR = CURR
        break
    if os.path.isdir(os.path.join(CURR, "QLDA")):
        QLDA_DIR = os.path.join(CURR, "QLDA")
        break
    CURR = os.path.dirname(CURR)

if QLDA_DIR:
    THU_MUC_TAM = os.path.join(QLDA_DIR, "99-Temp", "_kiem_excel")
else:
    THU_MUC_TAM = os.path.join(os.getcwd(), "QLDA", "99-Temp", "_kiem_excel")

DUNG_SAI_TUONG_DOI = 1e-4   # 0,01% - số lưu sẵn từ công cụ web thường đã làm tròn; đổi bằng --dung-sai
DUNG_SAI_TUYET_DOI = 1e-9
LOI_EXCEL = ("#DIV/0!", "#NAME?", "#REF!", "#VALUE!", "#N/A", "#NUM!", "#NULL!", "#SPILL!", "#CALC!")

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def tach_dia_chi(dia_chi):
    """'Sheet1!B48' -> ('Sheet1', 'B48'); cho phép tên sheet có nháy đơn."""
    if "!" not in dia_chi:
        raise ValueError(f"Địa chỉ phải có dạng Sheet!Ô, nhận được: {dia_chi}")
    sh, o = dia_chi.rsplit("!", 1)
    return sh.strip("'"), o.replace("$", "")


def ep_kieu(gia_tri_chuoi):
    try:
        return float(gia_tri_chuoi.replace(",", "."))
    except ValueError:
        return gia_tri_chuoi


def lech(a, b):
    if isinstance(a, (int, float)) and isinstance(b, (int, float)) and not isinstance(a, bool):
        return abs(a - b) > max(DUNG_SAI_TUYET_DOI, DUNG_SAI_TUONG_DOI * max(abs(a), abs(b)))
    return str(a).strip() != str(b).strip()


def main():
    ap = argparse.ArgumentParser(description="Kiểm tra công thức Excel bằng Excel 365")
    ap.add_argument("file")
    ap.add_argument("--doc", action="append", default=[], help="Ô cần đọc, vd Sheet1!B48")
    ap.add_argument("--sua", action="append", default=[], help="Sửa ô đầu vào, vd Sheet1!D10=1.0")
    ap.add_argument("--dung-sai", type=float, default=None, help="Dung sai tương đối, mặc định 1e-4")
    # Giữ thứ tự xuất hiện của --doc / --sua
    thu_tu = []
    argv = sys.argv[1:]
    for i, a in enumerate(argv):
        if a in ("--doc", "--sua") and i + 1 < len(argv):
            thu_tu.append((a, argv[i + 1]))
    args = ap.parse_args()
    global DUNG_SAI_TUONG_DOI
    if args.dung_sai is not None:
        DUNG_SAI_TUONG_DOI = args.dung_sai

    goc = os.path.abspath(args.file)
    if not os.path.isfile(goc):
        print(f"LỖI: không thấy file {goc}")
        return 2

    try:
        import openpyxl
        import win32com.client as win32
    except ImportError as e:
        print(f"LỖI: thiếu thư viện ({e}). Cài: python -m pip install openpyxl pywin32")
        return 2

    # --- 1. Đọc công thức và số lưu sẵn ---
    wb_f = openpyxl.load_workbook(goc, data_only=False)
    wb_v = openpyxl.load_workbook(goc, data_only=True)
    o_cong_thuc = []  # (sheet, ô, công thức, số lưu sẵn)
    for ws in wb_f.worksheets:
        ws_v = wb_v[ws.title]
        for row in ws.iter_rows():
            for c in row:
                if isinstance(c.value, str) and c.value.startswith("="):
                    o_cong_thuc.append((ws.title, c.coordinate, c.value, ws_v[c.coordinate].value))
    print("--- KIỂM TRA EXCEL BẰNG EXCEL 365 ---")
    print(f"File: {goc}")
    print(f"Số ô công thức: {len(o_cong_thuc)}")
    if not o_cong_thuc:
        print("CẢNH BÁO: file không có công thức nào (Excel chỉ chứa số tĩnh).")

    # --- 2. Mở bản sao bằng Excel ---
    os.makedirs(THU_MUC_TAM, exist_ok=True)
    ban_sao = os.path.join(THU_MUC_TAM, datetime.now().strftime("%H%M%S_") + os.path.basename(goc))
    shutil.copy2(goc, ban_sao)

    xl = win32.DispatchEx("Excel.Application")
    xl.Visible = False
    xl.DisplayAlerts = False
    so_loi, so_lech, so_khong_luu = 0, 0, 0
    try:
        wb = xl.Workbooks.Open(ban_sao, UpdateLinks=0, ReadOnly=True)
        xl.CalculateFull()

        # --- 3. Kiểm tra từng ô công thức ---
        for sh, o, ct, luu in o_cong_thuc:
            rg = wb.Worksheets(sh).Range(o)
            text = str(rg.Text).strip()
            gt = rg.Value
            if text in LOI_EXCEL or (isinstance(gt, int) and gt < -2146826000):
                so_loi += 1
                print(f"  [LỖI]  {sh}!{o} = {text}   <-- {ct}")
                continue
            if luu is None:
                so_khong_luu += 1
            elif gt is not None and lech(gt, luu):
                so_lech += 1
                print(f"  [LỆCH] {sh}!{o}: Excel tính = {gt!r}, số lưu sẵn = {luu!r}   <-- {ct}")

        # --- 4. Đọc / sửa theo thứ tự ---
        for loai, dc in thu_tu:
            if loai == "--sua":
                if "=" not in dc:
                    print(f"  Bỏ qua --sua sai cú pháp: {dc}")
                    continue
                o_dc, gt_moi = dc.split("=", 1)
                sh, o = tach_dia_chi(o_dc)
                wb.Worksheets(sh).Range(o).Value = ep_kieu(gt_moi)
                xl.CalculateFull()
                print(f"  [SỬA]  {sh}!{o} := {gt_moi}  --> tính lại")
            else:
                sh, o = tach_dia_chi(dc)
                print(f"  [ĐỌC]  {sh}!{o} = {wb.Worksheets(sh).Range(o).Text}")

        wb.Close(SaveChanges=False)
    except Exception as e:
        print(f"LỖI khi chạy Excel: {e}")
        return 2
    finally:
        xl.Quit()

    # --- 5. Tổng kết ---
    print("--- KẾT QUẢ ---")
    print(f"Ô lỗi #: {so_loi} | Ô lệch số lưu sẵn: {so_lech} | Ô không có số lưu sẵn: {so_khong_luu}")
    if so_khong_luu:
        print("  Ghi chú: Ô không có số lưu sẵn sẽ hiện trống trên trình xem không tự tính (bài học #5).")
    dat = so_loi == 0 and so_lech == 0
    print("KẾT LUẬN: ĐẠT" if dat else "KẾT LUẬN: KHÔNG ĐẠT")
    return 0 if dat else 1


if __name__ == "__main__":
    sys.exit(main())
