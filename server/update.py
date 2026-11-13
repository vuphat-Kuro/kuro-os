"""Kiểm tra và cập nhật phiên bản Kuro (semver, git upstream & GitHub raw).
Tham khảo kiến trúc cập nhật độc lập của Javis OS.
"""
import asyncio
import datetime
import json
import os
import re
import subprocess
import sys
import urllib.request
from pathlib import Path

import config

GITHUB_REPO = "vuphat-Kuro/kuro-os"
STATE_DIR = config.ROOT / "state"
STATE_FILE = STATE_DIR / "update_state.json"
LOG_FILE = STATE_DIR / "update.log"
VERSION_FILE = config.ROOT / "VERSION"


def ver_tuple(s: str) -> tuple[int, ...] | None:
    """Chuyển chuỗi phiên bản 'v1.4.0' hoặc '1.4.0' thành tuple (1, 4, 0)."""
    try:
        parts = [int(x) for x in re.split(r"[.\-]", (s or "").strip().lstrip("vV"))[:3] if x.isdigit()]
        while len(parts) < 3:
            parts.append(0)
        return tuple(parts[:3])
    except Exception:
        return None


def ver_newer(latest: str, cur: str) -> bool:
    """So sánh semver: latest có mới hơn cur không?"""
    lt, ct = ver_tuple(latest), ver_tuple(cur)
    if lt is None or ct is None:
        return False
    return lt > ct


def get_current_version() -> str:
    """Đọc phiên bản hiện tại từ file VERSION."""
    try:
        if VERSION_FILE.exists():
            return VERSION_FILE.read_text(encoding="utf-8").strip()
    except Exception:
        pass
    return "1.0.0"


def set_version(new_version: str) -> str:
    """Đặt số phiên bản mới cho Kuro (ghi vào file VERSION và cập nhật STATUS)."""
    v = (new_version or "").strip().lstrip("vV")
    if not re.match(r"^\d+(\.\d+)*$", v):
        raise ValueError(f"Số phiên bản '{new_version}' không hợp lệ (ví dụ đúng: 1.4.0, 1.4.1)")
    VERSION_FILE.write_text(v + "\n", encoding="utf-8")
    STATUS["current"] = v
    check(force=False)
    return v


STATUS = {
    "current": get_current_version(),
    "latest": get_current_version(),
    "behind": 0,
    "update_available": False,
    "notes": [],
    "repo": GITHUB_REPO,
    "branch": "main",
    "last_checked": None,
    "error": None,
}


def _git(*args: str) -> str:
    env = {**os.environ, "GIT_TERMINAL_PROMPT": "0", "GCM_INTERACTIVE": "never"}
    r = subprocess.run(
        ["git", *args],
        cwd=config.ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=60,
        env=env,
    )
    if r.returncode:
        raise RuntimeError(r.stderr.strip() or f"git {args[0]} lỗi {r.returncode}")
    return r.stdout.strip()


def _fetch_raw_github_version() -> str | None:
    """Hỏi raw GitHub để lấy VERSION mới nhất trên main."""
    try:
        url = f"https://raw.githubusercontent.com/{GITHUB_REPO}/main/VERSION"
        req = urllib.request.Request(url, headers={"User-Agent": "Kuro-OS"})
        with urllib.request.urlopen(req, timeout=6) as resp:
            if resp.status == 200:
                return resp.read().decode("utf-8").strip()
    except Exception:
        pass
    return None


def _parse_changelog_text(text: str, version: str) -> list[str]:
    """Trích xuất các dòng mô tả của phiên bản từ nội dung CHANGELOG.md."""
    lines = []
    in_ver = False
    v_clean = version.strip().lstrip("vV")
    for line in text.splitlines():
        if re.match(rf"^##\s*\[?v?{re.escape(v_clean)}\]?", line, re.IGNORECASE):
            in_ver = True
            continue
        elif in_ver and line.startswith("## "):
            break
        elif in_ver:
            stripped = line.strip()
            if stripped.startswith("- ") or stripped.startswith("* "):
                lines.append(stripped[2:].strip())
    return lines


def _fetch_raw_github_changelog(version: str) -> list[str]:
    """Hỏi raw GitHub để lấy nội dung mô tả của phiên bản trong CHANGELOG.md."""
    try:
        url = f"https://raw.githubusercontent.com/{GITHUB_REPO}/main/CHANGELOG.md"
        req = urllib.request.Request(url, headers={"User-Agent": "Kuro-OS"})
        with urllib.request.urlopen(req, timeout=6) as resp:
            if resp.status == 200:
                return _parse_changelog_text(resp.read().decode("utf-8"), version)
    except Exception:
        pass
    return []


def read_state() -> dict:
    try:
        if STATE_FILE.exists():
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except Exception:
        pass
    return {"phase": "idle", "result": None, "error": None}


