"""
Script tu dong hoa kiem tra dinh dang va xuat PDF phieu duyet vat tu thi cong (DNVT).
Dung openpyxl va win32com.client (Excel native COM tren Windows).
"""

import os
import sys
import argparse

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

import openpyxl
from openpyxl.styles import Font, Alignment, Border, Side


def fix_header_formatting(excel_path: str):
    """
    Kiem tra va sua loi dinh dang khoi tieu de tren cac sheet DNVT:
    - Xoa vien khung cell B1:E1, B3:E3
    - Dat lai font Times New Roman, co 12, chu dam, can giua
    """
    wb = openpyxl.load_workbook(excel_path)
    modified = False
    
    empty_border = Border(
        left=Side(border_style=None),
        right=Side(border_style=None),
        top=Side(border_style=None),
        bottom=Side(border_style=None)
    )
    bold_font_12 = Font(name="Times New Roman", size=12, bold=True)
    center_align = Alignment(horizontal="center", vertical="center", wrap_text=True)

    for sheet_name in wb.sheetnames:
        if sheet_name.startswith("DNVT"):
            ws = wb[sheet_name]
            # Kiem tra o B1
            cell_b1 = ws["B1"]
            if cell_b1.border and (cell_b1.border.left.border_style or cell_b1.border.top.border_style):
                cell_b1.border = empty_border
                cell_b1.font = bold_font_12
                cell_b1.alignment = center_align
                modified = True
            
            # Kiem tra o B3
            cell_b3 = ws["B3"]
            if cell_b3.border and (cell_b3.border.left.border_style or cell_b3.border.top.border_style):
                cell_b3.border = empty_border
                modified = True

    if modified:
        wb.save(excel_path)
        print(f"[OK] Da chuan hoa dinh dang header tai: {excel_path}")
    else:
        print(f"[INFO] Dinh dang header hop le: {excel_path}")


def export_sheet_to_pdf_com(excel_path: str, sheet_name: str, output_pdf_path: str):
    """
    Xuat 1 sheet cu the ra PDF bang dong co Microsoft Excel native qua Windows COM.
    Dam bao 100% dung chuoi font, net vien va dung 1 trang A4 Portrait.
    """
    abs_excel = os.path.abspath(excel_path)
    abs_pdf = os.path.abspath(output_pdf_path)
    os.makedirs(os.path.dirname(abs_pdf), exist_ok=True)

    import win32com.client
    excel_app = win32com.client.DispatchEx("Excel.Application")
    excel_app.Visible = False
    excel_app.DisplayAlerts = False

    try:
        wb = excel_app.Workbooks.Open(abs_excel, UpdateLinks=0, ReadOnly=True)
        try:
            ws = wb.Worksheets(sheet_name)
        except Exception:
            raise ValueError(f"Khong tim thay sheet '{sheet_name}' trong file {excel_path}")

        # Thiet lap trang in chuan 1 trang A4 Portrait
        ws.PageSetup.Orientation = 1  # 1 = xlPortrait
        ws.PageSetup.PaperSize = 9     # 9 = xlPaperA4
        ws.PageSetup.Zoom = False
        ws.PageSetup.FitToPagesWide = 1
        ws.PageSetup.FitToPagesTall = 1

        # Xuat PDF (Type 0 = xlTypePDF, Quality 0 = xlQualityStandard)
        ws.ExportAsFixedFormat(0, abs_pdf, 0, True, False)
        wb.Close(SaveChanges=False)
        print(f"[OK] Da xuat PDF thanh cong: {abs_pdf}")
    finally:
        excel_app.Quit()


def main():
    parser = argparse.ArgumentParser(description="Tool quan ly & xuat phieu duyet vat tu thi cong DNVT")
    parser.add_argument("--fix-header", help="Duong dan file Excel can kiem tra va sua header")
    parser.add_argument("--excel", help="Duong dan file Excel de xuat PDF")
    parser.add_argument("--sheet", help="Ten sheet can xuat (vd: DNVT-01)")
    parser.add_argument("--output-pdf", help="Duong dan file PDF dau ra")

    args = parser.parse_args()

    if args.fix_header:
        fix_header_formatting(args.fix_header)

    if args.excel and args.sheet and args.output_pdf:
        fix_header_formatting(args.excel)
        export_sheet_to_pdf_com(args.excel, args.sheet, args.output_pdf)


if __name__ == "__main__":
    main()
