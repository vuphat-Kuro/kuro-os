# Bộ agent kiểm toán hố móng CVT, v1.0 (11/11/2026)

Gói tự chứa để kiểm toán **vòng vây cọc ván thép và hố móng** của công ty (PKTTC, Phương Thành): chương trình tính (HTML một tệp, chạy offline), khung phương pháp đã duyệt, trình chạy dòng lệnh cho agent, bộ kiểm chứng, số liệu mẫu và định nghĩa agent cùng skill. Mọi con số do chương trình tính; agent đọc, kiểm hợp lý và báo cáo.

## Trong gói

| Thư mục, tệp | Nội dung |
|---|---|
| `chuong_trinh/20261111_KiemToanVongVay_CVT_v2.0.html` | Chương trình (mở bằng trình duyệt, không cần mạng). Tab Hướng dẫn, Đầu vào, Kết quả, Thuyết minh, Mô hình, 3D. |
| `chay_kiem_toan.py` | Chạy chương trình không cần mở tay: nạp JSON, tính, ghi tổng hợp, MCT Midas, Excel thuyết minh, hồi quy. |
| `khung_phuong_phap/` | Khung phương pháp tính v1.2 (duyệt 06/11/2026), bổ sung v1.3 và v1.4 (duyệt 11/11/2026). |
| `kiem/` | `hoi_quy_T11.js` (5 mốc hồi quy), `kiem_mct.py`, `kiem_mct_cu.py` (giải lại tệp MCT độc lập), `so_midas_khung.py` (đối soát bảng Midas), `doi_soat_xlsx.py`, `kiem_excel_com.py` (Excel thật). |
| `mau/` | `20261111_T11_mac_dinh_v2.0.json` (bộ số mặc định T11, đọc lại được bằng `--config`), `Mau_KiemToan_NinhCo_T11_T12.json` (mẫu cũ 5 giai đoạn), `20261111_ThuyetMinh_T11_Excel.xlsx`, `mct/` (tệp MCT mẫu khung chống, dầm cừ). |
| `agent/` | `ky-su-kiem-toan-ho-mong-cvt.md` (agent) và `kiem-toan-ho-mong-cvt/` (skill, kèm `references/phuong-phap.md`, `references/midas.md`). Bản dùng thật nằm ở `agents/` và `skills/` của brain, bản mirror ở `QLDA/.claude/skills/`. |

## Chạy nhanh
Cần Python 3, `pip install playwright`, Chromium hoặc Edge (`python -m playwright install chromium` nếu chưa có).
```bash
python chay_kiem_toan.py --out ket_qua                                   # bộ mặc định T11
python chay_kiem_toan.py --config du_an.json --out ket_qua_du_an         # dự án khác (JSON xuất từ chương trình)
python chay_kiem_toan.py --hoi-quy                                       # 5 mốc hồi quy, thoát 1 nếu lệch
python chay_kiem_toan.py --config du_an.json --khung-json T2:4 --khong-excel --khong-mct --out kq   # số khung chống để so Midas
```
Kết quả: `tong_hop.md`, `tong_hop.json`, `mct/`, `thuyet_minh.xlsx`, `ghi_chu.txt`. Dự án mới: mở HTML, nhập ở tab Đầu vào, menu Công cụ, "Xuất JSON", rồi dùng `--config`.

## Phiên bản và kiểm
- Chương trình v2.0 gồm: phương án gối đàn hồi (TCVN 10304 Phụ lục A), tab Hướng dẫn, xuất mô hình Midas (khung chống, dầm cừ 1 m), biểu đồ ứng suất kiểu Combined và bộ biểu đồ dầm cừ (M, V, N, σ, chuyển vị, phản lực), bảng nội lực CSV.
- Bộ mặc định T11: hồi quy `tong_hop 68b005dd`, `chi_tiet feeb1273`, `khung_mat_bang b187c6dd`, `thuyet_minh_cu 6104f99f`, `ty_so_40 e2741f1c`, 60 dòng, **47 trên 60 mục đạt**. `chay_kiem_toan.py --hoi-quy` in `KHỚP 5 mốc`.
- Tệp MCT: giải lại độc lập từ nội dung tệp, khung chống lệch ≤ 2,4·10⁻⁹, dầm cừ ≤ 8·10⁻⁴ (có lò xo ≤ 6,6·10⁻³). Tệp đặt `bSD = NO` (không biến dạng cắt) để Midas ra đúng số của chương trình.
- Excel thuyết minh T11: Excel thật tính lại 293 công thức, 0 lỗi, 0 lệch; đối soát độc lập 147 giá trị, 0 lệch.

## Chưa kiểm hoặc cần anh quyết
1. Trên Midas thật chưa thử: `*FRAME-RLS` (chiều nhả khớp), quy ước góc xoay ván nằm, ván đứng, tiết diện kép dạng hộp. Tiết diện dầm cừ trong MCT là hình vuông tương đương: M, V, chuyển vị đúng, **σ trên Midas không dùng được** (đề xuất đổi sang ống tròn để cả I và W đúng, chờ anh quyết).
2. Hệ số k của lớp đất (Bảng A.1) chưa có số thiết kế; tệp thử có lò xo dùng k giả 12.000, KHÔNG dùng cho hồ sơ.
3. Thuyết minh và Excel xuất ra là bản dự thảo chờ duyệt. Xuất MCT chưa có tầng neo, cột chống tạm, bệ chèn. Dầm cừ không có tải dọc trục (N = 0).
4. Bộ ca thử `99-Temp/qlda/mau_tinh/dot59/ca/` chỉ dựng lại được bản T11; 5 ca còn lại giữ bản 10/11 (bộ nạp ca gốc không còn).

## Quy tắc
Theo `QLDA/CLAUDE.md`: kết luận trước, không bịa số (thiếu thì "Chưa có căn cứ"), sao lưu `_backup/YYYYMMDD/` và ghi `_backup/_log.md` trước khi sửa hoặc ghi đè, không em dash. Gói chưa commit.
