---
name: "Word hồ sơ tự động"
description: "Sinh hàng loạt văn bản Word từ Excel (biên bản nghiệm thu, phiếu, tờ trình), ghép tập, thay hàng loạt, trích bảng Word ra Excel."
group: Xây dựng
source: vnp-hatang-bim (skill Claude của chủ brain, nhập 2026-10-09)
---

# Sinh hồ sơ Word hàng loạt

## Khi nào dùng

Sinh hàng loạt văn bản Word từ dữ liệu Excel và xử lý file Word theo lô - biên bản nghiệm thu công việc, phiếu yêu cầu nghiệm thu, phiếu kiểm tra, tờ trình, công văn, phiếu giao việc; ghép nhiều biên bản thành một tập, tìm & thay hàng loạt khi đổi tên công trình, trích bảng trong Word ra Excel, đổi tên file theo bảng. Dùng skill này khi người dùng nhắc tới biên bản, mẫu biên bản, in hàng loạt, mail merge, trộn thư, điền mẫu, phiếu nghiệm thu, hồ sơ chất lượng, tập hồ sơ hoàn công - kể cả khi họ chỉ nói "mỗi công tác một biên bản mà có 200 công tác", "copy paste mãi mệt quá", "đổi tên công trình trong cả tập hồ sơ", "gộp mấy chục file Word này lại", "lấy bảng trong file Word ra Excel".

Công việc gốc: một mẫu biên bản, một danh sách công tác, cần ra hàng trăm bản
chỉ khác nhau vài dòng. Làm tay là copy-paste-sửa, sai một chỗ là sai cả tập.

## Cách hoạt động

Mẫu Word chứa chỗ trống dạng `{{Tên cột}}`. Excel chứa dữ liệu, mỗi dòng ra một
file. Chỗ trống đặt được ở thân văn bản, **trong ô bảng**, ở **header và footer**.

Word thường cắt `{{Ten}}` thành nhiều đoạn nhỏ khi gõ hoặc khi sửa chính tả -
công cụ đã xử lý việc này, nên không cần dặn người dùng gõ liền một mạch.

## Trình tự chuẩn - đừng bỏ bước 1 và 2

```
1. python docgen.py cho-trong --mau mau.docx        # mẫu có những chỗ trống nào
2. python docgen.py kiem-tra  --mau mau.docx --du-lieu ds.xlsx   # khớp chưa
3. python docgen.py tao --mau mau.docx --du-lieu ds.xlsx \
       --ra-thu-muc bien-ban/ --ten "BB-{{So hieu}}-{{Hang muc}}.docx" \
       --tu-dong 2                                  # chạy thử 2 bản trước
4. Mở 2 file đó ra xem. Đúng rồi mới bỏ --tu-dong chạy toàn bộ.
```

Bước 3 với `--tu-dong 2` là bước quan trọng nhất. Sinh 200 file sai định dạng
rồi mới phát hiện thì mất công gấp đôi.

## Trường tự sinh

Không cần cột trong Excel, dùng được ngay trong mẫu:

`{{STT tự động}}` · `{{Ngày}}` · `{{Tháng}}` · `{{Năm}}` · `{{Ngày tháng}}` ·
`{{Ngày tháng đầy đủ}}` (ra dạng "ngày 26 tháng tám năm 2026" đúng văn phong
hành chính).

## Định dạng số trong hồ sơ Việt Nam

Số tự động chuyển sang `1.234,56` - dấu chấm phân nhóm nghìn, dấu phẩy thập
phân. Đây là quy ước bắt buộc trong hồ sơ trình duyệt. Muốn giữ số thô thì
thêm `--giu-so-tho`.

Cột số hiệu văn bản (`01`, `02`) bị Excel đọc thành số 1, 2. Ép giữ dạng chữ
bằng `--cot-chu "So hieu"`.

## Các việc khác với file Word đã có

`scripts/docxkit.py`:

| Lệnh | Việc |
|---|---|
| `ghep` | Ghép nhiều .docx thành một tập, mỗi file một trang |
| `thay` | Tìm & thay hàng loạt, giữ định dạng - đổi tên công trình, tên chủ đầu tư trong cả tập hồ sơ |
| `lay-bang` | Trích mọi bảng trong Word ra Excel - lấy lại số liệu từ biên bản cũ |
| `lay-chu` | Trích toàn văn ra .txt để tìm kiếm, đối chiếu |
| `doi-ten` | Đổi tên hàng loạt theo bảng Excel, có chế độ `--thu` chạy thử |

Lệnh `thay` mặc định **ghi đè file gốc**. Luôn nhắc người dùng dùng
`--ra-thu-muc` để giữ bản gốc, trừ khi họ nói rõ là muốn ghi đè.

## Xuất PDF

Thêm `--pdf` vào lệnh `tao`. Cần LibreOffice (chạy được mọi hệ) hoặc Microsoft
Word kèm `pip install pywin32` trên Windows. Nếu không có cái nào, công cụ báo
rõ chứ không lặng lẽ bỏ qua.

Hồ sơ nộp thầu và trình duyệt thường yêu cầu PDF có chữ ký số - phần ký vẫn
phải làm ngoài, công cụ này chỉ lo phần sinh và chuyển đổi.

## Nối với việc khác

- Danh sách công tác lấy từ đâu? Từ bảng khối lượng đã làm sạch bằng skill
  `excel-tu-dong-hoa`, hoặc từ sổ công đoạn EBS.
- Nội dung biên bản gồm những hạng mục kiểm tra nào? Xem skill
  `qc-nghiem-thu-ho-so`.
- Sinh xong cần tải lên CDE? Kiểm tra tên file bằng skill `cde-dong-bo` trước,
  vì hồ sơ sai quy ước tên sẽ bị trả về.
- Làm cả chuỗi hằng tháng → `quy-trinh-hop-nhat`.

## Giới hạn cần nói thật

Công cụ này thay chỗ trống, không dựng bố cục. Mẫu Word phải do người dùng
làm sẵn đúng thể thức (Nghị định 30/2020 về công tác văn thư, hoặc mẫu của chủ
đầu tư). Nếu người dùng chưa có mẫu, việc cần làm trước là dựng mẫu - không
phải chạy script.
