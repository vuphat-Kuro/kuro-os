"""Gói AutoCAD & hệ thống Plugins (tích hợp sẵn + gói bên ngoài). Chạy: .venv\\Scripts\\python -m unittest discover -s tests"""
import io
import json
import os
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

TMP = tempfile.mkdtemp()
os.environ.setdefault("KURO_STATE_DIR", TMP)
os.environ.setdefault("KURO_BRAINS_DIR", TMP)
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "server"))
sys.path.insert(0, str(ROOT / "goi" / "autocad" / "autocad-pkttc" / "scripts"))

import ezdxf  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
import config  # noqa: E402
import goi  # noqa: E402
import kiem_dxf  # noqa: E402
import main as srv_main  # noqa: E402
from pkttc_dxf import BanVe  # noqa: E402


def _make_zip(files: dict[str, str | bytes]) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for name, content in files.items():
            zf.writestr(name, content)
    return buf.getvalue()


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

    def test_cai_goi_ngoai_tu_zip_day_du_va_go(self):
        # Giữ sẵn 1 MCP server của người dùng để kiểm tra không bị ghi đè/xóa nhầm
        config.MCP_FILE.write_text(json.dumps({"mcpServers": {"user-keep": {"command": "echo"}}}), encoding="utf-8")
        data = _make_zip({
            "my-bridge-main/goi.json": json.dumps({
                "id": "cau-thu-nghiem",
                "ten": "Kiểm toán dầm cầu thử nghiệm",
                "mo_ta": "Plugin ngoài mẫu cho kỹ sư cầu",
                "phien_ban": "1.2.0",
                "skill": "dam-cau-mau",
                "agents": ["ky-su-dam-mau.md"],
                "mcp": {"bridge-mcp": {"command": "python", "args": ["-V"]}},
            }, ensure_ascii=False),
            "my-bridge-main/dam-cau-mau/SKILL.md": "---\nname: dam-cau-mau\ndescription: Skill mẫu\n---\n# Hướng dẫn",
            "my-bridge-main/agents/ky-su-dam-mau.md": "---\nname: ky-su-dam-mau\ndescription: Cộng sự mẫu\n---\nNội dung",
        })
        res = goi.cai_tu_zip(data, "cau-thu-nghiem.zip")
        self.assertTrue(res["ok"])
        self.assertEqual(res["id"], "cau-thu-nghiem")
        self.assertTrue((config.BRAIN / ".claude" / "skills" / "dam-cau-mau" / "SKILL.md").is_file())
        self.assertTrue((config.BRAIN / "agents" / "ky-su-dam-mau.md").is_file())
        mcp_now = json.loads(config.MCP_FILE.read_text(encoding="utf-8"))["mcpServers"]
        self.assertIn("user-keep", mcp_now)
        self.assertIn("bridge-mcp", mcp_now)

        ds = goi.danh_sach()
        ext = next(p for p in ds["plugins"] if p["id"] == "cau-thu-nghiem")
        self.assertEqual(ext["nguon"], "external")
        self.assertTrue(ext["da_cai"])
        self.assertEqual(ext["skills"], ["dam-cau-mau"])
        self.assertEqual(ext["agents"], ["ky-su-dam-mau.md"])
        self.assertEqual(ext["mcp"], ["bridge-mcp"])

        # Đồng bộ lại vẫn giữ nguyên plugin ngoài
        config.sync_bundled()
        self.assertTrue((config.BRAIN / ".claude" / "skills" / "dam-cau-mau" / "SKILL.md").is_file())

        # Gỡ plugin ngoài -> xóa skill, agent, đúng MCP của nó và giữ nguyên MCP của người dùng
        goi.go("cau-thu-nghiem")
        self.assertFalse((config.BRAIN / ".claude" / "skills" / "dam-cau-mau").exists())
        self.assertFalse((config.BRAIN / "agents" / "ky-su-dam-mau.md").exists())
        self.assertFalse((goi.ngoai_dir() / "cau-thu-nghiem").exists())
        mcp_after = json.loads(config.MCP_FILE.read_text(encoding="utf-8"))["mcpServers"]
        self.assertIn("user-keep", mcp_after)
        self.assertNotIn("bridge-mcp", mcp_after)

    def test_cai_goi_ngoai_chi_co_skill_md_va_tu_thu_muc(self):
        # 1) Zip chỉ có SKILL.md (không có goi.json)
        data = _make_zip({
            "SKILL.md": "---\nname: kiem-tra-thep-ngoai\ndescription: Kiểm tra bố trí cốt thép\n---\n# Quy trình"
        })
        res = goi.cai_tu_zip(data, "kiem-tra-thep-ngoai.kuro-plugin")
        self.assertEqual(res["id"], "kiem-tra-thep-ngoai")
        self.assertTrue((config.BRAIN / ".claude" / "skills" / "kiem-tra-thep-ngoai" / "SKILL.md").is_file())
        goi.go("kiem-tra-thep-ngoai")

        # 2) Thư mục cục bộ (không sửa nguồn)
        src = Path(tempfile.mkdtemp()) / "goi-thu-muc"
        (src / "skill-thu-muc").mkdir(parents=True)
        (src / "goi.json").write_text(json.dumps({
            "id": "goi-thu-muc",
            "ten": "Gói từ thư mục",
            "mo_ta": "Cài từ ổ đĩa cục bộ",
            "skill": "skill-thu-muc",
        }, ensure_ascii=False), encoding="utf-8")
        (src / "skill-thu-muc" / "SKILL.md").write_text("# Skill từ thư mục", encoding="utf-8")

        res2 = goi.cai_tu_duong_dan(str(src))
        self.assertEqual(res2["id"], "goi-thu-muc")
        self.assertTrue((config.BRAIN / ".claude" / "skills" / "skill-thu-muc" / "SKILL.md").is_file())
        goi.go("goi-thu-muc")
        # Thư mục nguồn vẫn còn nguyên vẹn
        self.assertTrue((src / "goi.json").is_file())

    def test_bao_mat_goi_ngoai(self):
        # Chặn Zip Slip
        bad_zip = _make_zip({"../thoat.txt": "hack"})
        with self.assertRaises(ValueError):
            goi.cai_tu_zip(bad_zip, "bad.zip")

        # Chặn cờ pip độc hại
        bad_pip = _make_zip({
            "goi.json": json.dumps({"id": "pip-xau", "skill": "s1", "pip": ["--index-url=http://evil"]}),
            "s1/SKILL.md": "# x",
        })
        with self.assertRaises(ValueError):
            goi.cai_tu_zip(bad_pip, "pip.zip")

        # Chặn trùng mã plugin tích hợp sẵn
        dup_builtin = _make_zip({
            "goi.json": json.dumps({"id": "autocad", "skill": "khac"}),
            "khac/SKILL.md": "# x",
        })
        with self.assertRaises(ValueError):
            goi.cai_tu_zip(dup_builtin, "dup.zip")

        # Chặn ghi đè skill lõi của Kuro
        dup_core = _make_zip({
            "goi.json": json.dumps({"id": "ngoai-trung-loi", "skill": "tinh-toan-ky-thuat"}),
            "tinh-toan-ky-thuat/SKILL.md": "# x",
        })
        with self.assertRaises(ValueError):
            goi.cai_tu_zip(dup_core, "dup-core.zip")


