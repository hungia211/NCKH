# Task 1 — Inventory HOSP

## Trạng thái

Hoàn tất.

## Mục đích

Kiểm kê toàn bộ bảng trong MIMIC-IV v3.1 HOSP, gồm số dòng, số cột, schema và kích thước file nén. Một số thống kê tổng quan ban đầu của `admissions`, `labevents` và `diagnoses_icd` cũng được lưu để định hướng các task tiếp theo.

## File chính

- `report/REPORT_task01.docx`: báo cáo Word dành cho người đọc.
- `report/REPORT_task01.md`: bản Markdown của báo cáo.
- `report/DATA_DICTIONARY_task01.docx`: bảng giải thích tiếng Việt cho 44 cột của năm bảng chính.
- `report/DATA_DICTIONARY_task01.md`: bản Markdown của từ điển dữ liệu.
- `outputs/tables/DATA_DICTIONARY_task01.xlsx`: workbook gồm tổng quan, toàn bộ cột và cách đọc các mốc thời gian.
- `outputs/tables/data_dictionary_core_tables_task01.csv`: bảng phẳng để đọc hoặc dùng lại bằng mã nguồn.
- `outputs/tables/phase1_hosp_exploration.xlsx`: workbook xem nhanh.
- `outputs/machine_readable/hosp_inventory.json`: inventory có cấu trúc.
- `scripts/explore_hosp.py`: script inventory đọc dữ liệu gốc ở chế độ chỉ đọc.
- `scripts/build_data_dictionary.py`: tái tạo CSV, Markdown và Word của từ điển dữ liệu.

## Phạm vi

Task này chưa tạo cohort, chưa làm sạch dữ liệu, chưa chọn cửa sổ thời gian, lab hoặc nhãn bệnh.
