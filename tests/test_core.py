"""Chạy: .venv\\Scripts\\python -m unittest discover -s tests"""
import json
import os
import re
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
        (root / ".env").write_text("# ghi chú\nKURO_MODEL_CLAUDE=\nKURO_PORT=7788\n", encoding="utf-8")
        config.ROOT = root
        try:
            config.save_env({"KURO_PROVIDER": "claude", "KURO_MODEL_CLAUDE": "opus", "TELEGRAM_OWNER_IDS": "12,34"})
            self.assertEqual((root / ".env").read_text(encoding="utf-8"),
                             "# ghi chú\nKURO_MODEL_CLAUDE=opus\nKURO_PORT=7788\nKURO_PROVIDER=claude\n"
                             "TELEGRAM_OWNER_IDS=12,34\n")
            self.assertEqual((config.MODEL, config.TG_OWNERS), ("opus", {12, 34}))
        finally:
            config.ROOT = keep[0]
            os.environ.clear()
            os.environ.update(keep[1])
            config.load_runtime()


class ModelPerAI(unittest.TestCase):
    """specs/001: mỗi AI nhớ model riêng, chặn tên sai, chuyển đổi bản cũ, báo khi đổi AI giữa phiên."""

    def setUp(self):
        self.root, self.keep = Path(tempfile.mkdtemp()), (config.ROOT, dict(os.environ))
        (self.root / ".env").write_text("", encoding="utf-8")
        config.ROOT = self.root
        for k in [k for k in os.environ if k.startswith("KURO_MODEL") or k == "KURO_PROVIDER"]:
            del os.environ[k]   # không để .env thật của máy chạy test lọt vào
        config.load_runtime()

    def tearDown(self):
        config.ROOT = self.keep[0]
        os.environ.clear()
        os.environ.update(self.keep[1])
        config.load_runtime()

    def test_switch_keeps_each_model(self):
        config.save_env({"KURO_PROVIDER": "antigravity", "KURO_MODEL_ANTIGRAVITY": "gemini-3.8-flash-medium"})
        self.assertEqual(config.MODEL, "gemini-3.8-flash-medium")
        config.save_env({"KURO_PROVIDER": "claude"})
        self.assertEqual(config.MODEL, "")                                   # lỗi gốc: không mang model Gemini sang
        config.save_env({"KURO_MODEL_CLAUDE": "sonnet", "KURO_PROVIDER": "antigravity"})
        self.assertEqual(config.MODEL, "gemini-3.8-flash-medium")            # quay lại vẫn còn

    def test_model_error(self):
        agy = [{"id": "gemini-3.8-flash-medium", "ten": "x"}, {"id": "claude-sonnet-5-5-low", "ten": "y"}]
        self.assertEqual(config.model_error("claude", "sonnet", []), "")
        self.assertEqual(config.model_error("", "claude-opus-5-5", []), "")
        self.assertIn("sonnet", config.model_error("claude", "gemini-3.8-flash-medium", []))
        self.assertEqual(config.model_error("antigravity", "gemini-3.8-flash-medium", agy), "")
        self.assertIn("gemini-3.8-flash-medium", config.model_error("antigravity", "gemini-3.8-flash-hi", agy))
        self.assertEqual(config.model_error("antigravity", "gemini-3.8-Flash-medium", agy), "")   # agy không phân biệt hoa
        self.assertEqual(config.model_error("antigravity", "bat-ky", []), "")    # chưa lấy được danh sách: không chặn
        self.assertEqual(config.model_error("deepseek", "bat-ky", agy), "")      # AI không có danh sách: không chặn

    def test_migrate_old_model(self):
        config.save_env({"KURO_PROVIDER": "claude", "KURO_MODEL": "gemini-3.8-flash-medium"})
        config.migrate_model()
        self.assertEqual((os.getenv("KURO_MODEL"), config.MODEL), ("", ""))  # không hợp lệ với Claude: bỏ
        config.save_env({"KURO_MODEL": "opus"})
        config.migrate_model()
        self.assertEqual((os.getenv("KURO_MODEL"), config.MODEL), ("", "opus"))

    def test_conversation_prefix_and_notice(self):
        import asyncio
        import engine
        seen = []

        async def fake(prompt, resume, cur, **_):   # bản 1.5.x thêm agent/cwd/model
            seen.append(resume)
            yield {"type": "final", "text": "", "claude_id": "moi"}

        async def collect(stored):
            return [e async for e in engine.run_turn("hỏi", stored)]

        keep_turn, engine._engine_turn = engine._engine_turn, fake
        try:
            config.save_env({"KURO_PROVIDER": "claude"})
            out = asyncio.run(collect("antigravity:cu"))
            self.assertIn("AI mới chưa biết", out[0]["text"])                # khác AI: báo một dòng
            self.assertEqual((seen[-1], out[-1]["claude_id"]), (None, "claude:moi"))
            out = asyncio.run(collect("abc"))                                 # mã trần bản cũ = claude: nối tiếp
            self.assertEqual((len(out), seen[-1]), (1, "abc"))
            self.assertEqual(engine.split_conv("agy:x"), ("antigravity", "x"))
        finally:
            engine._engine_turn = keep_turn


