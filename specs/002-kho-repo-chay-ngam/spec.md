# Đặc tả tính năng: Kho repo GitHub cho Kuro, tự dùng và chạy ngầm

**Nhánh**: `002-kho-repo-chay-ngam`

**Ngày tạo**: 2026-11-17

**Trạng thái**: Đã làm (bản 1.6.0)

**Đầu vào**: "Cài các GitHub sẵn có vào thẳng Kuro, biến Kuro thành một AI thực thụ chạy ngầm." Máy đã có 18 repo (khoảng 1.100 skill) trong `E:/0.Code/Repo github/`.

**Quyết định của người dùng (2026-11-17)**:
- Chạy ngầm gồm cả ba: tự tìm và dùng skill khi cần; tự làm việc theo lịch; tự cập nhật kho từ GitHub.
- Phạm vi: xây dựng (kho `xay-dung`: DDC, IfcOpenShell, xeokit, CADCraft) + công cụ làm việc (archify, anatomy, graphify, spec-kit). Không đưa ui-design, video, YouTube, công cụ lập trình.
- Chỉ chạy mã (script, MCP) đã duyệt.
- Kho đi theo bản Kuro trên GitHub (mọi máy cài Kuro đều có).
- Việc theo lịch cài sẵn: báo cáo tiến độ tuần; soát hồ sơ mới trong dự án.
- Repo có bản mới: tải về; phần hướng dẫn dùng ngay, phần mã chờ duyệt.

## Kịch bản sử dụng và kiểm tra *(bắt buộc)*

### Câu chuyện 1 - Hỏi bình thường, Kuro tự tìm đúng skill trong kho (Ưu tiên: P1)

Kỹ sư hỏi "bóc khối lượng bê tông từ file IFC này" mà không biết tên skill nào. Kuro tự tra kho, chọn skill phù hợp (ví dụ skill DDC bóc khối lượng BIM), đọc hướng dẫn, làm theo và trả lời bằng tiếng Việt, ghi rõ đã dùng skill nào từ repo nào.

**Vì sao ưu tiên này**: Đây là giá trị chính: Kuro dùng được cả nghìn skill mà không bị quá tải hay chọn sai như khi nạp hết.

**Kiểm tra độc lập**: Hỏi 10 câu chuyên môn thuộc 10 nhóm khác nhau (BIM, dự toán, tiến độ, an toàn, hợp đồng, sơ đồ...) mà không nêu tên skill; đếm số câu Kuro chọn đúng skill.

**Kịch bản chấp nhận**:

1. **Cho** kho có skill DDC về bóc khối lượng BIM, **khi** hỏi bóc khối lượng từ IFC, **thì** Kuro nêu tên skill và repo đã dùng, làm theo quy trình trong skill, trả lời tiếng Việt.
2. **Cho** một câu hỏi mà skill tiếng Việt sẵn có của Kuro đã phủ (ví dụ dự toán theo định mức Việt Nam), **khi** hỏi, **thì** Kuro ưu tiên skill tiếng Việt, chỉ dùng skill trong kho để bổ sung.
3. **Cho** câu hỏi không có skill phù hợp trong kho, **khi** hỏi, **thì** Kuro nói rõ không tìm thấy skill phù hợp và trả lời bằng kiến thức chung, không ép dùng skill sai.
4. **Cho** skill trong kho cần dữ liệu giá CWICR, **khi** dùng cho dự án, **thì** Kuro báo trước đó là dữ liệu cấm dùng thương mại.

---

### Câu chuyện 2 - Mã trong repo chỉ chạy khi đã duyệt (Ưu tiên: P1)

Skill trong kho có kèm script hoặc MCP server (ví dụ IfcOpenShell đọc tệp IFC). Kuro chỉ chạy được phần mã đã có trong sổ duyệt. Phần chưa duyệt thì Kuro vẫn đọc hướng dẫn nhưng nói rõ "mã này chưa được duyệt nên chưa chạy".

**Vì sao ưu tiên này**: Nguyên tắc IV (an toàn mặc định); máy có key AI và hồ sơ dự án.

**Kiểm tra độc lập**: Một skill có script đã duyệt và một skill có script chưa duyệt; yêu cầu Kuro dùng cả hai.

**Kịch bản chấp nhận**:

