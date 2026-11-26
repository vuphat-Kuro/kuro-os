"""Máy chủ MCP độc lập của Kuro: đưa skill ngành và công cụ tính cho MỌI AI, không riêng Claude.

Đường Claude dùng calc.SERVER (MCP chạy trong tiến trình Kuro). Codex/agy chạy chương trình riêng nên không thấy công cụ
đó, cũng không mở được SKILL.md khi Kuro tắt Bash: chúng chỉ nhận danh sách tên skill rồi tự làm theo trí nhớ (phản hồi
26/11/2026: Codex nhận "chưa dùng skill tinh-toan-ky-thuat"). Tệp này chạy qua stdio, Kuro khai cho Codex bằng -c
mcp_servers.kuro.* (tiet_kiem.codex_args). Chạy thử: .venv\\Scripts\\python server\\kuro_mcp.py
"""
import contextlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
with contextlib.redirect_stdout(sys.stderr):   # stdout là kênh MCP: chữ in lúc nạp (vd đồng bộ gói) làm hỏng giao thức
    import calc
    import config
    import kho
    from mcp.server.mcpserver import MCPServer

SKILL_DIR = config.BRAIN / ".claude" / "skills"
DOC_MAX = 60_000

srv = MCPServer("kuro", instructions="Skill ngành xây dựng và công cụ tính của Kuro (trợ lý kỹ sư hạ tầng).")


def doc_skill_nganh_text(ten: str, tep: str = "SKILL.md") -> str:
    """Nội dung một tệp của skill ngành trong brain; chặn đi ra ngoài thư mục skill."""
    goc = (SKILL_DIR / Path(ten).name).resolve()
    if not (goc / "SKILL.md").is_file():
        co = sorted(p.parent.name for p in SKILL_DIR.glob("*/SKILL.md"))
        return f"[LỖI] Không có skill ngành '{ten}'. Các skill có: {', '.join(co)}"
    f = (goc / (tep or "SKILL.md")).resolve()
    if not f.is_relative_to(goc) or not f.is_file():
        return f"[LỖI] Không có tệp '{tep}' trong skill '{ten}'."
    t = f.read_text(encoding="utf-8", errors="replace")
    return t if len(t) <= DOC_MAX else t[:DOC_MAX] + f"\n...(cắt, tệp dài {len(t):,} ký tự)"


@srv.tool(description="Đọc hướng dẫn của một SKILL NGÀNH của Kuro (tên trong danh mục skill ngành, vd 'tinh-toan-ky-thuat', "
                      "'qs-khoi-luong-du-toan'). Câu hỏi chuyên môn: gọi TRƯỚC khi trả lời rồi làm theo. tep: tệp kèm "
                      "theo trong skill (mặc định SKILL.md).")
def doc_skill_nganh(ten: str, tep: str = "SKILL.md") -> str:
    return doc_skill_nganh_text(ten, tep)


@srv.tool(description=calc.DESC)
def tinh_python(code: str, muc_dich: str = "") -> str:
    return calc.run_python(code, muc_dich)


@srv.tool(description="Tìm skill trong KHO 230 skill (BIM, IFC, bóc khối lượng, dự toán, tiến độ, an toàn, hợp đồng...) "
                      "khi skill ngành không phủ việc. Truyền TỪ KHOÁ TIẾNG ANH, vd 'ifc quantity takeoff concrete'.")
def tim_skill(tu_khoa: str) -> str:
    kq = kho.tim(tu_khoa)
    return json.dumps(kq, ensure_ascii=False) if kq else "Không có skill phù hợp trong kho."


@srv.tool(description="Đọc hướng dẫn của một skill trong KHO (mặc định SKILL.md, hoặc tệp kèm theo đường dẫn tương đối).")
def doc_skill(skill: str, tep: str = "SKILL.md") -> str:
    try:
        return kho.doc(skill, tep or "SKILL.md")
    except ValueError as e:
        return f"[LỖI] {e}"


@srv.tool(description="Chạy một script .py/.mjs/.js của skill trong KHO, CHỈ khi mã skill đã được duyệt. Thư mục làm việc "
                      "là dự án đang mở. doi_so: danh sách tham số dòng lệnh.")
def chay_ma_kho(skill: str, tep: str, doi_so: list[str] | None = None) -> str:
    try:
        return kho.chay(skill, tep, doi_so or [], Path.cwd())   # AI gọi MCP với thư mục làm việc = dự án đang mở
    except ValueError as e:
        return f"[LỖI] {e}"


TOOLS = ["doc_skill_nganh", "tinh_python", "tim_skill", "doc_skill", "chay_ma_kho"]

if __name__ == "__main__":
    srv.run("stdio")
