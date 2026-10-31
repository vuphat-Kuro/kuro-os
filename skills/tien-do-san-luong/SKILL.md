---
name: "Tiến độ & sản lượng"
description: "Lập, kiểm soát tiến độ: CPM, P6, MS Project, 4D/5D, huy động nhân lực - thiết bị, sản lượng, EVM, S-curve, bù tiến độ."
group: Xây dựng
source: vnp-hatang-bim (skill Claude của chủ brain, nhập 2026-10-09)
---

# Tiến độ, sản lượng và kiểm soát dự án

## Khi nào dùng

Lập và kiểm soát tiến độ thi công (CPM, đường găng, Primavera P6, MS Project), mô phỏng 4D và tích hợp khối lượng 5D, lập biểu đồ huy động nhân lực - thiết bị, báo cáo sản lượng và giá trị thực hiện, phân tích EVM (PV, EV, AC, CV, SV, CPI, SPI), phân tích chậm tiến độ và lập biện pháp bù tiến độ, báo cáo tiến độ ngày/tuần/tháng cho chủ đầu tư. Dùng skill này khi người dùng nhắc tới tiến độ, đường găng, P6, MS Project, Gantt, 4D, 5D, Fuzor, Navisworks Timeliner, sản lượng, EVM, CPI, SPI, S-curve, chậm tiến độ, bù tiến độ, báo cáo tuần/tháng, hoặc hỏi "dự án đang chậm bao nhiêu", "làm sao đuổi kịp", "lập kế hoạch thi công cho hạng mục này".

Người dùng lập tiến độ trên P6 và MS Project, mô phỏng 4D trên Fuzor và Navisworks, và đã dựng dashboard phân tích EVM. Viết ở trình độ đó. Giá trị skill này mang lại là **cấu trúc đúng ngay từ đầu** và **phân tích trung thực khi số liệu xấu**.

## Lập tiến độ

### Cấu trúc trước, thời gian sau

Thứ tự làm việc đúng: WBS → danh mục công việc → khối lượng → năng suất → thời gian → quan hệ logic → tài nguyên → đường găng. Nhảy thẳng vào việc gõ ngày tháng là cách tạo ra tiến độ không bảo vệ được.

- **WBS** cho hạ tầng tuyến nên phân theo: hạng mục → phân đoạn lý trình / công trình đơn lẻ → hạng mục con → công tác. Phân đoạn theo lý trình là trục tổ chức tự nhiên của dự án đường và cầu.
- **Thời lượng công việc** phải suy ra từ khối lượng ÷ năng suất tổ đội, không phải ước lượng cảm tính. Ghi rõ năng suất giả định trong ghi chú của công việc - khi tiến độ bị chất vấn, đây là thứ được hỏi đầu tiên.
- **Quan hệ logic** ưu tiên FS. Dùng SS/FF với lag chỉ khi thực sự phản ánh công nghệ thi công. Lag âm và constraint cứng là hai thứ làm hỏng đường găng - dùng càng ít càng tốt và phải giải thích được từng cái.
- Với công tác chờ đợi có tính công nghệ (bảo dưỡng bê tông, chờ cường độ căng kéo, chờ cố kết nền đất yếu), tạo công việc riêng chứ đừng gộp vào lag. Chúng phải nhìn thấy được trên biểu đồ.

### Ràng buộc đặc thù hạ tầng giao thông

Đưa vào tiến độ ngay từ đầu, đừng để phát hiện sau:

- Mùa mưa lũ, mực nước theo mùa với thi công dưới nước
- Thời gian bàn giao mặt bằng theo từng đoạn - thường là nguyên nhân chậm số một
- Thời gian chờ cố kết nền đất yếu (có thể hàng tháng, nằm trên đường găng)
- Thời gian chờ phê duyệt biện pháp thi công và thí nghiệm
- Cửa sổ được phép phong tỏa giao thông
- Thời gian chế tạo và vận chuyển cấu kiện đúc sẵn, thiết bị nhập khẩu
- Mốc kiểm tra công tác nghiệm thu của cơ quan chuyên môn

### Kiểm tra chất lượng tiến độ

Trước khi giao, soát: công việc không có quan hệ trước hoặc sau (dangling), constraint cứng không lý do, thời lượng bất thường (quá dài hoặc bằng 0 không phải mốc), đường găng có đi qua các hạng mục thực sự quyết định không, tổng thời lượng có khớp mốc hợp đồng không, và biểu đồ huy động nhân lực - thiết bị có bị đột biến vô lý không.

## 4D và 5D

- 4D chỉ hữu ích khi **cấu kiện trong mô hình được gán vào đúng công việc tiến độ**. Việc này đòi hỏi mô hình có tham số phân đoạn thi công khớp với WBS. Nếu chưa có, đó là việc phải làm trước - xem skill `bim-quan-ly-du-an`.
- Quy tắc gán: một công việc tiến độ ↔ một nhóm cấu kiện xác định được bằng bộ lọc tham số, không gán thủ công từng cái. Gán thủ công không sống nổi qua lần cập nhật tiến độ thứ hai.
- Đưa **kết cấu phụ trợ và thiết bị** vào mô hình 4D (đà giáo, cẩu, xe đúc, đường công vụ). Đây là chỗ mô phỏng 4D phát hiện ra vấn đề thật: xung đột không gian theo thời gian, đường vận chuyển bị chặn, thiết bị không đủ chỗ xoay.
- 5D: liên kết khối lượng và đơn giá với tiến độ để sinh đường cong dòng tiền và kế hoạch giải ngân. Độ tin cậy phụ thuộc chất lượng dữ liệu khối lượng trong mô hình - xem skill `qs-khoi-luong-du-toan`.