1. **Cho** MCP IfcOpenShell đã duyệt, **khi** hỏi đếm dầm cột trong tệp IFC, **thì** Kuro chạy được và trả số liệu kèm nguồn.
2. **Cho** script chưa có trong sổ duyệt, **khi** Kuro cần dùng, **thì** Kuro không chạy, báo tên script và cách xin duyệt.
3. **Cho** người dùng xem danh sách kho trong Cài đặt, **khi** mở, **thì** thấy từng repo: số skill, giấy phép, mã đã duyệt hay chưa, ngày duyệt.

---

### Câu chuyện 3 - Việc theo lịch chạy ngầm (Ưu tiên: P2)

Kuro tự chạy hai việc cài sẵn, bật hoặc tắt trong Cài đặt: (a) báo cáo tiến độ tuần lúc 7 giờ sáng thứ Hai; (b) mỗi tối soát tệp mới trong thư mục dự án đang mở, báo chỗ thiếu hoặc sai. Kết quả nằm trong một phiên chat riêng trên giao diện và gửi Telegram nếu đã bật.

**Vì sao ưu tiên này**: Biến Kuro từ "hỏi mới trả lời" thành trợ lý tự làm việc.

**Kiểm tra độc lập**: Bật việc soát hồ sơ, thêm một tệp vào thư mục dự án, chạy thử ngay (nút "Chạy thử"), xem phiên kết quả.

**Kịch bản chấp nhận**:

1. **Cho** việc báo cáo tuần đang bật, **khi** đến 7 giờ sáng thứ Hai, **thì** có phiên mới chứa báo cáo, đọc dữ liệu từ thư mục dự án đang mở.
2. **Cho** việc soát hồ sơ đang bật, **khi** đến giờ và có tệp mới từ lần soát trước, **thì** Kuro liệt kê tệp mới và vấn đề tìm thấy; không có tệp mới thì ghi "không có gì mới", không gọi AI.
3. **Cho** máy tắt hoặc Kuro không chạy đúng giờ, **khi** Kuro mở lại, **thì** không chạy bù hàng loạt; chỉ chạy lần kế tiếp theo lịch.
4. **Cho** người dùng tắt một việc trong Cài đặt, **khi** đến giờ, **thì** việc đó không chạy.

---

### Câu chuyện 4 - Kho tự cập nhật từ GitHub, mã mới chờ duyệt (Ưu tiên: P3)

Định kỳ Kuro kiểm tra các repo nguồn trên GitHub. Repo có bản mới thì tải về: phần hướng dẫn (chữ) dùng ngay; phần mã chạy được giữ bản đã duyệt cho tới khi người dùng bấm duyệt. Kuro báo "repo X có bản mới, Y tệp mã thay đổi chờ duyệt".

**Vì sao ưu tiên này**: Giữ kho mới mà không phá nguyên tắc chỉ chạy mã đã duyệt.

**Kiểm tra độc lập**: Giả lập repo nguồn có commit mới (sửa một SKILL.md và một script), chạy kiểm tra cập nhật.

**Kịch bản chấp nhận**:

1. **Cho** repo nguồn đổi một SKILL.md, **khi** Kuro cập nhật kho, **thì** lần hỏi sau dùng hướng dẫn mới.
2. **Cho** repo nguồn đổi một script đã duyệt, **khi** Kuro cập nhật kho, **thì** Kuro vẫn chạy bản script đã duyệt và báo có bản mới chờ duyệt.
3. **Cho** mất mạng hoặc repo nguồn bị xoá, **khi** đến lượt kiểm tra, **thì** kho giữ nguyên, ghi lý do, không báo lỗi lên giao diện chat.

---

### Trường hợp biên

- Hai skill trong kho trùng tên với skill sẵn có của Kuro: skill sẵn có (tiếng Việt) thắng; skill trong kho vẫn tìm được bằng tên đầy đủ kèm repo.
- Repo có giấy phép không cho chia sẻ lại hoặc không rõ giấy phép: không đưa vào kho trên GitHub; ghi lý do trong danh sách kho.
- Dữ liệu chỉ dùng phi thương mại (CWICR) hoặc giấy phép AGPL (xeokit): không đóng gói mã hay dữ liệu đó vào Kuro; skill chỉ hướng dẫn và cảnh báo khi dùng.
- Repo đã gỡ khỏi máy (OpenConstructionERP): các skill phụ thuộc nó bị đánh dấu "không dùng được", không xuất hiện khi Kuro tìm skill.
- Repo giả mạo (ví dụ `cadcraft-desktop/cadcraft`): danh sách nguồn chỉ nhận đúng địa chỉ repo đã ghi trong sổ.
- Máy người dùng khác chưa có công cụ mà mã đã duyệt cần (ví dụ môi trường IfcOpenShell): Kuro báo cách cài, không chạy dở.

