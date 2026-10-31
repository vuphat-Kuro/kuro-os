"""Kiểm tra bản mới trên GitHub bằng git, dùng lại đăng nhập lúc clone nên repo riêng tư không cần token."""
import asyncio
import os
import subprocess

import config

STATUS = {"current": (config.ROOT / "VERSION").read_text(encoding="utf-8").strip(),
          "latest": None, "behind": 0, "notes": []}


def _git(*args: str) -> str:
    # Chạy nền: cấm git và Git Credential Manager bật hộp thoại hỏi đăng nhập.
    env = {**os.environ, "GIT_TERMINAL_PROMPT": "0", "GCM_INTERACTIVE": "never"}
    r = subprocess.run(["git", *args], cwd=config.ROOT, capture_output=True, text=True, encoding="utf-8",
                       timeout=60, env=env)
    if r.returncode:
        raise RuntimeError(r.stderr.strip() or f"git {args[0]} lỗi {r.returncode}")
    return r.stdout.strip()


def check() -> None:
    if not (config.ROOT / ".git").exists():      # cài bằng file zip: không tự kiểm tra được
        return
    _git("fetch", "--quiet")
    behind = int(_git("rev-list", "--count", "HEAD..@{u}"))
    STATUS.update(behind=behind,
                  latest=_git("show", "@{u}:VERSION").strip() if behind else STATUS["current"],
                  notes=_git("log", "--format=%s", "-10", "HEAD..@{u}").splitlines() if behind else [])


async def loop(notify=None) -> None:
    """Kiểm tra lúc khởi động rồi 6 giờ một lần; có bản mới thì báo Telegram một lần cho mỗi bản."""
    told = None
    while True:
        try:
            await asyncio.to_thread(check)
            if notify and STATUS["behind"] and STATUS["latest"] != told:
                told = STATUS["latest"]
                await notify(f"Kuro có bản mới {told} (đang dùng {STATUS['current']}):\n- "
                             + "\n- ".join(STATUS["notes"]) + "\n\nBấm đúp cap-nhat.bat để cập nhật.")
        except Exception as e:  # mất mạng, chưa có upstream, hết hạn đăng nhập...
            print(f"[cap-nhat] chưa kiểm tra được: {e}")
        await asyncio.sleep(6 * 3600)
