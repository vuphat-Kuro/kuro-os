"""Cài diễn hoạ cho Kuro (specs/003): ComfyUI bản Windows + comfyui_controlnet_aux + RealVisXL + ControlNet Union SDXL.

Chạy bằng cai-dien-hoa.bat. Cài vào thư mục ComfyUI cạnh thư mục Kuro (đổi bằng KURO_COMFYUI_DIR). Tải khoảng 11,5 GB,
tải tiếp được nếu đứt mạng. Chạy lại bao nhiêu lần cũng được: phần đã có thì bỏ qua.
"""
import json
import os
import re
import shutil
import subprocess
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "server"))
import dien_hoa  # noqa: E402

COMFY = dien_hoa.COMFY
TAI = COMFY.parent / "_tai"
COMFY_TAG = "v0.45.0"
AUX_URL = "https://github.com/Fannovel16/comfyui_controlnet_aux"
AUX_COMMIT = "b9abafa1019e230ebd674e4ae93f11bdf9d8dfc2"
MODEL = [  # (url, thư mục đích trong ComfyUI/models, tên lưu)
    ("https://huggingface.co/SG161222/RealVisXL_V5.0/resolve/main/RealVisXL_V5.0_fp16.safetensors",
     "checkpoints", dien_hoa.CKPT),
    ("https://huggingface.co/xinsir/controlnet-union-sdxl-1.0/resolve/main/diffusion_pytorch_model_promax.safetensors",
     "controlnet", dien_hoa.CN),
]


def buoc(s: str) -> None:
    print(f"\n== {s}", flush=True)


def kiem_gpu() -> str:
    """Trả tên bản ComfyUI hợp driver. Đo: driver 566.07 chỉ tới CUDA 12.7, bản 'nvidia' mặc định cần driver mới hơn."""
    try:
        out = subprocess.run(["nvidia-smi", "--query-gpu=name,memory.total,driver_version", "--format=csv,noheader,nounits"],
                             capture_output=True, text=True, timeout=30).stdout.strip().splitlines()[0]
    except (OSError, IndexError, subprocess.TimeoutExpired):
        sys.exit("[LỖI] Không thấy card NVIDIA (nvidia-smi). Diễn hoạ SDXL cần card NVIDIA từ 8 GB VRAM.")
    ten, vram, driver = [x.strip() for x in out.split(",")]
    print(f"Card: {ten}, VRAM {int(vram) / 1024:.1f} GB, driver {driver}")
    if int(vram) < 7600:
        sys.exit("[LỖI] Card dưới 8 GB VRAM, SDXL + ControlNet không chạy nổi.")
    return "ComfyUI_windows_portable_nvidia.7z" if float(driver) >= 570 else "ComfyUI_windows_portable_nvidia_cu126.7z"


def kich_thuoc_xa(url: str) -> int:
    req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "Kuro"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return int(r.headers.get("Content-Length") or 0)


def tai(url: str, dich: Path) -> None:
    """curl có sẵn trên Windows 10+: -C - tải tiếp khi đứt; đủ dung lượng thì bỏ qua."""
    can = kich_thuoc_xa(url)
    if dich.exists() and can and dich.stat().st_size == can:
        print(f"Đã có {dich.name} ({can / 1e9:.2f} GB)")
        return
    dich.parent.mkdir(parents=True, exist_ok=True)
    print(f"Tải {dich.name} ({can / 1e9:.2f} GB) từ {url}")
    subprocess.run(["curl", "-L", "-C", "-", "--retry", "5", "-o", str(dich), url], check=True)
    if can and dich.stat().st_size != can:
        sys.exit(f"[LỖI] {dich.name} tải chưa đủ ({dich.stat().st_size} / {can} byte). Chạy lại để tải tiếp.")


def tim_7z() -> str:
    for p in (shutil.which("7z"), r"C:\Program Files\7-Zip\7z.exe", r"C:\Program Files (x86)\7-Zip\7z.exe"):
        if p and Path(p).exists():
            return p
    sys.exit("[LỖI] Chưa có 7-Zip để giải nén ComfyUI. Cài 7-Zip từ 7-zip.org rồi chạy lại.")


def main() -> None:
    buoc("1/5 Kiểm tra card đồ hoạ")
    goi = kiem_gpu()
    buoc(f"2/5 ComfyUI {COMFY_TAG}")
    if not (COMFY / "ComfyUI" / "main.py").exists():
        f = TAI / goi
        tai(f"https://github.com/comfyanonymous/ComfyUI/releases/download/{COMFY_TAG}/{goi}", f)
        subprocess.run([tim_7z(), "x", str(f), f"-o{COMFY.parent}", "-y"], check=True, stdout=subprocess.DEVNULL)
    print(f"ComfyUI ở {COMFY}")
    buoc("3/5 Bộ tiền xử lý comfyui_controlnet_aux (nhận nét, độ sâu)")
    aux = COMFY / "ComfyUI" / "custom_nodes" / "comfyui_controlnet_aux"
    if not aux.exists():
        subprocess.run(["git", "clone", "--quiet", AUX_URL, str(aux)], check=True)
    subprocess.run(["git", "-C", str(aux), "checkout", "--quiet", AUX_COMMIT], check=True)
    py = COMFY / "python_embeded" / "python.exe"
    subprocess.run([str(py), "-s", "-m", "pip", "install", "--disable-pip-version-check", "-r",
                    str(aux / "requirements.txt")], check=True)
    buoc("4/5 Model RealVisXL và ControlNet Union SDXL (khoảng 9,5 GB)")
    for url, thu_muc, ten in MODEL:
        dich = COMFY / "ComfyUI" / "models" / thu_muc / ten
        tai_ve = TAI / url.rsplit("/", 1)[1]
        if not dich.exists():
            tai(url, tai_ve)
            dich.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(tai_ve), str(dich))
        print(f"Có {ten}")
    buoc("5/5 Kiểm tra")
    if loi := dien_hoa.thieu():
        sys.exit("[LỖI] " + loi)
    print("Xong. Gửi ảnh bản vẽ vào khung chat Kuro kèm câu 'diễn hoạ ...' để thử.")


if __name__ == "__main__":
    main()
