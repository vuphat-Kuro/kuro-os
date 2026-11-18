# -*- coding: utf-8 -*-
"""
bm03a_builder.py - Soạn văn bản BM03A bằng cách NHÂN BẢN MẪU ĐÃ DUYỆT rồi chỉ thay nội dung.

Mẫu gốc: templates/Mau_BM03A_Trinh_Lanh_Dao_Da_Duyet.docx (header logo, lề, cỡ chữ, dãn dòng, bảng ký,
khối Ý kiến Ban Lãnh đạo đều giữ nguyên từ mẫu). Hàm này KHÔNG dựng lại định dạng: mỗi đoạn mới là bản sao
của một đoạn mẫu (căn cứ / mở đầu / thân bài) rồi thay chữ. Số trang tùy nội dung, không khống chế.

Chữ đậm trong đoạn: bọc bằng **...** (ví dụ "**2.849,88 m3**").
"""
import copy
import os
import re
import docx
from docx.oxml import parse_xml
from docx.oxml.ns import qn, nsdecls

SKILL_DIR = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
SAMPLE = os.path.join(SKILL_DIR, "templates", "Mau_BM03A_Trinh_Lanh_Dao_Da_Duyet.docx")
_W14 = "{http://schemas.microsoft.com/office/word/2010/wordml}"
_NUM = re.compile(r"^[\s\d.,\-+%/]+$")


# ---------- chữ trong đoạn: giữ rPr của run đầu, đổi nội dung ----------
def _set_text(p, text):
    runs = p.findall(qn("w:r"))
    proto = next((r for r in runs if r.find(qn("w:t")) is not None), runs[0] if runs else None)
    rpr = proto.find(qn("w:rPr")) if proto is not None else None
    for r in runs:
        p.remove(r)
    for i, part in enumerate(re.split(r"\*\*", text)):
        if part == "":
            continue
        r = parse_xml(f'<w:r {nsdecls("w")}><w:t xml:space="preserve"/></w:r>')
        r.find(qn("w:t")).text = part
        if rpr is not None:
            new = copy.deepcopy(rpr)
            if "**" in text:   # có đánh dấu đậm: chỉ phần giữa cặp ** đậm, còn lại thường
                for tag in ("w:b", "w:bCs"):
                    for e in new.findall(qn(tag)):
                        new.remove(e)
                if i % 2 == 1:
                    new.insert(0, parse_xml(f'<w:b {nsdecls("w")}/>'))
            r.insert(0, new)
        p.append(r)


def _clone(proto, text):
    p = copy.deepcopy(proto)
    for a in (_W14 + "paraId", _W14 + "textId"):
        p.attrib.pop(a, None)
    _set_text(p, text)
    return p


def _paras(tc):
    return tc.findall(qn("w:p"))


# ---------- bảng phụ lục theo kiểu bảng mẫu (khung đơn, đầu bảng tô xanh nhạt, cỡ 11) ----------
def _cell(text, w, bold=False, align="left", fill=False):
    shd = '<w:shd w:val="clear" w:color="auto" w:fill="DAE9F7"/>' if fill else ""
    b = "<w:b/><w:bCs/>" if bold else ""
    bd = "".join(f'<w:{s} w:val="single" w:sz="4" w:space="0" w:color="auto"/>' for s in ("top", "left", "bottom", "right"))
    tc = parse_xml(
        f'<w:tc {nsdecls("w")}><w:tcPr><w:tcW w:w="{w}" w:type="dxa"/><w:tcBorders>{bd}</w:tcBorders>{shd}'
        f'<w:vAlign w:val="center"/></w:tcPr><w:p><w:pPr><w:jc w:val="{align}"/></w:pPr></w:p></w:tc>')
    p = tc.find(qn("w:p"))
    p.append(parse_xml(f'<w:r {nsdecls("w")}><w:rPr>{b}<w:color w:val="000000"/><w:sz w:val="22"/><w:szCs w:val="22"/></w:rPr></w:r>'))
    _set_text(p, str(text) if str(text) else " ")
    return tc


def _table(headers, rows, widths=None, total=9100):
    n = len(headers)
    if not widths:   # cột TT hẹp, còn lại chia theo độ dài chữ
        first = 560 if str(headers[0]).strip().upper() in ("TT", "STT") else None
        lens = [max(6, min(40, max(len(str(r[i])) for r in rows + [headers]))) for i in range(n)]
        rest = total - (first or 0)
        idx = range(1 if first else 0, n)
        s = sum(lens[i] for i in idx)
        widths = ([first] if first else []) + [int(rest * lens[i] / s) for i in idx]
    grid = "".join(f'<w:gridCol w:w="{w}"/>' for w in widths)
    tbl = parse_xml(f'<w:tbl {nsdecls("w")}><w:tblPr><w:tblW w:w="{sum(widths)}" w:type="dxa"/><w:tblLayout w:type="fixed"/></w:tblPr>'
                    f'<w:tblGrid>{grid}</w:tblGrid></w:tbl>')

    def row(vals, head):
        tr = parse_xml(f'<w:tr {nsdecls("w")}><w:trPr><w:cantSplit/>{"<w:tblHeader/>" if head else ""}</w:trPr></w:tr>')
        for i, v in enumerate(vals):
            al = "center" if head or i == 0 else ("right" if _NUM.match(str(v)) else "left")
            tr.append(_cell(v, widths[i], bold=head, align=al, fill=head))
        return tr
    tbl.append(row(headers, True))
    for r in rows:
        tbl.append(row(r, False))
    return tbl


