> Đọc khi: Cần tra cứu định dạng file đầu ra, biểu mẫu báo cáo và văn phong giao tiếp, công văn, chỉ đạo.
> Nguồn gốc: tách từ GEMINI.md v2.12 (bản lưu). Quy tắc chung ở QLDA/CLAUDE.md; số mục trong file này là số nội bộ, giữ nguyên.

## PHẦN 11. ĐỊNH DẠNG ĐẦU RA & VĂN PHONG

### 11.1. Định dạng file

| Loại nội dung                                         | Định dạng                                              | Công cụ                                                                                          |
| ------------------------------------------------------- | --------------------------------------------------------- | -------------------------------------------------------------------------------------------------- |
| Số liệu, bảng tính, danh mục, ma trận, tiến độ | `.xlsx` (ưu tiên) / `.csv`                          | Python`pandas`, `openpyxl` – có công thức, định dạng tiêu đề, cố định dòng đầu |
| Công văn, báo cáo, thuyết minh, biên bản         | `.docx` (văn bản chính thức) / `.md` (bản nháp) | Python`python-docx`                                                                              |
| Biểu đồ                                              | `.png` nhúng vào báo cáo                            | `matplotlib`                                                                                     |
| Trả lời nhanh trên chat                              | Markdown (bảng, checklist)                               | —                                                                                                 |

- Sau khi xuất file, cung cấp **đường dẫn clickable** tới file.
- Script phục vụ lặp lại (báo cáo tháng, tổng hợp) lưu tại thư mục `02-Tools/<NN-NgonNgu>/<TenTool>/` để tái sử dụng.
- **Biểu mẫu báo cáo định kỳ nội bộ:** Thường được lập trên định dạng Word, Excel và PowerPoint.

### 11.2. Văn phong

- Tiếng Việt chuẩn mực, khoa học; thuật ngữ cầu đường, quản lý dự án.
- **Sử dụng Skill trong giao tiếp:** chỉ nêu skill khi giải quyết bài toán chuyên sâu hoặc khi anh yêu cầu.
- **Báo cáo lãnh đạo:** số liệu, đề xuất trước; nhận định, căn cứ sau; nêu rõ việc cần lãnh đạo quyết.
- **Văn bản gửi CĐT/TVGS:** thể thức hành chính (Quốc hiệu, số/ký hiệu, trích yếu, căn cứ, nội dung, nơi nhận); văn phong trang trọng, chặt chẽ.
- **Chỉ đạo công trường:** mệnh lệnh rõ – việc, người, hạn, tiêu chí hoàn thành.
- **Hướng dẫn kỹ thuật:** mục đích → đầu vào → căn cứ → phương pháp → các bước → kiểm tra → đầu ra.
- Rà soát văn bản: chỉ ra chỗ chưa rõ, thiếu căn cứ, trùng lặp, mâu thuẫn, khó triển khai.
- Tóm tắt tài liệu dài: giữ nguyên điều kiện, ngoại lệ, con số quan trọng.

### 11.2.1. Phụ lục Thể thức văn bản hành chính (theo Nghị định 30/2020/NĐ-CP)

- **Khổ giấy & Định lề:** Khổ A4 (210 mm × 297 mm), định hướng đứng. Lề trên: 20–25 mm; Lề dưới: 20–25 mm; Lề trái: 30–35 mm; Lề phải: 15–20 mm.
- **Phông chữ chuẩn:** Times New Roman, bộ mã Unicode (TCVN 6909:2001), màu đen.
- **Quy chuẩn thành phần thể thức chính yếu:**
  + **Quốc hiệu & Tiêu ngữ:** Đặt tại ô trên cùng góc phải. Quốc hiệu: chữ in hoa, cỡ chữ 12–13, đứng, đậm. Tiêu ngữ: chữ in thường, cỡ chữ 13–14, nghiêng, đậm, chữ cái đầu viết hoa, có gạch nối giữa các từ.
  + **Tên cơ quan, tổ chức ban hành:** Đặt tại ô trên cùng góc trái. Cỡ chữ 12–13, in hoa, đứng, đậm (vd. `CÔNG TY CP ĐẦU TƯ VÀ XÂY DỰNG GIAO THÔNG PHƯƠNG THÀNH / PHÒNG KỸ THUẬT – THI CÔNG`).
  + **Số, ký hiệu văn bản:** Cỡ chữ 13, đứng, in thường (vd. `Số: .../PT-KTTC`).
  + **Địa danh và ngày, tháng, năm ban hành:** Cỡ chữ 13–14, nghiêng (vd. `Hà Nội, ngày ... tháng ... năm ...`).
  + **Tên loại văn bản và trích yếu nội dung:** Tên loại: in hoa, cỡ chữ 13–14, đứng, đậm; Trích yếu: cỡ chữ 13–14, đứng, đậm (vd. `CÔNG VĂN / V/v rà soát biện pháp thi công...`).
  + **Nội dung văn bản:** Cỡ chữ 13–14, in thường, dãn dòng 1.15–1.5 line, dãn đoạn Before/After 2–6 pt.
  + **Chức vụ, họ tên và chữ ký:** Cỡ chữ 13–14, chức vụ in hoa đứng đậm, họ tên in thường đứng đậm.
  + **Nơi nhận:** Cỡ chữ 11–12, in thường, nghiêng, đậm chữ `Nơi nhận:`, danh sách nơi nhận chữ in thường cỡ 11.

