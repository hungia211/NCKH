# Giai đoạn 1 — Data Exploration

Giai đoạn này khảo sát dữ liệu HOSP trước khi định nghĩa cohort hoặc làm sạch dữ liệu. Không tạo dataset huấn luyện và không tự chọn cửa sổ thời gian, lab, aggregation hay ngưỡng nhãn.

## Bắt đầu từ đâu

1. Mở [STATUS.md](STATUS.md) để xem tiến độ hiện tại.
2. Mở [TASK_BREAKDOWN.md](TASK_BREAKDOWN.md) để xem mục tiêu và đầu ra của từng task.
3. Vào `tasks/<task>/README.md` để xem code, kết quả và báo cáo của task đó.

## Cấu trúc

```text
phase1_data_exploration/
├── README.md
├── STATUS.md
├── TASK_BREAKDOWN.md
├── tasks/
│   ├── task01_inventory/
│   │   ├── README.md
│   │   ├── scripts/
│   │   ├── outputs/
│   │   └── report/
│   ├── task02_key_linkage/
│   │   ├── README.md
│   │   ├── scripts/
│   │   ├── tests/
│   │   └── outputs/
│   ├── task03_labevents/
│   │   ├── README.md
│   │   ├── scripts/
│   │   ├── tests/
│   │   └── outputs/
│   ├── task04_diagnoses/
│   │   ├── README.md
│   │   ├── scripts/
│   │   ├── tests/
│   │   └── outputs/
│   ├── task05_admission_time/
│   │   ├── README.md
│   │   ├── scripts/
│   │   ├── tests/
│   │   └── outputs/
│   ├── task06_quality_leakage/
│   │   ├── README.md
│   │   ├── scripts/
│   │   └── outputs/
│   └── task07_phase1_summary/
│       ├── README.md
│       ├── scripts/
│       ├── report/
│       └── outputs/
└── .internal/               # ảnh QA và file kỹ thuật; thường không cần mở
```

Phase 1 hiện có đầy đủ Task 1 đến Task 7.

## Báo cáo chính

- Task 1: [Markdown](tasks/task01_inventory/report/REPORT_task01.md), [Word](tasks/task01_inventory/report/REPORT_task01.docx), [từ điển cột Word](tasks/task01_inventory/report/DATA_DICTIONARY_task01.docx) và [từ điển cột Excel](tasks/task01_inventory/outputs/tables/DATA_DICTIONARY_task01.xlsx).
- Task 2: [Markdown](tasks/task02_key_linkage/outputs/20260926T154108Z/REPORT_task02.md) và [Word](tasks/task02_key_linkage/outputs/20260926T154108Z/REPORT_task02.docx).
- Task 3: [Markdown](tasks/task03_labevents/outputs/20260930T163439Z/REPORT_task03.md) và [Word](tasks/task03_labevents/outputs/20260930T163439Z/REPORT_task03.docx).
- Task 4: [Markdown](tasks/task04_diagnoses/outputs/20260930T164935Z/REPORT_task04.md) và [Word](tasks/task04_diagnoses/outputs/20260930T164935Z/REPORT_task04.docx).
- Task 5: [Markdown](tasks/task05_admission_time/outputs/20261003T140751Z/REPORT_task05.md) và [Word](tasks/task05_admission_time/outputs/20261003T140751Z/REPORT_task05.docx).
- Task 6: [Markdown](tasks/task06_quality_leakage/outputs/20261003T141918Z/REPORT_task06.md) và [Word](tasks/task06_quality_leakage/outputs/20261003T141918Z/REPORT_task06.docx).
- Task 7: [Markdown](tasks/task07_phase1_summary/report/REPORT_task07.md) và [Word](tasks/task07_phase1_summary/report/REPORT_task07.docx).

## Quy ước quản lý

- `scripts/`: mã nguồn có thể chạy lại.
- `tests/`: kiểm thử nhỏ cho script của task.
- `outputs/`: file do script sinh ra; mỗi lần chạy lớn có thư mục timestamp riêng.
- `report/`: báo cáo ổn định dành cho người đọc.
- `.internal/`: ảnh render, file inspect và artifact phục vụ kiểm tra kỹ thuật.
- `data/hosp/`: dữ liệu gốc chỉ đọc, không bao giờ ghi đè.
- Báo cáo phải có mã task trong tên file: `REPORT_taskNN.md` và `REPORT_taskNN.docx`.

## Task tiếp theo

Phase 1 đã hoàn tất 7/7 task. Kế hoạch đề xuất tiếp theo là Phase 2 — Cohort Definition; chưa chọn cửa sổ chính thức, cohort cuối hoặc ngưỡng phenotype.