class PluginsApi(unittest.TestCase):
    def setUp(self):
        config.ensure_dirs()
        self.client = TestClient(srv_main.app, base_url="http://127.0.0.1:7788", client=("127.0.0.1", 50000))

    def test_api_plugins_end_to_end(self):
        r = self.client.get("/api/plugins")
        self.assertEqual(r.status_code, 200)
        body = r.json()
        self.assertTrue(any(p["id"] == "autocad" and p["nguon"] == "builtin" for p in body["plugins"]))

        # Cài & gỡ gói tích hợp sẵn qua API
        r_inst = self.client.post("/api/plugins/install", json={"id": "autocad"})
        self.assertEqual(r_inst.status_code, 200)
        self.assertTrue(r_inst.json()["ok"])
        self.assertTrue(next(p for p in r_inst.json()["plugins"] if p["id"] == "autocad")["da_cai"])

        r_un = self.client.post("/api/plugins/uninstall", json={"id": "autocad"})
        self.assertEqual(r_un.status_code, 200)
        self.assertFalse(next(p for p in r_un.json()["plugins"] if p["id"] == "autocad")["da_cai"])

        # Tải lên file .zip gói plugin bên ngoài qua API
        zip_bytes = _make_zip({
            "goi.json": json.dumps({
                "id": "api-ext-demo",
                "ten": "Plugin API mẫu",
                "mo_ta": "Thử nghiệm tải lên zip",
                "skill": "api-ext-skill",
            }, ensure_ascii=False),
            "api-ext-skill/SKILL.md": "# API Ext Skill",
        })
        r_up = self.client.post(
            "/api/plugins/install-external-upload",
            files={"file": ("api-ext-demo.zip", zip_bytes, "application/zip")},
        )
        self.assertEqual(r_up.status_code, 200, r_up.text)
        self.assertEqual(r_up.json()["id"], "api-ext-demo")
        self.assertTrue(any(p["id"] == "api-ext-demo" and p["nguon"] == "external" for p in r_up.json()["plugins"]))

        # Gỡ gói ngoài qua API
        r_del = self.client.post("/api/plugins/uninstall", json={"id": "api-ext-demo"})
        self.assertEqual(r_del.status_code, 200)
        self.assertFalse(any(p["id"] == "api-ext-demo" for p in r_del.json()["plugins"]))

        # Cài từ thư mục cục bộ qua API
        src = Path(tempfile.mkdtemp()) / "api-dir-demo"
        (src / "api-dir-skill").mkdir(parents=True)
        (src / "api-dir-skill" / "SKILL.md").write_text("---\nname: api-dir-skill\ndescription: Skill từ thư mục API\n---\n# Hi", encoding="utf-8")
        r_path = self.client.post("/api/plugins/install-external-path", json={"path": str(src)})
        self.assertEqual(r_path.status_code, 200, r_path.text)
        self.assertEqual(r_path.json()["id"], "api-dir-skill")
        self.assertEqual(self.client.post("/api/plugins/uninstall", json={"id": "api-dir-skill"}).status_code, 200)

        # Thiết bị từ xa (đã ghép hoặc chưa ghép) bị chặn
        remote = TestClient(srv_main.app, base_url="http://192.168.1.5:7788", client=("192.168.1.50", 50000))
        remote.cookies.set("kuro_t", config.remote_token())
        self.assertEqual(remote.get("/api/plugins").status_code, 403)

    def test_texthub_tich_hop_va_kiem_tra_may(self):
        r = self.client.get("/api/plugins")
        self.assertEqual(r.status_code, 200)
        th = next((p for p in r.json()["plugins"] if p["id"] == "texthub"), None)
        self.assertIsNotNone(th)
        self.assertEqual(th["nguon"], "builtin")
        self.assertEqual(th["phien_ban"], "0.9.3")
        self.assertTrue(th["co_cai_dat_may"])
        self.assertIsInstance(th["trang_thai_may"], dict)
        self.assertEqual(th["trang_thai_may"].get("id"), "texthub")
        self.assertNotEqual(th["trang_thai_may"].get("trang_thai"), "loi")

        # Cài & gỡ skill texthub trong Brain (không đụng AutoCAD)
        r_inst = self.client.post("/api/plugins/install", json={"id": "texthub"})
        self.assertEqual(r_inst.status_code, 200)
        self.assertTrue((config.BRAIN / ".claude" / "skills" / "texthub-cad" / "SKILL.md").is_file())

        # API setup chỉ đọc (status) hoạt động, hành động lạ bị chặn 400
        r_st = self.client.post("/api/plugins/setup", json={"id": "texthub", "action": "status"})
        self.assertEqual(r_st.status_code, 200)
        self.assertEqual(r_st.json()["ket_qua"]["id"], "texthub")
        self.assertEqual(self.client.post("/api/plugins/setup", json={"id": "texthub", "action": "hack"}).status_code, 400)
        self.assertEqual(self.client.post("/api/plugins/setup", json={"id": "autocad", "action": "status"}).status_code, 400)

        r_un = self.client.post("/api/plugins/uninstall", json={"id": "texthub"})
        self.assertEqual(r_un.status_code, 200)
        self.assertFalse((config.BRAIN / ".claude" / "skills" / "texthub-cad").exists())


if __name__ == "__main__":
    unittest.main()
