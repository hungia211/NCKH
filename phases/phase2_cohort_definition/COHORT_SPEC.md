# Đặc tả cohort Phase 2

> Phiên bản nháp: 0.1  
> Ngày soạn: 2026-10-14  
> Trạng thái: Hoàn tất bản nháp Task 1, chưa được duyệt để chạy lọc dữ liệu  
> Phạm vi: Cohort admission-level cho bài toán dự đoán multi-label disease phenotypes từ xét nghiệm giai đoạn sớm

## 1. Mục đích

Đặc tả này định nghĩa cấu trúc, nguồn dữ liệu, điều kiện eligibility và các rule cần quản lý để tạo cohort ở cấp `hadm_id`. Tài liệu tách rõ nội dung đã chốt từ Phase 1 và nội dung còn phải được lựa chọn sau phân tích kịch bản của Task 2.

Task 1 không tạo cohort, không loại record khỏi dữ liệu xử lý và không chọn cửa sổ 6, 12 hoặc 24 giờ. Chỉ Task 4 mới được phép áp dụng các rule lọc sau khi tất cả quyết định bắt buộc của Task 3 đã được ghi là **Đã chốt**.

## 2. Câu hỏi nghiên cứu

Liệu các đặc trưng xét nghiệm cận lâm sàng ở giai đoạn sớm của một hospital admission có thể hỗ trợ mô hình Machine Learning dự đoán đồng thời các phenotype bệnh được ghi nhận cho admission đó hay không?

## 3. Đơn vị phân tích và khóa

| Nội dung | Đặc tả | Trạng thái |
|---|---|---|
| Đơn vị phân tích | Một hàng cohort đại diện một `hadm_id` | Đã chốt, P2-D01 |
| Khóa bệnh nhân | Giữ `subject_id` của admission | Đã chốt, P2-D02 |
| Tính duy nhất | `hadm_id` không thiếu và duy nhất trong cohort cuối | Bắt buộc |
| Quan hệ khóa | Một `hadm_id` chỉ thuộc một `subject_id` theo `admissions` | Bắt buộc |
| Chia tập | Chia train, validation và test theo `subject_id` ở Phase 5 | Đã chốt, P2-D02 |

## 4. Nguồn dữ liệu

### 4.1. Bảng nguồn chính

| Bảng | Vai trò trong Phase 2 | Trường tối thiểu |
|---|---|---|
| `admissions` | Khung admission, chủ admission và các mốc thời gian | `subject_id`, `hadm_id`, `admittime`, `dischtime` |
| `labevents` | Xác định admission có lab đủ điều kiện trong early window | `subject_id`, `hadm_id`, `itemid`, `charttime`, `storetime`, `value`, `valuenum` |
| `diagnoses_icd` | Xác định admission có nguồn diagnosis để tạo nhãn ở Phase 4 | `subject_id`, `hadm_id`, `icd_code`, `icd_version` |

### 4.2. Bảng hỗ trợ kiểm tra

| Bảng | Vai trò | Ghi chú |
|---|---|---|
| `d_labitems` | Kiểm tra `itemid` có tồn tại trong từ điển xét nghiệm | Không phải dữ liệu bệnh nhân |
| `d_icd_diagnoses` | Đối soát dictionary ICD khi cần | Không dùng để xác định diagnosis của bệnh nhân |

Tất cả file nguồn tại `D:\UIT_thu\NCKH\data\hosp` chỉ được đọc. Mọi artifact xử lý phải nằm ngoài `data/hosp`.

## 5. Định nghĩa trường thời gian

| Trường | Ý nghĩa sử dụng trong Phase 2 | Vai trò dự kiến |
|---|---|---|
| `admittime` | Thời điểm bắt đầu hospital admission | Mốc bắt đầu early window |
| `dischtime` | Thời điểm kết thúc hospital admission | Kiểm tra interval và lab sau xuất viện |
| `charttime` | Thời điểm gắn với việc lấy hoặc ghi nhận kết quả xét nghiệm | Trường thời gian chính để xác định lab nằm trong window |
| `storetime` | Thời điểm kết quả được lưu trong hệ thống | Dùng để audit hoặc làm cutoff tùy quyết định P2-D12 |