def write_state(patch: dict) -> dict:
    st = read_state()
    st.update(patch)
    try:
        STATE_DIR.mkdir(parents=True, exist_ok=True)
        STATE_FILE.write_text(json.dumps(st, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception:
        pass
    return st


def read_log_tail(n: int = 50) -> str:
    try:
        if LOG_FILE.exists():
            lines = LOG_FILE.read_text(encoding="utf-8", errors="replace").splitlines()
            return "\n".join(lines[-n:])
    except Exception:
        pass
    return ""


def check(force: bool = False) -> dict:
    """Kiểm tra xem có bản mới trên GitHub không."""
    cur = get_current_version()
    latest = cur
    behind = 0
    notes: list[str] = []
    err = None

    # 1. Thử qua git upstream nếu là git checkout
    if (config.ROOT / ".git").exists():
        try:
            _git("fetch", "--quiet")
            behind = int(_git("rev-list", "--count", "HEAD..@{u}"))
            if behind > 0:
                try:
                    latest = _git("show", "@{u}:VERSION").strip()
                except Exception:
                    latest = cur
                notes = _git("log", "--format=%s", "-10", "HEAD..@{u}").splitlines()
        except Exception as e:
            err = f"git: {e}"

    # 2. Dự phòng: hỏi raw github nếu git chưa lấy được bản mới hoặc bị lỗi
    if not ver_newer(latest, cur) and behind == 0:
        raw_v = _fetch_raw_github_version()
        if raw_v and ver_newer(raw_v, cur):
            latest = raw_v

    avail = (behind > 0) or ver_newer(latest, cur)

    # 3. Lấy mô tả chi tiết nếu có bản mới mà notes còn rỗng
    if avail and not notes:
        if (config.ROOT / ".git").exists():
            try:
                ch_text = _git("show", "@{u}:CHANGELOG.md")
                notes = _parse_changelog_text(ch_text, latest)
            except Exception:
                pass
        if not notes:
            ch_file = config.ROOT / "CHANGELOG.md"
            if ch_file.exists():
                notes = _parse_changelog_text(ch_file.read_text(encoding="utf-8"), latest)
        if not notes:
            notes = _fetch_raw_github_changelog(latest)

    STATUS.update(
        current=cur,
        latest=latest,
        behind=behind,
        update_available=bool(avail),
        notes=notes,
        last_checked=datetime.datetime.now().isoformat(timespec="seconds"),
        error=err,
    )
    return STATUS


def get_status() -> dict:
    return STATUS


_UPDATE_ACTIVE = {"preparing", "pulling", "installing", "restarting"}


def start_update() -> dict:
    """Khởi chạy tiến trình cập nhật bản mới độc lập."""
    st = read_state()
    if st.get("phase") in _UPDATE_ACTIVE:
        started_at = st.get("started_at")
        if started_at:
            try:
                dt = datetime.datetime.fromisoformat(started_at)
                if (datetime.datetime.now() - dt).total_seconds() < 600:
                    return {"ok": False, "error": "Đang có tiến trình cập nhật đang chạy, vui lòng chờ."}
            except Exception:
                pass

    now_iso = datetime.datetime.now().isoformat(timespec="seconds")
    cur = get_current_version()
    target = STATUS.get("latest") or cur

    write_state({
        "phase": "preparing",
        "old_version": cur,
        "target_version": target,
        "result": None,
        "error": None,
        "started_at": now_iso,
        "finished_at": None,
    })

    try:
        py = str(config.ROOT / ".venv" / "Scripts" / "python.exe")
        if not Path(py).exists():
            py = sys.executable
        updater_script = str(config.ROOT / "server" / "updater.py")
        port = os.getenv("KURO_PORT", "7788")
        args = [
            py,
            updater_script,
            "--old-version", cur,
            "--target", target,
            "--port", str(port),
            "--server-pid", str(os.getpid()),
        ]

        if os.name == "nt":
            # DETACHED_PROCESS (0x00000008) | CREATE_NEW_PROCESS_GROUP (0x00000200)
            subprocess.Popen(args, cwd=str(config.ROOT), creationflags=0x00000008 | 0x00000200)
        else:
            subprocess.Popen(args, cwd=str(config.ROOT), start_new_session=True)

        return {"ok": True, "message": "Đã khởi động tiến trình cập nhật Kuro."}
    except Exception as e:
        write_state({"phase": "idle", "result": "error", "error": str(e), "finished_at": now_iso})
        return {"ok": False, "error": str(e)}


async def loop(notify=None) -> None:
    """Kiểm tra lúc khởi động rồi 6 giờ một lần; có bản mới thì báo Telegram."""
    told = None
    while True:
        try:
            await asyncio.to_thread(check)
            if notify and STATUS["update_available"] and STATUS["latest"] != told:
                told = STATUS["latest"]
                msg = f"🚀 Kuro có phiên bản mới {told} (bạn đang dùng {STATUS['current']}):"
                if STATUS["notes"]:
                    msg += "\n- " + "\n- ".join(STATUS["notes"])
                msg += "\n\nMở Kuro trên trình duyệt để bấm 'Cập nhật ngay' hoặc chạy cap-nhat.bat."
                await notify(msg)
        except Exception as e:
            print(f"[cap-nhat] chưa kiểm tra được: {e}")
        await asyncio.sleep(6 * 3600)
