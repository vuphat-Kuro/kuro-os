"""Kuro OS - server. Chạy: .venv\\Scripts\\python server\\main.py"""
import asyncio
import ipaddress
import os
import re
import shutil
from contextlib import asynccontextmanager
from urllib.parse import urlparse

import io
import time
import zipfile
from pathlib import Path
import yaml
import uvicorn
from fastapi import Depends, FastAPI, File, HTTPException, Request, UploadFile, WebSocket, WebSocketDisconnect
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


def get_network_info(target_url: str | None = None):
    """Lấy danh sách IP mạng LAN / Wi-Fi và sinh mã QR để kết nối từ điện thoại di động."""
    import socket
    import io
    import base64
    import qrcode

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

    all_ips.sort(key=lambda x: not x["is_primary"])
    url_to_encode = target_url or f"http://{primary_ip}:{port}"

    qr_b64 = ""
    try:
        qr = qrcode.QRCode(box_size=7, border=2)
        qr.add_data(url_to_encode)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        qr_b64 = "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode("utf-8")
    except Exception as e:
        print("[network_info] QR generation error:", e)

    return {
        "ok": True,
        "hostname": hostname,
        "primary_ip": primary_ip,
        "port": port,
        "primary_url": f"http://{primary_ip}:{port}",
        "url": url_to_encode,
        "all_ips": all_ips,
        "qr_code": qr_b64,
        "listening_all": (config.HOST in ("0.0.0.0", "::"))
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


@app.get("/api/context")
def default_context():
    """Thông số ngữ cảnh mặc định của hệ thống khi bắt đầu phiên mới."""
    window_size = get_model_context_window()
    mem_files_paths = [
        config.BRAIN / "memory" / "MEMORY.md",
        config.ROOT / "AGENTS.md",
        config.ROOT / "CLAUDE.md",
    ]
    mem_chars = sum(len(p.read_text(encoding="utf-8", errors="ignore")) for p in mem_files_paths if p.is_file())
    mem_tokens = int(mem_chars / 3.5)
    meta, body = engine.agent_persona("kuro-core")
    prompt_tokens = int((len(body) + len(meta.get("role", "")) + 600) / 3.5)
    skill_tokens = 4500
    system_tools_tokens = 3200
    mcp_tools_tokens = 2400
    autocompact_threshold = int(window_size * 0.8)
    autocompact_buffer = int(window_size * 0.05)
    baseline_tokens = mem_tokens + prompt_tokens + skill_tokens + system_tools_tokens + mcp_tools_tokens
    free_space = max(0, window_size - baseline_tokens - autocompact_buffer)
    percent_used = round((baseline_tokens / window_size) * 100, 1)

    branch = "main"
    try:
        r = subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=config.ROOT, capture_output=True, text=True, timeout=2)
        if r.returncode == 0 and r.stdout.strip():
            branch = r.stdout.strip()
    except Exception:
        pass

    return {
        "id": None,
        "title": "Phiên mới",
        "agent": "kuro-core",
        "agent_name": "Kuro Core",
        "environment": {
            "host": "Máy tính này (Local Windows)",
            "brain_path": str(config.BRAIN),
            "git_branch": branch,
            "provider": config.PROVIDER or "antigravity",
            "model": config.MODEL or "Mặc định",
            "context_window": window_size,
        },
        "usage": {
            "total_tokens": baseline_tokens,
            "window_size": window_size,
            "percent": percent_used,
            "autocompact_threshold": autocompact_threshold,
            "tokens_until_compact": autocompact_threshold - baseline_tokens,
        },
        "breakdown": {
            "messages": {"tokens": 0, "percent": 0.0, "color": "#38bdf8", "name": "Messages"},
            "memory_files": {"tokens": mem_tokens, "percent": round((mem_tokens / window_size) * 100, 1), "color": "#fb923c", "name": "Memory files"},
            "system_tools": {"tokens": system_tools_tokens, "percent": round((system_tools_tokens / window_size) * 100, 1), "color": "#34d399", "name": "System tools"},
            "mcp_tools": {"tokens": mcp_tools_tokens, "percent": round((mcp_tools_tokens / window_size) * 100, 1), "color": "#c084fc", "name": "MCP tools"},
            "system_prompt": {"tokens": prompt_tokens, "percent": round((prompt_tokens / window_size) * 100, 1), "color": "#94a3b8", "name": "System prompt"},
            "skills": {"tokens": skill_tokens, "percent": round((skill_tokens / window_size) * 100, 1), "color": "#facc15", "name": "Skills"},
            "autocompact_buffer": {"tokens": autocompact_buffer, "percent": round((autocompact_buffer / window_size) * 100, 1), "color": "#475569", "name": "Autocompact buffer"},
            "free_space": {"tokens": free_space, "percent": round((free_space / window_size) * 100, 1), "color": "#0f172a", "name": "Free space"},
        },
        "counts": {
            "messages_count": 0,
            "memory_files_count": len([p for p in mem_files_paths if p.is_file()]),
            "skills_count": 21,
            "mcp_tools_count": 12,
            "custom_agents_count": len(engine.list_agents_info()),
        },
        "artifacts": []
    }


