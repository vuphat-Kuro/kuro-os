# Kiểm tra dữ liệu vào/ra của phần mềm: Midas, Plaxis, Geo5, Excel

Phần mềm chỉ tính đúng cái được mô hình hóa. Phần lớn sai sót đến từ dữ liệu vào và sơ đồ không khớp hiện trường, ít khi do phần mềm. Mục này giúp rà soát cả file mô hình lẫn báo cáo đầu ra mà người dùng đưa.

Khi chưa có file mô hình, chỉ có ảnh chụp hoặc bảng kết quả, nói rõ giới hạn: chỉ rà được kết quả, chưa rà được dữ liệu vào.

## 1. Kiểm tra chung cho mọi phần mềm

**Dữ liệu vào**
- Hệ đơn vị thống nhất, không lẫn kN với N, m với mm
- Vật liệu và tiết diện gán đúng cho đúng phần tử, đặc trưng tiết diện khớp với tiết diện thực tế
- Trọng lượng bản thân: có bật tự động hay nhập tay, tránh tính hai lần hoặc bỏ sót
- Điều kiện biên và liên kết: gối, khớp, ngàm, mối nối trượt có giống cấu tạo thực không; lò xo nền lấy từ đâu
- Chiều dài tính toán và giằng thực tế trong mô hình có khớp với thiết kế lắp dựng không
- Loại tải, vị trí, hướng, điểm đặt; tải gió và tải ngang có đúng hướng bất lợi không
- Hệ số tải và tổ hợp có khớp với nguồn đã ghi trong sổ nguồn không (Claude không tự đặt)
- Giai đoạn thi công trong mô hình có khớp với trình tự thực tế

**Kết quả đầu ra**
- Tổng phản lực thẳng đứng khớp với tổng tải đặt vào (kiểm tra cân bằng)
- Dạng biến dạng hợp lý về hình dáng và chiều, không có chuyển vị bất thường ở điểm nào
- Nội lực lớn nhất nằm ở vị trí hợp lý theo cảm nhận cơ học
- Không có cảnh báo chưa xử lý (mất ổn định, ma trận suy biến, hội tụ)
- Kết quả cuối cùng dùng đúng tổ hợp khống chế, không phải một tải đơn lẻ
- Đối chiếu với một phép tính thô độc lập (xem mục 4)

## 2. Midas Civil / Midas Gen

- Loại phần tử (dầm, giàn, tấm) phù hợp với cách làm việc thực của bộ phận
- Phần tử chỉ chịu kéo hoặc chỉ chịu nén, phần tử cáp, liên kết đàn hồi: dùng đúng loại
- Giai đoạn thi công (construction stage): kích hoạt, hủy kích hoạt phần tử, tải, điều kiện biên đúng thứ tự thực tế; chú ý giai đoạn tháo dỡ
- Phân tích phi tuyến hình học hoặc ổn định (bậc hai, mất ổn định tuyến tính) có được dùng khi cần, và có kèm độ lệch ban đầu nếu tiêu chuẩn yêu cầu; **yêu cầu cụ thể lấy từ nguồn**
- Hệ số chiều dài tính toán do phần mềm tự lấy: đối chiếu với giả định của người thiết kế
- Kiểm tra thiết kế tự động trong phần mềm: xác nhận tiêu chuẩn được chọn có phải tiêu chuẩn dự án dùng hay không. Module thép của phần mềm thường theo AISC, Eurocode hoặc TCVN 5575; với KCPT cầu thì TCVN 5575:2024 nằm ngoài phạm vi (xem `nguon-tieu-chuan.md` mục 3.1), kết quả code check chỉ dùng làm đối chiếu trừ khi được chấp thuận
- Tổ hợp tải trong mô hình phải là tổ hợp của hệ tiêu chuẩn đã chọn (ví dụ hệ số vượt tải cặp lớn / nhỏ của TCVN 11815 Bảng 5.12), không dùng tổ hợp tự sinh mặc định của phần mềm
- Phân bố tải bánh xe, thiết bị di động: đủ vị trí bất lợi hay chỉ một vị trí

## 3. Plaxis và Geo5 (nền, hố đào)

- Phạm vi mô hình đủ rộng, biên không ảnh hưởng đến kết quả
- Lưới phần tử mịn hơn ở vùng có gradient lớn (quanh tường, đáy hố, mũi cọc)
- Mô hình đất và các thông số: nguồn thông số từ hố khoan nào, thí nghiệm nào, có phù hợp với mô hình đã chọn
- Điều kiện thoát nước: thoát nước hay không thoát nước, ứng xử ngắn hạn hay dài hạn
- Điều kiện mực nước ngầm ở từng giai đoạn: đã hạ, đã bơm, đã dâng
- Giai đoạn đào - chống - bơm - đổ bịt đáy - tháo chống có khớp trình tự thực tế không
- Mô hình tường, thanh chống, neo: độ cứng, tiết diện, dự ứng lực ban đầu lấy từ nguồn nào
- Tải mặt và công trình lân cận: có mô hình chưa
- Hệ số an toàn tính bằng giảm cường độ (nếu dùng) **không mặc nhiên tương đương** hệ số ổn định tiêu chuẩn yêu cầu; đối chiếu với yêu cầu trong nguồn trước khi kết luận
- Báo cáo đầu ra: xuất theo từng giai đoạn, không chỉ giai đoạn cuối; nội lực lớn nhất của cả quá trình mới là giá trị khống chế
- Geo5 và các phần mềm tính bằng phương pháp giải tích: nêu rõ phương pháp mà từng mô-đun dùng và điều kiện áp dụng của nó

## 4. Excel và tính tay

- Đơn vị ghi tường minh ở từng cột; công thức không chứa hằng số ẩn
- Mỗi công thức có cột nguồn (xem `bang-tinh-excel.md`)
- Ô đầu vào tách khỏi ô công thức, khóa ô công thức
- Có kiểm tra tự động (tổng phản lực, đơn vị, giá trị âm bất thường)
- Không dán giá trị lên công thức, không có liên kết ngoài trỏ về file cũ
- Kiểm tra thô độc lập: tính nhanh bậc độ lớn (nội lực lớn nhất, tổng phản lực, độ võng gần đúng) và so với kết quả phần mềm; lệch nhiều thì tìm nguyên nhân trước khi dùng

## 5. Khi kết quả phần mềm và tính thô lệch nhau

Báo người dùng, không tự chọn bên nào đúng. Liệt kê các nguyên nhân có thể: đơn vị, điều kiện biên, tải bị thiếu hay tính hai lần, giai đoạn, thông số đất. Đề nghị kiểm tra từng nguyên nhân theo thứ tự dễ kiểm nhất.
