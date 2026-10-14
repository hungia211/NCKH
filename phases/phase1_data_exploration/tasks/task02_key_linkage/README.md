# Task 2 — Kiểm tra khóa và liên kết

## Trạng thái

Hoàn tất lần chạy ngày 2026-09-26.

## Mục đích

Kiểm tra khả năng liên kết `patients`, `admissions`, `labevents`, `d_labitems`, `diagnoses_icd` và `d_icd_diagnoses` bằng các khóa tương ứng. Task chỉ khảo sát và ghi nhận bất nhất; không sửa dữ liệu gốc.

## File chính

- `outputs/20260926T154108Z/REPORT_task02.docx`: báo cáo Word chi tiết.
- `outputs/20260926T154108Z/REPORT_task02.md`: báo cáo Markdown.
- `outputs/20260926T154108Z/key_checks.csv`: các phép kiểm tra khóa.
- `outputs/20260926T154108Z/admission_overlap.csv`: độ phủ lab và diagnosis theo admission.
- `scripts/task2_links.py`: script khảo sát chính.
- `tests/test_task2_links.py`: kiểm thử hồi quy bằng dữ liệu tổng hợp nhỏ.

## Phạm vi

Task này chưa loại các dòng bất nhất, chưa tạo cohort và chưa ghép trực tiếp từng dòng lab với từng diagnosis.
