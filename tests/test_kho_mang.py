"""Chặn cứng xóa tệp trên kho mạng công ty. Chạy: .venv\\Scripts\\python -m unittest tests.test_kho_mang"""
import asyncio
import os
import sys
import tempfile
import unittest
from pathlib import Path

TMP = tempfile.mkdtemp()
os.environ["KURO_STATE_DIR"] = TMP
os.environ["KURO_BRAINS_DIR"] = TMP
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "server"))

import agy_chan_xoa  # noqa: E402
import config  # noqa: E402
import engine  # noqa: E402

KHO = r"\\phuongthanhtranconsin.data.com\12.KỸ THUẬT THI CÔNG\Cau A"


def chan(tool: str, **vao) -> bool:
    out = asyncio.run(engine.chan_xoa_kho_mang({"tool_name": tool, "tool_input": vao}, None, None))
    return out.get("hookSpecificOutput", {}).get("permissionDecision") == "deny"


class ChanXoaKhoMang(unittest.TestCase):
    def test_lenh_xoa_tren_kho_bi_chan(self):
        self.assertTrue(chan("Bash", command=f'Remove-Item -Recurse "{KHO}\\old"'))
        self.assertTrue(chan("Bash", command=f'cd "{KHO}"\nrm -rf tam'))
        self.assertTrue(chan("PowerShell", command=f'robocopy D:\\1 "{KHO}" /MIR'))
        self.assertTrue(chan("mcp__kuro__tinh_python", code=f'import shutil; shutil.rmtree(r"{KHO}")'))
        self.assertTrue(chan("Write", file_path=r"D:\1\don.py", content=f'import os; os.remove(r"{KHO}\\a.xlsx")'))

    def test_viec_hop_le_khong_bi_chan(self):
        self.assertFalse(chan("Bash", command=r'Remove-Item D:\1\tam.xlsx'))            # xóa trên máy: được
        self.assertFalse(chan("Bash", command=f'Get-ChildItem "{KHO}"'))                 # đọc kho: được
        self.assertFalse(chan("Read", file_path=f"{KHO}\\del.xlsx"))                     # tool đọc: bỏ qua
        self.assertFalse(chan("Write", file_path=r"D:\1\bao-cao.md", content=f"Cần delete {KHO}"))  # báo cáo, không phải script

    def test_la_kho_mang(self):
        self.assertTrue(config.la_kho_mang(KHO + r"\x.xlsx"))
        self.assertFalse(config.la_kho_mang(Path(TMP)))

    def test_cli_nhac_luat_moi_luot(self):   # hội thoại agy/codex cũ cũng phải nhận luật
        self.assertIn("CẤM XÓA", engine.cli_prompt("xóa giúp", first=False))


def chan_agy(ten: str, **args) -> bool:
    return agy_chan_xoa.quyet_dinh({"name": ten, "args": args}).get("decision") == "deny"


class ChanXoaAgy(unittest.TestCase):
    def test_chan(self):
        self.assertTrue(chan_agy("run_command", CommandLine=f'Remove-Item -LiteralPath "{KHO}\\a.pdf"', Cwd=r"d:\1"))
        self.assertTrue(chan_agy("delete_directory", DirectoryPath=KHO))
        self.assertTrue(chan_agy("write_to_file", TargetFile=r"D:\1\x.py", CodeContent=f'import os; os.remove(r"{KHO}\\a")'))

    def test_khong_chan(self):
        self.assertFalse(chan_agy("run_command", CommandLine=r"Remove-Item D:\1\a.pdf", Cwd=r"d:\1"))
        self.assertFalse(chan_agy("view_file", AbsolutePath=f"{KHO}\\del.pdf"))
        self.assertFalse(chan_agy("write_to_file", TargetFile=r"D:\1\bao-cao.md", CodeContent=f"delete {KHO}"))


if __name__ == "__main__":
    unittest.main()
