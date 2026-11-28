"""Sổ bóc khối lượng của dự án: AI bóc xong bảng nào thì ghi bảng đó ra Excel, khỏi mất số khi nén ngữ cảnh hay đổi AI.

Một dự án một sổ BOC_KHOI_LUONG.xlsx (mỗi hạng mục một sheet, lưu lại cùng tên thì thay sheet cũ) và bản .md cùng tên
để AI nào cũng đọc lại được bằng công cụ đọc tệp (Read không mở được .xlsx).
"""
import re
from datetime import datetime
from pathlib import Path

import config

TEN_SO = "BOC_KHOI_LUONG"
_KY_TU_CAM = re.compile(r"[\[\]:*?/\\]")


def noi_luu(ws_dir) -> Path:
    """03_KET_QUA nếu dự án theo chuẩn Kuro (sổ là sản phẩm nộp QS), không thì gốc dự án."""
    ws = Path(ws_dir)
    kq = ws / "03_KET_QUA"
    return (kq if kq.is_dir() else ws) / f"{TEN_SO}.xlsx"


def _so(v):
    """Chuỗi số kiểu '12.5' thành số để Excel cộng được. Có dấu phẩy thì giữ chữ: '12,5' kiểu Việt hay '1,250' kiểu Anh
    không phân biệt được, đoán sai là sai khối lượng."""
    if isinstance(v, str):
        s = v.strip()
        if re.fullmatch(r"-?\d+(\.\d+)?", s):
            return float(s) if "." in s else int(s)
    return v


def _ten_sheet(ten: str) -> str:
    return (_KY_TU_CAM.sub("-", ten).strip("' ") or "Hang muc")[:31]


def luu(ten: str, bang: list, nguon: str, ws_dir, ghi_chu: str = "") -> str:
    if config.la_kho_mang(ws_dir):
        raise ValueError("dự án đang mở nằm trên kho mạng công ty (chỉ đọc): mở thư mục dự án trên máy rồi lưu")
    if not bang or not all(isinstance(r, list) for r in bang) or len(bang) < 2:
        raise ValueError("bang phải là danh sách các dòng, dòng đầu là tiêu đề cột, có ít nhất 1 dòng số liệu")
    if not (nguon or "").strip():
        raise ValueError("thiếu nguon (tệp bản vẽ, số trang, tên hình chiếu/bảng)")
    import openpyxl
    from openpyxl.styles import Font
    f = noi_luu(ws_dir)
    wb = openpyxl.load_workbook(f) if f.is_file() else openpyxl.Workbook()
    if not f.is_file():
        wb.remove(wb.active)
    sh = _ten_sheet(ten)
    if sh in wb.sheetnames:
        wb.remove(wb[sh])
    ws = wb.create_sheet(sh)
    for r in bang:
        ws.append([_so(v) for v in r])
    for c in ws[1]:
        c.font = Font(bold=True)
    luc = f"{datetime.now():%d/%m/%Y %H:%M}"
    ws.append([])
    ws.append(["Nguồn:", nguon])
    if ghi_chu:
        ws.append(["Ghi chú:", ghi_chu])
    ws.append(["Lưu lúc:", luc])
    try:
        wb.save(f)
    except PermissionError:
        raise ValueError(f"không ghi được {f}: tệp đang mở trong Excel, nhờ người dùng đóng tệp rồi lưu lại")
    _ghi_md(wb, f.with_suffix(".md"))
    return (f"Đã lưu bảng '{sh}' ({len(bang) - 1} dòng) vào {f} (sheet '{sh}'), bản đọc lại cho AI: {f.with_suffix('.md')}. "
            "Báo đường dẫn tệp cho người dùng.")


def _o(v) -> str:
    return "" if v is None else str(v).replace("|", "/").replace("\n", " ")


def _ghi_md(wb, md: Path):
    phan = [f"# Sổ bóc khối lượng (tự sinh từ {md.with_suffix('.xlsx').name}, sửa trong Excel)"]
    for ws in wb.worksheets:
        dong = [list(r) for r in ws.iter_rows(values_only=True)]
        trong = next((i for i, r in enumerate(dong) if not any(v is not None for v in r)), len(dong))
        bang, cuoi = dong[:trong], dong[trong + 1:]
        if not bang:
            continue
        n = max(len(r) for r in bang)
        phan.append(f"\n## {ws.title}\n")
        phan.append("| " + " | ".join(_o(v) for v in bang[0]) + " |")
        phan.append("|" + "---|" * n)
        phan += ["| " + " | ".join(_o(v) for v in r) + " |" for r in bang[1:]]
        phan += [f"\n{_o(r[0])} {_o(r[1]) if len(r) > 1 else ''}" for r in cuoi if r and r[0]]
    md.write_text("\n".join(phan) + "\n", encoding="utf-8")


if __name__ == "__main__":   # tự kiểm: lưu 2 lần cùng tên chỉ còn 1 sheet, số chuỗi thành số
    import tempfile
    d = tempfile.mkdtemp()
    luu("Cọc D1000", [["Cấu kiện", "ĐV", "KL"], ["Cọc", "m3", "12.5"]], "bv.pdf tr3", d)
    print(luu("Cọc D1000", [["Cấu kiện", "ĐV", "KL"], ["Cọc", "m3", "1250.5"], ["Bệ", "m3", "12,5"]], "bv.pdf tr3", d))
    import openpyxl
    wb = openpyxl.load_workbook(noi_luu(d))
    assert wb.sheetnames == ["Cọc D1000"] and wb["Cọc D1000"]["C2"].value == 1250.5
    assert wb["Cọc D1000"]["C3"].value == "12,5"
    assert "| Cọc | m3 | 1250.5 |" in noi_luu(d).with_suffix(".md").read_text(encoding="utf-8")
    print("OK")
