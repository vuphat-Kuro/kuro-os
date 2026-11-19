"""Chặn cứng xóa tệp trên kho mạng công ty. Chạy: .venv\\Scripts\\python -m unittest tests.test_kho_mang"""
import asyncio
import json
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

    def test_cli_nhac_luat_moi_luot(self):   # hội thoại agy/codex cũ cũng phải nhận luật kho mạng + quy tắc thư mục
        ws = Path(tempfile.mkdtemp())
        for d in ("01_TAI_LIEU", "02_KURO_XU_LY", "03_KET_QUA"):
            (ws / d).mkdir()
        p = engine.cli_prompt("dọn dẹp thư mục", first=False, ws_dir=str(ws))
        self.assertIn("CẤM XÓA", p)
        self.assertIn("KURO STANDARD", p)
        self.assertTrue(p.endswith("dọn dẹp thư mục"))


def chan_agy(ten: str, **args) -> bool:
    return agy_chan_xoa.quyet_dinh({"name": ten, "args": args}).get("decision") == "deny"


class ChanXoaAgy(unittest.TestCase):
    def test_chan(self):
        self.assertTrue(chan_agy("run_command", CommandLine=f'Remove-Item -LiteralPath "{KHO}\\a.pdf"', Cwd=r"d:\1"))
        self.assertTrue(chan_agy("delete_directory", DirectoryPath=KHO))
        self.assertTrue(chan_agy("write_to_file", TargetFile=r"D:\1\x.py", CodeContent=f'import os; os.remove(r"{KHO}\\a")'))

    def test_luon_tra_decision(self):   # agy coi đầu ra thiếu "decision" là từ chối, chặn mọi tool (lỗi bản 8ebf487)
        import subprocess
        hook = Path(__file__).resolve().parent.parent / "server" / "agy_chan_xoa.py"
        inp = '{"toolCall": {"name": "view_file", "args": {"AbsolutePath": "D:\\\\1\\\\a.xlsx"}}}'
        for flag, mong in (("1", "allow"), ("", "ask")):
            r = subprocess.run([sys.executable, str(hook)], input=inp.encode(), capture_output=True,
                               env={**os.environ, "KURO_AGY": flag})
            self.assertEqual(json.loads(r.stdout)["decision"], mong)

    def test_go_hook_cu(self):
        import cli_engines
        f = Path(TMP) / "hooks.json"
        f.write_text('{"kuro-chan-xoa-kho-mang": {}, "cua-nguoi-dung": {"enabled": true}}', encoding="utf-8")
        cu, cli_engines.HOOK_AGY = cli_engines.HOOK_AGY, f
        try:
            cli_engines.go_hook_agy()
        finally:
            cli_engines.HOOK_AGY = cu
        self.assertEqual(json.loads(f.read_text(encoding="utf-8")), {"cua-nguoi-dung": {"enabled": True}})

    def test_khong_chan(self):
        self.assertFalse(chan_agy("run_command", CommandLine=r"Remove-Item D:\1\a.pdf", Cwd=r"d:\1"))
        self.assertFalse(chan_agy("view_file", AbsolutePath=f"{KHO}\\del.pdf"))
        self.assertFalse(chan_agy("write_to_file", TargetFile=r"D:\1\bao-cao.md", CodeContent=f"delete {KHO}"))


if __name__ == "__main__":
    unittest.main()
