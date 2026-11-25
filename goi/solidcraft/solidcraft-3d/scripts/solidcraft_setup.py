# -*- coding: utf-8 -*-
"""SolidCraft: status | install | uninstall. Dung goi/_chung/cai_phan_mem.py (tai portable ghim v0.49.0, kiem SHA-256)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "_chung"))
import cai_phan_mem as cp

CFG = {
    "id": "solidcraft", "ten": "SolidCraft", "repo": "tangency-labs/solidcraft", "tag": "v0.49.0", "tien_to": "solidcraft-",
    "exe": "solidcraft.exe", "cli": "solidcraft-cli.exe",
    "nhan_cai": "Tải và cài SolidCraft v0.49.0", "nhan_go": "Gỡ SolidCraft",
    "xac_nhan_go": "Gỡ SolidCraft khỏi máy tính này? (tệp của bạn không bị xóa)",
}

if __name__ == "__main__":
    cp.chay(CFG)
