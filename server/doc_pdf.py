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


_MA = {chr(k) for k in _TCVN3}


def _doi_tu(m) -> str:
    """Đổi một từ khi ký tự TCVN3 nằm sát chữ cái Latin ("chøc"); "ø20", "300×300" và từ Unicode giữ nguyên.
    Font TCVN3 chữ hoa (.VnTimeH) dùng chung mã với chữ thường, nên từ toàn chữ hoa thì viết hoa lại."""
    w = m.group(0)
    if any(ord(c) > 0xFF for c in w):
        return w
    sat_chu = lambda j: 0 <= j < len(w) and w[j].isascii() and w[j].isalpha()
    toan_ma = len(w) >= 2 and all(c in _MA for c in w)        # "§¸" = "Đá"
    if not toan_ma and not any(c in _MA and (sat_chu(i - 1) or sat_chu(i + 1)) for i, c in enumerate(w)):
        return w
    v = w.translate(_TCVN3)
    latin = [c for c in w if c.isascii() and c.isalpha()]
    return v.upper() if len(latin) >= 2 and all(c.isupper() for c in latin) else v


def doi_tcvn3(dong: str) -> str:
    # pdfium trả mã 0xAD (chữ "ư" của TCVN3) thành U+FFFE như dấu gạch nối mềm cuối dòng và nuốt dấu xuống dòng
    return re.sub(r"\S+", _doi_tu, dong.replace("￾", "\xad "))


def tim_pdf(text: str) -> list[Path]:
    out = []
    for m in _PDF.finditer(text or ""):
        p = Path(m.group(1).strip())
        if p not in out and p.is_file():
            out.append(p)
    return out[:MAX_PDF]


def doc(p: Path, ws_dir) -> str:
    import pypdfium2 as pdfium   # đi kèm pdfplumber; nạp muộn để Kuro vẫn chạy khi máy chưa cài
    st = p.stat()
    key = hashlib.sha1(f"{p.resolve()}|{st.st_size}|{st.st_mtime_ns}".encode()).hexdigest()[:10]
    out = workspace_rules.attachments_dir(Path(ws_dir)) / f"pdf_{key}"
    out.mkdir(parents=True, exist_ok=True)
    pdf = pdfium.PdfDocument(str(p))
    try:
        n = len(pdf)
        m = min(n, MAX_TRANG)
        chu = []
        for i in range(m):
            trang = pdf[i]
            anh = out / f"trang_{i + 1:03d}.png"
            if not anh.is_file():    # cùng tệp, cùng ngày sửa thì dùng lại ảnh đã xuất
                tam = anh.with_suffix(".tmp")
                trang.render(scale=SCALE).to_pil().save(tam, format="PNG")
                tam.replace(anh)
            dong = (doi_tcvn3(d) for d in trang.get_textpage().get_text_range().splitlines())
            chu.append(f"--- Trang {i + 1} ---\n" + "\n".join(d for d in dong if d.strip()))
    finally:
        pdf.close()
    toan_bo = "\n".join(chu)
    (out / "chu.txt").write_text(toan_bo, encoding="utf-8")
    cat = toan_bo[:MAX_CHU] + (f"\n... (còn nữa, xem {out / 'chu.txt'})" if len(toan_bo) > MAX_CHU else "")
    thieu = f" Chỉ xuất {m}/{n} trang đầu." if m < n else ""
    return (f"\n\n[Kuro đã mở sẵn PDF: {p} - {n} trang]\n"
            f"- Ảnh từng trang (PNG 144 dpi): {out}\\trang_001.png ... trang_{m:03d}.png.{thieu}\n"
            "- Số kích thước, bảng thống kê trên bản vẽ CAD thường là nét vẽ nên KHÔNG có trong phần chữ dưới đây: "
            "muốn bóc khối lượng phải mở ẢNH trang đó (công cụ xem ảnh/Read) và đọc số trên ảnh, không đoán. "
            "Ghi rõ số trang và tên hình chiếu cho mỗi con số.\n"
            f"- Chữ trích được (TCVN3 đã đổi sang Unicode):\n{cat}")


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
