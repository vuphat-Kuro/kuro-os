---
name: "BIM - Quản lý dự án"
description: "Quản lý BIM dự án: BEP, EIR, ISO 19650, LOD/LOI, CDE (ACC/BIM 360), phối hợp bộ môn, kiểm tra xung đột, duyệt mô hình."
group: Xây dựng
source: vnp-hatang-bim (skill Claude của chủ brain, nhập 2026-10-09)
---

# Quản lý BIM cấp dự án

## Khi nào dùng

Quản lý BIM cấp dự án - lập kế hoạch triển khai BIM (BEP/BIM Execution Plan), yêu cầu thông tin của chủ đầu tư (EIR), quy ước đặt tên và phân loại theo ISO 19650, xác định LOD/LOI cho từng giai đoạn, tổ chức môi trường dữ liệu chung (CDE) trên ACC/BIM 360/Trimble Connect, quy trình phối hợp đa bộ môn và kiểm tra xung đột (clash detection), quy trình duyệt và phát hành mô hình, kiểm tra chất lượng mô hình, đối chiếu mô hình với hiện trường. Dùng skill này khi người dùng nhắc tới BEP, EIR, ISO 19650, LOD, CDE, ACC, BIM 360, Navisworks, clash, phối hợp bộ môn, quy trình BIM, tiêu chuẩn đặt tên file, hoặc hỏi "triển khai BIM cho dự án này thế nào", "quản lý mô hình giữa các bộ môn ra sao", "làm sao để mô hình dùng được ngoài công trường".

Người dùng vừa dựng mô hình vừa quản lý BIM cho dự án hạ tầng giao thông, và đang xây dựng nền tảng số quản lý thi công. Trọng tâm của skill này không phải công cụ, mà là **làm sao mô hình thực sự phục vụ thi công thay vì chỉ để trình bày**.

## Nguyên tắc chi phối: mô hình phải trả lời được câu hỏi của ai đó

Mọi quyết định về LOD, tham số, quy ước đặt tên đều phải truy về một câu hỏi cụ thể mà ai đó sẽ hỏi. Nếu không ai hỏi, đừng mô hình hóa.

Khi người dùng đề nghị lập BEP hoặc chuẩn hóa quy trình, bắt đầu bằng việc liệt kê **các mục đích sử dụng mô hình (BIM uses)** cho dự án đó, rồi mới suy ngược ra yêu cầu. Danh sách mục đích thường gặp trong hạ tầng giao thông:

- Trình bày và lấy ý kiến phương án
- Kiểm tra xung đột đa bộ môn trước khi thi công
- Bóc tách khối lượng phục vụ dự toán hoặc thanh toán (5D)
- Mô phỏng và kiểm tra tính khả thi biện pháp thi công
- Lập và theo dõi tiến độ (4D)
- Trích xuất bản vẽ thi công
- Quản lý dữ liệu tài sản bàn giao cho giai đoạn khai thác
- Đối chiếu mô hình - hiện trường phục vụ nghiệm thu

Mỗi mục đích kéo theo yêu cầu khác nhau về LOD, LOI và tham số. Một mô hình phục vụ trình bày mà bị ép dùng để bóc khối lượng thanh toán là nguồn tranh chấp.

## Cấu trúc BEP

```
1. Thông tin dự án và các bên tham gia
2. Mục tiêu và mục đích sử dụng BIM (BIM uses) - gắn với lợi ích cụ thể
3. Vai trò, trách nhiệm và nhân sự BIM của từng bên
4. Chiến lược phân chia mô hình (theo bộ môn, theo phân đoạn tuyến, theo lý trình)
5. Cấp độ thông tin: LOD/LOI theo giai đoạn và theo loại cấu kiện
6. Quy ước đặt tên, phân loại, hệ tọa độ và cao độ chuẩn
7. Phần mềm, phiên bản, định dạng trao đổi (bao gồm IFC và phiên bản MVD)
8. Môi trường dữ liệu chung: cấu trúc thư mục, trạng thái tài liệu, quy trình duyệt
9. Quy trình phối hợp: tần suất họp, chu kỳ nộp mô hình, quy trình xử lý xung đột
10. Quy trình kiểm tra chất lượng mô hình và tiêu chí chấp nhận
11. Sản phẩm bàn giao theo từng mốc
12. Hạ tầng kỹ thuật, phân quyền, sao lưu
```

