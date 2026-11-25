# -*- coding: utf-8 -*-
"""MCP stdio cho LibreCAD (LibreCAD khong co MCP rieng): boc librecad_cli.py thanh 3 tool.

Giao thuc MCP toi thieu, tu viet (JSON-RPC moi dong): initialize, tools/list, tools/call, ping. Khong can thu vien ngoai.
Tool: librecad_status, librecad_convert(tep, to, out_dir, size), librecad_open(tep).
"""
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TOOLS = [
    {"name": "librecad_status", "description": "LibreCAD đã cài chưa (đường dẫn, phiên bản).",
     "inputSchema": {"type": "object", "properties": {}}},
    {"name": "librecad_convert", "description": "Đổi bản vẽ DXF/DWG sang PDF, PNG hoặc SVG bằng LibreCAD. Lưu kết quả vào thư mục dự án, không ghi vào kho mạng công ty.",
     "inputSchema": {"type": "object", "required": ["tep"], "properties": {
         "tep": {"type": "string", "description": "Đường dẫn tệp .dxf hoặc .dwg"},
         "to": {"type": "string", "enum": ["pdf", "png", "svg"], "default": "pdf"},
         "out_dir": {"type": "string", "description": "Thư mục lưu kết quả (mặc định cạnh tệp nguồn)"},
         "size": {"type": "string", "description": "Chỉ PNG: WxH điểm ảnh, vd 3000x2000"}}}},
    {"name": "librecad_open", "description": "Mở tệp DXF/DWG trong LibreCAD cho người dùng xem.",
     "inputSchema": {"type": "object", "required": ["tep"], "properties": {"tep": {"type": "string"}}}},
]


def chay(args):
    r = subprocess.run([sys.executable, "-X", "utf8", str(HERE / args[0]), *args[1:]], capture_output=True, text=True,
                       encoding="utf-8", errors="replace", timeout=150)
    return r.stdout.strip() or r.stderr.strip() or f"mã thoát {r.returncode}", r.returncode != 0


def goi_tool(name, a):
    if name == "librecad_status":
        return chay(["librecad_setup.py", "status"])
    if name == "librecad_convert":
        cmd = ["librecad_cli.py", "convert", a["tep"], "--to", a.get("to", "pdf")]
        if a.get("out_dir"):
            cmd += ["--out", a["out_dir"]]
        if a.get("size"):
            cmd += ["--size", a["size"]]
        return chay(cmd)
    if name == "librecad_open":
        return chay(["librecad_cli.py", "open", a["tep"]])
    return f"Tool không có: {name}", True


def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            m = json.loads(line)
        except ValueError:
            continue
        mid, method = m.get("id"), m.get("method")
        if mid is None:
            continue   # notification (vd notifications/initialized): khong tra loi
        if method == "initialize":
            res = {"protocolVersion": (m.get("params") or {}).get("protocolVersion", "2024-11-05"),
                   "capabilities": {"tools": {}}, "serverInfo": {"name": "librecad", "version": "1.0.0"}}
        elif method == "tools/list":
            res = {"tools": TOOLS}
        elif method == "tools/call":
            p = m.get("params") or {}
            try:
                text, loi = goi_tool(p.get("name"), p.get("arguments") or {})
            except Exception as e:  # noqa: BLE001
                text, loi = f"Lỗi: {e}", True
            res = {"content": [{"type": "text", "text": text}], "isError": loi}
        elif method == "ping":
            res = {}
        else:
            sys.stdout.write(json.dumps({"jsonrpc": "2.0", "id": mid, "error": {"code": -32601, "message": f"Không hỗ trợ: {method}"}}) + "\n")
            sys.stdout.flush()
            continue
        sys.stdout.write(json.dumps({"jsonrpc": "2.0", "id": mid, "result": res}, ensure_ascii=False) + "\n")
        sys.stdout.flush()


if __name__ == "__main__":
    main()
