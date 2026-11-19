"""Gói AutoCAD: script vẽ + kiểm DXF và cơ chế cài/gỡ gói. Chạy: .venv\\Scripts\\python -m unittest discover -s tests"""
import os
import sys
import tempfile
import unittest
from pathlib import Path

TMP = tempfile.mkdtemp()
os.environ.setdefault("KURO_STATE_DIR", TMP)
os.environ.setdefault("KURO_BRAINS_DIR", TMP)
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "server"))
sys.path.insert(0, str(ROOT / "goi" / "autocad" / "autocad-pkttc" / "scripts"))

import ezdxf  # noqa: E402
import config  # noqa: E402
import goi  # noqa: E402
import kiem_dxf  # noqa: E402
from pkttc_dxf import BanVe  # noqa: E402


class VeVaKiem(unittest.TestCase):
    def test_ban_ve_chuan_dat(self):
        bv = BanVe(ty_le=50)
        bv.net([(0, 0), (1000, 0), (1000, 500)], layer="1")
        bv.text("Mặt cắt 1-1 bê tông M300", (0, -300), nhom=2.5)
        bv.dim_ngang((0, 0), (1000, 0), (0, -150))
        f = os.path.join(tempfile.mkdtemp(), "a.dxf")
        loi, _ = bv.luu(f)
        self.assertEqual(loi, {})
        self.assertIn("Mặt cắt 1-1 bê tông M300", [e.dxf.text for e in ezdxf.readfile(f).modelspace().query("TEXT")])

    def test_ban_ve_sai_bi_bat(self):
        bv = BanVe(ty_le=50)
        bv.doc.styles.add("vn-abc", font="vn-abc.shx")
        bv.msp.add_text("sai layer", height=77, dxfattribs={"layer": "0", "style": "vn-abc"})   # layer, cỡ, TCVN3
        bv.msp.add_text("µ¸ tcvn3", height=100, dxfattribs={"layer": "3", "color": 1})          # mã TCVN3, không ByLayer
        d = bv.msp.add_linear_dim(base=(0, -100), p1=(0, 0), p2=(500, 0), text="999", dimstyle="D50",
                                  dxfattribs={"layer": "8"})                                    # dim sửa tay
        d.render()
        f = os.path.join(tempfile.mkdtemp(), "b.dxf")
        bv.doc.saveas(f)
        loi, _ = kiem_dxf.kiem(f)
        chuoi = " | ".join(loi)
        for mong_doi in ("không ở layer 3", "Cao chữ 77", "TCVN3", "không ByLayer", "override"):
            self.assertIn(mong_doi, chuoi)

    def test_tu_choi_tham_so_sai(self):
        with self.assertRaises(ValueError):
            BanVe(ty_le=33)
        with self.assertRaises(ValueError):
            BanVe(ty_le=50).text("x", (0, 0), nhom=4.0)


class CaiGoi(unittest.TestCase):
    def setUp(self):
        config.ensure_dirs()   # brain tạm cần đủ thư mục như lúc Kuro khởi động

    def test_cai_roi_go(self):
        skill = config.BRAIN / ".claude" / "skills" / "autocad-pkttc"
        goi.go("autocad")
        self.assertFalse(skill.exists())
        self.assertIn("chưa cài", goi.liet_ke())
        goi.cai("autocad")
        self.assertTrue((skill / "SKILL.md").is_file())
        self.assertTrue((skill / "scripts" / "kiem_dxf.py").is_file())
        self.assertIn("ĐÃ CÀI", goi.liet_ke())
        goi.go("autocad")
        self.assertFalse(skill.exists())
        with self.assertRaises(ValueError):
            goi.cai("khong-co")


if __name__ == "__main__":
    unittest.main()
