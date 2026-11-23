# Gói tiện ích tùy chọn

Mỗi thư mục con là một gói (`goi.json` + skill + script). Gói đi cùng mã nguồn Kuro nhưng **không vào brain** cho tới khi
người dùng yêu cầu cài.

- Trong giao diện Kuro: mở **Cài đặt -> Plugins** để xem danh sách plugin tích hợp sẵn, cài/gỡ trên máy hoặc cài thêm từ gói plugin bên ngoài (`.zip` / `.kuro-plugin` / thư mục).
- Trong khung chat Kuro: nói "cài gói AutoCAD" hoặc "cài gói TextHub" (AI gọi tool `goi_tien_ich`). "Gỡ gói ..." để gỡ.
- Dòng lệnh: `.venv\Scripts\python server\goi.py list | cai autocad | go autocad`
- Cài = chép skill vào `brains/<brain>/.claude/skills/` và `pip install` thư viện còn thiếu (cần mạng nếu thiếu).
  Sau đó bản cài tự cập nhật theo mã nguồn mỗi lần Kuro khởi động.
- Skill chỉ được mở khi việc liên quan: mô tả trong `SKILL.md` nói rõ khi nào dùng.

## Thêm gói mới
`goi/<id>/goi.json` (`ten`, `mo_ta`, `skill`, `pip`, `import`, tùy chọn `phien_ban`, `kiem_tra`) và thư mục `goi/<id>/<skill>/SKILL.md`; tên thư mục
skill phải trùng giá trị `skill` trong `goi.json`. Nếu gói có cài đặt phần mềm riêng trên máy (như plugin AutoCAD), khai thêm `"kiem_tra": "scripts/<script>.py status"` để giao diện Plugins hiển thị trạng thái trên máy và nút Cài/Cập nhật/Gỡ.

## Gói hiện có
- `autocad`: vẽ và xuất DXF theo chuẩn PKTTC (chữ Unicode, cỡ chữ, layer và nét in, dim) + script kiểm DXF.
  Điểm chưa chốt cần anh Nghĩa xác nhận: `autocad-pkttc/references/quy-chuan.md`, mục 5.
- `texthub`: Convert Font to Unicode - Đổi chữ TCVN3/VNI sang Unicode trong AutoCAD (PKTTC TextHub v0.9.3), kèm plugin AutoCAD (`PKTTC.TextHub.bundle`), kho 361 font SHX/TTF, skill `texthub-cad` và công cụ `texthub_setup.py`.
