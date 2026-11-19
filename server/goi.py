"""Gói tiện ích tùy chọn: nằm sẵn trong goi/<id>/ nhưng CHỈ vào brain khi người dùng yêu cầu cài.
    python server/goi.py list | cai <id> | go <id>
Cài = chép skill vào brain + pip các thư viện còn thiếu. Bản cài được cập nhật theo mã nguồn mỗi lần Kuro khởi động
(config.sync_bundled đọc state/goi-cai.json), nên chỉ cần cài một lần."""
import importlib.util
import json
import shutil
import subprocess
import sys
from pathlib import Path

import config

GOI = config.ROOT / "goi"


def _manifest(gid: str) -> dict:
    f = GOI / gid / "goi.json"
    if not f.is_file():
        raise ValueError(f"Không có gói '{gid}'. Gói hiện có: {', '.join(p.parent.name for p in GOI.glob('*/goi.json')) or 'chưa có'}")
    return json.loads(f.read_text(encoding="utf-8"))


def da_cai() -> dict:
    f = config.STATE / "goi-cai.json"
    return json.loads(f.read_text(encoding="utf-8")) if f.is_file() else {}


def _luu(st: dict) -> None:
    config.STATE.mkdir(parents=True, exist_ok=True)
    (config.STATE / "goi-cai.json").write_text(json.dumps(st, indent=1, ensure_ascii=False), encoding="utf-8")


def liet_ke() -> str:
    st = da_cai()
    rows = [f"- {p.parent.name}: {json.loads(p.read_text(encoding='utf-8'))['ten']} [{'ĐÃ CÀI' if p.parent.name in st else 'chưa cài'}]"
            for p in sorted(GOI.glob("*/goi.json"))]
    return "\n".join(rows) or "Chưa có gói tiện ích nào."


def _python() -> str:
    exe = Path(sys.executable)   # pythonw không có console để pip in ra
    return str(exe.with_name("python.exe")) if exe.name.lower() == "pythonw.exe" and exe.with_name("python.exe").is_file() else str(exe)


def cai(gid: str) -> str:
    m = _manifest(gid)
    thieu = [i for i in m.get("import", []) if importlib.util.find_spec(i) is None]
    if thieu:
        r = subprocess.run([_python(), "-m", "pip", "install", *m.get("pip", [])], capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=600)
        if r.returncode:
            raise ValueError("Không cài được thư viện (máy có mạng không?): " + (r.stderr.strip().splitlines() or ["lỗi pip"])[-1])
    st = da_cai()
    st[gid] = {"skill": m["skill"]}
    _luu(st)
    config.sync_bundled()
    dst = config.BRAIN / ".claude" / "skills" / m["skill"]
    if not (dst / "SKILL.md").is_file():
        raise ValueError(f"Chép skill không thành (kiểm tra {dst})")
    return (f"Đã cài gói '{gid}' ({m['ten']}). Skill `{m['skill']}` tự nạp khi việc liên quan; "
            "cuộc trò chuyện đang mở có thể chưa thấy, mở cuộc trò chuyện mới để chắc chắn.")


def go(gid: str) -> str:
    st = da_cai()
    if gid not in st:
        return f"Gói '{gid}' chưa cài."
    shutil.rmtree(config.BRAIN / ".claude" / "skills" / st.pop(gid)["skill"], ignore_errors=True)
    _luu(st)
    return f"Đã gỡ gói '{gid}'. Thư viện pip giữ nguyên (không ảnh hưởng gì)."


def chay(hanh_dong: str, gid: str = "") -> str:
    if hanh_dong == "list":
        return liet_ke()
    if hanh_dong in ("cai", "go"):
        return (cai if hanh_dong == "cai" else go)(gid)
    raise ValueError("hanh_dong phải là list, cai hoặc go")


if __name__ == "__main__":
    try:
        print(chay(*sys.argv[1:3]))
    except (ValueError, TypeError) as e:
        sys.exit(f"[LỖI] {e}")
