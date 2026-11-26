"""Tiết kiệm token cho mọi AI của Kuro (Claude, ChatGPT/Codex, Antigravity).

- Trả lời gọn (KURO_TRA_LOI_GON, mặc định bật): luật văn phong rút từ caveman 4.1.0 (github.com/JuliusBrussee/caveman),
  viết lại bằng tiếng Việt: bỏ rào đón, giữ nguyên số liệu, đơn vị, đường dẫn, điều khoản.
- context-mode (github.com/mksglu/context-mode, đã duyệt 2.1.7: không telemetry, không đọc key): MCP cất kết quả dài
  vào kho tìm kiếm FTS5 thay vì nhét cả vào ngữ cảnh. ctx_execute/ctx_batch chạy mã tuỳ ý nên chỉ mở khi Kuro bật Bash.
  Tìm server.mjs ở KURO_CONTEXT_MODE hoặc plugin Claude Code đã cài; KURO_CONTEXT_MODE=0 để tắt.
- RTK (github.com/rtk-ai/rtk, đã duyệt 0.49: telemetry tắt sẵn, bản build không có địa chỉ gửi): rút gọn đầu ra lệnh
  shell. Chỉ có ích khi Kuro bật Bash; Kuro đặt RTK_TELEMETRY_DISABLED=1 cho tiến trình con.
"""
import functools
import os
import re
import shutil
import subprocess
from pathlib import Path

import config

CTX_DOC = ["ctx_index", "ctx_search", "ctx_stats"]
CTX_CHAY_MA = ["ctx_execute", "ctx_batch"]
ENV = {"RTK_TELEMETRY_DISABLED": "1"}

TRA_LOI_GON = """

## Trả lời gọn (tiết kiệm token)
- Kết luận hoặc việc cần làm đi đầu, lý do sau. Không chào hỏi, không rào đón, không nhắc lại câu hỏi, không tóm tắt lại ở cuối, không câu kết xã giao.
- Câu ngắn, một ý một câu. Từ ngắn, đúng thuật ngữ ngành; không tự chế viết tắt.
- Số liệu, đơn vị, mác vật liệu, số hiệu điều khoản, đường dẫn, lệnh, mã: giữ NGUYÊN VĂN. Không bỏ chữ "không", "chưa", "chỉ", "trừ".
- Đang gọi công cụ: không viết chữ giữa các lần gọi thường lệ; chỉ một dòng khi đổi bước và một dòng kết quả.
- Bảng hoặc danh sách thay cho đoạn văn dài. Rõ ràng thắng ngắn gọn: thiếu chữ mà hiểu sai thì viết đủ."""


def gon() -> bool:
    return os.getenv("KURO_TRA_LOI_GON", "1").strip() != "0"


def _phien_ban(p: Path) -> tuple:
    return tuple(int(x) for x in re.findall(r"\d+", p.parent.name)) or (0,)


@functools.cache
def _node_du_moi() -> bool:
    """context-mode 2.x cần Node >= 24.15."""
    node = shutil.which("node")
    if not node:
        return False
    try:
        v = subprocess.run([node, "-v"], capture_output=True, text=True, timeout=10,
                           creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0)).stdout
        so = tuple(int(x) for x in re.findall(r"\d+", v)[:2])
        return so >= (24, 15)
    except (OSError, subprocess.SubprocessError, ValueError):
        return False


@functools.cache
def context_mode() -> str | None:
    """Đường dẫn server.mjs của context-mode, None nếu tắt hoặc máy chưa có."""
    chon = os.getenv("KURO_CONTEXT_MODE", "").strip()
    if chon == "0":
        return None
    if chon:
        ung_vien = [Path(chon)]
    else:
        goc = Path.home() / ".claude" / "plugins" / "cache" / "context-mode" / "context-mode"
        ung_vien = sorted(goc.glob("*/server.mjs"), key=_phien_ban, reverse=True)
    for p in ung_vien:
        if p.is_file() and _node_du_moi():
            return str(p)
    return None


def ctx_tools(shell: bool) -> list[str]:
    return CTX_DOC + (CTX_CHAY_MA if shell else []) if context_mode() else []


def mcp_claude(shell: bool) -> tuple[dict, list[str]]:
    """(mcp_servers, allowed_tools) thêm cho đường Claude."""
    srv = context_mode()
    if not srv:
        return {}, []
    return ({"context-mode": {"command": "node", "args": [srv, "--agent", "claude-code"]}},
            [f"mcp__context-mode__{t}" for t in ctx_tools(shell)])


def codex_args(shell: bool) -> list[str]:
    """Cờ -c cho codex exec: nạp context-mode và chỉ bật đúng các tool được phép."""
    srv = context_mode()
    if not srv:
        return []
    ds = ", ".join(f'"{t}"' for t in ctx_tools(shell))
    return ["-c", 'mcp_servers.context-mode.command="node"',
            "-c", f'mcp_servers.context-mode.args=["{srv.replace(chr(92), "/")}", "--agent", "codex"]',
            "-c", f"mcp_servers.context-mode.enabled_tools=[{ds}]",
            # approval_policy=never từ chối MCP tool cần duyệt; danh sách tool đã lọc theo quyền Bash ở trên
            "-c", 'mcp_servers.context-mode.default_tools_approval_mode="approve"']


def huong_dan(shell: bool) -> str:
    """Khối hướng dẫn nối vào system prompt (Claude) hoặc lượt đầu (Codex/agy)."""
    out = TRA_LOI_GON if gon() else ""
    if context_mode():
        out += ("\n\n## Kết quả dài (context-mode)\nTệp hay kết quả dài (văn bản, log, bảng xuất CSV/MD): dùng ctx_index cất "
                "vào kho rồi ctx_search lấy đúng đoạn cần, đừng đọc cả tệp vào hội thoại.")
        if shell:
            out += (" Cần lọc/đếm/tổng hợp dữ liệu lớn thì chạy bằng ctx_execute và chỉ in kết quả, không in dữ liệu thô. "
                    "Vẫn giữ luật kho mạng: không xoá, không ghi vào \\\\phuongthanhtranconsin.data.com.")
    if shell and shutil.which("rtk"):
        out += ("\n\n## Lệnh shell gọn (RTK)\nCó sẵn `rtk`: chạy lệnh qua nó để đầu ra ngắn, vd `rtk git status`, "
                "`rtk grep mẫu thư_mục`, `rtk read tệp`, `rtk ls`, `rtk find`, `rtk log tệp.log`, `rtk err lệnh`.")
    return out
