# Kết quả S5 - cổng cho Kuro và sửa phân loại SHX

Trạng thái: ĐẠT trên bản vẽ mẫu (headless); chưa thử trong AutoCAD giao diện đầy đủ. Ngày: 2026-11-21. Thư mục: `QLDA/99-Temp/texthub_s5/`.

## Trả lời hai câu hỏi về SHX

Em đọc header tệp (`AutoCAD-86 <loại> 1.0`), không đoán theo tên:

| Tệp | Header | Kết luận |
|---|---|---|
| `uv-abc.shx` | `unifont` | Unicode. Anh đúng; em từng xếp nhầm là TCVN3 trong kho |
| `VN_UNI.shx` | `unifont` | Unicode (cũng khớp dữ liệu bản vẽ thật: 809 mục style "2" chủ yếu là chữ Unicode) |
| `3T-Unicode`, `unicode`, `ads civil`, `txt`, `romans`, `simplex` | `unifont` | Unicode |
| `vn-abc`, `vntime`, `vntimeh`, `vnsimple` | `shapes` | 8 bit, TCVN3 |
| `VN1`, `vns` | `bigfont` | BigFont (em từng xếp nhầm `vns` là TCVN3) |

Đã sửa: kho font (`_tao_kho.ps1`, `_danh_sach.csv`, `README.md`), `FontRules` (thêm `uv-abc` và cơ chế ghi đè theo nội dung tệp), `Scanner` và `FontReport` đọc header của SHX tìm thấy trên máy hoặc trong kho rồi ghi đè bảng mã (`shxKind` có trong JSON). Trên bản sao bản vẽ thật: `VN_UNI`, `uv-abc` là `unifont` (Unicode); `vn-abc`, `vntime`, `vnsimple` là `shapes` (TCVN3); `vn1` là `bigfont`.

## Cổng cho Kuro

Kiến trúc: Kuro, máy chủ MCP `pkttc_mcp.py` (Python, không thư viện ngoài), named pipe cục bộ, vòng lặp trong lệnh `PKTEXTBRIDGE` chạy trên luồng chính của AutoCAD, các thao tác dùng chung `Ops` với lệnh gõ tay.

Mô hình an toàn:
- Cổng chỉ mở khi anh gõ `PKTEXTBRIDGE` và `YES`; đóng khi Kuro `shutdown`, tạo tệp `.stop`, hoặc sau 30 phút không dùng.
- Pipe chỉ cho đúng người dùng hiện tại; kết nối qua mạng bị cấm. DACL thật đọc từ pipe: `D:(D;;...;;;NU)(A;;...;;;<SID của anh>)`.
- Đọc (ping, scan, fonts, plan, fontsub.plan, purge.plan) không sửa bản vẽ.
- Ghi (plan.apply, fontsub.apply, purge.apply) luôn hỏi anh gõ `YES` trong AutoCAD, từng lần một. Kuro chỉ gửi `planId`; kế hoạch nằm trong bộ nhớ AutoCAD, dùng một lần.
- Ghi vẫn có sao lưu trước, một giao dịch (`U` một bước), nhật ký; mọi yêu cầu vào `audit.log`.
- Yêu cầu lớn hơn 4 MB, JSON hỏng, phương thức lạ, tham số có ký tự cấm đều bị từ chối mà cổng vẫn chạy.

Công cụ MCP: `pkttc_ping`, `pkttc_scan`, `pkttc_fonts`, `pkttc_plan_create`, `pkttc_plan_get`, `pkttc_plan_apply`, `pkttc_fontsub_plan`, `pkttc_fontsub_apply`, `pkttc_purge_plan`, `pkttc_purge_apply`, `pkttc_shutdown` (11). Hướng dẫn cho Kuro: `HUONG_DAN_KURO.md`; cấu hình mẫu: `kuro_mcp_config.json`.

## Kiểm thử

| Bộ | Kết quả |
|---|---|
| `run_tests_bridge.ps1` (accoreconsole + client + MCP, người dùng trả lời bằng dòng script) | 47/47 |
| `run_tests_apply.ps1` (hồi quy sau khi tách `Ops`) | 27/27 |
| `run_tests.ps1` (font, thêm kiểm header SHX) | 26/26 |
| Core (`texthub_s1`) | 134/134 |
| `PlanTests` | 9/9 |

Cổng (47): ping, scan phân trang, fonts; lập kế hoạch không đổi bản vẽ; tham số cấm (`-32602`), mã kế hoạch lạ hoặc dạng đường dẫn (`-32004`), phương thức lạ (`-32601`); người dùng `no` thì `rejected` và bản vẽ không đổi; `YES` thì `applied` 11 mục, có tệp sao lưu, Unicode 14, style `Arial_2`, kế hoạch dùng một lần, lập lại ra 0 mục; dọn style bị từ chối; JSON hỏng (`-32700`), 5 MB bị từ chối, cổng vẫn chạy; DACL; MCP (`initialize`, `tools/list` 11 công cụ, `plan_apply` chỉ nhận `planId` và `note`, tham số lạ bị bỏ, công cụ lạ và mã lạ là `isError` mà không hỏi người dùng); `audit.log` ghi tên máy khách, từ chối, đồng ý; `shutdown` đóng pipe, xóa tệp phát hiện; tệp mẫu trên đĩa không đổi.

