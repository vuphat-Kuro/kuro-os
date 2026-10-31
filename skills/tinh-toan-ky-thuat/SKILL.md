---
name: tinh-toan-ky-thuat
description: "Quy trình tính toán kỹ thuật chính xác bằng tool tinh_python: đơn vị, tiết diện, BTCT, nội lực khung; kiểm tra chéo, trích nguồn, lưu script để soát."
---

# Tính toán kỹ thuật chính xác

## Khi nào dùng

Mọi câu hỏi cần ra **con số kỹ thuật**: tải trọng, nội lực, đặc trưng tiết diện, khả năng chịu lực, độ võng,
khối lượng, quy đổi đơn vị, kiểm toán kết cấu phụ trợ. Kể cả phép tính "đơn giản": sai một hệ số là sai cả
hồ sơ. Dùng chung với skill nghiệp vụ (`kiem-toan-ket-cau-phu-tro`, `qs-khoi-luong-du-toan`...): skill
nghiệp vụ nói TÍNH GÌ và theo điều khoản nào, skill này nói TÍNH THẾ NÀO cho đúng.

## Luật bắt buộc

1. **Không tự nhẩm.** Mọi con số đi qua tool `tinh_python`. Câu trả lời ghi đường dẫn script
   (`tinh-toan/<tên>.py`) để người dùng mở ra soát.
2. **Dữ liệu đầu vào phải có nguồn**: kích thước lấy từ bản vẽ nào, tải từ đâu, cường độ vật liệu theo điều
   khoản nào. Hệ số hay cường độ lấy từ trí nhớ thì ghi "(cần xác minh)" ngay cạnh con số. Ưu tiên tra
   `references/` của skill nghiệp vụ và tài liệu trong `sources/` trước.
3. **Đơn vị rõ ràng.** Dùng `pint`, hoặc thống nhất một hệ N - mm - MPa và ghi ở đầu script.
   Nhớ: 1 kN/m = 1 N/mm; 1 kNm = 1e6 Nmm; 1 MPa = 1 N/mm².
4. **Kiểm tra chéo bằng một cách thứ hai**, in cả hai kết quả và độ lệch:
   - thư viện so với công thức tay (ví dụ M = qL²/8),
   - kiểm cân bằng tĩnh (`analyze(check_statics=True)` của PyNite),
   - so với dải hợp lý (hàm lượng thép, tỷ lệ nhịp/chiều cao, độ võng cho phép).
   Lệch quá 2% mà không giải thích được thì **dừng**, báo người dùng, không kết luận.
5. **Kết luận ĐẠT hoặc KHÔNG ĐẠT** chỉ khi đã có đủ: giá trị tính, giá trị cho phép kèm điều khoản, hệ số
   an toàn hay hệ số vượt tải đã áp. Thiếu một thứ thì ghi "chưa đủ dữ liệu để kết luận".

## Trình bày kết quả

1. Bảng đầu vào: đại lượng, giá trị, đơn vị, nguồn.
2. Công thức hoặc mô hình tính (một dòng mỗi bước).
3. Bảng kết quả: đại lượng, giá trị tính, giá trị cho phép, điều khoản, ĐẠT/KHÔNG ĐẠT.
4. Kiểm tra chéo: cách 2 cho bao nhiêu, lệch bao nhiêu phần trăm.
5. Giả định và điểm cần xác minh. Đường dẫn script.

## Mẫu đã kiểm (khớp tính tay, 2026-10-31)

### Đơn vị với pint

```python
import pint
u = pint.UnitRegistry()
q = (25 * u.kN / u.m**3) * (0.3 * u.m) * (0.6 * u.m)     # trọng lượng bản thân dầm 300x600
M = q * (6 * u.m) ** 2 / 8
print(q.to("kN/m"), M.to("kN*m"))                          # 4.5 kN/m, 20.25 kNm
```

### Đặc trưng tiết diện (sectionproperties), đơn vị mm

```python
from sectionproperties.analysis import Section
from sectionproperties.pre.library import rectangular_section   # còn i_section, circular_section, box_girder_section...
g = rectangular_section(d=600, b=300)
g.create_mesh(mesh_sizes=[2000])            # mm2; tiết diện phức tạp thì giảm để lưới mịn hơn
s = Section(g)
s.calculate_geometric_properties()
print(s.get_area(), s.get_ic())             # 180000, (5.4e9, 1.35e9, 0)
```

### Khả năng chịu uốn tiết diện BTCT (concreteproperties), N - mm - MPa

