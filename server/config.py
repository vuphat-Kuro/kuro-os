"""Cấu hình đọc từ .env, và tạo khung brain lần đầu chạy."""
import difflib
import hashlib
import json
import os
import re
import secrets
import shutil
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")


def _path(key: str, default: str) -> Path:
    p = Path(os.getenv(key) or default)
    return p if p.is_absolute() else ROOT / p


STATE = _path("KURO_STATE_DIR", "state")
BRAIN = _path("KURO_BRAINS_DIR", "brains") / os.getenv("KURO_BRAIN", "Brain Default")
# Mặc định chỉ máy này dùng. Bật cho điện thoại (0.0.0.0) ở hộp /remote; thiết bị khác vẫn phải có mã ghép trong QR.
HOST = os.getenv("KURO_HOST", "127.0.0.1")
PORT = int(os.getenv("KURO_PORT", "7788"))
MCP_FILE = STATE / "mcp.json"
REMINDERS_FILE = STATE / "reminders.json"

# Đường dẫn dữ liệu dùng chung mạng Phương Thành
DATA_KTTC = os.getenv("KURO_DATA_KTTC", r"\\phuongthanhtranconsin.data.com\12.KỸ THUẬT THI CÔNG")
DATA_HD_DU_AN = os.getenv("KURO_DATA_HD_DU_AN", r"\\phuongthanhtranconsin.data.com\4.HÀNH CHÍNH QUẢN TRỊ\HỢP ĐỒNG KINH TẾ - HỢP ĐỒNG DỰ ÁN\HĐ các Dự án")
DATA_HD_THAU_PHU = os.getenv("KURO_DATA_HD_THAU_PHU", r"\\phuongthanhtranconsin.data.com\4.HÀNH CHÍNH QUẢN TRỊ\HỢP ĐỒNG KINH TẾ - HỢP ĐỒNG DỰ ÁN\Hợp đồng kinh tế - Linh\HỢP ĐỒNG")


def goc_kho_mang() -> set[str]:
    """Tên máy chủ kho mạng chung (chữ thường), lấy từ các đường dẫn UNC DATA_*."""
    return {d.lstrip("\\").split("\\")[0].lower() for d in (DATA_KTTC, DATA_HD_DU_AN, DATA_HD_THAU_PHU)
            if d.startswith("\\\\")}


def la_kho_mang(p) -> bool:
    """Đường dẫn nằm trên kho mạng chung công ty (Kuro cấm xóa). resolve() đổi ổ map (Y:) về UNC nên bắt cả ổ map."""
    s = str(Path(p).resolve()).lower()
    return any(g in s for g in goc_kho_mang())


# Chặn cứng xóa trên kho mạng, dùng chung cho hook của Claude Code (engine.py) và của agy (agy_chan_xoa.py).
# shortcut: dò theo chữ, không bắt được đường dẫn ghép từ nhiều mảnh; cần chắc tuyệt đối thì bỏ quyền xóa NTFS của tài khoản trên kho.
LENH_XOA = re.compile(r"(?i)\b(rm|rmdir|rd|del|erase|ri|mv|move|move-item|remove-item|unlink|rmtree|send2trash)\b"
                      r"|delete|/(mir|purge|mov)\b|os\.remove")
_KY_TU_O = re.compile(r"(?<!\w)([a-zA-Z]):")
DUOI_MA = (".py", ".ps1", ".psm1", ".bat", ".cmd", ".vbs", ".js", ".sh", ".bas", ".ipynb")
TU_CHOI_XOA_KHO = ("Kuro bị cấm xóa hay di chuyển tệp trên kho mạng công ty, kể cả khi người dùng yêu cầu. "
                   "Không thử cách khác: báo người dùng tự xóa bằng tay và ghi rõ đường dẫn.")


def nhac_kho_mang(text: str) -> bool:
    """Chuỗi có nhắc tới kho mạng: tên máy chủ, hoặc ổ map tới kho (X:, Y:...)."""
    low = text.lower()
    return (any(g in low for g in goc_kho_mang())
            or any(la_kho_mang(f"{o}:\\") for o in {m.upper() for m in _KY_TU_O.findall(text)}))