`diagnoses_icd` không cung cấp timestamp xác lập từng diagnosis. Vì vậy cohort chỉ được diễn giải là có phenotype được ghi nhận cho admission, không phải dự đoán trước thời điểm bác sĩ chẩn đoán.

## 6. Định nghĩa eligibility theo thành phần

### 6.1. Admission eligibility

Một admission ứng viên phải:

1. Có `hadm_id` và `subject_id` không thiếu trong `admissions`.
2. Có một quan hệ duy nhất giữa `hadm_id` và `subject_id`.
3. Có `admittime` và `dischtime` đọc được để áp dụng rule thời gian.
4. Thỏa chính sách interval âm và admission kết thúc sớm sau khi các chính sách này được duyệt.
5. Thỏa mọi giới hạn quần thể bổ sung nếu P2-D14 phê duyệt một giới hạn như vậy.

### 6.2. Diagnosis eligibility

Một admission có diagnosis đủ điều kiện trong Phase 2 khi có ít nhất một dòng `diagnoses_icd`:

1. Có `subject_id`, `hadm_id`, `icd_code` và `icd_version` không thiếu.
2. Có `hadm_id` tồn tại trong `admissions`.
3. Có `subject_id` khớp chủ của `hadm_id` trong `admissions`.

Phase 2 không yêu cầu ICD phải map thành công sang PheCode. Việc khử trùng mã, đánh giá mapping coverage, thống kê phenotype và chọn label set thuộc Phase 4.

### 6.3. Laboratory row eligibility

Một dòng lab được xem là ứng viên cho đánh giá thời gian khi:

1. Có `hadm_id`; không khôi phục hoặc suy diễn `hadm_id` bị thiếu.
2. `hadm_id` tồn tại trong `admissions`.
3. `subject_id` của dòng lab khớp chủ admission.
4. `itemid` không thiếu và tồn tại trong `d_labitems`.
5. `charttime` không thiếu và đọc được.
6. Đáp ứng điều kiện kết quả tối thiểu sẽ được chốt tại P2-D13.
7. Đáp ứng quan hệ với `admittime`, `dischtime`, early window và `storetime` theo các quyết định đã duyệt.

Chuẩn hóa đơn vị, xử lý outlier, imputation và aggregation không phải điều kiện xử lý của Phase 2; các bước này thuộc Phase 3.

## 7. Early-admission window

- Mốc bắt đầu: `admittime`.
- Trường thời gian chính: `charttime`.
- Độ dài chính thức: **CHỜ QUYẾT ĐỊNH P2-D08**.
- Công thức biên dự kiến: `0 <= charttime - admittime < window_hours`.
- Quan hệ bắt buộc với `dischtime`: **CHỜ QUYẾT ĐỊNH P2-D10 và P2-D11**.
- Chính sách `storetime` tại cutoff: **CHỜ QUYẾT ĐỊNH P2-D12**.

Công thức trên là quy ước kỹ thuật nháp để Task 2 so sánh nhất quán các kịch bản 6, 12 và 24 giờ. Nó chưa phải lựa chọn cửa sổ chính thức.

## 8. Danh mục rule

### 8.1. Rule đã chốt hoặc bắt buộc về cấu trúc

