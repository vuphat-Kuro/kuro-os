"""
Công cụ tự động hóa xử lý văn bản hành chính Công ty Phương Thành (PT)
Tự động sao chép mẫu, làm sạch thể thức, xuất BM03A chuẩn 10 quy tắc đã duyệt, xuất PDF qua Microsoft Word COM và ghi sổ theo dõi Excel.
Được thiết kế độc lập, tự định vị mẫu, chạy trơn tru trên mọi máy tính.
"""

import os
import sys
import shutil
import argparse
import json

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

import docx
import openpyxl
from openpyxl.styles import Font, Alignment, Border, Side

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
LOCAL_TEMPLATES_DIR = os.path.join(SKILL_DIR, "templates")

# Mẫu luôn lấy từ templates/ của skill. Đầu ra mặc định là thư mục làm việc hiện hành (Kuro chạy với cwd = thư mục dự án).
MAU_ROOT = LOCAL_TEMPLATES_DIR
TEMP_ROOT = os.getcwd()
SO_THEO_DOI_ROOT = os.getcwd()

def resolve_template_path(code: str) -> str:
    """Tự động tìm kiếm file mẫu (templates/ của skill)"""
    code_upper = code.upper().replace("-", "").replace("_", "")
    target_filename = ""
    if "BM01" in code_upper or code_upper == "BM1":
        target_filename = "BM01_VB-2025_CV_Gui_Ra_Ngoai.docx"
    elif "BM03" in code_upper or "BM3" in code_upper:
        target_filename = "BM3A_VB-2025_VB_Noi_Bo.docx"
    else:
        raise ValueError(f"Không nhận diện được mã biểu mẫu: {code}. Chỉ chấp nhận BM01 hoặc BM03A.")

    candidates = [
        os.path.join(LOCAL_TEMPLATES_DIR, target_filename),
        os.path.join(MAU_ROOT, target_filename),
        os.path.join(os.getcwd(), "templates", target_filename),
        os.path.join(os.getcwd(), "skills", "soan-thao-cong-van", "templates", target_filename)
    ]
    for c in candidates:
        if os.path.exists(c):
            return os.path.abspath(c)
    raise FileNotFoundError(f"Không tìm thấy file mẫu: {target_filename}. Đã tìm ở: {candidates}")

SUPERSCRIPT_MAP = {
    "¹⁰": "", "¹¹": "", "¹²": "", "¹³": "",
    "⁰": "", "¹": "", "²": "", "³": "", "⁴": "",
    "⁵": "", "⁶": "", "⁷": "", "⁸": "", "⁹": ""
}

TYPO_REPLACEMENTS = {
    "Qúy": "Quý",
    "Công công trường": "Các công trường",
}


def clone_template(template_code: str, draft_filename: str, output_dir: str = None) -> str:
    """Sao chép mẫu gốc sang thư mục làm việc tạm thời."""
    target_dir = output_dir if output_dir else TEMP_ROOT
    os.makedirs(target_dir, exist_ok=True)
    
    src = resolve_template_path(template_code)
    if not draft_filename.endswith(".docx"):
        draft_filename += ".docx"
        
    dest = os.path.join(target_dir, draft_filename)
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

    # 4. Khi phát hành: Xóa Text Box Mẫu số BM01
    if is_release and len(doc.tables) >= 3:
        t2 = doc.tables[2]
        xml_t2 = t2._element.xml
        if "BM01" in xml_t2 or "Mẫu số" in xml_t2 or (len(t2.rows) == 1 and len(t2.columns) == 1):
            t2._element.getparent().remove(t2._element)
            print("[OK] Đã xóa khung 'Mẫu số: BM01' ở góc trên phải trang.")

    doc.save(docx_path)
    print(f"[OK] Đã làm sạch và cập nhật file: {docx_path}")
    return docx_path


