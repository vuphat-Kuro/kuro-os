# Nguyên tắc dự án Kuro OS

## Nguyên tắc cốt lõi

### I. Số liệu kỹ thuật có nguồn, không tự nhẩm
Mọi con số trong câu trả lời của Kuro phải tính bằng script (tool `tinh_python` hoặc script chạy bằng shell),
có đơn vị, kiểm tra chéo bằng cách thứ hai, có nguồn (TCVN/QCVN, bản vẽ, thí nghiệm). Bộ não nào không chạy được
script thì phải ghi rõ "(chưa kiểm bằng script)". Không bịa số hiệu điều khoản.

### II. Đo, không đoán
Cờ dòng lệnh, định dạng sự kiện, địa chỉ máy chủ, tên model của mọi hãng AI phải được đo trên chương trình thật
(ghi phiên bản và ngày đo trong chú thích mã). Danh sách model lấy từ chính CLI hoặc hãng, không chép tay.

### III. Lỗi phải hiện ra, và chặn trước được thì chặn trước
Không có "bong bóng trả lời rỗng": mọi lỗi có lý do bằng tiếng Việt trên giao diện. Cấu hình sai rõ ràng
(ví dụ model không thuộc AI đang chọn) phải bị chặn hoặc tự sửa trước khi gửi, không để người dùng gặp lỗi lúc chat.

### IV. An toàn mặc định
Chỉ nghe 127.0.0.1; kiểm `Host` và `Origin` cho mọi route nhạy cảm; `Bash` tắt mặc định; key chỉ trả về dạng
che; không nạp cấu hình cá nhân của Claude Code hay Codex; không đụng `.env`, `state/`, `brains/` khi cập nhật.

### V. Ít mã nhất, có kiểm tra
Giải pháp nhỏ nhất làm xong việc. Logic mới không tầm thường phải có bài kiểm tra trong `tests/test_core.py`.
Không thêm tính năng, tùy chọn hay thư viện chưa ai yêu cầu.

## Ràng buộc

- Windows 10/11 là nền tảng chính. Python 3.13 trong `.venv`, FastAPI, JavaScript thuần, không bước build.
- Người dùng cuối không rành máy tính: giao diện và thông báo bằng tiếng Việt, cài bằng bấm đúp, có biểu tượng.
- File `.bat` sửa bằng công cụ Edit/Write, không bằng lệnh Git Bash (bẫy `>nul` thành `>/dev/null`).
- Phát hành qua GitHub `vuphat-Kuro/kuro-os`; người dùng cập nhật bằng `cap-nhat.bat`.

## Quy trình làm việc

- Thử thật trên máy (giao diện và lượt chat thật) trước khi báo xong; chạy toàn bộ `tests/`.
- Mỗi lần phát hành: tăng `VERSION`, dòng tiêu đề commit bằng tiếng Việt (người dùng thấy trong thanh báo bản mới).
- Thay đổi lớn đi theo Spec Kit: đặc tả, kế hoạch, danh sách việc, rồi mới làm.

## Quản trị

Bộ nguyên tắc này đứng trên các thói quen khác của dự án. Sửa nguyên tắc thì tăng phiên bản (MAJOR: bỏ hoặc
định nghĩa lại nguyên tắc; MINOR: thêm nguyên tắc; PATCH: sửa câu chữ) và ghi ngày sửa.

**Phiên bản**: 1.0.0 | **Thông qua**: 2026-11-03 | **Sửa lần cuối**: 2026-11-03
