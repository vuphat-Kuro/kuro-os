#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
docxkit — Thao tác hàng loạt trên file Word đã có.

Các lệnh:
    ghep       Ghép nhiều file .docx thành một (mỗi file một trang)
    thay       Tìm & thay chữ trong hàng loạt file, giữ nguyên định dạng
    lay-bang   Trích mọi bảng trong file Word ra Excel
    lay-chu    Trích toàn văn ra .txt (để tìm kiếm, đối chiếu)
    doi-ten    Đổi tên hàng loạt theo bảng ánh xạ Excel

Ví dụ:
    python docxkit.py ghep --vao "bien-ban/*.docx" --ra tap-hop.docx
    python docxkit.py thay --vao "hoso/*.docx" --tu "Cầu Quảng Sơn" --thanh "Cầu Tân An"
    python docxkit.py lay-bang --vao bao-cao.docx --ra bang.xlsx
"""

import argparse
import copy
import glob
import re
from pathlib import Path

import pandas as pd
from docx import Document
from docx.enum.text import WD_BREAK


def mo_rong(mau, duoi=".docx"):
    kq = []
    for phan in str(mau).split(","):
        phan = phan.strip().strip('"')
        if not phan:
            continue
        p = Path(phan)
        if p.is_dir():
            kq += sorted(p.glob(f"*{duoi}"))
        elif any(k in phan for k in "*?["):
            kq += sorted(Path(x) for x in glob.glob(phan, recursive=True))
        elif p.exists():
            kq.append(p)
    return [p for p in kq if not p.name.startswith("~$")]


def moi_doan(doc):
    def tu_bang(bang):
        for hang in bang.rows:
            for o in hang.cells:
                for p in o.paragraphs:
                    yield p
                for b2 in o.tables:
                    yield from tu_bang(b2)

    for p in doc.paragraphs:
        yield p
    for b in doc.tables:
        yield from tu_bang(b)
    for sec in doc.sections:
        for phan in (sec.header, sec.footer):
            if phan is None:
                continue
            for p in phan.paragraphs:
                yield p
            for b in phan.tables:
                yield from tu_bang(b)


# ----------------------------------------------------------------------------

def lenh_ghep(a):
    files = mo_rong(a.vao)
    if len(files) < 2:
        raise SystemExit("❌ Cần ít nhất 2 file để ghép.")
    if a.theo_ten:
        files = sorted(files, key=lambda p: p.name)

    dich = Document(str(files[0]))
    for f in files[1:]:
        if a.ngat_trang:
            dich.add_paragraph().add_run().add_break(WD_BREAK.PAGE)
        nguon = Document(str(f))
        for phan_tu in nguon.element.body:
            # bỏ thẻ sectPr cuối để không đẻ thêm section thừa
            if phan_tu.tag.endswith("}sectPr"):
                continue
            dich.element.body.append(copy.deepcopy(phan_tu))

    Path(a.ra).parent.mkdir(parents=True, exist_ok=True)
    dich.save(a.ra)
    print(f"✅ Ghép {len(files)} file → {a.ra}")
    print("   Lưu ý: mỗi file gốc có thể có style riêng — mở kiểm tra "
          "định dạng trước khi in.")


def lenh_thay(a):
    files = mo_rong(a.vao)
    if not files:
        raise SystemExit("❌ Không tìm thấy file .docx nào.")
    cap = [(a.tu, a.thanh)] if a.tu else []
    if a.bang:
        b = pd.read_excel(a.bang)
        cot = list(b.columns)[:2]
        cap += [(str(r[cot[0]]), str(r[cot[1]])) for _, r in b.iterrows()]
    if not cap:
        raise SystemExit("❌ Cần --tu/--thanh hoặc --bang.")

    tong = 0
    for f in files:
        doc = Document(str(f))
        dem_file = 0
        for p in moi_doan(doc):
            van_ban = "".join(r.text for r in p.runs)
            if not van_ban:
                continue
            moi = van_ban
            for tu, thanh in cap:
                if a.hoa_thuong:
                    moi = re.sub(re.escape(tu), thanh, moi, flags=re.IGNORECASE)
                else:
                    moi = moi.replace(tu, thanh)
            if moi != van_ban:
                dem_file += 1
                p.runs[0].text = moi
                for r in p.runs[1:]:
                    r.text = ""
        if dem_file:
            dich = Path(a.ra_thu_muc) / f.name if a.ra_thu_muc else f
            if a.ra_thu_muc:
                Path(a.ra_thu_muc).mkdir(parents=True, exist_ok=True)
            doc.save(str(dich))
            print(f"   {f.name}: sửa {dem_file} đoạn → {dich}")
            tong += dem_file
        else:
            print(f"   {f.name}: không có gì để sửa")
    print(f"✅ Sửa tổng cộng {tong} đoạn trong {len(files)} file")
    if not a.ra_thu_muc:
        print("   ⚠️  Đã ghi đè file gốc. Lần sau dùng --ra-thu-muc để giữ bản gốc.")


def lenh_lay_bang(a):
    files = mo_rong(a.vao)
    cac_sheet, dem = {}, 0
    for f in files:
        doc = Document(str(f))
        for i, t in enumerate(doc.tables, 1):
            du_lieu = [[o.text.strip() for o in h.cells] for h in t.rows]
            if len(du_lieu) < 2:
                continue
            df = pd.DataFrame(du_lieu[1:], columns=du_lieu[0])
            ten = f"{f.stem[:22]}_B{i}"[:31]
            cac_sheet[ten] = df
            dem += 1
    if not cac_sheet:
        raise SystemExit("❌ Không tìm thấy bảng nào.")
    Path(a.ra).parent.mkdir(parents=True, exist_ok=True)
    with pd.ExcelWriter(a.ra, engine="openpyxl") as w:
        for ten, df in cac_sheet.items():
            df.to_excel(w, sheet_name=ten, index=False)
    print(f"✅ Trích {dem} bảng từ {len(files)} file → {a.ra}")


def lenh_lay_chu(a):
    files = mo_rong(a.vao)
    Path(a.ra).parent.mkdir(parents=True, exist_ok=True)
    with open(a.ra, "w", encoding="utf-8") as fh:
        for f in files:
            fh.write(f"\n{'=' * 60}\n{f.name}\n{'=' * 60}\n")
            doc = Document(str(f))
            for p in doc.paragraphs:
                if p.text.strip():
                    fh.write(p.text + "\n")
            for t in doc.tables:
                for h in t.rows:
                    fh.write(" | ".join(o.text.strip() for o in h.cells) + "\n")
    print(f"✅ Trích văn bản {len(files)} file → {a.ra}")


def lenh_doi_ten(a):
    b = pd.read_excel(a.bang)
    cot = list(b.columns)[:2]
    thu_muc = Path(a.thu_muc)
    dem, thieu = 0, []
    for _, r in b.iterrows():
        cu = thu_muc / str(r[cot[0]]).strip()
        moi = thu_muc / re.sub(r'[\\/:*?"<>|]', "_", str(r[cot[1]]).strip())
        if not cu.exists():
            thieu.append(cu.name)
            continue
        if a.thu:
            print(f"   {cu.name}  →  {moi.name}")
        else:
            cu.rename(moi)
        dem += 1
    print(f"{'🔎 Chạy thử: ' if a.thu else '✅ '}{dem} file"
          f"{' sẽ được' if a.thu else ' đã'} đổi tên")
    if thieu:
        print(f"⚠️  {len(thieu)} file không tìm thấy: {', '.join(thieu[:8])}")


def main():
    p = argparse.ArgumentParser(
        description="docxkit — thao tác hàng loạt trên file Word",
        formatter_class=argparse.RawDescriptionHelpFormatter, epilog=__doc__)
    sub = p.add_subparsers(dest="lenh", required=True)

    s = sub.add_parser("ghep", help="Ghép nhiều .docx thành một")
    s.add_argument("--vao", required=True)
    s.add_argument("--ra", required=True)
    s.add_argument("--ngat-trang", action="store_true", default=True)
    s.add_argument("--theo-ten", action="store_true", help="Sắp xếp theo tên file")
    s.set_defaults(func=lenh_ghep)

    s = sub.add_parser("thay", help="Tìm & thay hàng loạt")
    s.add_argument("--vao", required=True)
    s.add_argument("--tu", default="")
    s.add_argument("--thanh", default="")
    s.add_argument("--bang", default="", help="Excel 2 cột: tìm | thay")
    s.add_argument("--ra-thu-muc", default="", help="Bỏ trống = ghi đè file gốc")
    s.add_argument("--hoa-thuong", action="store_true", help="Không phân biệt hoa/thường")
    s.set_defaults(func=lenh_thay)

    s = sub.add_parser("lay-bang", help="Trích bảng ra Excel")
    s.add_argument("--vao", required=True)
    s.add_argument("--ra", required=True)
    s.set_defaults(func=lenh_lay_bang)

    s = sub.add_parser("lay-chu", help="Trích toàn văn ra .txt")
    s.add_argument("--vao", required=True)
    s.add_argument("--ra", required=True)
    s.set_defaults(func=lenh_lay_chu)

    s = sub.add_parser("doi-ten", help="Đổi tên hàng loạt theo bảng Excel")
    s.add_argument("--thu-muc", required=True)
    s.add_argument("--bang", required=True, help="Excel 2 cột: tên cũ | tên mới")
    s.add_argument("--thu", action="store_true", help="Chạy thử, chưa đổi thật")
    s.set_defaults(func=lenh_doi_ten)

    a = p.parse_args()
    a.func(a)


if __name__ == "__main__":
    main()
