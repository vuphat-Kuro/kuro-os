"""Tool tinh_python: tính toán bằng code thật thay vì để model tự nhẩm.

Chạy đoạn Python trong tiến trình riêng của venv Kuro (có sẵn thư viện kỹ thuật trong
requirements-ky-thuat.txt). Mỗi lần chạy lưu script vào brain/tinh-toan/ để soát lại về sau.
"""
import asyncio
import os
import subprocess
import sys
from datetime import datetime

from claude_agent_sdk import create_sdk_mcp_server, tool

import config

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


SERVER = create_sdk_mcp_server("kuro", tools=[tinh_python])
