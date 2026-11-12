# Nhật ký phiên bản Kuro OS

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
