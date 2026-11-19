#!/usr/bin/env python
"""Tiến trình cập nhật tách rời của Kuro OS (tương tự kiến trúc updater của Javis OS).
Chạy độc lập với server chính để không bị gián đoạn khi dừng server để cập nhật và khởi động lại.
"""
import argparse
import datetime
import json
import os
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STATE_DIR = ROOT / "state"
LOG_FILE = STATE_DIR / "update.log"
STATE_FILE = STATE_DIR / "update_state.json"
VERSION_FILE = ROOT / "VERSION"

NO_WINDOW = 0x08000000 if os.name == "nt" else 0


def now_str() -> str:
    return datetime.datetime.now().isoformat(timespec="seconds")


def log(msg: str) -> None:
    line = f"[{time.strftime('%H:%M:%S')}] {msg}"
    print(line, flush=True)
    try:
        STATE_DIR.mkdir(parents=True, exist_ok=True)
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass


def write_state(patch: dict) -> dict:
    st = {}
    try:
        if STATE_FILE.exists():
            st = json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except Exception:
        pass
    st.update(patch)
    try:
        STATE_DIR.mkdir(parents=True, exist_ok=True)
        STATE_FILE.write_text(json.dumps(st, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception:
        pass
    return st


def run_cmd(cmd: list[str]) -> subprocess.CompletedProcess:
    log("$ " + " ".join(cmd))
    env = {**os.environ, "GIT_TERMINAL_PROMPT": "0", "GCM_INTERACTIVE": "never"}
    r = subprocess.run(
        cmd,
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        creationflags=NO_WINDOW,
        env=env,
    )
    if r.returncode != 0:
        err = (r.stderr or r.stdout or "").strip()
        log(f"  (mã thoát {r.returncode}) {err[:400]}")
    return r


def venv_python() -> str:
    p = ROOT / ".venv" / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    return str(p) if p.exists() else sys.executable


def is_git_dirty() -> bool:
    r = run_cmd(["git", "status", "--porcelain", "--untracked-files=no"])
    return bool((r.stdout or "").strip())


def kill_process(pid: int, timeout_s: float = 10.0) -> None:
    if pid <= 0 or pid == os.getpid():
        return
    log(f"Đang dừng tiến trình PID {pid}...")
    if os.name == "nt":
        subprocess.run(["taskkill", "/F", "/PID", str(pid)], capture_output=True, creationflags=NO_WINDOW)
    else:
        try:
            import signal
            os.kill(pid, signal.SIGTERM)
        except OSError:
            pass


def _is_port_free(port: int) -> bool:
    import socket
    for host in ("127.0.0.1", "0.0.0.0"):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.bind((host, port))
        except OSError:
            return False
        finally:
            s.close()
    return True


def free_port(port: int | str) -> None:
    """Tắt các tiến trình đang chiếm cổng (ví dụ cổng 7788) và chờ cổng thực sự rảnh."""
    try:
        p = int(port)
    except ValueError:
        p = 7788
    if os.name == "nt":
        try:
            cmd = f'netstat -ano | findstr /r /c:":{p} .*LISTENING"'
            out = subprocess.check_output(cmd, shell=True, text=True, encoding="utf-8", errors="replace", creationflags=NO_WINDOW)
            for line in out.strip().splitlines():
                parts = line.strip().split()
                if len(parts) >= 5 and parts[-1].isdigit():
                    pid = int(parts[-1])
                    if pid > 0 and pid != os.getpid():
                        subprocess.run(["taskkill", "/F", "/T", "/PID", str(pid)], capture_output=True, creationflags=NO_WINDOW)
        except Exception:
            bat = ROOT / "tat-kuro.bat"
            if bat.exists():
                run_cmd(["cmd.exe", "/c", str(bat)])
    deadline = time.time() + 8.0
    while time.time() < deadline:
        if _is_port_free(p):
            return
        time.sleep(0.25)


_LOCAL_OPENER = urllib.request.build_opener(urllib.request.ProxyHandler({}))


def is_server_healthy(port: int | str) -> bool:
    url = f"http://127.0.0.1:{port}/health"
    try:
        with _LOCAL_OPENER.open(url, timeout=2) as resp:
            return resp.status == 200
    except Exception:
        return False


def start_kuro_server(port: int | str) -> None:
    log("Đang khởi động lại Kuro...")
    env = {**os.environ, "PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8", "KURO_PORT": str(port)}
    if os.name == "nt":
        desktop_py = ROOT / "app_desktop.py"
        pythonw = ROOT / ".venv" / "Scripts" / "pythonw.exe"
        if desktop_py.exists():
            exe = str(pythonw) if pythonw.exists() else venv_python()
            subprocess.Popen(
                [exe, str(desktop_py)],
                cwd=str(ROOT),
                creationflags=0x00000008 | 0x00000200,
                env=env,
            )
            return

        vbs = ROOT / "kuro.vbs"
        if vbs.exists():
            subprocess.Popen(["wscript.exe", "//nologo", str(vbs)], cwd=str(ROOT), creationflags=0x00000008, env=env)
            return

    # Fallback chạy trực tiếp uvicorn
    py = venv_python()
    subprocess.Popen(
        [py, "server/main.py"],
        cwd=str(ROOT),
        creationflags=0x00000008 | 0x00000200 if os.name == "nt" else 0,
        env=env,
    )


def main():
    parser = argparse.ArgumentParser(description="Kuro OS Independent Updater")
    parser.add_argument("--old-version", default="1.4.0", help="Phiên bản cũ")
    parser.add_argument("--target", default="", help="Phiên bản mục tiêu")
    parser.add_argument("--port", default="7788", help="Cổng server Kuro")
    parser.add_argument("--server-pid", type=int, default=0, help="PID server cũ cần tắt")
    args = parser.parse_args()

    log(f"=== Bắt đầu quy trình cập nhật Kuro (v{args.old_version} -> v{args.target or 'mới nhất'}) ===")
    write_state({
        "phase": "pulling",
        "started_at": now_str(),
        "old_version": args.old_version,
        "target_version": args.target,
        "result": None,
        "error": None,
    })

    stashed = False
    try:
        # Bước 1: Kéo mã nguồn mới
        if is_git_dirty():
            log("Phát hiện thay đổi cục bộ ở file code, cất tạm vào git stash...")
            r_stash = run_cmd(["git", "stash", "push", "-m", "kuro-auto-update"])
            stashed = (r_stash.returncode == 0)

        log("Đang kéo mã nguồn mới từ GitHub (origin/main)...")
        r_pull = run_cmd(["git", "pull", "--ff-only", "origin", "main"])
        if r_pull.returncode != 0:
            log("git pull --ff-only không thành công, thử git pull thông thường...")
            r_pull2 = run_cmd(["git", "pull", "origin", "main"])
            if r_pull2.returncode != 0:
                raise RuntimeError("Không thể kéo mã nguồn mới từ Git. Chi tiết trong update.log.")

        if stashed:
            log("Khôi phục các thay đổi cục bộ từ git stash...")
            run_cmd(["git", "stash", "pop"])

        # Bước 2: Cài đặt / cập nhật thư viện (tách riêng cốt lõi và gói kỹ thuật để gói kỹ thuật không làm hỏng lõi)
        write_state({"phase": "installing"})
        log("Cập nhật các gói thư viện lõi Python (requirements.txt)...")
        req_file = ROOT / "requirements.txt"
        req_tech = ROOT / "requirements-ky-thuat.txt"
        if req_file.exists():
            r_core = run_cmd([venv_python(), "-m", "pip", "install", "--disable-pip-version-check", "-r", str(req_file)])
            if r_core.returncode != 0:
                raise RuntimeError("Cài thư viện cốt lõi (requirements.txt) thất bại. Xem chi tiết trong state/update.log.")
        if req_tech.exists():
            log("Cập nhật các gói thư viện kỹ thuật (requirements-ky-thuat.txt)...")
            r_tech = run_cmd([venv_python(), "-m", "pip", "install", "--disable-pip-version-check", "-r", str(req_tech)])
            if r_tech.returncode != 0:
                log("Cảnh báo: Một số gói trong requirements-ky-thuat.txt chưa cài được trên phiên bản Python này; Kuro vẫn tiếp tục khởi động.")

        # Cập nhật phím tắt Desktop nếu có file script
        shortcut_ps = ROOT / "tao-loi-tat.ps1"
        if shortcut_ps.exists() and os.name == "nt":
            run_cmd(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(shortcut_ps)])

        # Bước 3: Khởi động lại Server
        write_state({"phase": "restarting"})
        log(f"Đang dừng phiên bản cũ (PID: {args.server_pid}, Port: {args.port})...")
        if args.server_pid:
            kill_process(args.server_pid)
        free_port(args.port)

        time.sleep(0.5)

        start_kuro_server(args.port)

        # Bước 4: Kiểm tra sức khỏe (Health Check - chờ tối đa 45s cho máy yếu sau cập nhật)
        log("Đang kiểm tra khởi động server Kuro...")
        ready = False
        for i in range(45):
            time.sleep(1)
            if is_server_healthy(args.port):
                ready = True
                break

        if not ready:
            err_log = STATE_DIR / "desktop_server_error.log"
            extra = ""
            if err_log.is_file():
                try:
                    last_lines = err_log.read_text(encoding="utf-8", errors="replace").strip().splitlines()
                    if last_lines:
                        extra = f" ({last_lines[-1][:200]})"
                except Exception:
                    pass
            raise RuntimeError(f"Server Kuro không phản hồi sau khi cập nhật (timeout 45s){extra}.")

        new_version = "1.0.0"
        if VERSION_FILE.exists():
            new_version = VERSION_FILE.read_text(encoding="utf-8").strip()

        log(f"🎉 Cập nhật thành công! Kuro đã hoạt động trên phiên bản {new_version} tại cổng {args.port}.")
        write_state({
            "phase": "idle",
            "result": "success",
            "finished_at": now_str(),
            "new_version": new_version,
            "error": None,
        })
    except Exception as e:
        err_msg = str(e)
        log(f"❌ Cập nhật thất bại: {err_msg}")
        write_state({
            "phase": "idle",
            "result": "error",
            "error": err_msg,
            "finished_at": now_str(),
        })


if __name__ == "__main__":
    main()
