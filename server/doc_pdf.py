"""Kuro mở sẵn PDF người dùng gửi (thả vào khung chat hoặc dán đường dẫn) để AI nào cũng bóc được khối lượng.

Vì sao làm ở máy chủ: codex chỉ đọc tệp bằng lệnh shell, tắt Bash là không đọc được PDF. Bản vẽ CAD xuất PDF
thì số kích thước và bảng thống kê thường là nét chữ SHX, không trích ra chữ được, nên ngoài phần chữ còn xuất
ảnh PNG từng trang (144 dpi, đọc rõ số 2.5 mm trên khổ A3) để AI xem. Chữ font TCVN3 ("mÆt c¾t") đổi sang Unicode.
"""
import hashlib
import re
from pathlib import Path

import workspace_rules

# Bảng TCVN3 (ABC) -> Unicode, lấy từ goi/texthub/.../charsets.csv (bộ chữ thường, không tính font chữ hoa "H")
_TCVN3 = str.maketrans(
    "¡¢£¤¥¦§¨©ª«¬\xad®µ¶·¸¹»¼½¾ÆÇÈÉÊËÌÎÏÐÑÒÓÔÕÖ×ØÜÝÞßáâãäåæçèéêëìíîïñòóôõö÷øùúûüýþ",
    "ĂÂÊÔƠƯĐăâêôơưđàảãáạằẳẵắặầẩẫấậèẻẽéẹềểễếệìỉĩíịòỏõóọồổỗốộờởỡớợùủũúụừửữứựỳỷỹýỵ")
# Đường dẫn ổ đĩa hoặc UNC kết thúc .pdf; tìm chồng lấn để "C:\x và D:\y.pdf" vẫn bắt được D:\y.pdf
_PDF = re.compile(r'(?=((?:[A-Za-z]:\\|\\\\)[^"\n<>|*?\[\]]*?\.pdf)(?![\w.]))', re.I)
SCALE = 2           # 72 dpi x 2
MAX_TRANG = 150
MAX_CHU = 20_000    # chữ đưa thẳng vào câu hỏi; bản đủ nằm trong chu.txt
MAX_PDF = 3
DPI_PHONG = 300     # phóng to một vùng: số 1.8 mm trên A1 vẫn rõ
MAX_PX = 2000       # cạnh dài ảnh phóng to


# Nhận TCVN3 theo TÊN FONT của từng ký tự (VnAvantH, .VnTime, ABCDEF+VnArialNarrowH...), không đoán theo chữ: đoán
# theo chữ từng làm hỏng Unicode chuẩn ("CÔNG" -> "CỄNG") vì Ô, Ì, Ý cũng là mã TCVN3. Font đuôi H là bộ chữ hoa.
_FONT_TCVN3 = re.compile(r"^(?:[A-Z]{6}\+)?\.?Vn", re.I)
_KIEU = re.compile(r"(Bold|Italic|Oblique|Medium|Light|Black|Narrow|Condensed|Regular|MT|PS|[-,])+$", re.I)


def la_tcvn3(font: str) -> bool:
    return bool(_FONT_TCVN3.match(font or ""))


def doi_ky_tu(c: str, font: str) -> str:
    """Một ký tự đọc từ PDF: đổi sang Unicode nếu nằm trong font TCVN3, giữ nguyên nếu font Unicode."""
    if not la_tcvn3(font):
        return c
    if c == "￾":    # pdfium báo mã 0xAD (chữ "ư" của TCVN3) như gạch nối mềm
        c = "\xad"
    c = c.translate(_TCVN3)
    return c.upper() if _KIEU.sub("", font.split("+")[-1]).endswith("H") else c


def _chu_trang(trang) -> list[str]:
    """Các dòng chữ của một trang, ký tự font TCVN3 đã đổi sang Unicode."""
    import ctypes
    import pypdfium2.raw as raw
    tp = trang.get_textpage()
    buf, co = ctypes.create_string_buffer(128), ctypes.c_int()
    out = []
    for i in range(tp.count_chars()):
        c = chr(raw.FPDFText_GetUnicode(tp.raw, i))
        dai = raw.FPDFText_GetFontInfo(tp.raw, i, buf, 128, ctypes.byref(co))
        out.append(doi_ky_tu(c, buf.value.decode("latin-1") if dai else ""))
    return [d.strip() for d in "".join(out).splitlines() if d.strip()]


