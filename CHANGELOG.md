# Nhật ký phiên bản Kuro OS

## [1.7.1] - 2026-11-17
- Nâng cấp nút dừng phản hồi & Đa luồng phiên hội thoại độc lập (Multi-Session Concurrent Stream):
  - **Nút Dừng phản hồi (Stop button):** Khi AI đang phản hồi, biểu tượng gửi tin tự động chuyển thành biểu tượng Stop vuông nổi bật (`⏹`), màu đỏ cam cảnh báo. Nhấn vào sẽ lập tức dừng phản hồi của phiên đó, ngắt process CLI nền và hiển thị thông báo `_(Đã dừng phản hồi theo yêu cầu)_`.
  - **Đa phiên xử lý độc lập, song song:** Chuyển đổi cơ chế chạy phản hồi sang các Task asyncio nền riêng biệt theo từng phiên (`session_id`), giải phóng hoàn toàn vòng lặp WebSocket. Kỹ sư có thể chuyển qua lại giữa các phiên khác nhau, gõ và gửi tin nhắn đồng thời mà không phải chờ đợi phiên trước xong.
  - **Chỉ báo trạng thái trực quan:** Thẻ phiên ở cột Lịch sử tự động hiển thị huy hiệu `Đang xử lý` khi đang chạy ngầm; thanh trạng thái hiển thị số lượng phiên đang xử lý song song.
  - **Chuẩn hóa hiển thị tên Agent:** Sửa đổi dấu gạch chéo kép `//` thành dấu hai chấm `:` chuẩn mực (ví dụ: `KURO CORE:`).

## [1.7.0] - 2026-11-17
- Diễn hoạ bản vẽ chạy trên máy (ComfyUI + RealVisXL V5 + ControlNet Union SDXL): gửi ảnh vào chat kèm câu "diễn hoạ ...", Kuro vẽ 2 phương án ảnh thật giữ đúng nét, lưu vào `<dự án>/dien-hoa/`. Nhận bản vẽ nét, ảnh hiện trạng, ảnh mô hình 3D/BIM; dùng được với mọi AI.
- Tự bật ComfyUI khi cần, tự tắt sau 10 phút rảnh. Máy khác cài bằng `cai-dien-hoa.bat` (cần card NVIDIA từ 8 GB, tải khoảng 11,5 GB).

