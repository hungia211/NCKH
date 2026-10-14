# Báo cáo Phase 2 Task 1 Soạn đặc tả cohort nháp

**Ngày báo cáo:** 14/10/2026  
**Phạm vi:** Đặc tả và quản lý rule, chưa lọc dữ liệu  
**Trạng thái:** Task 1 hoàn tất bản nháp, cohort specification chưa được duyệt

## 1 Mục đích và kết luận

Task 1 đã chuyển các quyết định kế thừa từ Phase 1 thành đặc tả cohort nháp phiên bản 0.1. Đặc tả định nghĩa đơn vị phân tích, bảng nguồn, trường thời gian, admission eligibility, diagnosis eligibility, lab eligibility, audit funnel và output contract.

Không có dữ liệu HOSP nào bị sửa hoặc lọc trong task này. Bảy quyết định P2-D08 đến P2-D14 vẫn ở trạng thái chờ và không được phép áp dụng trước khi Task 2 cung cấp bằng chứng và người nghiên cứu xác nhận tại Task 3.

## 2 Phạm vi thực hiện

Task 1 thực hiện các nội dung sau:

- Xác nhận cohort ở cấp `hadm_id` và giữ `subject_id`.
- Xác định vai trò của `admissions`, `labevents` và `diagnoses_icd`.
- Định nghĩa vai trò của `admittime`, `dischtime`, `charttime` và `storetime`.
- Định nghĩa eligibility riêng cho admission, diagnosis và lab.
- Tạo rule register có mã, logic, lý do, đơn vị audit và trạng thái.
- Tạo danh sách câu hỏi và bằng chứng cần có trong Task 2.
- Định nghĩa output contract và validation contract cho cohort tương lai.

Task 1 không chọn early window, không tạo cohort, không chuẩn hóa lab và không ánh xạ ICD sang PheCode.

## 3 Đầu vào và căn cứ

Đặc tả sử dụng research context hiện tại, kết quả Phase 1, Phase 2 Decision Log và Cohort Specification Template. Các số liệu Phase 1 chỉ được dùng làm căn cứ cho câu hỏi cần phân tích; Task 1 không tính lại số liệu.

Các dữ liệu chính của Phase 2 sẽ là `admissions`, `labevents` và `diagnoses_icd`. `d_labitems` chỉ hỗ trợ kiểm tra khóa xét nghiệm; `d_icd_diagnoses` là dictionary và không xác định diagnosis của bệnh nhân.

## 4 Cấu trúc cohort dự kiến

Cohort ở Task 4 dự kiến có một dòng duy nhất cho mỗi admission:

```text
subject_id | hadm_id | admittime | dischtime | selected_window_hours |
has_eligible_lab | eligible_lab_count | eligible_item_count |
has_diagnosis | cohort_version
```

Các trường thời gian, cờ và số đếm là metadata eligibility và audit. Chúng không mặc định trở thành feature mô hình.

## 5 Các rule đã chốt

| Nội dung | Rule chính | Căn cứ | Ảnh hưởng |
|---|---|---|---|
| Đơn vị phân tích | KEY-01, OUT-01 | P2-D01 | Một dòng mỗi `hadm_id` |
| Giữ khóa bệnh nhân | KEY-02 | P2-D02 | Giữ `subject_id`, chia tập ở Phase 5 |
| Lab thiếu hadm_id | LAB-01 | P2-D03 | Không khôi phục hoặc suy diễn |
| Lab sai chủ admission | LAB-02 | P2-D04 | Không thuộc tập ứng viên |
| Cách ghép | JOIN-01 | P2-D05 | Tổng hợp lab và diagnosis riêng theo admission |
| Dữ liệu nguồn | SRC-01 | P2-D06 | Chỉ đọc, không ghi đè |
| Nguồn diagnosis | DX-01 | Thiết kế Phase 2 | Admission cần ít nhất một diagnosis đủ điều kiện |

## 6 Định nghĩa eligibility

