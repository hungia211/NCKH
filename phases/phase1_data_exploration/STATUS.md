# Trạng thái Giai đoạn 1

## Tiến độ

| Task | Nội dung | Trạng thái | Ghi chú |
| --- | --- | --- | --- |
| 1 | Inventory toàn bộ bảng HOSP | Hoàn tất | Đã kiểm kê 22 bảng, schema và số dòng. |
| 2 | Kiểm tra khóa và liên kết | Hoàn tất | Đã kiểm tra khóa, orphan, sai `subject_id` và độ phủ admission. |
| 3 | Khảo sát `labevents` | Hoàn tất | Đã khảo sát toàn bộ dòng, itemid, kết quả, đơn vị và số lần đo trên admission. |
| 4 | Khảo sát `diagnoses_icd` | Hoàn tất | Đã khảo sát khóa, ICD-9/10, dictionary, seq_num, mã trùng và phân bố admission. |
| 5 | Khảo sát admission và thời gian | Hoàn tất | Đã đo vị trí thời gian lab và độ phủ mô tả 6/12/24 giờ trên lab có `hadm_id` hợp lệ. |
| 6 | Chất lượng dữ liệu và leakage | Hoàn tất | Đã lập danh mục 11 vấn đề chất lượng, 6 nguy cơ leakage và mức sẵn sàng của cohort. |
| 7 | Báo cáo và quyết định chuyển phase | Hoàn tất | Đã tạo báo cáo định kỳ, nhật ký quyết định và kế hoạch Phase 2 đề xuất. |

**Tổng cộng: 7/7 task đã hoàn tất.**

## Việc tiếp theo

Phase 1 đã hoàn tất. Bước tiếp theo là thảo luận và duyệt đặc tả Phase 2 — Cohort Definition. Các lựa chọn còn mở gồm cửa sổ giai đoạn sớm, cohort cuối, xử lý admission bất thường, đơn vị/kết quả chữ/outlier và label set sau ICD → Phecode.

## Cách tìm file

- Mỗi task đã bắt đầu nằm trong `tasks/`.
- Mã chạy lại nằm trong `tasks/<task>/scripts/`.
- Kết quả do script tạo nằm trong `tasks/<task>/outputs/`.
- Báo cáo dành cho người đọc nằm trong `tasks/<task>/report/` hoặc trong thư mục một lần chạy.
- File dựng báo cáo, ảnh kiểm tra và artifact kỹ thuật nằm trong `.internal/`; thông thường không cần mở.