Với dự án theo ISO 19650, bổ sung: EIR làm đầu vào, phân biệt BEP trước khi trúng thầu và BEP sau khi trúng thầu, ma trận trách nhiệm cung cấp thông tin, và lịch trình cung cấp thông tin (MIDP/TIDP).

Với văn bản BEP đầy đủ, tạo file .docx (đọc skill `docx` trước).

## LOD - quy tắc thực dụng

Đừng để LOD trở thành cuộc tranh luận học thuật. Định nghĩa theo cách kiểm tra được:

| Cấp | Nghĩa thực dụng | Dùng để |
|---|---|---|
| 200 | Hình dạng và vị trí gần đúng, kích thước tương đối | Phương án, so sánh, phối hợp sơ bộ |
| 300 | Hình học chính xác theo thiết kế, đúng vị trí và cao độ | Xuất bản vẽ, kiểm tra xung đột, bóc khối lượng chính |
| 350 | Bổ sung chi tiết liên kết và giao diện với bộ môn khác | Phối hợp thi công, kiểm tra không gian lắp đặt |
| 400 | Đủ chi tiết để chế tạo và thi công, gồm cốt thép, mối nối, dung sai | Chế tạo, gia công, biện pháp thi công chi tiết |
| 500 | Trạng thái hoàn công đã được kiểm chứng ngoài hiện trường | Bàn giao, quản lý tài sản |

Quan trọng hơn cấp số là **LOI - thông tin phi hình học**. Một cấu kiện LOD 300 mang đủ tham số mã công tác, mác bê tông, hạng mục, phân đoạn thi công thì hữu dụng hơn nhiều một cấu kiện LOD 400 trống rỗng tham số. Khi lập BEP, dành công sức cho bảng tham số bắt buộc nhiều hơn cho tranh luận về LOD.

Lập bảng LOD theo **từng nhóm cấu kiện × từng giai đoạn**, không đặt một con số chung cho cả dự án.

## Quy ước đặt tên

Nguyên tắc: tên phải **máy đọc được** (phân tách bằng dấu, các trường có độ dài và tập giá trị xác định) và **người đọc hiểu ngay**. Cấu trúc theo ISO 19650 thường gồm các trường: dự án - bên tham gia - phân khu/hệ thống - cao độ/vị trí - loại tài liệu - bộ môn - số hiệu, kèm mã trạng thái và số hiệu phiên bản.

Với hạ tầng tuyến, bổ sung trường **phân đoạn theo lý trình** - đây là trường quan trọng nhất trong dự án đường và cầu, và hay bị bỏ sót vì các mẫu chuẩn được viết cho công trình nhà.

Khi người dùng nhờ lập quy ước, luôn kèm theo:
- Bảng mã cho từng trường với danh mục giá trị đóng
- 3-5 ví dụ tên đầy đủ
- Ví dụ về tên **sai** và lý do sai - phần này giúp người thực hiện hơn cả bảng mã

## Hệ tọa độ và cao độ - nguồn sự cố âm thầm

Trong dự án hạ tầng, sai lệch hệ tọa độ giữa các bộ môn là lỗi tốn kém và khó phát hiện nhất. Luôn quy định rõ trong BEP:

- Hệ tọa độ quốc gia sử dụng và múi chiếu
- Điểm gốc dự án và cách thiết lập trên từng phần mềm (Revit shared coordinates, Civil 3D, Tekla)
- Cao độ chuẩn và mốc dẫn
- Quy trình kiểm tra: mọi mô hình nộp lên phải qua bước kiểm tra chồng khớp với mô hình tham chiếu

