"""Chạy: .venv\\Scripts\\python -m unittest discover -s tests"""
import os
import sys
import tempfile
import unittest
from datetime import datetime
from pathlib import Path

TMP = tempfile.mkdtemp()
os.environ["KURO_STATE_DIR"] = TMP
os.environ["KURO_BRAINS_DIR"] = TMP
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "server"))

import config  # noqa: E402
import scheduler  # noqa: E402
import store  # noqa: E402


class Cron(unittest.TestCase):
    def test_monday_7am(self):
        self.assertTrue(scheduler.cron_match("0 7 * * 1", datetime(2026, 11, 2, 7, 0)))   # thứ Hai
        self.assertFalse(scheduler.cron_match("0 7 * * 1", datetime(2026, 11, 3, 7, 0)))  # thứ Ba
        self.assertFalse(scheduler.cron_match("0 7 * * 1", datetime(2026, 11, 2, 7, 1)))

    def test_sunday_0_and_7(self):
        sun = datetime(2026, 11, 1, 9, 0)
        self.assertTrue(scheduler.cron_match("0 9 * * 0", sun))
        self.assertTrue(scheduler.cron_match("0 9 * * 7", sun))

    def test_step_range_list(self):
        self.assertTrue(scheduler.cron_match("*/15 8-17 * * 1-5", datetime(2026, 11, 2, 16, 45)))
        self.assertFalse(scheduler.cron_match("*/15 8-17 * * 1-5", datetime(2026, 11, 2, 18, 0)))
        self.assertTrue(scheduler.cron_match("0 12 1,15 * *", datetime(2026, 11, 15, 12, 0)))

    def test_dom_or_dow(self):
        # cron chuẩn: ngày 1 HOẶC thứ Hai
        self.assertTrue(scheduler.cron_match("0 8 1 * 1", datetime(2026, 11, 2, 8, 0)))
        self.assertTrue(scheduler.cron_match("0 8 1 * 1", datetime(2026, 11, 1, 8, 0)))

    def test_bad(self):
        for bad in ("0 7 * *", "61 * * * *", "0 25 * * *"):
            with self.assertRaises(ValueError):
                scheduler.cron_match(bad, datetime(2026, 11, 2))


class Store(unittest.TestCase):
    def test_roundtrip(self):
        config.ensure_dirs()
        store.init()
        sid = store.ensure(None, "thử")
        store.add(sid, "user", "chào")
        store.set_claude_id(sid, "abc")
        self.assertEqual(store.get(sid)["claude_id"], "abc")
        self.assertEqual([m["text"] for m in store.messages(sid)], ["chào"])
        self.assertEqual(store.ensure(sid, "khác"), sid)          # không tạo trùng
        self.assertTrue(any(s["id"] == sid for s in store.sessions()))


class Agents(unittest.TestCase):
    def test_load(self):
        import engine
        d = config.BRAIN / "agents"
        d.mkdir(parents=True, exist_ok=True)
        (d / "ky-su-qs.md").write_text(
            "---\r\ntype: agent\r\nname: Kỹ sư QS\r\nslug: ky-su-qs\r\nrole: Bóc khối lượng\r\n"
            "skills: [qs-khoi-luong-du-toan]\r\nmodel: \"\"\r\n---\r\nBạn là kỹ sư QS.\r\n---\r\nđoạn sau\r\n",
            encoding="utf-8")
        (d / "hong.md").write_text("---\nname: [chưa đóng\n---\nx", encoding="utf-8")   # YAML hỏng: bỏ qua
        (d / "ghi-chu.md").write_text("không có frontmatter", encoding="utf-8")
        a = engine.load_agents()
        self.assertEqual(list(a), ["ky-su-qs"])
        qs = a["ky-su-qs"]
        self.assertEqual((qs.description, qs.skills, qs.model), ("Bóc khối lượng", ["qs-khoi-luong-du-toan"], None))
        self.assertIn("đoạn sau", qs.prompt)        # dấu --- trong thân bài không cắt mất nội dung


class Calc(unittest.TestCase):
    def setUp(self):
        import calc
        self.calc = calc

    def test_ok_error_timeout(self):
        out = self.calc.run_python("print(2 * 21, 'tiếng Việt')", "thử")
        self.assertTrue(out.startswith("[OK]"))
        self.assertIn("42 tiếng Việt", out)
        self.assertTrue(any((config.BRAIN / "tinh-toan").glob("*.py")))   # script được lưu để truy vết
        self.assertIn("LỖI", self.calc.run_python("raise SystemExit(3)"))
        old, self.calc.TIMEOUT_S = self.calc.TIMEOUT_S, 2
        try:
            self.assertIn("QUÁ 2 GIÂY", self.calc.run_python("import time; time.sleep(10)"))
        finally:
            self.calc.TIMEOUT_S = old

    def test_skill_examples_match_hand_calcs(self):
        """Code mẫu trong skill phải chạy và khớp đáp số tính tay; lệch là skill dạy sai."""
        import re
        md = (config.ROOT / "skills" / "tinh-toan-ky-thuat" / "SKILL.md").read_text(encoding="utf-8")
        blocks = re.findall(r"```python\n(.*?)```", md, re.S)
        self.assertEqual(len(blocks), 4)
        expect = ["20.25 kilonewton * meter", "5400000000", "M_tay=168.9 kNm, M_lib=168.9 kNm", "45.0"]
        for code, want in zip(blocks, expect):
            out = self.calc.run_python(code)
            self.assertTrue(out.startswith("[OK]"), out)
            self.assertIn(want, out)
        self.assertRegex(out, r"1\.04\d")   # độ võng 5qL^4/384EI = 1.042 mm

    def test_default_skill_installed(self):
        config.ensure_dirs()
        self.assertTrue((config.BRAIN / ".claude" / "skills" / "tinh-toan-ky-thuat" / "SKILL.md").is_file())