def xoa_tren_kho_mang(text: str) -> bool:
    """Lệnh/mã vừa có động từ xóa hay di chuyển vừa nhắc tới kho mạng."""
    return bool(LENH_XOA.search(text)) and nhac_kho_mang(text)


# AI chạy Kuro. Mọi hãng đều đi qua Claude Code (giữ nguyên skill, agent, tool): hãng khác Claude được trỏ tới
# bằng ANTHROPIC_BASE_URL vì họ có cổng tương thích Anthropic. URL lấy từ tài liệu chính thức của từng hãng.
PROVIDERS = {
    "antigravity": {"ten": "Google Antigravity (agy)", "short": "AGY", "group": "cli", "cli": "agy",
                    "goi_y": "Không cần key. Cài: mở PowerShell gõ: irm https://antigravity.google/cli/install.ps1 | iex, "
                             "rồi gõ agy một lần để đăng nhập Google. Muốn AI tự chạy lệnh thì thêm Bash ở Tool được phép."},
    "claude": {"ten": "Tài khoản Claude (gói Pro/Max)", "short": "Claude", "group": "cli",
               "goi_y": "Không cần key. Mở PowerShell gõ: claude auth login"},
    # Bộ não chạy bằng chương trình riêng của hãng (server/cli_engines.py), không qua Claude Code.
    "chatgpt": {"ten": "Tài khoản ChatGPT (qua Codex)", "short": "Codex", "group": "cli", "cli": "codex",
                "goi_y": "Không cần key. Cài: npm install -g @openai/codex, rồi mở PowerShell gõ: codex login "
                         "và chọn Sign in with ChatGPT. Muốn AI tự chạy script tính toán thì thêm Bash ở Tool được phép."},
    "anthropic": {"ten": "Anthropic API key", "short": "Anthropic", "group": "api", "key": True,
                  "goi_y": "Lấy key ở console.anthropic.com. Tính tiền theo token."},
    "openrouter": {"ten": "OpenRouter (GPT, Gemini, Claude... một key)", "short": "OpenRouter", "group": "api",
                   "url": "https://openrouter.ai/api", "key": True,
                   "goi_y": "Lấy key ở openrouter.ai/keys. Model: chép tên ở openrouter.ai/models; để trống = Claude."},
    "deepseek": {"ten": "DeepSeek", "short": "DeepSeek", "group": "api", "url": "https://api.deepseek.com/anthropic", "key": True,
                 "goi_y": "Lấy key ở platform.deepseek.com. Tên model xem ở api-docs.deepseek.com."},
    "zai": {"ten": "GLM (Z.ai)", "short": "GLM", "group": "api", "url": "https://api.z.ai/api/anthropic", "key": True,
            "goi_y": "Lấy key ở z.ai. Tên model GLM xem ở docs.z.ai."},
    "kimi": {"ten": "Kimi (Moonshot)", "short": "Kimi", "group": "api", "url": "https://api.moonshot.ai/anthropic", "key": True,
             "goi_y": "Lấy key ở platform.kimi.ai. Tên model xem ở trang Kimi."},
    "ollama": {"ten": "Ollama trên máy (miễn phí, chạy offline)", "short": "Ollama", "group": "api",
               "url": "http://localhost:11434",
               "goi_y": "Cài Ollama (ollama.com) bản 0.14 trở lên, tải model rồi điền tên, vd qwen3-coder."},
    "custom": {"ten": "Máy chủ khác tương thích Anthropic", "short": "Custom", "group": "api", "key": True,
               "goi_y": "Điền địa chỉ, key và model."},
}
_MODEL_ENVS = ("ANTHROPIC_MODEL", "ANTHROPIC_DEFAULT_OPUS_MODEL", "ANTHROPIC_DEFAULT_SONNET_MODEL",
               "ANTHROPIC_DEFAULT_HAIKU_MODEL", "CLAUDE_CODE_SUBAGENT_MODEL")


