"""Kiểm thử tính năng kết nối đa nhà cung cấp AI & chạy song song theo từng phiên."""
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

import config  # noqa: E402
import engine  # noqa: E402
import main  # noqa: E402
import store  # noqa: E402


class MultiProviderConfig(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp())
        self.keep = (config.ROOT, dict(os.environ))
        (self.root / ".env").write_text("", encoding="utf-8")
        config.ROOT = self.root
        for k in [k for k in os.environ if k.startswith("KURO_")]:
            del os.environ[k]
        config.load_runtime()

    def tearDown(self):
        config.ROOT = self.keep[0]
        os.environ.clear()
        os.environ.update(self.keep[1])
        config.load_runtime()

    def test_isolated_env_per_provider(self):
        config.save_env({
            "KURO_PROVIDER": "antigravity",
            "KURO_ENABLED_PROVIDERS": "antigravity,claude,deepseek,openrouter",
            "KURO_MODEL_ANTIGRAVITY": "gemini-4-neon-high",
            "KURO_MODEL_CLAUDE": "sonnet",
            "KURO_AI_KEY_DEEPSEEK": "sk-ds-123",
            "KURO_MODEL_DEEPSEEK": "deepseek-chat",
            "KURO_AI_KEY_OPENROUTER": "sk-or-999",
            "KURO_MODEL_OPENROUTER": "openai/gpt-5",
        })
        self.assertEqual(config.enabled_providers(), ["antigravity", "claude", "deepseek", "openrouter"])
        self.assertEqual(config.get_provider_model("antigravity"), "gemini-4-neon-high")
        self.assertEqual(config.get_provider_model("claude"), "sonnet")
        self.assertEqual(config.provider_env(provider="claude"), {})
        self.assertEqual(config.provider_env(provider="antigravity"), {})

        ds_env = config.provider_env(provider="deepseek")
        or_env = config.provider_env(provider="openrouter")
        self.assertEqual(ds_env["ANTHROPIC_AUTH_TOKEN"], "sk-ds-123")
        self.assertEqual(ds_env["ANTHROPIC_BASE_URL"], "https://api.deepseek.com/anthropic")
        self.assertEqual(ds_env["ANTHROPIC_MODEL"], "deepseek-chat")
        self.assertEqual(or_env["ANTHROPIC_AUTH_TOKEN"], "sk-or-999")
        self.assertEqual(or_env["ANTHROPIC_BASE_URL"], "https://openrouter.ai/api")
        self.assertEqual(or_env["ANTHROPIC_MODEL"], "openai/gpt-5")

    def test_migrate_legacy_creds(self):
        config.save_env({
            "KURO_PROVIDER": "deepseek",
            "KURO_AI_KEY": "sk-old-ds",
            "KURO_BASE_URL": "https://custom.deepseek.local",
        })
        config.migrate_provider_creds()
        self.assertEqual(os.getenv("KURO_AI_KEY_DEEPSEEK"), "sk-old-ds")
        self.assertEqual(os.getenv("KURO_BASE_URL_DEEPSEEK"), "https://custom.deepseek.local")