def export_pdf(docx_path: str, pdf_path: str = None) -> str:
    """Xuất PDF từ file Word qua Microsoft Word COM (khi người dùng yêu cầu)."""
    try:
        import win32com.client
    except ImportError:
        print("[LƯU Ý] Chưa cài đặt pywin32, không thể dùng Word COM để xuất PDF tự động.")
        return ""

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
        os.makedirs(os.path.dirname(excel_path), exist_ok=True)
        # Tạo mới file sổ nếu chưa có
        wb_new = openpyxl.Workbook()
        ws_new = wb_new.active
        ws_new.title = f"Sổ VB {nam}"
        headers = ["STT", "Số văn bản", "Ngày ban hành", "Mẫu VB", "Phòng ban", "Nơi nhận", "Trích yếu nội dung", "Người ký", "Đường dẫn file", "Trạng thái"]
        ws_new.append(headers)
        wb_new.save(excel_path)
    
    wb = openpyxl.load_workbook(excel_path)
    ws = wb.active
    
    target_row = 8 if ws.max_row < 8 else ws.max_row + 1
    
    thin_border = Border(
        left=Side(style='thin', color='BFBFBF'),
        right=Side(style='thin', color='BFBFBF'),
        top=Side(style='thin', color='BFBFBF'),
        bottom=Side(style='thin', color='BFBFBF')
    )
    
    ws.row_dimensions[target_row].height = 24
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
    p_clone = subparsers.add_parser("clone", help="Sao chép mẫu sang thư mục làm việc")
    p_clone.add_argument("template", choices=["BM01", "BM03A", "BM3A"], help="Mã biểu mẫu")
    p_clone.add_argument("filename", help="Tên file nháp đích")
    p_clone.add_argument("--outdir", default=None, help="Thư mục xuất đích")
    
    # Subcommand: clean
    p_clean = subparsers.add_parser("clean", help="Làm sạch văn bản")
    p_clean.add_argument("path", help="Đường dẫn file docx")
    p_clean.add_argument("--release", action="store_true", help="Chế độ phát hành chính thức (xóa khung mẫu số)")
    
    # Subcommand: build-bm03a
    p_bm03a = subparsers.add_parser("build-bm03a", help="Sinh văn bản BM03A chuẩn duyệt từ file JSON cấu hình")
    p_bm03a.add_argument("json_config", help="Đường dẫn file JSON chứa tham số văn bản")
    p_bm03a.add_argument("--out", required=True, help="Đường dẫn file DOCX xuất ra")
    
    # Subcommand: pdf
    p_pdf = subparsers.add_parser("pdf", help="Xuất PDF qua Word COM (khi có yêu cầu)")
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
        clone_template(args.template, args.filename, args.outdir)
    elif args.command == "clean":
        clean_document(args.path, is_release=args.release)
    elif args.command == "build-bm03a":
        from bm03a_builder import build_bm03a_document
        with open(args.json_config, "r", encoding="utf-8") as f:
            cfg = json.load(f)
        build_bm03a_document(
            output_path=args.out,
            trich_yeu=cfg.get("trich_yeu", ""),
            noi_dung_paragraphs=cfg.get("noi_dung_paragraphs", []),
            so_vb=cfg.get("so_vb", "Số:       /PT-KTTC"),
            ngay_vb=cfg.get("ngay_vb", "Hà Nội, ngày ... tháng ... năm 2026"),
            kinh_gui=cfg.get("kinh_gui", "Ban Lãnh đạo Công ty"),
            can_cu_list=cfg.get("can_cu_list"),
            noi_nhan_list=cfg.get("noi_nhan_list"),
            nguoi_ky_chuc_danh=cfg.get("nguoi_ky_chuc_danh", "PHÒNG KỸ THUẬT THI CÔNG"),
            nguoi_ky_ho_ten=cfg.get("nguoi_ky_ho_ten", "TP. Đỗ Đắc Luận"),
            khoi_lanh_dao_title=cfg.get("khoi_lanh_dao_title", "Ý KIẾN BAN LÃNH ĐẠO CÔNG TY"),
            phu_luc_title=cfg.get("phu_luc_title"),
            phu_luc_table_headers=cfg.get("phu_luc_table_headers"),
            phu_luc_table_rows=cfg.get("phu_luc_table_rows"),
            phu_luc_notes=cfg.get("phu_luc_notes"),
            template_path=cfg.get("template_path")
        )
    elif args.command == "pdf":
        export_pdf(args.docx, args.out)
    elif args.command == "log":
        log_document_entry(args.so, args.ngay, args.mau, args.pb, args.nhan, args.trich, args.ky, args.file, args.status, args.nam)
    else:
        parser.print_help()
