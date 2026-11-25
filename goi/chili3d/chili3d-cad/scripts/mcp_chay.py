# -*- coding: utf-8 -*-
"""MCP stdio cho Chili3D: chay node voi @chili3d/mcp da cai trong state/chili3d-mcp, truyen thang stdin/stdout."""
import shutil
import subprocess
import sys
from pathlib import Path

BIN = Path(__file__).resolve().parents[4] / "state" / "chili3d-mcp" / "node_modules" / "@chili3d" / "mcp" / "bin" / "chili3d-mcp.mjs"

if not BIN.is_file() or not shutil.which("node"):
    sys.stderr.write("Chưa cài cầu nối Chili3D hoặc thiếu Node.js. Mở Cài đặt > Plugins của Kuro để cài.\n")
    sys.exit(2)
sys.exit(subprocess.run([shutil.which("node"), str(BIN), "mcp"]).returncode)
