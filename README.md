# Kuro - Trợ lý AI cho kỹ sư hạ tầng

Kuro chạy trên máy của bạn và trả lời tiếng Việt. Giao diện là trang web nội bộ, kết nối Telegram nếu muốn. Kuro nhớ thông tin dự án, dùng bộ skill ngành (biện pháp thi công, QS, QC, tiến độ, BIM, an toàn) và tính toán bằng script có lưu lại.

## Cài lần đầu (khoảng 10 phút)

**Cần có:**
- Windows 10 hoặc 11.
- [Git](https://git-scm.com/download/win).
- [Python 3.13](https://www.python.org/downloads/): lúc cài nhớ tích "Add python.exe to PATH".
- [Node.js](https://nodejs.org) và Claude Code: mở cửa sổ lệnh rồi gõ `npm install -g @anthropic-ai/claude-code`. Claude Code là phần chạy nền **miễn phí**, không cần tài khoản Claude.
- **Một AI để Kuro dùng**, chọn một trong các loại sau:
  - Tài khoản Claude (gói Pro/Max)
  - Anthropic API key
  - [OpenRouter](https://openrouter.ai): một key dùng được GPT, Gemini, Claude...
  - DeepSeek
  - GLM (Z.ai)
  - Kimi
  - [Ollama](https://ollama.com): chạy trên máy, miễn phí, không cần mạng
- Lời mời vào repo này: repo riêng tư, nhờ người quản lý thêm tài khoản GitHub của bạn.

**Các bước:**

1. Mở cửa sổ lệnh ở thư mục muốn đặt Kuro, rồi gõ:
   ```bat
   git clone https://github.com/vuphat-Kuro/kuro-os.git Kuro
   ```
   Lần đầu, cửa sổ đăng nhập GitHub sẽ hiện ra. Đăng nhập bằng tài khoản đã được mời.
2. Vào thư mục `Kuro`, bấm đúp `setup.bat`.
3. Nếu chọn tài khoản Claude: mở PowerShell, gõ `claude auth login` và đăng nhập. Dùng AI khác thì bỏ qua bước này.
4. Bấm đúp `run.bat`. Trình duyệt tự mở http://127.0.0.1:7788.
5. Lần đầu mở, Kuro hiện màn hình **Chọn AI cho Kuro**:
   - Chọn AI, dán key, điền tên model nếu hãng yêu cầu.
   - Bấm **Lưu và kiểm tra kết nối**.
   - Thấy dòng chữ xanh "Kết nối được" là dùng được.
   - Đổi AI lúc nào cũng được ở **⚙ Cài đặt**.

## Cập nhật

Khi có bản mới, Kuro hiện thông báo màu cam trên giao diện, kèm danh sách thay đổi. Nếu bạn đã bật Telegram, Kuro nhắn thêm qua Telegram. Cách cập nhật:

1. Tắt cửa sổ Kuro đang chạy.
2. Bấm đúp `cap-nhat.bat`.
3. Bấm đúp `run.bat`.

Cập nhật **không** đụng tới key (`.env`), lịch sử chat (`state/`) hay ký ức của bạn (`brains/`).

Skill và agent đi kèm cũng được cập nhật theo. Riêng skill bạn đã tự sửa thì Kuro giữ nguyên bản của bạn, và cửa sổ Kuro sẽ ghi dòng `[goi-kem] giữ bản bạn đã sửa: ...`. Muốn nhận bản mới thì xoá thư mục skill đó trong `brains/Brain Default/.claude/skills/`, rồi khởi động lại Kuro.

## Lưu ý

- Mỗi người dùng một máy, một tài khoản AI hoặc key riêng.
- Với AI khác Claude, chất lượng dùng công cụ (đọc file, tính toán, gọi skill) tuỳ model. Nên chọn model mạnh của hãng. Kuro chỉ mở ở `127.0.0.1`, máy khác trong mạng không vào được.
- Câu trả lời của Kuro là bản nháp hỗ trợ. Hồ sơ chính thức phải được người có chứng chỉ hành nghề kiểm tra và ký.
- Tài liệu kỹ thuật chi tiết: [KE-HOACH.md](KE-HOACH.md).

## Nguồn skill và giấy phép

| Skill | Nguồn | Giấy phép |
|---|---|---|
| `pm-hse`, `pm-investigate`, `pm-report`, `pm-rfi`, `pm-risk` | [claude-civil-pm-skills](https://github.com/ChineduNlem/claude-civil-pm-skills) | MIT (file `LICENSE` trong từng thư mục) |
| `constructability-risk-review`, `lookahead-constraint-sweep`, `productivity-assumption-stress-test`, `load-path-sanity-check` | [constructelligence-lab/construction-agent-skills](https://github.com/constructelligence-lab/construction-agent-skills) | CC BY 4.0 |
| Các skill còn lại và các agent | Tác giả Kuro | Dùng nội bộ |
