# Agent guide

## Trước khi làm việc

1. Đọc `PROJECT_CONTEXT.md` và xác định task thuộc giai đoạn nào.
2. Xác minh dữ liệu HOSP tại `D:\UIT_thu\NCKH\data\hosp` trong môi trường hiện tại. Chỉ đọc dữ liệu gốc.
3. Kiểm tra file, schema và dữ liệu hiện có; không tự giả định window hoặc threshold.
4. Đọc các báo cáo liên quan trong `docs/` nếu task đụng tới dữ liệu đã khảo sát.
5. Nếu repo có `.codegraph/`, ưu tiên CodeGraph để tìm symbol và luồng code trước khi đọc rộng bằng grep/find.

## Khi triển khai

- Giữ đơn vị phân tích là `hadm_id` và chia train/validation/test theo `subject_id`.
- Phân biệt patient-level data với dictionary tables.
- Tách exploration khỏi pipeline tạo dataset cuối.
- Ghi input, output, số dòng trước/sau, rule lọc, seed và cảnh báo.
- Không mặc định dùng 6, 12 hoặc 24 giờ; phải khảo sát và báo cáo kết quả.
- Không tự chọn một bệnh duy nhất; target chính là multi-label disease phenotypes.
- Không diễn giải association hoặc SHAP contribution thành quan hệ nhân quả.
- Khi dùng lịch sử nhiều admission, với admission mục tiêu chỉ được dùng các admission trước và xét nghiệm giai đoạn sớm của admission mục tiêu; không dùng diagnosis mục tiêu hoặc dữ liệu tương lai làm feature. Chi tiết tại `LONGITUDINAL_EXTENSION.md`.

## Báo cáo kết quả

Mỗi task cần nêu: mục đích, file/script thay đổi, input/output, số lượng trước/sau, phát hiện chính, rủi ro, quyết định còn chờ và cách chạy lại.

Tên file báo cáo phải kèm mã task để người đọc nhận biết ngay nội dung, theo mẫu `REPORT_taskNN.md` và `REPORT_taskNN.docx` (ví dụ `REPORT_task05.md`). Quy ước này áp dụng cho toàn bộ báo cáo; khi đổi tên phải cập nhật cả script tạo báo cáo và các đường dẫn tài liệu liên quan.

## Tạo file

- Dùng tên mô tả rõ ràng.
- Không ghi đè raw data.
- Ưu tiên script tái lập được.
- Đặt kết quả trung gian trong thư mục riêng và ghi metadata.
