"""Kuro OS - server. Chạy: .venv\\Scripts\\python server\\main.py"""
import asyncio
import os
import re
import shutil
from contextlib import asynccontextmanager
from urllib.parse import urlparse

import uvicorn
from fastapi import Depends, FastAPI, HTTPException, Request, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles

import cli_engines
import config
import engine
import scheduler
import store
import telegram
import update


@asynccontextmanager
async def lifespan(app):
    config.ensure_dirs()
    store.init()
    tasks = [asyncio.create_task(scheduler.loop(telegram.notify if config.TG_TOKEN else None))]
    if config.TG_TOKEN:
        tasks.append(asyncio.create_task(telegram.loop()))
    tasks.append(asyncio.create_task(update.loop(telegram.notify if config.TG_TOKEN else None)))
    yield
    for t in tasks:
        t.cancel()


app = FastAPI(lifespan=lifespan)


@app.get("/health")
def health():
    return {"ok": True, "brain": str(config.BRAIN)}


LOCAL = {"127.0.0.1", "localhost", "::1"}


def is_local(headers) -> bool:
    """Chỉ nhận yêu cầu từ chính trang Kuro: chặn trang web lạ gọi vào qua trình duyệt (CSRF, DNS rebinding)."""
    origin = headers.get("origin")
    return urlparse("//" + (headers.get("host") or "")).hostname in LOCAL and         (not origin or urlparse(origin).hostname in LOCAL)


def local_only(req: Request) -> None:
    if not is_local(req.headers):
        raise HTTPException(403, "Chỉ mở được từ máy này")


@app.get("/api/settings", dependencies=[Depends(local_only)])
def get_settings():
    out = {}
    for k, (secret, _) in config.SETTINGS.items():
        v = os.getenv(k, "")
        out[k] = {"set": bool(v), "hint": "…" + v[-4:] if v else ""} if secret else {"value": v}
    out["KURO_MODEL"] = {"value": config.MODEL}     # model của AI đang chọn, không phải khóa chung cũ
    return {"settings": out, "providers": config.PROVIDERS, "claude_cli": bool(shutil.which("claude")),
            "model_theo_ai": {p: os.getenv(config.model_key(p), "") for p in config.PROVIDERS},
            "cli": {k: bool(cli_engines.find(k)) for k in ("codex", "agy")},
            "telegram_on": bool(config.TG_TOKEN)}


@app.post("/api/settings", dependencies=[Depends(local_only)])
async def save_settings(body: dict[str, str]):
    updates = {}
    for k, v in body.items():
        if k not in config.SETTINGS:
            raise HTTPException(400, f"Không sửa được {k}")
        v = v.strip().replace(" ", "") if k in ("KURO_ALLOWED_TOOLS", "TELEGRAM_OWNER_IDS") else v.strip()
        if not re.fullmatch(config.SETTINGS[k][1], v):     # cũng chặn xuống dòng chèn thêm khóa lạ vào .env
            raise HTTPException(400, f"Giá trị {k} không hợp lệ")
        updates[k] = v
    if "KURO_MODEL" in updates:
        # Model luôn ghi vào khóa của AI đích (AI vừa chọn trong cùng lần lưu, không thì AI đang dùng): specs/001
        provider = updates.get("KURO_PROVIDER", config.PROVIDER)
        model = updates.pop("KURO_MODEL")
        agy = await cli_engines.models("agy") if provider == "antigravity" and model else []
        if err := config.model_error(provider, model, agy):
            raise HTTPException(400, err)
        model = next((m["id"] for m in agy if m["id"].lower() == model.lower()), model)   # lưu đúng cách viết
        updates[config.model_key(provider)] = model
    old_tg = (config.TG_TOKEN, config.TG_OWNERS)
    config.save_env(updates)
    # Model, tool, API key có hiệu lực từ lượt chat kế tiếp; vòng Telegram chỉ khởi tạo lúc server lên.
    return {"ok": True, "restart": (config.TG_TOKEN, config.TG_OWNERS) != old_tg}


@app.get("/api/models", dependencies=[Depends(local_only)])
async def get_models():
    kind = engine.cli_kind()
    found = config.CLAUDE_MODELS if config.PROVIDER in ("", "claude") else await cli_engines.models(kind) if kind else []
    return {"models": found, "current": config.MODEL}


@app.post("/api/test-ai", dependencies=[Depends(local_only)])
async def test_ai():
    return await engine.ping()


@app.get("/api/update")
def get_update():
    return update.STATUS


@app.get("/api/agents")
def get_agents():
    return engine.list_agents_info()


@app.post("/api/agents")
def create_agent(body: dict):
    name = (body.get("name") or "").strip()
    slug = (body.get("slug") or "").strip().lower()
    if not slug:
        import re
        slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    if not slug:
        raise HTTPException(400, "Tên hoặc mã agent không hợp lệ")
    role = (body.get("role") or "").strip()
    group = (body.get("group") or "Chuyên môn").strip()
    prompt = (body.get("prompt") or "").strip() or f"Bạn là {name}, chuyên trách {role}."
    skills = body.get("skills") or []
    from datetime import datetime
    content = f"""---
type: agent
name: {name}
slug: {slug}
role: {role}
group: {group}
skills: {skills}
model: ""
updated: {datetime.now():%Y-%m-%d}
---
{prompt}
"""
    for d in (config.ROOT / "agents", config.BRAIN / "agents"):
        d.mkdir(parents=True, exist_ok=True)
        (d / f"{slug}.md").write_text(content, encoding="utf-8")
    return {"ok": True, "slug": slug, "name": name}


@app.get("/api/sessions")
def list_sessions(agent: str | None = None):
    return store.sessions(agent=agent)


@app.post("/api/sessions")
def create_session(body: dict):
    agent = body.get("agent") or "kuro-core"
    title = body.get("title") or "Phiên mới"
    sid = store.ensure(None, title=title, agent=agent)
    return {"id": sid, "agent": agent, "title": title}


@app.delete("/api/sessions/{sid}")
def delete_session(sid: str):
    store.delete_session(sid)
    return {"ok": True}


@app.get("/api/sessions/{sid}")
def get_messages(sid: str):
    return store.messages(sid)


@app.websocket("/ws")
async def ws(sock: WebSocket):
    # shortcut: không có đăng nhập vì chỉ nghe 127.0.0.1; trước khi mở ra mạng phải thêm đăng nhập (KE-HOACH.md mục 8)
    if not is_local(sock.headers):
        await sock.close(code=1008)
        return
    await sock.accept()
    try:
        while True:
            req = await sock.receive_json()                  # {"session": id hoặc null, "text": "...", "agent": slug}
            text = (req.get("text") or "").strip()
            if not text:
                continue
            agent = req.get("agent") or "kuro-core"
            sid = store.ensure(req.get("session"), title=text, agent=agent)
            await sock.send_json({"type": "session", "id": sid, "agent": agent})
            await engine.chat(sid, text, agent=agent, emit=sock.send_json)
    except WebSocketDisconnect:
        pass


app.mount("/", StaticFiles(directory=config.ROOT / "dashboard", html=True), name="ui")

if __name__ == "__main__":
    uvicorn.run(app, host=config.HOST, port=config.PORT)