class TietKiem(unittest.TestCase):
    def test_system_prompt_khong_co_gio(self):
        """Giờ đổi mỗi phút mà nằm trong system prompt thì prompt cache hỏng mỗi lượt."""
        import engine
        with tempfile.TemporaryDirectory() as d:
            o = engine.options(None, cwd=d, provider="claude")
        self.assertNotIn("Bây giờ là", o.system_prompt["append"])
        self.assertEqual((o.skills, "Skill" in o.tools), ([], False))           # dự án không có .claude/skills
        self.assertIn("strict-mcp-config", o.extra_args)                       # không kéo kết nối claude.ai (~72k token)

    def test_hoi_thoai_qua_nang_thi_mo_moi(self):
        """Lần gọi trước quá ngưỡng: không resume hội thoại cũ, bàn giao tin gần nhất, báo cho người dùng."""
        import asyncio
        import engine
        seen = {}

        async def fake(prompt, resume, cur, **_):
            seen.update(prompt=prompt, resume=resume)
            yield {"type": "final", "text": "ok"}

        keep = engine._engine_turn
        engine._engine_turn = fake
        try:
            async def chay():
                return [ev async for ev in engine.run_turn(
                    "câu mới", "claude:cu", provider="claude", conv_ids={"claude": "cu"},
                    handoff_messages=[{"role": "user", "text": "câu cũ"}], lam_moi=150000)]
            evs = asyncio.run(chay())
        finally:
            engine._engine_turn = keep
        self.assertIsNone(seen["resume"])
        self.assertTrue(seen["prompt"].endswith("câu mới"))
        self.assertIn("150,000", evs[0]["text"])

    def test_cli_quy_tac_chi_gui_khi_doi(self):
        import engine
        with tempfile.TemporaryDirectory() as d:
            self.assertIn("<huong_dan_kuro>", engine.cli_prompt("câu 2", False, ws_dir=d, key="hoi-thoai-x"))
            lan_sau = engine.cli_prompt("câu 3", False, ws_dir=d, key="hoi-thoai-x")
        self.assertNotIn("<huong_dan_kuro>", lan_sau)
        self.assertIn("câu 3", lan_sau)

    def test_context_mode_chi_mo_chay_ma_khi_bat_bash(self):
        from unittest import mock
        import tiet_kiem
        with tempfile.TemporaryDirectory() as d:
            srv = Path(d) / "server.mjs"
            srv.write_text("", encoding="utf-8")
            try:
                with mock.patch.dict(os.environ, {"KURO_CONTEXT_MODE": str(srv)}), \
                        mock.patch.object(tiet_kiem, "_node_du_moi", lambda: True):
                    tiet_kiem.context_mode.cache_clear()
                    doc = " ".join(tiet_kiem.codex_args(shell=False))
                    self.assertIn("ctx_search", doc)
                    self.assertNotIn("ctx_execute", doc)
                    self.assertIn("ctx_execute", " ".join(tiet_kiem.codex_args(shell=True)))
                    self.assertEqual(tiet_kiem.mcp_claude(False)[1][0], "mcp__context-mode__ctx_index")
                with mock.patch.dict(os.environ, {"KURO_CONTEXT_MODE": "0"}):
                    tiet_kiem.context_mode.cache_clear()
                    self.assertEqual(tiet_kiem.codex_args(shell=True), [])
            finally:
                tiet_kiem.context_mode.cache_clear()


