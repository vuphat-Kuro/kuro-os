# Đặc tả tính năng: Mỗi AI nhớ model riêng

**Nhánh**: `001-model-rieng-tung-ai`

**Ngày tạo**: 2026-11-03

**Trạng thái**: Đã làm (bản 1.4.0)

**Đầu vào**: Lỗi người dùng gặp: chọn model `gemini-3.8-flash-medium` khi dùng Antigravity, rồi chuyển sang "Tài khoản Claude" thì model Gemini bị mang theo, Kuro báo "There's an issue with the selected model" khi kiểm tra kết nối.

## Kịch bản sử dụng và kiểm tra *(bắt buộc)*

### Câu chuyện 1 - Chuyển AI không mang model sai theo (Ưu tiên: P1)

Kỹ sư đang dùng Antigravity với model Gemini 3.8 Flash, mở Cài đặt chuyển sang Tài khoản Claude rồi bấm "Lưu và kiểm tra kết nối". Kuro dùng model của Claude (hoặc mặc định của Claude), kết nối thành công. Khi quay lại Antigravity, model Gemini 3.8 Flash vẫn còn nguyên.

**Vì sao ưu tiên này**: Đây chính là lỗi người dùng đang gặp; không sửa thì mọi lần đổi AI đều có nguy cơ hỏng.

**Kiểm tra độc lập**: Chọn model ở AI A, chuyển sang AI B, kiểm tra kết nối thành công; chuyển về AI A, model cũ còn đó.

**Kịch bản chấp nhận**:

1. **Cho** Antigravity đang dùng model `gemini-3.8-flash-medium`, **khi** chuyển sang Tài khoản Claude và kiểm tra kết nối, **thì** kết nối thành công và ô Model hiện model của Claude (trống nếu chưa từng chọn).
2. **Cho** đã chọn Claude với model Sonnet, **khi** chuyển sang Antigravity rồi quay lại Claude, **thì** ô Model của Claude vẫn là Sonnet và của Antigravity vẫn là model đã chọn trước đó.
3. **Cho** một AI chưa từng được chọn model, **khi** chuyển sang AI đó, **thì** ô Model trống (dùng mặc định của AI đó).

---

### Câu chuyện 2 - Đổi model nhanh cho Antigravity và Claude (Ưu tiên: P2)

Trên thanh trên cùng, cạnh trạng thái "SẴN SÀNG", có ô chọn model cho AI đang dùng: Antigravity hiện đúng danh sách model tài khoản được dùng; Claude hiện Mặc định, Sonnet, Opus, Haiku. Đổi ở đây là có hiệu lực từ câu hỏi kế tiếp và chỉ đổi model của AI đang dùng.

**Vì sao ưu tiên này**: Người dùng muốn đổi model qua lại thường xuyên mà không mở Cài đặt.

**Kiểm tra độc lập**: Chọn Claude, đổi sang Opus ở thanh trên, hỏi một câu, AI trả lời bằng Opus; mở Cài đặt thấy ô Model của Claude là Opus.

**Kịch bản chấp nhận**:

1. **Cho** AI đang dùng là Claude, **khi** mở trang, **thì** ô chọn nhanh hiện 4 lựa chọn: Mặc định, Sonnet, Opus, Haiku.
2. **Cho** AI đang dùng là Antigravity, **khi** mở trang, **thì** ô chọn nhanh hiện danh sách model lấy từ tài khoản Antigravity trên máy.
3. **Cho** AI đang dùng là ChatGPT, DeepSeek hoặc AI khác không có danh sách, **khi** mở trang, **thì** không hiện ô chọn nhanh.

---

### Câu chuyện 3 - Chặn tên model sai ngay lúc lưu (Ưu tiên: P2)

Khi người dùng gõ hoặc dán tên model không thuộc AI đang chọn (ví dụ tên Gemini cho Claude), Kuro không cho lưu và gợi ý các tên đúng. Với AI không có danh sách model, Kuro cho lưu; nút kiểm tra kết nối báo lỗi bằng tiếng Việt kèm cách sửa.

**Vì sao ưu tiên này**: Theo nguyên tắc III, lỗi cấu hình rõ ràng phải chặn trước, không để gặp lúc chat.

**Kiểm tra độc lập**: Chọn Claude, gõ `gemini-3.8-flash-medium` vào ô Model, bấm Lưu: Kuro từ chối và liệt kê sonnet, opus, haiku.

**Kịch bản chấp nhận**:

1. **Cho** AI đang chọn là Claude, **khi** lưu model `gemini-3.8-flash-medium`, **thì** Kuro từ chối, giữ nguyên model cũ và hiện thông báo tiếng Việt kèm danh sách tên hợp lệ.
2. **Cho** AI đang chọn là Antigravity, **khi** lưu một tên không có trong danh sách của tài khoản, **thì** Kuro từ chối và gợi ý tên gần đúng nhất nếu có.
3. **Cho** AI đang chọn là DeepSeek, **khi** lưu một tên bất kỳ rồi kiểm tra kết nối mà hãng báo model không tồn tại, **thì** Kuro hiện lỗi tiếng Việt: model không có ở hãng này, kèm chỗ tra tên đúng.

---

### Câu chuyện 4 - Đổi AI giữa phiên chat có báo rõ (Ưu tiên: P3)

Đang chat dở một phiên bằng Antigravity rồi đổi sang Claude, người dùng vẫn ở phiên cũ và hỏi tiếp được. Trước câu trả lời đầu tiên của AI mới, Kuro hiện một dòng: "AI mới chưa biết các câu trước trong phiên này".

