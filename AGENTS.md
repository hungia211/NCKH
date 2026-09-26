# Hướng dẫn cho agent trong repo này

Trước mọi task về nghiên cứu hiện tại, đọc theo thứ tự:

1. `research_context/PROJECT_CONTEXT.md`
2. `research_context/CURRENT_STATE.md`
3. `research_context/AGENT_GUIDE.md`
4. `research_context/ROADMAP.md`

Khi làm Giai đoạn 1, đọc thêm `phases/phase1_data_exploration/README.md` và cập nhật task, script, báo cáo, output trong thư mục đó.

Đề tài hiện tại là dự đoán **multi-label disease phenotypes** từ dữ liệu xét nghiệm giai đoạn sớm của một hospital admission trong MIMIC-IV v3.1 HOSP. Đơn vị phân tích là `hadm_id`; chia tập theo `subject_id`.

Dữ liệu HOSP trên máy hiện tại: `D:\UIT_thu\NCKH\data\hosp`. Đây là dữ liệu gốc, không sửa hoặc ghi đè. Trước khi chạy tác vụ, xác minh đường dẫn trong môi trường đang dùng.

Code và tài liệu ECG trước đây nằm trong `legacy_ecg/` chỉ để tham khảo lịch sử, không còn là pipeline nghiên cứu hiện tại.

Nếu có `.codegraph/`, dùng CodeGraph trước khi tìm hoặc đọc mã nguồn được index. Không tự đặt ngưỡng, cửa sổ thời gian hoặc thay đổi research design; ghi lại mọi quyết định cùng số liệu hỗ trợ.
