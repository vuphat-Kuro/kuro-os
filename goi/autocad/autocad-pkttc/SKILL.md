---
name: autocad-pkttc
description: "CHỈ dùng khi TẠO, SỬA hoặc XUẤT bản vẽ AutoCAD (DXF/DWG) hoặc kiểm một bản vẽ theo chuẩn trình bày: kiểu chữ Unicode, cỡ chữ, layer và nét in, dim, text, viewport. Không dùng khi chỉ đọc, hỏi nội dung bản vẽ hoặc việc không vẽ."
---

# Vẽ và xuất DXF theo chuẩn PKTTC (chữ Unicode)

Quy tắc chi tiết, nguồn và các điểm chưa chốt: `references/quy-chuan.md`. Chỉ mở khi cần tra.

## Quy trình

1. **Không tự viết layer, kiểu chữ, DimStyle.** Dùng `scripts/pkttc_dxf.py` (đã dựng sẵn đúng chuẩn). Thêm
   `scripts/` của skill này vào `sys.path` rồi:
   ```python
   from pkttc_dxf import BanVe
   bv = BanVe(ty_le=50)                                  # tỷ lệ in 1:50, đơn vị mm, DimStyle D50
   bv.net([(0, 0), (1000, 0), (1000, 500)], layer="1")   # nét theo layer 1..9
   bv.text("Mặt cắt 1-1", (0, -300), nhom=2.5)           # chữ Unicode, layer 3, cao = nhom x tỷ lệ
   bv.dim_ngang((0, 0), (1000, 0), (0, -150))            # dim layer 8, DimStyle D50, không sửa tay
   bv.luu("ten_tep.dxf")                                 # lưu rồi tự kiểm, in lỗi nếu có
   ```
2. **Lưu vào thư mục dự án đang mở**, tên `YYYYMMDD_MaDA_LoaiTL_NoiDung_vX.dxf`. Không ghi vào kho UNC.
3. **Kiểm trước khi giao:** `python scripts/kiem_dxf.py <tep.dxf>` (thoát 0 là đạt). Báo cho người dùng kết quả
   đúng như script in ra, kể cả cảnh báo. Không báo "đạt chuẩn" khi chưa chạy.
4. **DWG:** script chỉ ra DXF. Muốn DWG thì người dùng mở DXF bằng AutoCAD rồi `SAVEAS` (R2018). Không hứa đã có DWG.

## Luật cứng (tóm tắt)

- Mọi `TEXT`/`MTEXT` ở layer `3`; `DIMENSION`/`LEADER`/`HATCH` ở layer `8`; màu, kiểu nét, độ dày: `ByLayer`.
- Chữ chỉ dùng chuỗi Unicode có dấu, kiểu chữ TTF Unicode. Cấm kiểu chữ TCVN3 (`vn-abc`, `KT`, `VA*`).
- Cao chữ = nhóm (1,5 / 2,0 / 2,5 / 3,5 mm trên giấy) x tỷ lệ in.
- Dim dùng DimStyle `D<tỷ lệ>`. Cấm sửa tay giá trị dim.
- Viewport nằm layer `DEFPOINTS`, tỷ lệ chẵn trong dãy cho phép, đã khóa.
- Con số kích thước, cao độ, khối lượng vẫn phải tính bằng `tinh_python`, không nhẩm.

## Chưa làm trong gói này

Dựng layout và viewport tự động, đọc DWG, lập danh mục bản vẽ, chạy AutoLISP. Việc đó thì nói rõ là chưa có.
