# Task 3 — Khảo sát labevents

Task này khảo sát độ đầy đủ, khả năng liên kết, dạng kết quả, đơn vị và độ phủ theo xét nghiệm của toàn bộ `labevents`.

Quy tắc “dòng có nền tảng sử dụng” trong báo cáo chỉ là định nghĩa đo lường. Dòng phải có `subject_id`, `hadm_id`, `itemid`, khớp bệnh nhân và admission, khớp `d_labitems`, có `charttime` hợp lệ và có ít nhất một kết quả trong `valuenum` hoặc `value`. Quy tắc này chưa xóa dữ liệu và chưa phải tiêu chí cohort cuối.

Task không sử dụng bảng reference, không chọn lab, không chuẩn hóa đơn vị và không áp dụng cửa sổ thời gian.

## Kết quả hoàn tất

- `outputs/20260930T163439Z/REPORT_task03.docx`: báo cáo Word.
- `outputs/20260930T163439Z/REPORT_task03.md`: báo cáo Markdown.
- `outputs/20260930T163439Z/task03_labevents_review.xlsx`: workbook xem số liệu.
- Các CSV trong cùng thư mục chứa thống kê đầy đủ theo dòng, itemid, đơn vị và admission.

Chạy từ gốc repo:

```powershell
python phases\phase1_data_exploration\tasks\task03_labevents\scripts\run_analysis.py
```
