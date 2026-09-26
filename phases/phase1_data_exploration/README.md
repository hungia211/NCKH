# Phase 1 — Data Exploration

Thư mục này gom toàn bộ công việc của Giai đoạn 1 để dễ quản lý và tái lập.

## Cấu trúc

```text
phase1_data_exploration/
├── README.md
├── TASK_BREAKDOWN.md
├── REPORT.md
├── scripts/
│   ├── explore_hosp.py
│   └── explore_hosp_core.py
└── outputs/
    ├── machine_readable/   # JSON dùng cho script và tái lập
    └── tables/             # CSV và XLSX dành cho người đọc
```

## Cách sử dụng kết quả

- Mở `outputs/tables/phase1_hosp_exploration.xlsx` để xem tổng quan bằng Excel.
- Dùng các file CSV trong `outputs/tables/` khi cần lọc nhanh hoặc đọc bằng công cụ khác.
- Giữ JSON trong `outputs/machine_readable/` làm nguồn chuẩn có cấu trúc cho các script tiếp theo.
- Đọc `REPORT.md` để xem diễn giải và các vấn đề cần xử lý.

## Chạy lại

```powershell
python phases\phase1_data_exploration\scripts\explore_hosp.py
python phases\phase1_data_exploration\scripts\explore_hosp_core.py
python phases\phase1_data_exploration\scripts\export_readable_tables.py
```

Các script chỉ đọc `data/hosp/`; không sửa dữ liệu gốc.

## Khuyến nghị lưu kết quả khảo sát

Nên giữ ba lớp dữ liệu song song:

1. **JSON machine-readable:** giữ cấu trúc đầy đủ và metadata để script đọc lại.
2. **CSV tidy tables:** mỗi file là một bảng phẳng, phù hợp lọc, diff bằng Git và đọc bằng Pandas/R.
3. **XLSX review workbook:** gom các bảng quan trọng thành nhiều sheet, có định dạng số, filter và freeze header để xem thủ công.

Không nên dùng XLSX làm nguồn chuẩn cho pipeline. JSON/CSV được sinh lại bằng script; XLSX là bản phục vụ quan sát và thảo luận.

## Khuyến nghị lưu kết quả khảo sát

Nên giữ ba lớp dữ liệu song song:

1. **JSON machine-readable:** giữ cấu trúc đầy đủ và metadata để script đọc lại.
2. **CSV tidy tables:** mỗi file là một bảng phẳng, phù hợp lọc, diff bằng Git và đọc bằng Pandas/R.
3. **XLSX review workbook:** gom các bảng quan trọng thành nhiều sheet, có định dạng số, filter và freeze header để xem thủ công.

Không nên dùng XLSX làm nguồn chuẩn cho pipeline. JSON/CSV được sinh lại bằng script; XLSX là bản phục vụ quan sát và thảo luận.
