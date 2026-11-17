"""Diễn hoạ bản vẽ bằng ComfyUI + RealVisXL (SDXL) + ControlNet Union SDXL (specs/003).

ComfyUI cài riêng ngoài thư mục Kuro (cai-dien-hoa.bat), mặc định ở ../ComfyUI/ComfyUI_windows_portable cạnh thư mục
Kuro (đổi bằng KURO_COMFYUI_DIR). Kuro tự bật ComfyUI chạy ngầm ở 127.0.0.1:8188 khi cần và tự tắt sau 10 phút rảnh.
Ba loại đầu vào: bản vẽ nét (lineart), ảnh chụp hiện trạng và ảnh mô hình 3D/BIM (độ sâu).
"""
import json
import math
import os
import random
import re
import shutil
import subprocess
import threading
import time
import unicodedata
from pathlib import Path

import httpx
from PIL import Image

import config

COMFY = Path(os.getenv("KURO_COMFYUI_DIR") or config.ROOT.parent / "ComfyUI" / "ComfyUI_windows_portable")
URL = "http://127.0.0.1:8188"
CKPT = "RealVisXL_V5.0_fp16.safetensors"
CN = "controlnet_union_sdxl_promax.safetensors"
RANH_TAT_S = 600
SO_ANH = 2
DUOI_ANH = {".png", ".jpg", ".jpeg", ".webp", ".bmp"}
# Chế độ -> (bộ tiền xử lý controlnet_aux, kiểu ControlNet Union, độ mạnh). Đo trên bản cài ở specs/003 research.
CHE_DO = {
    "net": ("LineArtPreprocessor", "canny/lineart/anime_lineart/mlsd", 0.75),
    "anh": ("DepthAnythingV2Preprocessor", "depth", 0.6),
    "3d": ("DepthAnythingV2Preprocessor", "depth", 0.65),
}
DUOI_PROMPT = ", architectural visualization, photorealistic, high detail, realistic materials, natural daylight"
AM = ("cartoon, sketch, drawing, lowres, blurry, distorted lines, deformed structure, extra floors, watermark, "
      "text, logo, oversaturated")

_proc: subprocess.Popen | None = None
_lan_cuoi = 0.0
_khoa = threading.Lock()


def thieu() -> str:
    """Rỗng nếu máy đã cài đủ; không thì nói thiếu gì (để Kuro báo, không chạy dở)."""
    can = {
        "ComfyUI": COMFY / "ComfyUI" / "main.py",
        "Python của ComfyUI": COMFY / "python_embeded" / "python.exe",
        "model RealVisXL": COMFY / "ComfyUI" / "models" / "checkpoints" / CKPT,
        "ControlNet Union SDXL": COMFY / "ComfyUI" / "models" / "controlnet" / CN,
        "comfyui_controlnet_aux": COMFY / "ComfyUI" / "custom_nodes" / "comfyui_controlnet_aux",
    }
    mat = [ten for ten, p in can.items() if not p.exists()]
    return ("Máy này chưa có diễn hoạ (thiếu: " + ", ".join(mat) + "). Bấm đúp cai-dien-hoa.bat trong thư mục Kuro "
            "(cần card NVIDIA từ 8 GB VRAM, tải khoảng 12 GB).") if mat else ""


def dang_chay() -> bool:
    try:
        return httpx.get(f"{URL}/system_stats", timeout=2).status_code == 200
    except httpx.HTTPError:
        return False


def bat() -> None:
    global _proc, _lan_cuoi
    _lan_cuoi = time.time()   # vừa bật thì chưa tính là rảnh
    if dang_chay():
        return
    log = open(config.STATE / "comfyui.log", "ab")
    _proc = subprocess.Popen(
        [str(COMFY / "python_embeded" / "python.exe"), "-s", "ComfyUI/main.py", "--windows-standalone-build",
         "--listen", "127.0.0.1", "--port", "8188", "--disable-auto-launch",
         # Đo trên RTX 4060 8 GB: fp16 SDXL + ControlNet tràn VRAM (19 s/bước); UNet fp8 cho vừa VRAM
         "--fp8_e4m3fn-unet"],
        cwd=COMFY, stdout=log, stderr=subprocess.STDOUT, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    for _ in range(180):
        if dang_chay():
            return
        if _proc.poll() is not None:
            raise RuntimeError(f"ComfyUI dừng khi khởi động (mã {_proc.returncode}), xem state/comfyui.log")
        time.sleep(1)
    raise RuntimeError("ComfyUI không lên sau 3 phút, xem state/comfyui.log")


def tat_neu_ranh() -> bool:
    """Gọi định kỳ: chỉ tắt ComfyUI do Kuro bật, khi đã rảnh quá 10 phút."""
    global _proc
    if _proc and _proc.poll() is None and not _khoa.locked() and time.time() - _lan_cuoi > RANH_TAT_S:
        _proc.terminate()
        _proc = None
        return True
    return False


def kich_thuoc(w: int, h: int) -> tuple[int, int]:
    """Giữ tỉ lệ ảnh gốc, diện tích khoảng 1024x1024 (chuẩn SDXL), bội số 64, cạnh 512..1536."""
    k = math.sqrt(1024 * 1024 / (w * h))
    return tuple(min(1536, max(512, round(v * k / 64) * 64)) for v in (w, h))


def workflow(ten_anh: str, prompt_en: str, che_do: str, w: int, h: int, so_anh: int, seed: int) -> dict:
    pre, kieu, manh = CHE_DO[che_do]
    pre_in = {"image": ["3", 0], "resolution": 1024}
    pre_in |= {"coarse": "disable"} if pre == "LineArtPreprocessor" else {"ckpt_name": "depth_anything_v2_vits.pth"}
    return {
        "1": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": CKPT}},
        "2": {"class_type": "ControlNetLoader", "inputs": {"control_net_name": CN}},
        "3": {"class_type": "LoadImage", "inputs": {"image": ten_anh}},
        "4": {"class_type": pre, "inputs": pre_in},
        "5": {"class_type": "SetUnionControlNetType", "inputs": {"control_net": ["2", 0], "type": kieu}},
        "6": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["1", 1], "text": prompt_en + DUOI_PROMPT}},
        "7": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["1", 1], "text": AM}},
        "8": {"class_type": "ControlNetApplyAdvanced", "inputs": {
            "positive": ["6", 0], "negative": ["7", 0], "control_net": ["5", 0], "image": ["4", 0],
            "strength": manh, "start_percent": 0.0, "end_percent": 0.85, "vae": ["1", 2]}},
        "9": {"class_type": "EmptyLatentImage", "inputs": {"width": w, "height": h, "batch_size": so_anh}},
        "10": {"class_type": "KSampler", "inputs": {
            "model": ["1", 0], "positive": ["8", 0], "negative": ["8", 1], "latent_image": ["9", 0], "seed": seed,
            "steps": 28, "cfg": 4.5, "sampler_name": "dpmpp_2m", "scheduler": "karras", "denoise": 1.0}},
        "11": {"class_type": "VAEDecode", "inputs": {"samples": ["10", 0], "vae": ["1", 2]}},
        "12": {"class_type": "SaveImage", "inputs": {"images": ["11", 0], "filename_prefix": "kuro/dien-hoa"}},
    }


