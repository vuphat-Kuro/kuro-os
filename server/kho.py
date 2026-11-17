"""Kho skill đi kèm Kuro (specs/002): tìm, đọc, chạy mã đã duyệt, kiểm tra nguồn có bản mới.

Kho nằm ở kho/, mục lục kho/muc-luc.json do tools/dong_bo_kho.py sinh ra. Kuro không nạp kho vào lời nhắc: AI tự
gọi tim_skill / doc_skill / chay_ma_kho (khai trong calc.py). Mã chỉ chạy khi dấu vân tay gói mã của skill khớp
sổ duyệt: kho/da-duyet.json (đi kèm repo) hoặc state/kho-da-duyet.json (duyệt trên máy).
"""
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import config

KHO = config.ROOT / "kho"
MUC_LUC = KHO / "muc-luc.json"
SO_GOC = KHO / "da-duyet.json"
# Đuôi coi là "mã chạy được": gói mã của skill là các tệp này; .md, .json, ảnh... là chữ/dữ liệu, dùng ngay.
MA_DUOI = {".py", ".mjs", ".js", ".cjs", ".ts", ".tsx", ".ps1", ".sh", ".bat", ".cmd", ".exe", ".dll", ".vbs"}
CHAY_DUOI = {".py": "python", ".mjs": "node", ".js": "node", ".cjs": "node"}
TIMEOUT_S = 300
OUT_MAX = 20_000


def so_may() -> Path:
    return config.STATE / "kho-da-duyet.json"


def van_tay_goi(d: Path) -> str:
    """SHA-256 của mọi tệp mã trong thư mục skill (đường dẫn tương đối + nội dung); rỗng nếu skill không có mã."""
    files = sorted(f for f in d.rglob("*") if f.is_file() and f.suffix.lower() in MA_DUOI)
    if not files:
        return ""
    h = hashlib.sha256()
    for f in files:
        h.update(f.relative_to(d).as_posix().encode())
        h.update(f.read_bytes())
    return h.hexdigest()


def muc_luc() -> dict:
    try:
        return json.loads(MUC_LUC.read_text(encoding="utf-8"))
    except (FileNotFoundError, ValueError):
        return {"nguon": [], "skill": []}


def _skill(skill_id: str) -> dict:
    for s in muc_luc()["skill"]:
        if s["id"] == skill_id or s["ten"] == skill_id:
            return s
    raise ValueError(f'Không có skill "{skill_id}" trong kho. Gọi tim_skill để lấy đúng id.')


def tim(cau: str, n: int = 8) -> list[dict]:
    """Chấm điểm từ khoá trên tên (x3), nhóm (x2), mô tả (x1). Mô tả kho chủ yếu tiếng Anh."""
    tu = {t for t in re.findall(r"\w+", cau.lower()) if len(t) > 1}
    kq = []
    for s in muc_luc()["skill"]:
        ten = set(re.findall(r"\w+", s["ten"].lower().replace("-", " ")))
        nhom = set(re.findall(r"\w+", s.get("nhom", "").lower().replace("-", " ")))
        mo_ta = set(re.findall(r"\w+", s["mo_ta"].lower()))
        diem = 3 * len(tu & ten) + 2 * len(tu & nhom) + len(tu & mo_ta)
        if diem:
            kq.append((diem, s))
    kq.sort(key=lambda x: -x[0])
    return [{k: s.get(k) for k in ("id", "ten", "mo_ta", "repo", "co_ma", "can_bash")} for _, s in kq[:n]]


def doc(skill_id: str, tep: str = "SKILL.md") -> str:
    s = _skill(skill_id)
    base = (config.ROOT / s["duong_dan"]).resolve()
    p = (base / tep).resolve()
    if not p.is_relative_to(base) or not p.is_file():   # chặn ../ thoát ra ngoài thư mục skill
        raise ValueError(f'Không có tệp "{tep}" trong skill {s["id"]}.')
    text = p.read_text(encoding="utf-8", errors="replace")[:60_000]
    if tep == "SKILL.md":
        kem = sorted(f.relative_to(base).as_posix() for f in base.rglob("*") if f.is_file() and f.name != "SKILL.md")
        text += (f"\n\n---\n[Kuro] Skill {s['id']} (repo {s['repo']}, giấy phép {s.get('giay_phep', '?')}). "
                 f"Tệp kèm ({len(kem)}): {', '.join(kem[:80])}" + (" ..." if len(kem) > 80 else ""))
        if s.get("can_bash"):
            text += f"\n[Kuro] {s['can_bash']}"
    return text


