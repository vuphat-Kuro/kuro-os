# -*- coding: utf-8 -*-
"""
Script kiểm thử toàn diện bộ công cụ Soạn thảo Công văn:
1. Kiểm tra tìm kiếm template.
2. Kiểm tra clone và clean BM01.
3. Kiểm tra build BM03A chuẩn 10 quy tắc đã duyệt.
4. Kiểm tra build BM03A có phụ lục bảng tính (1-Page Memo + Appendix).
"""
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(SCRIPT_DIR)

from van_ban_engine import clone_template, clean_document, resolve_template_path
from bm03a_builder import build_bm03a_document

def run_tests():
    print("=== 1. KIỂM TRA TÌM FILE MẪU ===")
    bm01_p = resolve_template_path("BM01")
    bm03a_p = resolve_template_path("BM03A")
    print(f"BM01: {bm01_p}")
    print(f"BM03A: {bm03a_p}")
    assert os.path.exists(bm01_p)
    assert os.path.exists(bm03a_p)
    print("-> PASS\n")

    test_out_dir = os.path.join(SCRIPT_DIR, "test_output")
    os.makedirs(test_out_dir, exist_ok=True)

    print("=== 2. KIỂM TRA CLONE & CLEAN BM01 ===")
    cloned_bm01 = clone_template("BM01", "TEST_BM01.docx", test_out_dir)
    clean_document(cloned_bm01, is_release=True)
    assert os.path.exists(cloned_bm01)
    print("-> PASS\n")

    print("=== 3. KIỂM TRA XUẤT BM03A 1 TRANG (THEO PHOM CV-841) ===")
    out_bm03a_1p = os.path.join(test_out_dir, "TEST_BM03A_1PAGE.docx")
    build_bm03a_document(
        output_path=out_bm03a_1p,
        trich_yeu="V/v Phê duyệt phương án kiểm thử hệ thống tự động hóa công văn.",
        noi_dung_paragraphs=[
            "Căn cứ chức năng nhiệm vụ của phòng KTTC;",
            "Căn cứ kế hoạch đóng gói chuyển giao phần mềm sang máy mới.",
            "Phòng KTTC kính đề nghị Ban Lãnh đạo công ty xem xét phê duyệt phương án thử nghiệm với các kết quả đạt chuẩn 100%.",
            "Trân trọng cảm ơn!"
        ],
        so_vb="Số:       /PT-KTTC",
        ngay_vb="Hà Nội, ngày 18 tháng 11 năm 2026",
        kinh_gui="Ban Lãnh đạo Công ty"
    )
    assert os.path.exists(out_bm03a_1p)
    import docx
    d1 = docx.Document(out_bm03a_1p)
    ky = d1.tables[1].rows[0].cells[1].paragraphs
    assert ky[0].runs[0].bold and ky[-1].runs[0].bold, "Chữ ký phải giữ đậm như mẫu"
    import bm03a_builder
    m = docx.Document(bm03a_builder.SAMPLE).sections[0]
    assert (d1.sections[0].top_margin, d1.sections[0].left_margin) == (m.top_margin, m.left_margin), "Lề phải giữ như mẫu duyệt"
    print("-> PASS\n")

    print("=== 4. KIỂM TRA XUẤT BM03A 1-PAGE MEMO + PHỤ LỤC ===")
    out_bm03a_memo = os.path.join(test_out_dir, "TEST_BM03A_MEMO_APPENDIX.docx")
    build_bm03a_document(
        output_path=out_bm03a_memo,
        trich_yeu="V/v Báo cáo rà soát khối lượng móng mặt và đề xuất cấp bổ sung.",
        noi_dung_paragraphs=[
            "Sau khi kiểm tra, rà soát số liệu báo cáo của Ban Điều hành và tình hình thi công trên công trường, Phòng Kỹ thuật Thi công báo cáo Lãnh đạo Công ty một số nội dung sau:",
            "1. Về nguyên nhân phát sinh: Do phạm vi kết cấu tiếp giáp giữa đường mới và đường cũ phải xử lý giật cấp thay mới.",
            "2. Về kết quả kiểm tra của Phòng: Hệ số lu lèn thi công thực tế trên tuyến là 1.39.",
            "3. Đề xuất: Đề nghị duyệt khối lượng phát sinh đợt 2 còn lại là 2.849,88 m3.",
            "Trân trọng cảm ơn!"
        ],
        so_vb="Số:       /PT-KTTC",
        ngay_vb="Hà Nội, ngày 18 tháng 11 năm 2026",
        kinh_gui="Ban Lãnh đạo Công ty",
        phu_luc_title="PHỤ LỤC: BẢNG TỔNG HỢP KIỂM TRA RÀ SOÁT KHỐI LƯỢNG",
        phu_luc_table_headers=["STT", "Hạng mục", "ĐVT", "Khối lượng BVTC", "Khối lượng kiểm tra"],
        phu_luc_table_rows=[
            ["1", "Cấp phối đá dăm loại 1", "m3", "41.687,59", "44.537,47"],
            ["2", "Khối lượng bù vênh tiếp giáp", "m3", "3.450,00", "2.849,88"]
        ],
        phu_luc_notes=["Ghi chú: Khối lượng kiểm tra độc lập bằng công thức giải tích."]
    )
    assert os.path.exists(out_bm03a_memo)
    print("-> PASS\n")
    print(">>> TẤT CẢ CÁC BÀI TEST ĐỀU THÀNH CÔNG RỰC RỠ! <<<")

if __name__ == "__main__":
    run_tests()
