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
        # -I: không nạp module lạ từ thư mục làm việc; -X utf8: in tiếng Việt không lỗi mã
        r = subprocess.run([sys.executable, "-I", "-X", "utf8", str(f)], cwd=d, capture_output=True,
                           text=True, encoding="utf-8", errors="replace", timeout=TIMEOUT_S,
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


KHO_TOOLS = ["mcp__kuro__tim_skill", "mcp__kuro__doc_skill", "mcp__kuro__chay_ma_kho"]
SERVER = create_sdk_mcp_server("kuro", tools=[tinh_python, tim_skill, doc_skill, chay_ma_kho])
