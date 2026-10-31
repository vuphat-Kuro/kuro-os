"""Cấu hình đọc từ .env, và tạo khung brain lần đầu chạy."""
import hashlib
import json
import os
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
HOST = os.getenv("KURO_HOST", "127.0.0.1")
PORT = int(os.getenv("KURO_PORT", "7788"))
MCP_FILE = STATE / "mcp.json"
REMINDERS_FILE = STATE / "reminders.json"


def load_runtime() -> None:
    """Các giá trị sửa được lúc đang chạy (mục Cài đặt), đọc lại từ os.environ."""
    global MODEL, ALLOWED_TOOLS, TG_TOKEN, TG_OWNERS
    if not os.getenv("ANTHROPIC_API_KEY"):
        os.environ.pop("ANTHROPIC_API_KEY", None)   # dòng trống trong .env không được che phiên đăng nhập Claude
    MODEL = os.getenv("KURO_MODEL", "")
    # Tool không có trong danh sách này bị CLI từ chối (permission_mode=dontAsk): quyền được chặn bằng code.
    ALLOWED_TOOLS = [t.strip() for t in os.getenv(
        "KURO_ALLOWED_TOOLS", "Read,Glob,Grep,Write,Edit,WebSearch,WebFetch,mcp__kuro__tinh_python").split(",") if t.strip()]
    TG_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
    TG_OWNERS = {int(x) for x in os.getenv("TELEGRAM_OWNER_IDS", "").replace(" ", "").split(",") if x}


load_runtime()

# Khóa sửa từ giao diện: tên -> (bí mật?, regex hợp lệ). Bí mật chỉ trả về dạng che, không bao giờ trả nguyên văn.
SETTINGS = {
    "ANTHROPIC_API_KEY": (True, r"(sk-ant-[\w-]+)?"),
    "KURO_MODEL": (False, r"(sonnet|opus|haiku|claude-[\w.-]+)?"),
    "KURO_ALLOWED_TOOLS": (False, r"[\w-]+(,[\w-]+)*"),
    "TELEGRAM_BOT_TOKEN": (True, r"(\d+:[\w-]+)?"),
    "TELEGRAM_OWNER_IDS": (False, r"(\d+(,\d+)*)?"),
}


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
