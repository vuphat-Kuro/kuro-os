---
name: "QS - Khối lượng & dự toán"
description: "Đo bóc khối lượng, lập/kiểm tra dự toán, đơn giá, định mức, thanh toán, quyết toán, phát sinh, điều chỉnh giá hợp đồng."
group: Xây dựng
source: vnp-hatang-bim (skill Claude của chủ brain, nhập 2026-10-09)
---

# Đo bóc khối lượng & Dự toán (QS)

## Khi nào dùng

Đo bóc khối lượng, lập và kiểm tra dự toán, đơn giá, giá gói thầu, hồ sơ thanh toán - quyết toán, xử lý phát sinh và điều chỉnh giá hợp đồng cho công trình xây dựng Việt Nam. Dùng skill này bất cứ khi nào người dùng nhắc tới bóc tách khối lượng, tiên lượng, dự toán, đơn giá, định mức, vật liệu - nhân công - máy thi công, hao hụt vật tư, khối lượng phát sinh, bù giá, thanh toán giai đoạn, quyết toán A-B, hoặc đưa ra bảng tiên lượng/bảng dự toán cần soát - kể cả khi họ chỉ hỏi "cái này bao nhiêu tiền", "bóc giúp khối lượng phần này", "kiểm tra bảng này hộ tôi" mà không nói chữ "dự toán". Cũng dùng khi cần bóc khối lượng từ mô hình BIM (5D) hoặc từ bản vẽ.

Người dùng là kỹ sư QS có chứng chỉ nghiệp vụ, làm hạ tầng giao thông (cầu, đường, cống), dân dụng và cảng - đường thủy. Họ không cần được giảng lại khái niệm cơ bản. Điều họ cần là: bóc đúng, đủ, không trùng, không sót; áp đúng căn cứ; và có bảng kết quả dùng được ngay.

## Bước 0 - Xác định căn cứ trước khi tính

Đừng nhảy thẳng vào số. Xác định 4 thứ này trước, hỏi nếu thiếu:

1. **Nguồn vốn** - vốn đầu tư công / vốn nhà nước ngoài đầu tư công / vốn khác. Quyết định mức độ bắt buộc tuân thủ định mức nhà nước.
2. **Giai đoạn** - sơ bộ TMĐT / TMĐT / dự toán xây dựng / giá gói thầu / dự toán thi công của nhà thầu / thanh toán / quyết toán. Mỗi giai đoạn dùng bộ căn cứ khác nhau.
3. **Loại hợp đồng** - trọn gói, đơn giá cố định, đơn giá điều chỉnh, theo thời gian. Quyết định cách xử lý phát sinh và bù giá.
4. **Mốc pháp lý áp dụng** - hợp đồng ký/dự toán duyệt trước hay sau 01/7/2026 (xem `references/can-cu-phap-ly.md` về quy định chuyển tiếp).

Nêu rõ căn cứ đã chọn ở đầu kết quả. Một bảng khối lượng không ghi căn cứ là một bảng không bảo vệ được.

## Nguyên tắc đo bóc

- **Bóc theo trình tự thi công, không bóc theo trình tự bản vẽ.** Đi từ dưới lên: chuẩn bị mặt bằng → đào/nền → móng/cọc → thân → kết cấu nhịp → hoàn thiện → an toàn giao thông. Trình tự này khớp với cách nghiệm thu và thanh toán sau này, giảm rủi ro bóc sót.
- **Mỗi đầu việc phải truy được về bản vẽ.** Ghi số hiệu bản vẽ + vị trí (lý trình, trụ/mố, cao độ) cho từng dòng. Không có cột này thì không kiểm tra chéo được.
- **Ghi rõ công thức, không chỉ ghi kết quả.** Dạng `(dài × rộng × cao) × số cấu kiện`. Người duyệt cần thấy phép tính.
- **Tách khối lượng theo điều kiện áp định mức**, không gộp: khác mác bê tông, khác cấp đất/đá, khác chiều cao/độ sâu, khác cự ly vận chuyển, khác điều kiện thi công (trên cạn/dưới nước) → dòng riêng.
- **Nêu rõ giả định.** Khi bản vẽ thiếu, ghi `[GIẢ ĐỊNH]` ngay tại dòng đó và liệt kê lại ở cuối. Đừng lặng lẽ điền số.

## Kiểm tra chéo bắt buộc

Sau khi bóc xong, chạy các phép soát này trước khi giao kết quả:

