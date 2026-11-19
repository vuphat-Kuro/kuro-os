"""Kiểm thử quy tắc Local Workspace (Kuro Standard: 3 thư mục + 7 quy tắc + QUY_TAC_RIENG.md)."""
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

    def test_unset_then_apply_kuro_standard_and_custom(self):
        ws = self.tmp / "DU_AN_CAU_XYZ"
        ws.mkdir()

        # 1. Mở dự án mới chưa có quy tắc -> needs_prompt = True
        r_open = self.client.post("/api/workspaces/open", json={"path": str(ws)})
        self.assertEqual(r_open.status_code, 200)
        rules = r_open.json()["rules"]
        self.assertEqual(rules["mode"], "unset")
        self.assertTrue(rules["needs_prompt"])

        # 2. Áp dụng Kuro Standard -> tạo đủ 3 thư mục chuẩn và nạp đủ 7 quy tắc vào prompt
        r_apply = self.client.post("/api/workspaces/rules", json={"mode": "standard"})
        self.assertEqual(r_apply.status_code, 200)
        self.assertEqual(r_apply.json()["mode"], "standard")
        self.assertFalse(r_apply.json()["needs_prompt"])
        for d in ("01_TAI_LIEU", "02_KURO_XU_LY", "03_KET_QUA"):
            self.assertTrue((ws / d).is_dir(), f"Thiếu thư mục {d}")

        prompt_block = workspace_rules.build_workspace_rules_prompt(ws, engine.get_workspaces_config())
        self.assertIn("01_TAI_LIEU", prompt_block)
        self.assertIn("02_KURO_XU_LY", prompt_block)
        self.assertIn("03_KET_QUA", prompt_block)
        self.assertIn("TASK_001_", prompt_block)
        self.assertIn("7 QUY TẮC LÀM VIỆC", prompt_block)

        # 3. Lưu thêm QUY_TAC_RIENG.md -> tự chuyển sang standard+custom và bơm vào prompt
        r_custom = self.client.post("/api/workspaces/rules", json={
            "mode": "keep",
            "custom_content": "- Xuất thuyết minh theo TCVN 11823:2017\n- Bảng Excel dùng font Times New Roman",
        })
        self.assertEqual(r_custom.status_code, 200)
        self.assertEqual(r_custom.json()["mode"], "standard+custom")
        self.assertTrue((ws / "QUY_TAC_RIENG.md").is_file())
        prompt_block2 = workspace_rules.build_workspace_rules_prompt(ws, engine.get_workspaces_config())
        self.assertIn("TCVN 11823:2017", prompt_block2)

    def test_existing_custom_rules_used_immediately_without_prompt(self):
        ws = self.tmp / "DU_AN_DA_CO_QUY_TAC"
        ws.mkdir()
        (ws / "QUY_TAC_RIENG.md").write_text("# Quy tắc riêng\n- Lưu hết vào thư mục BaoCao/\n", encoding="utf-8")

        r_open = self.client.post("/api/workspaces/open", json={"path": str(ws)})
        self.assertEqual(r_open.status_code, 200)
        rules = r_open.json()["rules"]
        self.assertEqual(rules["mode"], "custom")
        self.assertFalse(rules["needs_prompt"])
        self.assertTrue(rules["has_custom_rules"])

    def test_existing_three_dirs_detected_as_standard(self):
        ws = self.tmp / "DU_AN_DA_CO_3_THU_MUC"
        for d in ("01_TAI_LIEU", "02_KURO_XU_LY", "03_KET_QUA"):
            (ws / d).mkdir(parents=True)

        r_open = self.client.post("/api/workspaces/open", json={"path": str(ws)})
        rules = r_open.json()["rules"]
        self.assertEqual(rules["mode"], "standard")
        self.assertFalse(rules["needs_prompt"])

    def test_decline_rules_remembered_no_repeat_prompt(self):
        ws = self.tmp / "DU_AN_KHONG_AP_DUNG"
        ws.mkdir()
        self.client.post("/api/workspaces/open", json={"path": str(ws)})
        r_no = self.client.post("/api/workspaces/rules", json={"mode": "none"})
        self.assertEqual(r_no.json()["mode"], "none")
        self.assertFalse(r_no.json()["needs_prompt"])
        self.assertFalse((ws / "01_TAI_LIEU").exists())

        # Mở lại dự án đó -> không hỏi lại nữa
        r_reopen = self.client.post("/api/workspaces/open", json={"path": str(ws)})
        self.assertFalse(r_reopen.json()["rules"]["needs_prompt"])


if __name__ == "__main__":
    unittest.main()
