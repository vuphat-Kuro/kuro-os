# Xuất sang Midas Civil và đối soát

Nút "Xuất MCT (Midas)" ở tab Mô hình, hoặc `chay_kiem_toan.py` (ghi vào `mct/`). Mỗi tầng khung chống một tệp (mỗi giai đoạn một trường hợp tải), mỗi giai đoạn dầm cừ một tệp. Nhập: File, Import, MIDAS MCT File.

## Cấu trúc tệp (đã tự kiểm trước khi xuất)
`*VERSION`, `*UNIT` (TONF, M, ngay đầu tệp), nút, phần tử, vật liệu, tiết diện, trường hợp tải, liên kết (`*CONSTRAINT`, `*SPRING`, `*FRAME-RLS`), tải (`*BEAMLOAD`), tổ hợp (`*LOADCOMB`), `*ENDDATA`. Chương trình kiểm mọi tham chiếu nút, phần tử và số tham số mỗi dòng; sai thì không xuất. Văn bản tự do (tên dự án, mô tả) bị làm sạch dấu phẩy.

## Khung chống mặt bằng
- Phần tử BEAM trong mặt bằng (Z = 0), thép H theo thư viện JIS của Midas (50 trên 53 dòng TCVN 7571-16 trùng tên), q = 1,1 × phản lực tầng chống đặt vào trong hố trên dầm biên.
- Gối tự cân bằng: khóa Dx, Dy ở nút góc 1, Dy ở nút góc 2, Dz ở bốn góc. Phản lực gối trên Midas bằng 0 là đúng.
- Khớp: `*FRAME-RLS`, nhả Mz với ván đứng, My với ván nằm; nút mà mọi đầu đều khớp được khóa thêm Rz. **Cú pháp `*FRAME-RLS` chưa thử trên Midas [CẦN KIỂM TRA].**
- Biến dạng cắt: `bSD = NO`. Nhập tệp cũ có `YES` thì tắt "Include shear deformation" trong tiết diện.

## Dầm cừ dải 1 m
- Nút dọc Z theo cao độ, chỉ tại đỉnh, mũi cừ, gối, lò xo, chỗ tải đổi, cực trị M và δ (6 đến 13 nút). Tải hình thang `UNILOAD GX`; chiều dương +X về phía hố.
- Gối chốt khóa đúng tại nút gối (`110101`, nút trên cùng `111101`), ngàm `111111`; nút khác tự do. Lò xo nền `*SPRING LINEAR` chỉ gồm lò xo đang chịu nén ở nghiệm hội tụ.
- Giai đoạn một tầng chống: hai trường hợp `GDn_N` (nước), `GDn_D` (đất) và tổ hợp `GDn_7-14` = 1·N + 0,75·D, `GDn_TongTai` = N + D.
- Tiết diện `SB` vuông tương đương giữ EI; σ trên Midas không dùng được. Dạng `SB` và `*SPRING` lấy từ tệp mẫu của anh, chạy được khi nhập.

## Đối soát bảng Midas
1. Xuất Beam Force và Beam Stress (xls) cho cùng trường hợp tải.
2. Khung chống: `python chay_kiem_toan.py --config <du_an>.json --khung-json T2:4 --khong-excel --khong-mct --out kq` (tầng T2, giai đoạn 4) ghi `kq/khung_T2_GD4.json`; rồi `python kiem/so_midas_khung.py <Beam Force.xls> <Beam Stress.xls> kq/khung_T2_GD4.json` in lệch lớn nhất của N, V, M, σ và danh sách thanh lệch. Số Midas phải lấy từ mô hình nhập từ tệp MCT do chương trình xuất (cùng cấu hình). Lệch lớn mà mô hình giống nhau: kiểm `bSD` trước (đã đặt NO trong tệp mới), rồi gối, khớp, tiết diện. Nút "Xuất bảng nội lực (CSV)" ở tab Mô hình cho bảng 5 điểm mỗi thanh dạng Beam Force, Beam Stress để so từng số bằng mắt.
3. Ứng suất Combined của Midas: Cb(min/max) = mép có |σ| lớn hơn của N/A ± M/W; chương trình dùng cùng công thức (kiểu Lớn nhất, Nhỏ nhất, Mép 1, Mép 2 ở tab Mô hình).

## Việc chưa kiểm trên Midas thật
`*FRAME-RLS` (chiều nhả), quy ước góc xoay ván nằm (90) và ván đứng (0), tiết diện kép dạng hộp, thép ngoài thư viện JIS (H900x300, H912x302, H918x303 khai kích thước tự nhập).