def key_key(provider: str) -> str:
    """Mỗi hãng API một khóa API key riêng trong .env để bật nhiều hãng song song không bị ghi đè."""
    return f"KURO_AI_KEY_{(provider or 'claude').upper()}"


def url_key(provider: str) -> str:
    """Mỗi hãng một khóa Base URL riêng trong .env."""
    return f"KURO_BASE_URL_{(provider or 'claude').upper()}"


def get_provider_model(provider: str | None = None) -> str:
    """Lấy model mặc định của một provider cụ thể (fallback MODEL toàn cục nếu cùng provider hiện hành)."""
    if provider is None:
        return MODEL
    prov = provider or "claude"
    cur = PROVIDER or "claude"
    val = os.getenv(model_key(prov), "")
    return val if (val or prov != cur) else MODEL


def get_provider_key(provider: str | None = None) -> str:
    """Lấy API key của một provider cụ thể (ưu tiên khóa riêng KURO_AI_KEY_<PROVIDER>, fallback KURO_AI_KEY cũ)."""
    if provider is None:
        prov = PROVIDER or "claude"
        return os.getenv(key_key(prov), "") or AI_KEY
    prov = provider or "claude"
    val = os.getenv(key_key(prov), "")
    if val:
        return val
    if prov == (PROVIDER or "claude"):
        return AI_KEY
    return ""


def get_provider_url(provider: str | None = None) -> str:
    """Lấy địa chỉ máy chủ của một provider cụ thể (ưu tiên khóa riêng, fallback KURO_BASE_URL cũ)."""
    if provider is None:
        prov = PROVIDER or "claude"
        return os.getenv(url_key(prov), "") or BASE_URL
    prov = provider or "claude"
    val = os.getenv(url_key(prov), "")
    if val:
        return val
    if prov == (PROVIDER or "claude"):
        return BASE_URL
    return ""


def provider_env(model_override: str | None = None, provider: str | None = None) -> dict[str, str]:
    """Biến môi trường cho tiến trình Claude Code theo AI đã chọn; đè lên biến sẵn có của máy."""
    prov = PROVIDER if provider is None else provider
    p = PROVIDERS.get(prov) or PROVIDERS["claude"]
    if prov in ("", "claude") or p.get("cli"):
        return {}
    ai_key = get_provider_key(provider)
    if prov == "anthropic":
        return {"ANTHROPIC_API_KEY": ai_key}
    # API_KEY rỗng để Claude Code không quay về đăng nhập Anthropic; model con và model nền cũng phải là model
    # của hãng đó, nếu không Claude Code sẽ gọi tên claude-haiku mà hãng không có.
    base_url = get_provider_url(provider)
    eff_model = model_override or get_provider_model(provider)
    env = {"ANTHROPIC_BASE_URL": base_url or p.get("url", ""), "ANTHROPIC_AUTH_TOKEN": ai_key or "ollama",
           "ANTHROPIC_API_KEY": ""}
    return env | ({k: eff_model for k in _MODEL_ENVS} if eff_model else {})


# Bí danh model mà Claude Code nhận (dùng thật từ bản 1.0); tên đầy đủ "claude-..." cũng hợp lệ.
CLAUDE_MODELS = [
    {"id": "", "ten": "Mặc định"},
    {"id": "opus", "ten": "Opus 5.5"},
    {"id": "sonnet", "ten": "Sonnet 5.5"},
    {"id": "fable", "ten": "Fable 5.2"},
    {"id": "haiku", "ten": "Haiku 5.5"},
]


def model_key(provider: str) -> str:
    """Mỗi AI một khóa model riêng trong .env; AI chưa chọn coi là claude."""
    return f"KURO_MODEL_{(provider or 'claude').upper()}"


