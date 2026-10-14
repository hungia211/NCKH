# Hướng dẫn cho agent trong repo này

Trước mọi task về nghiên cứu hiện tại, đọc theo thứ tự:

1. `research_context/PROJECT_CONTEXT.md`
2. `research_context/CURRENT_STATE.md`
3. `research_context/AGENT_GUIDE.md`
4. `research_context/ROADMAP.md`

Khi task liên quan đến modeling, so sánh mô hình hoặc lịch sử nhiều lần nhập viện, đọc thêm `research_context/LONGITUDINAL_EXTENSION.md`. Đây là hướng mở rộng sau baseline admission-level, không thay thế pipeline chính.

Khi làm Giai đoạn 1, đọc thêm `phases/phase1_data_exploration/README.md` và `phases/phase1_data_exploration/STATUS.md`; cập nhật task, script, báo cáo và output trong thư mục task tương ứng.

Khi làm Giai đoạn 2, đọc thêm `phases/phase2_cohort_definition/README.md`, `TASK_BREAKDOWN.md`, `STATUS.md` và `DECISION_LOG.md`. Không chạy bước tạo cohort trước khi các quyết định bắt buộc trong Task 3 được ghi là đã chốt.

Đề tài hiện tại là dự đoán **multi-label disease phenotypes** từ dữ liệu xét nghiệm giai đoạn sớm của một hospital admission trong MIMIC-IV v3.1 HOSP. Đơn vị phân tích là `hadm_id`; chia tập theo `subject_id`.

Dữ liệu HOSP trên máy hiện tại: `D:\UIT_thu\NCKH\data\hosp`. Đây là dữ liệu gốc, không sửa hoặc ghi đè. Trước khi chạy tác vụ, xác minh đường dẫn trong môi trường đang dùng.

Code và tài liệu ECG trước đây nằm trong `legacy_ecg/` chỉ để tham khảo lịch sử, không còn là pipeline nghiên cứu hiện tại.

Nếu có `.codegraph/`, dùng CodeGraph trước khi tìm hoặc đọc mã nguồn được index. Không tự đặt ngưỡng, cửa sổ thời gian hoặc thay đổi research design; ghi lại mọi quyết định cùng số liệu hỗ trợ.
