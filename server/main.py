"""Kuro OS - server. Chạy: .venv\\Scripts\\python server\\main.py"""
import asyncio
import hmac
import ipaddress
import json
import os
import re
import shutil
import subprocess
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
import threading
import time
import zipfile
from pathlib import Path
import yaml
import uvicorn
from fastapi import Depends, FastAPI, File, HTTPException, Request, UploadFile, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

import cli_engines
import config
import engine
from tra_cuu_hop_dong import tra_cuu_hop_dong
import scheduler
import store
import telegram
import token_stats
import goi
import kho
import update
import winproc
import workspace_rules


_FS_WATCH_SKIP = {".git", "node_modules", ".venv", "__pycache__", ".pytest_cache"}


def _workspace_fs_signature(ws_dir: Path, max_depth: int = 3, max_entries: int = 2000) -> tuple:
    """Tính chữ ký nhanh (số mục + băm tên/mtime/size) của thư mục dự án để tự động báo cây thư mục làm mới."""
    if not ws_dir.is_dir():
        return (str(ws_dir), 0, 0)
    import hashlib
    h = hashlib.blake2b(digest_size=8)
    count = 0
    stack: list[tuple[Path, int]] = [(ws_dir, 0)]
    while stack and count < max_entries:
        cur_dir, depth = stack.pop()
        try:
            with os.scandir(cur_dir) as it:
                entries = sorted(it, key=lambda e: e.name.lower())
        except OSError:
            continue
        for entry in entries:
            name = entry.name
            if name in _FS_WATCH_SKIP:
                continue
            try:
                st = entry.stat(follow_symlinks=False)
                is_dir = entry.is_dir(follow_symlinks=False)
                h.update(f"{depth}:{name}:{'d' if is_dir else 'f'}:{st.st_mtime_ns}:{st.st_size}\n".encode("utf-8", "replace"))
                count += 1
                if is_dir and depth < max_depth and count < max_entries:
                    stack.append((Path(entry.path), depth + 1))
            except OSError:
                continue
            if count >= max_entries:
                break
    return (str(ws_dir), count, h.hexdigest())


async def fs_watcher_loop() -> None:
    """Chỉ theo dõi thư mục dự án khi có ít nhất 1 cửa sổ đang BẬT tab Thư mục (Explorer)."""
    last_sig = None
    while True:
        try:
            await asyncio.sleep(1.5)
            if not manager.explorer_watchers:
                last_sig = None
                continue
            ws_dir = engine.active_workspace_dir()
            sig = await asyncio.to_thread(_workspace_fs_signature, ws_dir)
            if last_sig is not None and sig != last_sig and sig[0] == last_sig[0]:
                await manager.broadcast_explorer({
                    "type": "fs_changed",
                    "workspace": str(ws_dir),
                    "ts": time.time(),
                })
            last_sig = sig
        except asyncio.CancelledError:
            break
        except Exception:
            await asyncio.sleep(3)


@asynccontextmanager
async def lifespan(app):
    config.ensure_dirs()
    store.init()
    tasks = [
        asyncio.create_task(scheduler.loop(telegram.notify if config.TG_TOKEN else None)),
        asyncio.create_task(fs_watcher_loop()),
    ]
    if config.TG_TOKEN:
        tasks.append(asyncio.create_task(telegram.loop()))
    tasks.append(asyncio.create_task(update.loop(telegram.notify if config.TG_TOKEN else None)))
    yield
    for t in tasks:
        t.cancel()


app = FastAPI(lifespan=lifespan)


def may_nay(conn) -> bool:
    """Kết nối đến từ chính máy chạy Kuro (theo địa chỉ thật của gói tin, không theo header)."""
    try:
        return ipaddress.ip_address(conn.client.host).is_loopback
    except (AttributeError, TypeError, ValueError):
        return False


def dung_ma(t: str | None) -> bool:
    return bool(t) and hmac.compare_digest(t.encode(), config.remote_token().encode())


def da_ghep(conn) -> bool:
    """Máy này luôn được; điện thoại và máy khác phải có mã ghép (cookie nhận từ mã QR)."""
    return may_nay(conn) or dung_ma(conn.cookies.get("kuro_t"))


CHUA_GHEP = """<meta name="viewport" content="width=device-width"><body style="font:16px sans-serif;padding:24px">
<h3>Kuro: thiết bị này chưa được ghép</h3><p>Trên máy tính chạy Kuro, gõ <b>/remote</b> trong khung chat rồi quét mã QR.</p>"""


def _apply_no_cache(path: str, resp):
    """Không cache các tệp giao diện web chính để Ctrl+F5 trên Kuro Desktop & trình duyệt luôn lấy bản mới nhất."""
    if path in ("/", "/index.html", "/sw.js") or path.endswith((".html", ".js", ".css")):
        resp.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        resp.headers["Pragma"] = "no-cache"
        resp.headers["Expires"] = "0"
    return resp


@app.middleware("http")
async def chan_thiet_bi_la(req: Request, call_next):
    # Kiểm cả máy này: trình duyệt trên máy này vẫn có thể bị trang lạ mượn để gửi lệnh vào Kuro
    if not is_trusted_host(urlparse("//" + (req.headers.get("host") or "")).hostname):
        return HTMLResponse("Kuro: tên máy không hợp lệ", 421)          # DNS rebinding
    if req.method not in ("GET", "HEAD", "OPTIONS") and not cung_goc(req.headers):
        return HTMLResponse("Kuro: chặn yêu cầu gửi từ trang web khác", 403)  # CSRF
    if may_nay(req):
        return _apply_no_cache(req.url.path, await call_next(req))
    if dung_ma(req.query_params.get("t")):     # vừa quét QR: đổi mã trên địa chỉ thành cookie rồi bỏ khỏi địa chỉ
        r = RedirectResponse(str(req.url.remove_query_params("t")), 303)
        r.set_cookie("kuro_t", req.query_params["t"], max_age=365 * 86400, httponly=True, samesite="strict")
        return r
    if not da_ghep(req):
        return HTMLResponse(CHUA_GHEP, 401)
    return _apply_no_cache(req.url.path, await call_next(req))


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


def cung_goc(headers) -> bool:
    """Origin (nếu có) phải trùng đúng Host: trang khác cổng, khác máy LAN, khác *.ts.net đều bị chặn."""
    origin = headers.get("origin")
    if not origin:
        return True                      # không phải trình duyệt gửi chéo trang (curl, ứng dụng trên máy)
    o = urlparse(origin)
    return o.scheme in ("http", "https") and o.netloc.lower() == (headers.get("host") or "").lower()


def is_local(headers) -> bool:
    """Chấp nhận localhost và các thiết bị trong mạng riêng (Wi-Fi, LAN, Tailscale); chặn website lạ (CSRF, DNS rebinding)."""
    host_name = urlparse("//" + (headers.get("host") or "")).hostname
    return is_trusted_host(host_name) and cung_goc(headers)


class ConnectionManager:
    """Quản lý kết nối WebSocket và đồng bộ thời gian thực giữa máy tính & điện thoại."""
    def __init__(self):
        self.active_connections: list[WebSocket] = []
        self.explorer_watchers: set[WebSocket] = set()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.explorer_watchers.discard(websocket)
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    def set_explorer_watching(self, websocket: WebSocket, active: bool):
        if active:
            self.explorer_watchers.add(websocket)
        else:
            self.explorer_watchers.discard(websocket)

    async def broadcast(self, data: dict):
        for connection in list(self.active_connections):
            try:
                await connection.send_json(data)
            except Exception:
                pass

    async def broadcast_explorer(self, data: dict):
        for connection in list(self.explorer_watchers):
            try:
                await connection.send_json(data)
            except Exception:
                self.explorer_watchers.discard(connection)


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
    """Key, cài đặt, duyệt mã, cập nhật: chỉ trên chính máy tính, điện thoại đã ghép cũng không đổi được."""
    if not (may_nay(req) and is_local(req.headers)):
        raise HTTPException(403, "Chỉ mở được trên máy tính chạy Kuro")


@app.get("/api/token-stats", dependencies=[Depends(local_only)])
def get_token_stats(days: int = 7):
    """Token đã đốt theo nguồn (Kuro, Claude Desktop/Code, Codex): đọc nhật ký trên máy, không gọi API.
    Chỉ máy này: lộ tên dự án và câu hỏi đầu của các phiên AI khác."""
    return token_stats.thong_ke(max(1, min(days, 90)))


@app.get("/api/settings", dependencies=[Depends(local_only)])
def get_settings():
    out = {}
    for k, (secret, _) in config.SETTINGS.items():
        v = os.getenv(k, "")
        out[k] = {"set": bool(v), "hint": "…" + v[-4:] if v else ""} if secret else {"value": v}
    out["KURO_MODEL"] = {"value": config.MODEL}     # model của AI mặc định, giữ tương thích ngược
    enabled = config.enabled_providers()
    enabled_set = set(enabled)
    cli_status = {
        "claude": bool(shutil.which("claude")),
        "antigravity": bool(cli_engines.find("agy")),
        "chatgpt": bool(cli_engines.find("codex")),
    }
    providers_config = {}
    for p, info in config.PROVIDERS.items():
        key_val = config.get_provider_key(p)
        providers_config[p] = {
            "enabled": p in enabled_set,
            "is_default": p == config.PROVIDER,
            "model": config.get_provider_model(p),
            "has_key": bool(key_val),
            "key_hint": ("…" + key_val[-4:]) if key_val else "",
            "base_url": config.get_provider_url(p),
            "default_url": info.get("url", ""),
            "needs_key": bool(info.get("key")),
            "cli_installed": cli_status.get(p),
            "group": info.get("group", "api"),
            "short": info.get("short", p),
        }
    return {
        "settings": out,
        "providers": config.PROVIDERS,
        "providers_config": providers_config,
        "enabled_providers": enabled,
        "claude_cli": cli_status["claude"],
        "model_theo_ai": {p: config.get_provider_model(p) for p in config.PROVIDERS},
        "cli": {"codex": cli_status["chatgpt"], "agy": cli_status["antigravity"]},
        "telegram_on": bool(config.TG_TOKEN),
    }