class TokenStats(unittest.TestCase):
    def test_tach_nguon_va_khong_dem_trung(self):
        import datetime as dt
        import token_stats
        now = dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z")
        u = {"input_tokens": 10, "cache_creation_input_tokens": 1000, "cache_read_input_tokens": 50000, "output_tokens": 200}
        with tempfile.TemporaryDirectory() as d:
            home = Path(d)
            for ep, ten in (("sdk-py", "kuro"), ("claude-desktop", "desk")):
                p = home / ".claude" / "projects" / ten
                p.mkdir(parents=True)
                dong = json.dumps({"type": "assistant", "entrypoint": ep, "timestamp": now,
                                   "message": {"id": "m1", "usage": u, "content": []}})
                (p / "s.jsonl").write_text(dong + "\n" + dong + "\n", encoding="utf-8")   # một lần gọi, hai dòng
            c = home / ".codex" / "sessions" / "2026"
            c.mkdir(parents=True)
            (c / "r.jsonl").write_text(
                json.dumps({"payload": {"originator": "codex_exec", "cwd": "E:/du-an"}}) + "\n"
                + json.dumps({"timestamp": now, "type": "event_msg", "payload": {"type": "token_count", "info": {
                    "last_token_usage": {"input_tokens": 3000, "cached_input_tokens": 2000, "output_tokens": 10}}}}) + "\n",
                encoding="utf-8")
            r = token_stats.thong_ke(1, home=home)
        mot_lan = token_stats.quy_doi(10, 1000, 50000, 200)
        self.assertEqual(r["nguon"]["Kuro (Claude)"]["goi"], 1)
        self.assertEqual(r["nguon"]["Kuro (Claude)"]["quy_doi"], round(mot_lan))
        self.assertIn("Claude Desktop", r["nguon"])
        self.assertEqual(r["nguon"]["Kuro (Codex)"]["moi"], 1000)                 # input 3000 gồm 2000 đọc lại
        self.assertEqual(r["phien"][0]["max_ctx"], 51010)
        self.assertEqual(r["nguon"]["Kuro (Claude)"]["tiet_kiem"], round(0.9 * 50000 - 0.25 * 1000))


class DocPdf(unittest.TestCase):
    def test_mo_san_pdf(self):
        """PDF thả vào chat hoặc dán đường dẫn có dấu cách: Kuro xuất ảnh từng trang và chữ cho AI."""
        import pypdfium2 as pdfium
        import doc_pdf
        self.assertEqual(doc_pdf.doi_tcvn3("mÆt c¾t chi tiÕt ®Þnh h×nh"), "mặt cắt chi tiết định hình")
        self.assertEqual(doc_pdf.doi_tcvn3("Ø16 a200 ø20 300×300"), "Ø16 a200 ø20 300×300")   # ký hiệu giữ nguyên
        self.assertEqual(doc_pdf.doi_tcvn3("cét H300 KIÓM TRA DANH MôC"), "cột H300 KIỂM TRA DANH MỤC")
        self.assertEqual(doc_pdf.doi_tcvn3("hä vµ tªn DỰ ÁN vËt t￾"), "họ và tên DỰ ÁN vật tư ")
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "II. BAN VE TRU P31.pdf"
            pdf = pdfium.PdfDocument.new()
            pdf.new_page(842, 595)
            pdf.new_page(842, 595)
            pdf.save(str(p))
            pdf.close()
            self.assertEqual(doc_pdf.tim_pdf(f'"{p}" đọc bản vẽ'), [p])
            self.assertEqual(doc_pdf.tim_pdf(f"xem C:\\khong-co và\n[Tệp đính kèm: {p}]"), [p])
            self.assertEqual(doc_pdf.tim_pdf("không có tệp nào"), [])
            ws = Path(d) / "du-an"
            ws.mkdir()
            out = doc_pdf.khoi(f"bóc khối lượng {p}", ws)
            self.assertIn("2 trang", out)
            anh = list(ws.rglob("trang_*.png"))
            self.assertEqual(len(anh), 2)
            self.assertEqual(doc_pdf.khoi(str(p), ws), out)                       # lần 2 dùng lại ảnh đã xuất