class ParallelSessionsAndHandoff(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.keep = (config.STATE, config.BRAIN, config.ROOT, dict(os.environ))
        config.STATE = self.tmp / "state"
        config.BRAIN = self.tmp / "brain"
        config.STATE.mkdir(parents=True, exist_ok=True)
        config.BRAIN.mkdir(parents=True, exist_ok=True)
        store.init()

    def tearDown(self):
        config.STATE, config.BRAIN, config.ROOT = self.keep[0], self.keep[1], self.keep[2]
        os.environ.clear()
        os.environ.update(self.keep[3])
        config.load_runtime()

    def test_parallel_antigravity_and_claude_sessions(self):
        calls = []

        async def fake_engine_turn(prompt, resume, cur, agent="kuro-core", cwd=None, model=None):
            calls.append({"provider": cur, "model": model, "resume": resume, "prompt": prompt})
            # Giả lập độ trễ để chạy xen kẽ thực sự song song
            await asyncio.sleep(0.05 if cur == "antigravity" else 0.02)
            yield {"type": "text", "text": f"OK từ {cur}/{model}"}
            yield {"type": "final", "text": f"OK từ {cur}/{model}", "claude_id": f"cid-{cur}"}

        keep_turn = engine._engine_turn
        engine._engine_turn = fake_engine_turn
        try:
            async def run_both():
                return await asyncio.gather(
                    engine.chat("sess-agy", "Kiểm toán dầm", provider="antigravity", model="gemini-4-neon-high"),
                    engine.chat("sess-claude", "Viết script Python", provider="claude", model="sonnet"),
                )

            ans1, ans2 = asyncio.run(run_both())
            self.assertEqual(ans1, "OK từ antigravity/gemini-4-neon-high")
            self.assertEqual(ans2, "OK từ claude/sonnet")
            self.assertEqual({c["provider"] for c in calls}, {"antigravity", "claude"})

            s1 = store.get("sess-agy")
            s2 = store.get("sess-claude")
            self.assertEqual((s1["provider"], s1["model"]), ("antigravity", "gemini-4-neon-high"))
            self.assertEqual((s2["provider"], s2["model"]), ("claude", "sonnet"))
            self.assertEqual(store.get_conv_ids(s1), {"antigravity": "cid-antigravity"})
            self.assertEqual(store.get_conv_ids(s2), {"claude": "cid-claude"})
        finally:
            engine._engine_turn = keep_turn

    def test_switch_provider_mid_session_handoff_and_return(self):
        calls = []

        async def fake_engine_turn(prompt, resume, cur, agent="kuro-core", cwd=None, model=None):
            calls.append({"provider": cur, "model": model, "resume": resume, "prompt": prompt})
            yield {"type": "text", "text": f"Trả lời bởi {cur}"}
            yield {"type": "final", "text": f"Trả lời bởi {cur}", "claude_id": f"thread-{cur}-{len(calls)}"}

        keep_turn = engine._engine_turn
        engine._engine_turn = fake_engine_turn
        try:
            # Lượt 1: chạy bằng Antigravity
            asyncio.run(engine.chat("sess-mix", "Dự án Cầu Mỹ Thuận nhịp 120m", provider="antigravity", model="gemini-4-neon-high"))
            self.assertEqual(calls[0]["provider"], "antigravity")
            self.assertIsNone(calls[0]["resume"])

            # Lượt 2: chuyển sang Claude trong cùng phiên -> phải bàn giao ngữ cảnh lượt 1 & không mang model Gemini sang
            ans2 = asyncio.run(engine.chat("sess-mix", "Hãy kiểm tra tiếp hệ số tải trọng", provider="claude"))
            self.assertEqual(calls[1]["provider"], "claude")
            self.assertIsNone(calls[1]["model"])
            self.assertIsNone(calls[1]["resume"])
            self.assertIn("<ngu_canh_ban_giao>", calls[1]["prompt"])
            self.assertIn("Cầu Mỹ Thuận", calls[1]["prompt"])
            self.assertIn("đã bàn giao ngữ cảnh", ans2)

            # Lượt 3: quay lại Antigravity -> phải nối đúng resume thread cũ của Antigravity!
            ans3 = asyncio.run(engine.chat("sess-mix", "Tổng hợp kết quả thành bảng", provider="antigravity", model="gemini-4-neon-high"))
            self.assertEqual(calls[2]["provider"], "antigravity")
            self.assertEqual(calls[2]["resume"], "thread-antigravity-1")
            self.assertIn("tiếp nối mạch cũ", ans3)
            self.assertEqual(set(store.get_conv_ids("sess-mix").keys()), {"antigravity", "claude"})
        finally:
            engine._engine_turn = keep_turn


class MultiProviderApi(unittest.TestCase):
    def setUp(self):
        from starlette.testclient import TestClient
        self.tmp = Path(tempfile.mkdtemp())
        self.keep = (config.ROOT, config.STATE, config.BRAIN, dict(os.environ))
        config.ROOT = self.tmp / "repo"
        config.STATE = self.tmp / "state"
        config.BRAIN = self.tmp / "brain"
        config.ROOT.mkdir(parents=True, exist_ok=True)
        config.STATE.mkdir(parents=True, exist_ok=True)
        config.BRAIN.mkdir(parents=True, exist_ok=True)
        (config.ROOT / ".env").write_text("", encoding="utf-8")
        for k in [k for k in os.environ if k.startswith("KURO_")]:
            del os.environ[k]
        config.load_runtime()
        store.init()
        self.client = TestClient(main.app, base_url="http://127.0.0.1:7788", client=("127.0.0.1", 5000))

    def tearDown(self):
        config.ROOT, config.STATE, config.BRAIN = self.keep[0], self.keep[1], self.keep[2]
        os.environ.clear()
        os.environ.update(self.keep[3])
        config.load_runtime()

    def test_settings_models_sessions_quota_and_test_ai(self):
        # 1. Lưu cấu hình bật đồng thời antigravity + claude
        r = self.client.post("/api/settings", json={
            "KURO_PROVIDER": "antigravity",
            "KURO_ENABLED_PROVIDERS": "antigravity,claude",
            "KURO_MODEL_CLAUDE": "sonnet",
        })
        self.assertEqual(r.status_code, 200, r.text)
        self.assertEqual(r.json()["enabled_providers"], ["antigravity", "claude"])

        # 2. Kiểm tra GET /api/settings trả providers_config đầy đủ
        s = self.client.get("/api/settings").json()
        self.assertTrue(s["providers_config"]["antigravity"]["enabled"])
        self.assertTrue(s["providers_config"]["claude"]["enabled"])
        self.assertEqual(s["providers_config"]["claude"]["model"], "sonnet")

        # 3. Kiểm tra GET /api/models?scope=enabled gom nhóm cả 2 hãng
        m = self.client.get("/api/models?scope=enabled").json()
        group_ids = [g["provider"] for g in m["groups"]]
        self.assertEqual(group_ids, ["antigravity", "claude"])
        claude_grp = next(g for g in m["groups"] if g["provider"] == "claude")
        self.assertTrue(any(x["id"] == "sonnet" for x in claude_grp["models"]))

        # 4. Kiểm tra POST /api/sessions/{sid}/model & context window riêng theo provider
        sess_res = self.client.post("/api/sessions", json={"title": "Phiên Claude", "provider": "claude", "model": "sonnet"})
        self.assertEqual(sess_res.status_code, 200)
        sid = sess_res.json()["id"]
        ctx = self.client.get(f"/api/sessions/{sid}/context").json()
        self.assertEqual(ctx["environment"]["provider"], "claude")
        self.assertEqual(ctx["usage"]["window_size"], 200_000)

        self.client.post(f"/api/sessions/{sid}/model", json={"provider": "antigravity", "model": "gemini-3.8-flash-medium"})
        ctx2 = self.client.get(f"/api/sessions/{sid}/context").json()
        self.assertEqual(ctx2["environment"]["provider"], "antigravity")
        self.assertEqual(ctx2["usage"]["window_size"], 1_000_000)

        # 5. Kiểm tra Quota tách riêng theo từng provider
        store.add(sid, "user", "Hỏi trên AGY", provider="antigravity")
        store.add(sid, "user", "Hỏi trên Claude", provider="claude")
        q_cl = self.client.get("/api/quota?provider=claude").json()
        self.assertEqual(q_cl["provider"], "claude")
        self.assertEqual(q_cl["block_5h"]["used_count"], 1)
        self.assertEqual(len(q_cl["by_provider"]), 2)

        # 6. Kiểm tra POST /api/test-ai gọi đúng provider chỉ định
        ping_calls = []

        async def fake_ping(provider=None, model=None):
            ping_calls.append((provider, model))
            return {"ok": True, "text": "OK", "error": "", "provider": provider}

        keep_ping = engine.ping
        engine.ping = fake_ping
        try:
            t_res = self.client.post("/api/test-ai", json={"provider": "claude", "model": "opus"}).json()
            self.assertTrue(t_res["ok"])
            self.assertEqual(ping_calls, [("claude", "opus")])
        finally:
            engine.ping = keep_ping

        # 7. Kiểm tra Agent lưu được provider + model mặc định
        a_res = self.client.post("/api/agents", json={
            "name": "Kỹ sư Code",
            "slug": "ky-su-code",
            "role": "Viết script Python",
            "provider": "claude",
            "model": "sonnet",
        })
        self.assertEqual(a_res.status_code, 200)
        a_detail = self.client.get("/api/agents/ky-su-code").json()
        self.assertEqual((a_detail["provider"], a_detail["model"]), ("claude", "sonnet"))


if __name__ == "__main__":
    unittest.main()
