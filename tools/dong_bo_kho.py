"""Đồng bộ kho skill từ các repo nguồn (kho/nguon.json) vào kho/, sinh kho/muc-luc.json (specs/002).

Chạy trên máy người bảo trì rồi đẩy lên GitHub: .venv\\Scripts\\python tools\\dong_bo_kho.py
- Chữ (SKILL.md, tài liệu, json) thay ngay bằng bản mới.
- Gói mã của một skill đổi mà bản mới CHƯA có trong sổ duyệt kho/da-duyet.json: giữ gói mã cũ đang chạy,
  bản mới để ở kho/_cho-duyet/<repo>/<thư mục skill>/ để người bảo trì đọc rồi duyệt.
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "server"))
import config  # noqa: E402
import kho  # noqa: E402

SKIP_DIRS = {".git", "node_modules", "__pycache__"}


def frontmatter(text: str) -> dict:
    m = re.match(r"---\r?\n(.*?)\r?\n---", text, re.S)
    out = {}
    for line in (m.group(1).splitlines() if m else []):
        k, _, v = line.partition(":")
        if v and k.strip() in ("name", "description"):
            out[k.strip()] = v.strip().strip('"').strip("'")
    return out


def lay_nguon(n: dict) -> Path:
    p = Path(os.path.expanduser(n["clone"])) if n.get("clone") else None
    if p and p.exists():
        if (p / ".git").exists():
            head = subprocess.run(["git", "-C", str(p), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
            if head != n["commit"]:
                sys.exit(f"[LỖI] {n['id']}: clone đang ở {head[:7]}, nguon.json ghim {n['commit'][:7]}. "
                         "Đọc duyệt bản mới rồi sửa commit trong nguon.json.")
        return p
    p = config.STATE / "kho-nguon" / n["id"]
    if not p.exists():
        subprocess.run(["git", "clone", "--quiet", n["url"], str(p)], check=True)
    subprocess.run(["git", "-C", str(p), "checkout", "--quiet", n["commit"]], check=True)
    return p


def chep(src: Path, dst: Path, bo_duoi: set) -> None:
    if src.is_file():
        if src.suffix.lower() not in bo_duoi:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
        return
    for f in src.rglob("*"):
        if f.is_file() and not SKIP_DIRS & set(f.parts) and f.suffix.lower() not in bo_duoi:
            t = dst / f.relative_to(src)
            t.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(f, t)


def giu_ma_da_duyet(n_id: str, moi: Path, cu: Path, so: dict) -> list[str]:
    """Skill có gói mã mới chưa duyệt: đưa bản mới vào _cho-duyet, khôi phục gói mã cũ vào cây mới."""
    giu = []
    for sk in moi.rglob("SKILL.md"):
        d = sk.parent
        rel = d.relative_to(moi)
        sid = f"{n_id}/{rel.as_posix()}" if rel.parts else n_id
        fp_moi = kho.van_tay_goi(d)
        if not fp_moi or so.get(sid, {}).get("van_tay") in (None, fp_moi):
            continue   # không có mã, hoặc chưa từng duyệt (vẫn bị chặn lúc chạy), hoặc bản mới đã được duyệt
        cho = kho.KHO / "_cho-duyet" / n_id / rel
        shutil.rmtree(cho, ignore_errors=True)
        shutil.copytree(d, cho)
        for f in [f for f in d.rglob("*") if f.suffix.lower() in kho.MA_DUOI]:
            f.unlink()
        old = cu / rel
        for f in (old.rglob("*") if old.exists() else []):
            if f.is_file() and f.suffix.lower() in kho.MA_DUOI:
                (d / f.relative_to(old)).parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(f, d / f.relative_to(old))
        giu.append(sid)
    return giu


def dong_bo() -> dict:
    cfg = json.loads((kho.KHO / "nguon.json").read_text(encoding="utf-8"))
    bo_duoi = set(cfg.get("bo_duoi", []))
    so = kho.so_duyet()
    nguon_ml, skill_ml, bao = [], [], []
    for n in cfg["nguon"]:
        src = lay_nguon(n)
        dst = kho.KHO / n["id"]
        with tempfile.TemporaryDirectory(dir=kho.KHO) as tmp:
            moi = Path(tmp) / n["id"]
            moi.mkdir()
            bd = set(n["bo_duoi"]) if "bo_duoi" in n else bo_duoi   # nguồn cần .html (khuôn trang) tự khai riêng
            for c in n.get("chon", []):
                chep(src / c, moi / c, bd)
            if n.get("skill_don"):
                chep(src / n["skill_don"]["tu"], moi / n["skill_don"]["id"] / "SKILL.md", bd)
            for b in n.get("bo_tep", []):   # tệp làm việc ra bên ngoài (đăng bài...) không cho vào kho
                (moi / b).unlink(missing_ok=True)
            giu = giu_ma_da_duyet(n["id"], moi, dst, so)
            if dst.exists():
                shutil.rmtree(dst)   # không nuốt lỗi: xoá dở (thư mục đang mở) thì move sẽ lồng kho/x/x
            shutil.move(str(moi), str(dst))
        bao += [f"{n['id']}: giữ gói mã đã duyệt của {g}, bản mới chờ duyệt" for g in giu]
        so_skill = 0
        for sk in sorted(dst.rglob("SKILL.md")):
            d = sk.parent
            rel = d.relative_to(dst)
            fm = frontmatter(sk.read_text(encoding="utf-8", errors="replace"))
            fp = kho.van_tay_goi(d)
            skill_ml.append({
                "id": f"{n['id']}/{rel.as_posix()}" if rel.parts else n["id"],
                "ten": fm.get("name") or d.name, "mo_ta": (fm.get("description") or "")[:400],
                "repo": n["id"], "nhom": rel.parts[0] if len(rel.parts) > 1 else "",
                "duong_dan": d.relative_to(ROOT).as_posix(), "giay_phep": n["giay_phep"],
                "co_ma": bool(fp), "can_bash": n.get("can_bash", ""),
            })
            so_skill += 1
        nguon_ml.append({k: n.get(k, "") for k in ("id", "ten", "url", "commit", "giay_phep", "ghi_chu", "can_bash")}
                        | {"so_skill": so_skill})
    (kho.KHO / "muc-luc.json").write_text(json.dumps({"nguon": nguon_ml, "skill": skill_ml}, ensure_ascii=False,
                                                     indent=1), encoding="utf-8")
    return {"so_skill": len(skill_ml), "bao": bao}


if __name__ == "__main__":
    kq = dong_bo()
    print(f"Kho có {kq['so_skill']} skill.")
    for b in kq["bao"]:
        print(" -", b)
