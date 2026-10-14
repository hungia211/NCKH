# Cohort Specification — Template

> Trạng thái: mẫu nháp. Không dùng để chạy lọc cho đến khi mọi mục bắt buộc được điền và duyệt.

## 1. Phiên bản

- Cohort version:
- Ngày duyệt:
- Người duyệt:
- Commit/script version:

## 2. Câu hỏi nghiên cứu

Liệu các đặc trưng xét nghiệm cận lâm sàng ở giai đoạn sớm của một hospital admission có thể hỗ trợ mô hình Machine Learning dự đoán đồng thời các phenotype bệnh được ghi nhận cho admission đó hay không?

## 3. Đơn vị và khóa

- Đơn vị phân tích: `hadm_id`.
- Khóa bệnh nhân: `subject_id`.
- Yêu cầu `hadm_id` duy nhất trong cohort cuối: Có.
- Chia tập theo `subject_id`: Có, thực hiện ở Phase 5.

## 4. Bảng nguồn

| Bảng | Vai trò | Khóa |
|---|---|---|
| `admissions` | Khung admission và thời gian | `hadm_id`, `subject_id` |
| `labevents` | Xác định admission có lab trong window | `hadm_id`, `subject_id`, `itemid` |
| `diagnoses_icd` | Xác định admission có nguồn nhãn | `hadm_id`, `subject_id`, `icd_code`, `icd_version` |

## 5. Inclusion criteria

| Thứ tự | Rule ID | Điều kiện | Trạng thái |
|---:|---|---|---|
| 1 | INC-01 | `hadm_id` và `subject_id` tồn tại, khớp `admissions` | Đã chốt |
| 2 | INC-02 | Admission có ít nhất một diagnosis hợp lệ | Đã chốt về nguyên tắc |
| 3 | INC-03 | Admission có lab hợp lệ trong cửa sổ đã chọn | Chờ chọn window và định nghĩa lab tối thiểu |
| 4 | INC-04 | Điều kiện bổ sung nếu được duyệt | Chờ quyết định |

## 6. Exclusion criteria

| Rule ID | Điều kiện loại | Trạng thái |
|---|---|---|
| EXC-01 | Dòng lab thiếu `hadm_id` | Đã chốt |
| EXC-02 | Dòng lab sai `subject_id` so với admission | Đã chốt |
| EXC-03 | Admission có `dischtime < admittime` | Chờ quyết định |
| EXC-04 | Lab trước `admittime` hoặc sau `dischtime` | Chờ quyết định |
| EXC-05 | Kết quả không sẵn có theo `storetime` tại cutoff | Chờ quyết định |

## 7. Early-admission window

- Mốc bắt đầu: `admittime`.
- Trường thời gian xét nghiệm chính: `charttime`.
- Độ dài cửa sổ: **CHỜ QUYẾT ĐỊNH**.
- Quy ước biên dự kiến: `0 <= charttime - admittime < window_hours`.
- Cách xử lý admission kết thúc trước cửa sổ: **CHỜ QUYẾT ĐỊNH**.
- Chính sách `storetime`: **CHỜ QUYẾT ĐỊNH**.

## 8. Diagnosis eligibility

- Admission phải có ít nhất một dòng `diagnoses_icd` đủ khóa và khớp `admissions`.
- Chưa yêu cầu PheCode mapping thành công trong Phase 2; coverage mapping thuộc Phase 4.
- Khử trùng ICD/PheCode không thực hiện trong cohort key list, trừ khi chỉ dùng để tạo cờ có diagnosis.

## 9. Lab eligibility

- Không khôi phục `hadm_id`.
- `subject_id` phải khớp chủ admission.
- `itemid` phải tồn tại trong `d_labitems`.
- `charttime` phải đọc được.
- Điều kiện kết quả tối thiểu: **CHỜ QUYẾT ĐỊNH**.
- Chuẩn hóa đơn vị, outlier và aggregation: chuyển sang Phase 3.

## 10. Audit funnel bắt buộc

Với mỗi rule, lưu:

- số dòng lab trước/sau;
- số admission trước/sau;
- số subject trước/sau;
- số bị loại riêng tại rule;
- số bị loại tích lũy;
- reason code;
- mẫu số dùng tính tỷ lệ.

## 11. Output contract

Danh sách cohort tối thiểu:

```text
subject_id | hadm_id | admittime | dischtime | selected_window_hours |
has_eligible_lab | eligible_lab_count | eligible_item_count | has_diagnosis
```

Các cột thời gian và audit không được dùng trực tiếp như feature nếu chưa có quyết định riêng.

## 12. Validation

- `hadm_id` duy nhất và không thiếu.
- Một `hadm_id` chỉ thuộc một `subject_id`.
- Mọi admission có lab và diagnosis theo đặc tả.
- Không có vi phạm window/cutoff đã duyệt.
- Tổng số khớp audit funnel.
- Script chạy lại cho kết quả xác định.

## 13. Approval

```text
Trạng thái: CHƯA DUYỆT
Nội dung còn chờ:
Người xác nhận:
Ngày xác nhận:
```
