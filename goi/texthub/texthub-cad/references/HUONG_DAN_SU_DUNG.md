# Sử dụng PKTTC TextHub

## Nguyên tắc an toàn

- Lệnh quét, báo cáo và lập kế hoạch chỉ đọc: không sửa bản vẽ.
- Lệnh ghi luôn hỏi bạn gõ `YES` (hoặc bấm Yes khi trợ lý yêu cầu), sao lưu bản vẽ trước, ghi trong một bước. Hoàn tác bằng lệnh `U`.
- TextHub không tự lưu bản vẽ. Xem kết quả, hài lòng thì lưu.
- Bản sao lưu nằm ở `<thư mục bản vẽ>\_backup\YYYYMMDD\` kèm nhật ký `_log.md`.

## Bảng PKTEXTUI và menu KTTC

Gõ `PKTEXTUI` (hoặc chọn menu **KTTC > Text > Convert Font > PKTEXTUI**) để mở bảng TextHub. Bảng làm việc trên bản vẽ đang hiện, không chặn AutoCAD, gồm 5 thẻ:

1. **Quét:** đếm chữ theo bảng mã và cờ lỗi; bấm đúp một dòng để chọn và phóng tới chữ đó (chữ trong định nghĩa block thì chỉ báo vị trí).
2. **Đổi chữ:** (a) bấm **Quét font nguồn**: bảng liệt kê từng loại font cũ có chữ cần đổi (ví dụ `.VnAvantH`, `vn-abc.shx`) và số mục; (b) font đích đã chọn sẵn theo loại font nguồn: nguồn TrueType sang **Arial Unicode MS**, nguồn SHX sang **uv-abc.shx** (hai ô "Nguồn TrueType" và "Nguồn SHX", đổi được; nút **Đặt lại theo mặc định** áp lại cho mọi dòng); mỗi dòng đổi riêng trong cột "Font đích" (3 font Unicode `Arial Unicode MS`, `uv-abc.shx`, `3T-Unicode.shx` ghim đầu danh sách, sau đó mọi TrueType đã cài và SHX Unicode); cột ghi chú cho biết font đã in thử hay chưa; font đích chưa cài trên máy mà kho font có thì hiện nút **Cài font đích thiếu từ kho** (hỏi xác nhận, cài cho người dùng hiện tại, cần mở lại AutoCAD); (c) bấm **Lập kế hoạch**, xem cột **Xem trước** (chữ cũ vẽ bằng font TCVN3 gốc, chữ mới bằng font đích; SHX không xem trước được), bỏ chọn mục không muốn đổi; (d) bấm **Áp dụng mục đã chọn** và xác nhận. Sao lưu trước, đổi trong một bước, hoàn tác bằng `U`. Mỗi font đích có một style riêng đặt theo tên font (`Segoe UI`, `VN_UNI`...).
3. **Font:** báo cáo font của bản vẽ; **Thay font thiếu** và **Dọn style không dùng** (đều hỏi xác nhận, sao lưu, hoàn tác bằng `U`).
4. **Kho font:** thư mục và số tệp kho; mở thư mục kho; lưu script cài font thiếu (chỉ xem, không tự cài).
5. **Trợ lý:** mở hoặc đóng cổng Kuro, xem nhật ký.

Menu **KTTC** nằm cuối thanh menu, tạo mỗi lần AutoCAD khởi động (không sửa tệp CUIX của bạn). Nhóm **Text > Convert Font** liệt kê các lệnh bên dưới, mỗi dòng có giải thích ngắn; rê chuột để xem mô tả đầy đủ ở thanh trạng thái. Menu chỉ hiện khi thanh menu được bật (biến `MENUBAR` = 1).

## Lệnh

| Lệnh | Việc | Ghi vào bản vẽ |
|---|---|---|
| `PKTEXTUI` | Mở bảng TextHub (5 thẻ như trên) | Không (nút ghi trong bảng hỏi xác nhận) |
| `PKTEXTABOUT` | Phiên bản, danh sách lệnh, kho font, trạng thái cổng trợ lý | Không |
| `PKTEXTSCAN` | Quét TEXT, MTEXT, ATTRIB, ATTDEF, MLEADER, DIMENSION, ô bảng, cả bên trong block; ghi tệp JSON | Không |
| `PKTEXTAUDIT` | Tóm tắt trên dòng lệnh: số lượng theo loại, bảng mã, cờ cảnh báo, style thiếu font | Không |
| `PKTEXTPLAN` | Lập kế hoạch đổi chữ TCVN3 và VNI sang Unicode, ghi tệp JSON | Không |
| `PKTEXTAPPLY` | Áp dụng một kế hoạch đã lập | Có |
| `PKTEXTFIX` | Lập kế hoạch rồi áp dụng ngay | Có |
| `PKTEXTFONT` | Báo cáo font (style, BigFont, mã `\f`/`\F` trong MTEXT), đối chiếu máy và kho font, sinh script cài font | Không |
| `PKTEXTFONTSUB` | Thay font của style bị thiếu bằng font đã có trên máy | Có |
| `PKTEXTPURGE` | Xóa style chữ không dùng (không bao giờ xóa `Standard`) | Có |
| `PKTEXTBRIDGE` / `PKTEXTBRIDGESTOP` | Mở và đóng cổng cho trợ lý (Kuro) | Không (trợ lý xin phép khi ghi) |

## Quy trình đổi chữ cũ sang Unicode

1. `PKTEXTAUDIT` để xem bản vẽ có bao nhiêu chữ TCVN3 hoặc VNI (cờ `legacy`) và chữ sai bảng mã so với font (cờ `mismatch`).
2. `PKTEXTFIX`, xem tóm tắt (số mục sẽ đổi, mục bị bỏ qua và lý do, style đích), gõ `YES`.
3. Kiểm tra bản vẽ. Chưa ổn thì gõ `U`. Ổn thì lưu bản vẽ.
4. `PKTEXTPURGE` để dọn các style cũ không còn dùng (tùy chọn).

Font đích mặc định: chữ ở font nguồn TrueType sang **Arial Unicode MS**, chữ ở font nguồn SHX sang **uv-abc.shx**. Có thể chọn font đích khác cho từng loại font nguồn (bảng trong thẻ Đổi chữ, hoặc tham số `fontMap`, `targetFont`, `targetShxFont` khi trợ lý lập kế hoạch). Style đích đặt theo tên font (`Arial Unicode MS`, `uv-abc`). Arial Unicode MS đi kèm Microsoft Office; máy không có thì cài từ kho font (`05-ThuVien\06-Kho-Font\TTF\ARIALUNI.ttf`) và chỉ trên máy có giấy phép Office. Style cùng tên đã dùng đúng font đó thì được dùng lại; trùng tên nhưng khác font thì thêm hậu tố, ví dụ `Segoe UI_2`. Không dùng Arial, Tahoma, Verdana, Times kiểu thường làm font đích: trên AutoCAD 2020 (máy em thử) các font này không vẽ được chữ Việt `Ả Ế ọ Ố Ỡ Ơ Ư` (hiện ô trống). Arial Unicode MS, Segoe UI, Calibri đã thử và vẽ đủ 134 chữ Việt.

## Cần biết

- Chữ ở font HOA TCVN3 (`.VnTimeH`, `.VnAvantH`, `.VnArialH`...) hiển thị toàn chữ HOA; sau khi đổi, chữ trở thành chữ HOA Unicode vĩnh viễn.
- Mục chữ trên layer khóa, mục có field, mục có ký tự không đổi được và mục không chắc chắn được bỏ qua và liệt kê trong tóm tắt. DIMENSION chữ cũ chưa được đổi.
- Giữ độ rộng chữ được bật mặc định: chữ có thể bị nén hoặc giãn nhẹ để khớp độ rộng cũ.
- Khi có nghi ngờ về bảng mã của một đoạn chữ, TextHub giữ nguyên và báo là không chắc chắn, không tự đoán.