class Origin(unittest.TestCase):
    def test_validation_and_origin(self):
        import re
        import main
        rx = dict((k, v[1]) for k, v in config.SETTINGS.items())
        self.assertFalse(re.fullmatch(rx["KURO_MODEL"], "opus\nKURO_HOST=0.0.0.0"))   # không chèn được khóa lạ
        self.assertTrue(re.fullmatch(rx["TELEGRAM_BOT_TOKEN"], "123456:AAH-x_y"))
        self.assertTrue(main.is_local({"host": "127.0.0.1:7788", "origin": "http://127.0.0.1:7788"}))
        self.assertFalse(main.is_local({"host": "127.0.0.1:7788", "origin": "https://evil.example"}))
        self.assertFalse(main.is_local({"host": "evil.example:7788"}))                 # DNS rebinding

    def test_ghep_dien_thoai(self):
        """Máy khác trong mạng bị chặn; quét QR (mã ghép) thì vào được; điện thoại đã ghép vẫn không mở được cài đặt."""
        from starlette.testclient import TestClient
        import main
        url = "http://192.168.1.5:7788"
        la = TestClient(main.app, base_url=url, client=("192.168.1.20", 5000), follow_redirects=False)
        self.assertEqual(la.get("/").status_code, 401)
        self.assertEqual(la.get("/api/sessions").status_code, 401)
        self.assertEqual(la.get("/?t=doan-bua").status_code, 401)
        r = la.get(f"/?t={config.remote_token()}")
        self.assertEqual((r.status_code, r.headers["location"]), (303, url + "/"))      # mã không nằm lại trên địa chỉ
        self.assertNotEqual(la.get("/").status_code, 401)                               # cookie từ QR
        self.assertEqual(la.get("/api/settings").status_code, 403)
        nha = TestClient(main.app, base_url="http://127.0.0.1:7788", client=("127.0.0.1", 5000))
        self.assertEqual(nha.get("/api/settings").status_code, 200)

    def test_chan_trang_la(self):
        """Trang lạ mở trong trình duyệt của chính máy này không gửi lệnh được vào Kuro (CSRF, DNS rebinding)."""
        from starlette.testclient import TestClient
        import main
        # Origin trong mạng riêng nhưng khác gốc: trước đây lọt qua is_local
        for o in ("http://evil.ts.net", "http://192.168.1.9:7788", "http://127.0.0.1:8080", "null"):
            self.assertFalse(main.is_local({"host": "127.0.0.1:7788", "origin": o}), o)
        self.assertTrue(main.is_local({"host": "100.101.1.2:7788", "origin": "http://100.101.1.2:7788"}))
        nha = TestClient(main.app, base_url="http://127.0.0.1:7788", client=("127.0.0.1", 5000))
        r = nha.post("/api/agents/upload", headers={"origin": "https://evil.example"}, files={"file": ("a.md", b"x")})
        self.assertEqual(r.status_code, 403)                                            # tải tệp chéo trang
        self.assertEqual(nha.post("/api/khong-co", headers={"origin": "http://evil.ts.net"}).status_code, 403)
        self.assertNotEqual(nha.post("/api/khong-co", headers={"origin": "http://127.0.0.1:7788"}).status_code, 403)
        self.assertEqual(nha.get("/api/sessions", headers={"host": "evil.example:7788"}).status_code, 421)