def build_bm03a_document(
    output_path: str,
    trich_yeu: str,
    noi_dung_paragraphs: list,
    so_vb: str = "Số:       /PT-KTTC",
    ngay_vb: str = "Hà Nội, ngày ... tháng ... năm 2026",
    kinh_gui="Ban Lãnh đạo Công ty",
    can_cu_list: list = None,
    noi_nhan_list: list = None,
    nguoi_ky_chuc_danh: str = "PHÒNG KỸ THUẬT THI CÔNG",
    nguoi_ky_ho_ten: str = "TP. Đỗ Đắc Luận",
    khoi_lanh_dao_title: str = None,
    phu_luc_title: str = None,
    phu_luc_table_headers: list = None,
    phu_luc_table_rows: list = None,
    phu_luc_notes: list = None,
    phu_luc_col_widths: list = None,
    template_path: str = None,
) -> str:
    """Nhân bản mẫu duyệt, thay nội dung, lưu ra output_path. Trả về đường dẫn tuyệt đối."""
    src = template_path or SAMPLE
    if not os.path.isfile(src):
        raise FileNotFoundError(f"Không thấy file mẫu: {src}")
    doc = docx.Document(src)
    body = doc.element.body
    kids = list(body.iterchildren())
    tbls = [k for k in kids if k.tag == qn("w:tbl")]
    t_head, t_sign = tbls[0], tbls[1]
    t_appx = tbls[2] if len(tbls) > 2 else None
    # --- bảng đầu: Số + V/v | ngày | Kính gửi ---
    r0, r1 = t_head.findall(qn("w:tr"))
    c_so, c_ngay = r0.findall(qn("w:tc"))
    c_kg = r1.findall(qn("w:tc"))[1]
    so_p, vv_p = _paras(c_so)[:2]
    _set_text(so_p, so_vb)
    vv = trich_yeu.strip()
    vv = "V/v " + re.sub(r"^V/v:?\s*", "", vv)
    _set_text(vv_p, vv)
    _set_text(_paras(c_ngay)[0], ngay_vb)
    kg_p = _paras(c_kg)[1]
    kgs = [kinh_gui] if isinstance(kinh_gui, str) else list(kinh_gui)
    _set_text(kg_p, kgs[0])
    for extra in reversed(kgs[1:]):
        kg_p.addnext(_clone(kg_p, extra))

    # --- thân: căn cứ / mở đầu / các đoạn ---
    mid = kids[kids.index(t_head) + 1: kids.index(t_sign)]
    ps = [k for k in mid if k.tag == qn("w:p")]
    p_cc, p_cc_last, p_open, p_body = ps[0], ps[2], ps[3], ps[4]
    new = []
    cc = list(can_cu_list or [])
    for i, t in enumerate(cc):
        new.append(_clone(p_cc_last if i == len(cc) - 1 else p_cc, t))
    for i, item in enumerate(noi_dung_paragraphs):
        new.append(_clone(p_open if i == 0 else p_body, item["text"] if isinstance(item, dict) else str(item)))
    for k in mid:
        body.remove(k)
    for e in new:
        t_sign.addprevious(e)

    # --- Nơi nhận + chữ ký ---
    c_nn, c_ky = t_sign.find(qn("w:tr")).findall(qn("w:tc"))
    nn = _paras(c_nn)
    item_proto = nn[1]
    for p in nn[1:]:
        c_nn.remove(p)
    last = nn[0]
    for t in (noi_nhan_list or ["- Như trên;", "- Phòng KTKH (để thực hiện);", "- BĐH dự án (để thực hiện);", "- Lưu: VT, KTTC."]):
        e = _clone(item_proto, t)
        last.addnext(e)
        last = e
    ky = _paras(c_ky)
    _set_text(ky[0], nguoi_ky_chuc_danh)
    _set_text(ky[-1], nguoi_ky_ho_ten)

    # --- khối Ý kiến Lãnh đạo: giữ đúng mẫu (kể cả các dòng trống để viết tay) ---
    after = [k for k in body.iterchildren() if k is not t_appx and k.tag == qn("w:p")]
    if khoi_lanh_dao_title:
        yk = next(k for k in after if "Ý KIẾN" in "".join(k.itertext()))
        _set_text(yk, khoi_lanh_dao_title)

    # --- phụ lục: bỏ phần mẫu cũ, dựng lại theo kiểu bảng mẫu ---
    kids = list(body.iterchildren())
    tail = kids[kids.index(t_sign) + 1:-1]   # sau bảng ký, trước sectPr
    title_proto = next((k for k in tail if "PHỤC LỤC" in "".join(k.itertext()) or "PHỤ LỤC" in "".join(k.itertext())), None)
    drop = tail[tail.index(title_proto):] if title_proto is not None else []
    for k in drop:
        body.remove(k)
    sect = body.find(qn("w:sectPr"))
    if phu_luc_title and title_proto is not None:
        t = _clone(title_proto, phu_luc_title)
        ppr = t.find(qn("w:pPr"))
        ppr.insert(0, parse_xml(f'<w:pageBreakBefore {nsdecls("w")}/>'))
        sect.addprevious(t)
        gap = parse_xml(f'<w:p {nsdecls("w")}><w:pPr><w:spacing w:before="120"/></w:pPr></w:p>')
        sect.addprevious(gap)
        if phu_luc_table_headers and phu_luc_table_rows:
            sect.addprevious(_table(list(phu_luc_table_headers), [list(r) for r in phu_luc_table_rows], phu_luc_col_widths))
        for n in phu_luc_notes or []:
            sect.addprevious(_clone(p_body, n))
        sect.addprevious(parse_xml(f'<w:p {nsdecls("w")}/>'))
    else:
        sect.addprevious(parse_xml(f'<w:p {nsdecls("w")}/>'))

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    doc.save(output_path)
    print(f"[OK] Đã xuất văn bản BM03A (nhân bản mẫu duyệt) tại: {output_path}")
    return os.path.abspath(output_path)
