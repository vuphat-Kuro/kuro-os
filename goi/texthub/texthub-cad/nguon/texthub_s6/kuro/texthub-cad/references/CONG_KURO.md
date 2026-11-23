# Cổng Kuro: điều khiển TextHub trong AutoCAD

## Điều kiện

1. Plugin đã cài (`python scripts/texthub_setup.py status` cho `da_cai`) và AutoCAD đã mở lại.
2. Người dùng mở đúng bản vẽ, gõ `PKTEXTBRIDGE`, gõ `yes` (hoặc bảng `PKTEXTUI`, thẻ **Trợ lý**, nút **Mở cổng Kuro**). Trong AutoCAD giao diện, cổng chạy không chặn: người dùng vẫn dùng AutoCAD bình thường; mỗi thao tác ghi hiện một hộp thoại Yes/No.
3. Đóng cổng: `PKTEXTBRIDGESTOP`, nút **Đóng cổng**, hoặc gọi `shutdown`; tự đóng sau 30 phút không dùng.
4. Kuro nối bằng `scripts/texthub_cad.py` (mỗi lệnh một phương thức) hoặc máy chủ MCP `scripts/pkttc_mcp.py` (khai báo mẫu: `mcp.example.json`).

## Phương thức (script) và công cụ MCP tương ứng

| Phương thức | Công cụ MCP | Việc | Ghi vào bản vẽ |
|---|---|---|---|
| `ping` | `pkttc_ping` | Kiểm tra kết nối; bản AutoCAD, bản vẽ đang mở, kế hoạch đang chờ, số tệp kho font | Không |
| `scan` | `pkttc_scan` | Quét mọi loại chữ; tổng hợp theo loại, bảng mã, cờ, style. `items`: `none`, `flagged`, `all`; `offset`, `limit` (tối đa 500) | Không |
| `fonts` | `pkttc_fonts` | Font của style, BigFont, mã `\f`/`\F` trong MTEXT, đối chiếu máy và kho font | Không |
| `plan.create` | `pkttc_plan_create` | Lập kế hoạch đổi sang Unicode. Tham số: `targetFont` (mặc định Arial Unicode MS), `targetShxFont` (mặc định uv-abc.shx), `fontMap` (font nguồn sang font đích), `targetStyle`, `keepWidth`, `includeLocked` | Không |
| `plan.get` | `pkttc_plan_get` | Xem các mục của kế hoạch (phân trang) | Không |
| `plan.apply` | `pkttc_plan_apply` | Áp dụng kế hoạch (chỉ `planId`, tùy chọn `note`) | Có, sau khi người dùng bấm Yes |
| `fontsub.plan` / `fontsub.apply` | `pkttc_fontsub_plan` / `pkttc_fontsub_apply` | Thay font Style bị thiếu bằng font có sẵn | Có, sau Yes |
| `purge.plan` / `purge.apply` | `pkttc_purge_plan` / `pkttc_purge_apply` | Dọn Style chữ không dùng | Có, sau Yes |
| `shutdown` | `pkttc_shutdown` | Đóng cổng | Không |

## Quy tắc bắt buộc

1. Công cụ `*.apply` xin phép người dùng trong AutoCAD (hộp thoại Yes/No, mặc định No, kèm tên máy khách, mã kế hoạch, số mục, ghi chú, 5 mục mẫu). Cuộc gọi chờ đến khi người dùng trả lời. Kuro không thể tự phê duyệt.
2. `rejected`: dừng, hỏi lại người dùng; không gọi lại tự động.
3. Luôn lập kế hoạch và cho người dùng xem tóm tắt (số mục, mục bị bỏ qua và lý do, font đích, vài mẫu) trước khi áp dụng. Chữ ở font HOA (`.VnAvantH`...) sẽ thành chữ HOA Unicode vĩnh viễn: nói rõ khi có.
4. Chỉ gửi `planId`, không gửi nội dung chữ để ghi; mỗi kế hoạch chỉ áp dụng một lần; cổng đóng thì kế hoạch mất.
5. Trước mỗi lần ghi TextHub sao lưu bản vẽ vào `<thư mục bản vẽ>\_backup\YYYYMMDD\` và ghi `_log.md`. Người dùng hoàn tác bằng `U` (một bước). TextHub không tự lưu bản vẽ.
6. Mọi yêu cầu được ghi vào `%LOCALAPPDATA%\PKTTC\bridge\audit.log` (giờ, tên máy khách, phương thức, kết quả, đồng ý hay từ chối).
7. Cổng chỉ nhận kết nối từ đúng tài khoản Windows của người dùng đang mở AutoCAD, không nhận kết nối qua mạng.

## Phân loại font SHX (đọc từ header tệp)

`unifont` = Unicode (ví dụ `VN_UNI.shx`, `uv-abc.shx`, `3T-Unicode.shx`, `txt.shx`); `shapes` = 8 bit TCVN3 (`vn-abc`, `vntime`, `vnsimple`); `bigfont` = BigFont (`vn1`).