### 6.1 Admission

Admission phải có khóa đầy đủ, quan hệ `hadm_id` đến `subject_id` duy nhất và các mốc thời gian có thể đọc được. Chính sách đối với interval âm, admission kết thúc sớm và giới hạn quần thể vẫn chờ quyết định.

### 6.2 Diagnosis

Admission phải có ít nhất một dòng `diagnoses_icd` đủ khóa, có `hadm_id` tồn tại và có `subject_id` khớp `admissions`. Phase 2 chưa yêu cầu map PheCode thành công.

### 6.3 Laboratory

Dòng lab ứng viên phải có `hadm_id`, khớp chủ admission, có `itemid` trong dictionary và có `charttime` đọc được. Điều kiện kết quả tối thiểu, quan hệ với admission, early window và `storetime` vẫn chờ quyết định.

## 7 Quy ước cửa sổ nháp

Task 2 sẽ so sánh 6, 12 và 24 giờ theo cùng công thức nửa mở:

```text
0 <= charttime - admittime < window_hours
```

Đây là quy ước so sánh, không phải lựa chọn cửa sổ chính thức. Việc kết hợp điều kiện `charttime <= dischtime` phụ thuộc P2-D10 và P2-D11.

## 8 Các quyết định còn chờ

| Decision ID | Chủ đề | Cần Task 2 cung cấp | Trạng thái |
|---|---|---|---|
| P2-D08 | Early window | Coverage admission, subject, lab và itemid | Chờ quyết định |
| P2-D09 | Interval âm | Ảnh hưởng của 175 admission | Chờ quyết định |
| P2-D10 | Admission kết thúc sớm | Ảnh hưởng theo từng window | Chờ quyết định |
| P2-D11 | Lab ngoài admission | Lab trước admittime và sau dischtime | Chờ quyết định |
| P2-D12 | Storetime cutoff | Kết quả lưu sau cutoff | Chờ quyết định |
| P2-D13 | Lab tối thiểu | Phân bố số kết quả và itemid trên admission | Chờ quyết định |
| P2-D14 | Giới hạn quần thể | Lý do nghiên cứu và ảnh hưởng số lượng | Chờ quyết định |

## 9 Audit funnel và khả năng tái lập

Task 4 phải ghi số trước và sau từng rule ở cấp dòng lab, admission và subject; đồng thời ghi số bị loại riêng, số bị loại tích lũy, mẫu số và reason code. Thứ tự rule phải được đóng băng trong Task 3 vì các nhóm bị loại có thể chồng lấp.

Cohort cuối phải có manifest, checksum hoặc dấu vết tương đương, phiên bản script và khả năng tái lập trên cùng input.

## 10 Đầu ra Task 1

- `COHORT_SPEC.md`: đặc tả cohort nháp phiên bản 0.1.
- `rule_register_phase2_task01.csv`: danh mục 18 rule cấu trúc, eligibility, thời gian, audit và output.
- `decision_questions_phase2_task01.csv`: bảy quyết định còn chờ và bằng chứng Task 2 cần cung cấp.
- `REPORT_phase2_task01.md` và `REPORT_phase2_task01.docx`: báo cáo dành cho người đọc.
- `test_spec_consistency.py`: kiểm tra rule và decision ID nhất quán giữa các tài liệu.

## 11 Đánh giá hoàn tất Task 1

Task 1 đáp ứng điều kiện hoàn tất vì mỗi rule đã có mã, logic, lý do, đơn vị audit và trạng thái; các rule chưa được phê duyệt được tách riêng và không bị áp dụng. Đặc tả vẫn mang trạng thái **CHƯA DUYỆT** vì việc duyệt cohort specification cuối cùng thuộc Task 3.

Task tiếp theo là Task 2, phân tích chi tiết các kịch bản 6, 12 và 24 giờ cùng ảnh hưởng của admission kết thúc sớm, lab ngoài admission, `storetime` và điều kiện lab tối thiểu.
