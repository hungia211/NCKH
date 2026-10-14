# Task 6 — Chất lượng dữ liệu và nguy cơ leakage

Task này tổng hợp các phát hiện đã đo trong Task 2–5, mô tả cohort còn lại ở từng bước và ghi các biện pháp kiểm soát leakage cần dùng ở các phase sau.

Task không tạo dataset huấn luyện, không xóa dữ liệu gốc, không chọn cửa sổ thời gian và không đặt ngưỡng phenotype.

## Chạy lại

```powershell
python scripts/run_analysis.py
python scripts/build_report.py <run_dir>
```

Báo cáo dùng tên `REPORT_task06.md` và `REPORT_task06.docx`.