def tim_pdf(text: str) -> list[Path]:
    out = []
    for m in _PDF.finditer(text or ""):
        p = Path(m.group(1).strip())
        if p not in out and p.is_file():
            out.append(p)
    return out[:MAX_PDF]


def thu_muc(p: Path, ws_dir) -> Path:
    """Thư mục ảnh của một PDF trong dự án; cùng tệp, cùng ngày sửa thì dùng lại."""
    st = p.stat()
    key = hashlib.sha1(f"{p.resolve()}|{st.st_size}|{st.st_mtime_ns}".encode()).hexdigest()[:10]
    out = workspace_rules.attachments_dir(Path(ws_dir)) / f"pdf_{key}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def _vung(vung) -> tuple[float, float, float, float]:
    """'x0,y0,x1,y1' tính từ góc TRÊN-TRÁI theo tỉ lệ 0-1 của trang (hoặc %, vd 50,60,100,100)."""
    so = [float(v) for v in (re.split(r"[,;\s]+", vung.strip()) if isinstance(vung, str) else vung) if str(v) != ""]
    if len(so) != 4:
        raise ValueError("vung phải có 4 số x0,y0,x1,y1 (tỉ lệ 0-1 tính từ góc trên-trái trang)")
    if max(so) > 1:
        so = [v / 100 for v in so]
    x0, y0, x1, y1 = (min(max(v, 0.0), 1.0) for v in so)
    x0, x1, y0, y1 = min(x0, x1), max(x0, x1), min(y0, y1), max(y0, y1)
    if x1 - x0 < 0.01 or y1 - y0 < 0.01:
        raise ValueError("vung quá nhỏ (cần rộng/cao tối thiểu 1% trang)")
    return x0, y0, x1, y1


def phong_to(pdf_path: str, trang: int, vung, dpi: int, ws_dir) -> str:
    """Xuất PNG một vùng của trang ở độ phân giải cao để đọc số nhỏ; trả lời cho AI kèm đường dẫn ảnh."""
    import pypdfium2 as pdfium
    p = Path(str(pdf_path).strip().strip('"'))
    if p.suffix.lower() != ".pdf" or not p.is_file():
        raise ValueError(f"không thấy tệp PDF '{pdf_path}'")
    x0, y0, x1, y1 = _vung(vung)
    pdf = pdfium.PdfDocument(str(p))
    try:
        n = len(pdf)
        if not 1 <= int(trang) <= n:
            raise ValueError(f"trang {trang} không có, PDF có {n} trang")
        pg = pdf[int(trang) - 1]
        w, h = pg.get_size()   # điểm (1/72 inch), đã tính xoay trang
        scale = min(max(int(dpi or DPI_PHONG), 72), 600) / 72
        scale = min(scale, MAX_PX / max((x1 - x0) * w, (y1 - y0) * h))   # chặn ảnh quá lớn: tốn token mà AI cũng thu nhỏ lại
        out = thu_muc(p, ws_dir) / f"vung_t{int(trang):03d}_{x0:.2f}-{y0:.2f}-{x1:.2f}-{y1:.2f}_{round(scale * 72)}.png"
        if not out.is_file():
            # crop của pdfium tính theo điểm, cắt từ mép trái, dưới, phải, trên của trang đã xoay
            anh = pg.render(scale=scale, crop=(x0 * w, (1 - y1) * h, (1 - x1) * w, y0 * h)).to_pil()
            tam = out.with_suffix(".tmp")
            anh.save(tam, format="PNG")
            tam.replace(out)
    finally:
        pdf.close()
    return (f"Ảnh phóng to trang {trang}, vùng {x0:.2f},{y0:.2f} -> {x1:.2f},{y1:.2f} ({round(scale * 72)} dpi): {out}\n"
            "Mở ảnh này bằng công cụ xem ảnh (Claude: Read; Codex: view_image) rồi đọc số.")