def model_error(provider: str, model: str, agy_models: list[dict]) -> str:
    """Câu lỗi tiếng Việt nếu model không dùng được với AI có danh sách; rỗng nếu hợp lệ hoặc không kiểm được."""
    provider = provider or "claude"
    if not model:
        return ""
    if provider == "claude":
        ids = [m["id"] for m in CLAUDE_MODELS if m["id"]]
        if model in ids or model.startswith("claude-"):
            return ""
        goi_y = ", ".join(ids) + " (hoặc tên bắt đầu claude-)"
    elif provider == "antigravity" and agy_models:   # không lấy được danh sách thì không chặn
        ids = [m["id"] for m in agy_models]
        if model.lower() in (i.lower() for i in ids):   # đo thật: agy 1.3.3 nhận tên không phân biệt hoa thường
            return ""
        goi_y = ", ".join(difflib.get_close_matches(model, ids, n=3, cutoff=0.4) or ids[:5])
    else:
        return ""
    return f'Model "{model}" không dùng được với {PROVIDERS[provider]["ten"]}. Chọn: Mặc định, {goi_y}.'


def migrate_model() -> None:
    """Máy cài bản cũ có một KURO_MODEL chung: hợp lệ với AI đang chọn thì chuyển sang khóa của AI đó, rồi xoá trắng.
    Antigravity coi là hợp lệ vì lúc khởi động chưa lấy được danh sách (lúc lưu lần sau mới chặn)."""
    old = os.getenv("KURO_MODEL", "")
    if not old:
        return
    keep = not model_error(PROVIDER, old, []) and not os.getenv(model_key(PROVIDER))
    save_env(({model_key(PROVIDER): old} if keep else {}) | {"KURO_MODEL": ""})
    print(f"[model] chuyển KURO_MODEL cũ '{old}': " + (f"giữ cho {PROVIDER or 'claude'}" if keep else "bỏ (không hợp lệ)"))


def migrate_provider_creds() -> None:
    """Chuyển KURO_AI_KEY / KURO_BASE_URL dùng chung của bản cũ sang khóa riêng cho hãng đang chọn."""
    prov = PROVIDER
    if not prov or prov not in PROVIDERS:
        return
    updates = {}
    old_key = os.getenv("KURO_AI_KEY", "")
    if old_key and PROVIDERS[prov].get("key") and not os.getenv(key_key(prov)):
        updates[key_key(prov)] = old_key
    old_url = os.getenv("KURO_BASE_URL", "")
    if old_url and not PROVIDERS[prov].get("cli") and prov != "claude" and not os.getenv(url_key(prov)):
        updates[url_key(prov)] = old_url
    if updates:
        save_env(updates)


def _cli_available(provider: str) -> bool:
    """Kiểm tra nhanh CLI của hãng đã cài sẵn trên máy chưa (không chặn I/O)."""
    if provider == "claude":
        return bool(shutil.which("claude"))
    if provider == "antigravity":
        extra = Path(os.getenv("LOCALAPPDATA", "")) / "agy" / "bin" / "agy.exe"
        return bool(shutil.which("agy") or extra.is_file())
    if provider == "chatgpt":
        return bool(shutil.which("codex"))
    return False


def enabled_providers() -> list[str]:
    """Danh sách nhà cung cấp AI đang bật đồng thời để chọn nhanh ngay trong khung chat.

    - Nếu người dùng đã lưu KURO_ENABLED_PROVIDERS trong .env: dùng đúng danh sách đó (luôn giữ PROVIDER mặc định).
    - Nếu chưa từng cấu hình: tự động bật PROVIDER mặc định + các CLI đã cài sẵn trên máy (agy, claude, codex)
      và các hãng API đã có sẵn key riêng trong .env.
    """
    raw = os.getenv("KURO_ENABLED_PROVIDERS", "").strip()
    out: list[str] = []
    if raw:
        for item in raw.split(","):
            p = item.strip()
            if p in PROVIDERS and p not in out:
                out.append(p)
    else:
        if PROVIDER in PROVIDERS:
            out.append(PROVIDER)
        for p in ("antigravity", "claude", "chatgpt"):
            if p not in out and _cli_available(p):
                out.append(p)
        for p, info in PROVIDERS.items():
            if p not in out and info.get("key") and os.getenv(key_key(p)):
                out.append(p)
    if PROVIDER in PROVIDERS and PROVIDER not in out:
        out.insert(0, PROVIDER)
    if not out:
        out.append("claude")
    return out


