# Danh sách việc: Diễn hoạ bản vẽ

Kế hoạch gọn (không tách plan.md): `server/dien_hoa.py` (bật/tắt ComfyUI, quy trình API, nhận yêu cầu), `engine.py`
(nhánh diễn hoạ trong `chat`, `mot_lan` dịch prompt), `calc.py` (tool `dien_hoa` cho Claude), `scheduler.py` (tắt khi
rảnh), `tools/cai_dien_hoa.py` + `cai-dien-hoa.bat` (cài cho máy khác).

- [x] T001 Kiểm phần cứng máy: RTX 4060 Laptop 8 GB, driver 566.07 (CUDA ≤ 12.7 → bản cu126), RAM 15,6 GB, ổ E trống 265 GB
- [x] T002 Tra tên tệp, nguồn, dung lượng, giấy phép (ComfyUI v0.45.0 cu126 1,96 GB; RealVisXL V5 fp16 6,94 GB; ControlNet Union promax 2,51 GB)
- [x] T003 `server/dien_hoa.py`: thiếu gì, bật/tắt, kích thước, quy trình, `ve`, `yeu_cau`
- [x] T004 `engine.py`: `mot_lan`, `dien_hoa_anh`, nhánh diễn hoạ trong `chat`
- [x] T005 `calc.py`: tool `dien_hoa`; `scheduler.py`: tắt khi rảnh
- [x] T006 `tools/cai_dien_hoa.py`, `cai-dien-hoa.bat`
- [x] T007 Cài trên máy này bằng chính trình cài; đo tên nút và tham số thật qua `/object_info`, sửa quy trình cho khớp
- [x] T008 Bài kiểm tra: `yeu_cau`, `kich_thuoc`, `workflow` khớp `/object_info` đã đo
- [x] T009 Thử thật: bản vẽ nét, ảnh hiện trạng; đo thời gian; xem ảnh bằng mắt
- [x] T010 README, KE-HOACH, VERSION; đẩy lên GitHub

## Kết quả đo (2026-11-17, RTX 4060 Laptop 8 GB)

- `/object_info` khớp mọi nút và tham số của quy trình; lưu ở `tests/comfyui_object_info.json`, có bài kiểm tra.
- fp16: 475 giây cho 2 ảnh (tràn VRAM). Thêm `--fp8_e4m3fn-unet`: lần đầu 118 giây kể cả bật ComfyUI và dịch prompt,
  các lần sau 65 giây. Đạt SC-001.
- Bản vẽ nét mặt đứng: giữ đúng mái, 3 tầng, ô cửa. Ảnh hiện trạng: đổi vật liệu theo mô tả, giữ khối. Đạt SC-002 (người dùng đánh giá thêm).
- Tự tắt: vừa bật thì không tắt; rảnh quá 10 phút thì tắt, VRAM trả về mức nền. Đạt SC-003.
