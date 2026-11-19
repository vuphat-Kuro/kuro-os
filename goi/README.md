# Gói tiện ích tùy chọn

Mỗi thư mục con là một gói (`goi.json` + skill + script). Gói đi cùng mã nguồn Kuro nhưng **không vào brain** cho tới khi
người dùng yêu cầu cài.

- Trong Kuro: nói "cài gói AutoCAD" (AI gọi tool `goi_tien_ich`). "Gỡ gói AutoCAD" để gỡ.
- Dòng lệnh: `.venv\Scripts\python server\goi.py list | cai autocad | go autocad`
- Cài = chép skill vào `brains/<brain>/.claude/skills/` và `pip install` thư viện còn thiếu (cần mạng nếu thiếu).
  Sau đó bản cài tự cập nhật theo mã nguồn mỗi lần Kuro khởi động.
- Skill chỉ được mở khi việc liên quan: mô tả trong `SKILL.md` nói rõ khi nào dùng.

## Thêm gói mới
`goi/<id>/goi.json` (`ten`, `mo_ta`, `skill`, `pip`, `import`) và thư mục `goi/<id>/<skill>/SKILL.md`; tên thư mục
skill phải trùng giá trị `skill` trong `goi.json`.

## Gói hiện có
- `autocad`: vẽ và xuất DXF theo chuẩn PKTTC (chữ Unicode, cỡ chữ, layer và nét in, dim) + script kiểm DXF.
  Điểm chưa chốt cần anh Nghĩa xác nhận: `autocad-pkttc/references/quy-chuan.md`, mục 5.
