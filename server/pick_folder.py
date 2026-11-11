import sys
import os
import subprocess
from pathlib import Path

def pick():
    ps_script = Path(__file__).parent / "pick_folder.ps1"
    if not ps_script.is_file():
        return None
    try:
        cmd = [
            "powershell.exe",
            "-NoProfile",
            "-ExecutionPolicy", "Bypass",
            "-STA",
            "-File", str(ps_script)
        ]
        proc = subprocess.run(
            cmd,
            capture_output=True,
            timeout=180
        )
        out = proc.stdout.decode("utf-8", errors="ignore").strip()
        # Lấy dòng cuối cùng không rỗng
        lines = [line.strip() for line in out.splitlines() if line.strip()]
        if lines:
            selected = lines[-1]
            if os.path.isdir(selected):
                return selected
    except Exception as e:
        sys.stderr.write(f"Lỗi: {e}\n")
    return None

if __name__ == "__main__":
    folder = pick()
    if folder:
        sys.stdout.buffer.write(folder.encode("utf-8"))
        sys.stdout.buffer.flush()
        sys.exit(0)
    sys.exit(1)