def doc(p: Path, ws_dir) -> str:
    import pypdfium2 as pdfium   # đi kèm pdfplumber; nạp muộn để Kuro vẫn chạy khi máy chưa cài
    out = thu_muc(p, ws_dir)
    pdf = pdfium.PdfDocument(str(p))
    try:
        n = len(pdf)
        m = min(n, MAX_TRANG)
        trang_chu = []
        for i in range(m):
            trang = pdf[i]
            anh = out / f"trang_{i + 1:03d}.png"
            if not anh.is_file():    # cùng tệp, cùng ngày sửa thì dùng lại ảnh đã xuất
                tam = anh.with_suffix(".tmp")
                trang.render(scale=SCALE).to_pil().save(tam, format="PNG")
                tam.replace(anh)
            trang_chu.append(_chu_trang(trang))
    finally:
        pdf.close()
    toan_bo = gop_trang(trang_chu)
    (out / "chu.txt").write_text(toan_bo, encoding="utf-8")
    cat = toan_bo[:MAX_CHU] + (f"\n... (còn nữa, xem {out / 'chu.txt'})" if len(toan_bo) > MAX_CHU else "")
    thieu = f" Chỉ xuất {m}/{n} trang đầu." if m < n else ""
    return (f"\n\n[Kuro đã mở sẵn PDF: {p} - {n} trang]\n"
            f"- Ảnh từng trang (PNG 144 dpi): {out}\\trang_001.png ... trang_{m:03d}.png.{thieu}\n"
            "- Số kích thước, bảng thống kê trên bản vẽ CAD thường là nét vẽ nên KHÔNG có trong phần chữ dưới đây: "
            "muốn bóc khối lượng phải mở ẢNH trang đó và đọc số trên ảnh, không đoán. Mở ảnh thẳng bằng công cụ xem "
            "ảnh (Claude: Read; Codex: view_image), không cần liệt kê danh sách công cụ. Chỉ mở trang cần cho việc "
            "đang làm (mỗi ảnh ~4k token). Ghi rõ số trang và tên hình chiếu cho mỗi con số.\n"
            "- Số nhỏ, mờ, bảng thống kê dày chữ: gọi công cụ phong_to_pdf (pdf, trang, vung = x0,y0,x1,y1 tỉ lệ 0-1 "
            "từ góc trên-trái) để có ảnh 300 dpi đúng vùng đó, không đoán số.\n"
            "- Bóc xong mỗi bảng khối lượng: gọi luu_khoi_luong để ghi ra Excel trong dự án (không mất số khi nén "
            "ngữ cảnh hay đổi AI), báo đường dẫn tệp cho người dùng.\n"
            f"- Chữ trích được (TCVN3 đã đổi sang Unicode):\n{cat}")


def gop_trang(trang_chu: list[list[str]]) -> str:
    """Ghép chữ các trang; dòng lặp ở nhiều trang (khung tên, ô ký) chỉ ghi một lần ở đầu: bản vẽ 59 trang giảm 59%."""
    import collections
    dem = collections.Counter(d for t in trang_chu for d in set(t))
    lap = [d for d, c in dem.items() if c >= max(3, len(trang_chu) * 0.3)]
    bo = set(lap)
    phan = [f"--- Lặp lại ở nhiều trang (khung tên, ghi chú chung) ---\n" + "\n".join(lap)] if lap else []
    phan += [f"--- Trang {i + 1} ---\n" + "\n".join(d for d in t if d not in bo) for i, t in enumerate(trang_chu)]
    return "\n".join(phan)


def khoi(text: str, ws_dir) -> str:
    """Phần nối thêm vào câu hỏi gửi AI cho mọi PDF có trong tin nhắn; không có PDF thì chuỗi rỗng."""
    ra = []
    for p in tim_pdf(text):
        try:
            ra.append(doc(p, ws_dir))
        except ImportError:
            ra.append(f"\n\n[Kuro chưa mở được PDF {p}: máy thiếu thư viện pypdfium2, chạy setup.bat để cài]")
        except Exception as e:   # PDF hỏng/có mật khẩu: báo cho AI biết, không làm hỏng cả lượt chat
            ra.append(f"\n\n[Kuro không mở được PDF {p}: {e}]")
    return "".join(ra)
