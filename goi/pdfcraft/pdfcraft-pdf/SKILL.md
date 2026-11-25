---
name: pdfcraft-pdf
description: "CHỈ dùng khi người dùng muốn đọc/trích chữ, tìm chữ, gộp, tách, trích trang, xoay, xóa trang hoặc chú thích tệp PDF bằng PdfCraft, hoặc hỏi PdfCraft đã cài chưa. Không dùng để OCR PDF quét tiếng Việt (OCR chỉ có tiếng Anh, mất dấu) và không dùng khi chỉ hỏi nội dung văn bản kỹ thuật."
---

# PdfCraft (PDF, Rust, MIT/Apache-2.0, chạy offline)

Nguồn: https://github.com/storytold/pdfcraft. Bản portable ghim `v0.22.0`, kiểm SHA-256, cài ở `%LOCALAPPDATA%\Programs\PdfCraft`.
Máy đã có bản cài tay ở đó thì gói dùng luôn. Script ở `scripts/`.

## Bước 0 - Đã cài chưa
`python scripts/pdfcraft_setup.py status`. `chua_cai`: hỏi người dùng rồi `install` (tải nền ~130 MB; `status` báo `dang_cai` cho tới khi xong). Gỡ chỉ khi người dùng yêu cầu.

## Bước 1 - Dùng
Ưu tiên tool MCP `pdfcraft` (đã giới hạn trong thư mục `state/cong-viec/pdfcraft`, đổi bằng biến `PDFCRAFT_ROOT`). Hoặc CLI (`pdfcraft-cli.exe` trong thư mục cài):
```
pdfcraft-cli info  f.pdf                       # cấu trúc JSON
pdfcraft-cli text  f.pdf --page 3              # chữ theo thứ tự đọc
pdfcraft-cli combine a.pdf b.pdf --out c.pdf
pdfcraft-cli extract f.pdf --pages 1,3,5-8 --out g.pdf
pdfcraft-cli split f.pdf --every 10 --out-dir parts/
pdfcraft-cli edit  f.pdf --rotate 1,2:90 --delete 5 --out g.pdf
pdfcraft-cli tools                             # mọi tool + JSON Schema
```
- Tệp kết quả lưu vào thư mục dự án hiện hành của người dùng; KHÔNG ghi vào kho mạng UNC của công ty. Đưa tệp cần xử lý vào thư mục làm việc của MCP (`--root`) rồi mới gọi.
- Đã đo: trích chữ/tìm chữ tiếng Việt trên PDF có lớp chữ đúng; `ocr_recognize` trên PDF quét tiếng Việt MẤT DẤU (OCR chỉ có `en`). Không dùng OCR cho hồ sơ tiếng Việt.
- Chỉ nói "đã gộp/tách xong" khi lệnh trả mã 0 và thấy tệp ra.
