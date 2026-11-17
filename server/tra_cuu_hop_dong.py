"""Module tra cứu hợp đồng kinh tế và dự án từ kho dữ liệu mạng Phương Thành.

Tra cứu trực tiếp qua 2 file Excel index đầu mục:
1. TỔNG HỢP.xlsx (Hợp đồng thầu phụ & đội thi công)
2. DANH MỤC HỌP ĐỒNG, PHỤ LỤC HỢP ĐỒNG DỰ ÁN.xls (Hợp đồng dự án / CĐT)

TUYỆT ĐỐI KHÔNG quét đệ quy thư mục hợp đồng để tránh treo nghẽn mạng.
"""
from __future__ import annotations

import re
import time
import unicodedata
from pathlib import Path
from typing import Any

from server import config

# Đường dẫn mặc định tới 2 file Excel index
FILE_INDEX_THAU_PHU = Path(config.DATA_HD_THAU_PHU) / "TỔNG HỢP.xlsx"
FILE_INDEX_DU_AN = Path(config.DATA_HD_DU_AN) / "DANH MỤC HỌP ĐỒNG, PHỤ LỤC HỢP ĐỒNG DỰ ÁN.xls"

# Bộ nhớ đệm (Cache) trong tiến trình để tra cứu tức thì < 0.05s
_CACHE: dict[str, Any] = {
    "thau_phu": {"mtime": 0, "records": []},
    "du_an": {"mtime": 0, "records": []},
}


def _bo_dau(s: str) -> str:
    """Chuyển tiếng Việt có dấu thành không dấu để tìm kiếm mềm dẻo."""
    if not s:
        return ""
    s = unicodedata.normalize("NFD", str(s))
    s = re.sub(r"[\u0300-\u036f]", "", s)
    s = s.replace("đ", "d").replace("Đ", "D")
    return s.lower().strip()


def _format_cell(val: Any) -> str:
    if val is None:
        return ""
    if isinstance(val, float) and val.is_integer():
        return str(int(val))
    return str(val).strip()


