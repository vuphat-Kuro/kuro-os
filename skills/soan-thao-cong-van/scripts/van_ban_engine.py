"""
Công cụ tự động hóa xử lý văn bản hành chính Công ty Phương Thành (PT)
Tự động sao chép mẫu, làm sạch thể thức, xuất PDF qua Microsoft Word COM và ghi sổ theo dõi Excel.
"""

import os
import sys
import shutil
import argparse

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

import docx
import openpyxl
from openpyxl.styles import Font, Alignment, Border, Side

WORKSPACE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
MAU_ROOT = os.path.join(WORKSPACE_ROOT, "03-MauBieu", "03-Word", "01-MauCongVan")
TEMP_ROOT = os.path.join(WORKSPACE_ROOT, "99-Temp")
SO_THEO_DOI_ROOT = os.path.join(WORKSPACE_ROOT, "03-MauBieu", "03-Word", "02-SoTheoDoi")

BM01_FILE = os.path.join(MAU_ROOT, "BM01_VB-2025_CV_Gui_Ra_Ngoai.docx")
BM03A_FILE = os.path.join(MAU_ROOT, "BM3A_VB-2025_VB_Noi_Bo.docx")

SUPERSCRIPT_MAP = {
    "¹⁰": "", "¹¹": "", "¹²": "", "¹³": "",
    "⁰": "", "¹": "", "²": "", "³": "", "⁴": "",
    "⁵": "", "⁶": "", "⁷": "", "⁸": "", "⁹": ""
}

TYPO_REPLACEMENTS = {
    "Qúy": "Quý",
    "Công công trường": "Các công trường",
}


def clone_template(template_code: str, draft_filename: str) -> str:
    """Sao chép mẫu gốc sang thư mục 99-Temp với tên file nháp được chỉ định."""
    os.makedirs(TEMP_ROOT, exist_ok=True)
    code_upper = template_code.upper().replace("-", "").replace("_", "")
    
    if "BM01" in code_upper or code_upper == "BM1":
        src = BM01_FILE
    elif "BM03" in code_upper or "BM3" in code_upper:
        src = BM03A_FILE
    else:
        raise ValueError(f"Không nhận diện được mã biểu mẫu: {template_code}. Chỉ chấp nhận BM01 hoặc BM03A.")
    
    if not os.path.exists(src):
        raise FileNotFoundError(f"Không tìm thấy file mẫu gốc: {src}")
    
    if not draft_filename.endswith(".docx"):
        draft_filename += ".docx"
        
    dest = os.path.join(TEMP_ROOT, draft_filename)
    shutil.copy2(src, dest)
    print(f"[OK] Đã sao chép mẫu sang: {dest}")
    return dest