@app.get("/api/sessions/{sid}/context")
def session_context(sid: str):
    sess = store.get(sid)
    if not sess:
        raise HTTPException(404, "Không tìm thấy phiên")
    msgs = store.messages(sid)

    # 1. Message tokens
    msg_chars = sum(len(m.get("text", "")) for m in msgs)
    msg_tokens = int(msg_chars / 3.6) + (len(msgs) * 6)

    # 2. Model context window
    window_size = get_model_context_window(config.PROVIDER, config.MODEL)

    # 3. Memory files
    mem_files_paths = [
        config.BRAIN / "memory" / "MEMORY.md",
        config.ROOT / "AGENTS.md",
        config.ROOT / "CLAUDE.md",
    ]
    mem_chars = 0
    mem_count = 0
    for p in mem_files_paths:
        if p.is_file():
            mem_count += 1
            try:
                mem_chars += len(p.read_text(encoding="utf-8"))
            except Exception:
                pass
    mem_tokens = int(mem_chars / 3.5)

    # 4. System prompt for current agent
    agent_slug = sess.get("agent", "kuro-core")
    meta, body = engine.agent_persona(agent_slug)
    prompt_chars = len(body) + len(meta.get("role", "")) + 600
    prompt_tokens = int(prompt_chars / 3.5)

    # 5. Skills
    skills_dir = config.BRAIN / "skills"
    skills_count = 0
    skills_chars = 0
    if skills_dir.is_dir():
        for sp in skills_dir.glob("*/SKILL.md"):
            skills_count += 1
            skills_chars += min(2500, len(sp.read_text(encoding="utf-8", errors="ignore")))
    skill_tokens = int(skills_chars / 3.6) if skills_chars else 4500

    # 6. Tools
    system_tools_tokens = 3200
    mcp_tools_tokens = 2400
    mcp_tools_count = 12

    # 7. Autocompact buffer & thresholds
    autocompact_threshold = int(window_size * 0.8)
    autocompact_buffer = int(window_size * 0.05)

    total_used = msg_tokens + mem_tokens + prompt_tokens + skill_tokens + system_tools_tokens + mcp_tools_tokens
    free_space = max(0, window_size - total_used - autocompact_buffer)
    tokens_until_compact = max(0, autocompact_threshold - total_used)
    percent_used = round((total_used / window_size) * 100, 1)

    # 8. Git branch
    branch = "main"
    try:
        r = subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=config.ROOT, capture_output=True, text=True, timeout=2)
        if r.returncode == 0 and r.stdout.strip():
            branch = r.stdout.strip()
    except Exception:
        pass

    # 9. Artifacts / outputs
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
        "title": sess.get("title", ""),
        "agent": agent_slug,
        "agent_name": meta.get("name") or agent_slug,
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
            "messages_count": len(msgs),
            "memory_files_count": mem_count,
            "skills_count": skills_count or 21,
            "mcp_tools_count": mcp_tools_count,
            "custom_agents_count": len(engine.list_agents_info()),
        },
        "artifacts": artifacts
    }


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
def open_workspace(body: dict):
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


@app.get("/api/fs/file")
def get_fs_file(path: str):
    base = engine.active_workspace_dir()
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
            req = await sock.receive_json()                  # {"session": id hoặc null, "text": "...", "agent": slug, "workspace": path}
            text = (req.get("text") or "").strip()
            if not text:
                continue
            agent = req.get("agent") or "kuro-core"
            workspace = req.get("workspace") or str(engine.active_workspace_dir())
            sid = store.ensure(req.get("session"), title=text, agent=agent, workspace=workspace)
            await sock.send_json({"type": "session", "id": sid, "agent": agent, "workspace": workspace})
            await engine.chat(sid, text, agent=agent, emit=sock.send_json, workspace=workspace)
    except WebSocketDisconnect:
        pass


app.mount("/", StaticFiles(directory=config.ROOT / "dashboard", html=True), name="ui")

if __name__ == "__main__":
    uvicorn.run(app, host=config.HOST, port=config.PORT)
