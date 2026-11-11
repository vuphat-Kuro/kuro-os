# Phương pháp tính của chương trình (tóm tắt, nguồn: `khung_phuong_phap/`)

Căn cứ: TCVN 11815:2017 mục 7.3 (vòng vây cọc ván thép), TCVN 10400:2015, TCVN 5575:2024 (thanh chống thép), TCVN 10304:2014 Phụ lục A (gối đàn hồi), TCVN 7571-16 (thép H). Khung v1.2 duyệt 06/11/2026; bổ sung v1.3 và v1.4 duyệt 11/11/2026. Nội dung đầy đủ ở ba tệp trong `khung_phuong_phap/`; đây chỉ là bản đồ để đọc kết quả.

## Cấu trúc: bốn trục điều kiện, sáu module
Trục: 1 Thủy văn (mực nước thi công, nước trong hố), 2 Địa chất (lớp đất đáy móng), 3 Kết cấu (số tầng chống), 4 Thi công (biện pháp, bịt đáy).
- M1 Áp lực đất, nước (chủ động, bị động, nước ngoài và trong theo các sơ đồ Điều 7.3.2.6).
- M2 Đáy hố: bùng cát, trồi đất (tính một lần cho cả hố).
- M6 Bịt đáy: đẩy nổi, uốn bản (tính một lần cho cả hố).
- M3 Ngàm: chiều sâu đóng cọc t, ổn định lật (7.3.5.3, t tính trước rồi đặt gối tại t/2 dưới đáy đào).
- M4 Độ bền cừ: dầm FEM một chiều, σ = M/W_eff với W_eff = η_w · k_hm · W_x.
- M5 Khung chống: thanh chống, khung mặt bằng FEM, cột chống tạm, mối hàn, neo.

## Sơ đồ gối dưới cừ
- Giai đoạn không có tầng chống: công xôn ngàm tại t0 (7.3.3.2).
- Có tầng chống, chưa bịt đáy: gối chốt tại t/2 dưới đáy đào (dầm liên tục, 7.3.4.3 và 7.3.5.3), một tầng thì tổ hợp (7-14).
- Có bịt đáy: gối 0,5 m dưới mặt bê tông bịt đáy (anh chốt).
- **Tùy chọn gối đàn hồi** (TCVN 10304 Phụ lục A): lò xo cách nhau s (mặc định 0,4 m) từ đáy hố đến mũi cừ, C_z = k·z/γc, tải = p_a + p_w (bỏ p_p), lò xo chỉ chịu nén, hội tụ theo s/2 ngưỡng 1%, chuyển vị cừ ≤ L/400, áp lực nền (A.7). Cần hệ số k của lớp đất (Bảng A.1); thiếu thì giai đoạn đó dùng gối cố định và ghi "Chưa có căn cứ".

## Nhãn nguồn số liệu
`[ĐÃ XÁC MINH]` có văn bản gốc; `[NGƯỜI DÙNG KHAI]` anh chốt hoặc cung cấp; `[GIẢ THIẾT]` em đặt, chờ duyệt; `[CẦN KIỂM TRA]` chưa chắc; "Chưa có căn cứ" khi tiêu chuẩn hay hồ sơ không có số.

## Giới hạn đã biết
- Dầm cừ không có tải dọc trục (N = 0).
- Khung chống mặt bằng giải đàn hồi, chưa nhân hệ số ổn định φ trong biểu đồ σ; kiểm nén uốn (η, φ) tách riêng.
- Giai đoạn đắp đất lại và tháo giằng chưa mô hình hóa đầy đủ (Trục 4); cần kiểm riêng.
- Biến dạng cắt của thanh không xét (dầm Euler); Midas mặc định có xét nên phải đặt `bSD = NO`.
