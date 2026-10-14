# Giai đoạn 1 — Data Exploration

Mục tiêu của giai đoạn này là hiểu cấu trúc, độ đầy đủ và quan hệ giữa các bảng HOSP trước khi định nghĩa cohort, early-admission window, feature hoặc label threshold. Giai đoạn này không tạo dataset huấn luyện và không lọc mạnh dữ liệu.

## Task 1 — Inventory toàn bộ bảng

- Liệt kê các file HOSP, kích thước nén, số dòng, số cột và schema.
- Xác định bảng patient-level, admission-level, event-level và dictionary.
- Đầu ra: `tasks/task01_inventory/outputs/machine_readable/hosp_inventory.json`, các bảng CSV/XLSX và báo cáo trong cùng thư mục task.

## Task 2 — Khảo sát khóa và liên kết

- Kiểm tra `subject_id`, `hadm_id`, `itemid`, `icd_code + icd_version`.
- Đo số khóa duy nhất, số admission trên mỗi bệnh nhân, tính nhất quán một hadm_id thuộc một subject_id và orphan khi join dictionary.
- Đầu ra: báo cáo liên kết và cảnh báo join.

## Task 3 — Khảo sát `labevents`

- Đếm admission có lab, số loại `itemid`, tần suất item, missingness của `hadm_id`, `valuenum`, `valueuom` và thời gian.
- Phân tích đơn vị đo theo item và phân bố số lần đo theo admission.
- Chưa chọn top lab và chưa chọn aggregation.

## Task 4 — Khảo sát diagnosis

- Đếm admission có diagnosis, số ICD-9/ICD-10, số code duy nhất và số diagnosis/admission.
- Join dictionary để mô tả code nhưng không dùng dictionary thay cho `diagnoses_icd`.
- Chuẩn bị đầu vào cho bước ICD → Phecode sau này; chưa chốt phenotype hoặc threshold.

## Task 5 — Khảo sát admission và thời gian

- Kiểm tra `admittime`, `dischtime`, thời lượng admission và quan hệ thời gian lab-admission.
- Đo độ phủ lab trong các cửa sổ ứng viên 6/12/24 giờ như thống kê mô tả; chưa chọn cửa sổ chính thức.

## Task 6 — Kiểm tra chất lượng và nguy cơ leakage

- Kiểm tra timestamp, giá trị số, đơn vị, duplicate, orphan và record thiếu `hadm_id`.
- Tách rõ dữ liệu được ghi nhận trong admission với thời điểm diagnosis ICD không có timestamp chẩn đoán chính xác.

## Task 7 — Báo cáo và quyết định chuyển giai đoạn

- Tổng hợp số liệu, vấn đề dữ liệu và lựa chọn cần người nghiên cứu quyết định.
- Chỉ chuyển sang Giai đoạn 2 sau khi các vấn đề ảnh hưởng cohort đã được ghi nhận.

## Trạng thái

## Giải thích các task tiếp theo

### Task 2 Kiểm tra có ghép đúng dữ liệu hay không

Mỗi bệnh nhân được nhận diện bằng subject_id; mỗi lần nhập viện bằng hadm_id. Một bệnh nhân có thể nhập viện nhiều lần. Cần kiểm tra hadm_id trong labevents và diagnoses_icd có tồn tại trong admissions, đồng thời subject_id có khớp không. Orphan là bản ghi có khóa nhưng không tìm thấy bản ghi tương ứng ở bảng được nối; khác với khóa bị thiếu.

Tiếp theo đếm admission chỉ có lab, chỉ có diagnosis, có cả hai và không có cả hai. Đây là phép đo overlap, giúp biết bao nhiêu admission có khả năng xây dựng cả X và Y. Chưa thể suy ra số có cả hai từ hai tổng riêng lẻ đã báo cáo.

