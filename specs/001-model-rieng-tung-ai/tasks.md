# Danh sách việc: Mỗi AI nhớ model riêng

**Đầu vào**: `specs/001-model-rieng-tung-ai/` (spec.md, plan.md, research.md, data-model.md, contracts/api.md)
**Kiểm thử**: có (nguyên tắc V), viết cùng lúc với mã trong `tests/test_core.py`

Định dạng: `[ID] [P?] [Câu chuyện] Mô tả`. `[P]` = làm song song được (khác tệp, không phụ thuộc).

## Giai đoạn 1: Nền tảng (chặn mọi câu chuyện)

- [x] T001 Thêm `CLAUDE_MODELS` (Mặc định, sonnet, opus, haiku) và hàm `model_key(provider)` trả `KURO_MODEL_<ID>` trong `server/config.py`
- [x] T002 Đổi `load_runtime()` trong `server/config.py`: `MODEL` = giá trị `KURO_MODEL_<AI đang chọn>` (AI trống coi là claude)
- [x] T003 Thêm hàm `model_error(provider, model, agy_list)` trong `server/config.py`: trả câu lỗi tiếng Việt kèm gợi ý (difflib) hoặc rỗng nếu hợp lệ, theo quy tắc data-model.md

## Giai đoạn 2: Câu chuyện 1 - Chuyển AI không mang model sai (P1)

**Mục tiêu**: đổi AI không làm hỏng model; mỗi AI giữ model riêng.
**Kiểm tra độc lập**: quickstart bước 2.

- [x] T004 [US1] `POST /api/settings` trong `server/main.py`: ghi `KURO_MODEL` vào `model_key(AI trong thân hoặc AI đang chọn)`, không ghi khóa chung
- [x] T005 [US1] `GET /api/settings` trong `server/main.py`: `KURO_MODEL.value` = `config.MODEL`, thêm `model_theo_ai`
- [x] T006 [US1] `dashboard/app.js`: đổi AI trong hộp Cài đặt thì ô Model hiện model đã lưu của AI đó (cập nhật cả `dataset.orig`)
- [x] T007 [US1] Chuyển đổi bản cũ trong `server/config.py` (`migrate_model()` gọi từ `ensure_dirs()`): theo research.md mục 5
- [x] T008 [US1] Bài kiểm tra trong `tests/test_core.py`: lưu model cho 2 AI rồi đổi qua lại; chuyển đổi bản cũ hợp lệ và không hợp lệ

## Giai đoạn 3: Câu chuyện 3 - Chặn tên model sai lúc lưu (P2)

**Mục tiêu**: Claude/Antigravity không lưu được tên lạ.
**Kiểm tra độc lập**: quickstart bước 4.

- [x] T009 [US3] `save_settings` trong `server/main.py` thành `async`; gọi `config.model_error` (danh sách agy qua `cli_engines.models`), lỗi thì HTTP 400
- [x] T010 [US3] Dịch lỗi model của hãng không có danh sách sang tiếng Việt trong `server/engine.py` (dùng cho ping và lượt chat), theo research.md mục 7
- [x] T011 [P] [US3] Bài kiểm tra `model_error` trong `tests/test_core.py`: Claude nhận sonnet và `claude-...`, chặn tên Gemini; Antigravity theo danh sách; AI khác không chặn

## Giai đoạn 4: Câu chuyện 2 - Ô chọn nhanh cho Claude (P2)

**Mục tiêu**: ô chọn trên thanh trên cùng có cho Claude và Antigravity.
**Kiểm tra độc lập**: quickstart bước 3.

- [x] T012 [US2] `GET /api/models` trong `server/main.py`: trả `CLAUDE_MODELS` khi AI là claude (hoặc chưa chọn)
- [x] T013 [US2] `dashboard/app.js`: ô chọn nhanh bỏ lựa chọn "Model mặc định" tự thêm khi danh sách đã có mục rỗng (tránh trùng với Claude)

## Giai đoạn 5: Câu chuyện 4 - Báo khi đổi AI giữa phiên (P3)

**Mục tiêu**: hội thoại không nối nhầm giữa các AI, có dòng báo.
**Kiểm tra độc lập**: quickstart bước 5.

- [x] T014 [US4] `server/cli_engines.py`: sự kiện `final` trả mã hội thoại trần
- [x] T015 [US4] `server/engine.py`: `run_turn` gắn tiền tố `<AI>:` cho mọi mã, mã trần cũ coi là `claude`, chỉ nối tiếp khi trùng AI; `chat` phát dòng báo khi phiên đã có mã của AI khác
- [x] T016 [US4] Bài kiểm tra trong `tests/test_core.py`: hàm tách tiền tố (mã trần, trùng AI, khác AI)

## Giai đoạn 6: Hoàn thiện

- [x] T017 [P] `env.example`: thay `KURO_MODEL` bằng ghi chú khóa theo AI; `README.md`, `KE-HOACH.md` cập nhật
- [x] T018 Tăng số `app.js?v=` trong `dashboard/index.html`, tăng `VERSION`
- [x] T019 Chạy toàn bộ `tests/`, chạy thử thật quickstart bước 2 đến 6, rồi commit tiếng Việt và đẩy lên GitHub

## Phụ thuộc

- Giai đoạn 1 trước mọi giai đoạn khác.
- US1 (T004 đến T008) trước US3 (T009 dùng cùng hàm lưu).
- US2 và US4 độc lập với nhau, làm sau Giai đoạn 1.
- T019 cuối cùng.

## Chiến lược

MVP = Giai đoạn 1 + US1 (sửa đúng lỗi người dùng gặp). Sau đó US3, US2, US4, rồi hoàn thiện, thử thật và phát hành một lần.
