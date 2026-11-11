# -*- coding: utf-8 -*-
"""TM5: mở file xlsx thuyết minh bằng Excel (COM), tính lại toàn bộ, so giá trị tính lại với giá trị lưu sẵn từ chương trình,
đếm ô lỗi, và xuất PDF để xem bố cục trang. Chạy: python kiem_excel_com.py tm_thuyet_minh.xlsx"""
import sys, os, win32com.client, openpyxl
sys.stdout.reconfigure(encoding='utf-8')
src = os.path.abspath(sys.argv[1]); base = os.path.splitext(src)[0]
cached = openpyxl.load_workbook(src, data_only=True)       # giá trị lưu sẵn do chương trình ghi
forms = openpyxl.load_workbook(src)                         # công thức
xl = win32com.client.DispatchEx('Excel.Application'); xl.Visible = False; xl.DisplayAlerts = False
try:
    wb = xl.Workbooks.Open(src); xl.CalculateFull()
    bad = 0; nf = 0; maxrel = 0; errs = 0; worst = []
    for ws in forms:
        sh = wb.Worksheets(ws.title)
        for row in ws.iter_rows():
            for c in row:
                if isinstance(c.value, str) and c.value.startswith('='):
                    nf += 1
                    v = sh.Range(c.coordinate).Value; cv = cached[ws.title][c.coordinate].value
                    if isinstance(v, int) and v < 0 and v < -2000000000: errs += 1; worst.append((ws.title, c.coordinate, 'LỖI', c.value[:60])); continue
                    if isinstance(cv, (int, float)) and isinstance(v, (int, float)):
                        rel = abs(v - cv) / max(1e-9, abs(cv), 1e-6) if abs(cv) > 1e-6 else abs(v - cv)
                        if rel > 1e-6: bad += 1; worst.append((ws.title, c.coordinate, cv, v, c.value[:70]))
                        maxrel = max(maxrel, rel)
                    elif str(v) != str(cv): bad += 1; worst.append((ws.title, c.coordinate, cv, v, c.value[:70]))
    print(f'ô công thức: {nf}; lệch giá trị lưu sẵn (>1e-6): {bad}; ô lỗi: {errs}; lệch tương đối lớn nhất: {maxrel:.3g}')
    for w in worst[:25]: print('  ', w)
    if not os.environ.get('NO_PDF'):
        wb.ExportAsFixedFormat(0, base + '_excel.pdf'); print('PDF:', base + '_excel.pdf')
    wb.Close(False)
finally:
    xl.Quit()
