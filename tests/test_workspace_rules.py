"""Kiểm thử quy tắc thư mục dự án: nguồn duy nhất là tệp QUY_TAC_LAM_VIEC.md trong dự án."""
import os
import sys
import tempfile
import unittest
from pathlib import Path

TMP = tempfile.mkdtemp()
os.environ["KURO_STATE_DIR"] = TMP
os.environ["KURO_BRAINS_DIR"] = TMP
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "server"))

import config  # noqa: E402
import engine  # noqa: E402
import main  # noqa: E402
import workspace_rules  # noqa: E402

RF = "QUY_TAC_LAM_VIEC.md"


class WorkspaceRulesTest(unittest.TestCase):
    def setUp(self):
        from starlette.testclient import TestClient
        self.tmp = Path(tempfile.mkdtemp())
        self.keep = (config.STATE, engine.WORKSPACES_FILE)
        config.STATE = self.tmp / "state"
        config.STATE.mkdir(parents=True, exist_ok=True)
        engine.WORKSPACES_FILE = config.STATE / "workspaces.json"
        self.client = TestClient(main.app, base_url="http://127.0.0.1:7788", client=("127.0.0.1", 5000))

    def tearDown(self):
        config.STATE, engine.WORKSPACES_FILE = self.keep

    def prompt(self, ws):
        return workspace_rules.build_workspace_rules_prompt(ws, engine.get_workspaces_config())

    def test_apply_standard_writes_rules_file_then_user_edit_wins(self):
        ws = self.tmp / "DU_AN_CAU_XYZ"
        ws.mkdir()
        rules = self.client.post("/api/workspaces/open", json={"path": str(ws)}).json()["rules"]
        self.assertEqual(rules["mode"], "unset")
        self.assertTrue(rules["needs_prompt"])

        # Áp dụng Kuro Standard -> 3 thư mục + tệp quy tắc viết từ mẫu, prompt lấy từ tệp
        r = self.client.post("/api/workspaces/rules", json={"mode": "standard"}).json()
        self.assertEqual(r["mode"], "rules")
        self.assertFalse(r["needs_prompt"])
        for d in ("01_TAI_LIEU", "02_KURO_XU_LY", "03_KET_QUA"):
            self.assertTrue((ws / d).is_dir(), f"Thiếu thư mục {d}")
        self.assertTrue((ws / RF).is_file())
        self.assertIn("TASK_001_", self.prompt(ws))

        # Người dùng sửa tệp ngoài Kuro -> lượt sau làm theo bản đã sửa, không còn mẫu cũ
        (ws / RF).write_text("# Quy tắc\n- Kết quả lưu vào thư mục XUAT/\n", encoding="utf-8")
        p = self.prompt(ws)
        self.assertIn("XUAT/", p)
        self.assertNotIn("TASK_001_", p)

        # Áp dụng lại Kuro Standard không ghi đè tệp người dùng đã sửa
        self.client.post("/api/workspaces/rules", json={"mode": "standard"})
        self.assertIn("XUAT/", (ws / RF).read_text(encoding="utf-8"))

        # Sửa qua hộp thoại, rồi xóa trắng = bỏ quy tắc, làm việc bình thường
        r = self.client.post("/api/workspaces/rules", json={"mode": "keep", "content": "- Font Times New Roman"}).json()
        self.assertIn("Times New Roman", r["content"])
        r = self.client.post("/api/workspaces/rules", json={"mode": "keep", "content": "  "}).json()
        self.assertFalse(r["has_rules"])
        self.assertIn("NƠI LƯU KẾT QUẢ BẮT BUỘC", self.prompt(ws))

    def test_existing_rules_file_used_without_prompt(self):
        ws = self.tmp / "DU_AN_DA_CO_QUY_TAC"
        ws.mkdir()
        (ws / RF).write_text("# Quy tắc\n- Lưu hết vào thư mục BaoCao/\n", encoding="utf-8")
        rules = self.client.post("/api/workspaces/open", json={"path": str(ws)}).json()["rules"]
        self.assertEqual(rules["mode"], "rules")
        self.assertFalse(rules["needs_prompt"])

    def test_three_dirs_without_rules_file_works_normally(self):
        ws = self.tmp / "DU_AN_3_THU_MUC_KHONG_TEP"
        for d in ("01_TAI_LIEU", "02_KURO_XU_LY", "03_KET_QUA"):
            (ws / d).mkdir(parents=True)
        rules = self.client.post("/api/workspaces/open", json={"path": str(ws)}).json()["rules"]
        self.assertFalse(rules["has_rules"])
        self.assertNotIn("TASK_001_", self.prompt(ws))

    def test_old_v181_project_migrated_to_rules_file(self):
        ws = self.tmp / "DU_AN_CU"
        ws.mkdir()
        (ws / "QUY_TAC_RIENG.md").write_text("- Bảng Excel dùng font Times New Roman\n", encoding="utf-8")
        cfg = engine.get_workspaces_config()
        cfg["rules"] = {ws.resolve().as_posix().lower(): "standard"}
        engine.save_workspaces_config(cfg)
        st = workspace_rules.inspect_workspace_rules(ws, engine.get_workspaces_config())
        self.assertEqual(st["mode"], "rules")
        txt = (ws / RF).read_text(encoding="utf-8")
        self.assertIn("TASK_001_", txt)
        self.assertIn("Times New Roman", txt)
        self.assertFalse((ws / "QUY_TAC_RIENG.md").exists())

    def test_decline_rules_remembered_no_repeat_prompt(self):
        ws = self.tmp / "DU_AN_KHONG_AP_DUNG"
        ws.mkdir()
        self.client.post("/api/workspaces/open", json={"path": str(ws)})
        r_no = self.client.post("/api/workspaces/rules", json={"mode": "none"}).json()
        self.assertEqual(r_no["mode"], "none")
        self.assertFalse(r_no["needs_prompt"])
        self.assertFalse((ws / "01_TAI_LIEU").exists())
        r_reopen = self.client.post("/api/workspaces/open", json={"path": str(ws)})
        self.assertFalse(r_reopen.json()["rules"]["needs_prompt"])

    def test_attachments_inside_xu_ly(self):
        ws = self.tmp / "DU_AN_DINH_KEM"
        ws.mkdir()
        self.assertEqual(workspace_rules.attachments_dir(ws), ws / ".attachments")
        (ws / "02_KURO_XU_LY").mkdir()
        self.assertEqual(workspace_rules.attachments_dir(ws), ws / "02_KURO_XU_LY" / ".attachments")


if __name__ == "__main__":
    unittest.main()