| Rule ID | Logic | Lý do | Đơn vị audit | Trạng thái |
|---|---|---|---|---|
| KEY-01 | Bắt đầu từ `admissions`; yêu cầu `hadm_id` và `subject_id` tồn tại | Giữ cohort ở cấp admission | Admission, subject | Đã chốt |
| KEY-02 | Một `hadm_id` chỉ ánh xạ tới một `subject_id` | Ngăn liên kết sai bệnh nhân | Admission | Đã chốt |
| LAB-01 | Không dùng dòng `labevents` thiếu `hadm_id` | Không thể gán chắc chắn vào admission | Lab row | Đã chốt, P2-D03 |
| LAB-02 | Không dùng dòng lab có `subject_id` sai so với chủ admission | Ngăn sai liên kết | Lab row, admission | Đã chốt, P2-D04 |
| LAB-03 | `itemid` phải tồn tại trong `d_labitems` | Bảo đảm xét nghiệm có khóa dictionary hợp lệ | Lab row, itemid | Bắt buộc kỹ thuật |
| LAB-04 | `charttime` phải đọc được | Cần để áp dụng early window | Lab row, admission | Bắt buộc kỹ thuật |
| DX-01 | Admission có ít nhất một diagnosis đủ khóa và khớp admission, subject | Bảo đảm có nguồn nhãn cho Phase 4 | Diagnosis row, admission | Đã chốt về nguyên tắc |
| JOIN-01 | Tổng hợp nhánh lab và diagnosis riêng ở cấp `hadm_id`, sau đó mới ghép | Tránh nhân dòng many-to-many | Admission | Đã chốt, P2-D05 |
| SRC-01 | Chỉ đọc dữ liệu HOSP gốc | Bảo toàn dữ liệu nguồn | File | Đã chốt, P2-D06 |
| AUD-01 | Ghi funnel trước và sau từng rule | Bảo đảm khả năng truy nguyên | Row, admission, subject | Bắt buộc |
| OUT-01 | Cohort cuối có một dòng duy nhất cho mỗi `hadm_id` | Đúng đơn vị phân tích | Admission | Bắt buộc |

### 8.2. Rule chưa được phép áp dụng

| Rule ID | Chủ đề | Logic đang chờ | Decision ID | Trạng thái |
|---|---|---|---|---|
| WIN-01 | Độ dài early window | Chọn 6, 12, 24 giờ hoặc phương án khác được duyệt | P2-D08 | Chờ quyết định |
| TIM-01 | Admission interval âm | Loại admission hoặc áp dụng phương án khác có lý do | P2-D09 | Chờ quyết định |
| TIM-02 | Admission kết thúc sớm | Giữ phần quan sát, yêu cầu đủ toàn window hoặc phương án khác | P2-D10 | Chờ quyết định |
| TIM-03 | Lab ngoài admission | Chỉ giữ lab trong interval hoặc áp dụng quy tắc khác | P2-D11 | Chờ quyết định |
| STO-01 | `storetime` tại cutoff | Chỉ audit, yêu cầu trước cutoff hoặc phương án khác | P2-D12 | Chờ quyết định |
| LAB-05 | Điều kiện lab tối thiểu | Ít nhất một kết quả hợp lệ hoặc yêu cầu khác có bằng chứng | P2-D13 | Chờ quyết định |
| POP-01 | Giới hạn quần thể | Không bổ sung hoặc thêm tuổi, loại admission hay tiêu chí có cơ sở | P2-D14 | Chờ quyết định |

Danh mục máy đọc tương ứng được lưu tại `tasks/task01_cohort_spec/outputs/rule_register_phase2_task01.csv`.

## 9. Thứ tự áp dụng rule dự kiến

Thứ tự cuối cùng chỉ được đóng băng sau Task 3. Khung hiện tại là:

```text
admissions
    -> kiểm tra khóa và quan hệ hadm_id-subject_id
    -> áp dụng policy interval admission đã duyệt
    -> áp dụng giới hạn quần thể nếu có
    -> tạo cờ diagnosis eligibility ở cấp hadm_id

labevents
    -> loại thiếu hadm_id
    -> loại hadm_id không tồn tại hoặc sai subject_id
    -> kiểm tra itemid và charttime
    -> áp dụng điều kiện kết quả tối thiểu
    -> áp dụng quan hệ thời gian và early window
    -> áp dụng policy storetime
    -> tổng hợp lab eligibility ở cấp hadm_id

admission keys + diagnosis flags + lab flags
    -> giữ admission thỏa toàn bộ rule đã duyệt
    -> tạo cohort một dòng mỗi hadm_id
```

