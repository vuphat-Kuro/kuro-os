---
name: "Kiểm tra và đề xuất đồng bộ BVTC"
description: "Kiểm tra hiện trạng BVTC giữa thư mục nguồn và thư mục dự án, báo cáo tình trạng và đề xuất phương án đồng bộ"
group: "Hồ sơ & lưu trữ"
origin: javis-learned
status: active
created: 2026-10-21
---
## Khi nào dùng
Dùng khi người dùng yêu cầu kiểm tra tình trạng hồ sơ BVTC (bản vẽ thi công đã duyệt) của một dự án, đối chiếu giữa thư mục dự án tại Second Brain và thư mục nguồn trên máy tính, rồi đề xuất phương án đồng bộ.

## Chuẩn bị
- Đường dẫn thư mục nguồn BVTC (ví dụ: X:\\KY THUAT THI CONG\\15. Cam Lo - La Son\\BVTC\\BVTC DUYET).
- Đường dẫn thư mục hồ sơ dự án tại Second Brain (ví dụ: QLDA/01-DuAn/CLLS-XL01/03-BanVe-ThiCong/).
- Danh sách hạng mục dự án cần đối chiếu.

## Cách chạy
1. Kiểm tra thư mục hồ sơ dự án tại Second Brain: có trống không, đã có file nào chưa.
2. Kiểm tra thư mục nguồn BVTC: số lượng tệp, dung lượng, phân nhóm hạng mục.
3. Đối chiếu từng hạng mục giữa hai nơi.
4. Báo cáo tình trạng: nhóm nào đã có, nhóm nào chưa có, tổng số tệp thiếu.
5. Đề xuất phương án đồng bộ (sao chép toàn bộ, sao chép chọn lọc, hoặc không làm) và chờ người dùng duyệt trước khi thực hiện.

## Quy trình
Bước 1: Kiểm tra thư mục dự án.
Bước 2: Kiểm tra thư mục nguồn.
Bước 3: Đối chiếu hạng mục.
Bước 4: Báo cáo tình trạng và đề xuất phương án.
Bước 5: Chờ duyệt trước khi thực hiện sao chép.

## Bẫy
- Không tự sao chép file từ ổ máy X: vào Second Brain nếu chưa có người dùng duyệt.
- Không khẳng định được nội dung tệp nếu không thể mở đọc được từ môi trường này.

## Kiểm chứng
- Có báo cáo rõ ràng số tệp tại nguồn và tại thư mục dự án.
- Có đề xuất phương án đồng bộ cụ thể, chờ xác nhận từ người dùng.