Đầu ra dự kiến: bảng kiểm tra khóa và bảng độ phủ admission, kèm số bản ghi không khớp. Phải kiểm tra tính duy nhất của dictionary trước khi nối. Không nối trực tiếp toàn bộ lab với toàn bộ diagnosis theo hadm_id để tạo feature: nhiều lab và nhiều diagnosis có thể nhân số dòng. Hai nhánh sẽ được tổng hợp riêng rồi ghép ở cấp admission.

Với lab thiếu `hadm_id`, giữ nguyên dữ liệu gốc và thống kê riêng. Theo quyết định ngày 2026-10-03, không khôi phục hoặc suy diễn `hadm_id` bằng `subject_id` và thời gian; các dòng này sẽ bị loại khi tạo dữ liệu xử lý admission-level, kèm số lượng và lý do loại trong báo cáo làm sạch.

### Task 3 Kiểm tra xét nghiệm nào có dữ liệu sử dụng được

Với từng itemid, nối d_labitems để lấy tên, loại mẫu và nhóm xét nghiệm. Đếm cả số lần đo và số admission được đo: một xét nghiệm lặp nhiều lần ở ít admission không có nghĩa là phủ nhiều admission.

Đếm kết quả có valuenum, kết quả chỉ có value dạng chữ, đơn vị bị thiếu và các đơn vị xuất hiện. Một giá trị số thiếu không đồng nghĩa toàn bộ kết quả xét nghiệm bị mất. Với 10 itemid nhiều đơn vị, cần xem cụ thể từng đơn vị và số dòng, chưa tự đổi hoặc gộp.

Đầu ra dự kiến: bảng tần suất toàn bộ itemid, bảng đơn vị và phân bố số lần đo mỗi admission. Các bảng này giúp đề xuất lab và cách tổng hợp ở Phase 3; danh sách 30 lab hiện có chỉ là phần hiển thị các mục phổ biến.

### Task 4 Hiểu dữ liệu chẩn đoán trước khi tạo nhãn

Đếm riêng số dòng ICD-9 và ICD-10, số mã duy nhất của từng phiên bản, số admission chứa từng mã và số diagnosis mỗi admission. Con số 9.143 và 19.440 hiện tại là số mã duy nhất, không phải số dòng diagnosis hay số bệnh nhân.

Kiểm tra mã thiếu, mã không khớp dictionary và mã lặp trong cùng admission; giữ mã dưới dạng chuỗi để không mất số 0 đầu. Dùng cả icd_code và icd_version khi nối dictionary.

Đầu ra dự kiến: bảng tần suất ICD, phân bố diagnosis mỗi admission và bảng lỗi mapping dictionary. ICD sang Phecode và chọn bộ nhãn cuối thuộc Phase 4, chưa thực hiện ở task này.

### Task 5 Hiểu xét nghiệm diễn ra khi nào

Tính khoảng cách `charttime` so với `admittime` cho lab có `hadm_id` hợp lệ. Không dùng Task 5 để khôi phục `hadm_id` còn thiếu. Thống kê lab trước nhập viện, trong admission và sau xuất viện; kiểm tra thêm `storetime` để đánh giá khi nào kết quả được lưu. Việc định nghĩa thời điểm thông tin sẵn có cần được ghi rõ trước modeling.

So sánh số admission và số loại xét nghiệm có dữ liệu trong 6, 12 và 24 giờ đầu. Công bố rõ mốc bắt đầu, cách tính biên cửa sổ và cách xử lý admission kết thúc sớm. Kiểm tra số admission có dischtime trước admittime và mức độ bất thường trước khi tính độ phủ.

Đầu ra dự kiến: bảng độ phủ theo cửa sổ và báo cáo bất thường thời gian. Số liệu này phục vụ quyết định window ở Phase 2; chưa mặc định chọn 24 giờ.

### Task 6 Tổng hợp vấn đề chất lượng và leakage

Tổng hợp phát hiện từ Task 2 đến Task 5: khóa sai, bản ghi trùng, đơn vị không nhất quán, thời gian bất thường và kết quả không chuyển được sang số. Phân biệt một bản ghi bị lặp với các lần đo thực sự khác nhau, không tự xóa theo hadm_id và itemid.

