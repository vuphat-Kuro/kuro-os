# Sinh anh wizard (BMP) cho nhieu muc DPI tu logo Kuro. Chay: python installer/tao-anh.py  (can pillow)
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
root = Path(__file__).resolve().parent
logo = Image.open(root.parent / "dashboard" / "kuro_logo_512.png").convert("RGBA")
BIG = [(164, 314), (192, 386), (246, 459), (273, 556), (328, 604), (355, 700), (410, 797)]
SMALL = [(55, 55), (64, 68), (83, 80), (92, 97), (110, 106), (119, 123), (138, 140)]
BG = (245, 247, 250)

def font(px):
    for f in ("segoeuib.ttf", "arialbd.ttf"):
        try: return ImageFont.truetype(f"C:/Windows/Fonts/{f}", px)
        except OSError: pass
    return ImageFont.load_default()

def paste_logo(img, box_w, top, size):
    l = logo.resize((size, size), Image.LANCZOS)
    img.paste(l, ((box_w - size) // 2, top), l)

for i, (w, h) in enumerate(BIG):
    img = Image.new("RGB", (w, h), BG)
    paste_logo(img, w, int(h * 0.12), int(w * 0.72))
    d = ImageDraw.Draw(img)
    t = "KURO OS"; f = font(int(w * 0.17))
    tw = d.textlength(t, font=f)
    d.text(((w - tw) / 2, h * 0.12 + w * 0.72 + h * 0.03), t, fill=(30, 41, 59), font=f)
    f2 = font(int(w * 0.075)); s = "Trợ lý kỹ sư hạ tầng"
    sw = d.textlength(s, font=f2)
    d.text(((w - sw) / 2, h * 0.12 + w * 0.72 + h * 0.03 + w * 0.2), s, fill=(100, 116, 139), font=f2)
    img.save(root / "img" / f"WizardImage{i}.bmp")
for i, (w, h) in enumerate(SMALL):
    img = Image.new("RGB", (w, h), BG)
    paste_logo(img, w, (h - int(min(w, h) * 0.9)) // 2, int(min(w, h) * 0.9))
    img.save(root / "img" / f"WizardSmallImage{i}.bmp")
