# -*- coding: utf-8 -*-
"""CADCraft: status | install | uninstall. Dung goi/_chung/cai_phan_mem.py (tai portable ghim v0.20.1, kiem SHA-256)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "_chung"))
import cai_phan_mem as cp

CFG = {
    "id": "cadcraft", "ten": "CADCraft", "repo": "storytold/cadcraft", "tag": "v0.20.1", "tien_to": "cadcraft-",
    "exe": "cadcraft.exe", "cli": "cadcraft-cli.exe",
    "nhan_cai": "Tải và cài CADCraft v0.20.1", "nhan_go": "Gỡ CADCraft",
    "xac_nhan_go": "Gỡ CADCraft khỏi máy tính này? (tệp của bạn không bị xóa)",
}

if __name__ == "__main__":
    cp.chay(CFG)
