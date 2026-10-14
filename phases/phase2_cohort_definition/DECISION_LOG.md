# Phase 2 — Decision Log

Tài liệu này là nguồn duy nhất để theo dõi các quyết định ảnh hưởng cohort. Khi một quyết định được chốt, ghi ngày, người xác nhận, phương án và bằng chứng hỗ trợ.

## Quyết định kế thừa từ Phase 1

| Mã | Chủ đề | Trạng thái | Quyết định |
|---|---|---|---|
| P2-D01 | Đơn vị phân tích | Đã chốt | Một mẫu cuối cùng đại diện một `hadm_id`. |
| P2-D02 | Khóa bệnh nhân | Đã chốt | Giữ `subject_id`; chia tập theo bệnh nhân ở Phase 5. |
| P2-D03 | Lab thiếu hadm_id | Đã chốt | Không khôi phục hoặc suy diễn; không dùng trong dataset xử lý admission-level. |
| P2-D04 | Sai chủ admission | Đã chốt | Dòng lab có `subject_id` không khớp chủ của `hadm_id` không thuộc tập ứng viên. |
| P2-D05 | Cách ghép | Đã chốt | Tổng hợp nhánh lab và diagnosis riêng ở cấp admission rồi mới ghép. |
| P2-D06 | Dữ liệu gốc | Đã chốt | Chỉ đọc, không sửa hoặc ghi đè. |
| P2-D07 | Diễn giải diagnosis | Đã chốt | Không coi ICD là timestamp chẩn đoán; không tuyên bố dự đoán trước bác sĩ. |

## Quyết định bắt buộc trong Phase 2

| Mã | Chủ đề | Trạng thái | Phương án cần so sánh | Bằng chứng cần có |
|---|---|---|---|---|
| P2-D08 | Early window | Chờ quyết định | 6 giờ / 12 giờ / 24 giờ / phương án được đề xuất khác | Admission, subject, lab coverage và nguy cơ thông tin muộn |
| P2-D09 | Interval âm | Chờ quyết định | Loại admission / phương án khác có lý do | 175 admission và ảnh hưởng cohort |
| P2-D10 | Admission kết thúc sớm | Chờ quyết định | Giữ phần thời gian quan sát / yêu cầu đủ toàn cửa sổ / phương án khác | Số admission bị ảnh hưởng theo từng window |
| P2-D11 | Lab ngoài admission | Chờ quyết định | Chỉ giữ `admittime <= charttime <= dischtime` / quy tắc khác | 2.816.594 dòng trước và 53.761 dòng sau admission |
| P2-D12 | Storetime cutoff | Chờ quyết định | Chỉ dùng để audit / yêu cầu `storetime` trước cutoff / quy tắc khác | Coverage và số kết quả bị ảnh hưởng |
| P2-D13 | Lab tối thiểu | Chờ quyết định | Ít nhất một kết quả hợp lệ / yêu cầu khác | Phân bố số itemid và số kết quả trên admission |
| P2-D14 | Giới hạn quần thể | Chờ quyết định | Không bổ sung / tuổi / loại admission / tiêu chí có cơ sở khác | Liên hệ trực tiếp với câu hỏi nghiên cứu và ảnh hưởng số lượng |

## Mẫu ghi quyết định

```text
Mã quyết định:
Ngày:
Người xác nhận:
Phương án được chọn:
Lý do:
Bằng chứng/số liệu:
Ảnh hưởng đến code và dữ liệu:
```

Không đổi trạng thái thành **Đã chốt** nếu chưa có xác nhận rõ ràng của người nghiên cứu.