## 10. Audit funnel bắt buộc

Với mỗi rule, phải lưu:

- `rule_order` và `rule_id`;
- tên và mô tả rule;
- đơn vị đếm;
- số dòng lab trước và sau;
- số admission trước và sau;
- số subject trước và sau;
- số bị loại riêng tại rule;
- số bị loại tích lũy;
- mẫu số dùng tính tỷ lệ;
- `reason_code`;
- decision ID và phiên bản cohort liên quan.

Không cộng số bị loại từ các nhóm chồng lấp nếu chưa xác định thứ tự áp dụng. Funnel chính thức phải dùng thứ tự rule đã đóng băng trong Task 3.

## 11. Output contract của cohort

Cohort tối thiểu ở Task 4 dự kiến có:

```text
subject_id
hadm_id
admittime
dischtime
selected_window_hours
has_eligible_lab
eligible_lab_count
eligible_item_count
has_diagnosis
cohort_version
```

Các trường thời gian, cờ và số đếm lab trong file cohort là metadata eligibility và audit. Chúng không mặc định là feature đầu vào mô hình.

## 12. Validation contract

Cohort phải vượt các kiểm tra sau trước khi đóng băng:

1. `hadm_id` không thiếu và duy nhất.
2. `subject_id` không thiếu và khớp `admissions`.
3. Mỗi `hadm_id` thuộc đúng một `subject_id`.
4. Mọi admission có diagnosis đủ điều kiện.
5. Mọi admission có ít nhất một lab đáp ứng rule đã duyệt trong early window.
6. Không có bằng chứng lab dùng để giữ admission vi phạm interval hoặc cutoff đã duyệt.
7. Tổng số khớp audit funnel.
8. Chạy lại trên cùng input và cùng phiên bản script tạo cùng cohort.
9. Artifact cuối có manifest và checksum hoặc dấu vết tương đương.

## 13. Nội dung ngoài phạm vi Phase 2

- Chuẩn hóa 10 `itemid` có nhiều đơn vị.
- Xử lý outlier, scaling và missing-value imputation.
- Chọn xét nghiệm cuối và aggregation `first`, `last`, `mean`, `median`, `min`, `max` hoặc `delta`.
- Chuyển dữ liệu lab long sang feature matrix X.
- ICD sang PheCode, khử trùng label, chọn threshold và label set Y.
- Chia train, validation và test thực tế.
- Huấn luyện hoặc đánh giá mô hình.

## 14. Câu hỏi cần chốt sau Task 2

1. Chọn cửa sổ 6, 12, 24 giờ hay phương án khác?
2. Loại 175 admission có `dischtime < admittime` hay dùng phương án khác?
3. Admission kết thúc trước độ dài window được giữ phần quan sát hay bị loại?
4. Có chỉ giữ lab thỏa `admittime <= charttime <= dischtime` không?
5. `storetime` chỉ dùng để audit hay phải không vượt cutoff?
6. Một admission chỉ cần ít nhất một kết quả hợp lệ hay phải đạt mức tối thiểu khác?
7. Có bổ sung giới hạn quần thể theo tuổi, loại admission hoặc tiêu chí khác không?

Task 2 phải cung cấp số liệu ảnh hưởng để hỗ trợ các quyết định này. Không câu hỏi nào được tự động chốt từ số liệu hoặc từ code.

## 15. Phê duyệt

```text
Trạng thái: CHƯA DUYỆT
Người xác nhận:
Ngày xác nhận:
Phiên bản được duyệt:
Nội dung còn chờ: P2-D08 đến P2-D14
```