## Giới hạn

- Chưa thử trong AutoCAD giao diện đầy đủ. Vòng lặp chặn lệnh nên trong lúc cổng mở anh không gõ lệnh khác được; có gọi `DoEvents` để cửa sổ không treo, nhưng chưa kiểm tra trên giao diện thật. Nếu bất tiện, bước kế là chế độ không chặn (sự kiện `Idle`, hộp thoại xác nhận) trong khi vẫn giữ quy tắc YES.
- Phê duyệt bằng dòng lệnh: người gõ YES phải ngồi ở AutoCAD. Tiến trình khác cùng người dùng có thể giả lập bàn phím; đây là giới hạn chung của mô hình cùng tài khoản.
- Chưa có ký xác thực giữa máy khách và cổng (dựa vào ACL của người dùng).
- Kuro là giả thiết: giả định Kuro nói MCP qua stdio. Nếu Kuro nối kiểu khác, `pkttc_client.py` dùng được trực tiếp (JSON mỗi dòng qua pipe).
- Bản S2 cũ vẫn trong phiên AutoCAD đang mở; khởi động lại AutoCAD trước khi nạp bản này.

## Tệp

- Mới: `src/Db/Ops.cs`, `Bridge.cs`, `ShxHeader.cs`; lệnh `PKTEXTBRIDGE` trong `Commands.cs`.
- Python: `bridge/pkttc_client.py`, `bridge/pkttc_mcp.py`.
- Thử: `tests/bridge_test.py`, `run_tests_bridge.ps1`.
- Tài liệu: `HUONG_DAN_KURO.md`, `kuro_mcp_config.json`.


## Cập nhật 2026-11-21: chế độ không chặn

`PKTEXTBRIDGE` tự chọn chế độ: trong AutoCAD giao diện là **idle** (không chặn); trong `accoreconsole` hoặc khi `PKTTC_BRIDGE_MODE=loop` là **loop** (chặn, như trước).

Chế độ idle:
- Xử lý yêu cầu trong `Application.Idle` khi AutoCAD rảnh (dòng lệnh trống); luồng pipe đánh thức vòng lặp thông điệp bằng `WM_NULL` nên trả lời gần như tức thời (ping đo được 0,03 s).
- Việc ghi xin phép bằng hộp thoại Yes/No (mặc định No) nêu tên trợ lý, mã kế hoạch, số mục, ghi chú, 5 mục mẫu. Sau khi anh bấm Yes, việc ghi chạy trong một lệnh AutoCAD thật `PKTEXTBRIDGEEXEC` (gửi bằng `SendStringToExecute`) nên là một bước `U`; quá 30 giây mà lệnh không chạy thì trả lỗi và bản vẽ không đổi.
- Việc đọc chạy ngay khi rảnh, không hỏi. Cổng không nhận yêu cầu mới trong lúc hộp thoại đang mở (từng yêu cầu một).
- `PKTEXTBRIDGESTOP` đóng cổng; `shutdown` của Kuro, tệp `.stop`, hoặc 30 phút không dùng cũng đóng. AutoCAD không bị thoát.
- Quy tắc an toàn giữ nguyên: Kuro chỉ gửi `planId`, ACL pipe, sao lưu, nhật ký, `audit.log`.

Kiểm thử trên một phiên AutoCAD giao diện riêng (acad.exe thứ hai trên bản sao mẫu; phiên làm việc của anh không bị đụng, vẫn chạy nguyên), hộp thoại được bấm bằng Win32 như người dùng:
- `run_tests_idle.ps1`: 24/24 điều kiện đạt. Gồm: lệnh `PKTEXTSCAN` trong script chạy ngay sau `PKTEXTBRIDGE` (chứng minh không chặn); ping, scan, lập kế hoạch khi rảnh; hộp thoại hiện đủ tên trợ lý, mã kế hoạch, 11 mục, ghi chú; bấm No thì `rejected` và bản vẽ không đổi; bấm Yes thì `applied` 11 mục, 0 lỗi, ghi trong lệnh `PKTEXTBRIDGEEXEC`, có sao lưu, Unicode 14; lập lại ra 0 mục; dọn style bị từ chối; cổng sống sau các hộp thoại; ACL; `audit.log` ghi TỪ CHỐI và ĐỒNG Ý; `shutdown` đóng pipe và xóa tệp phát hiện mà AutoCAD vẫn chạy; tệp mẫu trên đĩa không đổi.
- Chế độ chặn hồi quy: `run_tests_bridge.ps1` vẫn 47/47.

Chưa kiểm: `PKTEXTBRIDGESTOP` gõ tay (không gõ được vào phiên thử), hành vi khi anh đang chạy một lệnh dài (cổng chờ đến khi AutoCAD rảnh), nhiều bản vẽ mở cùng lúc (cổng gắn với bản vẽ đang hoạt động lúc mở), nhấn Esc/đóng hộp thoại bằng nút X (được coi là từ chối).
