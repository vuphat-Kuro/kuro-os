# Quy chuẩn vẽ và xuất DXF PKTTC, bản chữ Unicode

Nguồn: `QLDA/06-QuyTac/06-QuyChuan-CAD.md` (Mục 10.2) của Phòng KT-TC, rút phần vẽ và xuất DXF.
Hằng số nằm ở đầu `scripts/pkttc_dxf.py`: sửa ở đó thì cả script vẽ và script kiểm đổi theo.

## 1. Không gian vẽ và đơn vị
- Model Space tỷ lệ 1:1, đơn vị mm. Cao độ ghi bằng m, lý trình dạng `Km12+345.67`.
- Khung tên và viewport ở Layout. Tỷ lệ viewport là số nguyên trong dãy 5, 10, 20, 25, 30, 50, 100, 150, 200, 250, 500, 1000.
- Khung viewport ở layer `DEFPOINTS` (không in), đã khóa khung nhìn.

## 2. Layer và nét in (100% ByLayer)
| Layer | Màu | Kiểu nét | Dùng cho |
|:-:|:-:|:-:|---|
| 1 | 1 | Continuous | Nét thấy chính, thép chủ |
| 2 | 2 | Continuous | Nét thấy mảnh |
| 3 | 3 | Continuous | Toàn bộ TEXT, MTEXT |
| 4 | 4 | HIDDEN | Nét khuất |
| 5 | 5 | Continuous | Nét phụ, đường gióng mảnh |
| 6 | 6 | Continuous | Chi tiết phụ trợ, thép đai |
| 7 | 7 | Continuous | Nét cắt đậm, khung tên |
| 8 | 8 | Continuous | DIM, LEADER, HATCH |
| 9 | 9 | CENTER | Tim, trục |
| DEFPOINTS | 7 | Continuous | Khung viewport, không in |

Nét in theo `KTTC_PlotStyleTable.ctb` (mm): 1 = 0,25; 2 = 0,18; 3 = 0,15; 4 = 0,20; 5 = 0,10; 6 = 0,13; 7 = 0,30; 8 = 0,15; 9 = 0,18.
Bản vẽ biện pháp thi công có bảng layer riêng (đường cắt KCPT layer 7, cấu kiện chính KCPT layer 1, cấu kiện phụ layer 2,
liên kết layer 6, công trình vĩnh cửu làm nền layer 5): xem Mục 10.2, tiểu mục 2 của file nguồn.

## 3. Chữ
- Chỉ dùng chuỗi Unicode. Ký hiệu: `%%c` (Ø), `%%d` (°), `%%p` (±).
- Cao chữ trên giấy theo nhóm: 1,5 / 2,0 / 2,5 / 3,5 mm. Cao chữ trong Model = nhóm x tỷ lệ in.
- Mọi chữ ở layer `3`. Cấm kiểu chữ TCVN3 (`vn-abc`, `KT`, `VA`, `VAB`, `VAH*`, `*BVN*`) trong gói này.

## 4. Dim
- DimStyle tên `D<tỷ lệ>` (D50 cho 1:50). Dim, leader, hatch ở layer `8`.
- Thông số chuẩn SDS: `DIMCLRD = 8`, `DIMCLRE = 8`, `DIMCLRT = 3`, `DIMTXT = 2,0`, `DIMASZ = 1,25`, `DIMEXE = 0,6`,
  `DIMEXO = 0,8`, `DIMGAP = 0,5`, `DIMDEC = 0`, `DIMTAD = 1`, `DIMSCALE = tỷ lệ`.
- Cấm sửa tay giá trị chữ của dim (dim override).

## 5. Điểm chưa chốt, cần anh Nghĩa xác nhận
1. **Kiểu chữ Unicode cho từng nhóm.** File nguồn chỉ liệt kê Unicode cho: 1,5 = `Arial`; 2,0 = `uv-abc`/`3TU` (SHX
   `3T-Unicode.shx`); 2,5 = `ArialH`. Nhóm 3,5 mm chỉ có kiểu TCVN3 (`VAHB`). Script đang dùng `Arial` (arial.ttf)
   cho 1,5 và 2,0, `ArialH` (arialbd.ttf) cho 2,5 và 3,5. Lý do: TTF có sẵn trên mọi máy Windows, SHX thì không.
2. **Kiểu chữ của dim.** Nguồn ghi `DIMTXSTY = KT` (TCVN3). Script dùng `Arial` để dim cũng là Unicode.
3. **`LTSCALE`.** Nguồn ghi 40 trong Model, 4 trong Layout, nhưng bộ `VeBPTCVongVay` đặt theo từng thực thể (tỷ lệ x 0,5).
   Script chưa kiểm và chưa đặt `LTSCALE`.
4. **Kiểm cỡ chữ** chưa gắn từng chữ với viewport chứa nó: chữ hợp lệ khi chia cho một trong các tỷ lệ của bản vẽ
   (các DimStyle `D<n>`, tỷ lệ viewport, hoặc 1) ra đúng một nhóm chuẩn.
