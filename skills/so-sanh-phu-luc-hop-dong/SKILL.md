---
name: "So sánh phụ lục hợp đồng"
description: "Bóc tách, đối chiếu bảng khối lượng (BoQ) giữa các phiên bản phụ lục hợp đồng xây dựng, giữ phân cấp đa tầng, lập Excel có công thức."
group: Vận hành
---

# Kỹ năng Đối chiếu & Phân tích Biến động Phụ lục Hợp đồng (BoQ Comparator)

Kỹ năng này chuẩn hóa quy trình tiếp nhận, bóc tách và đối chiếu bảng khối lượng (Bill of Quantities - BoQ) giữa các phiên bản Phụ lục hợp đồng hoặc giữa Hợp đồng gốc và các Phụ lục điều chỉnh trong các dự án xây dựng giao thông của Công ty CP Đầu tư và Xây dựng Giao thông Phương Thành.

Người dùng là **Phó phòng Kỹ thuật – Thi công**, trực tiếp quản lý khối lượng, kỹ thuật và tham mưu Ban Tổng Giám đốc. Mọi bảng tính đối chiếu phải đảm bảo tính toán chặt chẽ, truy xuất nguồn rõ ràng, giữ nguyên phân cấp các lớp hạng mục cha - con và sử dụng công thức động.

---

## 1. Nguyên tắc cốt lõi & An toàn hệ thống

1. **Tuân thủ quy tắc quản lý file theo `GEMINI.md`:**
   - **Tuyệt đối KHÔNG viết script tạm thời trực tiếp vào thư mục dự án** (như `01-DuAn/.../01-HoSoPhapLy/`). Thư mục pháp lý dự án chỉ chứa tài liệu gốc (PDF) và file kết quả bàn giao cuối cùng (`.xlsx`).
   - Mọi xử lý tạm thời (OCR, trích xuất text nháp, JSON trung gian) phải lưu trong thư mục `scratch/` của artifact hoặc thư mục `99-Temp/`.
   - Toàn bộ mã nguồn xử lý phải được kế thừa và vận hành từ công cụ chuẩn:
     `QLDA\02-Tools\02-Python\BoQ_Comparator\boq_comparator.py`.
2. **Bảo toàn cấu trúc phân cấp (Hierarchy Preservation):**
   - Không được "làm phẳng" (flatten) toàn bộ bảng danh mục công việc thành một danh sách đơn lẻ nếu hợp đồng gốc có phân đoạn/phần/hạng mục cha con.
   - Các dòng nhóm cha (Phân đoạn, Phần công trình, Hạng mục) phải có công thức Excel động `=SUM(...)` cộng các dòng con, không được gõ số tĩnh.
3. **Phân tách trách nhiệm nhà thầu:**
   - Tại các gói thầu Liên danh (như Gói XL01 Mở rộng cao tốc TP.HCM – Long Thành), bảng đối chiếu bắt buộc phải tách riêng 2 luồng số liệu: **Khối lượng/Giá trị của Phương Thành** và **Khối lượng/Giá trị của Toàn Liên danh**.
4. **Chuẩn mực trình bày Excel bàn giao:**
   - Font chữ toàn bộ workbook: **Times New Roman** (tiêu đề 11-14pt bold, dữ liệu 10pt, ghi chú 9pt italic).
   - Màu sắc nhận diện chuyên nghiệp:
     - Header tổng quan: Xanh Navy đậm (`#1B365D`)
     - Cột dữ liệu Phụ lục ban đầu: Xanh lam thép (`#2C5E8A`)
     - Cột dữ liệu Phụ lục điều chỉnh: Xanh mòng két / Teal (`#1B7878`)
     - Cột dữ liệu Chênh lệch biến động: Đỏ bầm Burgundy (`#9A3B3B`)
   - Bắt buộc cố định dòng tiêu đề (`freeze_panes`).
   - Định dạng số: Tiền tệ `#,##0`, Khối lượng `#,##0.00`, Tỷ lệ `0.00%`.

---

## 2. Quy trình thực hiện chuẩn 5 bước

