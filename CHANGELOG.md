# Nhật ký phiên bản Kuro OS

## [1.5.8] - 2026-11-12
- Kích hoạt tính năng xem trước trực tiếp toàn bộ các tệp và tài nguyên trong Panel Ngữ cảnh:
  - Tệp bộ nhớ (Memory files): Nhấp chuột trực tiếp vào bất kỳ tệp bộ nhớ nào (`CLAUDE.md`, `AGENTS.md`, `MEMORY.md`, `KE-HOACH.md`...) để mở ngay hộp thoại Modal xem trước nội dung tài liệu định dạng Markdown hoàn chỉnh.
  - Kỹ năng chuyên môn (Skills): Nhấp chuột vào từng kỹ năng để mở tệp hướng dẫn nghiệp vụ chuẩn (`SKILL.md`).
  - Tác nhân AI (Agents): Nhấp chuột vào từng kỹ sư chuyên môn để xem nhanh tệp định nghĩa vai trò và persona (`agents/*.md`).
  - Kết quả đầu ra (Artifacts): Nhấp chuột để xem trước tệp văn bản hoặc thẻ thông tin mở tệp bằng phần mềm chuyên dụng (Excel, Word, AutoCAD, PDF...).
- Mở rộng phạm vi tìm nạp tệp tin an toàn (`resolve_fs_target`): Cho phép API `/api/fs/file`, `/api/fs/open`, `/api/fs/reveal` truy xuất liền mạch cả thư mục dự án (workspace), thư mục gốc hệ thống (ROOT) và kho tri thức bộ não (BRAIN).

## [1.5.7] - 2026-11-12
- Nâng cấp Panel Ngữ cảnh (Context Breakdown) chuẩn phong cách Claude Code: Chuyển đổi các mục đếm tĩnh thành danh mục Accordion (thu gọn/mở rộng `▸` / `▾`) kèm badge số lượng thực tế.
- Bóc tách chi tiết từng thành phần ngữ cảnh:
  - Công cụ MCP & Hệ thống (MCP & System Tools): Hiển thị chi tiết từng công cụ (`kuro · tinh_python`, `system · Read`, `system · Write`, `system · Edit`, `system · Glob`, `system · Grep`, `system · Bash`, `system · WebSearch`, `system · WebFetch`...) kèm số token thực tế của từng công cụ.
  - Tệp bộ nhớ (Memory files): Quét và hiển thị chi tiết từng tệp bộ nhớ (`CLAUDE.md`, `AGENTS.md`, `MEMORY.md`, `KE-HOACH.md`...) kèm số token thực tế và hỗ trợ nhấp chuột để xem trước nhanh tệp tin.
  - Năng lực chuyên môn (Skills): Liệt kê đầy đủ 22 kỹ năng chuyên môn hạ tầng (Biện pháp thi công, BIM tự động hoá, Kiểm toán hố móng...) kèm số token thực tế từ nội dung SKILL.md.
  - Tác nhân tùy chỉnh (Agents): Liệt kê chi tiết 13 kỹ sư AI chuyên môn kèm số token persona thực tế.
- Khắc phục triệt để việc hardcode số liệu thống kê: Mọi bộ đếm, biểu đồ phân bổ token (Progress Bar) và tỷ lệ sử dụng ngữ cảnh đều được tính toán tự động và đồng bộ thời gian thực theo đúng phiên làm việc hiện tại.

## [1.5.6] - 2026-11-12
- Tối ưu giao diện thanh công cụ Cây thư mục: Ẩn các nút Tạo tệp và Tạo thư mục trên thanh tiêu đề để giao diện gọn gàng, thoáng mắt. Các thao tác Tạo tệp mới, Tạo thư mục mới, Đổi tên, Xóa, Sao chép, Dán vẫn được giữ nguyên đầy đủ trong Menu chuột phải (Context Menu).

