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
@app.get("/api/version")
async def get_version(check: bool = False):
    if check:
        await asyncio.to_thread(update.check, True)
    return update.get_status()


@app.post("/api/version", dependencies=[Depends(local_only)])
def set_version(body: dict):
    ver = (body.get("version") or "").strip()
    if not ver:
        raise HTTPException(400, "Số phiên bản không được để trống")
    try:
        updated = update.set_version(ver)
        return {"ok": True, "version": updated}
    except Exception as e:
        raise HTTPException(400, str(e))


@app.post("/api/update", dependencies=[Depends(local_only)])
async def run_update():
    res = update.start_update()
    if not res.get("ok"):
        raise HTTPException(400, res.get("error", "Không thể khởi động cập nhật"))
    return res


@app.get("/api/update/status")
def get_update_status():
    return {
        "state": update.read_state(),
        "log_tail": update.read_log_tail(),
    }


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


@app.get("/api/skills")
def list_skills():
    skills_dir = config.BRAIN / ".claude" / "skills"
    if not skills_dir.is_dir():
        skills_dir = config.ROOT / "skills"
    out = []
    if skills_dir.is_dir():
        import yaml
        for p in sorted(skills_dir.glob("*/SKILL.md")):
            raw = p.read_text(encoding="utf-8").replace("\r\n", "\n")
            meta = {}
            if raw.startswith("---\n"):
                try:
                    meta = yaml.safe_load(raw.split("---\n", 2)[1]) or {}
                except Exception:
                    meta = {}
            out.append({
                "slug": p.parent.name,
                "name": meta.get("name") or p.parent.name,
                "desc": (meta.get("description") or "").replace("\n", " ").strip()[:180]
            })
    return out


@app.get("/api/sessions/{sid}/context")
def session_context(sid: str):
    sess = store.get(sid)
    if not sess:
        raise HTTPException(404, "Không tìm thấy phiên")
    msgs = store.messages(sid)
    total_chars = sum(len(m.get("text", "")) for m in msgs)
    est_tokens = int(total_chars / 3.5)
    mem_file = config.BRAIN / "memory" / "MEMORY.md"
    mem_size = len(mem_file.read_text(encoding="utf-8")) if mem_file.is_file() else 0
    return {
        "id": sid,
        "title": sess.get("title", ""),
        "agent": sess.get("agent", "kuro-core"),
        "model": config.MODEL or "Mặc định",
        "provider": config.PROVIDER or "antigravity",
        "message_count": len(msgs),
        "total_chars": total_chars,
        "estimated_tokens": est_tokens,
        "memory_bytes": mem_size
    }


@app.post("/api/sessions/{sid}/compact")
async def compact_session(sid: str):
    sess = store.get(sid)
    if not sess:
        raise HTTPException(404, "Không tìm thấy phiên")
    msgs = store.messages(sid)
    if len(msgs) <= 2:
        return {"ok": True, "compacted": False, "msg": "Phiên còn quá ngắn (dưới 3 tin nhắn), chưa cần compact."}
    
    conversation_text = "\n\n".join(f"{'Người dùng' if m['role']=='user' else 'AI'}: {m['text']}" for m in msgs)
    summary_prompt = (
        "Hãy đọc toàn bộ cuộc trao đổi dưới đây và tóm tắt lại thật ngắn gọn, cô đọng nhưng giữ trọn vẹn "
        "mọi dữ liệu kỹ thuật quan trọng (số liệu, công thức, phương án, quyết định, việc đang làm dở dang).\n\n"
        f"Cuộc hội thoại:\n{conversation_text[:12000]}\n\n"
        "Định dạng kết quả: Bắt đầu bằng dòng `### [BẢN TÓM TẮT NGỮ CẢNH HỘI THOẠI ĐÃ ĐƯỢC THU GỌN]` rồi gạch đầu dòng các điểm chính."
    )
    
    summary_text = ""
    async for ev in engine.run_turn(summary_prompt, None, agent=sess.get("agent", "kuro-core")):
        if ev.get("type") == "text":
            summary_text += ev.get("text", "")
        elif ev.get("type") == "final" and not summary_text:
            summary_text = ev.get("text", "")
            
    if not summary_text:
        summary_text = f"### [BẢN TÓM TẮT NGỮ CẢNH THU GỌN]\n- Phiên thảo luận gồm {len(msgs)} tin nhắn đã được cô đọng.\n- Đã sẵn sàng tiếp tục mạch công việc."
        
    store.replace_messages(sid, [
        {"role": "user", "text": "*(Hệ thống: Toàn bộ ngữ cảnh trước đó đã được thu gọn bằng lệnh /compact)*"},
        {"role": "assistant", "text": summary_text}
    ])
    return {"ok": True, "compacted": True, "summary": summary_text}


@app.get("/api/fs/tree")
def get_fs_tree(sub: str = "", show_hidden: bool = False):
    base = config.ROOT
    target = (base / sub).resolve()
    if not str(target).startswith(str(base.resolve())):
        raise HTTPException(400, "Đường dẫn không hợp lệ")
    if not target.is_dir():
        raise HTTPException(404, "Thư mục không tồn tại")
    
    ignore_names = {".git", ".venv", "__pycache__", ".pytest_cache"} if not show_hidden else set()
    
    items = []
    try:
        for p in sorted(target.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower())):
            if p.name in ignore_names:
                continue
            if not show_hidden and p.name.startswith(".") and p.name not in {".claude", ".env", ".gitignore"}:
                continue
            rel = p.relative_to(base).as_posix()
            is_d = p.is_dir()
            items.append({
                "name": p.name,
                "path": rel,
                "is_dir": is_d,
                "ext": p.suffix.lower() if not is_d else "",
                "size": p.stat().st_size if not is_d else None
            })
    except Exception as e:
        raise HTTPException(500, f"Lỗi đọc thư mục: {e}")
    return {"path": sub, "name": target.name or "Kuro", "items": items}


@app.get("/api/fs/file")
def get_fs_file(path: str):
    base = config.ROOT
    target = (base / path).resolve()
    if not str(target).startswith(str(base.resolve())) or not target.is_file():
        raise HTTPException(404, "Không tìm thấy file")
    if target.stat().st_size > 3 * 1024 * 1024:
        raise HTTPException(400, "File quá lớn để xem trực tiếp (> 3MB)")
    try:
        content = target.read_text(encoding="utf-8", errors="replace")
        return {"path": path, "name": target.name, "content": content, "size": target.stat().st_size}
    except Exception as e:
        raise HTTPException(500, f"Lỗi đọc file: {e}")


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
