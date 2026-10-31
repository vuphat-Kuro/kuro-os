---
name: "BIM - Tự động hoá"
description: "Viết, gỡ lỗi script BIM: Dynamo, Revit API, pyRevit, Tekla API, Grasshopper; tham số hoá, rải thép, bóc khối lượng từ model."
group: Xây dựng
source: vnp-hatang-bim (skill Claude của chủ brain, nhập 2026-10-09)
---

# Tự động hóa BIM

## Khi nào dùng

Viết và gỡ lỗi script tự động hóa BIM - Dynamo, Python/IronPython, Revit API (pyRevit, C#), Tekla Open API và Grasshopper-Tekla Live Link, đọc/ghi Excel từ mô hình, tham số hóa cấu kiện, rải cốt thép tự động, bóc tách khối lượng từ model, kiểm tra và chuẩn hóa dữ liệu tham số, đặt tên và phân loại đối tượng hàng loạt. Dùng skill này khi người dùng nhắc tới Dynamo, Revit API, Tekla API, Grasshopper, pyRevit, script, tự động hóa mô hình, tham số, shared parameter, schedule, hoặc nói "làm sao tự động cái này", "model 200 cấu kiện tay lâu quá", "lấy dữ liệu từ Revit ra Excel", "dựng dầm theo bảng thông số" - kể cả khi họ chỉ mô tả một tác vụ lặp trong mô hình. Cũng dùng khi cần điều khiển Revit hoặc AutoCAD qua kết nối MCP.

Người dùng làm R&D Tekla và Revit, đã tự viết thuật toán rải cốt thép 3D qua Grasshopper, tham số hóa dầm bản rỗng và dầm Super-T bằng Dynamo với dữ liệu từ Excel. Họ có nền tảng lập trình (Python, C#, web). Viết cho trình độ đó: đi thẳng vào giải pháp, không giải thích Dynamo là gì.

## Chọn công cụ trước khi viết code

Đây là quyết định quan trọng nhất và hay bị bỏ qua:

| Nhu cầu | Công cụ nên dùng |
|---|---|
| Tác vụ một lần, hình học đơn giản, người khác cũng phải chạy được | Dynamo graph |
| Logic phức tạp, nhiều điều kiện, xử lý dữ liệu | Python node trong Dynamo, hoặc pyRevit |
| Dùng lặp lại nhiều dự án, cần giao diện, cần tốc độ | pyRevit extension hoặc add-in C# |
| Hình học tham số phức tạp, biến hình theo tuyến | Grasshopper (Rhino.Inside.Revit) hoặc Grasshopper-Tekla Live Link |
| Kết cấu thép, cấu kiện chế tạo, cốt thép chi tiết | Tekla Open API (C#) hoặc Grasshopper-Tekla |
| Xử lý dữ liệu ngoài mô hình (kiểm tra, báo cáo, so sánh) | Python thuần đọc file xuất ra, hoặc IFC/ODBC |
| Điều khiển tương tác trong phiên làm việc hiện tại | MCP `revit-mcp` / `autocad-mcp` (xem bên dưới) |

Nếu người dùng chưa nói rõ tần suất sử dụng và ai sẽ chạy script, hỏi - nó quyết định hoàn toàn kiến trúc giải pháp.

## Dùng kết nối MCP khi có

Người dùng có kết nối `revit-mcp` và `autocad-mcp`. Các công cụ này bị hoãn nạp, nên **gọi `tool_search` trước để nạp định nghĩa và lấy đúng tên tham số** - đừng đoán schema.

Với `revit-mcp`, các nhóm việc hay dùng:
- Truy vấn: `ai_element_filter`, `get_current_view_elements`, `get_selected_elements`, `get_available_family_types`, `get_current_view_info`
- Thống kê: `analyze_model_statistics`, `get_material_quantities`, `export_room_data`
- Tạo đối tượng: `create_level`, `create_grid`, `create_line_based_element`, `create_point_based_element`, `create_surface_based_element`, `create_structural_framing_system`, `create_room`
- Thao tác: `operate_element`, `color_elements`, `delete_element`, `tag_all_rooms`, `tag_all_walls`
- Tùy biến: `send_code_to_revit` để chạy C# trực tiếp khi không có công cụ sẵn

**Nguyên tắc an toàn khi thao tác trên mô hình thật:**

1. Truy vấn trước, sửa sau. Luôn đếm và liệt kê đối tượng sẽ bị ảnh hưởng, báo cho người dùng, rồi mới thực hiện.
2. Trước bất kỳ thao tác nào tạo/sửa/xóa hàng loạt, nhắc người dùng lưu bản sao mô hình. Undo trong Revit không phải lúc nào cũng hoàn tác được thao tác từ API.
3. Với `delete_element` hoặc bất kỳ thao tác không hoàn tác dễ dàng: nêu rõ danh sách đối tượng và **chờ người dùng xác nhận** trước khi gọi.
4. Chạy thử trên một vài đối tượng trước khi chạy trên toàn mô hình.
5. Với `send_code_to_revit`, đọc lại code cho người dùng trước khi gửi nếu code có thao tác ghi.

## Viết Dynamo

- Ưu tiên **danh sách và lacing** đúng ngay từ đầu; phần lớn lỗi Dynamo là lỗi cấu trúc list, không phải lỗi logic. Khi kết quả sai số lượng, kiểm tra `List.Flatten` / `List.Chop` / lacing trước tiên.
- Với Python node, ghi rõ phiên bản engine (IronPython 2.7 hay CPython3) vì cú pháp và thư viện khác nhau. Revit đời mới mặc định CPython3.
- Mẫu khung Python node trong Dynamo (giao dịch, lấy document, xuất kết quả) xem `references/mau-code.md`.
- Khi đọc dữ liệu từ Excel: đọc toàn bộ vùng một lần rồi xử lý trong bộ nhớ, không đọc từng ô. Ghi rõ giả định về chỉ số hàng/cột đầu tiên.
- Với graph người khác sẽ dùng, đặt tên node nhóm rõ ràng, gom input vào một nhóm ở đầu graph, và thêm node ghi chú nêu điều kiện đầu vào.

## Viết Revit API

- Mọi thao tác ghi phải nằm trong `Transaction`. Với thao tác hàng loạt, dùng một transaction cho cả lô thay vì mỗi phần tử một transaction - nhanh hơn nhiều lần.
- `FilteredElementCollector` với `WhereElementIsNotElementType()` và filter theo category; tránh lấy toàn bộ rồi lọc bằng vòng lặp Python.
- Đơn vị nội bộ của Revit là feet. Chuyển đổi bằng `UnitUtils`, không nhân hệ số thủ công - hệ số cứng là nguồn lỗi âm thầm.
- Bắt ngoại lệ theo từng phần tử và ghi log phần tử lỗi, thay vì để cả script dừng giữa chừng ở phần tử thứ 800.
- Khi cần tham số: phân biệt built-in parameter, project parameter, shared parameter, và family parameter. Chỉ shared parameter mới xuất được sang schedule và trao đổi được giữa các dự án.

## Viết Tekla Open API và Grasshopper

- Tekla Open API dùng C#; các lớp chính là `Model`, `ModelObject`, `Beam`, `ContourPlate`, `Rebar`/`RebarGroup`, `Assembly`. Sau khi thay đổi, gọi `CommitChanges()` - quên bước này là lỗi phổ biến nhất.
- Với rải cốt thép theo đường cong hoặc theo mặt biến đổi, Grasshopper thường gọn hơn viết API thuần: dựng đường dẫn trong Grasshopper, đẩy sang Tekla qua Live Link, giữ liên kết tham số để chỉnh sửa lại được.
- Với cấu kiện chế tạo, luôn kiểm tra `Assembly` và đánh số (numbering) sau khi tạo hàng loạt - bản vẽ chế tạo phụ thuộc vào việc này.
- Ghi rõ đơn vị: Tekla làm việc bằng mm ở API.

## Bóc tách khối lượng từ mô hình

Đây là ứng dụng có giá trị nhất và cũng dễ sai nhất. Xem thêm skill `qs-khoi-luong-du-toan` để biết yêu cầu về kết quả.

- Xuất theo **mã hiệu công tác**, không xuất theo category. Muốn vậy, phải có tham số phân loại công tác gắn trên cấu kiện - nếu chưa có, đó là việc đầu tiên phải làm.
- Tách theo điều kiện áp định mức: mác bê tông, cao độ, điều kiện thi công. Nếu mô hình không mang thông tin này, khối lượng xuất ra không dùng trực tiếp cho dự toán được - nói rõ điều đó thay vì xuất số cho xong.
- Kiểm tra quy tắc join giữa các cấu kiện trước khi tin vào thể tích.
- Luôn xuất kèm cột định danh phần tử (ElementId / GUID) để đối chiếu ngược lại mô hình khi có tranh chấp số liệu.

## Kiểm tra và chuẩn hóa dữ liệu mô hình

Loại script có giá trị lâu dài nhất, và người dùng nên có sẵn bộ này cho mọi dự án:

- Phát hiện tham số bắt buộc bị trống
- Phát hiện giá trị không thuộc danh mục cho phép (mác bê tông lạ, tên hạng mục sai chính tả)
- Phát hiện cấu kiện trùng vị trí, cấu kiện mồ côi, cấu kiện nằm ngoài phạm vi dự án
- Kiểm tra quy tắc đặt tên theo quy ước dự án
- Kiểm tra worksets, phase, và view template được gán đúng
- Xuất báo cáo dạng bảng kèm ElementId để người dùng nhảy thẳng tới đối tượng lỗi

Khi viết loại script này, luôn tách phần **phát hiện** và phần **sửa**. Chạy phát hiện, cho người dùng xem báo cáo, rồi mới hỏi có sửa tự động không.

## Chất lượng code

Script BIM thường được viết vội rồi dùng nhiều năm. Vì vậy:

- Đặt toàn bộ tham số cấu hình (tên tham số, đường dẫn, ngưỡng) lên đầu file thành hằng số, không rải rác trong code.
- In ra số lượng đối tượng xử lý thành công / bỏ qua / lỗi ở cuối mỗi lần chạy.
- Với script sửa đổi mô hình, thêm chế độ chạy thử chỉ in ra dự kiến thay đổi mà không ghi.
- Ghi chú tiếng Việt trong code là hợp lý vì người dùng và đồng nghiệp đọc - nhưng tên biến để tiếng Anh không dấu.
