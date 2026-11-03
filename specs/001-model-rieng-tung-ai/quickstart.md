# Thử nhanh: Mỗi AI nhớ model riêng

Điều kiện: Kuro đang chạy ở http://127.0.0.1:7788, máy có Claude Code và `agy` đã đăng nhập.

1. **Chạy bài kiểm tra tự động**: `.venv\Scripts\python -m unittest discover -s tests`, kỳ vọng tất cả OK.
2. **Lỗi gốc (Câu chuyện 1)**: Cài đặt, chọn Antigravity, model `gemini-3.8-flash-medium`, Lưu. Chọn Tài khoản Claude, bấm
   "Lưu và kiểm tra kết nối": ô Model trống (hoặc model Claude đã lưu), kết nối được. Chọn lại Antigravity: ô Model
   hiện `gemini-3.8-flash-medium`.
3. **Ô chọn nhanh (Câu chuyện 2)**: với Claude thấy Mặc định, Sonnet, Opus, Haiku; chọn Opus, hỏi "bạn là model nào".
   Với Antigravity thấy danh sách tài khoản. Với ChatGPT không thấy ô chọn.
4. **Chặn tên sai (Câu chuyện 3)**: chọn Claude, gõ `gemini-3.8-flash-medium`, Lưu: bị từ chối, có danh sách tên đúng.
5. **Đổi AI giữa phiên (Câu chuyện 4)**: hỏi một câu bằng Claude, đổi sang Antigravity, hỏi tiếp cùng phiên: thấy dòng
   "AI mới chưa biết các câu trước trong phiên này". Đổi model trong cùng AI: không thấy dòng này.
6. **Máy cũ (FR-008)**: đặt `KURO_PROVIDER=claude`, `KURO_MODEL=gemini-3.8-flash-medium` trong `.env`, khởi động lại:
   Kuro chạy, `KURO_MODEL` thành rỗng, Claude dùng mặc định.
