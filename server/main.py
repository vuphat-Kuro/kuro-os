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
    return {"settings": out, "claude_cli": bool(shutil.which("claude")), "telegram_on": bool(config.TG_TOKEN)}


@app.post("/api/settings", dependencies=[Depends(local_only)])
def save_settings(body: dict[str, str]):
    updates = {}
    for k, v in body.items():
        if k not in config.SETTINGS:
            raise HTTPException(400, f"Không sửa được {k}")
        v = v.strip().replace(" ", "") if k in ("KURO_ALLOWED_TOOLS", "TELEGRAM_OWNER_IDS") else v.strip()
        if not re.fullmatch(config.SETTINGS[k][1], v):     # cũng chặn xuống dòng chèn thêm khóa lạ vào .env
            raise HTTPException(400, f"Giá trị {k} không hợp lệ")
        updates[k] = v
    old_tg = (config.TG_TOKEN, config.TG_OWNERS)
    config.save_env(updates)
    # Model, tool, API key có hiệu lực từ lượt chat kế tiếp; vòng Telegram chỉ khởi tạo lúc server lên.
    return {"ok": True, "restart": (config.TG_TOKEN, config.TG_OWNERS) != old_tg}


@app.get("/api/update")
def get_update():
    return update.STATUS


@app.get("/api/sessions")
def list_sessions():
    return store.sessions()


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
            req = await sock.receive_json()                  # {"session": id hoặc null, "text": "..."}
            text = (req.get("text") or "").strip()
            if not text:
                continue
            sid = store.ensure(req.get("session"), title=text)
            await sock.send_json({"type": "session", "id": sid})
            await engine.chat(sid, text, emit=sock.send_json)
    except WebSocketDisconnect:
        pass


app.mount("/", StaticFiles(directory=config.ROOT / "dashboard", html=True), name="ui")

if __name__ == "__main__":
    uvicorn.run(app, host=config.HOST, port=config.PORT)
