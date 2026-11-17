# Bộ công cụ & File mẫu Xác nhận thanh quyết toán Thầu phụ / Tổ đội thi công
Phòng Kỹ thuật - Thi công | Công ty CP Đầu tư và Xây dựng Giao thông Phương Thành

## 1. Cấu trúc thư mục
- `mau/Mau_XacNhan_ThanhQuyetToan_ThauPhu.xlsx`: Tệp Excel mẫu chuẩn mực của Phòng KTTC, gồm đầy đủ 6 sheet:
  - `TTC`: Thông tin chung (Dự án, Gói thầu, Đội thi công, Số HĐ, Ngày HĐ, Đợt XNKL, Người lập/duyệt).
  - `1.XNKL`: Phiếu xác nhận khối lượng đợt / quyết toán (Hạng mục, ĐVT, KL HĐ/BVTC, Lũy kế trước, Đề nghị đợt này, Phòng KTTC xác nhận, Tỷ lệ hoàn thành).
  - `2.VTC`: Phiếu xác nhận vật tư thi công theo BVTC và BPTC (Xi măng, Cát, Đá, Thép, Bê tông...).
  - `3.VTLC`: Phiếu đánh giá hao hụt vật tư luân chuyển (Đà giáo, Ván khuôn, Búa rung, Cọc ván thép...).
  - `4.DGTD`: Bảng đánh giá tiến độ thi công so với cam kết hợp đồng.
  - `GHI_CHU`: Bảng đối soát số liệu nội bộ giữa BĐH và Phòng KTTC, gắn nhãn căn cứ.
- `tao_ho_so_mau.py`: Script Python tự động sinh file mẫu hoặc nhân bản file mẫu vào thư mục dự án đang làm việc (`5. XAC NHAN KHOI LUONG/`).

## 2. Quy tắc lưu trữ tệp tin trong Kuro OS
- **Tuyệt đối không lưu vào `QLDA/99-Temp/qlda/`** (đây là tàn dư của hệ thống cũ, không tồn tại trên các máy tính mới).
- **Mọi tệp làm việc phải được lưu trực tiếp vào thư mục dự án đang làm việc (active workspace)**:
  - Dự án theo chuẩn 9 thư mục: lưu vào `<Workspace>/5. XAC NHAN KHOI LUONG/<Ten_Doi>/`
  - Dự án thông thường: lưu vào `<Workspace>/XAC_NHAN_KHOI_LUONG/` hoặc ngay thư mục gốc của dự án.
- Tên tệp xuất bản chuẩn: `XNKL_[TenDoi]_[Dot]_[YYYYMMDD].xlsx` (ví dụ: `XNKL_ToanTienPhat_Dot1_20261117.xlsx`).

## 3. Lệnh khởi tạo file mẫu nhanh vào thư mục dự án
```bash
python tools/XacNhanThanhQuyetToan/tao_ho_so_mau.py --dest "<duong_dan_thu_muc_du_an>/5. XAC NHAN KHOI LUONG/Bang_Xac_Nhan_Thanh_Toan.xlsx"
```
