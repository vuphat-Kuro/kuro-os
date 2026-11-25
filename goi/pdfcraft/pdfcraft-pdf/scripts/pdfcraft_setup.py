# -*- coding: utf-8 -*-
"""PdfCraft: status | install | uninstall. Dung goi/_chung/cai_phan_mem.py (tai portable ghim v0.22.0, kiem SHA-256)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "_chung"))
import cai_phan_mem as cp

CFG = {
    "id": "pdfcraft", "ten": "PdfCraft", "repo": "storytold/pdfcraft", "tag": "v0.22.0", "tien_to": "pdfcraft-",
    "exe": "pdfcraft.exe", "cli": "pdfcraft-cli.exe",
    "nhan_cai": "Tải và cài PdfCraft v0.22.0", "nhan_go": "Gỡ PdfCraft",
    "xac_nhan_go": "Gỡ PdfCraft khỏi máy tính này? (tệp của bạn không bị xóa)",
}

if __name__ == "__main__":
    cp.chay(CFG)