class Providers(unittest.TestCase):
    def setUp(self):
        self.keep = (config.PROVIDER, config.AI_KEY, config.BASE_URL, config.MODEL)

    def tearDown(self):
        config.PROVIDER, config.AI_KEY, config.BASE_URL, config.MODEL = self.keep

    def test_env_per_provider(self):
        config.PROVIDER, config.AI_KEY, config.BASE_URL, config.MODEL = "claude", "", "", ""
        self.assertEqual(config.provider_env(), {})                                     # dùng đăng nhập Claude
        config.PROVIDER, config.AI_KEY = "anthropic", "sk-ant-x"
        self.assertEqual(config.provider_env(), {"ANTHROPIC_API_KEY": "sk-ant-x"})
        config.PROVIDER, config.AI_KEY, config.MODEL = "deepseek", "k1", "m1"
        env = config.provider_env()
        self.assertEqual((env["ANTHROPIC_BASE_URL"], env["ANTHROPIC_AUTH_TOKEN"], env["ANTHROPIC_API_KEY"]),
                         ("https://api.deepseek.com/anthropic", "k1", ""))
        self.assertEqual(env["CLAUDE_CODE_SUBAGENT_MODEL"], "m1")                      # agent con cũng dùng model hãng đó
        config.PROVIDER, config.AI_KEY, config.BASE_URL = "ollama", "", "http://192.168.1.5:11434"
        self.assertEqual(config.provider_env()["ANTHROPIC_BASE_URL"], "http://192.168.1.5:11434")
        self.assertTrue(all(re.fullmatch(config.SETTINGS["KURO_PROVIDER"][1], p) for p in config.PROVIDERS))


class CliEngines(unittest.TestCase):
    """Sự kiện mẫu chép từ đầu ra thật của codex-cli 0.156.1 và agy 1.3.3 (31/10/2026)."""

    def run_parse(self, parse, events):
        import cli_engines  # noqa: F401
        st = {"id": None, "text": False, "error": "", "tools": set(), "notes": [], "usage": None, "init_tools": []}
        out = [o for e in events for o in parse(e, st)]
        return st, out

    def test_codex(self):
        import cli_engines
        st, out = self.run_parse(cli_engines._codex_event, [
            {"type": "thread.started", "thread_id": "t1"},
            {"type": "item.started", "item": {"type": "command_execution"}},
            {"type": "item.completed", "item": {"type": "agent_message", "text": "OK"}}])
        self.assertEqual((st["id"], [o["type"] for o in out], out[-1]["text"]), ("t1", ["tool", "text"], "OK"))

    def test_agy_denied_is_not_silent(self):
        import cli_engines
        st, out = self.run_parse(cli_engines._agy_event, [
            {"event": "init", "conversation_id": "c1"},
            {"event": "step_update", "step_update": {"step_index": 2, "state": "ACTIVE", "step_type": "tool",
                                                     "tool_name": "write_file"}},
            {"event": "result", "result": {"status": "SUCCESS", "response": "",
                                           "denied_actions": [{"action": "write_file", "display_name": "WriteFile"}]}}])
        self.assertEqual(st["id"], "c1")
        self.assertIn("WriteFile", st["error"])        # agy dừng vì bị chặn: phải báo, không trả bong bóng rỗng

    def test_agy_text(self):
        import cli_engines
        st, out = self.run_parse(cli_engines._agy_event, [
            {"event": "step_update", "step_update": {"step_type": "agent_response", "text_delta": "OK"}},
            {"event": "result", "result": {"status": "SUCCESS", "response": "OK\n"}}])
        self.assertEqual(([o["text"] for o in out], st["error"]), (["OK"], ""))   # không lặp lại response


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


