"""Kuro OS - server. Chạy: .venv\\Scripts\\python server\\main.py"""
import asyncio
import ipaddress
import json
import os
import re
import shutil
import sys
from pathlib import Path

# Đảm bảo đường dẫn thư mục server và root luôn có trong sys.path
_SERVER_DIR = Path(__file__).resolve().parent
_ROOT_DIR = _SERVER_DIR.parent
if str(_SERVER_DIR) not in sys.path:
    sys.path.insert(0, str(_SERVER_DIR))
if str(_ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(_ROOT_DIR))

from contextlib import asynccontextmanager
from urllib.parse import urlparse, quote
import uuid

import io
import time
import zipfile
from pathlib import Path
import yaml
import uvicorn
from fastapi import Depends, FastAPI, File, HTTPException, Request, UploadFile, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
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


def is_trusted_host(hostname: str | None) -> bool:
    if not hostname:
        return False
    if hostname in LOCAL:
        return True
    try:
        ip = ipaddress.ip_address(hostname)
        if ip.is_private or ip.is_loopback:
            return True
        if ip in ipaddress.ip_network("100.64.0.0/10"):
            return True
        return False
    except ValueError:
        return hostname.endswith(".local") or hostname.endswith(".ts.net")


def is_local(headers) -> bool:
    """Chấp nhận localhost và các thiết bị trong mạng riêng (Wi-Fi, LAN, Tailscale); chặn website lạ (CSRF, DNS rebinding)."""
    origin = headers.get("origin")
    host_name = urlparse("//" + (headers.get("host") or "")).hostname
    origin_name = urlparse(origin).hostname if origin else None
    return is_trusted_host(host_name) and (not origin or is_trusted_host(origin_name))


class ConnectionManager:
    """Quản lý kết nối WebSocket và đồng bộ thời gian thực giữa máy tính & điện thoại."""
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, data: dict):
        for connection in list(self.active_connections):
            try:
                await connection.send_json(data)
            except Exception:
                pass


manager = ConnectionManager()
ACTIVE_STATE_FILE = config.STATE / "active_state.json"