## [1.5.5] - 2026-11-12
- Tìm kiếm đệ quy toàn bộ cây thư mục dự án (Recursive File Search): Nâng cấp ô tìm kiếm trong tab Cây thư mục để quét sâu vào mọi thư mục con, hiển thị danh sách kết quả trực quan kèm đường dẫn chi tiết và đánh dấu từ khóa khớp.
- Mở tệp tin bằng phần mềm chuyên dụng trên Windows: Double-click vào bất kỳ tệp tin nào (hoặc bấm nút "Mở trên Windows") để tự động khởi chạy bằng phần mềm mặc định trên máy tính (Microsoft Excel cho .xlsx, Word cho .docx, AutoCAD cho .dwg/.dxf, Adobe Acrobat cho .pdf...).
- Thẻ thông tin tệp chuyên dụng (Binary File Card): Khắc phục triệt để hiện tượng hiển thị ký tự mã nhị phân khi xem trước tệp Excel/Word/CAD. Thay thế bằng giao diện thẻ đẹp mắt kèm nút mở trực tiếp và mở thư mục trong Explorer.
- Bộ công cụ quản lý tệp tin chuẩn Windows ngay trên giao diện: Hỗ trợ tạo tệp mới, tạo thư mục mới, sao chép (Copy), dán (Paste), đổi tên (Rename - F2), xóa tệp/thư mục (Delete) qua cả Menu chuột phải (Context Menu) và thanh công cụ tiện ích.

## [1.5.4] - 2026-11-12
- Thanh vạch điều hướng câu hỏi (Message Ticks Rail): Hiển thị các vạch tick trên mép phải thanh cuộn đánh dấu câu hỏi của người dùng. Rê chuột vào sẽ hiện popover danh sách 15 câu hỏi xung quanh vị trí xem, bấm vào để cuộn nhanh và nháy sáng câu hỏi (theo phong cách Javis OS).
- Nút cuộn nhanh xuống cuối (Scroll to Bottom): Tự động hiển thị nút tròn khi người dùng cuộn lên xem lịch sử trao đổi, bấm vào để lướt ngay xuống tin nhắn mới nhất.
- Chọn Model AI riêng biệt cho từng cuộc hội thoại (Per-Session Model): Cho phép đổi model độc lập cho từng phiên chat mà không làm ảnh hưởng đến các phiên chat khác hay cấu hình chung toàn cục.
- Dán ảnh trực tiếp từ bộ nhớ tạm (Clipboard Image Paste): Hỗ trợ nhấn Ctrl+V khi vừa chụp ảnh màn hình (Snipping Tool, Win+Shift+S) hoặc kéo thả ảnh vào khung chat. Tự động lưu an toàn vào thư mục `.attachments/` của dự án, hiển thị thumbnail xem trước và đính kèm đường dẫn cho AI phân tích.

## [1.5.3] - 2026-11-12
- Bổ sung tính năng sao chép và dán (copy/paste) file vào khung chat chuẩn phong cách Claude Code: Khi copy file trong Windows Explorer (Ctrl+C), nhấn Ctrl+V vào khung chat sẽ tự động điền đường dẫn tuyệt đối của file (tự động bao nháy kép nếu tên file có khoảng trắng).
- Hỗ trợ copy cùng lúc nhiều file và kéo thả (drag & drop) file từ Windows Explorer vào khung chat.
- Tích hợp cầu nối đọc Clipboard Windows (CF_HDROP) qua DesktopApi và API nội bộ `/api/clipboard/files`.

## [1.5.2] - 2026-11-12
- Chuẩn hóa luồng khởi động lại sau khi cập nhật: Luôn tự động mở lại ứng dụng Desktop native (`app_desktop.py`), khắc phục triệt để việc mở nhầm sang trình duyệt web (`127.0.0.1:7788`).
- Cập nhật kuro.vbs và cap-nhat.bat ưu tiên chạy ứng dụng Desktop native qua `pythonw.exe`.

## [1.5.1] - 2026-11-12
- Tích hợp Agent Xác nhận thanh quyết toán thầu phụ và đội thi công (nhóm Quản lý & Hồ sơ).
- Bổ sung công cụ kiểm tra sản phẩm đầu ra `tools/kiem_tra_san_pham.py`.
- Tối ưu biểu tượng giao diện và bộ 3 câu hỏi gợi ý nhanh (Quick Prompts) chuyên môn thanh quyết toán trên Dashboard.
- Nâng cấp cơ chế thông báo cập nhật, tự động hiển thị mô tả phiên bản từ GitHub.

## [1.5.0] - 2026-11-11
- Nâng cấp nhận diện logo và biểu tượng ứng dụng chuẩn trên Taskbar và Desktop.
- Cải tiến cây thư mục và danh sách dự án gần đây.
- Bổ sung Agent Kiểm toán hố móng mố trụ cầu và cống thoát nước.
