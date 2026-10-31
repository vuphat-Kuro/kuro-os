---
name: "QC - Nghiệm thu & hồ sơ chất lượng"
description: "Lập, kiểm soát hồ sơ chất lượng: biên bản nghiệm thu, ITP, checklist công đoạn, nhật ký thi công, NCR, hồ sơ hoàn công."
group: Xây dựng
source: vnp-hatang-bim (skill Claude của chủ brain, nhập 2026-10-09)
---

# Hồ sơ nghiệm thu & kiểm soát chất lượng (QA/QC)

## Khi nào dùng

Lập và kiểm soát hồ sơ chất lượng thi công - biên bản nghiệm thu công việc, nghiệm thu giai đoạn/chuyển bước, nghiệm thu hoàn thành, nhật ký thi công, kế hoạch kiểm tra thí nghiệm (ITP), checklist nghiệm thu theo từng công đoạn, hồ sơ hoàn thành công trình, xử lý sai sót chất lượng và không phù hợp. Dùng skill này khi người dùng nhắc tới nghiệm thu, biên bản, hồ sơ chất lượng, hồ sơ hoàn công, ITP, checklist, nhật ký thi công, thí nghiệm vật liệu, chứng chỉ chất lượng, NCR, hoặc hỏi "cần những gì để nghiệm thu phần này", "công đoạn này kiểm tra cái gì", "hồ sơ thanh toán bị trả vì thiếu gì" - kể cả khi họ chỉ mô tả một công tác thi công và hỏi cần chuẩn bị gì.

Người dùng làm cả kỹ thuật hiện trường lẫn QC/QA cho công trình giao thông, dân dụng và cảng. Họ biết thi công. Cái họ cần từ skill này là: bộ hồ sơ **đủ và đúng thứ tự**, không bị trả lại, và checklist kiểm tra bám sát công đoạn thật ngoài công trường.

## Nguyên tắc gốc: hồ sơ đi cùng công việc, không đi sau

Sai lầm đắt nhất trong quản lý chất lượng là làm xong rồi mới đi gom hồ sơ. Khi hỗ trợ người dùng, luôn đặt hồ sơ vào đúng thời điểm của nó:

- **Trước khi thi công** - thiết kế biện pháp được duyệt, vật liệu được chấp thuận (chứng chỉ xuất xưởng + kết quả thí nghiệm mẫu), thiết bị được kiểm định, nhân sự đủ điều kiện, mặt bằng được bàn giao, trắc địa định vị.
- **Trong khi thi công** - nhật ký thi công ghi theo ngày, biên bản kiểm tra công tác ẩn giấu (cốt thép, ván khuôn, nền móng - những thứ sau đó bị che lấp vĩnh viễn), phiếu thí nghiệm hiện trường, biên bản lấy mẫu.
- **Sau khi hoàn thành công việc** - biên bản nghiệm thu công việc xây dựng, bản vẽ hoàn công bộ phận, kết quả thí nghiệm mẫu đến tuổi.

Nếu người dùng đang xin hồ sơ cho một công việc **đã thi công xong** mà thiếu bước ẩn giấu, nói thẳng rằng phần đó không hợp thức hóa được bằng giấy tờ - phải xử lý bằng kiểm định hoặc thí nghiệm bổ sung. Không giúp dựng hồ sơ khống.

## Ba cấp nghiệm thu

| Cấp | Đối tượng | Ai ký | Điều kiện tiên quyết |
|---|---|---|---|
| Nghiệm thu công việc xây dựng | Từng công tác (cốt thép bệ trụ, đắp lớp K95 lớp 3, đổ bê tông đốt K5…) | Giám sát nhà thầu + Tư vấn giám sát (và đại diện CĐT nếu có thỏa thuận) | Vật liệu đã chấp thuận, công tác trước đã nghiệm thu |
| Nghiệm thu giai đoạn / chuyển bước thi công | Bộ phận, hạng mục, hoặc mốc chuyển bước quan trọng | CĐT + TVGS + nhà thầu (thiết kế nếu cần) | Toàn bộ công việc trong giai đoạn đã nghiệm thu |
| Nghiệm thu hoàn thành công trình / hạng mục | Toàn công trình hoặc hạng mục đưa vào khai thác | CĐT chủ trì, có kiểm tra công tác nghiệm thu của cơ quan chuyên môn về xây dựng với công trình thuộc diện phải kiểm tra | Hồ sơ hoàn thành đầy đủ, các điều kiện đưa vào khai thác được đáp ứng |

Với công trình giao thông cấp cao, việc kiểm tra công tác nghiệm thu của cơ quan chuyên môn là mốc gây chậm nhiều nhất. Khi lập kế hoạch, đưa mốc này vào sớm và liệt kê hồ sơ phải nộp kèm.

## Lập kế hoạch kiểm tra và thí nghiệm (ITP)

Đây là sản phẩm giá trị nhất mà skill này tạo ra. Cấu trúc bảng ITP:

```
STT | Công đoạn | Nội dung kiểm tra | Tiêu chí chấp nhận | Tần suất / mật độ lấy mẫu |
Phương pháp - tiêu chuẩn áp dụng | Hồ sơ sinh ra | Điểm dừng (H/W/R) | Trách nhiệm
```

