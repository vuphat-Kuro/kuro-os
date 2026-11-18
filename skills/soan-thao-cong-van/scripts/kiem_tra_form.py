# -*- coding: utf-8 -*-
"""Kiểm tra một file BM03A có đúng form mẫu duyệt không (không cần Word).

Dùng:  python kiem_tra_form.py NHAP_BM03A_X.docx
In từng mục ĐẠT / LỖI; thoát mã 1 nếu có lỗi. Chạy sau khi dựng file, trước khi báo người dùng.
"""
import os
import re
import sys
import docx
from docx.oxml.ns import qn

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bm03a_builder import SAMPLE


def check(path):
    d, m = docx.Document(path), docx.Document(SAMPLE)
    s, ms = d.sections[0], m.sections[0]
    errs = []

    def ok(cond, msg):
        print(("ĐẠT  " if cond else "LỖI  ") + msg)
        if not cond:
            errs.append(msg)

    ok((s.top_margin, s.bottom_margin, s.left_margin, s.right_margin) == (ms.top_margin, ms.bottom_margin, ms.left_margin, ms.right_margin), "Lề giống mẫu duyệt")
    ok(s.different_first_page_header_footer and len(s.first_page_header.tables) == 1, "Header (logo + thông tin công ty) chỉ ở trang đầu")
    ok(len(d.tables) >= 2 and len(d.tables[0].rows) == len(m.tables[0].rows), "Cấu trúc bảng Số / V/v / ngày / Kính gửi như mẫu")
    sign = d.tables[1].rows[0].cells[1].paragraphs if len(d.tables) > 1 else []
    txt = [p.text.strip() for p in sign if p.text.strip()]
    ok(txt[:1] == ["PHÒNG KỸ THUẬT THI CÔNG"] and len(txt) == 2 and all(p.runs[0].bold for p in sign if p.text.strip()), "Khối ký đúng 2 dòng, in đậm")
    ok(any(p.text.strip() == "Ý KIẾN BAN LÃNH ĐẠO CÔNG TY" for p in d.paragraphs), "Có khối Ý KIẾN BAN LÃNH ĐẠO CÔNG TY")
    nn = d.tables[1].rows[0].cells[0].paragraphs if len(d.tables) > 1 else []
    ok(bool(nn) and nn[0].text.strip() == "Nơi nhận:" and nn[-1].text.strip() == "- Lưu: VT, KTTC.", "Nơi nhận kết thúc bằng '- Lưu: VT, KTTC.'")
    body = [p for p in d.paragraphs if p.text.strip() and p.paragraph_format.first_line_indent]
    ok(any(p.text.strip() == "Trân trọng cảm ơn!" for p in body), "Có câu kết 'Trân trọng cảm ơn!' (dấu !)")
    sizes = {r.font.size.pt for p in body for r in p.runs if r.font.size}
    ok(sizes <= {13.0}, f"Thân bài cỡ 13 (thấy: {sorted(sizes)})")
    ok(not any("—" in p.text for p in d.paragraphs), "Không dùng gạch dài")
    alltxt = "\n".join(p.text for p in d.paragraphs) + "\n".join(c.text for t in d.tables for r in t.rows for c in r.cells)
    for kw in ("Mẫu số", "PHỤC LỤC", "Căn cứ Báo cáo số 06/6.2026/XL01", "XL01 CLLS", "cấp phối đá dăm"):
        ok(kw not in alltxt, f"Không còn chữ của mẫu cũ: {kw!r}")
    left = re.findall(r"\[CẦN BỔ SUNG[^\]]*\]", alltxt)
    print(("CHÚ Ý " + "; ".join(sorted(set(left)))) if left else "ĐẠT  Không còn [CẦN BỔ SUNG]")
    return errs


if __name__ == "__main__":
    sys.exit(1 if check(sys.argv[1]) else 0)