class Kho(unittest.TestCase):
    """specs/002: tìm, đọc, chỉ chạy mã đã duyệt, đồng bộ giữ mã đã duyệt."""

    def test_tim_doc_that(self):
        import kho
        kq = kho.tim("ifc quantity takeoff")
        self.assertTrue(kq and kq[0]["repo"] == "ddc")                        # kho thật trong repo
        self.assertIn("[Kuro] Skill", kho.doc(kq[0]["id"]))
        with self.assertRaises(ValueError):
            kho.doc(kq[0]["id"], "../../../.env")                           # không thoát ra ngoài skill

    def test_chi_chay_ma_da_duyet(self):
        import kho
        tmp = Path(tempfile.mkdtemp())
        keep = (config.ROOT, config.STATE, kho.MUC_LUC, kho.SO_GOC)
        d = tmp / "kho" / "t" / "s"
        d.mkdir(parents=True)
        (d / "SKILL.md").write_text("---\nname: s\n---\n", encoding="utf-8")
        (d / "run.py").write_text("print('xin chao')", encoding="utf-8")
        (tmp / "state").mkdir()
        ml = tmp / "kho" / "muc-luc.json"
        ml.write_text(json.dumps({"nguon": [], "skill": [{"id": "t/s", "ten": "s", "mo_ta": "", "repo": "t",
                                                          "duong_dan": "kho/t/s", "co_ma": True}]}), encoding="utf-8")
        config.ROOT, config.STATE, kho.MUC_LUC, kho.SO_GOC = tmp, tmp / "state", ml, tmp / "kho" / "da-duyet.json"
        try:
            self.assertIn("[CHẶN]", kho.chay("t/s", "run.py", [], tmp))     # chưa duyệt
            kho.duyet("t/s")
            self.assertIn("xin chao", kho.chay("t/s", "run.py", [], tmp))   # đã duyệt
            (d / "run.py").write_text("print('da sua')", encoding="utf-8")
            self.assertIn("[CHẶN]", kho.chay("t/s", "run.py", [], tmp))     # sửa sau khi duyệt: chặn lại
            self.assertIn("[CHẶN]", kho.chay("t/s", "../../../x.py", [], tmp))
        finally:
            config.ROOT, config.STATE, kho.MUC_LUC, kho.SO_GOC = keep

    def test_dong_bo_giu_ma_da_duyet(self):
        import kho
        sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
        import dong_bo_kho
        tmp = Path(tempfile.mkdtemp())
        keep = kho.KHO
        kho.KHO = tmp / "kho"
        try:
            cu, moi = tmp / "cu" / "a", tmp / "moi" / "a"
            for root, code, doc in ((cu, "print(1)", "cu"), (moi, "print(2)", "moi")):
                root.mkdir(parents=True)
                (root / "SKILL.md").write_text(doc, encoding="utf-8")
                (root / "x.py").write_text(code, encoding="utf-8")
            so = {"r/a": {"van_tay": kho.van_tay_goi(cu)}}
            giu = dong_bo_kho.giu_ma_da_duyet("r", tmp / "moi", tmp / "cu", so)
            self.assertEqual(giu, ["r/a"])
            self.assertEqual((moi / "x.py").read_text(), "print(1)")           # mã cũ đã duyệt vẫn chạy
            self.assertEqual((moi / "SKILL.md").read_text(), "moi")             # chữ dùng bản mới
            self.assertEqual((kho.KHO / "_cho-duyet" / "r" / "a" / "x.py").read_text(), "print(2)")
        finally:
            kho.KHO = keep


class Lich(unittest.TestCase):
    def setUp(self):
        import scheduler
        self.keep = config.REMINDERS_FILE
        config.REMINDERS_FILE = Path(tempfile.mkdtemp()) / "reminders.json"
        self.s = scheduler

    def tearDown(self):
        config.REMINDERS_FILE = self.keep

    def test_mac_dinh_khong_ghi_de(self):
        self.s.save([{"id": "bao-cao-tuan", "cron": "0 8 * * 1", "prompt": "của tôi", "enabled": False}])
        viec = {v["id"]: v for v in self.s.ensure_defaults()}
        self.assertEqual(set(viec), {"bao-cao-tuan", "soat-ho-so", "kiem-tra-kho"})
        self.assertEqual((viec["bao-cao-tuan"]["enabled"], viec["bao-cao-tuan"]["prompt"]), (False, "của tôi"))

    def test_soat_khong_co_tep_moi_thi_khong_goi_ai(self):
        import asyncio
        import time
        import engine
        goc = Path(tempfile.mkdtemp())
        (goc / "cu.docx").write_text("x")
        (config.STATE / "soat-ho-so.json").write_text(json.dumps({"lan_truoc": time.time() + 60}))

        async def khong_duoc_goi(*a, **k):
            raise AssertionError("không được gọi AI khi không có tệp mới")
        keep = (engine.chat, engine.active_workspace_dir)
        engine.chat, engine.active_workspace_dir = khong_duoc_goi, lambda: goc
        try:
            config.ensure_dirs()
            store.init()
            self.assertIn("Không có gì mới", asyncio.run(self.s.run_job(next(
                v for v in self.s.MAC_DINH if v["id"] == "soat-ho-so"))))
            self.assertEqual(self.s.tep_moi(goc, time.time() - 3600), ["cu.docx"])
        finally:
            engine.chat, engine.active_workspace_dir = keep


