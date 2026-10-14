# Task 4 — Khảo sát diagnoses icd

Task này khảo sát toàn bộ `diagnoses_icd`: độ đầy đủ của khóa, khả năng liên kết với admission và dictionary, ICD-9/ICD-10, tần suất mã, `seq_num`, số diagnosis trên admission và mã lặp.

“Dòng có nền tảng sử dụng” phải có `subject_id`, `hadm_id`, `icd_code`, `icd_version`, khớp bệnh nhân và admission, đồng thời khớp `d_icd_diagnoses`. Đây là định nghĩa khảo sát, chưa phải bộ nhãn cuối.

Task không map ICD sang Phecode, không chọn phenotype, không đặt ngưỡng tần suất và không chỉ giữ `seq_num = 1`.

## Kết quả hoàn tất

- `outputs/20260930T164935Z/REPORT_task04.docx`: báo cáo Word.
- `outputs/20260930T164935Z/REPORT_task04.md`: báo cáo Markdown.
- `outputs/20260930T164935Z/task04_diagnoses_review.xlsx`: workbook xem số liệu.
- Các CSV trong cùng thư mục chứa thống kê đầy đủ theo mã, phiên bản ICD, seq_num và admission.

Chạy từ gốc repo:

```powershell
python phases\phase1_data_exploration\tasks\task04_diagnoses\scripts\run_analysis.py
```