class Settings(unittest.TestCase):
    def test_save_env_keeps_comments(self):
        root, keep = Path(tempfile.mkdtemp()), (config.ROOT, dict(os.environ))
        (root / ".env").write_text("# ghi chú\nKURO_MODEL=\nKURO_PORT=7788\n", encoding="utf-8")
        config.ROOT = root
        try:
            config.save_env({"KURO_MODEL": "opus", "TELEGRAM_OWNER_IDS": "12,34"})
            self.assertEqual((root / ".env").read_text(encoding="utf-8"),
                             "# ghi chú\nKURO_MODEL=opus\nKURO_PORT=7788\nTELEGRAM_OWNER_IDS=12,34\n")
            self.assertEqual((config.MODEL, config.TG_OWNERS), ("opus", {12, 34}))
        finally:
            config.ROOT = keep[0]
            os.environ.clear()
            os.environ.update(keep[1])
            config.load_runtime()

    def test_validation_and_origin(self):
        import re
        import main
        rx = dict((k, v[1]) for k, v in config.SETTINGS.items())
        self.assertFalse(re.fullmatch(rx["KURO_MODEL"], "opus\nKURO_HOST=0.0.0.0"))   # không chèn được khóa lạ
        self.assertTrue(re.fullmatch(rx["TELEGRAM_BOT_TOKEN"], "123456:AAH-x_y"))
        self.assertTrue(main.is_local({"host": "127.0.0.1:7788", "origin": "http://127.0.0.1:7788"}))
        self.assertFalse(main.is_local({"host": "127.0.0.1:7788", "origin": "https://evil.example"}))
        self.assertFalse(main.is_local({"host": "evil.example:7788"}))                 # DNS rebinding


class Bundled(unittest.TestCase):
    def test_update_but_keep_user_edits(self):
        keep = (config.ROOT, config.BRAIN, config.STATE)
        tmp = Path(tempfile.mkdtemp())
        config.ROOT, config.BRAIN, config.STATE = tmp / "repo", tmp / "brain", tmp / "state"
        src, dst = config.ROOT / "skills" / "a" / "SKILL.md", config.BRAIN / ".claude" / "skills" / "a" / "SKILL.md"
        try:
            src.parent.mkdir(parents=True)
            config.STATE.mkdir()
            src.write_text("v1", encoding="utf-8")
            config.sync_bundled()
            self.assertEqual(dst.read_text(encoding="utf-8"), "v1")                  # cài mới
            src.write_text("v2", encoding="utf-8")
            config.sync_bundled()
            self.assertEqual(dst.read_text(encoding="utf-8"), "v2")                  # chưa sửa: nhận bản mới
            dst.write_text("của tôi", encoding="utf-8")
            src.write_text("v3", encoding="utf-8")
            config.sync_bundled()
            self.assertEqual(dst.read_text(encoding="utf-8"), "của tôi")             # đã sửa: giữ nguyên
        finally:
            config.ROOT, config.BRAIN, config.STATE = keep


class Update(unittest.TestCase):
    def test_detects_new_version(self):
        import subprocess
        import update
        tmp = Path(tempfile.mkdtemp())

        def git(cwd, *a):
            subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", *a], cwd=cwd, check=True,
                           capture_output=True)
        git(tmp, "init", "--bare", "-b", "main", "origin.git")
        git(tmp, "clone", "origin.git", "tac-gia")
        (tmp / "tac-gia" / "VERSION").write_text("1.0.0\n")
        git(tmp / "tac-gia", "add", ".")
        git(tmp / "tac-gia", "commit", "-m", "Bản đầu")
        git(tmp / "tac-gia", "push", "-u", "origin", "main")
        git(tmp, "clone", "origin.git", "nguoi-dung")
        (tmp / "tac-gia" / "VERSION").write_text("1.1.0\n")
        git(tmp / "tac-gia", "commit", "-am", "Thêm skill an toàn")
        git(tmp / "tac-gia", "push")
        keep = config.ROOT
        config.ROOT = tmp / "nguoi-dung"
        try:
            update.check()
            self.assertEqual((update.STATUS["behind"], update.STATUS["latest"], update.STATUS["notes"]),
                             (1, "1.1.0", ["Thêm skill an toàn"]))
        finally:
            config.ROOT = keep


if __name__ == "__main__":
    unittest.main()