class DienHoa(unittest.TestCase):
    """specs/003: nhận yêu cầu diễn hoạ, kích thước SDXL, quy trình ComfyUI nối đúng nút."""

    def test_yeu_cau(self):
        import dien_hoa
        j = dien_hoa.yeu_cau("Diễn hoạ thành nhà phố 3 tầng [Tệp đính kèm: E:/da/mat-dung.png]")
        self.assertEqual((j["che_do"], j["anh"].name, j["mo_ta"]), ("net", "mat-dung.png", "Diễn hoạ thành nhà phố 3 tầng"))
        self.assertEqual(dien_hoa.yeu_cau("diễn họa ảnh hiện trạng [Tệp đính kèm: a.jpg]")["che_do"], "anh")
        self.assertEqual(dien_hoa.yeu_cau("render mô hình Revit [Hình ảnh đính kèm: a.png]")["che_do"], "3d")
        self.assertIsNone(dien_hoa.yeu_cau("diễn hoạ giúp mình"))                           # không có ảnh
        self.assertIsNone(dien_hoa.yeu_cau("xem file [Tệp đính kèm: a.png]"))               # không nhờ diễn hoạ
        self.assertIsNone(dien_hoa.yeu_cau("diễn hoạ [Tệp đính kèm: bang-tinh.xlsx]"))      # không phải ảnh

    def test_kich_thuoc(self):
        import dien_hoa
        for w, h in ((1920, 1080), (800, 2000), (1024, 1024), (300, 300)):
            W, H = dien_hoa.kich_thuoc(w, h)
            self.assertTrue(W % 64 == 0 and H % 64 == 0 and 512 <= W <= 1536 and 512 <= H <= 1536)
            self.assertAlmostEqual(W / H, w / h, delta=0.25 if w != 800 else 0.6)  # giữ gần tỉ lệ gốc

    def test_workflow_noi_dung_nut(self):
        import dien_hoa
        for che_do in dien_hoa.CHE_DO:
            wf = dien_hoa.workflow("a.png", "house", che_do, 1024, 1024, 2, 1)
            for nut in wf.values():
                for v in nut["inputs"].values():
                    if isinstance(v, list):
                        self.assertIn(v[0], wf)                                               # không trỏ tới nút lạ
            self.assertEqual(wf["9"]["inputs"]["batch_size"], 2)

    def test_workflow_khop_comfyui_that(self):
        """Tên nút, tên tham số và giá trị chọn khớp /object_info đo trên bản cài thật (tests/comfyui_object_info.json)."""
        import dien_hoa
        oi = json.loads((Path(__file__).parent / "comfyui_object_info.json").read_text(encoding="utf-8"))
        for che_do in dien_hoa.CHE_DO:
            for id_, nut in dien_hoa.workflow("a.png", "house", che_do, 1024, 1024, 2, 1).items():
                self.assertIn(nut["class_type"], oi, id_)
                cho = oi[nut["class_type"]]
                for ten, v in nut["inputs"].items():
                    self.assertIn(ten, cho, f"{nut['class_type']}.{ten}")
                    if cho[ten] is not None and not isinstance(v, list):
                        self.assertIn(v, cho[ten], f"{nut['class_type']}.{ten}")


if __name__ == "__main__":
    unittest.main()
