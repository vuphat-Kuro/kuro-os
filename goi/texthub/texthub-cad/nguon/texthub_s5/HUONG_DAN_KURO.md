# Cổng cho trợ lý (Kuro): điều khiển PKTTC TextHub trong AutoCAD

## Điều kiện

1. Plugin đã cài và AutoCAD đã mở lại (TextHub tự nạp; gõ `PKTEXTABOUT` để kiểm tra).
2. Người dùng mở đúng bản vẽ, gõ `PKTEXTBRIDGE`, gõ `yes` (hoặc bảng `PKTEXTUI`, thẻ **Trợ lý**, nút **Mở cổng Kuro**). Trong AutoCAD giao diện cổng chạy **không chặn**: người dùng vẫn dùng AutoCAD bình thường; mỗi thao tác ghi của trợ lý hiện một hộp thoại Yes/No. Cổng làm việc trên bản vẽ đang hiện lúc mở.
3. Đóng cổng: `PKTEXTBRIDGESTOP`, nút **Đóng cổng**, hoặc trợ lý gửi `shutdown`; tự đóng sau 30 phút không dùng.
4. Chế độ chặn (vòng lặp trong lệnh, xin phép bằng gõ `YES` trên dòng lệnh) chỉ dùng cho `accoreconsole` hoặc khi đặt biến môi trường `PKTTC_BRIDGE_MODE=loop`.
5. Trợ lý nối bằng máy chủ MCP `Contents\Bridge\pkttc_mcp.py` hoặc thư viện `Contents\Bridge\pkttc_client.py` (Python 3, chỉ thư viện chuẩn). Trợ lý và AutoCAD phải chạy trên cùng máy Windows, cùng tài khoản người dùng.

## Công cụ MCP

| Công cụ | Việc | Ghi vào bản vẽ |
|---|---|---|
| `pkttc_ping` | Kiểm tra kết nối; phiên bản AutoCAD, bản vẽ đang mở, kế hoạch đang chờ | Không |
| `pkttc_scan` | Quét mọi loại chữ; tổng hợp theo loại, bảng mã, cờ, style. `items`: `none`, `flagged`, `all`; `offset`, `limit` (tối đa 500) | Không |
| `pkttc_fonts` | Font của style, BigFont, mã `\f`/`\F` trong MTEXT, đối chiếu máy và kho font; gợi ý thay thế | Không |
| `pkttc_plan_create` | Lập kế hoạch đổi sang Unicode. `targetFont` (mặc định Arial Unicode MS, cho font nguồn TrueType), `targetShxFont` (mặc định uv-abc.shx, cho font nguồn SHX), `fontMap` (font nguồn sang font đích từng loại), `targetStyle`, `keepWidth`, `includeLocked` | Không |
| `pkttc_plan_get` | Xem các mục của kế hoạch (phân trang) | Không |
| `pkttc_plan_apply` | Áp dụng kế hoạch (chỉ `planId`, tùy chọn `note`) | Có, sau khi người dùng bấm Yes |
| `pkttc_fontsub_plan` / `pkttc_fontsub_apply` | Thay font Style bị thiếu bằng font đã có trên máy | Có, sau Yes |
| `pkttc_purge_plan` / `pkttc_purge_apply` | Dọn Style chữ không dùng | Có, sau Yes |
| `pkttc_shutdown` | Đóng cổng | Không |

## Quy tắc bắt buộc

1. Công cụ `*_apply` xin phép người dùng trong AutoCAD: hộp thoại Yes/No (mặc định No) kèm tên trợ lý, mã kế hoạch, số mục, ghi chú và 5 mục mẫu. Cuộc gọi chờ đến khi người dùng trả lời. Trợ lý không thể tự phê duyệt.
2. `rejected`: dừng, hỏi lại người dùng; không gọi lại tự động.
3. Luôn `plan_create` và cho người dùng xem tóm tắt (số mục, mục bị bỏ qua và lý do, font đích, vài mẫu) trước khi `plan_apply`. Chữ ở font HOA (`.VnAvantH`...) sẽ thành chữ HOA Unicode vĩnh viễn: nói rõ khi có.
4. Chỉ gửi `planId`, không gửi nội dung chữ để ghi; mỗi kế hoạch chỉ áp dụng một lần; cổng đóng thì kế hoạch mất.
5. Trước mỗi lần ghi TextHub sao lưu bản vẽ vào `<thư mục bản vẽ>\_backup\YYYYMMDD\` và ghi `_log.md`. Người dùng hoàn tác bằng `U` (một bước). TextHub không tự lưu bản vẽ.
6. Mọi yêu cầu được ghi vào `%LOCALAPPDATA%\PKTTC\bridge\audit.log` (giờ, tên máy khách, phương thức, kết quả, đồng ý hay từ chối).
7. Cổng chỉ nhận kết nối từ đúng tài khoản Windows của người dùng đang mở AutoCAD, không nhận kết nối qua mạng.

## Phân loại font SHX (đọc từ header tệp)

`unifont` = Unicode (ví dụ `VN_UNI.shx`, `uv-abc.shx`, `3T-Unicode.shx`, `txt.shx`); `shapes` = 8 bit TCVN3 (`vn-abc`, `vntime`, `vnsimple`); `bigfont` = BigFont (`vn1`).