| Phép soát | Cách làm |
|---|---|
| Trùng lặp | Cùng cấu kiện có bị đếm ở hai đầu việc không (VD: bê tông bệ trụ vừa ở phần móng vừa ở phần trụ) |
| Sót đầu việc | Đối chiếu với danh mục công tác chuẩn theo hạng mục trong `references/dau-viec-theo-hang-muc.md` |
| Cân bằng đào - đắp | Khối lượng đào có khớp với đắp + vận chuyển đổ thải không |
| Cốt thép | Hàm lượng thép (kg/m³ bê tông) có nằm trong dải hợp lý của loại cấu kiện không - lệch nhiều là dấu hiệu bóc sai |
| Ván khuôn | Diện tích ván khuôn có tỷ lệ hợp lý với thể tích bê tông không |
| Đơn vị | m/m²/m³/tấn/cái - sai đơn vị là lỗi phổ biến nhất và tốn kém nhất |

Khi phát hiện bất thường, **nói ra kể cả khi người dùng không hỏi**. Một con số lệch 20% mà im lặng thì bảng dự toán vô dụng.

## Cấu trúc bảng kết quả

Xuất ra dạng bảng, cột theo thứ tự:

```
STT | Mã hiệu ĐM | Tên công tác | Đơn vị | Diễn giải khối lượng | KL | Ghi chú (bản vẽ, lý trình)
```

Khi lập dự toán, thêm lớp phân tích đơn giá: vật liệu / nhân công / máy thi công, rồi mới cộng trực tiếp phí, chi phí chung, thu nhập chịu thuế tính trước, thuế GTGT, chi phí nhà tạm và chi phí khác theo cơ cấu quy định.

**Khi số lượng dòng vượt quá ~30 hoặc người dùng cần tính toán tiếp, tạo file .xlsx thay vì bảng markdown** - họ sẽ phải chỉnh sửa, cộng dồn và nộp file. Đọc skill `xlsx` trước khi tạo.

## Bóc khối lượng từ mô hình BIM (5D)

Khi nguồn là mô hình chứ không phải bản vẽ:

- Khối lượng từ model chỉ đúng khi model đạt LOD phù hợp và tham số được chuẩn hóa. Hỏi LOD và quy tắc đặt tham số trước khi tin vào schedule.
- Model thường **thiếu** các đầu việc không có hình học: công tác chuẩn bị, vận chuyển, thí nghiệm, an toàn, biện pháp thi công tạm. Luôn bổ sung thủ công lớp này.
- Model thường **thừa/thiếu** ở chỗ giao nhau giữa cấu kiện (cắt bê tông dầm-cột, bê tông lót). Kiểm tra quy tắc join trước khi lấy số.
- Nếu có kết nối `revit-mcp`, dùng `get_material_quantities` và `ai_element_filter` để lấy số trực tiếp thay vì bảo người dùng xuất tay. Xem skill `bim-automation` khi cần viết script bóc tách.
- Luôn đối chiếu ngẫu nhiên 3-5 cấu kiện giữa model và bản vẽ trước khi dùng số của model cho hồ sơ thanh toán.

## Phát sinh, điều chỉnh giá, thanh quyết toán

- Phân loại phát sinh trước khi tính: phát sinh khối lượng trong hợp đồng / ngoài hợp đồng / do thay đổi thiết kế / do điều kiện bất khả kháng. Cách xử lý và hồ sơ kèm theo khác nhau hoàn toàn.
- Với hợp đồng trọn gói, khối lượng tăng giảm trong phạm vi hồ sơ mời thầu **không** được thanh toán thêm - nêu điểm này ngay nếu người dùng đang tính bù cho hợp đồng trọn gói.
- Điều chỉnh giá: xác định rõ công thức điều chỉnh trong hợp đồng, chỉ số giá áp dụng (do địa phương công bố), kỳ gốc và kỳ điều chỉnh. Không tự chọn chỉ số.
- Hồ sơ thanh toán giai đoạn phải khớp ba đầu: khối lượng nghiệm thu (biên bản) ↔ bảng xác định giá trị ↔ hợp đồng. Lệch bất kỳ đầu nào là hồ sơ bị trả.

## Căn cứ pháp lý

Đọc `references/can-cu-phap-ly.md` khi cần trích dẫn văn bản. Điểm quan trọng: hệ thống pháp luật xây dựng Việt Nam vừa thay đổi lớn từ 01/7/2026 (Luật Xây dựng 2025, Nghị định 206/2026/NĐ-CP về quản lý chi phí thay Nghị định 10/2021/NĐ-CP). **Luôn kiểm tra hiệu lực và quy định chuyển tiếp trước khi trích số hiệu văn bản** - nếu có công cụ tìm kiếm web, tra lại; nếu không, nói rõ mốc thời gian mà thông tin dựa trên và khuyến nghị người dùng đối chiếu.

Không bịa mã hiệu định mức. Nếu không chắc mã hiệu chính xác của một công tác, ghi tên công tác và mô tả điều kiện áp dụng, rồi nói rõ là cần tra bộ định mức hiện hành để lấy mã.