Với mô hình lớn theo tuyến, cân nhắc chia theo phân đoạn có gốc tọa độ cục bộ, nhưng phải có quy trình quy đổi rõ ràng.

## Kiểm tra xung đột

- Chia **ma trận kiểm tra xung đột** theo cặp bộ môn, không chạy tất cả với tất cả. Mỗi cặp có dung sai riêng.
- Phân loại xung đột theo mức: nghiêm trọng (phải sửa thiết kế) - trung bình (xử lý bằng biện pháp thi công) - nhẹ/nhiễu (bỏ qua có ghi nhận). Nếu không phân loại, danh sách 4000 xung đột trở nên vô dụng.
- Xung đột với **kết cấu phụ trợ và không gian thao tác** là loại có giá trị cao nhất trong thi công nhưng ít được kiểm tra: đà giáo, cẩu, xe đúc, đường vận chuyển, không gian bảo dưỡng.
- Mỗi xung đột phải có: mã, vị trí, bộ môn liên quan, người chịu trách nhiệm xử lý, hạn xử lý, trạng thái. Theo dõi bằng bảng, không bằng ảnh chụp màn hình rời rạc.
- Đóng vòng lặp: xung đột chỉ được đóng khi mô hình cập nhật đã nộp lại và kiểm tra lại đạt.

## Môi trường dữ liệu chung (CDE)

Bốn trạng thái tài liệu cần được thực thi thật, không chỉ ghi trong BEP: đang thực hiện (WIP) - đã chia sẻ (Shared) - đã phát hành (Published) - lưu trữ (Archive). Quy định rõ ai được chuyển trạng thái nào.

Sai lầm phổ biến: dùng CDE như ổ cứng chung. Dấu hiệu nhận biết - có file tên kiểu "final_v3_moinhat". Khi thấy dấu hiệu này, vấn đề là quy trình duyệt chưa được thực thi, không phải vấn đề công cụ.

## Đối chiếu mô hình với hiện trường

Đây là chỗ BIM tạo giá trị trực tiếp cho công tác nghiệm thu, và cũng là thế mạnh của người dùng:

- Xuất bản vẽ và thông số kiểm tra từ mô hình cho đội hiện trường, kèm mã cấu kiện để ghi nhận ngược lại
- Ghi nhận sai lệch thực tế trở lại mô hình (as-built), không chỉ ghi trong hồ sơ giấy
- Dùng dữ liệu đo đạc (máy toàn đạc, quét laser, ảnh chụp bằng thiết bị bay) để kiểm tra hình học ở các mốc quan trọng
- Liên kết trạng thái thi công của cấu kiện trong mô hình với biên bản nghiệm thu tương ứng - xem skill `qc-nghiem-thu-ho-so` và `tien-do-san-luong`

Khung pháp lý hiện hành đã có quy định riêng về **ứng dụng công nghệ thông tin và mô hình thông tin công trình (BIM) trong quản lý thi công** trong Nghị định 207/2026/NĐ-CP (hiệu lực 01/7/2026, thay Nghị định 06/2021/NĐ-CP). Đây là căn cứ hữu ích khi cần thuyết phục chủ đầu tư đưa quy trình BIM vào hệ thống quản lý chất lượng chính thức của dự án thay vì coi là hoạt động phụ trợ. Kiểm tra lại nội dung điều khoản cụ thể trước khi trích dẫn vào văn bản.

## Khi tư vấn triển khai, giữ tinh thần thực tế

Nhiều nỗ lực BIM thất bại không vì kỹ thuật mà vì áp quy trình quá nặng so với năng lực đội thực hiện. Khi đề xuất, hỏi về năng lực và số lượng nhân sự BIM thực có, rồi đề xuất theo lộ trình: làm tốt 2-3 mục đích sử dụng trước, mở rộng sau. Nói thẳng nếu kế hoạch người dùng đưa ra vượt quá nguồn lực họ mô tả.