def get_active_state() -> dict:
    if ACTIVE_STATE_FILE.is_file():
        try:
            return json.loads(ACTIVE_STATE_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    ws = engine.active_workspace_dir()
    return {
        "workspace": str(ws),
        "workspace_name": ws.name,
        "agent": "kuro-core",
        "session": None
    }


def save_active_state(st: dict):
    try:
        ACTIVE_STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        ACTIVE_STATE_FILE.write_text(json.dumps(st, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception:
        pass


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


@app.get("/api/clipboard/files")
def api_get_clipboard_files():
    """Lấy danh sách đường dẫn file hiện có trong Clipboard Windows khi người dùng copy file."""
    try:
        from system_clipboard import get_clipboard_files
        return {"files": get_clipboard_files()}
    except Exception as e:
        return {"files": [], "error": str(e)}


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
    members = body.get("members") or []
    from datetime import datetime
    content = f"""---
type: agent
name: {name}
slug: {slug}
role: {role}
group: {group}
skills: {skills}
members: {members}
model: ""
updated: {datetime.now():%Y-%m-%d}
---
{prompt}
"""
    for d in (config.ROOT / "agents", config.BRAIN / "agents"):
        d.mkdir(parents=True, exist_ok=True)
        (d / f"{slug}.md").write_text(content, encoding="utf-8")
    return {"ok": True, "slug": slug, "name": name, "group": group, "members": members}


@app.get("/api/agents/{slug}")
def get_agent_detail(slug: str):
    meta, body = engine.agent_persona(slug)
    if not meta and not body:
        raise HTTPException(404, "Không tìm thấy cộng sự")
    return {
        "slug": slug,
        "name": meta.get("name") or slug,
        "role": meta.get("role") or "",
        "group": meta.get("group") or ("Hệ thống" if slug == "kuro-core" else "Chuyên môn"),
        "skills": meta.get("skills") or [],
        "members": meta.get("members") or [],
        "prompt": body,
        "is_core": slug == "kuro-core",
    }


@app.put("/api/agents/{slug}")
def update_agent(slug: str, body: dict):
    if slug == "kuro-core":
        raise HTTPException(400, "Không thể sửa agent hệ thống Kuro Core")
    name = (body.get("name") or "").strip()
    if not name:
        raise HTTPException(400, "Tên cộng sự không được để trống")
    role = (body.get("role") or "").strip()
    group = (body.get("group") or "Chuyên môn").strip()
    prompt = (body.get("prompt") or "").strip() or f"Bạn là {name}, chuyên trách {role}."
    skills = body.get("skills") or []
    members = body.get("members") or []
    from datetime import datetime
    content = f"""---
type: agent
name: {name}
slug: {slug}
role: {role}
group: {group}
skills: {skills}
members: {members}
model: ""
updated: {datetime.now():%Y-%m-%d}
---
{prompt}
"""
    for d in (config.BRAIN / "agents", config.ROOT / "agents"):
        d.mkdir(parents=True, exist_ok=True)
        (d / f"{slug}.md").write_text(content, encoding="utf-8")
    return {"ok": True, "slug": slug, "name": name, "group": group, "members": members}


@app.post("/api/agents/upload")
async def upload_agent_file(file: UploadFile = File(...)):
    filename = file.filename or ""
    content_bytes = await file.read()
    if not content_bytes:
        raise HTTPException(400, "Tệp tải lên rỗng")

    from datetime import datetime
    import io
    import re
    from pathlib import Path
    import zipfile
    import yaml

    imported_agents = []

    def save_agent_md(raw_text: str, default_slug: str):
        raw_text = raw_text.replace("\r\n", "\n")
        meta = {}
        body = raw_text.strip()
        if raw_text.startswith("---\n"):
            try:
                _, fm, body = raw_text.split("---\n", 2)
                meta = yaml.safe_load(fm) or {}
            except Exception:
                pass
        slug = (meta.get("slug") or default_slug).strip().lower()
        slug = re.sub(r"[^a-z0-9]+", "-", slug).strip("-")
        if not slug:
            slug = f"agent-{int(datetime.now().timestamp())}"
        name = meta.get("name") or slug
        role = meta.get("role") or "Chuyên gia chuyên trách"
        group = meta.get("group") or "Chuyên môn"
        skills = meta.get("skills") or []
        members = meta.get("members") or []

        # Tái tạo frontmatter sạch chuẩn
        final_text = f"""---
type: agent
name: {name}
slug: {slug}
role: {role}
group: {group}
skills: {skills}
members: {members}
model: ""
updated: {datetime.now():%Y-%m-%d}
---
{body.strip()}
"""
        for d in (config.ROOT / "agents", config.BRAIN / "agents"):
            d.mkdir(parents=True, exist_ok=True)
            (d / f"{slug}.md").write_text(final_text, encoding="utf-8")
        imported_agents.append({"slug": slug, "name": name, "group": group})

    ext = Path(filename).suffix.lower()

    if ext == ".md":
        save_agent_md(content_bytes.decode("utf-8", errors="replace"), Path(filename).stem)
    elif ext in (".zip", ".skill"):
        # Thử mở dưới dạng zip
        try:
            with zipfile.ZipFile(io.BytesIO(content_bytes)) as z:
                for name in z.namelist():
                    if name.endswith("/") or name.startswith("__MACOSX/") or Path(name).name.startswith("."):
                        continue
                    p_name = Path(name)
                    if p_name.suffix.lower() == ".md":
                        file_data = z.read(name).decode("utf-8", errors="replace")
                        if "type: agent" in file_data or "agents/" in name or not ("skills/" in name):
                            save_agent_md(file_data, p_name.stem)
                        elif "type: skill" in file_data or p_name.name == "SKILL.md" or "skills/" in name:
                            skill_dir = p_name.parent.name if p_name.name == "SKILL.md" else p_name.stem
                            for target_base in (config.ROOT / "skills", config.BRAIN / ".claude" / "skills"):
                                target_dir = target_base / skill_dir
                                target_dir.mkdir(parents=True, exist_ok=True)
                                (target_dir / p_name.name).write_text(file_data, encoding="utf-8")
        except zipfile.BadZipFile:
            if ext == ".skill":
                save_agent_md(content_bytes.decode("utf-8", errors="replace"), Path(filename).stem)
            else:
                raise HTTPException(400, "Tệp zip hoặc skill bị lỗi hoặc không thể giải nén")
    else:
        raise HTTPException(400, "Vui lòng chọn tệp .zip, .md hoặc .skill")

    return {"ok": True, "count": len(imported_agents), "agents": imported_agents}


@app.delete("/api/agents/{slug}")
def delete_agent(slug: str):
    if slug == "kuro-core":
        raise HTTPException(400, "Không thể xóa agent hệ thống Kuro Core")
    deleted = False
    for d in (config.BRAIN / "agents", config.ROOT / "agents"):
        p = d / f"{slug}.md"
        if p.is_file():
            try:
                p.unlink()
                deleted = True
            except Exception as e:
                raise HTTPException(500, f"Lỗi xóa file agent: {e}")
    if not deleted:
        raise HTTPException(404, "Không tìm thấy file agent để xóa")
    return {"ok": True, "slug": slug}


@app.get("/api/groups")
def get_groups():
    return engine.get_groups_config()


@app.post("/api/groups")
def save_group_config(body: dict):
    old_name = (body.get("old_name") or "").strip()
    name = (body.get("name") or old_name).strip()
    role = (body.get("role") or "").strip()
    workflow = (body.get("workflow") or "").strip()
    if not name or name == "Hệ thống":
        raise HTTPException(400, "Tên nhóm không hợp lệ hoặc không thể chỉnh sửa nhóm Hệ thống")

    # Nếu đổi tên nhóm thì cập nhật các agent con
    if old_name and old_name != name and old_name != "Hệ thống":
        rename_agent_group({"old_name": old_name, "new_name": name})

    cfg = engine.get_groups_config()
    if old_name and old_name != name and old_name in cfg:
        del cfg[old_name]

    if workflow or role:
        cfg[name] = {"role": role, "workflow": workflow}
    else:
        if name in cfg:
            del cfg[name]

    engine.save_groups_config(cfg)
    return {"ok": True, "name": name, "has_workflow": bool(workflow)}


@app.post("/api/agent-groups/rename")
def rename_agent_group(body: dict):
    old_name = (body.get("old_name") or "").strip()
    new_name = (body.get("new_name") or "").strip()
    if not old_name or not new_name or old_name == "Hệ thống":
        raise HTTPException(400, "Tên nhóm không hợp lệ hoặc không thể đổi tên nhóm Hệ thống")
    import re
    updated_count = 0
    for d in (config.BRAIN / "agents", config.ROOT / "agents"):
        if not d.is_dir():
            continue
        for p in d.glob("*.md"):
            txt = p.read_text(encoding="utf-8")
            if re.search(rf"^group:\s*{re.escape(old_name)}\s*$", txt, flags=re.MULTILINE):
                new_txt = re.sub(rf"^group:\s*{re.escape(old_name)}\s*$", f"group: {new_name}", txt, flags=re.MULTILINE)
                p.write_text(new_txt, encoding="utf-8")
                updated_count += 1
    return {"ok": True, "old_name": old_name, "new_name": new_name, "updated": updated_count}


@app.get("/api/sessions")
def list_sessions(agent: str | None = None, workspace: str | None = None):
    ws = workspace if workspace is not None else str(engine.active_workspace_dir())
    return store.sessions(agent=agent, workspace=ws)


@app.post("/api/sessions")
def create_session(body: dict):
    agent = body.get("agent") or "kuro-core"
    title = body.get("title") or "Phiên mới"
    workspace = body.get("workspace") or str(engine.active_workspace_dir())
    sid = store.ensure(None, title=title, agent=agent, workspace=workspace)
    return {"id": sid, "agent": agent, "title": title, "workspace": workspace}


@app.delete("/api/sessions/{sid}")
def delete_session(sid: str):
    store.delete_session(sid)
    return {"ok": True}


@app.get("/api/sessions/{sid}")
def get_messages(sid: str):
    return store.messages(sid)


@app.get("/api/sessions/{sid}/info")
def get_session_info(sid: str):
    sess = store.get(sid)
    if not sess:
        raise HTTPException(404, "Không tìm thấy phiên")
    return sess


@app.post("/api/sessions/{sid}/model")
def set_session_model(sid: str, body: dict):
    model = (body.get("model") or "").strip()
    store.set_model(sid, model)
    return {"ok": True, "model": model}


@app.post("/api/upload-file")
async def upload_general_file(file: UploadFile = File(...)):
    filename = file.filename or "file.dat"
    ext = Path(filename).suffix.lower()
    safe_name = f"att_{time.strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}_{Path(filename).stem[:24]}{ext}"
    
    ws_dir = engine.active_workspace_dir()
    attach_dir = ws_dir / ".attachments"
    attach_dir.mkdir(parents=True, exist_ok=True)
    target_path = attach_dir / safe_name
    
    content = await file.read()
    target_path.write_bytes(content)
    
    return {
        "ok": True,
        "filename": safe_name,
        "original_name": filename,
        "path": str(target_path),
        "url": f"/api/attachments/{safe_name}",
        "size": len(content),
        "is_image": ext in {".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp", ".svg"}
    }


@app.post("/api/fs/pick-native-file", dependencies=[Depends(local_only)])
async def pick_native_file():
    if sys.platform != "win32":
        raise HTTPException(400, "Tính năng chỉ hỗ trợ trên Windows")
    import subprocess
    ps_script = Path(__file__).parent / "pick_file.ps1"
    try:
        loop = asyncio.get_event_loop()
        def _run():
            cmd = [
                "powershell.exe",
                "-NoProfile",
                "-ExecutionPolicy", "Bypass",
                "-STA",
                "-File", str(ps_script)
            ]
            return subprocess.run(
                cmd,
                capture_output=True,
                timeout=300
            )
        proc = await loop.run_in_executor(None, _run)
        lines = [line.strip() for line in proc.stdout.decode("utf-8", errors="ignore").splitlines() if line.strip()]
        files = [l for l in lines if Path(l).is_file()]
        if files:
            return {"ok": True, "files": files}
        return {"ok": False, "cancelled": True}
    except Exception as e:
        return {"ok": False, "error": str(e)}


@app.post("/api/upload-image")
async def upload_image(file: UploadFile = File(...)):
    filename = file.filename or "image.png"
    ext = Path(filename).suffix.lower()
    if ext not in {".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp", ".svg"}:
        ext = ".png"
    safe_name = f"img_{time.strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}{ext}"
    
    ws_dir = engine.active_workspace_dir()
    attach_dir = ws_dir / ".attachments"
    attach_dir.mkdir(parents=True, exist_ok=True)
    target_path = attach_dir / safe_name
    
    content = await file.read()
    target_path.write_bytes(content)
    
    return {
        "ok": True,
        "filename": safe_name,
        "original_name": filename,
        "path": str(target_path),
        "url": f"/api/attachments/{safe_name}",
        "size": len(content)
    }


@app.get("/api/attachments/{filename}")
def get_attachment(filename: str):
    safe_filename = Path(filename).name
    ws_dir = engine.active_workspace_dir()
    target = (ws_dir / ".attachments" / safe_filename).resolve()
    if not target.is_file():
        target = (config.ROOT / ".attachments" / safe_filename).resolve()
        if not target.is_file():
            raise HTTPException(404, "Không tìm thấy ảnh đính kèm")
    return FileResponse(target)


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


def get_tailscale_info() -> dict:
    """Kiểm tra và lấy trạng thái Tailscale trên máy tính (IP, tài khoản, thiết bị đã ghép nối)."""
    import json
    import subprocess
    import shutil
    from pathlib import Path

    ts_bin = shutil.which("tailscale")
    if not ts_bin:
        default_p = Path(r"C:\Program Files\Tailscale\tailscale.exe")
        if default_p.is_file():
            ts_bin = str(default_p)
    if not ts_bin:
        return {"installed": False, "running": False}

    try:
        res = subprocess.run([ts_bin, "status", "--json"], capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=5)
        if res.returncode != 0 or not res.stdout.strip():
            return {"installed": True, "running": False}
        data = json.loads(res.stdout)
        backend = data.get("BackendState", "")
        running = (backend == "Running")

        ips = data.get("TailscaleIPs", [])
        ipv4 = next((ip for ip in ips if "." in ip and not ip.startswith("127.")), "")

        user_info = {}
        for u in (data.get("User") or {}).values():
            user_info = {
                "login": u.get("LoginName", ""),
                "name": u.get("DisplayName", "")
            }
            break

        peers = []
        for p in (data.get("Peer") or {}).values():
            peer_ips = p.get("TailscaleIPs", [])
            p_ipv4 = next((ip for ip in peer_ips if "." in ip), "")
            peers.append({
                "name": p.get("HostName", ""),
                "dns": p.get("DNSName", "").rstrip("."),
                "os": p.get("OS", ""),
                "ip": p_ipv4,
                "online": p.get("Online", False)
            })

        return {
            "installed": True,
            "running": running,
            "ip": ipv4,
            "dns": (data.get("Self") or {}).get("DNSName", "").rstrip("."),
            "user": user_info,
            "peers": peers
        }
    except Exception as e:
        print(f"[tailscale] Lỗi đọc trạng thái: {e}")
        return {"installed": True, "running": False}


def get_network_info(target_url: str | None = None):
    """Lấy danh sách IP mạng LAN / Wi-Fi, tích hợp Tailscale và sinh mã QR kết nối từ điện thoại."""
    import socket
    import io
    import base64
    import qrcode

    def make_qr(url_str: str) -> str:
        try:
            qr = qrcode.QRCode(box_size=7, border=2)
            qr.add_data(url_str)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode("utf-8")
        except Exception as e:
            print("[network_info] QR generation error:", e)
            return ""

    port = config.PORT
    hostname = socket.gethostname()
    primary_ip = "127.0.0.1"
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        primary_ip = s.getsockname()[0]
        s.close()
    except Exception:
        pass

    all_ips = []
    try:
        for ip in socket.gethostbyname_ex(hostname)[2]:
            if not ip.startswith("127."):
                ip_type = "Wi-Fi / LAN"
                if ip.startswith("100."):
                    ip_type = "Tailscale VPN"
                elif ip.startswith("192.168.209.") or ip.startswith("192.168.41."):
                    ip_type = "Mạng ảo (Virtual LAN)"
                all_ips.append({
                    "ip": ip,
                    "type": ip_type,
                    "url": f"http://{ip}:{port}",
                    "is_primary": (ip == primary_ip)
                })
    except Exception:
        pass

    if not any(x["ip"] == primary_ip for x in all_ips):
        all_ips.insert(0, {
            "ip": primary_ip,
            "type": "Wi-Fi / LAN",
            "url": f"http://{primary_ip}:{port}",
            "is_primary": True
        })

    # Lấy thông tin Tailscale chuyên biệt
    ts = get_tailscale_info()
    ts_ip = ts.get("ip") if ts.get("running") else ""
    ts_url = f"http://{ts_ip}:{port}" if ts_ip else ""
    ts_qr = make_qr(ts_url) if ts_url else ""

    # Đảm bảo IP Tailscale có trong all_ips
    if ts_ip and not any(x["ip"] == ts_ip for x in all_ips):
        all_ips.append({
            "ip": ts_ip,
            "type": "Tailscale VPN",
            "url": ts_url,
            "is_primary": False
        })

    all_ips.sort(key=lambda x: not x["is_primary"])
    url_to_encode = target_url or (ts_url if ts_url else f"http://{primary_ip}:{port}")
    qr_b64 = make_qr(url_to_encode)

    return {
        "ok": True,
        "hostname": hostname,
        "primary_ip": primary_ip,
        "port": port,
        "primary_url": f"http://{primary_ip}:{port}",
        "url": url_to_encode,
        "all_ips": all_ips,
        "qr_code": qr_b64,
        "listening_all": (config.HOST in ("0.0.0.0", "::")),
        "tailscale": ts,
        "tailscale_ip": ts_ip,
        "tailscale_url": ts_url,
        "tailscale_qr": ts_qr
    }


@app.get("/api/network/remote")
def api_network_remote(url: str | None = None):
    """Lấy thông tin mạng LAN & sinh mã QR kết nối tức thì qua điện thoại di động."""
    return get_network_info(url)


def get_model_context_window(provider: str | None = None, model: str | None = None) -> int:
    """Xác định dung lượng Context Window theo Provider và Model AI đang dùng."""
    prov = (provider or config.PROVIDER or "antigravity").lower()
    mod = (model or config.MODEL or "").lower()

    if prov in ("antigravity", "gemini") or "gemini" in mod or "flash" in mod or "pro" in mod:
        return 1_000_000
    if "claude" in prov or "anthropic" in prov or any(k in mod for k in ("claude", "sonnet", "opus", "haiku")):
        return 200_000
    if any(k in prov for k in ("chatgpt", "codex", "openai")) or any(k in mod for k in ("gpt", "o1", "o3")):
        return 128_000
    if "deepseek" in prov or "deepseek" in mod:
        return 128_000
    if "ollama" in prov:
        return 32_000
    return 1_000_000 if prov == "antigravity" else 200_000


def collect_context_snapshot(sid: str = None, agent_slug: str = None) -> dict:
    """Tập hợp chi tiết và số liệu thực tế của toàn bộ ngữ cảnh (tệp bộ nhớ, công cụ MCP, kỹ năng, agent)."""
    # 1. Message tokens & count
    msgs = store.messages(sid) if sid else []
    msg_chars = sum(len(m.get("text", "")) for m in msgs)
    msg_tokens = int(msg_chars / 3.6) + (len(msgs) * 6) if msgs else 0
    msgs_count = len(msgs)

    # 2. Model context window
    window_size = get_model_context_window(config.PROVIDER, config.MODEL)

    # 3. Memory files thực tế
    candidates = [
        config.ROOT / "CLAUDE.md",
        config.ROOT / "AGENTS.md",
        config.BRAIN / "memory" / "MEMORY.md",
        config.ROOT / "KE-HOACH.md",
    ]
    facts_dir = config.BRAIN / "memory" / "facts"
    if facts_dir.is_dir():
        candidates.extend(sorted(facts_dir.glob("*.md")))

    memory_files = []
    seen_paths = set()
    for p in candidates:
        if not p.is_file():
            continue
        canon = str(p.resolve())
        if canon in seen_paths:
            continue
        seen_paths.add(canon)
        try:
            txt = p.read_text(encoding="utf-8", errors="ignore")
            chars = len(txt)
            tok = max(1, int(chars / 3.5))
            try:
                rel = p.relative_to(config.ROOT)
                disp = str(rel).replace("\\", "/")
            except Exception:
                disp = f"brains/{config.BRAIN.name}/{p.name}"
            memory_files.append({
                "name": p.name,
                "path": disp,
                "full_path": str(p).replace("\\", "/"),
                "chars": chars,
                "tokens": tok,
                "exists": True
            })
        except Exception:
            pass

    mem_tokens = sum(f["tokens"] for f in memory_files)
    mem_count = len(memory_files)

    # 4. Agent & System prompt
    if not agent_slug:
        if sid:
            sess = store.get(sid)
            agent_slug = sess.get("agent", "kuro-core") if sess else "kuro-core"
        else:
            agent_slug = "kuro-core"
    meta, body = engine.agent_persona(agent_slug)
    prompt_chars = len(body) + len(meta.get("role", "")) + 600
    prompt_tokens = int(prompt_chars / 3.5)
    agent_name = meta.get("name") or agent_slug

    # 5. Skills thực tế
    skills = []
    seen_skills = set()
    for d in (config.BRAIN / ".claude" / "skills", config.ROOT / "skills", config.BRAIN / "skills"):
        if not d.is_dir():
            continue
        for sp in sorted(d.glob("*/SKILL.md")):
            slug = sp.parent.name
            if slug in seen_skills:
                continue
            seen_skills.add(slug)
            try:
                raw = sp.read_text(encoding="utf-8", errors="ignore").replace("\r\n", "\n")
                smeta = {}
                if raw.startswith("---\n"):
                    try:
                        smeta = yaml.safe_load(raw.split("---\n", 2)[1]) or {}
                    except Exception:
                        pass
                chars = len(raw)
                tok = max(20, min(2500, int(chars / 3.6)))
                skills.append({
                    "slug": slug,
                    "name": smeta.get("name") or slug,
                    "desc": (smeta.get("description") or "").replace("\n", " ").strip()[:160],
                    "tokens": tok
                })
            except Exception:
                pass
    skill_tokens = sum(s["tokens"] for s in skills)
    skills_count = len(skills)

    # 6. Custom Agents
    custom_agents = []
    for a in engine.list_agents_info():
        aslug = a.get("slug", "")
        ameta, abody = engine.agent_persona(aslug)
        achars = len(abody) + len(ameta.get("role", "")) + 400
        atok = max(50, int(achars / 3.5))
        custom_agents.append({
            "slug": aslug,
            "name": a.get("name") or aslug,
            "role": a.get("role") or "",
            "group": a.get("group") or "Chuyên môn",
            "is_team": a.get("is_team", False),
            "tokens": atok
        })
    custom_agents_count = len(custom_agents)

    # 7. MCP Tools & System Tools
    mcp_tools = [
        {
            "name": "kuro · tinh_python",
            "server": "kuro",
            "desc": "Thực hiện phép tính Python an toàn, kiểm toán chính xác",
            "tokens": 180
        },
        {"name": "system · Read", "server": "system", "desc": "Đọc nội dung tệp tin văn bản, mã nguồn", "tokens": 165},
        {"name": "system · Write", "server": "system", "desc": "Tạo mới hoặc ghi đè nội dung tệp tin", "tokens": 175},
        {"name": "system · Edit", "server": "system", "desc": "Chỉnh sửa chính xác khối nội dung tệp tin", "tokens": 190},
        {"name": "system · Glob", "server": "system", "desc": "Tìm kiếm tệp tin theo mẫu pattern", "tokens": 140},
        {"name": "system · Grep", "server": "system", "desc": "Tìm kiếm nội dung tệp tin bằng RegEx", "tokens": 155},
        {"name": "system · Bash", "server": "system", "desc": "Thực thi lệnh shell / powershell an toàn", "tokens": 210},
        {"name": "system · WebSearch", "server": "system", "desc": "Tìm kiếm tài liệu kỹ thuật trên web", "tokens": 180},
        {"name": "system · WebFetch", "server": "system", "desc": "Truy xuất nội dung trang web kỹ thuật", "tokens": 170},
    ]
    if config.MCP_FILE.is_file():
        try:
            mcp_data = json.loads(config.MCP_FILE.read_text(encoding="utf-8"))
            for sname, sval in mcp_data.get("mcpServers", {}).items():
                tools_list = sval.get("tools") or []
                if tools_list:
                    for t in tools_list:
                        t_name = t if isinstance(t, str) else t.get("name", "tool")
                        mcp_tools.append({
                            "name": f"{sname} · {t_name}",
                            "server": sname,
                            "desc": f"Công cụ mở rộng {t_name} từ {sname}",
                            "tokens": 220
                        })
                else:
                    mcp_tools.append({
                        "name": f"{sname} · service",
                        "server": sname,
                        "desc": f"Dịch vụ MCP tích hợp: {sname}",
                        "tokens": 250
                    })
        except Exception:
            pass

    mcp_tools_count = len(mcp_tools)
    mcp_tools_tokens = sum(t["tokens"] for t in mcp_tools if t["server"] != "system")
    system_tools_tokens = sum(t["tokens"] for t in mcp_tools if t["server"] == "system")

    # 8. Buffer & Tổng
    autocompact_threshold = int(window_size * 0.8)
    autocompact_buffer = int(window_size * 0.05)
    total_used = msg_tokens + mem_tokens + prompt_tokens + skill_tokens + system_tools_tokens + mcp_tools_tokens
    free_space = max(0, window_size - total_used - autocompact_buffer)
    tokens_until_compact = max(0, autocompact_threshold - total_used)
    percent_used = round((total_used / window_size) * 100, 1)

    # 9. Git branch
    branch = "main"
    try:
        r = subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=config.ROOT, capture_output=True, text=True, timeout=2)
        if r.returncode == 0 and r.stdout.strip():
            branch = r.stdout.strip()
    except Exception:
        pass

    # 10. Artifacts
    artifacts = []
    for ext in ("*.xlsx", "*.docx", "*.pdf", "*.py", "*.md", "*.csv"):
        for f in (config.ROOT).glob(ext):
            if f.name in ("README.md", "CLAUDE.md", "AGENTS.md", "KE-HOACH.md", "VERSION"):
                continue
            try:
                artifacts.append({
                    "name": f.name,
                    "path": str(f.relative_to(config.ROOT)).replace("\\", "/"),
                    "mtime": f.stat().st_mtime
                })
            except Exception:
                pass
    artifacts = sorted(artifacts, key=lambda x: x["mtime"], reverse=True)[:10]

    return {
        "id": sid,
        "title": store.get(sid).get("title", "") if sid and store.get(sid) else "Phiên mới",
        "agent": agent_slug,
        "agent_name": agent_name,
        "environment": {
            "host": "Máy tính này (Local Windows)",
            "brain_path": str(config.BRAIN),
            "git_branch": branch,
            "provider": config.PROVIDER or "antigravity",
            "model": config.MODEL or "Mặc định",
            "context_window": window_size,
        },
        "usage": {
            "total_tokens": total_used,
            "window_size": window_size,
            "percent": percent_used,
            "autocompact_threshold": autocompact_threshold,
            "tokens_until_compact": tokens_until_compact,
        },
        "breakdown": {
            "messages": {"tokens": msg_tokens, "percent": round((msg_tokens / window_size) * 100, 1), "color": "#38bdf8", "name": "Messages"},
            "memory_files": {"tokens": mem_tokens, "percent": round((mem_tokens / window_size) * 100, 1), "color": "#fb923c", "name": "Memory files"},
            "system_tools": {"tokens": system_tools_tokens, "percent": round((system_tools_tokens / window_size) * 100, 1), "color": "#34d399", "name": "System tools"},
            "mcp_tools": {"tokens": mcp_tools_tokens, "percent": round((mcp_tools_tokens / window_size) * 100, 1), "color": "#c084fc", "name": "MCP tools"},
            "system_prompt": {"tokens": prompt_tokens, "percent": round((prompt_tokens / window_size) * 100, 1), "color": "#94a3b8", "name": "System prompt"},
            "skills": {"tokens": skill_tokens, "percent": round((skill_tokens / window_size) * 100, 1), "color": "#facc15", "name": "Skills"},
            "autocompact_buffer": {"tokens": autocompact_buffer, "percent": round((autocompact_buffer / window_size) * 100, 1), "color": "#475569", "name": "Autocompact buffer"},
            "free_space": {"tokens": free_space, "percent": round((free_space / window_size) * 100, 1), "color": "#0f172a", "name": "Free space"},
        },
        "counts": {
            "messages_count": msgs_count,
            "memory_files_count": mem_count,
            "skills_count": skills_count,
            "mcp_tools_count": mcp_tools_count,
            "custom_agents_count": custom_agents_count,
        },
        "details": {
            "memory_files": memory_files,
            "mcp_tools": mcp_tools,
            "skills": skills,
            "custom_agents": custom_agents,
        },
        "artifacts": artifacts
    }


@app.get("/api/context")
def default_context():
    """Thông số ngữ cảnh mặc định của hệ thống khi bắt đầu phiên mới."""
    return collect_context_snapshot(sid=None, agent_slug="kuro-core")


@app.get("/api/sessions/{sid}/context")
def session_context(sid: str):
    sess = store.get(sid)
    if not sess:
        raise HTTPException(404, "Không tìm thấy phiên")
    agent_slug = sess.get("agent", "kuro-core")
    return collect_context_snapshot(sid=sid, agent_slug=agent_slug)


@app.post("/api/sessions/{sid}/compact")
async def compact_session(sid: str):
    sess = store.get(sid)
    if not sess:
        raise HTTPException(404, "Không tìm thấy phiên")
    msgs = store.messages(sid)
    if len(msgs) < 2:
        return {"ok": True, "compacted": False, "msg": "Phiên chưa có đủ tin nhắn để nén (cần ít nhất 2 tin nhắn)."}
    
    conversation_text = "\n\n".join(f"{'Người dùng' if m['role']=='user' else 'AI'}: {m['text']}" for m in msgs)
    summary_prompt = (
        "Hãy đọc toàn bộ cuộc trao đổi dưới đây và tóm tắt lại thật ngắn gọn, cô đọng nhưng giữ trọn vẹn "
        "mọi dữ liệu kỹ thuật quan trọng (số liệu, công thức, phương án, quyết định, việc đang làm dở dang).\n\n"
        f"Cuộc hội thoại:\n{conversation_text[:12000]}\n\n"
        "Định dạng kết quả: Bắt đầu bằng dòng `### [BẢN TÓM TẮT NGỮ CẢNH HỘI THOẠI ĐÃ ĐƯỢC THU GỌN]` rồi gạch đầu dòng các điểm chính."
    )
    
    summary_text = ""
    try:
        async for ev in engine.run_turn(summary_prompt, None, agent=sess.get("agent", "kuro-core")):
            if ev.get("type") == "text":
                summary_text += ev.get("text", "")
            elif ev.get("type") == "final" and not summary_text:
                summary_text = ev.get("text", "")
    except Exception as e:
        print(f"[compact] engine run error: {e}")
            
    if not summary_text:
        # Fallback tạo bản tóm tắt từ các tin nhắn hiện có
        key_points = []
        for m in msgs:
            t = m.get("text", "").strip()
            if t and not t.startswith("*("):
                first_line = t.split("\n")[0][:140]
                role_label = "Kỹ sư" if m.get("role") == "user" else "Kuro"
                key_points.append(f"- **{role_label}:** {first_line}")
        summary_text = "### [BẢN TÓM TẮT NGỮ CẢNH HỘI THOẠI ĐÃ ĐƯỢC THU GỌN]\n" + ("\n".join(key_points[-8:]) if key_points else "- Đã thu gọn toàn bộ ngữ cảnh trao đổi trước đó.")
        
    store.replace_messages(sid, [
        {"role": "user", "text": "*(Hệ thống: Toàn bộ ngữ cảnh trước đó đã được thu gọn bằng lệnh /compact)*"},
        {"role": "assistant", "text": summary_text}
    ])
    return {"ok": True, "compacted": True, "summary": summary_text, "session_id": sid}


@app.get("/api/workspaces")
def get_workspaces():
    cfg = engine.get_workspaces_config()
    active = engine.active_workspace_dir()
    recent = cfg.get("recent") or []
    has_active = any(Path(r.get("path", "")).resolve() == active.resolve() for r in recent if r.get("path"))
    if not has_active:
        recent.insert(0, {
            "name": active.name,
            "path": str(active.resolve()),
            "last_opened": int(time.time())
        })
        cfg["active"] = str(active.resolve())
        cfg["recent"] = recent
        engine.save_workspaces_config(cfg)
    return {
        "active": str(active.resolve()),
        "name": active.name,
        "recent": recent
    }


@app.post("/api/workspaces/open", dependencies=[Depends(local_only)])
async def open_workspace(body: dict):
    p_str = (body.get("path") or "").strip()
    if not p_str:
        raise HTTPException(400, "Đường dẫn thư mục không được để trống")
    p = Path(p_str).resolve()
    create = bool(body.get("create", True))
    if not p.is_dir():
        if create:
            try:
                p.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                raise HTTPException(400, f"Không tạo được thư mục: {e}")
        else:
            raise HTTPException(404, f"Thư mục không tồn tại: {p_str}")

    cfg = engine.get_workspaces_config()
    recent = [r for r in (cfg.get("recent") or []) if Path(r.get("path", "")).resolve() != p]
    name = body.get("name") or p.name
    recent.insert(0, {
        "name": name,
        "path": str(p),
        "last_opened": int(time.time())
    })
    recent = recent[:25]
    cfg["active"] = str(p)
    cfg["recent"] = recent
    engine.save_workspaces_config(cfg)

    cur_st = get_active_state()
    cur_st["workspace"] = str(p)
    cur_st["workspace_name"] = p.name
    save_active_state(cur_st)
    try:
        await manager.broadcast({
            "type": "workspace_changed",
            "active": str(p),
            "name": p.name,
            "recent": recent
        })
    except Exception as e:
        print(f"[WS] Broadcast error: {e}")

    return {
        "ok": True,
        "active": str(p),
        "name": p.name,
        "recent": recent
    }


@app.delete("/api/workspaces/recent", dependencies=[Depends(local_only)])
def remove_recent_workspace(path: str):
    cfg = engine.get_workspaces_config()
    target = Path(path).resolve()
    recent = [r for r in (cfg.get("recent") or []) if Path(r.get("path", "")).resolve() != target]
    cfg["recent"] = recent
    engine.save_workspaces_config(cfg)
    return {"ok": True, "recent": recent}


@app.get("/api/active-state")
def api_get_active_state():
    st = get_active_state()
    ws = engine.active_workspace_dir()
    st["workspace"] = str(ws)
    st["workspace_name"] = ws.name
    return st


@app.post("/api/active-state", dependencies=[Depends(local_only)])
async def api_set_active_state(body: dict):
    st = get_active_state()
    if body.get("agent"):
        st["agent"] = body["agent"]
    if "session" in body:
        st["session"] = body["session"]
    if body.get("workspace"):
        st["workspace"] = body["workspace"]
        st["workspace_name"] = Path(body["workspace"]).name
    save_active_state(st)
    await manager.broadcast({
        "type": "sync_active",
        "agent": st.get("agent"),
        "session": st.get("session"),
        "workspace": st.get("workspace"),
        "workspace_name": st.get("workspace_name")
    })
    return {"ok": True, "state": st}


@app.get("/api/fs/drives", dependencies=[Depends(local_only)])
def get_system_drives():
    drives = []
    if sys.platform == "win32":
        import string
        from ctypes import windll
        bitmask = windll.kernel32.GetLogicalDrives()
        for letter in string.ascii_uppercase:
            if bitmask & 1:
                drive_path = f"{letter}:\\"
                try:
                    usage = shutil.disk_usage(drive_path)
                    free_gb = round(usage.free / (1024 ** 3), 1)
                    total_gb = round(usage.total / (1024 ** 3), 1)
                    drives.append({
                        "name": f"Ổ đĩa {letter}: ({free_gb} GB trống / {total_gb} GB)",
                        "path": drive_path,
                        "letter": letter
                    })
                except Exception:
                    drives.append({
                        "name": f"Ổ đĩa {letter}:",
                        "path": drive_path,
                        "letter": letter
                    })
            bitmask >>= 1
    else:
        drives.append({"name": "Thư mục gốc (Root /)", "path": "/", "letter": "/"})
    return {"drives": drives}


@app.get("/api/fs/directories", dependencies=[Depends(local_only)])
def get_system_directories(path: str = ""):
    if not path:
        return get_system_drives()
    p = Path(path).resolve()
    if not p.is_dir():
        raise HTTPException(404, "Thư mục không tồn tại")
    
    ignore_dirs = {
        "$recycle.bin", "system volume information", "recovery", "config.msi",
        "msocache", "perflogs", "node_modules", ".git"
    }
    subdirs = []
    try:
        for entry in sorted(p.iterdir(), key=lambda x: x.name.lower()):
            try:
                if entry.is_dir():
                    if entry.name.lower() in ignore_dirs or entry.name.startswith("$"):
                        continue
                    subdirs.append({
                        "name": entry.name,
                        "path": str(entry.resolve()),
                        "is_dir": True
                    })
            except Exception:
                continue
    except PermissionError:
        pass
    except Exception as e:
        raise HTTPException(500, f"Lỗi đọc thư mục: {e}")

    parent = str(p.parent.resolve()) if p.parent != p else None
    return {
        "current_path": str(p),
        "name": p.name or str(p),
        "parent": parent,
        "directories": subdirs
    }


@app.post("/api/workspaces/browse-native", dependencies=[Depends(local_only)])
async def browse_native_workspace():
    if sys.platform != "win32":
        raise HTTPException(400, "Tính năng chỉ hỗ trợ trên Windows")
    import subprocess
    ps_script = Path(__file__).parent / "pick_folder.ps1"
    try:
        loop = asyncio.get_event_loop()
        def _run():
            cmd = [
                "powershell.exe",
                "-NoProfile",
                "-ExecutionPolicy", "Bypass",
                "-STA",
                "-File", str(ps_script)
            ]
            return subprocess.run(
                cmd,
                capture_output=True,
                timeout=300
            )
        proc = await loop.run_in_executor(None, _run)
        lines = [line.strip() for line in proc.stdout.decode("utf-8", errors="ignore").splitlines() if line.strip()]
        selected = lines[-1] if lines else ""
        if selected and Path(selected).is_dir():
            p = Path(selected).resolve()
            cfg = engine.get_workspaces_config()
            recent = [r for r in (cfg.get("recent") or []) if Path(r.get("path", "")).resolve() != p]
            name = p.name or str(p)
            recent.insert(0, {
                "name": name,
                "path": str(p),
                "last_opened": int(time.time())
            })
            recent = recent[:25]
            cfg["active"] = str(p)
            cfg["recent"] = recent
            engine.save_workspaces_config(cfg)

            cur_st = get_active_state()
            cur_st["workspace"] = str(p)
            cur_st["workspace_name"] = name
            save_active_state(cur_st)

            await manager.broadcast({
                "type": "workspace_changed",
                "active": str(p),
                "name": name,
                "recent": recent
            })
            return {"ok": True, "path": str(p), "name": name, "recent": recent}
        return {"ok": False, "cancelled": True}
    except Exception as e:
        print(f"[browse-native] Lỗi mở hộp thoại Windows: {e}")
        return {"ok": False, "error": str(e)}


@app.get("/api/fs/tree")
def get_fs_tree(sub: str = "", show_hidden: bool = False):
    base = engine.active_workspace_dir()
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
    return {
        "path": sub,
        "name": target.name or base.name,
        "workspace_name": base.name,
        "workspace_path": str(base),
        "items": items
    }


BINARY_FILE_EXTENSIONS = {
    ".xlsx", ".xls", ".xlsm", ".xlsb", ".xltx",
    ".docx", ".doc", ".docm", ".dotx",
    ".pptx", ".ppt", ".pptm",
    ".pdf",
    ".dwg", ".dxf", ".dgn",
    ".zip", ".rar", ".7z", ".tar", ".gz",
    ".exe", ".dll", ".bin", ".iso", ".msi",
    ".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp", ".ico"
}


def resolve_fs_target(path: str) -> Path:
    """Xác định đường dẫn an toàn trong workspace, root dự án hoặc brain."""
    p = Path(path)
    base = engine.active_workspace_dir().resolve()
    root_base = config.ROOT.resolve()
    brain_base = config.BRAIN.resolve()

    if p.is_absolute():
        target = p.resolve()
    else:
        t1 = (base / path).resolve()
        if t1.exists():
            target = t1
        else:
            t2 = (root_base / path).resolve()
            if t2.exists():
                target = t2
            else:
                t3 = (brain_base / path).resolve()
                if t3.exists():
                    target = t3
                else:
                    target = t1

    allowed = (
        str(target).startswith(str(base)) or
        str(target).startswith(str(root_base)) or
        str(target).startswith(str(brain_base))
    )
    if not allowed or not target.exists():
        raise HTTPException(404, "Không tìm thấy tệp hoặc thư mục")
    return target


@app.get("/api/fs/file")
def get_fs_file(path: str):
    target = resolve_fs_target(path)
    if not target.is_file():
        raise HTTPException(400, "Đường dẫn không phải là tệp tin")
    ext = target.suffix.lower()
    sz = target.stat().st_size
    if ext in BINARY_FILE_EXTENSIONS:
        return {
            "path": path,
            "name": target.name,
            "is_binary": True,
            "ext": ext,
            "size": sz
        }
    if sz > 3 * 1024 * 1024:
        raise HTTPException(400, "File quá lớn để xem trực tiếp (> 3MB)")
    try:
        content = target.read_text(encoding="utf-8", errors="replace")
        return {
            "path": path,
            "name": target.name,
            "is_binary": False,
            "ext": ext,
            "content": content,
            "size": sz
        }
    except Exception as e:
        raise HTTPException(500, f"Lỗi đọc file: {e}")


@app.get("/api/fs/search")
def search_fs(q: str = ""):
    q = (q or "").strip().lower()
    if not q:
        return {"query": "", "items": []}
    base = engine.active_workspace_dir()
    results = []
    ignore_names = {".git", ".venv", "__pycache__", ".pytest_cache", "node_modules", ".attachments"}
    
    try:
        for root, dirs, files in os.walk(base):
            dirs[:] = [d for d in dirs if d not in ignore_names and not d.startswith(".")]
            rel_dir = os.path.relpath(root, base)
            rel_dir = "" if rel_dir == "." else rel_dir.replace("\\", "/")
            
            for d in dirs:
                if q in d.lower():
                    rel_p = f"{rel_dir}/{d}" if rel_dir else d
                    results.append({
                        "name": d,
                        "path": rel_p,
                        "is_dir": True,
                        "ext": "",
                        "size": None
                    })
                    if len(results) >= 150:
                        break
            if len(results) >= 150:
                break
                
            for f in files:
                if q in f.lower():
                    rel_p = f"{rel_dir}/{f}" if rel_dir else f
                    full_p = os.path.join(root, f)
                    try:
                        sz = os.path.getsize(full_p)
                    except Exception:
                        sz = 0
                    results.append({
                        "name": f,
                        "path": rel_p,
                        "is_dir": False,
                        "ext": Path(f).suffix.lower(),
                        "size": sz
                    })
                    if len(results) >= 150:
                        break
            if len(results) >= 150:
                break
    except Exception as e:
        raise HTTPException(500, f"Lỗi tìm kiếm: {e}")
    return {"query": q, "items": results}


@app.post("/api/fs/open")
def open_fs_item(body: dict):
    path = (body.get("path") or "").strip()
    target = resolve_fs_target(path) if path else engine.active_workspace_dir().resolve()
    try:
        os.startfile(str(target))
        return {"ok": True, "path": str(target)}
    except Exception as e:
        raise HTTPException(500, f"Lỗi mở bằng Windows: {e}")


@app.post("/api/fs/reveal")
def reveal_fs_item(body: dict):
    path = (body.get("path") or "").strip()
    target = resolve_fs_target(path) if path else engine.active_workspace_dir().resolve()
    try:
        if target.is_dir():
            subprocess.run(["explorer.exe", str(target)], check=False)
        else:
            subprocess.run(["explorer.exe", f"/select,{str(target)}"], check=False)
        return {"ok": True}
    except Exception as e:
        raise HTTPException(500, f"Lỗi mở thư mục trong Explorer: {e}")


@app.post("/api/fs/new-folder")
def create_fs_folder(body: dict):
    parent = (body.get("parent") or "").strip()
    name = (body.get("name") or "").strip()
    if not name or any(c in name for c in r'<>:"/\|?*'):
        raise HTTPException(400, "Tên thư mục không hợp lệ")
    base = engine.active_workspace_dir()
    parent_dir = (base / parent).resolve() if parent else base.resolve()
    if not str(parent_dir).startswith(str(base.resolve())) or not parent_dir.is_dir():
        raise HTTPException(400, "Thư mục cha không hợp lệ")
    new_dir = parent_dir / name
    if new_dir.exists():
        raise HTTPException(400, "Thư mục đã tồn tại")
    try:
        new_dir.mkdir(parents=True, exist_ok=False)
        return {"ok": True, "path": new_dir.relative_to(base).as_posix(), "name": name}
    except Exception as e:
        raise HTTPException(500, f"Lỗi tạo thư mục: {e}")


@app.post("/api/fs/new-file")
def create_fs_file(body: dict):
    parent = (body.get("parent") or "").strip()
    name = (body.get("name") or "").strip()
    if not name or any(c in name for c in r'<>:"/\|?*'):
        raise HTTPException(400, "Tên tệp tin không hợp lệ")
    base = engine.active_workspace_dir()
    parent_dir = (base / parent).resolve() if parent else base.resolve()
    if not str(parent_dir).startswith(str(base.resolve())) or not parent_dir.is_dir():
        raise HTTPException(400, "Thư mục cha không hợp lệ")
    new_file = parent_dir / name
    if new_file.exists():
        raise HTTPException(400, "Tệp tin đã tồn tại")
    try:
        new_file.touch()
        return {"ok": True, "path": new_file.relative_to(base).as_posix(), "name": name}
    except Exception as e:
        raise HTTPException(500, f"Lỗi tạo tệp tin: {e}")


@app.post("/api/fs/delete")
def delete_fs_item(body: dict):
    path = (body.get("path") or "").strip()
    if not path:
        raise HTTPException(400, "Không thể xóa thư mục gốc của dự án")
    base = engine.active_workspace_dir()
    target = (base / path).resolve()
    if not str(target).startswith(str(base.resolve())) or target == base.resolve() or not target.exists():
        raise HTTPException(400, "Đường dẫn không hợp lệ hoặc không tồn tại")
    try:
        if target.is_dir():
            shutil.rmtree(target)
        else:
            target.unlink()
        return {"ok": True, "path": path}
    except Exception as e:
        raise HTTPException(500, f"Lỗi xóa: {e}")


@app.post("/api/fs/rename")
def rename_fs_item(body: dict):
    path = (body.get("path") or "").strip()
    new_name = (body.get("new_name") or "").strip()
    if not path:
        raise HTTPException(400, "Không thể đổi tên thư mục gốc")
    if not new_name or any(c in new_name for c in r'<>:"/\|?*'):
        raise HTTPException(400, "Tên mới không hợp lệ")
    base = engine.active_workspace_dir()
    target = (base / path).resolve()
    if not str(target).startswith(str(base.resolve())) or target == base.resolve() or not target.exists():
        raise HTTPException(400, "Đường dẫn không hợp lệ hoặc không tồn tại")
    new_target = target.parent / new_name
    if new_target.exists():
        raise HTTPException(400, f"Tên '{new_name}' đã tồn tại")
    try:
        target.rename(new_target)
        return {"ok": True, "old_path": path, "new_path": new_target.relative_to(base).as_posix(), "new_name": new_name}
    except Exception as e:
        raise HTTPException(500, f"Lỗi đổi tên: {e}")


@app.post("/api/fs/copy")
def copy_fs_item(body: dict):
    src_path = (body.get("src") or "").strip()
    dest_dir_path = (body.get("dest") or "").strip()
    if not src_path:
        raise HTTPException(400, "Đường dẫn nguồn không hợp lệ")
    base = engine.active_workspace_dir()
    src = (base / src_path).resolve()
    dest_dir = (base / dest_dir_path).resolve() if dest_dir_path else base.resolve()
    
    if not str(src).startswith(str(base.resolve())) or not src.exists():
        raise HTTPException(400, "Tệp nguồn không tồn tại")
    if not str(dest_dir).startswith(str(base.resolve())) or not dest_dir.is_dir():
        raise HTTPException(400, "Thư mục đích không tồn tại")
    
    name = src.name
    dest = dest_dir / name
    if dest.exists():
        stem = src.stem if src.is_file() else src.name
        suffix = src.suffix if src.is_file() else ""
        count = 1
        while dest.exists():
            dest = dest_dir / f"{stem} - Copy ({count}){suffix}" if count > 1 else dest_dir / f"{stem} - Copy{suffix}"
            count += 1
            
    try:
        if src.is_dir():
            shutil.copytree(src, dest)
        else:
            shutil.copy2(src, dest)
        return {"ok": True, "new_path": dest.relative_to(base).as_posix(), "new_name": dest.name}
    except Exception as e:
        raise HTTPException(500, f"Lỗi sao chép: {e}")


@app.websocket("/ws")
async def ws(sock: WebSocket):
    if not is_local(sock.headers):
        await sock.close(code=1008)
        return
    await manager.connect(sock)
    try:
        # Gửi init state cho client mới kết nối
        cur_st = get_active_state()
        await sock.send_json({"type": "init_state", "state": cur_st})

        while True:
            req = await sock.receive_json()
            req_type = req.get("type")
            if req_type == "ping":
                await sock.send_json({"type": "pong"})
                continue

            if req_type == "sync_active":
                st = get_active_state()
                if req.get("agent"):
                    st["agent"] = req["agent"]
                if "session" in req:
                    st["session"] = req["session"]
                if req.get("workspace"):
                    st["workspace"] = req["workspace"]
                    st["workspace_name"] = Path(req["workspace"]).name
                save_active_state(st)
                await manager.broadcast({
                    "type": "sync_active",
                    "agent": st.get("agent"),
                    "session": st.get("session"),
                    "workspace": st.get("workspace"),
                    "workspace_name": st.get("workspace_name")
                })
                continue

            text = (req.get("text") or "").strip()
            if not text:
                continue
            agent = req.get("agent") or "kuro-core"
            workspace = req.get("workspace") or str(engine.active_workspace_dir())
            req_model = req.get("model") or None
            sid = store.ensure(req.get("session"), title=text, agent=agent, workspace=workspace, model=req_model or "")

            # Cập nhật trạng thái active
            cur_st = get_active_state()
            cur_st["agent"] = agent
            cur_st["session"] = sid
            cur_st["workspace"] = workspace
            cur_st["workspace_name"] = Path(workspace).name
            if req_model:
                cur_st["model"] = req_model
            save_active_state(cur_st)

            # Broadcast thông tin session & tin nhắn người dùng tới TẤT CẢ các thiết bị kết nối
            await manager.broadcast({
                "type": "session",
                "id": sid,
                "agent": agent,
                "workspace": workspace,
                "title": text,
                "model": req_model
            })
            await manager.broadcast({
                "type": "user_message",
                "session": sid,
                "agent": agent,
                "workspace": workspace,
                "text": text,
                "attachments": req.get("attachments") or [],
                "model": req_model
            })

            # Broadcast từng token streaming tới tất cả thiết bị
            async def broadcast_chunk(chunk: dict):
                payload = dict(chunk)
                payload["session"] = sid
                payload["agent"] = agent
                payload["workspace"] = workspace
                await manager.broadcast(payload)

            answer = await engine.chat(sid, text, agent=agent, emit=broadcast_chunk, workspace=workspace, model=req_model)

            # Broadcast sự kiện hoàn tất lượt với toàn bộ nội dung câu trả lời hoàn chỉnh
            await manager.broadcast({
                "type": "turn_complete",
                "session": sid,
                "agent": agent,
                "workspace": workspace,
                "answer": answer
            })

            # Broadcast kết thúc phiên để đồng bộ lịch sử trên cả 2 màn hình
            await manager.broadcast({
                "type": "session_saved",
                "id": sid,
                "agent": agent,
                "workspace": workspace,
                "title": text
            })
    except WebSocketDisconnect:
        manager.disconnect(sock)
    except Exception:
        manager.disconnect(sock)


app.mount("/", StaticFiles(directory=config.ROOT / "dashboard", html=True), name="ui")

if __name__ == "__main__":
    uvicorn.run(app, host=config.HOST, port=config.PORT)
