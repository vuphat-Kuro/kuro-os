"""Tool tinh_python: tính toán bằng code thật thay vì để model tự nhẩm.

Chạy đoạn Python trong tiến trình riêng của venv Kuro (có sẵn thư viện kỹ thuật trong
requirements-ky-thuat.txt). Mỗi lần chạy lưu script vào brain/tinh-toan/ để soát lại về sau.
"""
import asyncio
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from claude_agent_sdk import create_sdk_mcp_server, tool

import config
import kho

TIMEOUT_S = 120
OUT_MAX = 20_000

DESC = (
    "Chạy Python để TÍNH TOÁN chính xác, dùng cho MỌI con số kỹ thuật (không tự nhẩm). Có sẵn: pint (đơn vị), "
    "numpy, scipy, pandas, sectionproperties (đặc trưng tiết diện), concreteproperties (tiết diện BTCT), "
    "PyNiteFEA (phân tích khung), shapely, ezdxf, openpyxl, python-docx, pdfplumber, ifcopenshell. "
    "In kết quả bằng print(), kèm đơn vị. Thư mục làm việc là brain/tinh-toan/. Giới hạn 120 giây."
)


def run_python(code: str, muc_dich: str = "") -> str:
    d = config.BRAIN / "tinh-toan"
    d.mkdir(parents=True, exist_ok=True)
    f = d / f"{datetime.now():%Y%m%d-%H%M%S-%f}.py"
    f.write_text((f"# {muc_dich}\n" if muc_dich else "") + code, encoding="utf-8")
    try:
        # -I: không nạp module lạ từ thư mục làm việc; -X utf8: in tiếng Việt không lỗi mã; CREATE_NO_WINDOW: không nháy console
        no_win = getattr(subprocess, "CREATE_NO_WINDOW", 0)
        r = subprocess.run([sys.executable, "-I", "-X", "utf8", str(f)], cwd=d, capture_output=True,
                           text=True, encoding="utf-8", errors="replace", timeout=TIMEOUT_S,
                           creationflags=no_win,
                           env={**os.environ, "MPLBACKEND": "Agg"})
        status = "OK" if r.returncode == 0 else f"LỖI exit={r.returncode}"
        out = r.stdout + (f"\n[stderr]\n{r.stderr}" if r.stderr.strip() else "")
    except subprocess.TimeoutExpired:
        status, out = f"QUÁ {TIMEOUT_S} GIÂY, đã dừng", ""
    if len(out) > OUT_MAX:
        out = "...(cắt bớt phần đầu)\n" + out[-OUT_MAX:]
    return f"[{status}] script lưu tại tinh-toan/{f.name}\n{out}"


@tool("tinh_python", DESC, {"code": str, "muc_dich": str})
async def tinh_python(args):
    text = await asyncio.to_thread(run_python, args["code"], args.get("muc_dich", ""))
    return {"content": [{"type": "text", "text": text}]}


def _text(t: str) -> dict:
    return {"content": [{"type": "text", "text": t}]}


# Kho skill (specs/002): 230 skill từ GitHub KHÔNG nạp vào lời nhắc; AI tự tìm, đọc, chạy mã đã duyệt.
@tool("tim_skill", "Tìm skill trong KHO (DDC xây dựng: BIM, IFC, bóc khối lượng, dự toán, tiến độ, an toàn, hợp đồng, "
      "hồ sơ; archify vẽ sơ đồ; anatomy hình minh hoạ; graphify; spec-kit) khi skill sẵn có của Kuro không phủ việc. "
      "Mô tả kho bằng tiếng Anh: truyền TỪ KHOÁ TIẾNG ANH, vd 'ifc quantity takeoff concrete'.",
      {"tu_khoa": str})
async def tim_skill(args):
    kq = kho.tim(args["tu_khoa"])
    return _text(json.dumps(kq, ensure_ascii=False) if kq else "Không có skill phù hợp trong kho.")


@tool("doc_skill", "Đọc hướng dẫn của một skill trong kho (mặc định SKILL.md, hoặc tệp kèm theo đường dẫn tương đối).",
      {"skill": str, "tep": str})
async def doc_skill(args):
    try:
        return _text(kho.doc(args["skill"], args.get("tep") or "SKILL.md"))
    except ValueError as e:
        return _text(f"[LỖI] {e}")


@tool("chay_ma_kho", "Chạy một script .py/.mjs/.js của skill trong kho, CHỈ khi mã skill đã được duyệt. Thư mục làm "
      "việc là dự án đang mở. doi_so là danh sách tham số dòng lệnh.", {"skill": str, "tep": str, "doi_so": list})
async def chay_ma_kho(args):
    import engine   # nhập muộn: engine nhập calc
    try:
        cwd = engine.active_workspace_dir()
        text = await asyncio.to_thread(kho.chay, args["skill"], args["tep"], args.get("doi_so") or [], cwd)
    except ValueError as e:
        text = f"[LỖI] {e}"
    return _text(text)