@app.post("/api/settings", dependencies=[Depends(local_only)])
async def save_settings(body: dict[str, str]):
    updates = {}
    for k, v in body.items():
        if k not in config.SETTINGS:
            raise HTTPException(400, f"Không sửa được {k}")
        v = "" if v is None else str(v)
        v = v.strip().replace(" ", "") if k in ("KURO_ALLOWED_TOOLS", "TELEGRAM_OWNER_IDS", "KURO_ENABLED_PROVIDERS") else v.strip()
        if not re.fullmatch(config.SETTINGS[k][1], v):     # cũng chặn xuống dòng chèn thêm khóa lạ vào .env
            raise HTTPException(400, f"Giá trị {k} không hợp lệ")
        updates[k] = v

    # Validate & chuẩn hóa KURO_MODEL (kiểu cũ) theo AI đích
    if "KURO_MODEL" in updates:
        provider = updates.get("KURO_PROVIDER", config.PROVIDER)
        model = updates.pop("KURO_MODEL")
        agy = await cli_engines.models("agy") if provider == "antigravity" and model else []
        if err := config.model_error(provider, model, agy):
            raise HTTPException(400, err)
        model = next((m["id"] for m in agy if m["id"].lower() == model.lower()), model)
        updates[config.model_key(provider)] = model

    # Validate các khóa model riêng theo từng AI (KURO_MODEL_<PROVIDER>)
    agy_cache = None
    for p in config.PROVIDERS:
        mk = config.model_key(p)
        if mk in updates and updates[mk]:
            if p == "antigravity":
                if agy_cache is None:
                    agy_cache = await cli_engines.models("agy")
                agy = agy_cache
            else:
                agy = []
            if err := config.model_error(p, updates[mk], agy):
                raise HTTPException(400, err)
            if p == "antigravity" and agy:
                updates[mk] = next((m["id"] for m in agy if m["id"].lower() == updates[mk].lower()), updates[mk])

    # Đảm bảo AI mặc định luôn nằm trong danh sách enabled nếu KURO_ENABLED_PROVIDERS có giá trị
    eff_default = updates.get("KURO_PROVIDER", config.PROVIDER)
    if "KURO_ENABLED_PROVIDERS" in updates:
        en_list = [x for x in updates["KURO_ENABLED_PROVIDERS"].split(",") if x in config.PROVIDERS]
        if eff_default in config.PROVIDERS and eff_default not in en_list:
            en_list.insert(0, eff_default)
        updates["KURO_ENABLED_PROVIDERS"] = ",".join(dict.fromkeys(en_list))
    elif "KURO_PROVIDER" in updates and updates["KURO_PROVIDER"] in config.PROVIDERS:
        existing_en = os.getenv("KURO_ENABLED_PROVIDERS", "").strip()
        if existing_en:
            en_list = [x for x in existing_en.split(",") if x in config.PROVIDERS]
            if updates["KURO_PROVIDER"] not in en_list:
                en_list.insert(0, updates["KURO_PROVIDER"])
                updates["KURO_ENABLED_PROVIDERS"] = ",".join(en_list)

    old_tg = (config.TG_TOKEN, config.TG_OWNERS)
    config.save_env(updates)
    # Model, tool, API key có hiệu lực từ lượt chat kế tiếp; vòng Telegram chỉ khởi tạo lúc server lên.
    return {"ok": True, "restart": (config.TG_TOKEN, config.TG_OWNERS) != old_tg,
            "enabled_providers": config.enabled_providers()}


DEFAULT_AGY_MODELS = [
    {"id": "gemini-4-neon-high", "ten": "Gemini 4 Neon (High)"},
    {"id": "gemini-4-neon-xhigh", "ten": "Gemini 4 Neon (XHigh)"},
    {"id": "gemini-4-neon-medium", "ten": "Gemini 4 Neon (Medium)"},
    {"id": "gemini-4-neon-low", "ten": "Gemini 4 Neon (Low)"},
    {"id": "gemini-3.8-flash-medium", "ten": "Gemini 3.8 Flash (Medium - Khuyên dùng)"},
    {"id": "gemini-3.8-flash-high", "ten": "Gemini 3.8 Flash (High)"},
    {"id": "gemini-3.8-flash-low", "ten": "Gemini 3.8 Flash (Low)"},
    {"id": "gemini-4-argon-high", "ten": "Gemini 4 Argon (High - Rất mạnh)"},
    {"id": "gemini-4-argon-medium", "ten": "Gemini 4 Argon (Medium)"},
    {"id": "gemini-4-argon-low", "ten": "Gemini 4 Argon (Low)"},
    {"id": "gemini-4-hydrogen-high", "ten": "Gemini 4 Hydrogen (High)"},
    {"id": "gemini-4-hydrogen-medium", "ten": "Gemini 4 Hydrogen (Medium)"},
    {"id": "gemini-4-hydrogen-low", "ten": "Gemini 4 Hydrogen (Low)"},
    {"id": "claude-opus-5-5-high", "ten": "Claude Opus 5.5 (High)"},
    {"id": "claude-opus-5-5-medium", "ten": "Claude Opus 5.5 (Medium)"},
    {"id": "claude-opus-5-5-low", "ten": "Claude Opus 5.5 (Low)"},
    {"id": "claude-sonnet-5-5-high", "ten": "Claude Sonnet 5.5 (High)"},
    {"id": "claude-sonnet-5-5-medium", "ten": "Claude Sonnet 5.5 (Medium)"},
    {"id": "claude-sonnet-5-5-low", "ten": "Claude Sonnet 5.5 (Low)"},
]


async def _models_for_provider(p: str) -> list[dict]:
    """Lấy danh sách model khả dụng cho một nhà cung cấp AI cụ thể."""
    p = p or "claude"
    if p == "claude":
        caps = await engine.claude_models_caps()
        if caps:
            items = [{"id": "", "ten": "Mặc định"}]
            seen: set[str] = set()
            for c in caps:
                val = (c.get("value") or "").strip()
                if not val or val.lower() == "default" or val.lower() in seen:
                    continue
                seen.add(val.lower())
                ten = (c.get("displayName") or val).strip()
                items.append({
                    "id": val,
                    "ten": ten,
                    "resolved": c.get("resolvedModel") or val,
                    "effort_levels": c.get("supportedEffortLevels") or [],
                })
            if len(items) > 1:
                return items
        return list(config.CLAUDE_MODELS)
    if p == "antigravity":
        found = await cli_engines.models("agy")
        return list(found) if found else list(DEFAULT_AGY_MODELS)
    if p in ("chatgpt", "codex"):
        found = await cli_engines.models("codex")
        cur = config.get_provider_model("chatgpt")
        items = list(found) if found else []
        if cur and not any(m["id"] == cur for m in items):
            items.append({"id": cur, "ten": cur})
        return items
    # Các hãng API key / Ollama / Custom: nếu người dùng đã cấu hình model mặc định thì đưa lên để chọn nhanh
    cur = config.get_provider_model(p)
    return [{"id": cur, "ten": cur}] if cur else []


@app.get("/api/models", dependencies=[Depends(local_only)])
async def get_models(provider: str | None = None, scope: str | None = None):
    if scope == "enabled":
        enabled = config.enabled_providers()
        lists = await asyncio.gather(*(_models_for_provider(p) for p in enabled))
        groups = []
        cli_map = {
            "claude": bool(shutil.which("claude")),
            "antigravity": bool(cli_engines.find("agy")),
            "chatgpt": bool(cli_engines.find("codex")),
        }
        for p, items in zip(enabled, lists):
            info = config.PROVIDERS.get(p, {})
            def_m = config.get_provider_model(p)
            # Loại bỏ phần tử rỗng trùng (UI sẽ tự render mục "Mặc định" đầu mỗi nhóm)
            clean_items = [m for m in items if m.get("id")]
            if def_m and not any(m["id"].lower() == def_m.lower() for m in clean_items):
                clean_items.insert(0, {"id": def_m, "ten": def_m})
            groups.append({
                "provider": p,
                "name": info.get("ten", p),
                "short": info.get("short", p),
                "default_model": def_m,
                "cli_installed": cli_map.get(p),
                "models": clean_items,
            })
        def_prov = config.PROVIDER or (enabled[0] if enabled else "claude")
        default_group = next((g for g in groups if g["provider"] == def_prov), groups[0] if groups else None)
        return {
            "default_provider": def_prov,
            "default_model": config.get_provider_model(def_prov),
            "enabled_providers": enabled,
            "groups": groups,
            "models": default_group["models"] if default_group else [],
            "current": config.get_provider_model(def_prov),
        }

    p = provider if provider is not None else config.PROVIDER
    found = await _models_for_provider(p or "claude")
    curr = config.get_provider_model(p or "claude") if provider else config.MODEL
    return {"models": found, "current": curr, "provider": p or "claude"}


_USAGE = {"t": 0.0, "v": None}
_AGY_USAGE = {"t": 0.0, "v": None}
_AGY_USAGE_LOCK = threading.Lock()
_USAGE_RE = re.compile(r"Current (session|week \(all models\)): (\d+(?:\.\d+)?)% used(?: · resets ([^\n(]+?))?(?: \(|\n|$)")
_AGY_PCT_RE = re.compile(r"(\d+(?:\.\d+)?)\s*%")


def _parse_reset(txt: str):
    """"Nov 20, 6:19pm", "6:19pm", hoặc ISO UTC "2026-11-20T11:06:15Z" -> datetime cục bộ (naive); không hiểu thì None."""
    from datetime import datetime, timedelta
    now = datetime.now()
    txt = (txt or "").strip()
    if not txt:
        return None
    if "T" in txt and ("Z" in txt or "+" in txt or txt.count("-") >= 2):
        try:
            iso = txt[:-1] + "+00:00" if txt.endswith("Z") else txt
            d = datetime.fromisoformat(iso)
            if d.tzinfo is not None:
                d = d.astimezone().replace(tzinfo=None)
            return d
        except ValueError:
            pass
    for fmt in ("%b %d, %I:%M%p", "%b %d, %I%p", "%I:%M%p", "%I%p"):
        try:
            d = datetime.strptime(txt, fmt)
        except ValueError:
            continue
        if "%b" in fmt:
            d = d.replace(year=now.year)
            return d if d > now - timedelta(days=1) else d.replace(year=now.year + 1)
        d = now.replace(hour=d.hour, minute=d.minute, second=0, microsecond=0)
        return d if d > now else d + timedelta(days=1)
    return None


def _claude_usage(force: bool = False) -> dict | None:
    """Hạn mức THẬT của gói Claude: chạy lệnh /usage của Claude Code (cục bộ, không gọi model), cache 60 giây.
    Phản ánh cả phần dùng ngoài Kuro (Claude Code, app Claude) vì là hạn mức của cả tài khoản."""
    if not force and _USAGE["v"] and time.time() - _USAGE["t"] < 60:
        return _USAGE["v"]

    async def go():
        from claude_agent_sdk import AssistantMessage, ClaudeAgentOptions, ClaudeSDKClient
        async with ClaudeSDKClient(ClaudeAgentOptions(setting_sources=[], cwd=str(config.STATE))) as c:
            await c.query("/usage")
            async for m in c.receive_response():
                if isinstance(m, AssistantMessage):
                    return "".join(getattr(b, "text", "") for b in m.content)
        return ""
    try:
        txt = asyncio.run(asyncio.wait_for(go(), 45))
    except Exception as e:
        print(f"[quota] không lấy được /usage: {e}")
        return _USAGE["v"]
    found = {m.group(1).split(" ")[0]: (float(m.group(2)), m.group(3) or "") for m in _USAGE_RE.finditer(txt or "")}
    if "session" not in found:   # gói API key hoặc định dạng đổi: không có hạn mức theo gói
        return None
    _USAGE.update(t=time.time(), v=found)
    return found


def _agy_usage(force: bool = False) -> dict | None:
    """Hạn mức THẬT của Google Antigravity: chạy lệnh chính thức `agy -p /usage`, cache 60 giây."""
    if not force and _AGY_USAGE["v"] and time.time() - _AGY_USAGE["t"] < 60:
        return _AGY_USAGE["v"]
    agy_bin = cli_engines.find("agy")
    if not agy_bin:
        return None
    with _AGY_USAGE_LOCK:
        if not force and _AGY_USAGE["v"] and time.time() - _AGY_USAGE["t"] < 60:
            return _AGY_USAGE["v"]
        try:
            proc = subprocess.run(
                [agy_bin, "-p", "/usage", "--print-timeout", "15s", "--output-format", "text"],
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                stdin=subprocess.DEVNULL,
                timeout=22,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            )
            txt = (proc.stdout or b"").decode("utf-8", "replace")
        except Exception as e:
            print(f"[quota] không lấy được agy /usage: {e}")
            return _AGY_USAGE["v"]

        groups: dict[str, dict] = {}
        for raw_line in txt.splitlines():
            if "\t" not in raw_line:
                continue
            parts = [p.strip() for p in raw_line.split("\t")]
            if len(parts) < 3:
                continue
            grp, label, pct_str = parts[0], parts[1], parts[2]
            reset_raw = parts[3] if len(parts) >= 4 else ""
            m_pct = _AGY_PCT_RE.search(pct_str)
            if not m_pct:
                continue
            raw_pct = float(m_pct.group(1))
            lbl_low = label.lower()
            # AGY trả về tỷ lệ CÒN LẠI (Remaining %), quy đổi về % ĐÃ DÙNG để đồng bộ với Claude & thanh tiến trình Kuro
            used_val = raw_pct if "used" in lbl_low else max(0.0, min(100.0, 100.0 - raw_pct))
            used_pct = int(round(used_val)) if abs(used_val - round(used_val)) < 0.05 else round(used_val, 1)

            if any(k in lbl_low for k in ("five hour", "5 hour", "5-hour", "5h", "session")):
                win_key = "session"
            elif "week" in lbl_low:
                win_key = "week"
            else:
                continue
            groups.setdefault(grp, {})[win_key] = (used_pct, reset_raw)

        if not groups:
            return _AGY_USAGE["v"]
        _AGY_USAGE.update(t=time.time(), v=groups)
        return groups