def _load_thau_phu(file_path: Path | None = None) -> list[dict]:
    p = file_path or FILE_INDEX_THAU_PHU
    if not p.is_file():
        return []
    try:
        cur_mtime = p.stat().st_mtime
    except Exception:
        cur_mtime = 0

    cache = _CACHE["thau_phu"]
    if cache["records"] and cache["mtime"] == cur_mtime:
        return cache["records"]

    import openpyxl

    records = []
    try:
        wb = openpyxl.load_workbook(p, read_only=True, data_only=True)
        for sname in wb.sheetnames:
            ws = wb[sname]
            header_idx = None
            col_map: dict[str, int] = {}

            for row_idx, row in enumerate(ws.iter_rows(values_only=True)):
                if row_idx > 15 and header_idx is None:
                    break
                row_str = [_format_cell(c).lower() for c in row]
                if any("tên hợp đồng" in c or "số hợp đồng" in c or "hợp đồng" in c for c in row_str) and any(
                    "đối tác" in c or "nội dung" in c or "công trình" in c for c in row_str
                ):
                    header_idx = row_idx
                    for col_idx, c in enumerate(row_str):
                        if "tên hợp đồng" in c or "số hđ" in c or "số hợp đồng" in c:
                            col_map["so_hd"] = col_idx
                        elif "công trình" in c or "dự án" in c:
                            col_map["cong_trinh"] = col_idx
                        elif "ngày" in c:
                            col_map["ngay_hd"] = col_idx
                        elif "nội dung" in c:
                            col_map["noi_dung"] = col_idx
                        elif "đối tác" in c or "nhà thầu" in c or "đơn vị" in c:
                            col_map["doi_tac"] = col_idx
                        elif "giá trị" in c:
                            col_map["gia_tri"] = col_idx
                        elif "phòng" in c:
                            col_map["phong_ql"] = col_idx
                        elif "soạn thảo" in c or "người ký" in c:
                            col_map["nguoi_soan"] = col_idx
                    break

            if header_idx is None:
                continue

            for row_idx, row in enumerate(ws.iter_rows(values_only=True)):
                if row_idx <= header_idx:
                    continue
                so_hd = _format_cell(row[col_map["so_hd"]]) if "so_hd" in col_map and col_map["so_hd"] < len(row) else ""
                noi_dung = _format_cell(row[col_map["noi_dung"]]) if "noi_dung" in col_map and col_map["noi_dung"] < len(row) else ""
                doi_tac = _format_cell(row[col_map["doi_tac"]]) if "doi_tac" in col_map and col_map["doi_tac"] < len(row) else ""
                cong_trinh = _format_cell(row[col_map["cong_trinh"]]) if "cong_trinh" in col_map and col_map["cong_trinh"] < len(row) else ""
                ngay_hd = _format_cell(row[col_map["ngay_hd"]]) if "ngay_hd" in col_map and col_map["ngay_hd"] < len(row) else ""
                gia_tri = _format_cell(row[col_map["gia_tri"]]) if "gia_tri" in col_map and col_map["gia_tri"] < len(row) else ""
                phong_ql = _format_cell(row[col_map["phong_ql"]]) if "phong_ql" in col_map and col_map["phong_ql"] < len(row) else ""

                if not so_hd and not noi_dung and not doi_tac:
                    continue

                # Trích xuất năm để gợi ý thư mục năm scan
                nam = ""
                m = re.search(r"20[12]\d", ngay_hd + " " + so_hd)
                if m:
                    nam = m.group(0)

                rec = {
                    "loai": "thau_phu",
                    "loai_hien_thi": "Thầu phụ / Đội thi công",
                    "sheet": sname,
                    "so_hd": so_hd,
                    "cong_trinh": cong_trinh,
                    "ngay_hd": ngay_hd,
                    "noi_dung": noi_dung,
                    "doi_tac": doi_tac,
                    "gia_tri": gia_tri,
                    "phong_ql": phong_ql,
                    "nam": nam,
                    "goi_y_thu_muc": f"{config.DATA_HD_THAU_PHU}\\Năm {nam}" if nam else config.DATA_HD_THAU_PHU,
                }
                records.append(rec)
        wb.close()
    except Exception as e:
        print(f"[tra_cuu_hop_dong] Lỗi đọc file thầu phụ {p}: {e}")

    cache["mtime"] = cur_mtime
    cache["records"] = records
    return records