```python
import math
from concreteproperties.concrete_section import ConcreteSection
from concreteproperties.material import Concrete, SteelBar
from concreteproperties.pre import add_bar_rectangular_array
from concreteproperties.stress_strain_profile import ConcreteLinear, RectangularStressBlock, SteelElasticPlastic
from sectionproperties.pre.library import rectangular_section

Rb, Rbt, Eb, Rs, Es = 14.5, 1.05, 30_000, 350, 200_000   # B25, CB400-V theo TCVN 5574:2018 (cần xác minh)
b, h, a_bv, d_bar, n_bar = 300, 600, 40, 20, 3
conc = Concrete("B25", 2.4e-6, ConcreteLinear(elastic_modulus=Eb), "lightgrey",
                RectangularStressBlock(compressive_strength=Rb, alpha=1.0, gamma=0.8, ultimate_strain=0.0035),
                flexural_tensile_strength=Rbt)
steel = SteelBar("CB400-V", 7.85e-6, SteelElasticPlastic(yield_strength=Rs, elastic_modulus=Es, fracture_strain=0.05), "grey")
As1, y0 = math.pi * d_bar**2 / 4, a_bv + d_bar / 2
geom = add_bar_rectangular_array(rectangular_section(d=h, b=b, material=conc), area=As1, material=steel,
                                 n_x=n_bar, x_s=(b - 2 * y0) / (n_bar - 1), n_y=1, anchor=(y0, y0))
M_prog = ConcreteSection(geom).ultimate_bending_capacity().m_x / 1e6
As, h0 = n_bar * As1, h - y0
x = Rs * As / (Rb * b)
M_tay = Rs * As * (h0 - x / 2) / 1e6
print(f"M_tay={M_tay:.1f} kNm, M_lib={M_prog:.1f} kNm, lech={(M_prog - M_tay) / M_tay * 100:+.2f}%")   # 168.9 / 168.9
```

Lưu ý: `concreteproperties` không có sẵn TCVN. Khối ứng suất chữ nhật (`alpha`, `gamma`) và biến dạng giới
hạn phải đặt theo TCVN 5574:2018 và ghi nguồn; còn phải tự kiểm thêm ξ ≤ ξR, hàm lượng thép tối thiểu và
tối đa. Thư viện chỉ giải phần cân bằng tiết diện.

### Nội lực và độ võng khung (PyNite), N - mm

```python
from Pynite import FEModel3D
m = FEModel3D()
m.add_node("A", 0, 0, 0); m.add_node("B", 6000, 0, 0)
m.add_material("B25", E=30_000, G=12_500, nu=0.2, rho=2.4e-9)
m.add_section("300x600", A=180_000, Iy=1.35e9, Iz=5.4e9, J=2.8e9)
m.add_member("D1", "A", "B", "B25", "300x600")
m.def_support("A", True, True, True, True, False, False)    # gối cố định
m.def_support("B", False, True, True, False, False, False)  # gối di động
m.add_member_dist_load("D1", "Fy", -10, -10)                # 10 kN/m hướng xuống
m.analyze(check_statics=True)                                # in bảng cân bằng tĩnh
d1 = m.members["D1"]
print(max(abs(d1.max_moment("Mz")), abs(d1.min_moment("Mz"))) / 1e6,   # 45.00 kNm = qL²/8
      abs(d1.min_deflection("dy")))                                     # 1.042 mm = 5qL⁴/384EI
```

Tổ hợp tải: `m.add_load_combo("TH1", {"TT": 1.1, "HT": 1.2})` rồi gán `case="TT"` khi đặt tải; hệ số lấy theo
tiêu chuẩn tải trọng đang áp dụng, ghi nguồn.

### Thư viện khác đã cài

`numpy`, `scipy` (giải phương trình, tối ưu), `pandas` (bảng), `shapely` (hình học 2D), `ezdxf` (đọc/ghi DXF),
`openpyxl` (Excel), `python-docx` (Word), `pdfplumber` (đọc bảng trong PDF tiêu chuẩn), `ifcopenshell`
(đọc mô hình IFC, bóc khối lượng), `matplotlib` (vẽ biểu đồ, lưu PNG vào `tinh-toan/`).

## Bẫy

- Trộn kN với N, m với mm: luôn ghi hệ đơn vị ở dòng đầu script.
- PyNite: trục `Fy` là trục đứng toàn cục; tải hướng xuống mang dấu âm.
- Script quá 120 giây sẽ bị dừng: mô hình lớn thì chia nhỏ hoặc giảm độ mịn lưới.
- Không đọc hay ghi file ngoài brain trong script tính toán.