def _select_agy_usage_group(groups: dict | None, model_id: str = "") -> dict | None:
    """Chọn đúng nhóm hạn mức AGY ứng với model đang dùng (Gemini Models / Claude & GPT / Gemini 4 Argon)."""
    if not groups:
        return None
    mid = (model_id or "").lower()
    gemini_grp = None
    claude_gpt_grp = None
    argon_grp = None
    for name, data in groups.items():
        nlow = name.lower()
        if "claude" in nlow or "gpt" in nlow:
            claude_gpt_grp = data
        elif "argon" in nlow:
            argon_grp = data
        elif "gemini" in nlow:
            gemini_grp = data

    chosen = None
    if ("claude" in mid or "gpt" in mid) and claude_gpt_grp:
        chosen = dict(claude_gpt_grp)
    elif ("argon" in mid or "g1-pro" in mid) and argon_grp:
        chosen = dict(argon_grp)
        if "session" not in chosen and gemini_grp and "session" in gemini_grp:
            chosen["session"] = gemini_grp["session"]
    elif gemini_grp:
        chosen = dict(gemini_grp)
    else:
        chosen = dict(next(iter(groups.values())))
    return chosen if ("session" in chosen or "week" in chosen) else None


def _provider_quota_stats(provider: str, now: float, default_provider: str, force: bool = False, model_id: str = "") -> dict:
    """Hạn mức một nhà cung cấp. Claude & AGY: số THẬT từ /usage. Codex / API khác: đếm lượt hỏi cục bộ trong Kuro."""
    from datetime import datetime
    t_5h_ago = now - 5 * 3600
    t_week_ago = now - 7 * 86400
    own = "(provider=? OR provider='' OR provider IS NULL)" if provider == default_provider else "provider=?"
    msgs_5h = store._q(f"SELECT ts FROM messages WHERE role='user' AND ts >= ? AND {own} ORDER BY ts ASC", (t_5h_ago, provider))
    count_week = len(store._q(f"SELECT ts FROM messages WHERE role='user' AND ts >= ? AND {own}", (t_week_ago, provider)))
    count_5h = len(msgs_5h)

    real = None
    if provider == "claude":
        real = _claude_usage(force)
    elif provider == "antigravity":
        real = _select_agy_usage_group(_agy_usage(force), model_id)

    if real:
        def part(key):
            if key not in real:
                return None, "", ""
            pct, raw = real[key]
            d = _parse_reset(raw)
            if not d:
                return pct, raw or "không rõ", ""
            rem = max(0, int((d - datetime.now()).total_seconds()))
            h, m = rem // 3600, (rem % 3600) // 60
            return pct, d, (f"còn {h}h {m:02d}m" if h else f"còn {m}m")
        p5, d5, in5 = part("session")
        pw, dw, _ = part("week")
        return {
            "source": "real",
            "block_5h": {"percent": p5, "used_count": count_5h, "max_count": None,
                         "reset_time": d5.strftime("%H:%M") if hasattr(d5, "strftime") else d5, "reset_in": in5},
            "weekly": {"percent": pw, "used_count": count_week, "max_count": None,
                       "reset_day": dw.strftime("%a %d/%m %H:%M") if hasattr(dw, "strftime") else dw},
        }
    return {
        "source": "local",
        "block_5h": {"percent": None, "used_count": count_5h, "max_count": None, "reset_time": "", "reset_in": ""},
        "weekly": {"percent": None, "used_count": count_week, "max_count": None, "reset_day": ""},
    }


@app.get("/api/thinking_support")
async def api_thinking_support(provider: str | None = None, model: str | None = None):
    """Model này chỉnh được mức suy nghĩ không (giao diện dùng để bật/tắt nút Cao/Tiêu chuẩn/Tắt)."""
    return await engine.thinking_support(provider or "", model or "")


@app.get("/api/quota")
def get_quota(session_id: str | None = None, provider: str | None = None, model: str | None = None, refresh: int = 0):
    now = time.time()
    sess = store.get(session_id) if session_id else None
    default_prov = config.PROVIDER or "antigravity"
    active_prov = (provider or "").strip() or store.session_provider(sess) or default_prov
    model_id = (model or "").strip() or (sess.get("model") if sess else None) or config.get_provider_model(active_prov) or ""
    provider_info = config.PROVIDERS.get(active_prov, {})
    provider_name = provider_info.get("ten", active_prov)
    provider_short = provider_info.get("short", active_prov)

    stats = _provider_quota_stats(active_prov, now, default_prov, bool(refresh), model_id=model_id)
    pct_5h = stats["block_5h"]["percent"] or 0
    pct_week = stats["weekly"]["percent"] or 0

    model_name = model_id or "Model mặc định"
    known_models = list(cli_engines._models.get("agy", [])) + DEFAULT_AGY_MODELS + config.CLAUDE_MODELS
    for m in known_models:
        if m.get("id") and m["id"] == model_id:
            model_name = m.get("ten") or model_id
            break

    if stats["source"] != "real":
        status_code = "unknown"
        status_text = "ℹ️ Hãng không cung cấp hạn mức"
    elif pct_5h >= 90 or pct_week >= 90:
        status_code = "danger"
        status_text = "🔴 Sắp chạm hạn mức"
    elif pct_5h >= 70 or pct_week >= 70:
        status_code = "warning"
        status_text = "🟡 Mức sử dụng cao"
    else:
        status_code = "normal"
        status_text = "🟢 Hạn mức dồi dào"

    by_provider = []
    for p in config.enabled_providers():
        p_info = config.PROVIDERS.get(p, {})
        p_mid = model_id if p == active_prov else (config.get_provider_model(p) or "")
        p_stats = _provider_quota_stats(p, now, default_prov, force=bool(refresh) and p == active_prov, model_id=p_mid)
        by_provider.append({
            "provider": p,
            "short": p_info.get("short", p),
            "name": p_info.get("ten", p),
            "used_5h": p_stats["block_5h"]["used_count"],
            "pct_5h": p_stats["block_5h"]["percent"],
            "used_week": p_stats["weekly"]["used_count"],
            "pct_week": p_stats["weekly"]["percent"],
        })

    return {
        "ok": True,
        "provider": active_prov,
        "provider_name": provider_name,
        "provider_short": provider_short,
        "model_id": model_id,
        "model_name": model_name,
        "source": stats["source"],
        "block_5h": stats["block_5h"],
        "weekly": stats["weekly"],
        "by_provider": by_provider,
        "status": status_code,
        "status_text": status_text,
    }


@app.post("/api/test-ai", dependencies=[Depends(local_only)])
async def test_ai(req: Request):
    provider = None
    model = None
    try:
        raw = await req.body()
        if raw:
            body = json.loads(raw)
            if isinstance(body, dict):
                provider = (body.get("provider") or "").strip() or None
                model = (body.get("model") or "").strip() if "model" in body else None
    except Exception:
        pass
    if provider and provider not in config.PROVIDERS:
        raise HTTPException(400, f"Nhà cung cấp không hợp lệ: {provider}")
    return await engine.ping(provider=provider, model=model)


def _claude_exe() -> str:
    exe = shutil.which("claude")
    if not exe:
        raise HTTPException(400, "Chưa cài Claude Code. Cài: npm install -g @anthropic-ai/claude-code")
    return exe