@tool("dien_hoa", "Diễn hoạ ảnh thật từ bản vẽ nét, ảnh chụp hiện trạng hoặc ảnh mô hình 3D/BIM (ComfyUI + RealVisXL "
      "+ ControlNet Union SDXL chạy trên máy, không gửi bản vẽ ra ngoài). anh: đường dẫn ảnh (tuyệt đối hoặc trong dự án "
      "đang mở); mo_ta: công trình, vật liệu, cảnh quan, ánh sáng (tiếng Việt được); che_do: net | anh | 3d. Ra 2 phương "
      "án trong <dự án>/dien-hoa/. Mất 1-3 phút.", {"anh": str, "mo_ta": str, "che_do": str})
async def dien_hoa_tool(args):
    import engine   # nhập muộn: engine nhập calc
    ws = engine.active_workspace_dir()
    anh = Path(args["anh"]) if Path(args["anh"]).is_absolute() else ws / args["anh"]
    try:
        ra = await engine.dien_hoa_anh(anh, args.get("mo_ta", ""), args.get("che_do") or "net", str(ws))
        return _text("Đã diễn hoạ, chèn ảnh vào câu trả lời bằng markdown:\n" +
                     "\n".join(f"![Phương án {i}](/api/attachments/{p.name})  ({p})" for i, p in enumerate(ra, 1)))
    except Exception as e:
        return _text(f"[LỖI] {e}")


@tool("goi_tien_ich", "Gói tiện ích tùy chọn của Kuro (vd 'autocad': quy tắc vẽ và xuất DXF chuẩn PKTTC). CHỈ gọi khi người "
      "dùng YÊU CẦU RÕ cài, gỡ hoặc xem gói; không tự cài. hanh_dong: list | cai | go; id: mã gói (bỏ trống với list).",
      {"hanh_dong": str, "id": str})
async def goi_tien_ich(args):
    import goi
    try:
        text = await asyncio.to_thread(goi.chay, args["hanh_dong"], args.get("id") or "")
    except ValueError as e:
        text = f"[LỖI] {e}"
    return _text(text)


DESC_PHONG_TO = ("Phóng to MỘT VÙNG của trang PDF (bản vẽ) thành ảnh PNG độ phân giải cao (mặc định 300 dpi) để đọc số "
                 "kích thước nhỏ, bảng thống kê thép/khối lượng. pdf: đường dẫn tệp PDF; trang: số trang (từ 1); vung: "
                 "'x0,y0,x1,y1' tỉ lệ 0-1 tính từ góc TRÊN-TRÁI trang (vd góc dưới phải: '0.6,0.6,1,1'); dpi: tùy chọn. "
                 "Trả về đường dẫn ảnh, mở ảnh để đọc.")
DESC_LUU_KL = ("Lưu MỘT bảng khối lượng đã bóc vào sổ BOC_KHOI_LUONG.xlsx của dự án đang mở (mỗi hạng mục một sheet, "
               "lưu lại cùng ten thì thay bảng cũ) kèm bản .md để đọc lại. Gọi ngay khi bóc xong mỗi bảng. ten: tên hạng "
               "mục/cấu kiện; bang: danh sách dòng, dòng đầu là tiêu đề cột (vd STT, Cấu kiện, Đơn vị, Khối lượng, Diễn "
               "giải, Nguồn), số để dạng số; nguon: tệp bản vẽ + trang + hình chiếu; ghi_chu: giả định, chỗ cần xác minh.")


def _ws():
    import engine   # nhập muộn: engine nhập calc
    return engine.active_workspace_dir()


@tool("phong_to_pdf", DESC_PHONG_TO, {"pdf": str, "trang": int, "vung": str, "dpi": int})
async def phong_to_pdf(args):
    import doc_pdf
    try:
        text = await asyncio.to_thread(doc_pdf.phong_to, args["pdf"], args["trang"], args["vung"],
                                       args.get("dpi") or doc_pdf.DPI_PHONG, _ws())
    except Exception as e:   # PDF hỏng, sai trang, sai vùng: báo cho AI sửa lời gọi
        text = f"[LỖI] {e}"
    return _text(text)


@tool("luu_khoi_luong", DESC_LUU_KL, {"ten": str, "bang": list, "nguon": str, "ghi_chu": str})
async def luu_khoi_luong(args):
    import khoi_luong
    try:
        text = await asyncio.to_thread(khoi_luong.luu, args["ten"], args["bang"], args.get("nguon", ""), _ws(),
                                       args.get("ghi_chu", ""))
    except ValueError as e:
        text = f"[LỖI] {e}"
    return _text(text)


KHO_TOOLS = ["mcp__kuro__tim_skill", "mcp__kuro__doc_skill", "mcp__kuro__chay_ma_kho", "mcp__kuro__dien_hoa",
             "mcp__kuro__goi_tien_ich", "mcp__kuro__phong_to_pdf", "mcp__kuro__luu_khoi_luong"]
SERVER = create_sdk_mcp_server("kuro", tools=[tinh_python, tim_skill, doc_skill, chay_ma_kho, dien_hoa_tool, goi_tien_ich,
                                              phong_to_pdf, luu_khoi_luong])
