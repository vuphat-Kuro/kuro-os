---
name: "Quy trình hồ sơ một lệnh"
description: "Gói chuỗi việc hồ sơ lặp hằng tuần/tháng thành một lệnh .yaml: gộp bảng, soát lỗi, sinh biên bản, xuất PDF, tải lên CDE."
group: Xây dựng
source: vnp-hatang-bim (skill Claude của chủ brain, nhập 2026-10-09)
---

# Gói chuỗi việc lặp lại thành một lệnh

## Khi nào dùng

Gói một chuỗi việc lặp lại hằng tuần/hằng tháng thành một lệnh duy nhất chạy được - ví dụ gộp bảng khối lượng các đội, soát lỗi, sinh biên bản nghiệm thu, xuất PDF, kiểm tra tên file, rồi tải lên CDE. Quy trình viết trong file .yaml, có biến thay đổi theo kỳ, chạy thử trước khi chạy thật, dừng đúng chỗ khi lỗi và chạy tiếp được từ bước đó. Dùng skill này khi người dùng nhắc tới quy trình, tự động hóa cả chuỗi, làm hồ sơ hằng tháng, báo cáo định kỳ, chạy một loạt bước, hoặc nói "tháng nào cũng phải làm lại từng ấy việc", "có cách nào chạy một phát ra hết không", "gói lại thành một lệnh". Cũng dùng khi người dùng vừa làm xong một chuỗi thao tác thủ công và muốn lần sau khỏi làm lại.

Hồ sơ tháng gồm sáu bảy bước giống hệt nhau, tháng nào cũng thế, chỉ khác cái
ngày tháng. Viết một lần vào file `.yaml`, tháng sau chạy một lệnh.

## Nhận ra lúc nào nên gói

Dấu hiệu rõ nhất: người dùng vừa gõ ba bốn lệnh liên tiếp, hoặc kể lại một
chuỗi thao tác họ vẫn làm tay. Lúc đó **đề xuất gói lại** - họ thường không tự
nghĩ tới vì đang bận làm cho xong việc hôm nay.

Ngược lại, việc chạy đúng một lần thì đừng gói. Viết file quy trình cho một
việc chạy một lần là tốn công hơn làm tay.

## Cách viết

```yaml
ten: Hồ sơ nghiệm thu tháng 8
bien:
  thang: "2026-08"
  goc: "D:/DuAn/CauQuangSon"
buoc:
  - ten: Gộp bảng khối lượng các đội
    lenh: xlkit
    tham_so: [gop, --vao, "{goc}/khoi-luong/*.xlsx", --ra, "{goc}/tong-{thang}.xlsx"]

  - ten: Soát lỗi trước khi lập biên bản
    lenh: xlkit
    tham_so: [soat, --vao, "{goc}/tong-{thang}.xlsx", --khoa, "Mã hiệu"]

  - ten: Sinh biên bản
    lenh: docgen
    tham_so: [tao, --mau, "{goc}/mau/BB-NT.docx", --du-lieu, "{goc}/tong-{thang}.xlsx",
              --ra-thu-muc, "{goc}/bien-ban-{thang}", --ten, "BB-{{So hieu}}.docx", --pdf]

  - ten: Tải lên CDE
    lenh: cde
    tham_so: [tai-len, --du-an, "b.xxxx", --thu-muc, "urn:...", --vao, "{goc}/bien-ban-{thang}"]
    hoi_truoc: true
```

`{thang}` là biến trong quy trình. `{{So hieu}}` là chỗ trống của mẫu Word -
hai thứ khác nhau, công cụ phân biệt được, không cần né tránh.

`lenh` nhận: `xlkit`, `docgen`, `docxkit`, `cde`, `iso19650`, hoặc `shell` cho
lệnh hệ thống bất kỳ.

## Ba cờ đáng nhớ

- `hoi_truoc: true` - dừng lại hỏi trước khi làm việc không lùi được (tải lên,
  gửi đi, ghi đè). **Luôn đặt cờ này cho mọi bước tác động lên máy chủ.**
- `bo_qua_loi: true` - bước này lỗi vẫn chạy tiếp. Mặc định là dừng, và mặc
  định đó đúng: bước soát lỗi mà thất bại thì các bước sau vô nghĩa.
- `--tu-buoc N` khi chạy - chạy tiếp từ bước N sau khi đã sửa lỗi, không phải
  làm lại từ đầu.

## Trình tự triển khai

```
python chay.py --mau > quy-trinh/ho-so-thang.yaml   # sinh khung
# sửa file cho khớp đường dẫn thật
python chay.py quy-trinh/ho-so-thang.yaml --thu     # xem sẽ chạy gì, chưa chạy
python chay.py quy-trinh/ho-so-thang.yaml           # chạy thật
python chay.py quy-trinh/ho-so-thang.yaml --bien thang=2026-09   # kỳ sau
```

Luôn chạy `--thu` trước lần chạy thật đầu tiên. Nó in ra đúng từng lệnh sẽ
chạy - đọc qua là thấy ngay đường dẫn sai hay thiếu tham số.

## Thiết kế quy trình cho tốt

**Đặt bước soát ngay sau bước gộp**, trước mọi bước sinh hồ sơ. Chi phí phát
hiện lỗi ở bước 2 rẻ hơn nhiều so với phát hiện sau khi đã sinh 200 biên bản.

**Bước tải lên để cuối cùng và có `hoi_truoc`.** Mọi thứ trước đó chỉ động vào
máy của người dùng, sửa lại được. Tải lên CDE là lúc người khác nhìn thấy.

**Đặt tên bước bằng tiếng người, không phải tên lệnh.** File quy trình sẽ được
đọc lại sau sáu tháng, có thể bởi người khác trong tổ.

## Nối với việc khác

Các bước gọi tới ba skill còn lại trong bộ: `excel-tu-dong-hoa`,
`word-ho-so-tu-dong`, `cde-dong-bo`. Khi người dùng hỏi chi tiết một bước cụ
thể, đọc skill tương ứng thay vì đoán tham số.
