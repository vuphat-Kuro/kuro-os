# Cấu hình đường dẫn - Xác nhận thanh quyết toán

> Đọc khi bắt đầu một hồ sơ xác nhận. Kiểm ngày 17/11/2026. Ổ Y hoặc đường dẫn mạng UNC là dữ liệu chung, máy nào cũng truy cập được. Mục đánh dấu "chưa kiểm" thì phải mở thử trước khi dùng.

## 1. Gốc dữ liệu
- Ổ dữ liệu chung Phòng KT-TC: `Y:\` (hoặc UNC: `\\phuongthanhtranconsin.data.com\12.KỸ THUẬT THI CÔNG\`)
- Thư viện Phòng: `Y:\5. THU VIEN PHONG\` (hoặc `\\phuongthanhtranconsin.data.com\12.KỸ THUẬT THI CÔNG\5. THU VIEN PHONG\`)
- Mẫu hồ sơ đóng gói chuẩn trong Kuro:
  - `tools\XacNhanThanhQuyetToan\mau\MAU_XNKL-DOT_KTTC.xlsx` (hoặc `QLDA\03-MauBieu\02-Excel\MAU_XNKL-DOT_KTTC.xlsx`): mẫu đợt (TTC, 1.XNKL, 4.DGTD).
  - `tools\XacNhanThanhQuyetToan\mau\MAU_XNKL-QT_KTTC.xlsx` (hoặc `QLDA\03-MauBieu\02-Excel\MAU_XNKL-QT_KTTC.xlsx`): mẫu quyết toán (đủ TTC, 1.XNKL, 2.VTC, 3.VTLC, 4.DGTD).

## 2. Cấu trúc thư mục từng dự án
Mỗi dự án nằm ở `Y:\<tên dự án>\` (hoặc `\\phuongthanhtranconsin.data.com\12.KỸ THUẬT THI CÔNG\<tên dự án>\`). Các thư mục cần dùng:

| Thư mục | Nội dung |
|---|---|
| `5. XAC NHAN KHOI LUONG\2. DOI CHIEU NHAN CONG\<tên đội>\` | Phiếu Phòng đã ký (`KTTC_<đội>_XNKL D<n> ....pdf`) và bản đối chiếu của BĐH |
| `5. XAC NHAN KHOI LUONG\2. DOI CHIEU NHAN CONG\HOP DONG\` | Hợp đồng PDF đánh số (1.pdf, 2.pdf, ...) và index xlsx |
| `0. TK BVTC\` | Bản vẽ thi công (nếu dự án có thư mục này) |

Thư mục đội có thể đánh số (`14. Huong Giang`) hoặc không (`Tran Quyet Chi`). Tìm theo tên đội không dấu.

## 3. Bảng dự án đã biết

| Dự án | Đường dẫn gốc | BVTC | Hợp đồng và index | Trạng thái |
|---|---|---|---|---|
| Mở rộng đoạn cao tốc TP. HCM - Long Thành (gói XL01) | `Y:\GOI XL01 MO RONG LONG THANH\` | `Y:\GOI XL01 MO RONG LONG THANH\0. TK BVTC\` | `HOP DONG\` có 1.pdf đến 5.pdf. Không có HĐ 372/HĐTC.2026 (đội Hương Giang). File `01-DANH MUC HD VD5 TN.xlsx` là bản sao sai, không dùng. | Đã có phiếu đợt 1 Hương Giang: `5. XAC NHAN KHOI LUONG\2. DOI CHIEU NHAN CONG\14. Huong Giang\` |
| Gói 15 - Cầu Bến Rừng | `Y:\GOI 15 - CAU BEN RUNG\` | chưa xác định, dò trong dự án | `HOP DONG\` có 1.pdf đến 5.pdf và `01-DANH MUC HD VD5 TN.xlsx` (chưa kiểm nội dung, nghi là bản sao sai) | Đội Trần Quyết Chí (mẫu đợt D8 đọc từ D:\GoogleDrive, chưa kiểm trên Y:) |
| Tiền Yên - Móng Cái | `Y:\TIEN YEN-MONG CAI\` | chưa xác định | `HOP DONG\01-DANH MUC HD TIEN YEN - MONG CAI.xlsx` (chưa kiểm nội dung) | |
| Gói 13 XL - Cầu Vĩnh An (MSQL45) | `Y:\GOI 13XL-MSQL45 CAU VINH AN\` | chưa xác định | `HOP DONG\01-DANH MUC HD G13 - CAU VINH AN.xlsx` (chưa kiểm nội dung) | |
| 2021 - Gói 2XL Phan Thiết - Dầu Giây | `Y:\2021. GOI 2XL-PHAN THIET - DAU GIAY - KTTC\` | chưa xác định | `HOP DONG\01-DANH MUC HD G2XL - PTDG.xlsx` (chưa kiểm nội dung) | |

Dự án khác (xem danh sách thư mục trên Y: hoặc UNC): dùng cùng cấu trúc mục 2. Ghi bổ sung vào bảng sau khi kiểm.

## 4. Index hợp đồng công ty (Đường dẫn chính xác)
- **Kho Hợp đồng Đội thi công & Thầu phụ:**
  - Đường dẫn UNC: `\\phuongthanhtranconsin.data.com\4.HÀNH CHÍNH QUẢN TRỊ\HỢP ĐỒNG KINH TẾ - HỢP ĐỒNG DỰ ÁN\Hợp đồng kinh tế - Linh\HỢP ĐỒNG\`
  - Tệp Excel index bắt buộc: `TỔNG HỢP.xlsx` (các sheet: `HĐ Phương Thành`, `HĐ Đối Tác`, `HĐ Khai Thác Mỏ`...).
- **Kho Hợp đồng các Dự án (Chủ đầu tư / Ban QLDA):**
  - Đường dẫn UNC: `\\phuongthanhtranconsin.data.com\4.HÀNH CHÍNH QUẢN TRỊ\HỢP ĐỒNG KINH TẾ - HỢP ĐỒNG DỰ ÁN\HĐ các Dự án\`
  - Tệp Excel index bắt buộc: `DANH MỤC HỌP ĐỒNG, PHỤ LỤC HỢP ĐỒNG DỰ ÁN.xls`.
- **Quy tắc VÀNG:** Tuyệt đối không quét đệ quy toàn bộ thư mục hợp đồng vì dữ liệu rất lớn. Mọi tra cứu hợp đồng BẮT BUỘC thực hiện qua file Excel đầu mục, xác định chính xác số HĐ, năm ký hoặc mã dự án rồi mới truy cập thẳng vào thư mục đích lấy file scan.

## 5. Quy tắc lưu tệp kết quả & Bảo vệ kho dữ liệu công ty
- **Kho mạng UNC / Ổ Y: LÀ KHO CHỈ ĐỌC / TRA CỨU (READ-ONLY):**
  - Kho mạng `\\phuongthanhtranconsin.data.com\...` (hoặc ổ `Y:\`) chỉ phục vụ đọc, tra cứu hồ sơ và lấy file mẫu.
  - **TUYỆT ĐỐI KHÔNG** tự ý lưu tệp kết quả, tạo thư mục rác hay ghi đè vào kho mạng chung này (trừ khi có chỉ đạo rõ ràng từ người dùng).
  - **CẤM XÓA, KỂ CẢ KHI NGƯỜI DÙNG YÊU CẦU:** Kuro không xóa bất kỳ tệp hay thư mục nào trên kho mạng / ổ `Y:\`. Người dùng tự xóa bằng tay; Kuro chỉ ghi rõ đường dẫn cần xóa.
  - **KHÔNG tự động tạo tệp:** chỉ thêm hoặc tạo tệp trên kho mạng khi người dùng yêu cầu đích danh việc thêm/tạo tệp đó (chức năng Thêm/Tạo tệp), đúng tệp và đúng vị trí được yêu cầu.
- **Vị trí lưu kết quả bắt buộc (Active Workspace trên máy người dùng):**
  - Mọi tệp tin kết quả do AI/tool sinh ra (.xlsx, .html, .docx, .py, script, báo cáo, biểu mẫu...) **BẮT BUỘC lưu vào thư mục dự án hiện hành trên máy người dùng đang cài** (Active Workspace đang mở trong Kuro, ví dụ: `D:\1`, thư mục dự án trên máy cục bộ).
  - Với dự án có cấu trúc 9 thư mục: lưu vào `<Workspace>\5. XAC NHAN KHOI LUONG\<Ten_Doi>\`.
  - Với dự án thông thường: lưu vào `<Workspace>\XAC_NHAN_KHOI_LUONG\` hoặc ngay thư mục dự án hiện hành.
  - **TUYỆT ĐỐI KHÔNG** lưu vào đường dẫn `QLDA\99-Temp\` hay bất kỳ thư mục ảo nào khác.
- **Nguyên tắc hỏi vị trí lưu khi chưa rõ:**
  - Nếu trong thư mục dự án hiện hành chưa có quy tắc phân loại thư mục lưu (hoặc chưa rõ cấu trúc lưu cho hạng mục đó), **BẮT BUỘC hỏi lại người dùng** xem muốn lưu tệp ở đâu, tuyệt đối không tự ý lưu vào các vị trí chưa được phép.

## 6. Quy ước tra cứu
- Phiếu đợt trước: lọc `KTTC_<tên đội>_XNKL D<n>*` trong thư mục đội. Chỉ dùng bản có chữ ký Phòng KT-TC.
- Hợp đồng: mở đúng một PDF theo số HĐ hoặc qua file Excel index. Không duyệt cả thư mục hợp đồng của nhiều năm.
- BVTC: `0. TK BVTC\` của dự án, phần khối lượng.
- Hỗ trợ cả đường dẫn bắt đầu từ `Y:\` hoặc đường dẫn UNC `\\phuongthanhtranconsin.data.com\12.KỸ THUẬT THI CÔNG\`.
