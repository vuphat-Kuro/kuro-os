# BoQ_Comparator - Công Cụ So Sánh Phụ Lục Hợp Đồng & Bảng Khối Lượng (BoQ)

## 1. Mục đích công cụ
Công cụ tự động hóa việc đọc, bóc tách và đối chiếu bảng khối lượng (Bill of Quantities - BoQ) giữa 2 phiên bản Phụ lục hợp đồng (hoặc giữa Hợp đồng ban đầu và Phụ lục điều chỉnh). 

Công cụ giải quyết các bài toán cốt lõi:
1. **Giữ nguyên cây phân cấp cha – con:** Tự động nhận diện các cấp bậc (Phân đoạn, Phần, Mục công trình, Cụm vị trí, Đầu mục công việc).
2. **Cài đặt công thức tự động:** Tạo các công thức `=SUM(...)` tại tất cả các dòng cấp cha để kiểm soát tổng giá trị nhiều tầng.
3. **Đối chiếu đa nhà thầu:** Tách bạch khối lượng và giá trị của nhà thầu được chỉ định (ví dụ: Phương Thành) so với Toàn Liên danh.
4. **Phân tích biến động:** Tính toán chi tiết chênh lệch khối lượng, chênh lệch đơn giá, tỷ lệ % thay đổi đơn giá, chênh lệch giá trị và tự động nhận diện lý do điều chỉnh.

---

## 2. Yêu cầu môi trường & Thư viện
* **Ngôn ngữ:** Python 3.10+ (Đã tương thích Python 3.14 trên máy làm việc).
* **Thư viện phụ thuộc:**
  ```text
  openpyxl>=3.1.0
  PyMuPDF>=1.23.0
  rapidocr_onnxruntime>=1.2.0
  ```

---

## 3. Cấu trúc thư mục công cụ
```text
02-Tools/02-Python/BoQ_Comparator/
├── README.md               # Hướng dẫn sử dụng
├── requirements.txt        # Thư viện phụ thuộc
├── boq_comparator.py       # Module chính & giao diện dòng lệnh (CLI)
├── core/
│   ├── pdf_parser.py       # Bóc tách bảng dữ liệu từ PDF (vector & OCR scan)
│   ├── matcher.py          # Thuật toán đối chiếu đầu mục và ghép cặp dữ liệu
│   └── excel_writer.py     # Xuất bảng tính Excel phân cấp đa tầng
└── configs/
    └── default_config.json # Cấu hình mặc định (tỷ lệ giảm thầu, màu sắc, font)
```

---

## 4. Hướng dẫn sử dụng (CLI)

Chạy công cụ qua dòng lệnh:
```bash
python boq_comparator.py \
  --base "D:/GGAI_QLDA/01-DuAn/MRLT-XL01/01-HoSoPhapLy/2026.01.15 PLHĐ 118.1-VEC gói XL01 HCM - LT.pdf" \
  --adjusted "D:/GGAI_QLDA/01-DuAn/MRLT-XL01/01-HoSoPhapLy/Bill PLHD04.pdf" \
  --contractor "Phương Thành" \
  --output "D:/GGAI_QLDA/01-DuAn/MRLT-XL01/01-HoSoPhapLy/BangSoSanh_ChiTiet.xlsx"
```

### Các tham số tùy chọn:
* `--base` (hoặc `-b`): Đường dẫn file phụ lục ban đầu (PDF scan hoặc text).
* `--adjusted` (hoặc `-a`): Đường dẫn file phụ lục điều chỉnh (PDF text/vector).
* `--contractor` (hoặc `-c`): Tên nhà thầu cần bóc tách khối lượng riêng (Mặc định: `Phương Thành`).
* `--output` (hoặc `-o`): Đường dẫn file Excel đầu ra (.xlsx).
* `--discount` (hoặc `-d`): Tỷ lệ giảm thầu nếu có (Mặc định: `0.0502` tương ứng 5,02%).

---

## 5. Đầu ra của công cụ
File Excel xuất ra chuẩn Times New Roman với 2 Sheet nghiệp vụ:
1. `01_TongHop_PhanCap`: Bảng tổng hợp điều hành theo từng phân đoạn, phục vụ báo cáo Ban Tổng Giám đốc.
2. `02_ChiTiet_SoSanh_Bill`: Bảng chi tiết toàn bộ các đầu mục công việc, có công thức tính tổng các lớp cha con và các cột đánh giá biến động.
