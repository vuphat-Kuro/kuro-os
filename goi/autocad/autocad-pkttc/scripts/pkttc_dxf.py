# -*- coding: utf-8 -*-
"""Dựng bản vẽ DXF chuẩn PKTTC bằng ezdxf: layer 1..9, chữ Unicode, DimStyle D<tỷ lệ>.
Môi trường: Python 3, ezdxf 1.4.x; DXF R2018, mở được bằng AutoCAD 2020.
Quy tắc: references/quy-chuan.md. Kiểm: kiem_dxf.py (luu() tự gọi)."""
import ezdxf
from ezdxf import units

# ---- Tham số chỉnh được (script kiểm đọc cùng các hằng số này) ----
TY_LE_CHO_PHEP = (5, 10, 20, 25, 30, 50, 100, 150, 200, 250, 500, 1000)
NHOM_CHU = (1.5, 2.0, 2.5, 3.5)                           # cao chữ trên giấy, mm
STYLE_THEO_NHOM = {1.5: "Arial", 2.0: "Arial", 2.5: "ArialH", 3.5: "ArialH"}
FONT_STYLE = {"Arial": "arial.ttf", "ArialH": "arialbd.ttf"}   # TTF Unicode, máy Windows nào cũng có
STYLE_DIM = "Arial"
# tên layer: (màu ACI, kiểu nét, độ dày 1/100 mm; DXF chỉ nhận 0, 5, 9, 13, 15, 18, 20, 25, 30...)
# Layer 4: quy chuẩn ghi 0,10 mm nhưng DXF không có mức đó, lấy 0,09. Nét in thật do KTTC_PlotStyleTable.ctb quyết định.
LAYERS = {
    "1": (1, "Continuous", 20), "2": (2, "Continuous", 15), "3": (3, "Continuous", 15),
    "4": (4, "HIDDEN", 9), "5": (5, "Continuous", 20), "6": (6, "Continuous", 15),
    "7": (7, "Continuous", 20), "8": (8, "Continuous", 9), "9": (9, "CENTER", 15),
    "DEFPOINTS": (7, "Continuous", 0),
}
DIM_SDS = dict(dimclrd=8, dimclre=8, dimclrt=3, dimtxt=2.0, dimasz=1.25, dimexe=0.6, dimexo=0.8,
               dimgap=0.5, dimdec=0, dimtad=1, dimtih=0, dimtoh=0, dimtix=0)


class BanVe:
    def __init__(self, ty_le: int = 1):
        if ty_le != 1 and ty_le not in TY_LE_CHO_PHEP:
            raise ValueError(f"Tỷ lệ 1:{ty_le} ngoài dãy cho phép {TY_LE_CHO_PHEP}")
        self.ty_le = ty_le
        self.doc = ezdxf.new("R2018", setup=["linetypes"])
        self.doc.units = units.MM
        self.msp = self.doc.modelspace()
        for ten, (mau, net, lw) in LAYERS.items():
            lay = self.doc.layers.get(ten) if ten in self.doc.layers else self.doc.layers.add(ten)   # ezdxf đã có sẵn DEFPOINTS
            lay.color, lay.dxf.linetype, lay.dxf.lineweight = mau, net, lw
            if ten == "DEFPOINTS":
                lay.dxf.plot = 0
        for ten, font in FONT_STYLE.items():
            self.doc.styles.add(ten, font=font)
        self.dimstyle = f"D{ty_le}"
        self.doc.dimstyles.new(self.dimstyle, dxfattribs={**DIM_SDS, "dimtxsty": STYLE_DIM, "dimscale": float(ty_le)})

    def net(self, diem, layer: str = "1", kin: bool = False):
        """Polyline nét theo layer 1..9. Layer khác chuẩn thì báo lỗi, không tự tạo."""
        if layer not in LAYERS or layer in ("3", "8", "DEFPOINTS"):
            raise ValueError(f"Layer {layer!r} không dùng cho nét vẽ: chọn 1, 2, 4, 5, 6, 7, 9")
        return self.msp.add_lwpolyline(list(diem), close=kin, dxfattribs={"layer": layer})

    def text(self, chuoi: str, vi_tri, nhom: float = 2.0, goc: float = 0.0):
        """Chữ Unicode, layer 3, cao = nhóm x tỷ lệ in."""
        if nhom not in NHOM_CHU:
            raise ValueError(f"Nhóm chữ {nhom} ngoài {NHOM_CHU}")
        e = self.msp.add_text(chuoi, height=nhom * self.ty_le, rotation=goc,
                              dxfattribs={"layer": "3", "style": STYLE_THEO_NHOM[nhom]})
        e.set_placement(vi_tri)
        return e

    def dim_ngang(self, p1, p2, vi_tri):
        return self._dim(p1, p2, vi_tri, 0)

    def dim_doc(self, p1, p2, vi_tri):
        return self._dim(p1, p2, vi_tri, 90)

    def _dim(self, p1, p2, vi_tri, goc):
        d = self.msp.add_linear_dim(base=vi_tri, p1=p1, p2=p2, angle=goc, dimstyle=self.dimstyle,
                                    dxfattribs={"layer": "8"})
        d.render()   # không truyền text: giá trị dim luôn là số đo thật
        return d

    def luu(self, duong_dan: str):
        """Lưu DXF rồi kiểm; trả về (danh sách lỗi, danh sách cảnh báo)."""
        import kiem_dxf   # nhập muộn: kiem_dxf nhập hằng số của tệp này
        self.doc.saveas(duong_dan)
        loi, canh_bao = kiem_dxf.kiem(duong_dan)
        kiem_dxf.in_ket_qua(duong_dan, loi, canh_bao)
        return loi, canh_bao
