# Danh sách việc: Kho repo GitHub cho Kuro

**Kiểm thử**: có, trong `tests/test_core.py`. `[P]` = làm song song được.

## Giai đoạn 1: Dữ liệu kho

- [x] T001 `kho/nguon.json`: 5 nguồn trong phạm vi (DDC, archify, anatomy, graphify, spec-kit) với url, commit, giấy phép, đường dẫn chọn/loại, ghi chú "cần Bash" cho graphify/spec-kit
- [x] T002 `tools/dong_bo_kho.py`: chép từ clone gốc theo nguon.json, sinh `kho/muc-luc.json` (id, tên, mô tả, repo, nhóm, đường dẫn, dấu vân tay gói mã, cần Bash), giữ gói mã đã duyệt khi bản mới khác
- [x] T003 Chạy đồng bộ lần đầu; `kho/da-duyet.json` duyệt sẵn archify và anatomy (đã đọc mã), DDC để chờ duyệt

## Giai đoạn 2: US1 - Tự tìm skill (P1)

- [x] T004 `server/kho.py`: `tim(cau, n)`, `doc(skill, tep)` (chặn thoát thư mục)
- [x] T005 `server/calc.py`: tool `tim_skill`, `doc_skill` trong MCP `kuro`
- [x] T006 `server/engine.py`: luôn cho phép 3 tool kho; `cli_prompt` thêm đường dẫn mục lục kho
- [x] T007 `CLAUDE.md`: luật dùng `tim_skill` khi skill sẵn có không phủ, nêu tên skill + repo, cảnh báo CWICR
- [x] T008 [P] Bài kiểm tra: tìm "concrete quantity takeoff" ra skill DDC liên quan; `doc` chặn `..`

## Giai đoạn 3: US2 - Chỉ chạy mã đã duyệt (P1)

- [x] T009 `server/kho.py`: `van_tay_goi`, `da_duyet`, `chay(skill, tep, doi_so)`, `duyet(skill)`
- [x] T010 `server/calc.py`: tool `chay_ma_kho`
- [x] T011 `server/main.py`: `GET /api/kho`, `POST /api/kho/duyet` (local_only)
- [x] T012 Dashboard: mục "Kho skill" trong Cài đặt (repo, số skill, giấy phép, gói mã chờ duyệt, nút Duyệt)
- [x] T013 [P] Bài kiểm tra: chưa duyệt bị chặn; duyệt rồi chạy được; sửa 1 byte bị chặn lại

## Giai đoạn 4: US3 - Việc theo lịch (P2)

- [x] T014 `server/scheduler.py`: thêm việc cài sẵn khi thiếu; `soat-ho-so` chỉ gọi AI khi có tệp mới; `kiem-tra-kho` không gọi AI
- [x] T015 `server/main.py`: `GET /api/lich`, `POST /api/lich/{id}` (bật/tắt), `POST /api/lich/{id}/chay`
- [x] T016 Dashboard: mục "Việc theo lịch" (bật/tắt, Chạy thử, lần chạy gần nhất)
- [x] T017 [P] Bài kiểm tra: thêm việc cài sẵn không ghi đè việc người dùng đã sửa; soát không có tệp mới thì không gọi AI

## Giai đoạn 5: US4 - Kho tự cập nhật (P3)

- [x] T018 `server/kho.py`: `kiem_tra_nguon()` bằng `git ls-remote`, báo repo có commit mới
- [x] T019 [P] Bài kiểm tra đồng bộ: chữ đổi thì thay; mã đổi chưa duyệt thì giữ bản cũ, bản mới ở `.cho-duyet`

## Giai đoạn 6: Hoàn thiện

- [x] T020 README, KE-HOACH (mục kho, bẫy), tăng VERSION
- [x] T021 Chạy toàn bộ tests, thử thật: câu hỏi IFC/dự toán qua Claude dùng `tim_skill`; vẽ sơ đồ bằng archify qua `chay_ma_kho`; chạy thử `soat-ho-so`; đẩy lên GitHub. Ghi chú 2026-11-17: thử thật qua Antigravity (tự tìm 3 skill DDC clash); đường Claude chưa thử trực tiếp vì phiên đăng nhập Claude trên máy hết hạn, đã gọi thẳng 3 tool MCP thay thế