def ve(anh: Path, prompt_en: str, che_do: str, thu_muc_ra: Path, so_anh: int = SO_ANH) -> list[Path]:
    """Vẽ và trả đường dẫn ảnh kết quả trong thu_muc_ra. Chạy đồng bộ (gọi qua asyncio.to_thread)."""
    global _lan_cuoi
    if loi := thieu():
        raise RuntimeError(loi)
    if not anh.is_file() or anh.suffix.lower() not in DUOI_ANH:
        raise RuntimeError(f"Không đọc được ảnh {anh} (cần .png, .jpg, .webp, .bmp).")
    che_do = che_do if che_do in CHE_DO else "net"
    with _khoa:
        _lan_cuoi = time.time()
        bat()
        ten = f"kuro_{int(time.time())}{anh.suffix.lower()}"
        shutil.copy2(anh, COMFY / "ComfyUI" / "input" / ten)
        with Image.open(anh) as im:
            w, h = kich_thuoc(*im.size)
        wf = workflow(ten, prompt_en, che_do, w, h, so_anh, random.randint(1, 2**31))
        r = httpx.post(f"{URL}/prompt", json={"prompt": wf, "client_id": "kuro"}, timeout=30)
        if r.status_code != 200:
            raise RuntimeError(f"ComfyUI từ chối quy trình: {r.text[:500]}")
        pid = r.json()["prompt_id"]
        for _ in range(900):   # tối đa 15 phút (lần đầu còn tải bộ nhận nét/độ sâu)
            hist = httpx.get(f"{URL}/history/{pid}", timeout=10).json().get(pid)
            if hist:
                break
            time.sleep(1)
        else:
            raise RuntimeError("Quá 15 phút chưa vẽ xong, xem state/comfyui.log")
        if (hist.get("status") or {}).get("status_str") == "error":
            raise RuntimeError("ComfyUI báo lỗi: " + json.dumps(hist["status"].get("messages", [])[-1:],
                                                                  ensure_ascii=False)[:500])
        thu_muc_ra.mkdir(parents=True, exist_ok=True)
        ra = []
        for o in hist["outputs"].get("12", {}).get("images", []):
            src = COMFY / "ComfyUI" / "output" / o.get("subfolder", "") / o["filename"]
            dst = thu_muc_ra / f"dien-hoa_{time.strftime('%Y%m%d_%H%M%S')}_{len(ra) + 1}.png"
            shutil.copy2(src, dst)
            ra.append(dst)
        _lan_cuoi = time.time()
        return ra


def _bo_dau(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", s.lower()) if unicodedata.category(c) != "Mn").replace("đ", "d")


def yeu_cau(text: str) -> dict | None:
    """Câu có chữ diễn hoạ/render kèm ảnh đính kèm thì Kuro tự diễn hoạ, dùng được với mọi AI."""
    t = _bo_dau(text)
    if not re.search(r"\bdien hoa\b|\brender\b|/dien-hoa", t):
        return None
    anh = [p.strip() for p in re.findall(r"\[(?:Tệp|Hình ảnh) đính kèm:\s*([^\]]+)\]", text)]
    anh = [p for p in anh if Path(p).suffix.lower() in DUOI_ANH]
    if not anh:
        return None
    che_do = "anh" if re.search(r"hien trang|anh chup|anh thuc", t) else \
        "3d" if re.search(r"\b3d\b|mo hinh|bim|revit|sketchup|ifc", t) else "net"
    mo_ta = re.sub(r"\[(?:Tệp|Hình ảnh) đính kèm:[^\]]+\]", "", text).strip()
    return {"anh": Path(anh[0]), "che_do": che_do, "mo_ta": mo_ta}
