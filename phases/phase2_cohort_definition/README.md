# Giai đoạn 2 — Cohort Definition

## Mục tiêu

Xác định tập hospital admission đủ điều kiện cho nghiên cứu và tạo một cohort có thể tái lập ở cấp `hadm_id`. Phase 2 chỉ làm sạch các vấn đề ảnh hưởng trực tiếp đến khóa, liên kết và thời gian của cohort.

Phase này chưa chuẩn hóa giá trị xét nghiệm, chưa xử lý outlier, chưa chọn cách aggregation và chưa ánh xạ ICD sang PheCode. Các công việc đó thuộc Phase 3 và Phase 4.

## Điểm xuất phát từ Phase 1

- Toàn bộ `admissions`: 546.028 admission.
- Có lab ứng viên và diagnosis: 446.891 admission.
- Có lab nằm trong admission hợp lệ và diagnosis: 432.410 admission.
- Có lab cùng diagnosis trong 6/12/24 giờ: 189.102 / 308.719 / 400.092 admission.
- Có 73.768.897 dòng `labevents` thiếu `hadm_id`; đã quyết định không khôi phục và không dùng trong dữ liệu xử lý admission-level.
- Có 413 dòng lab sai `subject_id` so với admission.
- Có 175 admission với `dischtime < admittime`.

Các con số trên là số liệu khảo sát, chưa phải cohort chính thức.

## Nguyên tắc bắt buộc

1. Dữ liệu gốc tại `D:\UIT_thu\NCKH\data\hosp` chỉ được đọc.
2. Đơn vị cohort là `hadm_id`; luôn giữ `subject_id` để chia tập theo bệnh nhân ở Phase 5.
3. Không suy diễn `hadm_id` bị thiếu.
4. Không tự chọn cửa sổ 6/12/24 giờ hoặc tiêu chí loại khi chưa được duyệt.
5. Mỗi rule lọc phải có tên, lý do, số dòng/admission/subject trước và sau.
6. Không nối trực tiếp các dòng lab với các dòng diagnosis; tạo danh sách khóa hoặc cờ ở cấp admission.
7. Mọi output xử lý phải nằm ngoài `data/hosp/` và có manifest/version.

## Luồng công việc

```text
Kết quả Phase 1
      ↓
Task 1: Đặc tả cohort nháp
      ↓
Task 2: So sánh kịch bản 6/12/24 giờ
      ↓
Task 3: Chốt quyết định nghiên cứu
      ↓
Task 4: Tạo cohort xử lý mới
      ↓
Task 5: Kiểm tra, đóng băng và bàn giao cohort
```

Task 4 không được bắt đầu trước khi các quyết định bắt buộc của Task 3 được ghi là **Đã chốt**.

## Tài liệu quản lý

- [TASK_BREAKDOWN.md](TASK_BREAKDOWN.md): nội dung, đầu ra và điều kiện hoàn tất của từng task.
- [STATUS.md](STATUS.md): tiến độ hiện tại.
- [DECISION_LOG.md](DECISION_LOG.md): quyết định đã chốt và câu hỏi đang chờ.
- [COHORT_SPEC_TEMPLATE.md](COHORT_SPEC_TEMPLATE.md): mẫu đặc tả cần hoàn thiện trước khi chạy lọc.
- [COHORT_SPEC.md](COHORT_SPEC.md): đặc tả cohort nháp hiện tại; chưa dùng để chạy lọc cho đến khi Task 3 phê duyệt.

## Task đã bắt đầu

- Task 1: [README](tasks/task01_cohort_spec/README.md), [báo cáo Markdown](tasks/task01_cohort_spec/report/REPORT_phase2_task01.md), báo cáo Word và các bảng rule trong cùng thư mục task.

## Quy ước thư mục khi bắt đầu task

```text
phase2_cohort_definition/
├── README.md
├── TASK_BREAKDOWN.md
├── STATUS.md
├── DECISION_LOG.md
├── COHORT_SPEC_TEMPLATE.md
└── tasks/
    └── taskNN_<name>/
        ├── README.md
        ├── scripts/
        ├── tests/
        ├── outputs/
        └── report/
```

Chỉ tạo thư mục task khi bắt đầu thực hiện task đó. Báo cáo dùng tên `REPORT_phase2_taskNN.md` và `REPORT_phase2_taskNN.docx`.

## Điều kiện kết thúc Phase 2

- Có cohort specification đã được duyệt.
- Có danh sách `hadm_id` và `subject_id` đủ điều kiện, không trùng khóa.
- Có audit funnel ghi số lượng trước/sau từng rule.
- Các admission đều liên kết hợp lệ với `admissions` và `diagnoses_icd`.
- Có bằng chứng về lab hợp lệ trong cửa sổ đã chọn.
- Có manifest, phiên bản và script tái lập.
- Có báo cáo bàn giao cho Phase 3 và Phase 4.
