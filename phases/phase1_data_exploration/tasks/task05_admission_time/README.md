# Task 5 — Khảo sát admission và thời gian

Task này khảo sát quan hệ giữa `charttime`, `storetime`, `admittime` và `dischtime` trên toàn bộ dòng xét nghiệm đáp ứng định nghĩa nền tảng sử dụng của Task 3.

## Nguyên tắc

- Chỉ dùng `hadm_id` có sẵn và hợp lệ; không khôi phục `hadm_id` thiếu.
- Không sửa dữ liệu HOSP gốc.
- Các cửa sổ 6, 12 và 24 giờ chỉ là thống kê mô tả, chưa phải lựa chọn chính thức.
- Khoảng cửa sổ dùng quy ước nửa mở: `0 <= charttime - admittime < số giờ`, đồng thời xét nghiệm phải nằm trong admission.

## Chạy lại

```powershell
python scripts/run_analysis.py
python scripts/build_report.py <run_dir>
```

Mỗi lần chạy tạo một thư mục riêng trong `outputs/`. Báo cáo dùng tên `REPORT_task05.md` và `REPORT_task05.docx`.
