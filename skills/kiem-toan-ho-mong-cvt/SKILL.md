---
name: Kiểm toán hố móng CVT
description: "Kiểm toán vòng vây cọc ván thép bằng chương trình HTML: chạy, đọc đạt/không đạt, xuất MCT Midas, đối soát."
group: Vận hành
---

# Kiểm toán hố móng, vòng vây cọc ván thép (bộ CVT)

Chương trình `NHAP_kiem_toan_vong_vay` (HTML một tệp, chạy offline) tính vòng vây cọc ván thép theo TCVN 11815:2017 mục 7.3, khung phương pháp v1.2 cộng bổ sung v1.3, v1.4 (đã duyệt 11/11/2026). Skill này dạy chạy chương trình, đọc kết quả đúng, xuất mô hình sang Midas và đối soát. **Chương trình tính, AI không tự tính tay.**

## Khi nào dùng
- "Kiểm toán vòng vây trụ T11", "chạy lại bộ số này", "đạt hay không đạt giai đoạn 3".
- "Xuất MCT sang Midas", "đối chiếu bảng Beam Force, Beam Stress với chương trình".
- "Thêm gối đàn hồi theo TCVN 10304", "so sánh gối cố định và gối đàn hồi".
- Không dùng cho: bóc khối lượng, lập BPTC, bản vẽ CAD (dùng skill khác).

## Chuẩn bị
- Gói chạy: `tools/KiemToanHoMongCVT/` (README ở đó). Chương trình: `chuong_trinh/20261111_KiemToanVongVay_CVT_v2.0.html`; khung phương pháp: `khung_phuong_phap/`.
- Cần Python 3 với `playwright` và Chromium hoặc Edge. Không cần mạng, không cần Midas.
- Số liệu vào: tệp JSON xuất từ chương trình (menu Công cụ, "Xuất JSON"), hoặc bộ mặc định T11 Ninh Cơ. Dự án mới: người dùng nhập ở tab Đầu vào rồi xuất JSON; AI không tự điền địa chất, cao độ, tải.

## Cách chạy
```bash
python tools/KiemToanHoMongCVT/chay_kiem_toan.py --config <du_an>.json --out <thu_muc_ket_qua>
python tools/KiemToanHoMongCVT/chay_kiem_toan.py --hoi-quy        # sau mọi thay đổi chương trình: 5 mốc phải KHỚP
```
Đầu ra: `tong_hop.md` (bảng đạt, không đạt), `tong_hop.json` (số từng giai đoạn: M, σ, phản lực, khung mặt bằng), `mct/*.mct`, `thuyet_minh.xlsx`, `ghi_chu.txt`. Chi tiết tham số xem README của gói.

## Quy trình
1. Đọc JSON đầu vào, liệt kê ô thiếu (hệ số k của lớp đất khi dùng gối đàn hồi, tải băng, cột chống tạm). Thiếu thì hỏi hoặc ghi "Chưa có căn cứ"; không tự đặt số.
2. Chạy `chay_kiem_toan.py`. `ghi_chu.txt` phải trống lỗi.
3. Đọc `tong_hop.md` trước: kết luận (có mục không đạt hay không), rồi từng mục không đạt: tỷ số, giai đoạn, vị trí.
4. Kiểm tính hợp lý: cân bằng lực khung mặt bằng, chuyển vị cừ ≤ L/400 khi dùng gối đàn hồi, tầng nào thanh chống không đạt. Tỷ số > 1 là không đạt, 0,9 đến 1 là sát.
5. Báo cáo: kết luận trước, bảng mục không đạt, giả thiết đã dùng (nhãn `[GIẢ THIẾT]`, `[NGƯỜI DÙNG KHAI]`, `[ĐÃ XÁC MINH]`), việc cần anh quyết. Mẫu ở mục Đầu ra của agent `ky-su-kiem-toan-ho-mong-cvt`.
6. Cần Midas: dùng `mct/`, xem `references/midas.md` (cách nhập, bẫy biến dạng cắt, cách đối soát).
7. Lưu tệp mới có phiên bản vào `99-Temp/<slug>/`; trước khi sửa hay ghi đè tệp đã có thì sao lưu vào `_backup/YYYYMMDD/` và ghi `_backup/_log.md`.

## Bẫy
- **Số liệu trong HTML tự lưu trong trình duyệt**, còn `chay_kiem_toan.py` luôn nạp sạch: kết quả hai nơi chỉ khớp khi cùng một JSON.
- **Gối đàn hồi chỉ dùng cho giai đoạn không có bịt đáy**; giai đoạn có bịt đáy luôn gối cố định 0,5 m dưới mặt bê tông. Thiếu k thì giai đoạn đó tự rơi về gối cố định và ghi "Chưa có căn cứ".
- **Giai đoạn một tầng chống dùng tổ hợp (7-14)** M = M_B + 0,75·M_m, nên M_max của chương trình lớn hơn M tổng tải.
- **Midas mặc định có biến dạng cắt**, chương trình thì không: tệp MCT đã đặt `bSD = NO`; mô hình cũ nhập từ trước sẽ lệch vài phần trăm.
- **Tiết diện dầm cừ trong MCT là hình vuông tương đương**: M, V, chuyển vị đúng, σ trên Midas KHÔNG dùng được (W khác cừ thật).
- Phản lực gối khung chống trên Midas gần 0 vì khung tự cân bằng; xem lực dọc thanh và mômen.
- Không dùng em dash (U+2014) trong mọi văn bản.

## Kiểm chứng
- Bộ mặc định T11: `python chay_kiem_toan.py --hoi-quy` in `KHỚP 5 mốc` (tong_hop 68b005dd, chi_tiet feeb1273, khung_mat_bang b187c6dd, thuyet_minh_cu 6104f99f, ty_so_40 e2741f1c) và 47 trên 60 mục đạt.
- MCT: `kiem/kiem_mct.py`, `kiem/kiem_mct_cu.py` giải lại độc lập từ nội dung tệp, lệch ≤ 1e-3 với chương trình.
- Excel: `kiem/kiem_excel_com.py` (cần Excel thật) tính lại công thức, 0 lệch, 0 lỗi.