### Bước 1: Tiếp nhận và phân loại hồ sơ
- Xác định đường dẫn file Phụ lục ban đầu (Base BoQ) và Phụ lục điều chỉnh (Adjusted BoQ).
- Kiểm tra định dạng file:
  - Nếu là PDF vector (văn bản có thể copy text): Dùng `PyMuPDF` (`fitz`) để trích xuất text block và bảng biểu.
  - Nếu là PDF scan dạng ảnh: Dùng `fitz` chuyển sang pixmap và chạy OCR qua `rapidocr_onnxruntime`.
  - Nếu là Excel/CSV: Đọc trực tiếp bằng `openpyxl` hoặc module `csv`.

### Bước 2: Chuẩn hóa cây phân cấp danh mục
- Xác định cấu trúc cây hạng mục của dự án:
  - **Level 1:** Phân đoạn gói thầu (ví dụ: Phân đoạn Km4 - Km9+240; Phân đoạn Km9+240 - Km13+900; Chi phí khác).
  - **Level 2:** Phần công trình (ví dụ: Phần Tuyến, Phần Cầu).
  - **Level 3:** Nhóm hạng mục / Cụm kết cấu (ví dụ: Xử lý đất yếu, Cọc khoan nhồi M1P-109P, Dầm Super-T, Đường công vụ, Mố nhô...).
  - **Level 4:** Các đầu mục công việc cụ thể (Work items / Bill lines).

### Bước 3: So khớp tương quan (Matching Engine)
- Áp dụng thuật toán so khớp đa tầng:
  1. So khớp chính xác theo mã hiệu/STT hợp đồng.
  2. So khớp mờ (Fuzzy matching) theo tên công việc chuẩn hóa (bỏ dấu cách thừa, chuyển chữ thường) kết hợp đối chiếu đơn vị tính.
  3. Áp dụng quy tắc đặc thù ngành cầu đường: nhận diện các trường hợp gộp hạng mục (ví dụ cọc trụ 18P gộp vào M1P-17P thành M1P-18P), phân tách chi tiết (ví dụ dầm Super-T chia theo 3 nhóm chiều dài).

### Bước 4: Chạy công cụ tạo bảng tính
Sử dụng công cụ `BoQ_Comparator` đã đóng gói sẵn:
```bash
python "D:/GGAI_QLDA/02-Tools/02-Python/BoQ_Comparator/boq_comparator.py" \
  --base "<Đường_dẫn_BoQ_gốc>" \
  --adjusted "<Đường_dẫn_BoQ_điều_chỉnh>" \
  --contractor "Phương Thành" \
  --output "<Đường_dẫn_file_Excel_kết_quả>"
```

### Bước 5: Kiểm tra chất lượng & Bàn giao
- Kiểm tra tính nguyên vẹn của công thức:
  - Đảm bảo các dòng Level 3 dùng `=SUM(đầu_mục_con)`.
  - Đảm bảo các dòng Level 2 dùng `=SUM(các_dòng_Level_3)`.
  - Đảm bảo các dòng Level 1 dùng `=SUM(các_dòng_Level_2)`.
  - Dòng Tổng cộng cuối bảng khớp với giá trị tổng phê duyệt.
- Kiểm tra 2 Sheet:
  1. `01_TongHop_PhanCap`: Báo cáo quản lý cấp phòng và Ban Giám đốc.
  2. `02_ChiTiet_SoSanh_Bill`: Báo cáo chi tiết kỹ thuật - kinh tế cho kỹ sư dự án và QS.

---

## 3. Quản lý công cụ & Nâng cấp (Tool Maintenance)

- Vị trí mã nguồn: `QLDA\02-Tools\02-Python\BoQ_Comparator\`
- Dữ liệu mẫu kiểm thử: `QLDA\02-Tools\02-Python\BoQ_Comparator\data\`
- Khi gặp dự án mới có cấu trúc bảng biểu hoặc định dạng PDF đặc thù:
  - Cập nhật quy tắc mapping hoặc parser trực tiếp trong `boq_comparator.py`.
  - Thêm config hoặc bộ từ khóa mới vào tool.
  - **Không tạo script rời rạc trong các thư mục dự án.**