def clean_document(docx_path: str, is_release: bool = False, remove_sample_notes: bool = True) -> str:
    """
    Làm sạch văn bản Word:
    - Xóa các số chỉ số trên (¹⁰ ¹¹ ¹² ¹³)
    - Sửa các lỗi chính tả đã biết (Qúy -> Quý, Công công trường -> Các công trường)
    - Nếu phát hành (is_release=True):
        + BM03A: Xóa dòng/bảng 'Mẫu số: BM03A/VB-2025' trong Header, giữ nguyên Logo và thông tin công ty.
        + BM01: Xóa Table 2 (chứa khung Text Box Mẫu số: BM01/VB-2025) và khối ghi chú mẫu nếu có.
    """
    if not os.path.exists(docx_path):
        raise FileNotFoundError(f"File không tồn tại: {docx_path}")
    
    doc = docx.Document(docx_path)
    
    # 1. Làm sạch văn bản trong thân tài liệu (Paragraphs)
    paragraphs_to_remove = []
    found_note_block = False
    
    for p in doc.paragraphs:
        # Nhận diện khối Ghi chú mẫu ở cuối BM01 để xóa khi phát hành
        if remove_sample_notes and p.text.strip().startswith("Ghi chú:"):
            found_note_block = True
        if found_note_block and remove_sample_notes:
            paragraphs_to_remove.append(p)
            continue
            
        for run in p.runs:
            for bad, good in SUPERSCRIPT_MAP.items():
                if bad in run.text:
                    run.text = run.text.replace(bad, good)
            for bad, good in TYPO_REPLACEMENTS.items():
                if bad in run.text:
                    run.text = run.text.replace(bad, good)
                    
    for p in paragraphs_to_remove:
        p_elem = p._element
        p_elem.getparent().remove(p_elem)
        
    # 2. Làm sạch văn bản trong các Bảng (Tables)
    for t in doc.tables:
        for row in t.rows:
            for cell in row.cells:
                for p in cell.paragraphs:
                    for run in p.runs:
                        for bad, good in SUPERSCRIPT_MAP.items():
                            if bad in run.text:
                                run.text = run.text.replace(bad, good)
                        for bad, good in TYPO_REPLACEMENTS.items():
                            if bad in run.text:
                                run.text = run.text.replace(bad, good)

    # 3. Xử lý Header & Footer
    for section in doc.sections:
        header = section.header
        # Xóa số chỉ số trên trong Header
        for p in header.paragraphs:
            for run in p.runs:
                for bad, good in SUPERSCRIPT_MAP.items():
                    if bad in run.text:
                        run.text = run.text.replace(bad, good)
                for bad, good in TYPO_REPLACEMENTS.items():
                    if bad in run.text:
                        run.text = run.text.replace(bad, good)
        for t in header.tables:
            for row in t.rows:
                for cell in row.cells:
                    for p in cell.paragraphs:
                        for run in p.runs:
                            for bad, good in SUPERSCRIPT_MAP.items():
                                if bad in run.text:
                                    run.text = run.text.replace(bad, good)
                            for bad, good in TYPO_REPLACEMENTS.items():
                                if bad in run.text:
                                    run.text = run.text.replace(bad, good)
                                    
        # Khi phát hành: Xóa dòng/bảng Mẫu số ở Header BM03A
        if is_release and len(header.tables) >= 2:
            first_t = header.tables[0]
            if "BM03A" in first_t.rows[0].cells[0].text or "Mẫu số" in first_t.rows[0].cells[0].text:
                first_t._element.getparent().remove(first_t._element)
                print("[OK] Đã xóa bảng 'Mẫu số: BM03A' trong Header, giữ nguyên Logo và thông tin Công ty.")

    # 4. Khi phát hành: Xóa Text Box Mẫu số BM01 (nằm trong Table 2 của BM01)
    if is_release and len(doc.tables) >= 3:
        t2 = doc.tables[2]
        xml_t2 = t2._element.xml
        if "BM01" in xml_t2 or "Mẫu số" in xml_t2 or len(t2.rows) == 1 and len(t2.columns) == 1:
            t2._element.getparent().remove(t2._element)
            print("[OK] Đã xóa khung 'Mẫu số: BM01' ở góc trên phải trang.")

    doc.save(docx_path)
    print(f"[OK] Đã làm sạch và cập nhật file: {docx_path}")
    return docx_path


def export_pdf(docx_path: str, pdf_path: str = None) -> str:
    """Xuất PDF từ file Word qua Microsoft Word COM, đảm bảo trung thực 100% bố cục."""
    import win32com.client
    docx_abs = os.path.abspath(docx_path)
    if not os.path.exists(docx_abs):
        raise FileNotFoundError(f"File DOCX không tồn tại: {docx_abs}")
    
    if pdf_path is None:
        pdf_path = os.path.splitext(docx_abs)[0] + ".pdf"
    else:
        pdf_path = os.path.abspath(pdf_path)
        
    os.makedirs(os.path.dirname(pdf_path), exist_ok=True)
    
    word = win32com.client.Dispatch("Word.Application")
    word.Visible = False
    doc = None
    try:
        doc = word.Documents.Open(docx_abs)
        # 17 = wdFormatPDF
        try:
            doc.SaveAs2(pdf_path, FileFormat=17)
        except Exception:
            try:
                doc.ExportAsFixedFormat(pdf_path, 17)
            except Exception:
                doc.SaveAs(pdf_path, FileFormat=17)
        print(f"[OK] Đã xuất PDF thành công: {pdf_path}")
    finally:
        if doc is not None:
            doc.Close(False)
        word.Quit()
        
    return pdf_path


