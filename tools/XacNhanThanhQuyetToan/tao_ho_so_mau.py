"""Công cụ tạo và nhân bản file mẫu Xác nhận thanh quyết toán thầu phụ / đội thi công.
Phòng Kỹ thuật - Thi công | Công ty CP ĐTXD Giao thông Phương Thành.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
import openpyxl
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

ROOT = Path(__file__).resolve().parent.parent.parent
MAU_DIR = Path(__file__).resolve().parent / "mau"
MAU_FILE = MAU_DIR / "Mau_XacNhan_ThanhQuyetToan_ThauPhu.xlsx"


def tao_file_mau(dest_path: Path | str | None = None) -> Path:
    target = Path(dest_path) if dest_path else MAU_FILE
    target.parent.mkdir(parents=True, exist_ok=True)

    wb = openpyxl.Workbook()
    # Xóa sheet mặc định
    wb.remove(wb.active)

    # Đinh dạng chung
    font_family = "Times New Roman"
    font_title = Font(name=font_family, size=15, bold=True, color="002060")
    font_subtitle = Font(name=font_family, size=11, italic=True)
    font_header = Font(name=font_family, size=11, bold=True, color="FFFFFF")
    font_bold = Font(name=font_family, size=11, bold=True)
    font_normal = Font(name=font_family, size=11)
    font_note = Font(name=font_family, size=10, italic=True, color="555555")

    fill_header = PatternFill(start_color="1F497D", end_color="1F497D", fill_type="solid")
    fill_sub = PatternFill(start_color="DCE6F1", end_color="DCE6F1", fill_type="solid")
    fill_highlight = PatternFill(start_color="FFF2CC", end_color="FFF2CC", fill_type="solid")

    thin_border = Border(
        left=Side(style="thin", color="000000"),
        right=Side(style="thin", color="000000"),
        top=Side(style="thin", color="000000"),
        bottom=Side(style="thin", color="000000"),
    )

    align_center = Alignment(horizontal="center", vertical="center", wrap_text=True)
    align_left = Alignment(horizontal="left", vertical="center", wrap_text=True)
    align_right = Alignment(horizontal="right", vertical="center")

    # ==================== SHEET 1: TTC (THÔNG TIN CHUNG) ====================
    ws_ttc = wb.create_sheet("TTC")
    ws_ttc.views.sheetView[0].showGridLines = True
    ws_ttc.column_dimensions["A"].width = 6
    ws_ttc.column_dimensions["B"].width = 28
    ws_ttc.column_dimensions["C"].width = 45
    ws_ttc.column_dimensions["D"].width = 25

    ws_ttc["B1"] = "CÔNG TY CP ĐTXD GIAO THÔNG PHƯƠNG THÀNH"
    ws_ttc["B1"].font = font_bold
    ws_ttc["B2"] = "PHÒNG KỸ THUẬT - THI CÔNG"
    ws_ttc["B2"].font = Font(name=font_family, size=11, bold=True, color="1F497D")

    ws_ttc["B4"] = "BẢNG THÔNG TIN CHUNG HỒ SƠ THANH QUYẾT TOÁN"
    ws_ttc["B4"].font = font_title

    ttc_rows = [
        ("tda", "Tên dự án / Công trình", "Cầu Ninh Cơ (hoặc tên dự án đang làm việc)"),
        ("tgt", "Gói thầu", "Gói thầu số ..."),
        ("dtc", "Tên Đội thi công / Thầu phụ", "Đội thi công / Công ty ..."),
        ("shd", "Số Hợp đồng", "Số: .../HĐKT/2026/PT-TC"),
        ("nhd", "Ngày ký Hợp đồng", "2026-01-15"),
        ("ndhd", "Nội dung hợp đồng", "Thi công kết cấu phần dưới mố trụ cầu"),
        ("dot", "Đợt xác nhận (dot)", "Đợt 1 (hoặc QT nếu là Quyết toán)"),
        ("nnt", "Ngày biên bản nghiệm thu BĐH", "2026-03-31"),
        ("nxn", "Ngày xác nhận Phòng KTTC", "=TODAY()"),
        ("ngl", "Người lập hồ sơ", "Kỹ sư phụ trách"),
        ("ngkt", "Người kiểm tra (Phòng KTTC)", "Trưởng bộ phận QS/QC"),
        ("ngd", "Lãnh đạo phê duyệt", "Trưởng phòng KTTC"),
    ]

    ws_ttc.cell(row=6, column=2, value="Mã định danh").font = font_header
    ws_ttc.cell(row=6, column=2).fill = fill_header
    ws_ttc.cell(row=6, column=3, value="Thông số hồ sơ").font = font_header
    ws_ttc.cell(row=6, column=3).fill = fill_header
    ws_ttc.cell(row=6, column=4, value="Giá trị khai báo / Công thức").font = font_header
    ws_ttc.cell(row=6, column=4).fill = fill_header

    for idx, (code, title, val) in enumerate(ttc_rows, start=7):
        ws_ttc.cell(row=idx, column=2, value=code).alignment = align_center
        ws_ttc.cell(row=idx, column=2).font = font_bold
        ws_ttc.cell(row=idx, column=2).border = thin_border

        ws_ttc.cell(row=idx, column=3, value=title).alignment = align_left
        ws_ttc.cell(row=idx, column=3).font = font_normal
        ws_ttc.cell(row=idx, column=3).border = thin_border

        c_val = ws_ttc.cell(row=idx, column=4, value=val)
        c_val.alignment = align_left
        c_val.font = font_normal
        c_val.border = thin_border
        if code in ("tda", "dtc", "shd", "dot"):
            c_val.fill = fill_highlight

    # ==================== SHEET 2: 1.XNKL (PHIẾU XÁC NHẬN KHỐI LƯỢNG) ====================
    ws_xnkl = wb.create_sheet("1.XNKL")
    ws_xnkl.views.sheetView[0].showGridLines = True
    col_widths_xnkl = {"A": 5, "B": 38, "C": 8, "D": 14, "E": 14, "F": 15, "G": 15, "H": 16, "I": 16, "J": 12, "K": 20}
    for col_l, w in col_widths_xnkl.items():
        ws_xnkl.column_dimensions[col_l].width = w

    ws_xnkl["A1"] = "CÔNG TY CP ĐTXD GIAO THÔNG PHƯƠNG THÀNH"
    ws_xnkl["A1"].font = font_bold
    ws_xnkl["A2"] = "PHÒNG KỸ THUẬT - THI CÔNG"
    ws_xnkl["A2"].font = Font(name=font_family, size=11, bold=True, color="1F497D")

    ws_xnkl.merge_cells("A4:K4")
    ws_xnkl["A4"] = "PHIẾU XÁC NHẬN KHỐI LƯỢNG THI CÔNG HOÀN THÀNH"
    ws_xnkl["A4"].font = font_title
    ws_xnkl["A4"].alignment = align_center

    ws_xnkl.merge_cells("A5:K5")
    ws_xnkl["A5"] = "Công trình: ='TTC'!D7 | Đơn vị thi công: ='TTC'!D9 | Đợt xác nhận: ='TTC'!D13"
    ws_xnkl["A5"].font = font_subtitle
    ws_xnkl["A5"].alignment = align_center

    headers_xnkl = [
        ("A7", "STT"),
        ("B7", "Danh mục hạng mục công việc"),
        ("C7", "ĐVT"),
        ("D7", "Khối lượng\ntheo HĐ"),
        ("E7", "Khối lượng\ntheo BVTC"),
        ("F7", "Lũy kế kỳ trước\nPhòng đã ký"),
        ("G7", "Đề nghị kỳ này\ncủa BĐH"),
        ("H7", "Phòng KTTC\nxác nhận kỳ này"),
        ("I7", "Lũy kế đến\nhết kỳ này"),
        ("J7", "Tỷ lệ %\nhoàn thành"),
        ("K7", "Ghi chú nguồn đối chiếu"),
    ]
    for cell_ref, text in headers_xnkl:
        c = ws_xnkl[cell_ref]
        c.value = text
        c.font = font_header
        c.fill = fill_header
        c.alignment = align_center
        c.border = thin_border

    sample_items = [
        ("1", "Khoan tạo lỗ cọc khoan nhồi D1200 trong đất", "m", 120.0, 120.0, 0.0, 120.0, 120.0, "=F8+H8", "=I8/E8", "BB nghiệm thu số 01/BĐH"),
        ("2", "Khoan tạo lỗ cọc khoan nhồi D1200 vào đá", "m", 30.0, 30.0, 0.0, 30.0, 30.0, "=F9+H9", "=I9/E9", "BB nghiệm thu số 02/BĐH"),
        ("3", "Gia công và hạ lồng thép cọc khoan nhồi D1200", "tấn", 18.5, 18.5, 0.0, 18.5, 18.5, "=F10+H10", "=I10/E10", "Theo BVTC cọc T11"),
        ("4", "Đổ bê tông cọc khoan nhồi D1200 C30/38", "m3", 169.6, 169.6, 0.0, 169.6, 169.6, "=F11+H11", "=I11/E11", "Phiếu xuất xưởng bê tông"),
        ("5", "Đập đầu cọc khoan nhồi D1200 (1,0m/cọc)", "cọc", 4.0, 4.0, 0.0, 4.0, 4.0, "=F12+H12", "=I12/E12", "Nghiệm thu phần đầu cọc"),
        ("6", "Công nhật: Vệ sinh dọn dẹp mặt bằng thi công (ngoài HĐ)", "công", 0.0, 0.0, 0.0, 15.0, 15.0, "=F13+H13", "-", "Biên bản xác nhận công nhật BĐH"),
    ]

    for idx, row in enumerate(sample_items, start=8):
        ws_xnkl.cell(row=idx, column=1, value=row[0]).alignment = align_center
        ws_xnkl.cell(row=idx, column=2, value=row[1]).alignment = align_left
        ws_xnkl.cell(row=idx, column=3, value=row[2]).alignment = align_center
        ws_xnkl.cell(row=idx, column=4, value=row[3]).number_format = "#,##0.00"
        ws_xnkl.cell(row=idx, column=5, value=row[4]).number_format = "#,##0.00"
        ws_xnkl.cell(row=idx, column=6, value=row[5]).number_format = "#,##0.00"
        ws_xnkl.cell(row=idx, column=7, value=row[6]).number_format = "#,##0.00"
        ws_xnkl.cell(row=idx, column=8, value=row[7]).number_format = "#,##0.00"
        ws_xnkl.cell(row=idx, column=9, value=row[8]).number_format = "#,##0.00"
        if row[9] != "-":
            ws_xnkl.cell(row=idx, column=10, value=row[9]).number_format = "0.0%"
        else:
            ws_xnkl.cell(row=idx, column=10, value=row[9]).alignment = align_center
        ws_xnkl.cell(row=idx, column=11, value=row[10]).font = font_note

        for c_idx in range(1, 12):
            cell = ws_xnkl.cell(row=idx, column=c_idx)
            cell.border = thin_border
            if not cell.font.italic:
                cell.font = font_normal

    # Dòng chữ ký
    sig_row = 16
    ws_xnkl.cell(row=sig_row, column=2, value="NGƯỜI LẬP HỒ SƠ\n(Ký và ghi rõ họ tên)").alignment = align_center
    ws_xnkl.cell(row=sig_row, column=2).font = font_bold
    ws_xnkl.cell(row=sig_row, column=6, value="PHỤ TRÁCH KỸ THUẬT / QS\n(Ký và ghi rõ họ tên)").alignment = align_center
    ws_xnkl.cell(row=sig_row, column=6).font = font_bold
    ws_xnkl.cell(row=sig_row, column=9, value="TRƯỞNG PHÒNG KT-TC\n(Ký và ghi rõ họ tên)").alignment = align_center
    ws_xnkl.cell(row=sig_row, column=9).font = font_bold

    # ==================== SHEET 3: 2.VTC (VẬT TƯ THI CÔNG THEO BVTC) ====================
    ws_vtc = wb.create_sheet("2.VTC")
    ws_vtc.views.sheetView[0].showGridLines = True
    col_widths_vtc = {"A": 5, "B": 35, "C": 10, "D": 18, "E": 18, "F": 18, "G": 25}
    for col_l, w in col_widths_vtc.items():
        ws_vtc.column_dimensions[col_l].width = w

    ws_vtc["A2"] = "PHIẾU XÁC NHẬN VẬT TƯ THI CÔNG THEO BVTC VÀ BPTC"
    ws_vtc["A2"].font = font_title
    headers_vtc = [
        ("A4", "STT"), ("B4", "Tên chủng loại vật tư"), ("C4", "ĐVT"),
        ("D4", "Khối lượng theo BVTC"), ("E4", "BPTC bổ sung (nếu có)"),
        ("F4", "Tổng Phòng xác nhận"), ("G4", "Căn cứ bản vẽ / Thí nghiệm")
    ]
    for cell_ref, text in headers_vtc:
        c = ws_vtc[cell_ref]
        c.value = text
        c.font = font_header
        c.fill = fill_header
        c.alignment = align_center
        c.border = thin_border

    sample_vtc = [
        ("1", "Thép tròn cốt cọc CB400V (D>=18mm)", "kg", 14500.0, 0.0, "=D5+E5", "Bản vẽ TKBVTC Cọc T11"),
        ("2", "Thép đai CB240T (D<10mm)", "kg", 3980.0, 0.0, "=D6+E6", "Bản vẽ TKBVTC Cọc T11"),
        ("3", "Bê tông thương phẩm C30/38", "m3", 169.6, 0.0, "=D7+E7", "Bảng tính KL hình học cọc"),
        ("4", "Ống siêu âm thép D60x2.0mm", "m", 480.0, 0.0, "=D8+E8", "Quy trình thí nghiệm siêu âm cọc"),
    ]
    for idx, row in enumerate(sample_vtc, start=5):
        ws_vtc.cell(row=idx, column=1, value=row[0]).alignment = align_center
        ws_vtc.cell(row=idx, column=2, value=row[1]).alignment = align_left
        ws_vtc.cell(row=idx, column=3, value=row[2]).alignment = align_center
        ws_vtc.cell(row=idx, column=4, value=row[3]).number_format = "#,##0.00"
        ws_vtc.cell(row=idx, column=5, value=row[4]).number_format = "#,##0.00"
        ws_vtc.cell(row=idx, column=6, value=row[5]).number_format = "#,##0.00"
        ws_vtc.cell(row=idx, column=7, value=row[6]).font = font_note
        for c_idx in range(1, 8):
            ws_vtc.cell(row=idx, column=c_idx).border = thin_border

    # ==================== SHEET 4: 3.VTLC (VẬT TƯ LUÂN CHUYỂN) ====================
    ws_vtlc = wb.create_sheet("3.VTLC")
    ws_vtlc.views.sheetView[0].showGridLines = True
    col_widths_vtlc = {"A": 5, "B": 32, "C": 8, "D": 14, "E": 14, "F": 14, "G": 14, "H": 18, "I": 20}
    for col_l, w in col_widths_vtlc.items():
        ws_vtlc.column_dimensions[col_l].width = w

    ws_vtlc["A2"] = "PHIẾU ĐÁNH GIÁ HAO HỤT VẬT TƯ LUÂN CHUYỂN (BPTC)"
    ws_vtlc["A2"].font = font_title
    headers_vtlc = [
        ("A4", "STT"), ("B4", "Tên thiết bị / Vật tư luân chuyển"), ("C4", "ĐVT"),
        ("D4", "Khối lượng cấp"), ("E4", "Khối lượng thu hồi"), ("F4", "Hao hụt thực tế"),
        ("G4", "Định mức BPTC"), ("H4", "Đánh giá hao hụt"), ("I4", "Đề xuất xử lý")
    ]
    for cell_ref, text in headers_vtlc:
        c = ws_vtlc[cell_ref]
        c.value = text
        c.font = font_header
        c.fill = fill_header
        c.alignment = align_center
        c.border = thin_border

    sample_vtlc = [
        ("1", "Cọc ván thép Larsen IV (L=18m)", "tấn", 86.4, 85.0, "=D5-E5", 2.5, "Trong định mức", "Nhập kho hoàn trả vật tư"),
        ("2", "Thép hình vành đai và giằng H400", "tấn", 42.0, 41.2, "=D6-E6", 1.5, "Trong định mức", "Tái luân chuyển sang trụ T12"),
    ]
    for idx, row in enumerate(sample_vtlc, start=5):
        ws_vtlc.cell(row=idx, column=1, value=row[0]).alignment = align_center
        ws_vtlc.cell(row=idx, column=2, value=row[1]).alignment = align_left
        ws_vtlc.cell(row=idx, column=3, value=row[2]).alignment = align_center
        ws_vtlc.cell(row=idx, column=4, value=row[3]).number_format = "#,##0.00"
        ws_vtlc.cell(row=idx, column=5, value=row[4]).number_format = "#,##0.00"
        ws_vtlc.cell(row=idx, column=6, value=row[5]).number_format = "#,##0.00"
        ws_vtlc.cell(row=idx, column=7, value=row[6]).number_format = "#,##0.00"
        ws_vtlc.cell(row=idx, column=8, value=row[7]).alignment = align_center
        ws_vtlc.cell(row=idx, column=9, value=row[8]).font = font_note
        for c_idx in range(1, 10):
            ws_vtlc.cell(row=idx, column=c_idx).border = thin_border

    # ==================== SHEET 5: 4.DGTD (ĐÁNH GIÁ TIẾN ĐỘ) ====================
    ws_dgtd = wb.create_sheet("4.DGTD")
    ws_dgtd.views.sheetView[0].showGridLines = True
    col_widths_dgtd = {"A": 5, "B": 35, "C": 14, "D": 14, "E": 14, "F": 15, "G": 18, "H": 25}
    for col_l, w in col_widths_dgtd.items():
        ws_dgtd.column_dimensions[col_l].width = w

    ws_dgtd["A2"] = "BẢNG ĐÁNH GIÁ TIẾN ĐỘ THI CÔNG THEO HỢP ĐỒNG"
    ws_dgtd["A2"].font = font_title
    headers_dgtd = [
        ("A4", "STT"), ("B4", "Đầu mục thi công"), ("C4", "Ngày bắt đầu"),
        ("D4", "Ngày kết thúc"), ("E4", "Thời gian TT (ngày)"), ("F4", "Cam kết HĐ (ngày)"),
        ("G4", "Đánh giá tiến độ"), ("H4", "Nguyên nhân & Căn cứ")
    ]
    for cell_ref, text in headers_dgtd:
        c = ws_dgtd[cell_ref]
        c.value = text
        c.font = font_header
        c.fill = fill_header
        c.alignment = align_center
        c.border = thin_border

    sample_dgtd = [
        ("1", "Khoan và đổ bê tông 04 cọc khoan nhồi trụ T11", "2026-02-01", "2026-02-25", "=D5-C5+1", 30, "Đạt tiến độ", "Nhật ký thi công và biên bản BĐH"),
        ("2", "Thi công vòng vây cọc ván thép Larsen IV trụ T11", "2026-03-01", "2026-03-15", "=D6-C6+1", 15, "Đạt tiến độ", "Đúng theo tiến độ BPTC phê duyệt"),
    ]
    for idx, row in enumerate(sample_dgtd, start=5):
        ws_dgtd.cell(row=idx, column=1, value=row[0]).alignment = align_center
        ws_dgtd.cell(row=idx, column=2, value=row[1]).alignment = align_left
        ws_dgtd.cell(row=idx, column=3, value=row[2]).alignment = align_center
        ws_dgtd.cell(row=idx, column=4, value=row[3]).alignment = align_center
        ws_dgtd.cell(row=idx, column=5, value=row[4]).alignment = align_center
        ws_dgtd.cell(row=idx, column=6, value=row[5]).alignment = align_center
        ws_dgtd.cell(row=idx, column=7, value=row[6]).alignment = align_center
        ws_dgtd.cell(row=idx, column=8, value=row[7]).font = font_note
        for c_idx in range(1, 9):
            ws_dgtd.cell(row=idx, column=c_idx).border = thin_border

    # ==================== SHEET 6: GHI_CHU (ĐỐI SOÁT & NHÃN NGUỒN) ====================
    ws_gc = wb.create_sheet("GHI_CHU")
    ws_gc.views.sheetView[0].showGridLines = True
    col_widths_gc = {"A": 5, "B": 25, "C": 20, "D": 20, "E": 18, "F": 35}
    for col_l, w in col_widths_gc.items():
        ws_gc.column_dimensions[col_l].width = w

    ws_gc["A2"] = "BẢNG ĐỐI SOÁT SỐ LIỆU VÀ NHÃN CĂN CỨ XÁC MINH"
    ws_gc["A2"].font = font_title
    headers_gc = [
        ("A4", "STT"), ("B4", "Hạng mục / Chỉ số"), ("C4", "Đề nghị của BĐH"),
        ("D4", "Phòng KTTC chốt"), ("E4", "Nhãn xác minh"), ("F4", "Nguồn tài liệu & Việc xin ý kiến")
    ]
    for cell_ref, text in headers_gc:
        c = ws_gc[cell_ref]
        c.value = text
        c.font = font_header
        c.fill = fill_header
        c.alignment = align_center
        c.border = thin_border

    sample_gc = [
        ("1", "Khoan cọc khoan nhồi D1200", "150 m", "150 m", "[ĐÃ XÁC MINH]", "Khớp với TKBVTC và Biên bản nghiệm thu BĐH"),
        ("2", "Công nhật dọn dẹp mặt bằng", "20 công", "15 công", "[CẦN KIỂM TRA]", "BĐH đề nghị 20 công, Phòng chỉ duyệt 15 công theo báo cáo ảnh thực tế"),
    ]
    for idx, row in enumerate(sample_gc, start=5):
        ws_gc.cell(row=idx, column=1, value=row[0]).alignment = align_center
        ws_gc.cell(row=idx, column=2, value=row[1]).alignment = align_left
        ws_gc.cell(row=idx, column=3, value=row[2]).alignment = align_right
        ws_gc.cell(row=idx, column=4, value=row[3]).alignment = align_right
        ws_gc.cell(row=idx, column=5, value=row[4]).alignment = align_center
        ws_gc.cell(row=idx, column=6, value=row[5]).font = font_note
        for c_idx in range(1, 7):
            ws_gc.cell(row=idx, column=c_idx).border = thin_border

    wb.save(target)
    print(f"[tao_ho_so_mau] Đã tạo thành công file mẫu Excel chuẩn tại: {target}")
    return target


def sao_chep_mau_vao_du_an(workspace_path: Path | str, ten_file: str = "Bang_Xac_Nhan_Thanh_Toan.xlsx") -> Path:
    """Sao chép hoặc khởi tạo bảng tính xác nhận thanh quyết toán vào thư mục dự án."""
    ws_dir = Path(workspace_path)
    if not ws_dir.is_dir():
        ws_dir.mkdir(parents=True, exist_ok=True)

    dest_dir = ws_dir / "5. XAC NHAN KHOI LUONG"
    if not dest_dir.exists():
        # Thử tìm thư mục XAC NHAN KHOI LUONG không có số đầu
        alt = ws_dir / "XAC NHAN KHOI LUONG"
        dest_dir = alt if alt.exists() else ws_dir

    dest_file = dest_dir / ten_file
    if not MAU_FILE.exists():
        tao_file_mau(MAU_FILE)

    import shutil
    shutil.copy2(MAU_FILE, dest_file)
    print(f"[sao_chep_mau] Đã nhân bản file mẫu vào dự án: {dest_file}")
    return dest_file


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Tạo file Excel mẫu xác nhận thanh quyết toán thầu phụ")
    parser.add_argument("--dest", help="Đường dẫn file đích cần tạo", default=None)
    args = parser.parse_args()
    tao_file_mau(args.dest)
