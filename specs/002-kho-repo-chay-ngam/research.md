# Nghiên cứu: Kho repo GitHub

Đo trên bản clone ở `E:/0.Code/Repo github/` ngày 2026-11-17.

## 1. Repo và giấy phép

| Repo | Commit | Giấy phép | Quyết định |
|---|---|---|---|
| datadrivenconstruction/DDC_Skills_for_AI_Agents_in_Construction | 410ed1e | MIT | Đưa thư mục skill nhóm 1-5. Loại `6_OpenConstructionERP/` (phần mềm đã gỡ), `Books/`, PDF sách, script publish, dữ liệu CWICR (CC BY-NC) |
| tt-a1i/archify | a406594 | Apache-2.0 | Đưa thư mục `archify/` (18 MB, không cần cài thêm, chạy bằng Node) |
| wheresryan22/anatomy | 1482e84 | MIT | Đưa SKILL.md, references, kit, scripts, examples |
| Graphify-Labs/graphify | a9860f7 | Apache-2.0 | Chỉ hướng dẫn; chạy cần gói `graphifyy` (uv) và shell, ghi "cần Bash" |
| github/spec-kit | ba8363f | MIT | Chỉ hướng dẫn; quy trình cần lệnh `specify` và PowerShell, ghi "cần Bash" |
| IfcOpenShell/IfcOpenShell | 3026407 | GPL-3.0 | Không đóng gói; thư viện `ifcopenshell` đã có trong `requirements-ky-thuat.txt` |
| xeokit/xeokit-sdk | 07a9878 | AGPL-3.0 | Không đóng gói; skill nhắc nghĩa vụ mở mã khi phát hành |
| storytold/cadcraft | 3b7eb1b | Apache-2.0 | Chưa có skill nào; chưa đưa |

## 2. Không nạp kho vào lời nhắc

- **Quyết định**: kho nằm ngoài `brain/.claude/skills`; tool `tim_skill` chấm điểm từ khoá trên tên + mô tả + thư mục nhóm, trả 8 kết quả.
- **Lý do**: KE-HOACH mục 10 đo được: 49 skill đã làm chọn sai nhiều hơn. Mô tả DDC bằng tiếng Anh nên mô tả tool dặn AI truyền từ khoá tiếng Anh (AI tự dịch câu hỏi tiếng Việt).
- **Đã cân nhắc**: nhúng vector (thêm thư viện, tải mô hình); nạp hết (vỡ SC-002).

## 3. Đọc skill không phụ thuộc quyền Read

- **Quyết định**: `doc_skill` trả nội dung SKILL.md và đọc được tệp kèm theo đường dẫn tương đối trong thư mục skill.
- **Lý do**: Claude Code ở chế độ `dontAsk` có thể từ chối đọc ngoài thư mục làm việc (brain); tool nội bộ chặn được `..` thoát ra ngoài skill.

## 4. Chạy mã đã duyệt

- **Quyết định**: đơn vị duyệt là **gói mã của một skill** = SHA-256 của mọi tệp không phải `.md` trong thư mục skill. `chay_ma_kho(skill, tep, doi_so)` chỉ chạy khi dấu vân tay gói khớp sổ duyệt (`kho/da-duyet.json` đi kèm repo hoặc `state/kho-da-duyet.json` duyệt trên máy). `.py` chạy bằng Python của venv, `.mjs/.js` bằng `node`; đuôi khác bị từ chối. Thư mục làm việc là dự án đang mở; giới hạn 300 giây.
- **Lý do**: không cần bật Bash cho cả máy; sửa một byte trong mã đã duyệt là tự chặn.
- **Đã cân nhắc**: duyệt từng tệp (archify có hàng trăm tệp); bật Bash (mở toàn máy).

## 5. Cập nhật kho không phá `git pull`

- **Quyết định**: kho là tệp theo dõi bởi git trong repo Kuro. Kiểm tra bản mới trên máy người dùng chỉ hỏi `git ls-remote` từng nguồn và báo; áp dụng bản mới là chạy `tools/dong_bo_kho.py` trên máy người bảo trì rồi đẩy lên, máy khác nhận qua cập nhật Kuro thường. Đồng bộ: chữ thay ngay; gói mã có dấu vân tay mới chưa duyệt thì giữ bản cũ đang chạy, bản mới lưu cạnh dạng `<skill>.cho-duyet/`.
- **Lý do**: sửa tệp theo dõi trên máy người dùng làm `git pull --ff-only` của `cap-nhat.bat` thất bại.

## 6. Việc theo lịch

- **Quyết định**: dùng lại `state/reminders.json`; khi khởi động thêm 3 việc nếu chưa có theo `id`: `bao-cao-tuan` (`0 7 * * 1`), `soat-ho-so` (`0 20 * * *`), `kiem-tra-kho` (`0 9 * * 1`, không gọi AI). `soat-ho-so` ghi `state/soat-ho-so.json` (thời điểm soát trước) và chỉ gọi AI khi có tệp sửa sau mốc đó. Vòng lặp hiện tại chỉ khớp phút hiện tại nên tự không chạy bù.
