# -*- coding: utf-8 -*-
"""CLI-Hub (gói pip cli-anything-hub, MIT): status | install | uninstall vào Python của Kuro. Ghim phiên bản."""
import importlib.metadata as md
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "_chung"))
import cai_phan_mem as cp

PIN = "0.4.1"
PKG = "cli-anything-hub"
cp.cfg_nhan.update(nhan_cai=f"Cài CLI-Hub {PIN} (pip)", nhan_go="Gỡ CLI-Hub",
                   xac_nhan_go="Gỡ gói cli-anything-hub khỏi Python của Kuro? (các CLI đã cài bằng nó không bị gỡ)")


def ver():
    try:
        return md.version(PKG)
    except md.PackageNotFoundError:
        return ""


def status(extra=None):
    v = ver()
    d = {"ok": True, "phien_ban_goi": PIN}
    if not v:
        cp.out({**d, "trang_thai": "chua_cai", "goi_y": ["install"], "thong_bao": "Chưa cài CLI-Hub (công cụ tra cứu/cài CLI cho phần mềm).", **(extra or {})})
    cp.out({**d, "trang_thai": "da_cai" if v == PIN else "co_ban_moi", "goi_y": [] if v == PIN else ["install"],
            "cai_dat": {"phien_ban": v, "duong_dan": sys.executable},
            "thong_bao": f"CLI-Hub {v} trong Python của Kuro. Chạy: python -c \"from cli_hub.cli import main; main()\" <lệnh>", **(extra or {})})


def pip(*a):
    r = subprocess.run([sys.executable, "-m", "pip", *a, "--disable-pip-version-check"], capture_output=True, text=True,
                       encoding="utf-8", errors="replace", timeout=150, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    if r.returncode:
        cp.out({"ok": False, "trang_thai": "loi", "thong_bao": "pip lỗi: " + ((r.stderr or r.stdout).strip().splitlines() or [""])[-1][:250]}, 1)


def main():
    act = sys.argv[1] if len(sys.argv) > 1 else "status"
    if act == "status":
        status()
    elif act == "install":
        pip("install", f"{PKG}=={PIN}")
        status({"thong_bao": f"Đã cài CLI-Hub {PIN}."})
    elif act == "uninstall":
        pip("uninstall", "-y", PKG)
        status({"thong_bao": "Đã gỡ CLI-Hub."})
    else:
        cp.out({"ok": False, "trang_thai": "loi", "thong_bao": f"Hành động không hỗ trợ: {act}"}, 1)


if __name__ == "__main__":
    main()