def log_document_entry(so_vb: str, ngay_vb: str, mau_vb: str, phong_ban: str,
                       noi_nhan: str, trich_yeu: str, nguoi_ky: str,
                       duong_dan_file: str, trang_thai: str = "Đã ban hành",
                       nam: int = 2026) -> int:
    """Ghi một dòng vào sổ theo dõi So_van_ban_[NĂM].xlsx."""
    excel_path = os.path.join(SO_THEO_DOI_ROOT, f"So_van_ban_{nam}.xlsx")
    if not os.path.exists(excel_path):
        raise FileNotFoundError(f"Không tìm thấy file sổ theo dõi: {excel_path}")
    
    wb = openpyxl.load_workbook(excel_path)
    ws = wb.active
    
    # Tìm dòng trống đầu tiên từ dòng 8 trở đi
    target_row = 8
    while target_row <= 500:
        val_so = ws.cell(row=target_row, column=2).value
        val_trich = ws.cell(row=target_row, column=7).value
        if (val_so is None or str(val_so).strip() == "") and (val_trich is None or str(val_trich).strip() == ""):
            break
        target_row += 1
        
    thin_border = Border(
        left=Side(style='thin', color='BFBFBF'),
        right=Side(style='thin', color='BFBFBF'),
        top=Side(style='thin', color='BFBFBF'),
        bottom=Side(style='thin', color='BFBFBF')
    )
    
    ws.row_dimensions[target_row].height = 24
    
    # Ghi dữ liệu 10 cột
    ws.cell(row=target_row, column=1, value=f'=IF(B{target_row}<>"", ROW()-7, "")')
    ws.cell(row=target_row, column=2, value=so_vb)
    ws.cell(row=target_row, column=3, value=ngay_vb)
    ws.cell(row=target_row, column=4, value=mau_vb)
    ws.cell(row=target_row, column=5, value=phong_ban)
    ws.cell(row=target_row, column=6, value=noi_nhan)
    ws.cell(row=target_row, column=7, value=trich_yeu)
    ws.cell(row=target_row, column=8, value=nguoi_ky)
    ws.cell(row=target_row, column=9, value=duong_dan_file)
    ws.cell(row=target_row, column=10, value=trang_thai)
    
    for col_idx in range(1, 11):
        cell = ws.cell(row=target_row, column=col_idx)
        cell.font = Font(name='Times New Roman', size=11)
        cell.border = thin_border
        if col_idx in [1, 2, 3, 4, 5, 8, 10]:
            cell.alignment = Alignment(horizontal='center', vertical='center')
        else:
            cell.alignment = Alignment(horizontal='left', vertical='center', wrap_text=True)
            
    wb.save(excel_path)
    print(f"[OK] Đã ghi sổ theo dõi tại dòng {target_row} trong file: {excel_path}")
    return target_row


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PT Văn thư Engine - Xử lý công văn, văn bản")
    subparsers = parser.add_subparsers(dest="command")
    
    # Subcommand: clone
    p_clone = subparsers.add_parser("clone", help="Sao chép mẫu sang 99-Temp")
    p_clone.add_argument("template", choices=["BM01", "BM03A", "BM3A"], help="Mã biểu mẫu")
    p_clone.add_argument("filename", help="Tên file nháp đích")
    
    # Subcommand: clean
    p_clean = subparsers.add_parser("clean", help="Làm sạch văn bản")
    p_clean.add_argument("path", help="Đường dẫn file docx")
    p_clean.add_argument("--release", action="store_true", help="Chế độ phát hành chính thức (xóa khung mẫu số)")
    
    # Subcommand: pdf
    p_pdf = subparsers.add_parser("pdf", help="Xuất PDF qua Word COM")
    p_pdf.add_argument("docx", help="Đường dẫn file docx")
    p_pdf.add_argument("--out", help="Đường dẫn file pdf đích (tùy chọn)")
    
    # Subcommand: log
    p_log = subparsers.add_parser("log", help="Ghi sổ theo dõi văn bản")
    p_log.add_argument("--so", required=True, help="Số văn bản")
    p_log.add_argument("--ngay", required=True, help="Ngày ban hành")
    p_log.add_argument("--mau", required=True, help="Mẫu văn bản (BM01 / BM03A)")
    p_log.add_argument("--pb", default="P.KTTC", help="Phòng ban soạn thảo")
    p_log.add_argument("--nhan", required=True, help="Nơi nhận")
    p_log.add_argument("--trich", required=True, help="Trích yếu nội dung")
    p_log.add_argument("--ky", required=True, help="Người ký")
    p_log.add_argument("--file", required=True, help="Đường dẫn file lưu trữ")
    p_log.add_argument("--status", default="Đã ban hành", help="Trạng thái")
    p_log.add_argument("--nam", type=int, default=2026, help="Năm theo dõi")
    
    args = parser.parse_args()
    
    if args.command == "clone":
        clone_template(args.template, args.filename)
    elif args.command == "clean":
        clean_document(args.path, is_release=args.release)
    elif args.command == "pdf":
        export_pdf(args.docx, args.out)
    elif args.command == "log":
        log_document_entry(args.so, args.ngay, args.mau, args.pb, args.nhan, args.trich, args.ky, args.file, args.status, args.nam)
    else:
        parser.print_help()