## [1.6.1] - 2026-11-17
- Nâng cấp toàn diện Agent "Xác nhận thanh quyết toán thầu phụ và đội thi công" phiên bản gói v2:
  - **Tích hợp trọn bộ nghiệp vụ chuyên sâu:** Soát xét và đối chiếu khối lượng đa tầng (1.XNKL), vật tư thi công theo BVTC/BPTC (2.VTC), định mức hao hụt vật tư luân chuyển (3.VTLC), đánh giá tiến độ hợp đồng (4.DGTD), và kiểm soát công nhật hiện trường.
  - **Đóng gói 2 bộ mẫu Excel chính thức:** `MAU_XNKL-DOT_KTTC.xlsx` (phiếu đợt) và `MAU_XNKL-QT_KTTC.xlsx` (phiếu quyết toán 5 sheet đầy đủ) tại `tools/XacNhanThanhQuyetToan/mau/` và `QLDA/03-MauBieu/02-Excel/`.
  - **Bổ sung 6 kỹ năng (skills) ngành mới:** `so-sanh-phu-luc-hop-dong` (BoQ Comparator), `duyet-vat-tu-thi-cong` (hệ thống 4 mẫu DNVT-01..04), `kiem-tra-dong-bo-bvtc`, `kiem-tra-khoi-luong`, `soan-thao-cong-van`, và `xlsx`.
  - **Tích hợp bộ công cụ tự động hóa:** `BoQ_Comparator`, `kiem_tra_san_pham.py`, `tinh_lai_excel.py` (tính lại công thức qua Excel COM).
  - **Tuân thủ tuyệt đối các nguyên tắc đã thống nhất:**
    - Kho dữ liệu công ty `\\phuongthanhtranconsin.data.com\` (hoặc ổ Y:) là Read-Only chỉ để tra cứu tài liệu và lấy mẫu.
    - Tra cứu hợp đồng bắt buộc qua file Excel đầu mục `TỔNG HỢP.xlsx` và `DANH MỤC HỌP ĐỒNG, PHỤ LỤC HỢP ĐỒNG DỰ ÁN.xls`, tuyệt đối không quét đệ quy.
    - Mọi tệp bảng tính kết quả bắt buộc lưu vào thư mục dự án hiện hành trên máy người dùng (Active Workspace), cấm lưu vào `QLDA/99-Temp/` hay đường dẫn ảo; hỏi lại người dùng nếu chưa rõ cấu trúc lưu.

## [1.5.18] - 2026-11-17
- Thiết lập rào chắn quy tắc lưu tệp kết quả và bảo vệ kho dữ liệu công ty:
  - **Kho mạng UNC công ty là kho Read-Only (Chỉ đọc & Tra cứu):** Xác lập nguyên tắc bất khả xâm phạm trên toàn hệ thống (`AGENTS.md`, `CLAUDE.md`, `facts/kho-du-lieu-phuong-thanh.md`, `server/engine.py`): Thư mục mạng `\\phuongthanhtranconsin.data.com\12.KỸ THUẬT THI CÔNG` và các kho hợp đồng chỉ phục vụ đọc, tra cứu tài liệu và lấy file mẫu. Tuyệt đối không tự ý lưu tệp kết quả, tạo thư mục rác hay ghi đè lên kho mạng chung công ty (trừ khi có chỉ đạo rõ ràng từ người dùng).
  - **Quy định nơi lưu kết quả bắt buộc (Active Workspace trên máy người dùng):** Mọi tệp tin kết quả do AI/tool sinh ra (.xlsx, .html, .docx, .py, script, báo cáo, biểu mẫu...) bắt buộc phải lưu vào thư mục dự án hiện hành trên máy người dùng đang cài (Active Workspace đang mở trong Kuro, ví dụ: `D:\1`, `projects/...`).
  - **Nguyên tắc hỏi vị trí lưu khi chưa rõ:** Nếu trong thư mục dự án hiện hành chưa có quy tắc phân loại thư mục lưu (hoặc chưa rõ cấu trúc lưu cho hạng mục đó), AI bắt buộc phải hỏi lại người dùng vị trí muốn lưu trước khi thực hiện ghi tệp, tuyệt đối không tự ý lưu vào các vị trí chưa được phép.

## [1.5.17] - 2026-11-17
- Chuẩn hóa thư mục lưu trữ và bổ sung bộ tệp mẫu cho Agent Xác nhận thanh quyết toán:
  - Loại bỏ hoàn toàn đường dẫn ảo `QLDA/99-Temp/qlda/` trong `agents/xac-nhan-thanh-quyet-toan.md` và `skills/kiem-toan-ho-mong-cvt/SKILL.md` (vốn là tàn dư của hệ thống cũ, gây lỗi thiếu thư mục khi cài trên máy mới).
  - Quy định chuẩn xác vị trí lưu tệp: Mọi tệp bảng tính xác nhận thanh quyết toán phải được tạo và lưu trực tiếp trong thư mục dự án đang làm việc (`<Workspace>/5. XAC NHAN KHOI LUONG/<Ten_Doi>/` hoặc `<Workspace>/XAC_NHAN_KHOI_LUONG/`).
  - Đóng gói sẵn bộ tệp Excel mẫu chuẩn mực tại `tools/XacNhanThanhQuyetToan/mau/Mau_XacNhan_ThanhQuyetToan_ThauPhu.xlsx` gồm đầy đủ 6 sheet chuyên môn: `TTC` (Thông tin chung), `1.XNKL` (Phiếu xác nhận khối lượng đợt / quyết toán), `2.VTC` (Vật tư thi công theo BVTC), `3.VTLC` (Hao hụt vật tư luân chuyển BPTC), `4.DGTD` (Đánh giá tiến độ hợp đồng), `GHI_CHU` (Đối soát nội bộ BĐH vs Phòng KTTC).
  - Bổ sung công cụ `tools/XacNhanThanhQuyetToan/tao_ho_so_mau.py` để AI tự động nhân bản file mẫu sang thư mục dự án khi bắt đầu soát xét hồ sơ.
  - Chuẩn hóa toàn bộ danh xưng trong agent sang "kỹ sư phụ trách / người dùng" để áp dụng cho mọi máy tính trong công ty.

## [1.5.16] - 2026-11-17
- Hoàn thiện toàn diện giao diện Chat Input chuẩn Claude Desktop & Antigravity 2.0:
  - Menu nút cộng (+) đa cấp (Flyout Submenu): Bổ sung mục "Trình kết nối (Connectors) >" với các công tắc toggle (Python tính toán, Claude in Chrome, project-report-mcp, Google Drive...) và "Plugin & Kỹ năng >" tích hợp ô tìm kiếm cùng danh mục kỹ năng hạ tầng giao thông.
  - Bổ sung nút Thinking Pill (Mức độ suy nghĩ: Cao / Tiêu chuẩn / Tắt) và vòng tròn trạng thái hoạt động (Status Ring spinner) ngay trên thanh đáy Bottom Toolbar.
  - Nút Gửi tròn (Send button) và toàn bộ hàng điều khiển nằm tách biệt ở dòng dưới cùng, tuyệt đối không chèn hay đè lên vùng nhập văn bản.
- Cô lập và sửa triệt để cơ chế lưu Model riêng cho từng phiên làm việc:
  - Khắc phục hiện tượng đổi model ở một phiên làm các phiên khác bị đổi theo: Tách biệt biến model môi trường `provider_env(chosen_model)` với model toàn cục của `.env`, đồng thời chỉ định `effective_model` cho từng lượt chat của session.
  - Sửa hàm chuyển đổi Agent không tự động đóng phiên đang mở nếu đã có lịch sử.
- Thiết lập kho dữ liệu mạng dùng chung - Công ty CP ĐTXD Giao thông Phương Thành:
  - Chuẩn hóa 3 đường dẫn UNC mạng dùng chung trong `server/config.py` và `env.example`: Thư viện KTTC (`\\phuongthanhtranconsin.data.com\12.KỸ THUẬT THI CÔNG`), Kho HĐ Dự án (`HĐ các Dự án`), Kho HĐ Thầu phụ (`Hợp đồng kinh tế - Linh\HỢP ĐỒNG`).
  - Xây dựng module `server/tra_cuu_hop_dong.py` và API `/api/contracts/search`: Tra cứu tức thì (<0.05s) qua 2 file Excel index `TỔNG HỢP.xlsx` và `DANH MỤC HỌP ĐỒNG, PHỤ LỤC HỢP ĐỒNG DỰ ÁN.xls`, tuyệt đối không quét đệ quy tránh treo mạng công ty.
  - Lưu trữ quy định tra cứu vào hệ thống ký ức bền vững `facts/kho-du-lieu-phuong-thanh.md`, `MEMORY.md`, `AGENTS.md` và `CLAUDE.md`.

## [1.5.15] - 2026-11-16
- Chuẩn hóa persona Agent và cơ chế gọi công cụ kiểm toán hố móng CVT:
  - Khắc phục việc Agent tự động xưng hô cố định "anh Nghĩa" trên mọi máy: Loại bỏ việc hardcode tên cá nhân trong `agents/ky-su-kiem-toan-ho-mong-cvt.md` và `agents/xac-nhan-thanh-quyet-toan.md`, chuyển sang cơ chế xưng hô linh hoạt theo kỹ sư phụ trách / người dùng trên máy.
  - Bổ sung chỉ thị bắt buộc trong Agent: Khi người dùng yêu cầu xuất file báo cáo (Excel, HTML), Agent phải trực tiếp thực thi script `python tools/KiemToanHoMongCVT/chay_kiem_toan.py` hoặc dùng công cụ ghi tệp để tạo file thật ra thư mục dự án (`projects/<tên_dự_án>/`), cấm xuất mã thô và bảo người dùng copy dán vào Notepad.
  - Hướng dẫn người dùng khởi tạo **Phiên mới (➕ Phiên mới)** sau khi thêm quyền công cụ `Bash` để AI giải phóng hoàn toàn ngữ cảnh cấm đoán cũ.

## [1.5.14] - 2026-11-16
- Mở khóa toàn diện quyền ghi tệp và thực thi script cho Google Antigravity & OpenAI Codex (Fix write_file permission):
  - Khắc phục triệt để lỗi máy cài mới báo "phiên làm việc bị khóa quyền ghi tệp trực tiếp / write_file bị chặn trên hệ thống" khi yêu cầu xuất tệp HTML hoặc Excel (.xlsx).
  - Tự động bổ sung quyền `Bash` và `Write` vào danh mục `KURO_ALLOWED_TOOLS` mặc định, cho phép AI chạy script Python kiểm toán kỹ thuật và ghi tệp trực tiếp vào thư mục dự án.
  - Tự động gắn cờ `--dangerously-skip-permissions` khi gọi Google Antigravity (`agy`) ở chế độ headless và đặt chế độ `workspace-write` cho Codex khi phiên có quyền ghi tệp hoặc chạy shell.
  - Loại bỏ hoàn toàn câu nhắc cấm đoán ghi file trong system prompt (`cli_prompt`), hướng dẫn AI chủ động tạo tệp báo cáo thật ra đĩa thay vì chỉ xuất mã nguồn thô và bảo người dùng copy dán vào Notepad.

## [1.5.13] - 2026-11-13
- Cô lập và lưu cố định Model AI riêng biệt cho từng phiên làm việc (Session Model Isolation):
  - Khắc phục triệt để lỗi đổi model ở một vị trí khiến các phiên khác bị đổi theo: Model được lưu cố định vào cơ sở dữ liệu SQLite theo từng phiên (`sessions.model`), loại bỏ hiện tượng ghi đè model phiên vào trạng thái toàn cục `active_state.json`.
  - Hiển thị huy hiệu Model (Model Badge) trực quan ngay trên từng thẻ phiên trong danh sách Lịch sử hội thoại ở sidebar, giúp kỹ sư dễ dàng quan sát phiên nào đang dùng mô hình AI nào (Gemini Argon, Claude Opus 5.5, Sonnet,...).
  - Tự động cập nhật và đồng bộ mô hình AI tương ứng giữa thanh Model Pill dưới đáy khung chat, thông tin Model trong Panel Ngữ cảnh (Context Inspector) và cơ sở dữ liệu ngay khi chuyển phiên.
  - Xóa sạch biến model chờ (`pendingSessionModel`) khi mở phiên cũ hoặc sau khi khởi tạo phiên thành công, ngăn ngừa hoàn toàn tình trạng rò rỉ model từ phiên mới sang các phiên đã tồn tại.

## [1.5.12] - 2026-11-13
- Thiết kế lại hoàn toàn khung nhập nội dung chat (Chat Input Box) theo chuẩn hiện đại của Claude Code và Antigravity 2.0:
  - Tách biệt vùng nhập văn bản và hàng công cụ đáy (Bottom Toolbar): Nút gửi tin nhắn tròn bo góc tinh tế nằm ở góc dưới cùng bên phải, không còn bị chèn hay che khuất nội dung gõ phím.
  - Chuyển thanh chọn Model AI xuống đáy khung chat (Model Pill): Cho phép người dùng chuyển đổi mô hình AI riêng biệt cho từng cuộc hội thoại trực tiếp ngay tại vị trí soạn thảo mà không phải nhìn lên góc trên màn hình.
  - Bổ sung nút dấu cộng (+) đa năng: Tích hợp menu đính kèm tệp tin tài liệu (.xlsx, .docx, .pdf, .dwg...), thêm thư mục dự án qua cửa sổ Windows native (`pick_file.ps1`, `pick_folder.ps1`), gọi nhanh danh mục lệnh gạch chéo (/), kiểm tra ngữ cảnh và danh mục 22 kỹ năng chuyên môn.
  - Bổ sung thanh chọn Chế độ thực thi (Mode Pill): Tùy chọn nhanh giữa Tự động (Auto), Lập kế hoạch trước khi làm (Plan Mode) và Bám đuổi mục tiêu bền bỉ (Goal Mode).
  - Nâng cấp bộ đính kèm tệp đa năng: Hỗ trợ đính kèm cả ảnh lẫn tài liệu kỹ thuật, tự động lưu vào `.attachments/` và gắn kèm thông tin vào ngữ cảnh câu hỏi cho AI xử lý.

## [1.5.11] - 2026-11-13
- Khắc phục triệt để lỗi Kuro bị kẹt không phản hồi khi đang xem dở câu trả lời (phải chuyển phiên rồi mở lại mới thấy nội dung):
  - Bổ sung cơ chế phát sự kiện `turn_complete` từ backend mang trọn vẹn toàn bộ câu trả lời (`answer`) sau khi AI sinh xong và lưu vào cơ sở dữ liệu.
  - Tối ưu hóa hiệu năng render giao diện với Throttled Render (`scheduleBotRender` qua `requestAnimationFrame` 60fps), loại bỏ hoàn toàn hiện tượng nghẽn luồng WebView2 (Render Choking) khi nhận dồn dập hàng chục token Markdown mỗi giây.
  - Bổ sung cơ chế WebSocket Heartbeat Ping/Pong (15 giây) định kỳ hai chiều, giữ kết nối thông suốt liên tục khi AI suy nghĩ lâu hoặc chạy script kiểm toán Python mất nhiều thời gian.
  - Tích hợp bộ tự động phục hồi và đồng bộ (Auto-Recovery Sync): nếu giao diện đang ở trạng thái xử lý mà kết nối bị ngắt quãng hoặc quá thời gian chờ, hệ thống tự động kiểm tra và kéo toàn bộ câu trả lời đã lưu về hiển thị ngay lập tức mà không cần người dùng phải bấm chuyển phiên.

## [1.5.10] - 2026-11-13
- Sửa lỗi cú pháp JavaScript gây treo đơ giao diện khởi động: Khắc phục triệt để lỗi Unexpected token trong tệp app.js khiến ứng dụng không tải được danh sách cộng sự, gợi ý câu hỏi nhanh và trạng thái kết nối.
- Nâng cấp số phiên bản cache và Service Worker (v44 / kuro-os-v24) để trình duyệt và WebView2 tự động làm mới mã nguồn, không bị kẹt cache phiên bản cũ.

## [1.5.9] - 2026-11-13
- Khắc phục triệt để lỗi không mở được ứng dụng Desktop Kuro OS trên máy mới tải về:
  - Bổ sung các thư viện Desktop cốt lõi (`pywebview`, `pywin32`, `pythonnet`, `psutil`, `qrcode`, `pillow`) vào `requirements.txt`.
  - Nâng cấp `setup.bat` thông minh: tự động phát hiện mọi biến thể Python trên máy (`py -3.13`, `py -3.12`, `py -3.11`, `py`, `python`), không chặn tiến trình cài đặt nếu người dùng chưa cài Claude Code CLI.
  - Cơ chế tự phục hồi trong `app_desktop.py`: tự động cài bù gói `pywebview` nếu thiếu, tự động mở trên trình duyệt web kèm thông báo hướng dẫn thay vì bị crash ẩn.
- Chuẩn hóa hệ thống kiểm tra và cập nhật phiên bản:
  - Đồng bộ toàn bộ nhãn hiển thị phiên bản tĩnh trên giao diện (`v1.5.9`), chấm dứt triệt để hiện tượng hiển thị nhãn cũ `1.4` gây hiểu lầm.
  - Bổ sung nút "⚡ Cập nhật lại từ GitHub" trong hộp thoại phiên bản, cho phép người dùng chạy lại tiến trình cập nhật mã nguồn và cài thư viện bất cứ lúc nào kể cả khi đang ở bản mới nhất.
  - Bổ sung hộp thoại phản hồi rõ ràng khi nhấp nút "Kiểm tra bản mới trên GitHub" để người dùng nắm rõ tình trạng cập nhật của máy.

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