## Báo cáo sản lượng và EVM

### Ba đại lượng gốc

| Ký hiệu | Nghĩa | Nguồn số liệu |
|---|---|---|
| PV | Giá trị kế hoạch - giá trị công việc đáng lẽ hoàn thành đến kỳ báo cáo | Tiến độ cơ sở × đơn giá |
| EV | Giá trị thực hiện - giá trị công việc **thực sự** hoàn thành | Khối lượng nghiệm thu × đơn giá hợp đồng |
| AC | Chi phí thực tế đã bỏ ra | Kế toán, không phải ước tính |

Điểm mấu chốt và hay bị làm sai: **EV phải dựa trên khối lượng đã nghiệm thu, không dựa trên phần trăm hoàn thành do đội thi công tự đánh giá**. Phần trăm tự đánh giá luôn lạc quan, và EVM tính từ số liệu đó không phát hiện được vấn đề - đúng lúc cần nó nhất.

### Chỉ số

- CV = EV − AC. Âm là vượt chi phí.
- SV = EV − PV. Âm là chậm tiến độ (tính theo giá trị).
- CPI = EV / AC. Dưới 1 là kém hiệu quả chi phí.
- SPI = EV / PV. Dưới 1 là chậm.
- EAC ước tính chi phí khi hoàn thành: cách thận trọng là BAC / CPI khi xu hướng hiện tại được cho là tiếp diễn.

Hai lưu ý khi diễn giải:

1. **SPI mất ý nghĩa về cuối dự án** - nó tiến về 1 khi các công việc dần hoàn thành kể cả khi dự án chậm nặng. Về cuối, dùng phân tích đường găng và dự báo ngày hoàn thành, không dùng SPI.
2. **SPI theo giá trị không nói được công việc chậm nằm ở đâu.** Một dự án có SPI = 1,0 vẫn có thể sắp vỡ tiến độ nếu phần chậm nằm trên đường găng còn phần vượt nằm ở hạng mục không găng. Luôn xem SPI cùng với trạng thái đường găng.

### Báo cáo trung thực

Khi số liệu xấu, nói rõ. Vai trò hữu ích nhất ở đây là chỉ ra vấn đề sớm, không phải trình bày số liệu sao cho dễ chịu. Nếu người dùng đưa số liệu cho thấy dự án đang chậm hoặc vượt chi phí, nêu ra kể cả khi họ chỉ nhờ định dạng bảng biểu.

## Phân tích chậm tiến độ

Khi dự án chậm, đi theo trình tự:

1. **Chậm ở đâu** - so sánh tiến độ hiện tại với tiến độ cơ sở, xác định công việc trễ và công việc trên đường găng đã thay đổi.
2. **Đường găng có đổi không** - thường có. Đường găng mới quyết định biện pháp bù, không phải đường găng cũ.
3. **Nguyên nhân và trách nhiệm** - phân loại: do nhà thầu / do chủ đầu tư (mặt bằng, thay đổi thiết kế, chậm phê duyệt) / do bất khả kháng. Phân loại này quyết định quyền được gia hạn thời gian và quyền được bồi thường chi phí - hai thứ khác nhau, đừng gộp.
4. **Lưu hồ sơ ngay** - thông báo, nhật ký, ảnh, biên bản hiện trường theo mốc thời gian. Khiếu nại gia hạn thắng hay thua phụ thuộc hồ sơ được lập tại thời điểm phát sinh, không phải lập lại sau này.
5. **Biện pháp bù** - tăng ca, tăng mũi thi công, thay đổi công nghệ, chồng lấn công việc (fast-tracking), rút ngắn bằng tăng nguồn lực (crashing). Với mỗi biện pháp, nêu chi phí tăng thêm và rủi ro chất lượng - an toàn kèm theo. Chồng lấn công việc luôn tăng rủi ro làm lại.

## Định dạng kết quả

- Báo cáo ngày/tuần gửi nhóm: viết thẳng trong hội thoại, ngắn gọn, dạng đã làm - sẽ làm - vướng mắc - đề xuất.
- Báo cáo tháng cho chủ đầu tư: tạo file .docx hoặc .xlsx (đọc skill tương ứng trước).
- Bảng theo dõi sản lượng, EVM, khối lượng: tạo .xlsx - người dùng sẽ phải cập nhật hàng kỳ, đừng đưa bảng markdown.
- Biểu đồ S-curve, biểu đồ huy động: nêu rõ trục và nguồn số liệu; khi tạo trong Excel, dựng sẵn công thức để kỳ sau chỉ cần nhập số mới.