def so_duyet() -> dict:
    out = {}
    for f in (SO_GOC, so_may()):
        try:
            out.update(json.loads(f.read_text(encoding="utf-8")))
        except (FileNotFoundError, ValueError):
            pass
    return out


def da_duyet(s: dict) -> bool:
    # Tính lại dấu vân tay mỗi lần: mã bị sửa sau khi duyệt là tự bị chặn.
    fp = van_tay_goi(config.ROOT / s["duong_dan"])
    return bool(fp) and so_duyet().get(s["id"], {}).get("van_tay") == fp


def duyet(skill_id: str, nguoi: str = "chủ máy") -> dict:
    s = _skill(skill_id)
    fp = van_tay_goi(config.ROOT / s["duong_dan"])
    if not fp:
        raise ValueError(f"Skill {s['id']} không có mã, không cần duyệt.")
    so = {}
    try:
        so = json.loads(so_may().read_text(encoding="utf-8"))
    except (FileNotFoundError, ValueError):
        pass
    so[s["id"]] = {"van_tay": fp, "nguoi": nguoi, "ngay": datetime.now().isoformat(timespec="seconds")}
    so_may().parent.mkdir(parents=True, exist_ok=True)
    so_may().write_text(json.dumps(so, ensure_ascii=False, indent=1), encoding="utf-8")
    return so[s["id"]]


def chay(skill_id: str, tep: str, doi_so: list[str], cwd: Path) -> str:
    s = _skill(skill_id)
    base = (config.ROOT / s["duong_dan"]).resolve()
    p = (base / tep).resolve()
    if not p.is_relative_to(base) or not p.is_file():
        return f'[CHẶN] Không có tệp "{tep}" trong skill {s["id"]}.'
    if p.suffix.lower() not in CHAY_DUOI:
        return f"[CHẶN] Chỉ chạy được .py, .mjs, .js, .cjs; tệp {tep} không thuộc loại này."
    if not da_duyet(s):
        return (f"[CHẶN] Mã của skill {s['id']} chưa được duyệt (hoặc đã đổi sau khi duyệt) nên chưa chạy. "
                "Chủ máy duyệt ở ⚙ Cài đặt > Kho skill.")
    exe = sys.executable if CHAY_DUOI[p.suffix.lower()] == "python" else shutil.which("node")
    if not exe:
        return "[CHẶN] Máy chưa có Node.js (nodejs.org) để chạy mã này."
    try:
        r = subprocess.run([exe, str(p), *map(str, doi_so)], cwd=cwd, capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=TIMEOUT_S,
                           env={**os.environ, "PYTHONUTF8": "1"},
                           creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        out = r.stdout + (f"\n[stderr]\n{r.stderr}" if r.stderr.strip() else "")
        status = "OK" if r.returncode == 0 else f"LỖI exit={r.returncode}"
    except subprocess.TimeoutExpired:
        status, out = f"QUÁ {TIMEOUT_S} GIÂY, đã dừng", ""
    if len(out) > OUT_MAX:
        out = "...(cắt bớt phần đầu)\n" + out[-OUT_MAX:]
    return f"[{status}] {s['id']}/{tep} chạy trong {cwd}\n{out}"


def danh_sach() -> dict:
    """Cho mục Kho skill trong Cài đặt."""
    ml = muc_luc()
    so = so_duyet()
    ma = [{"id": s["id"], "repo": s["repo"], "da_duyet": da_duyet(s), "ngay": so.get(s["id"], {}).get("ngay")}
          for s in ml["skill"] if s.get("co_ma")]
    cho = sorted(p.relative_to(KHO / "_cho-duyet").as_posix() for p in (KHO / "_cho-duyet").glob("*/*")) \
        if (KHO / "_cho-duyet").is_dir() else []
    return {"nguon": ml["nguon"], "goi_ma": ma, "ban_moi_cho_duyet": cho, "so_skill": len(ml["skill"])}


def kiem_tra_nguon() -> list[str]:
    """Repo nguồn nào có commit mới so với commit đang ghim (git ls-remote, không tải gì)."""
    moi = []
    for n in muc_luc()["nguon"]:
        try:
            r = subprocess.run(["git", "ls-remote", n["url"], "HEAD"], capture_output=True, text=True, timeout=30,
                               env={**os.environ, "GIT_TERMINAL_PROMPT": "0"},
                               creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
            head = (r.stdout.split() or [""])[0]
            if head and head != n["commit"]:
                moi.append(f"{n['ten']} ({n['url']}): có commit mới {head[:7]}, kho đang dùng {n['commit'][:7]}")
        except (OSError, subprocess.TimeoutExpired) as e:
            print(f"[kho] không kiểm tra được {n['id']}: {e}")
    return moi