**Vì sao ưu tiên này**: Tránh người dùng tưởng AI mới nhớ ngữ cảnh rồi nhận câu trả lời lệch.

**Kiểm tra độc lập**: Hỏi một câu bằng AI A, đổi sang AI B, hỏi tiếp trong cùng phiên: thấy dòng thông báo và câu trả lời của AI B.

**Kịch bản chấp nhận**:

1. **Cho** phiên đã có câu trả lời của Antigravity, **khi** đổi sang Claude và hỏi tiếp, **thì** Kuro hiện dòng thông báo trước câu trả lời và chat tiếp bình thường.
2. **Cho** phiên đã có câu trả lời của Claude, **khi** đổi chỉ model (vẫn là Claude), **thì** không hiện thông báo và AI vẫn nhớ hội thoại.
3. **Cho** phiên mới chưa có câu nào, **khi** đổi AI rồi hỏi, **thì** không hiện thông báo.

---

### Trường hợp biên

- Máy đã cài bản cũ có một model chung: nếu model đó hợp lệ với AI đang dùng thì giữ cho AI đó; không hợp lệ hoặc không xác định được thì bỏ (dùng mặc định), không gây lỗi khi mở Kuro.
- Danh sách model của Antigravity không lấy được (mất mạng, chưa đăng nhập): không chặn lưu; ô chọn nhanh ẩn đi; nút kiểm tra kết nối báo lỗi rõ.
- Model đã lưu trước đây nay không còn trong danh sách của tài khoản (Google đổi tên): ô chọn nhanh vẫn hiện tên cũ để người dùng thấy và đổi; kiểm tra kết nối báo lỗi tiếng Việt.
- Tác vụ chạy nền (nhắc hẹn, Telegram) dùng đúng AI và model đang chọn tại thời điểm chạy.

## Yêu cầu *(bắt buộc)*

### Yêu cầu chức năng

- **FR-001**: Hệ thống PHẢI lưu model riêng cho từng AI và chỉ dùng model của AI đang chọn khi chat, kiểm tra kết nối, nhắc hẹn và Telegram.
- **FR-002**: Hệ thống PHẢI giữ nguyên model của mỗi AI khi người dùng chuyển qua lại giữa các AI.
- **FR-003**: Hệ thống PHẢI hiện ô chọn model nhanh trên thanh trên cùng khi AI đang dùng là Antigravity (danh sách từ tài khoản trên máy) hoặc Claude (Mặc định, Sonnet, Opus, Haiku), và ẩn với AI khác.
- **FR-004**: Đổi model ở ô chọn nhanh PHẢI chỉ đổi model của AI đang dùng và có hiệu lực từ câu hỏi kế tiếp.
- **FR-005**: Với AI có danh sách model, hệ thống PHẢI từ chối lưu tên không có trong danh sách, giữ model cũ và hiện thông báo tiếng Việt kèm tên hợp lệ.
- **FR-006**: Với AI không có danh sách model, hệ thống PHẢI cho lưu và khi kiểm tra kết nối thất bại vì model, PHẢI hiện lỗi tiếng Việt kèm chỗ tra tên đúng.
- **FR-007**: Khi người dùng hỏi tiếp trong phiên đã có câu trả lời của AI khác, hệ thống PHẢI hiện một dòng thông báo "AI mới chưa biết các câu trước trong phiên này" trước câu trả lời; đổi model trong cùng AI thì không hiện.
- **FR-008**: Khi khởi động trên máy có cấu hình model chung kiểu cũ, hệ thống PHẢI chuyển đổi theo quy tắc ở phần Trường hợp biên mà không cần người dùng làm gì và không làm mất cấu hình khác.

### Thực thể chính

- **AI (nhà cung cấp)**: một lựa chọn trong danh sách "Chọn AI" (Claude, Antigravity, ChatGPT, DeepSeek...); có thể có danh sách model hoặc không.
- **Model đã chọn của AI**: tên model người dùng chọn cho một AI cụ thể; trống nghĩa là dùng mặc định của AI đó.
- **Phiên chat**: chuỗi câu hỏi và trả lời; ghi nhớ AI nào đã trả lời gần nhất để biết khi nào cần thông báo đổi AI.

## Tiêu chí thành công *(bắt buộc)*

### Kết quả đo được

- **SC-001**: Chuyển qua lại giữa 3 AI bất kỳ 10 lần liên tiếp, 100% lần kiểm tra kết nối không còn lỗi do model của AI khác.
- **SC-002**: Đổi model của Antigravity hoặc Claude chỉ cần 1 lần bấm chọn, không mở Cài đặt.
- **SC-003**: 100% trường hợp lưu tên model sai cho Claude hoặc Antigravity bị chặn trước khi chat.
- **SC-004**: Máy đã cài bản cũ cập nhật lên bản mới mở được Kuro và chat được ngay, không cần cấu hình lại.
- **SC-005**: Mọi lỗi liên quan đến model hiện bằng tiếng Việt, có câu chỉ cách sửa.

## Giả định

- Danh sách model của Claude gồm các tên rút gọn Sonnet, Opus, Haiku mà Claude Code nhận; tên đầy đủ (bắt đầu bằng `claude-`) cũng được chấp nhận vì người dùng có thể cần model cụ thể.
- Danh sách model của Antigravity lấy từ chính chương trình Antigravity trên máy, không chép tay.
- ChatGPT (Codex) và các AI qua máy chủ tương thích chưa có cách liệt kê model đo được, nên không có ô chọn nhanh và không chặn lúc lưu.
- Người dùng dùng Kuro một mình trên máy của mình; không cần đồng bộ lựa chọn model giữa các máy.