Đánh giá nguy cơ sử dụng xét nghiệm muộn và nguy cơ các admission cùng bệnh nhân xuất hiện ở nhiều tập dữ liệu. Các bước học từ dữ liệu như điền thiếu và chuẩn hóa sau này phải được fit trên train. diagnoses_icd không cung cấp thời điểm bác sĩ xác lập từng diagnosis, nên không thể dùng nó để khẳng định dự đoán trước chẩn đoán.

Đầu ra dự kiến: danh sách vấn đề, số dòng/admission bị ảnh hưởng, bằng chứng và phương án xử lý cần xem xét. Chưa áp dụng quy tắc loại tự động.

### Task 7 Chốt báo cáo và các quyết định còn thiếu

Tổng hợp các bảng kết quả, định nghĩa từng chỉ số, script tạo ra chúng và các vấn đề còn mở. Báo cáo quyết định loại lab thiếu `hadm_id`, ảnh hưởng đến số lượng dữ liệu, phương án cohort và các cửa sổ thời gian còn cần người nghiên cứu quyết định.

Đầu ra dự kiến: báo cáo Markdown và Word cập nhật, bảng Excel/CSV, nhật ký quyết định. Chỉ chuyển sang Phase 2 khi các vấn đề quan trọng đối với cohort đã được giải quyết hoặc có phương án xử lý được thống nhất.

## Tiến độ thực tế

- Đã tạo script inventory đọc-only: `tasks/task01_inventory/scripts/explore_hosp.py`.
- Task 1 hoàn tất: inventory đủ 22 bảng.
- Task 2 đã chạy đầy đủ ngày 2026-09-26: kiểm tra khóa tham chiếu, orphan, subject_id theo admission, overlap và phân bố admission trên bệnh nhân. Kết quả tại `tasks/task02_key_linkage/outputs/20260926T154108Z/`. Phát hiện 413 dòng lab bất nhất subject_id cần truy nguyên; không tự sửa nguồn hoặc chốt cohort.
- Task 3 hoàn tất ngày 2026-09-30: khảo sát toàn bộ 158.374.764 dòng labevents. Kết quả tại `tasks/task03_labevents/outputs/20260930T163439Z/`. Có 79.439.965 dòng và 447.165 admission đáp ứng định nghĩa nền tảng sử dụng; chưa xóa hoặc sửa dòng nào.
- Task 4 hoàn tất ngày 2026-09-30: khảo sát toàn bộ 6.364.488 dòng diagnoses_icd. Kết quả tại `tasks/task04_diagnoses/outputs/20260930T164935Z/`. Toàn bộ dòng khớp admission, bệnh nhân và dictionary; ghi nhận 388 dòng trùng mã trong admission và 10 admission có nhiều hơn một dòng seq_num = 1.
- Task 5 hoàn tất ngày 2026-10-03: khảo sát toàn bộ 79.439.965 dòng lab ứng viên tại `tasks/task05_admission_time/outputs/20261003T140751Z/`. Có 76.563.834 dòng nằm trong admission hợp lệ; độ phủ lần lượt là 189.225, 308.886 và 400.315 admission trong 6, 12 và 24 giờ đầu. Ba cửa sổ chỉ là mô tả.
- Task 6 hoàn tất ngày 2026-10-03 tại `tasks/task06_quality_leakage/outputs/20261003T141918Z/`. Đã lập danh mục 11 vấn đề chất lượng, 6 nguy cơ leakage và thống kê cohort có cả diagnosis cùng lab 6/12/24 giờ lần lượt là 189.102, 308.719 và 400.092 admission.
- Task 7 hoàn tất ngày 2026-10-04 tại `tasks/task07_phase1_summary/`. Báo cáo định kỳ tổng hợp Task 1–6, nhật ký quyết định và kế hoạch Phase 2 đề xuất đã được tạo; Phase 1 hoàn tất 7/7 task.