Ký hiệu điểm kiểm soát:
- **H (Hold point)** - phải có xác nhận mới được thi công tiếp. Dùng cho công tác ẩn giấu và mốc chuyển bước.
- **W (Witness point)** - mời chứng kiến, nếu bên được mời không đến đúng hẹn thì vẫn được tiếp tục.
- **R (Review)** - chỉ xem xét hồ sơ.

Đặt H đúng chỗ là kỹ năng cốt lõi: đặt quá nhiều thì tắc tiến độ, đặt quá ít thì mất kiểm soát. Quy tắc: đặt H ở mọi điểm mà sau đó **không kiểm tra lại được** hoặc **sửa chữa tốn kém bất thường**.

Xem `references/itp-mau-theo-cong-tac.md` cho các bộ ITP khởi điểm theo từng loại công tác (bê tông, cốt thép, cọc khoan nhồi, nền đường, cấp phối đá dăm, bê tông nhựa, dầm DƯL, nạo vét - kết cấu bến).

## Checklist nghiệm thu hiện trường

Khi người dùng cần checklist cho một công tác cụ thể, viết theo cách một kỹ sư thật dùng được: từng dòng là một thứ **quan sát hoặc đo được**, có trị số hoặc dung sai, không phải khẩu hiệu.

Kém: "Kiểm tra cốt thép đúng thiết kế."
Được: "Đường kính, số lượng thanh chủ đúng bản vẽ số …; khoảng cách đai đo tại 3 vị trí, sai lệch ≤ … mm; chiều dày lớp bê tông bảo vệ đo bằng con kê tại tối thiểu 5 điểm; chiều dài nối buộc ≥ … lần đường kính; vệ sinh, không dính dầu mỡ, gỉ vẩy."

Khi không chắc con số dung sai cụ thể của một tiêu chuẩn, **ghi rõ vị trí cần tra và tên tiêu chuẩn thay vì đoán số**. Con số dung sai sai lệch trong checklist gây hậu quả trực tiếp ngoài công trường.

## Tiêu chuẩn kỹ thuật

Xem `references/tieu-chuan-thuong-dung.md` cho danh mục TCVN thường dùng theo loại công tác. Ba lưu ý:

1. Tiêu chuẩn được viện dẫn phải là **tiêu chuẩn nêu trong hồ sơ hợp đồng và chỉ dẫn kỹ thuật của dự án**, không phải tiêu chuẩn mới nhất. Hỏi chỉ dẫn kỹ thuật (specification) trước.
2. Với dự án vốn nước ngoài hoặc theo mẫu FIDIC, có thể áp dụng AASHTO, ASTM, BS, EN. Hỏi rõ.
3. Số hiệu và năm ban hành tiêu chuẩn thay đổi theo thời gian. Nếu có công cụ tìm kiếm, xác minh; nếu không, nói rõ cần đối chiếu.

## Căn cứ pháp lý

Khung quản lý chất lượng thi công đã thay đổi từ 01/7/2026: **Nghị định 207/2026/NĐ-CP** (ban hành 15/6/2026) thay thế Nghị định 06/2021/NĐ-CP, chi tiết hóa Luật Xây dựng số 135/2025/QH15. Một số điểm liên quan trực tiếp đến công việc hằng ngày:

- Bổ sung điều riêng về **ứng dụng công nghệ thông tin và mô hình thông tin công trình (BIM) trong quản lý thi công** - đây là căn cứ để đưa quy trình BIM vào hệ thống quản lý chất lượng của dự án, thay vì coi BIM là việc phụ trợ.
- **Tách riêng hồ sơ hoàn thành và điều kiện đưa công trình vào khai thác, sử dụng** - hai bộ yêu cầu khác nhau, đừng gộp.
- Siết điều kiện đưa vào sử dụng, trong đó có yêu cầu về giấy phép hoặc đăng ký môi trường.
- Bổ sung quy định về bàn giao công trình trong dự án khu đô thị và yêu cầu đồng bộ hạ tầng kỹ thuật, hạ tầng xã hội.

**Kiểm tra hiệu lực và quy định chuyển tiếp trước khi trích dẫn.** Hợp đồng ký trước 01/7/2026 có thể vẫn vận hành theo Nghị định 06/2021. Nếu có công cụ tìm kiếm web, tra lại số điều khoản cụ thể trước khi ghi vào văn bản chính thức - không trích số điều nếu chưa xác minh.

## Xử lý không phù hợp (NCR)

Khi người dùng mô tả một sai sót chất lượng đã xảy ra, đi theo trình tự này thay vì nhảy ngay vào giải pháp:

1. Mô tả hiện trạng đo đạc được (không phải cảm nhận), kèm ảnh và vị trí.
2. Đánh giá mức độ: có ảnh hưởng chịu lực / tuổi thọ / an toàn khai thác không.
3. Phân loại hướng xử lý: chấp nhận nguyên trạng có điều kiện - sửa chữa - làm lại - hoặc phải có ý kiến của đơn vị thiết kế.
4. Xác định ai có thẩm quyền quyết định ở mức đó. Nhà thầu không tự quyết định chấp nhận nguyên trạng cho khiếm khuyết ảnh hưởng chịu lực.
5. Ghi nhận biện pháp phòng ngừa tái diễn.

Với khiếm khuyết có thể ảnh hưởng an toàn chịu lực, luôn khuyến nghị kiểm định độc lập và ý kiến của thiết kế. Không đề xuất phương án sửa chữa kết cấu chịu lực như một kết luận kỹ thuật chắc chắn.