def load_runtime() -> None:
    """Các giá trị sửa được lúc đang chạy (mục Cài đặt), đọc lại từ os.environ."""
    global MODEL, ALLOWED_TOOLS, TG_TOKEN, TG_OWNERS, PROVIDER, AI_KEY, BASE_URL, ENABLED_PROVIDERS, DATA_KTTC, DATA_HD_DU_AN, DATA_HD_THAU_PHU
    if not os.getenv("ANTHROPIC_API_KEY"):
        os.environ.pop("ANTHROPIC_API_KEY", None)   # dòng trống trong .env không được che phiên đăng nhập Claude
    PROVIDER = os.getenv("KURO_PROVIDER", "")       # trống = chưa chọn: giao diện mở màn hình chọn AI
    AI_KEY = os.getenv("KURO_AI_KEY", "")
    BASE_URL = os.getenv("KURO_BASE_URL", "")
    MODEL = os.getenv(model_key(PROVIDER), "")      # luôn là model của AI đang chọn (specs/001)
    ENABLED_PROVIDERS = enabled_providers()
    # Tool không có trong danh sách này bị CLI từ chối (permission_mode=dontAsk): quyền được chặn bằng code.
    ALLOWED_TOOLS = [t.strip() for t in os.getenv(
        "KURO_ALLOWED_TOOLS", "Read,Glob,Grep,Write,Edit,WebSearch,WebFetch,Bash,mcp__kuro__tinh_python").split(",") if t.strip()]
    TG_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
    TG_OWNERS = {int(x) for x in os.getenv("TELEGRAM_OWNER_IDS", "").replace(" ", "").split(",") if x}
    DATA_KTTC = os.getenv("KURO_DATA_KTTC", r"\\phuongthanhtranconsin.data.com\12.KỸ THUẬT THI CÔNG")
    DATA_HD_DU_AN = os.getenv("KURO_DATA_HD_DU_AN", r"\\phuongthanhtranconsin.data.com\4.HÀNH CHÍNH QUẢN TRỊ\HỢP ĐỒNG KINH TẾ - HỢP ĐỒNG DỰ ÁN\HĐ các Dự án")
    DATA_HD_THAU_PHU = os.getenv("KURO_DATA_HD_THAU_PHU", r"\\phuongthanhtranconsin.data.com\4.HÀNH CHÍNH QUẢN TRỊ\HỢP ĐỒNG KINH TẾ - HỢP ĐỒNG DỰ ÁN\Hợp đồng kinh tế - Linh\HỢP ĐỒNG")


load_runtime()

_PROV_ALT = "|".join(PROVIDERS)
# Khóa sửa từ giao diện: tên -> (bí mật?, regex hợp lệ). Bí mật chỉ trả về dạng che, không bao giờ trả nguyên văn.
SETTINGS = {
    "KURO_PROVIDER": (False, f"({_PROV_ALT})?"),
    "KURO_ENABLED_PROVIDERS": (False, rf"(({_PROV_ALT})(,({_PROV_ALT}))*)?"),
    "KURO_AI_KEY": (True, r"[\w.:-]*"),
    "KURO_BASE_URL": (False, r"(https?://[\w.:/-]+)?"),
    "KURO_MODEL": (False, r"[\w.:/\[\]-]*"),
    "KURO_ALLOWED_TOOLS": (False, r"[\w-]+(,[\w-]+)*"),
    "TELEGRAM_BOT_TOKEN": (True, r"(\d+:[\w-]+)?"),
    "TELEGRAM_OWNER_IDS": (False, r"(\d+(,\d+)*)?"),
    "KURO_HOST": (False, r"(127\.0\.0\.1|0\.0\.0\.0)?"),
    "KURO_DATA_KTTC": (False, r".*"),
    "KURO_DATA_HD_DU_AN": (False, r".*"),
    "KURO_DATA_HD_THAU_PHU": (False, r".*"),
}
for _p in PROVIDERS:
    SETTINGS[model_key(_p)] = (False, r"[\w.:/\[\]-]*")
    SETTINGS[key_key(_p)] = (True, r"[\w.:-]*")
    SETTINGS[url_key(_p)] = (False, r"(https?://[\w.:/-]+)?")


