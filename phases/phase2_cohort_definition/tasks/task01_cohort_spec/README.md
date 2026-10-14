# Phase 2 Task 1 Soạn đặc tả cohort nháp

## Trạng thái

Hoàn tất bản nháp ngày 2026-10-14. Đặc tả chưa được duyệt để chạy lọc dữ liệu.

## Mục đích

Chuyển các quyết định đã chốt từ Phase 1 thành đặc tả cohort có cấu trúc, đồng thời tách riêng những rule phải chờ bằng chứng Task 2 và quyết định của người nghiên cứu ở Task 3.

## Input

- `research_context/PROJECT_CONTEXT.md`
- `research_context/CURRENT_STATE.md`
- Kết quả và báo cáo Phase 1
- `phases/phase2_cohort_definition/DECISION_LOG.md`
- `phases/phase2_cohort_definition/COHORT_SPEC_TEMPLATE.md`

Task này không đọc lại toàn bộ dữ liệu HOSP và không áp dụng lọc record.

## File chính

- `../../COHORT_SPEC.md`: đặc tả cohort nháp phiên bản 0.1.
- `outputs/rule_register_phase2_task01.csv`: danh mục rule máy đọc.
- `outputs/decision_questions_phase2_task01.csv`: câu hỏi cần bằng chứng và phê duyệt.
- `report/REPORT_phase2_task01.md`: báo cáo Markdown.
- `report/REPORT_phase2_task01.docx`: báo cáo Word dành cho người đọc.
- `scripts/build_report.py`: tái tạo báo cáo Word từ bản Markdown.
- `tests/test_spec_consistency.py`: kiểm tra tính nhất quán giữa đặc tả, rule register và decision log.

## Quy tắc đã chốt

- Đơn vị phân tích là `hadm_id`.
- Giữ `subject_id` và chia tập theo bệnh nhân ở Phase 5.
- Không khôi phục lab thiếu `hadm_id`.
- Không dùng dòng lab sai chủ admission.
- Admission phải có nguồn diagnosis hợp lệ.
- Tổng hợp lab và diagnosis riêng ở cấp admission.
- Chỉ đọc dữ liệu HOSP gốc.

## Quy tắc chưa được phép áp dụng

- Chọn early window.
- Xử lý interval âm.
- Xử lý admission kết thúc sớm.
- Xử lý lab trước nhập viện và sau xuất viện.
- Chính sách `storetime`.
- Điều kiện lab tối thiểu.
- Giới hạn quần thể bổ sung.

## Cách chạy lại

Từ gốc repo, dùng Python có `python-docx`:

```powershell
python phases\phase2_cohort_definition\tasks\task01_cohort_spec\tests\test_spec_consistency.py
python phases\phase2_cohort_definition\tasks\task01_cohort_spec\scripts\build_report.py
```

## Điều kiện hoàn tất

- Mỗi rule có mã, nguồn, logic, lý do, đơn vị audit và trạng thái.
- Các quyết định P2-D08 đến P2-D14 vẫn được đánh dấu chờ quyết định.
- Không có cohort hoặc dữ liệu xử lý mới được tạo.
- Báo cáo Markdown và Word mô tả đúng phạm vi Task 1.

## Ngoài phạm vi

Task 1 không chọn cửa sổ, không tạo cohort, không chuẩn hóa lab, không map PheCode và không huấn luyện mô hình.