def _load_du_an(file_path: Path | None = None) -> list[dict]:
    p = file_path or FILE_INDEX_DU_AN
    if not p.is_file():
        return []
    try:
        cur_mtime = p.stat().st_mtime
    except Exception:
        cur_mtime = 0

    cache = _CACHE["du_an"]
    if cache["records"] and cache["mtime"] == cur_mtime:
        return cache["records"]

    import xlrd

    records = []
    try:
        wb = xlrd.open_workbook(p)
        for sname in wb.sheet_names():
            ws = wb.sheet_by_name(sname)
            header_idx = None
            col_map: dict[str, int] = {}

            for r in range(min(15, ws.nrows)):
                row_str = [_format_cell(ws.cell_value(r, c)).lower() for c in range(ws.ncols)]
                if any("hđ số" in c or "số hợp đồng" in c or "tên ct" in c or "công trình" in c for c in row_str):
                    header_idx = r
                    for col_idx, c in enumerate(row_str):
                        if "hđ số" in c or "số hợp đồng" in c or "số vb" in c:
                            col_map["so_hd"] = col_idx
                        elif "tên ct" in c or "công trình" in c or "dự án" in c:
                            col_map["cong_trinh"] = col_idx
                        elif "đối tác" in c or "chủ đầu tư" in c or "ban qlda" in c:
                            col_map["doi_tac"] = col_idx
                        elif "nội dung" in c:
                            col_map["noi_dung"] = col_idx
                        elif "ngày" in c and "tháng" in c:
                            col_map["ngay_hd"] = col_idx
                    break

            if header_idx is None:
                continue

            for r in range(header_idx + 1, ws.nrows):
                row_vals = [ws.cell_value(r, c) for c in range(ws.ncols)]
                so_hd = _format_cell(row_vals[col_map["so_hd"]]) if "so_hd" in col_map and col_map["so_hd"] < len(row_vals) else ""
                cong_trinh = _format_cell(row_vals[col_map["cong_trinh"]]) if "cong_trinh" in col_map and col_map["cong_trinh"] < len(row_vals) else ""
                doi_tac = _format_cell(row_vals[col_map["doi_tac"]]) if "doi_tac" in col_map and col_map["doi_tac"] < len(row_vals) else ""
                noi_dung = _format_cell(row_vals[col_map["noi_dung"]]) if "noi_dung" in col_map and col_map["noi_dung"] < len(row_vals) else ""
                ngay_hd = _format_cell(row_vals[col_map["ngay_hd"]]) if "ngay_hd" in col_map and col_map["ngay_hd"] < len(row_vals) else ""

                if not so_hd and not cong_trinh and not noi_dung:
                    continue

                nam = ""
                m = re.search(r"20[12]\d", ngay_hd + " " + so_hd + " " + sname)
                if m:
                    nam = m.group(0)

                rec = {
                    "loai": "du_an",
                    "loai_hien_thi": "HĐ Dự án / CĐT",
                    "sheet": sname,
                    "so_hd": so_hd,
                    "cong_trinh": cong_trinh,
                    "ngay_hd": ngay_hd,
                    "noi_dung": noi_dung,
                    "doi_tac": doi_tac,
                    "gia_tri": "",
                    "phong_ql": "Ban QLDA / CĐT",
                    "nam": nam,
                    "goi_y_thu_muc": f"{config.DATA_HD_DU_AN}\\{cong_trinh}" if cong_trinh else config.DATA_HD_DU_AN,
                }
                records.append(rec)
    except Exception as e:
        print(f"[tra_cuu_hop_dong] Lỗi đọc file dự án {p}: {e}")

    cache["mtime"] = cur_mtime
    cache["records"] = records
    return records


def tra_cuu_hop_dong(tu_khoa: str, loai: str = "all", limit: int = 50) -> dict[str, Any]:
    """Tìm kiếm hợp đồng theo từ khóa (tên đối tác, số HĐ, tên dự án, nội dung).

    Parameters:
    - tu_khoa: từ khóa cần tìm (không dấu hoặc có dấu)
    - loai: 'all' (tất cả), 'thau_phu' (thầu phụ & đội thi công), 'du_an' (dự án / CĐT)
    - limit: số lượng bản ghi tối đa trả về

    Returns:
    - dict gồm status, total, query, items
    """
    tu_khoa_clean = tu_khoa.strip()
    tu_khoa_kd = _bo_dau(tu_khoa_clean)
    words = [w for w in tu_khoa_kd.split() if w]

    items: list[dict] = []
    all_recs: list[dict] = []

    if loai in ("all", "thau_phu"):
        all_recs.extend(_load_thau_phu())
    if loai in ("all", "du_an"):
        all_recs.extend(_load_du_an())

    for r in all_recs:
        full_text = f"{r['so_hd']} {r['cong_trinh']} {r['doi_tac']} {r['noi_dung']} {r['sheet']} {r['nam']}"
        full_text_kd = _bo_dau(full_text)

        # Kiểm tra nếu mọi từ trong từ khóa đều xuất hiện
        if not words or all(w in full_text_kd for w in words):
            items.append(r)
            if len(items) >= limit:
                break

    return {
        "ok": True,
        "query": tu_khoa,
        "loai": loai,
        "total_matched": len(items),
        "items": items,
        "thong_bao": (
            f"Tìm thấy {len(items)} hợp đồng khớp từ khóa '{tu_khoa}'. "
            "Để mở file scan gốc, vui lòng truy cập đúng thư mục trong 'goi_y_thu_muc', TUYỆT ĐỐI không quét cây thư mục."
        ),
    }


if __name__ == "__main__":
    import json
    import sys

    q = sys.argv[1] if len(sys.argv) > 1 else "Ninh Cơ"
    res = tra_cuu_hop_dong(q, limit=5)
    print(json.dumps(res, indent=2, ensure_ascii=False))