def remote_token() -> str:
    """Mã ghép điện thoại: tạo một lần, lưu ở state/, chỉ đưa ra qua mã QR trên máy này."""
    f = STATE / "remote_token.txt"
    if not f.exists():
        f.write_text(secrets.token_urlsafe(24), encoding="utf-8")
    return f.read_text(encoding="utf-8").strip()


def save_env(updates: dict[str, str]) -> None:
    """Ghi khóa vào .env (giữ chú thích và thứ tự, khóa mới thêm cuối file) rồi áp dụng ngay."""
    env = ROOT / ".env"
    lines = env.read_text(encoding="utf-8").splitlines() if env.exists() else []
    left = dict(updates)
    for i, line in enumerate(lines):
        k = line.split("=", 1)[0].strip()
        if k in left and not line.lstrip().startswith("#"):
            lines[i] = f"{k}={left.pop(k)}"
    lines += [f"{k}={v}" for k, v in left.items()]
    env.write_text("\n".join(lines) + "\n", encoding="utf-8")
    os.environ.update(updates)
    load_runtime()

BRAIN_CLAUDE_MD = """# Brain của Kuro

- `memory/MEMORY.md`: mục lục ký ức, mỗi dòng trỏ tới một file trong `memory/facts/`.
- Gặp thông tin bền vững về người dùng (nghề, dự án, sở thích, quyết định) thì ghi một file
  `memory/facts/<slug>.md` (frontmatter `type: user|preference|business|decision`) và thêm 1 dòng vào MEMORY.md.
  Trùng thì sửa file cũ, không tạo bản sao.
- `sources/`: tài liệu gốc người dùng đưa vào, chỉ đọc. `wiki/`: tri thức đã chưng cất, có `[[liên kết]]`.
- Skill nằm ở `.claude/skills/<slug>/SKILL.md`.
"""


def ensure_dirs() -> None:
    STATE.mkdir(parents=True, exist_ok=True)
    for sub in ("memory/facts", "sources", "wiki", ".claude/skills", "agents"):
        (BRAIN / sub).mkdir(parents=True, exist_ok=True)
    mem = BRAIN / "memory" / "MEMORY.md"
    if not mem.exists():
        mem.write_text("# Ký ức\n\n", encoding="utf-8")
    md = BRAIN / "CLAUDE.md"
    if not md.exists():
        md.write_text(BRAIN_CLAUDE_MD, encoding="utf-8")
    migrate_model()
    migrate_provider_creds()
    sync_bundled()


def _hash(p: Path) -> str:
    h = hashlib.sha256()
    files = [p] if p.is_file() else [f for f in p.rglob("*") if f.is_file() and "__pycache__" not in f.parts]
    for f in sorted(files):
        h.update(f.relative_to(p.parent).as_posix().encode())
        h.update(f.read_bytes())
    return h.hexdigest()