@app.get("/api/claude-login", dependencies=[Depends(local_only)])
async def claude_login_status():
    """Claude CLI đã đăng nhập chưa (claude auth status)."""
    exe = _claude_exe()
    try:
        r = await asyncio.to_thread(subprocess.run, [exe, "auth", "status"], capture_output=True, text=True,
                                    encoding="utf-8", errors="replace", timeout=20,
                                    creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        j = json.loads(r.stdout or "{}")
    except (subprocess.TimeoutExpired, ValueError) as e:
        raise HTTPException(500, f"Không đọc được trạng thái đăng nhập: {type(e).__name__}")
    return {"loggedIn": bool(j.get("loggedIn")), "method": j.get("authMethod", "")}


@app.post("/api/claude-login", dependencies=[Depends(local_only)])
def claude_login():
    """Mở cửa sổ dòng lệnh chạy `claude auth login` (trình duyệt tự mở để đăng nhập)."""
    exe = _claude_exe()
    if sys.platform != "win32":
        raise HTTPException(400, "Mở terminal và gõ: claude auth login")
    subprocess.Popen(["cmd", "/k", exe, "auth", "login"], creationflags=subprocess.CREATE_NEW_CONSOLE)
    return {"ok": True}


# Plugins (Gói tiện ích tùy chọn tích hợp sẵn & cài từ bên ngoài)
@app.get("/api/plugins", dependencies=[Depends(local_only)])
async def get_plugins():
    return await asyncio.to_thread(goi.danh_sach, True)


@app.post("/api/plugins/install", dependencies=[Depends(local_only)])
async def install_plugin(body: dict):
    gid = str(body.get("id") or "").strip()
    if not gid:
        raise HTTPException(400, "Thiếu mã plugin cần cài.")
    try:
        msg = await asyncio.to_thread(goi.cai, gid)
    except ValueError as e:
        raise HTTPException(400, str(e))
    except Exception as e:
        raise HTTPException(500, f"Lỗi cài plugin: {e}")
    return {"ok": True, "id": gid, "message": msg, **(await asyncio.to_thread(goi.danh_sach, True))}


@app.post("/api/plugins/uninstall", dependencies=[Depends(local_only)])
async def uninstall_plugin(body: dict):
    gid = str(body.get("id") or "").strip()
    if not gid:
        raise HTTPException(400, "Thiếu mã plugin cần gỡ.")
    try:
        msg = await asyncio.to_thread(goi.go, gid)
    except ValueError as e:
        raise HTTPException(400, str(e))
    except Exception as e:
        raise HTTPException(500, f"Lỗi gỡ plugin: {e}")
    return {"ok": True, "id": gid, "message": msg, **(await asyncio.to_thread(goi.danh_sach, True))}


@app.post("/api/plugins/mcp", dependencies=[Depends(local_only)])
async def plugin_mcp_toggle(body: dict):
    gid = str(body.get("id") or "").strip()
    if not gid:
        raise HTTPException(400, "Thiếu mã plugin.")
    try:
        msg = await asyncio.to_thread(goi.mcp_bat, gid, bool(body.get("bat")))
    except ValueError as e:
        raise HTTPException(400, str(e))
    except Exception as e:
        raise HTTPException(500, f"Lỗi cấu hình MCP: {e}")
    return {"ok": True, "id": gid, "message": msg, **(await asyncio.to_thread(goi.danh_sach, True))}


@app.post("/api/plugins/setup", dependencies=[Depends(local_only)])
async def setup_plugin_machine(body: dict):
    gid = str(body.get("id") or "").strip()
    action = str(body.get("action") or "").strip()
    if not gid or not action:
        raise HTTPException(400, "Thiếu mã plugin hoặc hành động cài đặt trên máy.")
    try:
        res = await asyncio.to_thread(goi.cai_dat_may, gid, action)
    except ValueError as e:
        raise HTTPException(400, str(e))
    except Exception as e:
        raise HTTPException(500, f"Lỗi cài đặt trên máy: {e}")
    return {**res, **(await asyncio.to_thread(goi.danh_sach, True))}


@app.post("/api/plugins/install-external-upload", dependencies=[Depends(local_only)])
async def install_external_plugin_upload(file: UploadFile = File(...)):
    filename = file.filename or "plugin.zip"
    if Path(filename).suffix.lower() not in (".zip", ".kuro-plugin"):
        raise HTTPException(400, "Chỉ hỗ trợ tệp nén .zip hoặc .kuro-plugin.")
    data = await file.read(goi.MAX_ZIP_BYTES + 1)
    if len(data) > goi.MAX_ZIP_BYTES:
        raise HTTPException(400, f"Tệp gói plugin vượt quá giới hạn {goi.MAX_ZIP_BYTES // (1024 * 1024)} MB.")
    try:
        res = await asyncio.to_thread(goi.cai_tu_zip, data, filename)
    except ValueError as e:
        raise HTTPException(400, str(e))
    except Exception as e:
        raise HTTPException(500, f"Lỗi cài gói plugin ngoài: {e}")
    return {**res, **(await asyncio.to_thread(goi.danh_sach, True))}


@app.post("/api/plugins/install-external-path", dependencies=[Depends(local_only)])
async def install_external_plugin_path(body: dict):
    path_str = str(body.get("path") or "").strip()
    if not path_str:
        raise HTTPException(400, "Vui lòng nhập hoặc chọn đường dẫn gói plugin.")
    try:
        res = await asyncio.to_thread(goi.cai_tu_duong_dan, path_str)
    except ValueError as e:
        raise HTTPException(400, str(e))
    except Exception as e:
        raise HTTPException(500, f"Lỗi cài gói plugin ngoài: {e}")
    return {**res, **(await asyncio.to_thread(goi.danh_sach, True))}


@app.post("/api/plugins/pick-folder", dependencies=[Depends(local_only)])
async def pick_plugin_folder():
    if sys.platform != "win32":
        raise HTTPException(400, "Hộp thoại chọn thư mục chỉ hỗ trợ trên Windows; vui lòng dán đường dẫn hoặc tải tệp .zip.")
    ps_script = Path(__file__).parent / "pick_folder.ps1"
    def _run():
        cmd = [
            "powershell.exe",
            "-NoProfile",
            "-ExecutionPolicy", "Bypass",
            "-STA",
            "-File", str(ps_script),
            "-Description", "Chọn thư mục chứa gói plugin cho Kuro OS",
        ]
        return subprocess.run(
            cmd,
            capture_output=True,
            timeout=300,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
    try:
        proc = await asyncio.to_thread(_run)
        lines = [line.strip() for line in proc.stdout.decode("utf-8", errors="ignore").splitlines() if line.strip()]
        selected = lines[-1] if lines else ""
        if selected and Path(selected).is_dir():
            return {"ok": True, "path": str(Path(selected).resolve())}
        return {"ok": False, "cancelled": True}
    except Exception as e:
        return {"ok": False, "error": str(e)}


# Kho skill và việc theo lịch (specs/002)
@app.get("/api/kho", dependencies=[Depends(local_only)])
def get_kho():
    return kho.danh_sach()


@app.post("/api/kho/duyet", dependencies=[Depends(local_only)])
def duyet_kho(body: dict[str, str]):
    try:
        return {"ok": True, **kho.duyet(body.get("skill", ""))}
    except ValueError as e:
        raise HTTPException(400, str(e))


@app.get("/api/lich", dependencies=[Depends(local_only)])
def get_lich():
    chay = scheduler.lan_chay()
    return {"viec": [{k: v.get(k) for k in ("id", "ten", "cron", "enabled", "kieu")} | {"lan_chay": chay.get(v["id"])}
                     for v in scheduler.ensure_defaults()]}


@app.post("/api/lich/{vid}", dependencies=[Depends(local_only)])
def bat_tat_lich(vid: str, body: dict[str, bool]):
    viec = scheduler.ensure_defaults()
    for v in viec:
        if v["id"] == vid:
            v["enabled"] = bool(body.get("enabled"))
            scheduler.save(viec)
            return {"ok": True}
    raise HTTPException(404, f"Không có việc {vid}")


@app.post("/api/lich/{vid}/chay", dependencies=[Depends(local_only)])
async def chay_thu_lich(vid: str):
    v = next((v for v in scheduler.ensure_defaults() if v["id"] == vid), None)
    if not v:
        raise HTTPException(404, f"Không có việc {vid}")
    return {"ok": True, "ket_qua": await scheduler.run_job(v), "phien": f"nhac-{vid}"}


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
    provider = (body.get("provider") or "").strip()
    if provider and provider not in config.PROVIDERS:
        raise HTTPException(400, f"Nhà cung cấp AI không hợp lệ: {provider}")
    model = (body.get("model") or "").strip()
    from datetime import datetime
    content = f"""---
type: agent
name: {name}
slug: {slug}
role: {role}
group: {group}
skills: {skills}
members: {members}
provider: "{provider}"
model: "{model}"
updated: {datetime.now():%Y-%m-%d}
---
{prompt}
"""
    for d in (config.ROOT / "agents", config.BRAIN / "agents"):
        d.mkdir(parents=True, exist_ok=True)
        (d / f"{slug}.md").write_text(content, encoding="utf-8")
    return {"ok": True, "slug": slug, "name": name, "group": group, "members": members, "provider": provider, "model": model}


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
        "provider": (meta.get("provider") or "").strip(),
        "model": (meta.get("model") or "").strip(),
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
    provider = (body.get("provider") or "").strip()
    if provider and provider not in config.PROVIDERS:
        raise HTTPException(400, f"Nhà cung cấp AI không hợp lệ: {provider}")
    model = (body.get("model") or "").strip()
    from datetime import datetime
    content = f"""---
type: agent
name: {name}
slug: {slug}
role: {role}
group: {group}
skills: {skills}
members: {members}
provider: "{provider}"
model: "{model}"
updated: {datetime.now():%Y-%m-%d}
---
{prompt}
"""
    for d in (config.BRAIN / "agents", config.ROOT / "agents"):
        d.mkdir(parents=True, exist_ok=True)
        (d / f"{slug}.md").write_text(content, encoding="utf-8")
    return {"ok": True, "slug": slug, "name": name, "group": group, "members": members, "provider": provider, "model": model}


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


@app.get("/api/contracts/search")
def api_tra_cuu_hop_dong(q: str = "", loai: str = "all", limit: int = 50):
    return tra_cuu_hop_dong(q, loai=loai, limit=limit)


@app.get("/api/sessions")
def list_sessions(agent: str | None = None, workspace: str | None = None):
    ws = workspace if workspace is not None else str(engine.active_workspace_dir())
    return store.sessions(agent=agent, workspace=ws)


@app.post("/api/sessions")
def create_session(body: dict):
    agent = body.get("agent") or "kuro-core"
    title = body.get("title") or "Phiên mới"
    workspace = body.get("workspace") or str(engine.active_workspace_dir())
    provider = (body.get("provider") or "").strip()
    if provider and provider not in config.PROVIDERS:
        raise HTTPException(400, f"Nhà cung cấp AI không hợp lệ: {provider}")
    model = (body.get("model") or "").strip()
    sid = store.ensure(None, title=title, agent=agent, workspace=workspace, model=model, provider=provider)
    return {"id": sid, "agent": agent, "title": title, "workspace": workspace, "provider": provider, "model": model}


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
    if not sess.get("provider"):
        sess["provider"] = store.session_provider(sess)
    task = session_chat_tasks.get(sid)
    sess["running"] = bool(task and not task.done())
    return sess


@app.post("/api/sessions/{sid}/model")
def set_session_model(sid: str, body: dict):
    model = (body.get("model") or "").strip()
    provider = body.get("provider")
    if provider is not None:
        provider = str(provider).strip()
        if provider and provider not in config.PROVIDERS:
            raise HTTPException(400, f"Nhà cung cấp AI không hợp lệ: {provider}")
    store.set_model(sid, model, provider=provider)
    return {"ok": True, "provider": provider or "", "model": model}


# Quản lý task chat theo từng session (xử lý độc lập, song song)
session_chat_tasks: dict[str, asyncio.Task] = {}


@app.post("/api/sessions/{sid}/stop")
async def stop_session_chat(sid: str):
    task = session_chat_tasks.get(sid)
    if task and not task.done():
        task.cancel()
        session_chat_tasks.pop(sid, None)
        await manager.broadcast({
            "type": "turn_stopped",
            "session": sid,
            "message": "_(Đã dừng phản hồi theo yêu cầu)_"
        })
        return {"ok": True, "stopped": True, "session": sid}
    return {"ok": True, "stopped": False, "session": sid}


@app.post("/api/upload-file")
async def upload_general_file(file: UploadFile = File(...)):
    filename = file.filename or "file.dat"
    ext = Path(filename).suffix.lower()
    safe_name = f"att_{time.strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}_{Path(filename).stem[:24]}{ext}"
    
    attach_dir = workspace_rules.attachments_dir(engine.active_workspace_dir())
    attach_dir.mkdir(parents=True, exist_ok=True)
    target_path = attach_dir / safe_name

    with target_path.open("wb") as out:   # ghi từng khối ra đĩa, tệp hàng trăm MB không phình RAM
        shutil.copyfileobj(file.file, out, 1024 * 1024)
    size = target_path.stat().st_size

    return {
        "ok": True,
        "filename": safe_name,
        "original_name": filename,
        "path": str(target_path),
        "url": f"/api/attachments/{safe_name}",
        "size": size,
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
                timeout=300,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0)
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
    
    attach_dir = workspace_rules.attachments_dir(engine.active_workspace_dir())
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
    # chỗ mới (02_KURO_XU_LY/.attachments), chỗ cũ ở gốc dự án, rồi thư mục Kuro
    for d in (workspace_rules.attachments_dir(ws_dir), ws_dir / ".attachments", config.ROOT / ".attachments"):
        target = (d / safe_filename).resolve()
        if target.is_file():
            return FileResponse(target)
    raise HTTPException(404, "Không tìm thấy ảnh đính kèm")


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
        no_win = getattr(subprocess, "CREATE_NO_WINDOW", 0)
        res = subprocess.run([ts_bin, "status", "--json"], capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=5, creationflags=no_win)
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
            qr.add_data(f"{url_str.rstrip('/')}/?t={config.remote_token()}")   # mã ghép: chỉ ai quét QR mới vào được
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


@app.get("/api/network/remote", dependencies=[Depends(local_only)])
def api_network_remote(url: str | None = None):
    """Lấy thông tin mạng LAN & sinh mã QR kết nối tức thì qua điện thoại di động."""
    return get_network_info(url)


# Ký tự/token của văn bản tiếng Việt: đo thật 2026-11 qua Claude Code get_context_usage (1.55-1.79). Số cũ 3.5-3.6 là hệ số tiếng Anh.
CTX_CHARS_PER_TOK = 1.7
_CTX_REAL: dict = {}
_CTX_REAL_LOCK = threading.Lock()
_CTX_REAL_TTL = 600   # giây; số "cố định" (prompt, tool, skill, bộ nhớ) chỉ đổi khi sửa tệp nên cache 10 phút là đủ


CTX_CHARS_PER_TOK_GEMINI = 2.8   # agy đo thật 2026-11: prompt Kuro 16276 ký tự = 5775 token (bộ tách từ Gemini gọn hơn Claude)
AGY_BASE_TOKENS = 11_100   # agy 1.5.13 đo thật: prompt hệ thống + 60 công cụ của agy, giống nhau ở thư mục trống và thư mục dự án


def _ctx_tok(chars: int, provider: str | None = None) -> int:
    return int(chars / (CTX_CHARS_PER_TOK_GEMINI if provider == "antigravity" else CTX_CHARS_PER_TOK))


get_model_context_window = config.cua_so_ngu_canh   # chuyển sang config để engine, token_stats dùng chung


async def _fetch_real_context(provider: str, model: str, agent_slug: str, ws: str):
    from claude_agent_sdk import ClaudeSDKClient
    si = engine.skill_index()

    async def one(strip_index: bool):
        o = engine.options(None, agent_slug, cwd=ws, model=model or None, provider=provider)
        if strip_index:   # lần thứ hai bỏ danh mục skill: hiệu hai lần đo = token thật của danh mục skill Kuro
            sp = dict(o.system_prompt)
            sp["append"] = sp["append"].replace(si, "")
            o.system_prompt = sp
        async with ClaudeSDKClient(o) as c:
            return await c.get_context_usage()

    return await asyncio.gather(one(False), one(True))


def _real_context_usage(provider: str, model: str, agent_slug: str, ws: str) -> dict | None:
    """Số THẬT từ Claude Code (get_context_usage, cùng bộ đếm với lệnh /context), cache 10 phút.
    None nếu AI chạy bằng CLI riêng (agy/codex) hoặc Claude Code không trả lời."""
    if engine.cli_kind(provider):
        return None
    key = (provider, model, agent_slug, ws)
    with _CTX_REAL_LOCK:
        hit = _CTX_REAL.get(key)
        if hit and time.time() - hit[0] < _CTX_REAL_TTL:
            return hit[1]
        try:
            full, bare = asyncio.run(asyncio.wait_for(_fetch_real_context(provider, model, agent_slug, ws), 60))
        except Exception as e:
            print(f"[context] không lấy được số thật từ Claude Code: {e}")
            _CTX_REAL[key] = (time.time() - _CTX_REAL_TTL + 60, hit[1] if hit else None)   # thử lại sau 60 giây
            return hit[1] if hit else None
        cat = {c["name"]: c["tokens"] for c in full["categories"]}
        bare_sp = {c["name"]: c["tokens"] for c in bare["categories"]}.get("System prompt", 0)
        real = {
            "window": full.get("rawMaxTokens") or full["maxTokens"],
            "buffer": cat.get("Autocompact buffer", 0),
            "window_default": full.get("autocompactSource") == "unknown-model",   # model lạ: Claude Code tự lấy 200k
            "model": full.get("model", ""),
            "system_prompt": cat.get("System prompt", 0),
            "skill_index": max(0, cat.get("System prompt", 0) - bare_sp),
            "system_tools": cat.get("System tools", 0),
            "agents": cat.get("Custom agents", 0),
            "memory": cat.get("Memory files", 0),
            "skills": cat.get("Skills", 0),
            "memory_files": full.get("memoryFiles") or [],
            "mcp_tools": full.get("mcpTools") or [],
            "agent_tokens": {a.get("agentType"): a.get("tokens", 0) for a in (full.get("agents") or [])},
        }
        _CTX_REAL[key] = (time.time(), real)
        return real


_CTX_MSG: dict = {}


def _real_messages_tokens(provider: str, model: str, agent_slug: str, ws: str, conv_id: str, n_msgs: int) -> int | None:
    """Token thật của hội thoại (gồm kết quả tool, tệp đính kèm) bằng cách nạp lại phiên vào Claude Code.
    Không gọi model. Cache theo (phiên, số tin) nên chỉ đo lại khi có tin mới."""
    key = (provider, conv_id, n_msgs)
    if key in _CTX_MSG:
        return _CTX_MSG[key]
    from claude_agent_sdk import ClaudeSDKClient

    async def go():
        o = engine.options(conv_id, agent_slug, cwd=ws, model=model or None, provider=provider)
        async with ClaudeSDKClient(o) as c:
            return await c.get_context_usage()
    try:
        u = asyncio.run(asyncio.wait_for(go(), 60))
        tok = next((c["tokens"] for c in u["categories"] if c["name"] == "Messages"), None)
    except Exception as e:
        print(f"[context] không đo được Messages thật: {e}")
        return None
    if len(_CTX_MSG) > 200:
        _CTX_MSG.clear()
    _CTX_MSG[key] = tok
    return tok


_AGY_TRANSCRIPT_CACHE: dict = {}
_CHAT_FILE_URL_RE = re.compile(r"file:///[^\s\)\"'>\]]+|file://[^\s\)\"'>\]]+", re.IGNORECASE)
_CHAT_WIN_PATH_RE = re.compile(
    r"(?:[A-Za-z]:[\\/]|\\\\[^\\\s<>|\"*?]+\\)[^\r\n<>|\"*?()\[\],;'`]+?\.(?:xlsx|xls|xlsm|xlsb|csv|docx|doc|pptx|ppt|pdf|html|htm|md|py|json|db|sqlite|sqlite3|sql|txt|yaml|yml|xml|dwg|dxf|dgn|ifc|rvt|png|jpg|jpeg|webp|svg|zip|rar|7z|kml|kmz|geojson)",
    re.IGNORECASE,
)
_ARTIFACT_EXTS = {
    ".xlsx", ".xls", ".xlsm", ".csv", ".docx", ".doc", ".pptx", ".ppt",
    ".pdf", ".html", ".htm", ".md", ".py", ".json", ".db", ".sqlite",
    ".sqlite3", ".sql", ".dwg", ".dxf", ".dgn", ".ifc", ".png", ".jpg",
    ".jpeg", ".webp", ".svg", ".zip", ".kml", ".kmz", ".geojson",
}
_ARTIFACT_SKIP_NAMES = {"README.md", "CLAUDE.md", "AGENTS.md", "KE-HOACH.md", "VERSION", "SKILL.md", "CHANGELOG.md"}
_ARTIFACT_SKIP_DIRS = {".git", ".venv", "venv", "node_modules", "__pycache__", ".pytest_cache", ".attachments", ".archify", ".system_generated"}


def _resolve_session_workspace(sess_row: dict | None) -> Path:
    """Lấy đúng thư mục dự án của phiên (giữ nguyên chữ hoa/thường thật trên đĩa)."""
    raw_ws = (sess_row.get("workspace") if isinstance(sess_row, dict) else "") or ""
    if raw_ws:
        # Ưu tiên lấy đúng tên gốc từ workspaces.json nếu khớp không phân biệt hoa thường
        try:
            cfg = engine.get_workspaces_config()
            norm_target = store.normalize_workspace(raw_ws)
            candidates = [cfg.get("active") or ""] + [r.get("path") or "" for r in (cfg.get("recent") or []) if isinstance(r, dict)]
            for c in candidates:
                if c and store.normalize_workspace(c) == norm_target and Path(c).is_dir():
                    return Path(c)
        except Exception:
            pass
        try:
            p = Path(raw_ws)
            if p.is_dir():
                return p.resolve()
        except Exception:
            pass
    return engine.active_workspace_dir()


def _agy_transcript_stats(conv_id: str | None) -> dict | None:
    """Đọc số liệu THẬT từ nhật ký transcript.jsonl của agy (cache theo mtime + size nên rất nhanh)."""
    if not conv_id:
        return None
    home = Path.home()
    cand_paths = (
        home / ".gemini" / "antigravity-cli" / "brain" / conv_id / ".system_generated" / "logs" / "transcript.jsonl",
        home / ".gemini" / "antigravity" / "brain" / conv_id / ".system_generated" / "logs" / "transcript.jsonl",
    )
    tp = next((p for p in cand_paths if p.is_file()), None)
    if not tp:
        return None
    try:
        st = tp.stat()
        cache_key = (str(tp), st.st_mtime_ns, st.st_size)
        if cache_key in _AGY_TRANSCRIPT_CACHE:
            return _AGY_TRANSCRIPT_CACHE[cache_key]
    except OSError:
        return None

    last_in = 0
    last_cache = 0
    last_out = 0
    last_model = ""
    tool_counts: dict[str, int] = {}
    touched_files: list[str] = []
    steps_count = 0
    write_tools = {"write_file", "edit_file", "write_to_file", "replace_file_content", "multi_replace_file_content"}
    try:
        with tp.open("r", encoding="utf-8", errors="ignore") as f:
            for ln in f:
                ln = ln.strip()
                if not ln:
                    continue
                try:
                    obj = json.loads(ln)
                except ValueError:
                    continue
                if obj.get("type") != "PLANNER_RESPONSE":
                    continue
                steps_count += 1
                inp = int(obj.get("input_tokens") or 0)
                cache = int(obj.get("cache_read_tokens") or 0)
                out = int(obj.get("output_tokens") or 0)
                if inp or cache or out:
                    last_in, last_cache, last_out = inp, cache, out
                if obj.get("model"):
                    last_model = str(obj["model"])
                for tc in (obj.get("tool_calls") or []):
                    if not isinstance(tc, dict):
                        continue
                    tname = str(tc.get("name") or "").strip()
                    if tname:
                        tool_counts[tname] = tool_counts.get(tname, 0) + 1
                    if tname in write_tools:
                        args = tc.get("args") or tc.get("arguments") or {}
                        if isinstance(args, dict):
                            for k in ("Path", "path", "TargetFile", "file_path", "AbsolutePath"):
                                val = args.get(k)
                                if isinstance(val, str) and val.strip():
                                    touched_files.append(val.strip().strip('"').strip("'"))
                                    break
    except Exception:
        return None

    total_tokens = last_in + last_cache + last_out
    result = {
        "input_tokens": last_in,
        "cache_read_tokens": last_cache,
        "output_tokens": last_out,
        "total_tokens": total_tokens,
        "model": last_model,
        "tool_counts": tool_counts,
        "touched_files": list(reversed(touched_files)),
        "steps_count": steps_count,
    }
    if len(_AGY_TRANSCRIPT_CACHE) > 64:
        _AGY_TRANSCRIPT_CACHE.clear()
    _AGY_TRANSCRIPT_CACHE[cache_key] = result
    return result


def _list_configured_mcp_servers(provider: str) -> list[str]:
    """Liệt kê tên các MCP server đang cấu hình cho hệ thống / agy."""
    names: list[str] = []
    seen: set[str] = set()
    # 1. state/mcp.json của Kuro
    try:
        mcp_file = config.STATE / "mcp.json"
        if mcp_file.is_file():
            data = json.loads(mcp_file.read_text(encoding="utf-8", errors="ignore"))
            servers = data.get("mcpServers") if isinstance(data, dict) else {}
            if isinstance(servers, dict):
                for k, v in servers.items():
                    if k and (not isinstance(v, dict) or not v.get("disabled")) and k not in seen:
                        seen.add(k)
                        names.append(str(k))
    except Exception:
        pass
    # 2. Thư mục MCP đã nạp của Antigravity (~/.gemini/antigravity/mcp/*)
    if provider == "antigravity":
        try:
            agy_mcp_dir = Path.home() / ".gemini" / "antigravity" / "mcp"
            if agy_mcp_dir.is_dir():
                for d in sorted(agy_mcp_dir.iterdir()):
                    if d.is_dir() and d.name not in seen:
                        seen.add(d.name)
                        names.append(d.name)
        except Exception:
            pass
    return names


def _decode_file_uri_str(raw: str) -> str:
    from urllib.parse import unquote
    s = re.sub(r"#L\d+(?:-L?\d+)?$", "", (raw or "").strip())
    if s.lower().startswith("file://"):
        try:
            u = urlparse(s)
            if u.netloc and u.netloc.lower() != "localhost":
                return "\\\\" + u.netloc + unquote(u.path).replace("/", "\\")
            p_str = unquote(u.path)
            if sys.platform == "win32" and re.match(r"^/[A-Za-z]:", p_str):
                p_str = p_str[1:]
            return p_str.replace("/", "\\") if sys.platform == "win32" else p_str
        except Exception:
            return s
    return s


def _extract_chat_artifacts(msgs: list[dict], ws_dir: Path, extra_paths: list[str] | None = None, limit: int = 15) -> list[dict]:
    """Lấy danh sách tệp kết quả từ chính hội thoại (ưu tiên) + tệp mới sửa gần đây trong thư mục dự án của phiên."""
    ws_resolved = ws_dir.resolve()
    artifacts: list[dict] = []
    seen: set[str] = set()

    def _try_add(raw_path: str, from_chat: bool):
        if not raw_path or len(artifacts) >= limit:
            return
        dec = _decode_file_uri_str(raw_path).strip().strip("`'\".,;:")
        if not dec or ".system_generated" in dec or "transcript.jsonl" in dec:
            return
        try:
            p = Path(dec)
            if not p.is_absolute() and not dec.startswith("\\\\"):
                p = (ws_resolved / dec)
            if not p.is_file():
                return
            rp = p.resolve()
        except Exception:
            return
        if rp.name in _ARTIFACT_SKIP_NAMES:
            return
        key = str(rp).lower()
        if key in seen:
            return
        seen.add(key)
        try:
            rel = str(rp.relative_to(ws_resolved)).replace("\\", "/")
        except Exception:
            rel = str(rp)
        try:
            mtime = rp.stat().st_mtime
        except OSError:
            mtime = 0.0
        artifacts.append({
            "name": rp.name,
            "path": rel,
            "full_path": str(rp),
            "mtime": mtime,
            "from_chat": from_chat,
        })

    # 1. Ưu tiên các tệp AI vừa tạo/sửa trực tiếp bằng tool trong hội thoại
    for ep in (extra_paths or []):
        _try_add(ep, from_chat=True)

    # 2. Các tệp xuất ra / liên kết được nhắc tới trong tin nhắn của phiên (mới nhất trước)
    for m in reversed(msgs or []):
        txt = m.get("text") or ""
        if not txt:
            continue
        for match in _CHAT_FILE_URL_RE.findall(txt):
            _try_add(match, from_chat=True)
        for match in _CHAT_WIN_PATH_RE.findall(txt):
            _try_add(match, from_chat=True)
        if len(artifacts) >= limit:
            break

    # 3. Bổ sung tệp mới sửa gần đây trong chính thư mục dự án của phiên (tối đa 2 cấp con, không quét config.ROOT)
    if len(artifacts) < limit and ws_resolved.is_dir():
        ws_files: list[tuple[float, Path]] = []

        def _scan_dir(d: Path, depth: int):
            if depth > 2:
                return
            try:
                for entry in d.iterdir():
                    if entry.name.startswith(".") and entry.name not in (".", ".."):
                        continue
                    if entry.is_dir():
                        if entry.name in _ARTIFACT_SKIP_DIRS:
                            continue
                        _scan_dir(entry, depth + 1)
                    elif entry.is_file():
                        if entry.name in _ARTIFACT_SKIP_NAMES:
                            continue
                        if entry.suffix.lower() in _ARTIFACT_EXTS:
                            try:
                                ws_files.append((entry.stat().st_mtime, entry))
                            except OSError:
                                pass
            except OSError:
                pass

        _scan_dir(ws_resolved, 0)
        ws_files.sort(key=lambda x: x[0], reverse=True)
        for _mt, fp in ws_files:
            if len(artifacts) >= limit:
                break
            _try_add(str(fp), from_chat=False)

    return artifacts


def collect_context_snapshot(sid: str = None, agent_slug: str = None) -> dict:
    """Tập hợp số liệu ngữ cảnh. Claude/API chạy qua Claude Code: lấy số THẬT từ bộ đếm của Claude Code.
    Agy: ưu tiên lấy số THẬT từ transcript.jsonl hoặc usage đã lưu của agy; Codex: ưu tiên usage thật từ stream."""
    # 1. Messages: lấy từ SQLite của phiên
    msgs = store.messages(sid) if sid else []
    msg_chars = sum(len(m.get("text", "")) for m in msgs)
    msg_tokens = 0   # tính sau khi biết provider
    msgs_count = len(msgs)

    # 2. Provider + model của phiên
    sess_row = store.get(sid) if sid else None
    sess_provider = store.session_provider(sess_row) or (config.PROVIDER or "antigravity")
    sess_model = (sess_row.get("model") if sess_row else None) or config.get_provider_model(sess_provider) or ""

    # 3. Agent & đúng thư mục dự án của phiên
    if not agent_slug:
        agent_slug = (sess_row.get("agent", "kuro-core") if sess_row else "kuro-core")
    meta, _body = engine.agent_persona(agent_slug)
    agent_name = meta.get("name") or agent_slug
    ws_dir = _resolve_session_workspace(sess_row)
    ws = str(ws_dir)

    skill_rows = []   # (slug, name, desc, số ký tự dòng của skill trong danh mục)
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
                desc = str(smeta.get("description") or "").replace("\n", " ").strip()
                skill_rows.append((slug, smeta.get("name") or slug, desc[:160], len(slug) + min(len(desc), 220) + len(sp.as_posix()) + 12))
            except Exception:
                pass

    real = _real_context_usage(sess_provider, sess_model, agent_slug, ws)
    measured = real is not None
    conv_id = store.get_conv_ids(sid).get(sess_provider) if sid else None
    real_msg = _real_messages_tokens(sess_provider, sess_model, agent_slug, ws, conv_id, msgs_count) if (measured and conv_id) else None
    msg_tokens = real_msg if real_msg is not None else ((_ctx_tok(msg_chars, sess_provider) + msgs_count * 6) if msgs else 0)
    agy_stats = _agy_transcript_stats(conv_id) if (sess_provider == "antigravity" and conv_id) else None
    saved_usage = store.get_usage(sess_row, sess_provider) if sess_row else None
    memory_files = []
    if measured:
        window_size = real["window"]
        window_source = "claude-code"
        if real["window_default"]:   # model ngoài họ Claude: Claude Code không biết cửa sổ nên tự lấy 200k
            window_size = get_model_context_window(sess_provider, sess_model)
            window_source = "bang-tra-cuu" if window_size != 200_000 else "mac-dinh"
        autocompact_buffer = real["buffer"]
        for f in real["memory_files"]:
            p = Path(f["path"])
            memory_files.append({"name": p.name, "path": str(p).replace("\\", "/"), "full_path": str(p).replace("\\", "/"),
                                 "tokens": f.get("tokens", 0), "exists": True})
        mem_tokens = real["memory"]
        skill_index_tok = real["skill_index"]
        prompt_tokens = max(0, real["system_prompt"] - skill_index_tok)
        skill_tokens = real["skills"] + skill_index_tok
        system_tools_tokens = real["system_tools"]
        agents_tokens = real["agents"]
        mcp_rows = [{"name": f"{t.get('serverName') or t.get('server') or 'mcp'} · {t.get('name', 'tool')}",
                     "server": t.get("serverName") or t.get("server") or "mcp",
                     "desc": "Công cụ MCP (số đo thật từ Claude Code)", "tokens": t.get("tokens", 0)} for t in real["mcp_tools"]]
        mcp_tools_tokens = sum(t["tokens"] for t in mcp_rows)
        sys_names = [t for t in config.ALLOWED_TOOLS if not t.startswith("mcp__")] + ["Skill", "Agent"]
        share = system_tools_tokens // max(1, len(sys_names))
        sys_rows = [{"name": f"system · {n}", "server": "system",
                     "desc": "Công cụ của Claude Code (tổng đo thật, chia đều cho các công cụ)", "tokens": share} for n in sys_names]
        mcp_tools = sys_rows + mcp_rows
    else:
        window_size = get_model_context_window(sess_provider, sess_model)
        window_source = "uoc-tinh"
        autocompact_buffer = min(33_000, int(window_size * 0.2))
        # Tệp bộ nhớ & quy tắc thực tế đang áp dụng cho phiên (workspace + Brain AGENTS.md)
        seen_mem: set[str] = set()
        mem_candidates = [
            ws_dir / "AGENTS.md",
            ws_dir / "QUY_TAC_LAM_VIEC.md",
            ws_dir / "CLAUDE.md",
            ws_dir / "MEMORY.md",
            config.BRAIN / "AGENTS.md",
        ]
        for p in mem_candidates:
            try:
                if not p.is_file():
                    continue
                rp = str(p.resolve()).lower()
                if rp in seen_mem:
                    continue
                seen_mem.add(rp)
                txt = p.read_text(encoding="utf-8", errors="ignore")
                memory_files.append({
                    "name": p.name,
                    "path": str(p.resolve()).replace("\\", "/"),
                    "full_path": str(p.resolve()).replace("\\", "/"),
                    "tokens": max(1, _ctx_tok(len(txt), sess_provider)),
                    "exists": True,
                })
            except Exception:
                pass
        mem_tokens = sum(f["tokens"] for f in memory_files)
        full_prompt = engine.cli_prompt("", True, agent_slug, ws)
        skill_index_tok = _ctx_tok(len(engine.skill_index()), sess_provider)
        skill_tokens = skill_index_tok
        prompt_tokens = max(0, _ctx_tok(len(full_prompt), sess_provider) - skill_index_tok)
        system_tools_tokens = AGY_BASE_TOKENS if sess_provider == "antigravity" else 0
        agents_tokens = 0
        mcp_tools, mcp_tools_tokens = [], 0

        # Danh sách công cụ thực tế đã gọi trong hội thoại + MCP server đang bật (cho AGY)
        if sess_provider == "antigravity":
            used_tools = (agy_stats.get("tool_counts") if agy_stats else None) or {}
            init_tools = (saved_usage.get("init_tools") if isinstance(saved_usage, dict) else None) or []
            if used_tools:
                sorted_used = sorted(used_tools.items(), key=lambda kv: (-kv[1], kv[0]))
                total_calls = sum(used_tools.values()) or 1
                for tname, cnt in sorted_used:
                    mcp_tools.append({
                        "name": f"agy · {tname} ({cnt} lần)",
                        "server": "agy",
                        "desc": f"Công cụ hệ thống AGY đã gọi {cnt} lần trong hội thoại này",
                        "tokens": max(1, int(system_tools_tokens * cnt / total_calls)),
                    })
            elif init_tools:
                share = system_tools_tokens // max(1, len(init_tools))
                for tname in init_tools[:30]:
                    mcp_tools.append({
                        "name": f"agy · {tname}",
                        "server": "agy",
                        "desc": "Công cụ hệ thống của Google Antigravity",
                        "tokens": share,
                    })
            for mname in _list_configured_mcp_servers(sess_provider):
                mcp_tools.append({
                    "name": f"mcp · {mname}",
                    "server": mname,
                    "desc": "MCP Server đang bật trong Antigravity / Kuro",
                    "tokens": 0,
                })

        # Đồng bộ số token THẬT của hội thoại từ AGY transcript / stream usage hoặc Codex stream usage
        real_cli_total = 0
        if sess_provider == "antigravity":
            if agy_stats and agy_stats.get("total_tokens", 0) > 0:
                real_cli_total = int(agy_stats["total_tokens"])
                window_source = "agy-real"
                measured = True
            elif saved_usage and int(saved_usage.get("total_tokens") or 0) > 0:
                real_cli_total = int(saved_usage["total_tokens"])
                window_source = "agy-real"
                measured = True
        elif sess_provider == "chatgpt":
            # Ngữ cảnh thật = đầu vào của LẦN GỌI GẦN NHẤT (nhật ký ~/.codex/sessions). usage của turn.completed cộng dồn
            # mọi lần gọi trong lượt nên từng hiện 222% (604k/272k) khi ngữ cảnh thật chỉ 101k (đo 26/11/2026).
            t = token_stats.mot_phien([conv_id]) if conv_id else None
            if t and t.get("ctx_cuoi"):
                real_cli_total = int(t["ctx_cuoi"])
            elif saved_usage and int(saved_usage.get("total_tokens") or 0) > 0:
                real_cli_total = int(saved_usage["total_tokens"])
            if real_cli_total:
                window_source = "codex-real"
                measured = True

        if real_cli_total > 0:
            fixed_overhead = mem_tokens + prompt_tokens + skill_tokens + system_tools_tokens + mcp_tools_tokens + agents_tokens
            if real_cli_total >= fixed_overhead:
                msg_tokens = real_cli_total - fixed_overhead
            else:
                # Lượt đầu rất ngắn: không hiển thị vượt quá số token thật mà model báo về
                scale = real_cli_total / max(1, fixed_overhead)
                mem_tokens = int(mem_tokens * scale)
                prompt_tokens = int(prompt_tokens * scale)
                skill_tokens = int(skill_tokens * scale)
                system_tools_tokens = int(system_tools_tokens * scale)
                msg_tokens = max(0, real_cli_total - (mem_tokens + prompt_tokens + skill_tokens + system_tools_tokens))

    # Danh sách skill: chia token danh mục theo độ dài từng dòng
    line_total = sum(r[3] for r in skill_rows) or 1
    skills = [{"slug": s, "name": n, "desc": d, "tokens": int(skill_index_tok * c / line_total)} for s, n, d, c in skill_rows]
    skills_count = len(skills)
    mem_count = len(memory_files)

    # Agent: token thật theo agentType nếu có, không thì ước tính theo chữ
    custom_agents = []
    for a in engine.list_agents_info():
        aslug = a.get("slug", "")
        if real and aslug in real["agent_tokens"]:
            atok = real["agent_tokens"][aslug]
        else:
            ameta, abody = engine.agent_persona(aslug)
            atok = max(1, _ctx_tok(len(abody) + len(ameta.get("role", "")) + 400))
        custom_agents.append({"slug": aslug, "name": a.get("name") or aslug, "role": a.get("role") or "",
                              "group": a.get("group") or "Chuyên môn", "is_team": a.get("is_team", False), "tokens": atok})
    custom_agents_count = len(custom_agents)

    mcp_tools_count = len(mcp_tools)

    # Tổng. Claude Code: ngưỡng tự nén = cửa sổ - buffer (buffer cố định 33k, không phải 5% cửa sổ)
    autocompact_threshold = max(0, window_size - autocompact_buffer)
    total_used = msg_tokens + mem_tokens + prompt_tokens + skill_tokens + system_tools_tokens + mcp_tools_tokens + agents_tokens
    free_space = max(0, window_size - total_used - autocompact_buffer)
    tokens_until_compact = max(0, autocompact_threshold - total_used)
    percent_used = round((total_used / window_size) * 100, 1)

    # 9. Git branch của đúng thư mục dự án phiên đang làm việc
    branch = "Không có Git"
    try:
        no_win = getattr(subprocess, "CREATE_NO_WINDOW", 0)
        r = subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=ws_dir, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=2, creationflags=no_win)
        if r.returncode == 0 and r.stdout.strip():
            branch = r.stdout.strip()
    except Exception:
        pass

    # 10. Artifacts: ưu tiên tệp xuất ra từ chính hội thoại + tệp mới sửa trong dự án của phiên
    agy_touched = agy_stats.get("touched_files") if agy_stats else None
    artifacts = _extract_chat_artifacts(msgs, ws_dir, extra_paths=agy_touched, limit=15)

    return {
        "id": sid,
        "title": sess_row.get("title", "") if sess_row else "Phiên mới",
        "agent": agent_slug,
        "agent_name": agent_name,
        "session_provider": store.session_provider(sess_row) if sess_row else "",
        "session_model": (sess_row.get("model") if sess_row else "") or "",
        "environment": {
            "host": "Máy tính này (Local Windows)",
            "workspace_name": ws_dir.name,
            "workspace_path": str(ws_dir),
            "brain_path": str(config.BRAIN),
            "git_branch": branch,
            "provider": sess_provider,
            "provider_name": config.PROVIDERS.get(sess_provider, {}).get("ten", sess_provider),
            "provider_short": config.PROVIDERS.get(sess_provider, {}).get("short", sess_provider),
            "model": sess_model or "Mặc định",
            "context_window": window_size,
            "window_source": window_source,
            "measured": measured,
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
            "custom_agents": {"tokens": agents_tokens, "percent": round((agents_tokens / window_size) * 100, 1), "color": "#818cf8", "name": "Custom agents"},
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


@app.post("/api/sessions/{sid}/compact")
async def session_compact(sid: str):
    """Nút Nén ngữ cảnh: AI tóm tắt phiên, bỏ hội thoại cũ; câu tiếp theo mở hội thoại mới chỉ với bản tóm tắt."""
    if sid in session_chat_tasks and not session_chat_tasks[sid].done():
        return {"ok": False, "error": "Phiên đang trả lời, đợi xong lượt này rồi nén."}
    kq = await engine.nen_phien(sid)
    if kq.get("ok"):
        await manager.broadcast({"type": "session_saved", "id": sid})   # máy khác (điện thoại) tải lại lịch sử
    return kq


@app.get("/api/sessions/{sid}/token")
def session_token(sid: str):
    """Token của phiên Kuro này (lần gọi gần nhất so với ngưỡng): giao diện báo đỏ ngay sau lượt chat."""
    sess = store.get(sid)
    if not sess:
        return {}
    prov = store.session_provider(sess) or config.PROVIDER or "claude"
    ids = store.get_conv_ids(sid)
    # chỉ hội thoại của AI đang dùng: hội thoại cũ của AI khác trong cùng phiên không còn đốt token
    return token_stats.mot_phien([ids.get(prov, "")], provider=prov,
                                 model=sess.get("model") or config.get_provider_model(prov)) or {}


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
    sess_prov = store.session_provider(sess) or (config.PROVIDER or "claude")
    sess_mod = (sess.get("model") or "").strip() or None
    try:
        async for ev in engine.run_turn(summary_prompt, None, agent=sess.get("agent", "kuro-core"),
                                        model=sess_mod, provider=sess_prov):
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
        "recent": recent,
        "rules": workspace_rules.inspect_workspace_rules(active, cfg),
    }


@app.get("/api/workspaces/rules")
def get_workspace_rules(path: str | None = None):
    cfg = engine.get_workspaces_config()
    ws = Path(path).resolve() if (path and Path(path).is_dir()) else engine.active_workspace_dir()
    info = workspace_rules.inspect_workspace_rules(ws, cfg)
    return {
        **info,
        "content": workspace_rules.read_rules(ws),
        "template": workspace_rules.KURO_STANDARD_TEMPLATE,
    }


@app.post("/api/workspaces/rules", dependencies=[Depends(local_only)])
async def save_workspace_rules(body: dict):
    cfg = engine.get_workspaces_config()
    p_str = (body.get("path") or "").strip()
    ws = Path(p_str).resolve() if p_str else engine.active_workspace_dir()
    mode = (body.get("mode") or "keep").strip().lower()
    try:
        info = workspace_rules.apply_workspace_rules(
            ws,
            mode=mode,
            ws_cfg=cfg,
            save_cfg_fn=engine.save_workspaces_config,
            content=body.get("content"),   # None = không đụng tới nội dung tệp quy tắc
        )
    except ValueError as e:
        raise HTTPException(400, str(e))
    except Exception as e:
        raise HTTPException(500, f"Không lưu được quy tắc dự án: {e}")

    await manager.broadcast_explorer({
        "type": "fs_changed",
        "workspace": str(ws),
        "ts": time.time(),
    })
    return {
        "ok": True,
        **info,
        "content": workspace_rules.read_rules(ws),
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
        "recent": recent,
        "rules": workspace_rules.inspect_workspace_rules(p, cfg),
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
                timeout=300,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0)
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
            return {
                "ok": True,
                "path": str(p),
                "name": name,
                "recent": recent,
                "rules": workspace_rules.inspect_workspace_rules(p, cfg),
            }
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
    ".db", ".sqlite", ".sqlite3",
    ".zip", ".rar", ".7z", ".tar", ".gz",
    ".exe", ".dll", ".bin", ".iso", ".msi",
    ".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp", ".ico"
}


def _find_in_root_recursive(rel_raw: str, root: Path, max_dirs: int = 4000) -> Path | None:
    """Tìm tệp hoặc thư mục theo đường dẫn tương đối/tên tệp (khớp hậu tố đường dẫn) bên trong `root`."""
    cleaned = (rel_raw or "").strip().strip("`'\"").replace("\\", "/").lstrip("./")
    parts = [p.lower() for p in cleaned.split("/") if p and p != "."]
    if not parts or not root.is_dir():
        return None
    target_name = parts[-1]
    n_parts = len(parts)
    skip_dirs = {".git", ".venv", "venv", "node_modules", "__pycache__", ".pytest_cache", ".archify"}
    matches: list[tuple[int, float, Path]] = []
    visited = 0
    try:
        for cur_root, dirs, files in os.walk(root):
            visited += 1
            if visited > max_dirs:
                break
            dirs[:] = [d for d in dirs if d not in skip_dirs and not (d.startswith(".") and d != ".attachments")]
            rel_dir = os.path.relpath(cur_root, root)
            dir_parts = [] if rel_dir == "." else [x.lower() for x in rel_dir.replace("\\", "/").split("/")]

            # Kiểm tra khớp tệp tin
            for fname in files:
                if fname.lower() != target_name:
                    continue
                cand_parts = dir_parts + [fname.lower()]
                if len(cand_parts) >= n_parts and cand_parts[-n_parts:] == parts:
                    fp = Path(cur_root) / fname
                    try:
                        mt = fp.stat().st_mtime
                    except OSError:
                        mt = 0.0
                    # Ưu tiên khớp tệp tin (score 2) > thư mục (score 1), rồi theo mtime mới nhất
                    matches.append((2, mt, fp.resolve()))

            # Kiểm tra khớp thư mục
            for dname in dirs:
                if dname.lower() != target_name:
                    continue
                cand_parts = dir_parts + [dname.lower()]
                if len(cand_parts) >= n_parts and cand_parts[-n_parts:] == parts:
                    dp = Path(cur_root) / dname
                    try:
                        mt = dp.stat().st_mtime
                    except OSError:
                        mt = 0.0
                    matches.append((1, mt, dp.resolve()))
    except Exception:
        pass
    if not matches:
        return None
    matches.sort(key=lambda x: (x[0], x[1]), reverse=True)
    return matches[0][2]


def resolve_fs_target(path: str) -> Path:
    """Xác định đường dẫn an toàn trong workspace, root dự án hoặc brain (hỗ trợ tìm tệp nằm trong thư mục con)."""
    raw = (path or "").strip().strip("`'\"")
    p = Path(raw)
    base = engine.active_workspace_dir().resolve()
    root_base = config.ROOT.resolve()
    brain_base = config.BRAIN.resolve()

    allowed_roots = [base, root_base, brain_base]
    recent_roots: list[Path] = []
    try:
        cfg = engine.get_workspaces_config()
        for r in (cfg.get("recent") or []):
            rp = (r.get("path") or "").strip() if isinstance(r, dict) else ""
            if rp and Path(rp).is_dir():
                rr = Path(rp).resolve()
                allowed_roots.append(rr)
                if str(rr).lower() != str(base).lower():
                    recent_roots.append(rr)
    except Exception:
        pass

    target = None
    if p.is_absolute():
        cand = p.resolve()
        if cand.exists():
            target = cand
        elif str(cand).lower().startswith(str(base).lower() + os.sep):
            # Đường dẫn tuyệt đối đoán thiếu thư mục con: thử tìm lại phần đuôi trong workspace
            tail = str(cand)[len(str(base)) + 1:]
            target = _find_in_root_recursive(tail, base)
    else:
        for b in (base, root_base, brain_base, *recent_roots):
            cand = (b / raw).resolve()
            if cand.exists():
                target = cand
                break
        if target is None:
            for b in (base, *recent_roots, root_base, brain_base):
                found = _find_in_root_recursive(raw, b)
                if found is not None:
                    target = found
                    break

    if target is None or not target.exists():
        raise HTTPException(404, f"Không tìm thấy tệp hoặc thư mục: {raw}")

    t_low = str(target).lower()
    allowed = any(t_low.startswith(str(ar).lower()) for ar in allowed_roots)
    if not allowed:
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


_BLOCKED_OPEN_EXTS = {
    ".exe", ".bat", ".cmd", ".com", ".msi", ".scr", ".vbs", ".vbe",
    ".ps1", ".wsf", ".reg", ".hta", ".pif", ".cpl"
}


def resolve_open_target(path: str) -> Path:
    """Chuẩn hóa đường dẫn tệp/thư mục trên máy cục bộ (tuyệt đối, UNC, file:///, hoặc tương đối/rút gọn trong dự án)."""
    from urllib.parse import unquote
    raw = (path or "").strip().strip("`'\"")
    base = engine.active_workspace_dir().resolve()
    if not raw:
        return base
    if raw.lower().startswith("file://"):
        u = urlparse(raw)
        if u.netloc and u.netloc.lower() != "localhost":
            # Đường dẫn UNC dạng file://server/share/path
            raw = "\\\\" + u.netloc + unquote(u.path).replace("/", "\\")
        else:
            p_str = unquote(u.path)
            if sys.platform == "win32" and re.match(r"^/[A-Za-z]:", p_str):
                p_str = p_str[1:]
            raw = p_str.replace("/", "\\") if sys.platform == "win32" else p_str
    # Loại bỏ hậu tố dòng như #L10-L20 nếu đến từ link markdown
    raw = re.sub(r"#L\d+(?:-L?\d+)?$", "", raw)

    p = Path(raw)
    if p.is_absolute() or raw.startswith("\\\\"):
        if p.exists():
            return p
        # Nếu là đường dẫn ghép thiếu thư mục con bên trong workspace đang mở -> tìm đệ quy theo phần đuôi
        if str(p).lower().startswith(str(base).lower() + os.sep):
            tail = str(p)[len(str(base)) + 1:]
            found = _find_in_root_recursive(tail, base)
            if found is not None:
                return found
        raise HTTPException(404, f"Không tìm thấy tệp hoặc thư mục trên máy: {raw}")

    recent_roots: list[Path] = []
    try:
        cfg = engine.get_workspaces_config()
        for r in (cfg.get("recent") or []):
            rp = (r.get("path") or "").strip() if isinstance(r, dict) else ""
            if rp and Path(rp).is_dir():
                rr = Path(rp).resolve()
                if str(rr).lower() != str(base).lower():
                    recent_roots.append(rr)
    except Exception:
        pass

    # 1. Kiểm tra đường dẫn trực tiếp
    for root in (base, config.ROOT.resolve(), config.BRAIN.resolve(), *recent_roots):
        cand = (root / raw).resolve()
        if cand.exists():
            return cand

    # 2. Tìm đệ quy theo hậu tố đường dẫn / tên tệp trong workspace đang mở, rồi workspace gần đây, rồi ROOT/BRAIN
    for root in (base, *recent_roots, config.ROOT.resolve(), config.BRAIN.resolve()):
        found = _find_in_root_recursive(raw, root)
        if found is not None:
            return found

    raise HTTPException(404, f"Không tìm thấy tệp hoặc thư mục: {raw}")


@app.get("/api/fs/resolve")
def resolve_fs_path_api(path: str = ""):
    """Giải đường dẫn rút gọn/tương đối thành đường dẫn đầy đủ thật trên đĩa (phục vụ tooltip rê chuột & menu mở tệp)."""
    try:
        target = resolve_open_target(path)
        return {"ok": True, "path": str(target), "is_dir": target.is_dir(), "name": target.name}
    except HTTPException:
        return {"ok": False, "path": path}


@app.post("/api/fs/open", dependencies=[Depends(local_only)])
def open_fs_item(body: dict):
    path = (body.get("path") or "").strip()
    open_with = bool(body.get("open_with"))
    target = resolve_open_target(path)
    try:
        if open_with and sys.platform == "win32":
            if target.is_dir():
                subprocess.Popen(["explorer.exe", str(target)])
            else:
                subprocess.Popen(["rundll32.exe", "shell32.dll,OpenAs_RunDLL", str(target)])
            return {"ok": True, "path": str(target), "mode": "open_with"}

        if target.is_file() and target.suffix.lower() in _BLOCKED_OPEN_EXTS:
            raise HTTPException(
                400,
                f"Tệp thực thi ({target.suffix}) không được chạy trực tiếp từ khung chat để đảm bảo an toàn. "
                "Hãy chọn 'Mở thư mục chứa tệp (Explorer)' để kiểm tra trước."
            )
        os.startfile(str(target))
        return {"ok": True, "path": str(target), "mode": "default"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Lỗi mở bằng Windows: {e}")


@app.post("/api/fs/reveal", dependencies=[Depends(local_only)])
def reveal_fs_item(body: dict):
    path = (body.get("path") or "").strip()
    target = resolve_open_target(path)
    try:
        if target.is_dir():
            subprocess.Popen(["explorer.exe", str(target)])
        elif sys.platform == "win32":
            # Chuẩn dòng lệnh Windows Explorer: /select,"<đường dẫn có khoảng trắng>"
            subprocess.Popen(f'explorer.exe /select,"{str(target)}"')
        else:
            subprocess.Popen(["explorer.exe", f"/select,{str(target)}"])
        return {"ok": True, "path": str(target)}
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
    if config.la_kho_mang(target):
        raise HTTPException(403, "Kuro không xóa tệp trên kho mạng công ty. Hãy tự xóa bằng tay trong Windows Explorer.")
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
    if not (is_local(sock.headers) and da_ghep(sock)):
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

            if req_type == "stop":
                target_sid = req.get("session")
                if target_sid and target_sid in session_chat_tasks:
                    task = session_chat_tasks.get(target_sid)
                    if task and not task.done():
                        task.cancel()
                    session_chat_tasks.pop(target_sid, None)
                    await manager.broadcast({
                        "type": "turn_stopped",
                        "session": target_sid,
                        "message": "_(Đã dừng phản hồi theo yêu cầu)_"
                    })
                continue

            if req_type == "fs_watch":
                manager.set_explorer_watching(sock, bool(req.get("active")))
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
            req_provider = (req.get("provider") or "").strip()
            if req_provider and req_provider not in config.PROVIDERS:
                req_provider = ""
            has_req_model = "model" in req and req.get("model") is not None
            req_model = (req.get("model") or "").strip() if has_req_model else None
            req_thinking = (req.get("thinking") or "").strip()

            # Ưu tiên provider/model gửi lên; nếu đổi provider mà không truyền model thì không mang model hãng cũ sang
            existing_sess = store.get(req.get("session")) if req.get("session") else None
            existing_provider = store.session_provider(existing_sess)
            agent_meta, _ = engine.agent_persona(agent)
            agent_prov = (agent_meta.get("provider") or "").strip()
            agent_model = (agent_meta.get("model") or "").strip()

            effective_provider = req_provider or existing_provider or agent_prov or (config.PROVIDER or "claude")
            switched_prov = bool(existing_provider and existing_provider != effective_provider)
            if has_req_model:
                effective_model = req_model or ""
            elif switched_prov:
                effective_model = ""
            else:
                effective_model = (existing_sess.get("model") if existing_sess else "") or (agent_model if effective_provider == agent_prov else "") or ""

            sid = store.ensure(req.get("session"), title=text, agent=agent, workspace=workspace,
                               model=effective_model, provider=effective_provider)
            if effective_provider != (existing_sess.get("provider") if existing_sess else "") or effective_model != (existing_sess.get("model") if existing_sess else ""):
                store.set_model(sid, effective_model, provider=effective_provider)

            # Cập nhật trạng thái active (phiên và thư mục làm việc, provider + model lưu riêng theo từng session)
            cur_st = get_active_state()
            cur_st["agent"] = agent
            cur_st["session"] = sid
            cur_st["workspace"] = workspace
            cur_st["workspace_name"] = Path(workspace).name
            save_active_state(cur_st)

            # Broadcast thông tin session & tin nhắn người dùng tới TẤT CẢ các thiết bị kết nối
            await manager.broadcast({
                "type": "session",
                "id": sid,
                "agent": agent,
                "workspace": workspace,
                "title": text,
                "provider": effective_provider,
                "model": effective_model
            })
            await manager.broadcast({
                "type": "user_message",
                "session": sid,
                "agent": agent,
                "workspace": workspace,
                "text": text,
                "attachments": req.get("attachments") or [],
                "provider": effective_provider,
                "model": effective_model
            })

            # Chạy phản hồi trong Task nền riêng biệt cho từng phiên (không làm nghẽn socket!)
            # Cho phép các phiên khác (kể cả khác nhà cung cấp AI: agy vs claude) chạy song song hoàn toàn độc lập!
            async def run_session_turn(session_id: str, prompt_text: str, session_agent: str, session_ws: str,
                                       session_provider: str, session_model: str | None, session_thinking: str = ""):
                try:
                    async def broadcast_chunk(chunk: dict):
                        payload = dict(chunk)
                        payload["session"] = session_id
                        payload["agent"] = session_agent
                        payload["workspace"] = session_ws
                        payload["provider"] = session_provider
                        await manager.broadcast(payload)

                    answer = await engine.chat(session_id, prompt_text, agent=session_agent, emit=broadcast_chunk,
                                               workspace=session_ws, model=session_model, provider=session_provider,
                                               thinking=session_thinking or None)

                    # Broadcast sự kiện hoàn tất lượt với toàn bộ nội dung câu trả lời hoàn chỉnh
                    await manager.broadcast({
                        "type": "turn_complete",
                        "session": session_id,
                        "agent": session_agent,
                        "workspace": session_ws,
                        "provider": session_provider,
                        "answer": answer
                    })

                    # Broadcast kết thúc phiên để đồng bộ lịch sử
                    await manager.broadcast({
                        "type": "session_saved",
                        "id": session_id,
                        "agent": session_agent,
                        "workspace": session_ws,
                        "provider": session_provider,
                        "model": session_model or "",
                        "title": prompt_text
                    })
                except asyncio.CancelledError:
                    # Người dùng bấm dừng phản hồi
                    await manager.broadcast({
                        "type": "turn_stopped",
                        "session": session_id,
                        "agent": session_agent,
                        "workspace": session_ws,
                        "message": "_(Đã dừng phản hồi theo yêu cầu)_"
                    })
                except Exception as ex:
                    await manager.broadcast({
                        "type": "turn_error",
                        "session": session_id,
                        "agent": session_agent,
                        "workspace": session_ws,
                        "error": str(ex)
                    })
                finally:
                    if session_chat_tasks.get(session_id) == this_turn_task:
                        session_chat_tasks.pop(session_id, None)

            # Nếu phiên này đang có task chạy trước đó thì dừng task cũ
            if sid in session_chat_tasks and not session_chat_tasks[sid].done():
                session_chat_tasks[sid].cancel()

            this_turn_task = asyncio.create_task(
                run_session_turn(sid, text, agent, workspace, effective_provider, effective_model, req_thinking)
            )
            session_chat_tasks[sid] = this_turn_task
    except WebSocketDisconnect:
        manager.disconnect(sock)
    except Exception:
        manager.disconnect(sock)


app.mount("/", StaticFiles(directory=config.ROOT / "dashboard", html=True), name="ui")

if __name__ == "__main__":
    winproc.an_cua_so()
    winproc.gop_tien_trinh_con()
    uvicorn.run(app, host=config.HOST, port=config.PORT)
