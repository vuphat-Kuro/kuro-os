# -*- coding: utf-8 -*-
"""May chu MCP (stdio) cho PKTTC TextHub: tro ly goi cong cua AutoCAD qua cac cong cu pkttc_*.
Khong can thu vien ngoai. Dang ky vao tro ly (vi du Kuro) nhu mot may chu MCP lenh:
    {"mcpServers": {"pkttc-text": {"command": "python", "args": ["<duong dan>/pkttc_mcp.py"]}}}
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pkttc_client import BridgeError, Client, find_bridges  # noqa: E402

SERVER_INFO = {"name": "pkttc-text", "version": "0.5.0"}
INSTRUCTIONS = (
    "Dieu khien plugin PKTTC TextHub trong AutoCAD (doi bang ma chu tieng Viet TCVN3/VNI sang Unicode, quan ly font va style). "
    "Dieu kien: nguoi dung phai go lenh PKTEXTBRIDGE trong AutoCAD de mo cong. "
    "Quy trinh: pkttc_ping, pkttc_scan (xem tong quan), pkttc_plan_create (lap ke hoach, KHONG sua ban ve), cho nguoi dung xem ke hoach, "
    "roi pkttc_plan_apply. Moi cong cu *_apply se XIN PHEP NGUOI DUNG trong AutoCAD (hop thoai Yes/No; o che do chan thi go YES tren dong lenh); ban khong the tu phe duyet. "
    "Cuoc goi doi den khi nguoi dung tra loi: ket qua status = applied | rejected | failed | nothing. Neu rejected thi dung lai va hoi nguoi dung, "
    "khong thu lai tu dong. Ban sao luu va nhat ky duoc tao truoc moi lan ghi; nguoi dung hoan tac bang lenh U trong AutoCAD. "
    "Khong gui noi dung chu de ghi: chi gui planId."
)

# ten cong cu -> (phuong thuc, mo ta, schema tham so, la thao tac ghi)
TOOLS = {
    "pkttc_ping": ("ping", "Kiem tra ket noi: tra ve phien ban AutoCAD, ban ve dang mo, cac ke hoach dang cho.", {}, False),
    "pkttc_scan": ("scan", "Quet chi doc moi loai chu (TEXT, MTEXT, ATTRIB, ATTDEF, MLEADER, DIMENSION, o bang) va tong hop theo loai, bang ma, co hieu, style.", {
        "items": {"type": "string", "enum": ["none", "flagged", "all"], "description": "none = chi tong hop; flagged = them cac muc co co hieu hoac khong phai ASCII; all = tat ca"},
        "offset": {"type": "integer", "minimum": 0}, "limit": {"type": "integer", "minimum": 1, "maximum": 500}}, False),
    "pkttc_fonts": ("fonts", "Bao cao font (style, bigfont, ma \\f trong MTEXT) doi chieu voi may va kho font cua phong; goi y thay the. Chi doc.", {}, False),
    "pkttc_plan_create": ("plan.create", "Lap ke hoach doi chu TCVN3/VNI sang Unicode. KHONG sua ban ve. Tra ve planId, so muc, ly do bo qua, mau 10 muc.", {
        "targetFont": {"type": "string", "description": "Font dich cho chu co font nguon TrueType, mac dinh Arial Unicode MS (Arial thuong khong ve du chu Viet tren AutoCAD 2020)"},
        "targetShxFont": {"type": "string", "description": "Font dich cho chu co font nguon SHX, mac dinh uv-abc.shx (phai la SHX Unicode)"},
        "fontMap": {"type": "object", "additionalProperties": {"type": "string"}, "description": "Font nguon -> font dich cho tung loai font nguon, vi du {\".VnAvantH\": \"Segoe UI\", \"vn-abc.shx\": \"VN_UNI.shx\"}. Font nguon khong co trong bang dung targetFont. Font dich SHX phai la SHX Unicode (header unifont)."},
        "targetStyle": {"type": "string", "description": "De trong = dat theo ten font (khong tien to); tranh trung ten bang hau to _2"},
        "keepWidth": {"type": "boolean", "description": "Giu do rong chu (mac dinh true)"},
        "includeLocked": {"type": "boolean", "description": "Co doi ca muc tren layer khoa (mac dinh false)"}}, False),
    "pkttc_plan_get": ("plan.get", "Xem cac muc cua mot ke hoach (phan trang). Chi doc.", {
        "planId": {"type": "string"}, "offset": {"type": "integer", "minimum": 0}, "limit": {"type": "integer", "minimum": 1, "maximum": 200}}, False),
    "pkttc_plan_apply": ("plan.apply", "AP DUNG ke hoach len ban ve. XIN PHEP NGUOI DUNG trong AutoCAD (Yes/No) (cuoc goi doi). Sao luu truoc, mot giao dich, hoan tac bang U.", {
        "planId": {"type": "string"}, "note": {"type": "string", "description": "Ghi chu ngan hien cho nguoi dung khi xin phep"}}, True),
    "pkttc_fontsub_plan": ("fontsub.plan", "Lap ke hoach thay font cua Style bi thieu bang font da co san tren may. Chi doc.", {}, False),
    "pkttc_fontsub_apply": ("fontsub.apply", "AP DUNG thay font Style. XIN PHEP NGUOI DUNG trong AutoCAD (Yes/No).", {
        "planId": {"type": "string"}, "note": {"type": "string"}}, True),
    "pkttc_purge_plan": ("purge.plan", "Liet ke Style chu khong con dung (co the don). Chi doc.", {}, False),
    "pkttc_purge_apply": ("purge.apply", "AP DUNG don Style khong dung. XIN PHEP NGUOI DUNG trong AutoCAD (Yes/No).", {
        "planId": {"type": "string"}, "note": {"type": "string"}}, True),
    "pkttc_shutdown": ("shutdown", "Dong cong (tra AutoCAD lai cho nguoi dung).", {}, False),
}
REQUIRED = {"pkttc_plan_get": ["planId"], "pkttc_plan_apply": ["planId"], "pkttc_fontsub_apply": ["planId"], "pkttc_purge_apply": ["planId"]}


def tools_list():
    out = []
    for name, (_m, desc, props, _w) in TOOLS.items():
        schema = {"type": "object", "properties": props, "additionalProperties": False}
        if name in REQUIRED:
            schema["required"] = REQUIRED[name]
        out.append({"name": name, "description": desc, "inputSchema": schema})
    return out


def call_tool(name, args):
    if name not in TOOLS:
        return {"isError": True, "content": [{"type": "text", "text": "Cong cu khong ton tai: " + name}]}
    method, _d, props, write = TOOLS[name]
    clean = {k: v for k, v in (args or {}).items() if k in props}      # bo tham so la
    try:
        result = Client(client_name=os.environ.get("PKTTC_CLIENT_NAME", "Kuro")).call(method, clean, timeout=900 if write else 120)
        return {"content": [{"type": "text", "text": json.dumps(result, ensure_ascii=False, indent=2)}]}
    except (BridgeError, TimeoutError) as e:
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}


def handle(msg):
    method = msg.get("method")
    mid = msg.get("id")
    if method == "initialize":
        pv = (msg.get("params") or {}).get("protocolVersion", "2024-11-05")
        return {"jsonrpc": "2.0", "id": mid, "result": {
            "protocolVersion": pv, "capabilities": {"tools": {}}, "serverInfo": SERVER_INFO, "instructions": INSTRUCTIONS}}
    if method == "ping":
        return {"jsonrpc": "2.0", "id": mid, "result": {}}
    if method == "tools/list":
        return {"jsonrpc": "2.0", "id": mid, "result": {"tools": tools_list()}}
    if method == "tools/call":
        p = msg.get("params") or {}
        return {"jsonrpc": "2.0", "id": mid, "result": call_tool(p.get("name"), p.get("arguments"))}
    if mid is None:
        return None                                  # thong bao (notifications/*): khong tra loi
    return {"jsonrpc": "2.0", "id": mid, "error": {"code": -32601, "message": "Khong ho tro: %s" % method}}


def main():
    stdin = sys.stdin.buffer
    stdout = sys.stdout.buffer
    for raw in stdin:
        raw = raw.strip()
        if not raw:
            continue
        try:
            msg = json.loads(raw.decode("utf-8"))
        except ValueError:
            resp = {"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": "JSON khong hop le"}}
        else:
            resp = handle(msg)
        if resp is not None:
            stdout.write(json.dumps(resp, ensure_ascii=False).encode("utf-8") + b"\n")
            stdout.flush()


if __name__ == "__main__":
    main()
