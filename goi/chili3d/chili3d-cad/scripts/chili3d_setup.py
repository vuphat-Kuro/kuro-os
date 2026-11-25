# -*- coding: utf-8 -*-
"""Chili3D (CAD 3D chay tren trinh duyet, AGPL-3.0): status | open | mcp-install | mcp-uninstall (cau noi MCP @chili3d/mcp bang npm).

Kuro KHONG kem va khong chay ma Chili3D: trang web mo tu https://chili3d.com (hoac ban tu dung cua nguoi dung) va tu noi
nguoc ve cong WebSocket 127.0.0.1:17373 do @chili3d/mcp mo. Goi npm: cai vao state/chili3d-mcp, ghim phien ban.
"""
import shutil
import subprocess
import sys
import webbrowser
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "_chung"))
import cai_phan_mem as cp

PIN = "0.8.0"          # ban web Chili3D tham chieu
PIN_MCP = "0.1.0"      # @chili3d/mcp
DIR = cp.ROOT / "state" / "chili3d-mcp"
BIN = DIR / "node_modules" / "@chili3d" / "mcp" / "bin" / "chili3d-mcp.mjs"


def node_ok():
    n = shutil.which("node")
    if not n:
        return None
    try:
        v = subprocess.run([n, "--version"], capture_output=True, text=True, timeout=10).stdout.strip().lstrip("v")
        return n if int(v.split(".")[0]) >= 20 else None
    except (OSError, ValueError, subprocess.SubprocessError):
        return None


def status(extra=None):
    """Phan mem = trang web Chili3D (khong cai gi). Cau noi npm la phan MCP (hanh dong mcp-install/mcp-uninstall)."""
    cp.out({"ok": True, "phien_ban_goi": PIN, "trang_thai": "web", "goi_y": [],
            "nut_them": [{"action": "open", "nhan": "Mở Chili3D"}],
            "thong_bao": "Chili3D là web app chạy trong trình duyệt: không cần cài. Mở https://chili3d.com rồi để tab ở phía trước khi dùng MCP.",
            **(extra or {})})


def main():
    act = sys.argv[1] if len(sys.argv) > 1 else "status"
    if act == "status":
        status()
    elif act == "open":
        webbrowser.open("https://chili3d.com/?bridge=17373")
        status({"thong_bao": "Đã mở https://chili3d.com trong trình duyệt."})
    elif act == "mcp-install":
        npm = shutil.which("npm")
        if not npm or not node_ok():
            cp.out({"ok": False, "trang_thai": "loi", "thong_bao": "Thiếu Node.js 20+ hoặc npm."}, 1)
        DIR.mkdir(parents=True, exist_ok=True)
        r = subprocess.run([npm, "install", "--prefix", str(DIR), f"@chili3d/mcp@{PIN_MCP}", "--no-audit", "--no-fund", "--ignore-scripts"],
                           capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=150,
                           creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        if r.returncode or not BIN.is_file():
            cp.out({"ok": False, "trang_thai": "loi", "thong_bao": "npm lỗi: " + ((r.stderr or r.stdout).strip().splitlines() or [""])[-1][:250]}, 1)
        status({"thong_bao": f"Đã cài cầu nối MCP @chili3d/mcp {PIN_MCP}."})
    elif act == "mcp-uninstall":
        shutil.rmtree(DIR, ignore_errors=True)
        status({"thong_bao": "Đã gỡ cầu nối MCP."})
    else:
        cp.out({"ok": False, "trang_thai": "loi", "thong_bao": f"Hành động không hỗ trợ: {act}"}, 1)


if __name__ == "__main__":
    main()
