# Đặc tả tính năng: Diễn hoạ bản vẽ bằng AI chạy trên máy

**Nhánh**: `003-dien-hoa-ban-ve` (làm trên `main`) | **Ngày tạo**: 2026-11-17 | **Trạng thái**: Xong (v1.7.0)

**Đầu vào**: "Cập nhật vào Kuro ComfyUI + comfyui_controlnet_aux + model SDXL + ControlNet Union SDXL để khi gọi ra có thể tự làm diễn hoạ bản vẽ khi cần." Ưu điểm người dùng nêu: miễn phí, không gửi bản vẽ ra ngoài, giữ hình sát nhất.

**Quyết định của người dùng (2026-11-17)**: model RealVisXL (ảnh thật); Kuro tự bật ComfyUI khi cần và tự tắt sau 10 phút rảnh; nhận bản vẽ nét, ảnh chụp hiện trạng, ảnh mô hình 3D/BIM; đồng ý tải khoảng 11,5 GB, cài ở `E:/0.Code/ComfyUI`; máy khác tự chọn cài bằng `cai-dien-hoa.bat`; mỗi lần ra 2 phương án.

## Kịch bản sử dụng

### Câu chuyện 1 - Diễn hoạ từ khung chat với mọi AI (P1)

Kỹ sư đính kèm ảnh mặt đứng và gõ "diễn hoạ thành nhà phố 3 tầng, mặt tiền kính, buổi chiều". Kuro trả 2 ảnh thật giữ đúng nét bản vẽ, hiện ngay trong khung chat và lưu vào `<dự án>/dien-hoa/`. Dùng được dù AI đang chọn là Claude, ChatGPT hay Antigravity.

**Chấp nhận**: (1) ảnh nét → 2 ảnh giữ bố cục nét; (2) ảnh chụp hiện trạng hoặc ảnh mô hình 3D → 2 ảnh giữ bố cục và chiều sâu; (3) câu có "diễn hoạ" nhưng không kèm ảnh → chat bình thường; (4) mô tả tiếng Việt được AI đang chọn dịch sang prompt tiếng Anh, dịch lỗi thì dùng nguyên văn.

### Câu chuyện 2 - Claude tự gọi diễn hoạ khi cần (P2)

Với Claude, Kuro có công cụ `dien_hoa`; Claude tự gọi khi người dùng nhờ minh hoạ phương án.

### Câu chuyện 3 - Tự bật, tự tắt (P2)

ComfyUI chỉ chạy khi cần; rảnh 10 phút thì Kuro tắt để trả VRAM và RAM. Chỉ tắt ComfyUI do Kuro bật.

### Câu chuyện 4 - Máy khác tự chọn cài (P3)

`cai-dien-hoa.bat`: kiểm card NVIDIA ≥ 8 GB, chọn bản ComfyUI hợp driver, tải tiếp khi đứt mạng, chạy lại bỏ qua phần đã có. Máy chưa cài thì Kuro trả lời "máy này chưa có diễn hoạ" kèm cách cài, không chạy dở.

## Yêu cầu chức năng

- **FR-001**: Diễn hoạ chạy hoàn toàn trên máy (ComfyUI ở 127.0.0.1); bản vẽ không gửi ra Internet. Riêng câu mô tả được gửi cho AI đang chọn để dịch.
- **FR-002**: Ba chế độ: nét (lineart), hiện trạng và 3D (độ sâu), tự nhận theo câu chữ, mặc định nét.
- **FR-003**: Mỗi lần 2 ảnh, giữ tỉ lệ ảnh gốc, lưu `<dự án>/dien-hoa/` và hiện trong chat.
- **FR-004**: Thiếu thành phần thì báo rõ thiếu gì và cách cài.
- **FR-005**: Model và ComfyUI không nằm trong repo Kuro; trình cài tải từ nguồn chính thức, ghim phiên bản.

## Tiêu chí thành công

- **SC-001**: Trên máy RTX 4060 8 GB, 2 ảnh 1024² trong dưới 3 phút kể cả bật ComfyUI.
- **SC-002**: Ảnh kết quả giữ đúng đường nét chính của bản vẽ (người dùng đánh giá).
- **SC-003**: Sau 10 phút rảnh, VRAM được trả lại.

## Giả định

- Giấy phép: ComfyUI GPL-3.0 (không đóng gói, chỉ cài riêng), RealVisXL OpenRAIL++, ControlNet Union SDXL và controlnet_aux Apache-2.0.
- Bộ tiền xử lý (nét, độ sâu) tải model nhỏ ở lần đầu dùng từ HuggingFace.
