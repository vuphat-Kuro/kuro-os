# Nghiên cứu: Mỗi AI nhớ model riêng

## 1. Lưu model theo AI ở đâu

- **Quyết định**: mỗi AI một khóa trong `.env`: `KURO_MODEL_<ID viết hoa>` (vd `KURO_MODEL_CLAUDE`, `KURO_MODEL_ANTIGRAVITY`).
- **Lý do**: `.env` đã là nơi lưu cấu hình, `save_env` đã giữ chú thích và thứ tự; không thêm tệp hay bảng mới.
- **Đã cân nhắc**: một khóa JSON `KURO_MODELS={...}` (khó đọc tay, regex phức tạp); bảng SQLite (cấu hình nằm hai nơi).

## 2. Giữ tương thích nơi gọi

- **Quyết định**: `config.MODEL` = giá trị khóa của AI đang chọn (AI trống coi là `claude`). API vẫn nhận `KURO_MODEL`.
- **Lý do**: 6 chỗ đọc `config.MODEL` (Claude Code, codex, agy, ping, /api/models) đúng ngay, không phải sửa; giao diện cũ vẫn gửi được.
- **Đã cân nhắc**: đổi mọi nơi gọi sang hàm `model_for(provider)` (nhiều diff hơn, cùng kết quả).

## 3. Danh sách model hợp lệ

- **Quyết định**: Claude: `""`, `sonnet`, `opus`, `haiku`, và mọi tên bắt đầu `claude-`. Antigravity: kết quả `agy models` (đã nhớ tạm). AI khác: không có danh sách, không chặn.
- **Lý do**: bí danh sonnet/opus/haiku đã dùng thật từ bản 1.0; tên `claude-...` đầy đủ cần cho người muốn model cụ thể. Không chép tay danh sách Gemini (nguyên tắc II).
- **Đã cân nhắc**: hỏi máy chủ Anthropic danh sách model (cần API key, tài khoản gói không có).

## 4. Gợi ý khi tên sai

- **Quyết định**: `difflib.get_close_matches` của thư viện chuẩn, tối đa 3 tên; kèm toàn bộ danh sách nếu ngắn (Claude).
- **Lý do**: có sẵn trong Python, không thêm phụ thuộc.

## 5. Chuyển đổi máy cài bản cũ

- **Quyết định**: lúc khởi động, nếu còn `KURO_MODEL` khác rỗng: model hợp lệ với AI đang chọn (theo quy tắc mục 3, riêng Antigravity coi là hợp lệ vì chưa lấy được danh sách lúc khởi động) thì chép sang khóa của AI đó; rồi xoá trắng `KURO_MODEL`. Chạy một lần, sau đó `KURO_MODEL` rỗng nên không chạy lại.
- **Lý do**: đúng ca lỗi của người dùng (Claude + tên Gemini) bị bỏ; ca hợp lệ được giữ.

## 6. Biết khi nào báo "AI mới chưa biết các câu trước"

- **Quyết định**: mã hội thoại lưu dạng `<id AI>:<mã>` cho mọi AI (hiện chỉ codex/agy có tiền tố, Claude Code thì trần). Mã trần cũ coi là của `claude`. Tiền tố khác AI đang chọn: không nối tiếp, phát dòng báo trước câu trả lời.
- **Lý do**: không đổi lược đồ SQLite; cũng sửa lỗi ẩn: Claude và DeepSeek đều đi qua Claude Code nên trước đây dùng chung mã trần, đổi giữa chúng sẽ nối nhầm hội thoại.
- **Đã cân nhắc**: thêm cột `provider` vào bảng phiên (phải chuyển đổi lược đồ).

## 7. Dịch lỗi model của hãng không có danh sách

- **Quyết định**: lỗi chứa dấu hiệu model không tồn tại (đo thật: "issue with the selected model", "may not exist", "model_not_found", "not found" kèm "model") được đổi thành: "Model `<tên>` không có ở <tên AI>. <gợi ý tra tên của AI đó>." kèm nguyên văn lỗi gốc.
- **Lý do**: FR-006; giữ nguyên văn để không mất thông tin gỡ lỗi.