def sync_bundled() -> None:
    """Chép skill/agent đi kèm mã nguồn vào brain; bản mới (sau cap-nhat.bat) thay bản cũ.

    Bản người dùng đã tự sửa thì giữ nguyên: chỉ thay khi bản trong brain còn đúng y bản Kuro đã chép lần
    trước (dấu vân tay lưu ở state/goi-kem.json), nên không bao giờ mất chỉnh sửa của người dùng.
    """
    log = STATE / "goi-kem.json"
    seen = json.loads(log.read_text(encoding="utf-8")) if log.is_file() else {}
    pairs = [(s.parent, BRAIN / ".claude" / "skills" / s.parent.name) for s in (ROOT / "skills").glob("*/SKILL.md")]
    pairs += [(a, BRAIN / "agents" / a.name) for a in (ROOT / "agents").glob("*.md")]
    goi = STATE / "goi-cai.json"   # gói tiện ích tùy chọn (server/goi.py): chỉ gói người dùng đã yêu cầu cài
    for gid, g in (json.loads(goi.read_text(encoding="utf-8")) if goi.is_file() else {}).items():
        base = (STATE / "plugins" / gid) if g.get("nguon") == "external" else (ROOT / "goi" / gid)
        skills = g.get("skills") or ([g["skill"]] if g.get("skill") else [])
        for s in skills:
            if (base / s).is_dir():
                pairs.append((base / s, BRAIN / ".claude" / "skills" / s))
        for a in (g.get("agents") or []):
            if (base / "agents" / a).is_file():
                pairs.append((base / "agents" / a, BRAIN / "agents" / a))
    for src, dst in pairs:
        key, new = f"{src.parent.name}/{src.name}", _hash(src)
        if dst.exists():
            cur = _hash(dst)
            if cur == new:
                seen[key] = new
                continue
            if seen.get(key) != cur:
                print(f"[goi-kem] giữ bản bạn đã sửa: {dst.name}")
                continue
            shutil.rmtree(dst) if dst.is_dir() else dst.unlink()
        shutil.copytree(src, dst) if src.is_dir() else shutil.copy2(src, dst)
        seen[key] = new
    log.write_text(json.dumps(seen, indent=1, ensure_ascii=False), encoding="utf-8")


def cua_so_ngu_canh(provider: str | None = None, model: str | None = None) -> int:
    """Cửa sổ ngữ cảnh khi Claude Code không biết (AI chạy bằng CLI riêng, model ngoài họ Claude) hoặc hỏi lỗi.
    Nguồn: Claude 5.x đo thật bằng Claude Code; Codex đo bằng `codex debug models`; Agy do người dùng chốt 1M;
    DeepSeek, GLM, Kimi lấy từ tài liệu chính thức (api-docs.deepseek.com, docs.z.ai, platform.kimi.ai), tra 2026-11.
    Đặt KURO_CONTEXT_WINDOW_<AI viết hoa> trong .env để ghi đè."""
    prov = (provider or PROVIDER or "claude").lower()
    mod = (model or get_provider_model(prov) or "").lower()
    ov = os.getenv(f"KURO_CONTEXT_WINDOW_{prov.upper()}", "").strip()
    if ov.isdigit() and int(ov) > 0:
        return int(ov)
    if prov == "antigravity":
        return 1_000_000
    if prov in ("claude", "anthropic") or mod.startswith("claude") or mod in ("opus", "sonnet", "haiku", "fable"):
        return 200_000 if re.match(r"claude-(?:(?:opus|sonnet|haiku)-)?[34](?:[-.]|$)", mod) else 1_000_000
    if prov == "chatgpt" or "gpt" in mod:
        return 272_000
    if prov == "deepseek" or "deepseek" in mod:
        return 1_048_576
    if prov == "zai" or "glm" in mod:
        return 1_000_000 if re.search(r"glm-5\.[23]", mod) else 200_000
    if prov == "kimi" or "kimi" in mod:
        return 1_048_576 if "k3" in mod else 262_144
    if "gemini" in mod:
        return 1_000_000
    if prov == "ollama":
        return 32_000
    return 200_000


def nguong_ngu_canh(provider: str | None = None, model: str | None = None) -> int:
    """Token mỗi lần gọi mà Kuro coi là quá nặng: báo đỏ và lượt sau tự mở hội thoại mới với AI.
    Mặc định 80% cửa sổ của model đang dùng (ngữ cảnh không bao giờ chạm 100%); KURO_NGUONG_NGU_CANH=<phần trăm> để chỉnh.
    Ngưỡng cố định 100k cũ quá thấp với model 1M: đọc vài trang PDF là nhảy hội thoại sau 1-2 câu (phản hồi 26/11/2026)."""
    try:
        pt = float(os.getenv("KURO_NGUONG_NGU_CANH", "80"))
    except ValueError:
        pt = 80.0
    return int(cua_so_ngu_canh(provider, model) * min(max(pt, 10.0), 95.0) / 100)
