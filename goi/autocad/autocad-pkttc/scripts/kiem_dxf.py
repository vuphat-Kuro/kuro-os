# -*- coding: utf-8 -*-
"""Kiểm một tệp DXF theo chuẩn PKTTC (chữ Unicode): layer, ByLayer, kiểu chữ, cỡ chữ, dim, viewport.
    python kiem_dxf.py <tep.dxf>        thoát 0 nếu không có LỖI, 1 nếu có (cảnh báo không làm thoát 1)
Giới hạn: cỡ chữ chưa gắn từng chữ với viewport chứa nó (xem references/quy-chuan.md, mục 5)."""
import re
import sys

import ezdxf
from ezdxf.lldxf import const

from pkttc_dxf import LAYERS, NHOM_CHU, TY_LE_CHO_PHEP

FONT_TCVN3 = {"vn-abc.shx", "vntime.shx", "vnavan.ttf", "vnavanb.ttf", "vhavan.ttf", "vhavanb.ttf"}
KY_TU_TCVN3 = set("µ¸¶·¹")   # dấu thanh của TCVN3 hiện thành Latin-1; không có lý do chính đáng xuất hiện trong chữ Unicode
LAYER_8 = {"DIMENSION", "LEADER", "MLEADER", "HATCH"}


def _chu(e) -> str:
    return e.dxf.text if e.dxftype() == "TEXT" else e.text


def kiem(duong_dan: str):
    d = ezdxf.readfile(duong_dan)
    loi, canh_bao = {}, {}

    def ghi(nhom, thong_diep, e=None):
        mau = f" (vd handle {e.dxf.handle})" if e is not None else ""
        nhom.setdefault(thong_diep, [0, mau])[0] += 1

    if d.dxfversion < "AC1021":
        ghi(loi, f"DXF {d.dxfversion} cũ hơn R2007: không lưu được chữ Unicode")
    if d.header.get("$INSUNITS", 0) != 4:
        ghi(canh_bao, "Đơn vị bản vẽ ($INSUNITS) chưa là mm")

    # Layer chuẩn: màu, kiểu nét, DEFPOINTS không in
    for ten, (mau, net, _) in LAYERS.items():
        if ten not in d.layers:
            continue
        lay = d.layers.get(ten)
        if lay.dxf.color != mau or lay.dxf.linetype.upper() != net.upper():
            ghi(loi, f"Layer {ten} sai màu hoặc kiểu nét (cần màu {mau}, {net})")
        if ten == "DEFPOINTS" and lay.dxf.get("plot", 1) != 0:
            ghi(loi, "Layer DEFPOINTS chưa đặt không in")

    # Tỷ lệ hợp lệ của bản vẽ: các DimStyle D<n>, viewport, và 1
    ty_le = {1}
    for ds in d.dimstyles:
        m = re.fullmatch(r"D(\d+)", ds.dxf.name)
        if m:
            ty_le.add(int(m.group(1)))
            if abs(ds.dxf.get("dimscale", 1) - int(m.group(1))) > 1e-9:
                ghi(loi, f"DimStyle {ds.dxf.name} có DIMSCALE khác {m.group(1)}")
    for lo in d.layouts:
        if lo.name == "Model":
            continue
        for v in lo.query("VIEWPORT"):
            if v.dxf.get("status", 0) <= 0 or v.dxf.id == 1 or v.dxf.height <= 0 or v.dxf.view_height <= 0:
                continue
            n = v.dxf.view_height / v.dxf.height
            if abs(n - round(n)) > 1e-6 or round(n) not in TY_LE_CHO_PHEP:
                ghi(loi, f"Viewport tỷ lệ 1:{n:.3f} ngoài dãy cho phép", v)
            else:
                ty_le.add(round(n))
            if v.dxf.layer.upper() != "DEFPOINTS":
                ghi(loi, f"Khung viewport ở layer {v.dxf.layer}, phải là DEFPOINTS", v)
            if not v.dxf.flags & const.VSF_LOCK_ZOOM:
                ghi(loi, "Viewport chưa khóa khung nhìn", v)

    kieu_dung = set()
    layer_la = {"0", *LAYERS}
    for lo in d.layouts:
        for e in lo:
            t, lay = e.dxftype(), e.dxf.layer
            if lay not in layer_la and "|" not in lay:
                ghi(canh_bao, f"Có đối tượng ở layer ngoài chuẩn (vd {lay!r})", e)
            if e.dxf.get("color", 256) != 256 or e.dxf.get("linetype", "ByLayer").upper() != "BYLAYER" \
                    or e.dxf.get("lineweight", -1) != -1:
                ghi(loi, "Có đối tượng không ByLayer (màu, kiểu nét hoặc độ dày gán riêng)", e)
            if t in ("TEXT", "MTEXT"):
                if lay != "3":
                    ghi(loi, "Chữ (TEXT/MTEXT) không ở layer 3", e)
                kieu_dung.add(e.dxf.style)
                if KY_TU_TCVN3 & set(_chu(e)):
                    ghi(loi, "Chuỗi chữ nghi mã TCVN3 (không phải Unicode)", e)
                h = e.dxf.height if t == "TEXT" else e.dxf.char_height
                if not any(round(h / s, 2) in NHOM_CHU for s in ty_le):
                    ghi(loi, f"Cao chữ {h:g} không ra nhóm {NHOM_CHU} với tỷ lệ nào của bản vẽ {sorted(ty_le)}", e)
            elif t in LAYER_8 and lay != "8":
                ghi(loi, f"{t} không ở layer 8", e)
            if t == "DIMENSION":
                if not re.fullmatch(r"D\d+", e.dxf.dimstyle):
                    ghi(loi, f"Dim dùng DimStyle {e.dxf.dimstyle!r}, cần dạng D<tỷ lệ>", e)
                if e.dxf.get("text", "") not in ("", "<>"):
                    ghi(loi, "Dim bị sửa tay giá trị chữ (override)", e)

    for ds in d.dimstyles:
        if re.fullmatch(r"D\d+", ds.dxf.name):
            kieu_dung.add(ds.dxf.get("dimtxsty", "Standard"))
    for ten in sorted(kieu_dung):
        if ten not in d.styles:
            ghi(loi, f"Kiểu chữ {ten!r} không tồn tại trong bản vẽ")
        elif d.styles.get(ten).dxf.font.lower() in FONT_TCVN3:
            ghi(loi, f"Kiểu chữ {ten!r} dùng font TCVN3 ({d.styles.get(ten).dxf.font})")
    return loi, canh_bao


def in_ket_qua(duong_dan, loi, canh_bao):
    for muc, tien_to in ((loi, "LỖI"), (canh_bao, "CẢNH BÁO")):
        for tb, (n, mau) in muc.items():
            print(f"{tien_to}: {tb} x{n}{mau}")
    print(f"{duong_dan}: " + ("ĐẠT (không có lỗi)" if not loi else f"{len(loi)} loại lỗi"))


if __name__ == "__main__":
    if sys.stdout.encoding.lower() != "utf-8":
        sys.stdout.reconfigure(encoding="utf-8")
    l, c = kiem(sys.argv[1])
    in_ket_qua(sys.argv[1], l, c)
    sys.exit(1 if l else 0)
