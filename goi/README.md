# Gói tiện ích tùy chọn

Mỗi thư mục con là một gói (`goi.json` + skill + script). Gói đi cùng mã nguồn Kuro nhưng **không vào brain** cho tới khi
người dùng yêu cầu cài.

- Trong giao diện Kuro: mở **Cài đặt -> Plugins** để xem danh sách plugin tích hợp sẵn, cài/gỡ trên máy hoặc cài thêm từ gói plugin bên ngoài (`.zip` / `.kuro-plugin` / thư mục).
- Trong khung chat Kuro: nói "cài gói AutoCAD" hoặc "cài gói TextHub" (AI gọi tool `goi_tien_ich`). "Gỡ gói ..." để gỡ.
- Dòng lệnh: `.venv\Scripts\python server\goi.py list | cai autocad | go autocad`
- Cài = chép skill vào `brains/<brain>/.claude/skills/` và `pip install` thư viện còn thiếu (cần mạng nếu thiếu).
  Sau đó bản cài tự cập nhật theo mã nguồn mỗi lần Kuro khởi động.
- Skill chỉ được mở khi việc liên quan: mô tả trong `SKILL.md` nói rõ khi nào dùng.

## Thêm gói mới
`goi/<id>/goi.json` (`ten`, `mo_ta`, `skill`, `pip`, `import`, tùy chọn `phien_ban`, `kiem_tra`) và thư mục `goi/<id>/<skill>/SKILL.md`; tên thư mục
skill phải trùng giá trị `skill` trong `goi.json`. Nếu gói có cài đặt phần mềm riêng trên máy (như plugin AutoCAD), khai thêm `"kiem_tra": "scripts/<script>.py status"` để giao diện Plugins hiển thị trạng thái trên máy và nút Cài/Cập nhật/Gỡ.

## Gói hiện có
- `autocad`: vẽ và xuất DXF theo chuẩn PKTTC (chữ Unicode, cỡ chữ, layer và nét in, dim) + script kiểm DXF.
  Điểm chưa chốt cần anh Nghĩa xác nhận: `autocad-pkttc/references/quy-chuan.md`, mục 5.
- `librecad`: tích hợp LibreCAD (CAD 2D, GPLv2): cài/gỡ bằng winget từ Cài đặt > Plugins (không kèm mã LibreCAD), skill `librecad-cad` đổi DXF/DWG sang PDF/PNG/SVG và mở bản vẽ qua dòng lệnh LibreCAD. Cú pháp CLI cần xác minh trên bản đã cài.
- `pdfcraft` (PdfCraft, PDF), `cadcraft` (CADCraft, DXF/DWG), `solidcraft` (SolidCraft, CAD 3D tham số): tải bản portable x64 ĐÃ GHIM phiên bản từ GitHub Release, kiểm SHA-256 theo `SHA256SUMS.txt` của release (chữ ký `.asc` không được kiểm), cài vào `%LOCALAPPDATA%\Programs\<Tên>` không cần admin, tải chạy nền (trạng thái `dang_cai`, bấm "Làm mới"). Kèm MCP qua `mcp_chay.py`. Mã cài dùng chung ở `goi/_chung/cai_phan_mem.py` (đổi phiên bản: sửa `tag` trong `<app>_setup.py` và `mcp_chay.py`). Cả ba Apache-2.0/MIT.
- `chili3d`: cầu nối MCP `@chili3d/mcp` (npm, ghim 0.1.0, cần Node 20+) cài ở `state/chili3d-mcp`; trang Chili3D (AGPL-3.0) mở từ chili3d.com, Kuro không kèm mã.
- `cli-hub`: cài gói pip `cli-anything-hub` (ghim 0.4.1) vào Python của Kuro, kèm skill dặn hỏi người dùng từng lần trước khi `cli-hub install <CLI>`. Không có MCP. Skill của ~70 CLI dựng sẵn và quy trình dựng CLI mới nằm ở kho skill `kho/cli-anything` (ghim `34f5195`, Apache-2.0).
- Gói có khối `mcp` có thêm hàng "MCP" trong Cài đặt > Plugins với nút Cài MCP / Gỡ MCP (ghi/xóa riêng khối đó trong `state/mcp.json`, không đụng skill; không ghi đè mục MCP cùng tên mà bạn đã tự khai báo khác). Có hiệu lực cho phiên chat mới.
- Phát hiện phần mềm đã cài: thư mục của Kuro, rồi `Program Files\<Tên>`, rồi PATH; phiên bản lấy từ registry Uninstall. Bản cài tay (MSI) được nhận là "Đã cài", không ép cập nhật; gỡ bản đó làm trong Cài đặt Windows.
- Chuỗi `${KURO_ROOT}` và `${KURO_PYTHON}` trong khối `mcp` của `goi.json` được thay bằng đường dẫn thật lúc cài gói (cần khởi động lại Kuro để `server/goi.py` mới có hiệu lực; gói đã bật trước đó thì Tắt rồi Bật lại).
- `texthub`: Convert Font to Unicode - Đổi chữ TCVN3/VNI sang Unicode trong AutoCAD (PKTTC TextHub v0.9.3), kèm plugin AutoCAD (`PKTTC.TextHub.bundle`), kho 361 font SHX/TTF, skill `texthub-cad` và công cụ `texthub_setup.py`.