## Yêu cầu *(bắt buộc)*

### Yêu cầu chức năng

- **FR-001**: Hệ thống PHẢI có một kho skill đi kèm Kuro, gồm các repo trong phạm vi đã chốt, mỗi repo ghi: nguồn GitHub, phiên bản (commit), giấy phép, số skill, trạng thái duyệt mã.
- **FR-002**: Kuro PHẢI tự tìm skill phù hợp trong kho theo câu hỏi, mà không đưa toàn bộ danh sách skill của kho vào mỗi lượt chat.
- **FR-003**: Kuro PHẢI ưu tiên skill tiếng Việt sẵn có khi chúng phủ cùng việc, và nêu tên skill cùng repo đã dùng trong câu trả lời.
- **FR-004**: Hệ thống PHẢI chỉ cho chạy script và MCP server có trong sổ duyệt (khớp đúng nội dung đã duyệt); mã chưa duyệt hoặc đã đổi sau khi duyệt bị chặn, kèm thông báo tiếng Việt.
- **FR-005**: Giao diện PHẢI có danh sách kho trong Cài đặt: repo, số skill, giấy phép, trạng thái duyệt, nút duyệt cho mã đang chờ.
- **FR-006**: Hệ thống PHẢI có hai việc theo lịch cài sẵn (báo cáo tiến độ tuần, soát hồ sơ mới), bật/tắt và chạy thử được trong Cài đặt, kết quả vào phiên riêng và Telegram nếu bật.
- **FR-007**: Việc soát hồ sơ PHẢI chỉ gọi AI khi có tệp mới kể từ lần soát trước.
- **FR-008**: Hệ thống PHẢI định kỳ kiểm tra bản mới của từng repo nguồn, cập nhật phần hướng dẫn ngay và giữ phần mã ở bản đã duyệt cho tới khi được duyệt.
- **FR-009**: Hệ thống PHẢI loại khỏi kho trên GitHub mọi mã hoặc dữ liệu có giấy phép không cho phân phối lại cùng Kuro (CC BY-NC, AGPL, không rõ giấy phép), và ghi lý do.

### Thực thể chính

- **Repo nguồn**: một repo GitHub trong phạm vi; có địa chỉ đúng, commit đang dùng, giấy phép, danh sách skill, danh sách tệp mã.
- **Skill trong kho**: tên, mô tả, repo gốc, đường dẫn hướng dẫn, trạng thái dùng được hay không.
- **Sổ duyệt**: mỗi mục là một tệp mã hoặc MCP server đã duyệt, kèm dấu vân tay nội dung, người duyệt, ngày duyệt.
- **Việc theo lịch**: tên, lịch chạy, bật/tắt, lần chạy gần nhất, phiên kết quả.

## Tiêu chí thành công *(bắt buộc)*

### Kết quả đo được

- **SC-001**: Với 10 câu hỏi chuyên môn không nêu tên skill, Kuro chọn đúng skill ít nhất 8 câu.
- **SC-002**: Thời gian chờ câu trả lời đầu tiên không tăng quá 5 giây so với trước khi có kho.
- **SC-003**: 100% lần Kuro cần chạy mã chưa duyệt đều bị chặn và có thông báo.
- **SC-004**: Hai việc theo lịch chạy đúng giờ trong 7 ngày liên tục khi máy bật.
- **SC-005**: Máy người dùng khác cập nhật Kuro xong có ngay kho và hai việc theo lịch, không phải cài tay gì thêm ngoài công cụ phụ thuộc được báo rõ.

## Giả định

- Repo nguồn lấy từ bản đã kiểm tra trên máy (`E:/0.Code/Repo github/`); khi đưa vào Kuro dùng đúng địa chỉ GitHub gốc đã ghi.
- Skill DDC và công cụ là giấy phép MIT (theo skill `kho-xay-dung-mo`); giấy phép của archify, anatomy, graphify, spec-kit sẽ kiểm tra ở bước kế hoạch.
- "Thư mục dự án đang mở" là workspace dự án của bản Kuro 1.5.x (`projects/`).
- Người duyệt mã là chủ máy (người dùng hoặc anh của người dùng); không cần phân quyền nhiều người.
- Hướng dẫn trong skill (chữ) được dùng ngay khi cập nhật theo lựa chọn của người dùng; rủi ro chữ lạ lái AI được giảm bằng việc mã vẫn phải duyệt và Bash vẫn tắt mặc định.
