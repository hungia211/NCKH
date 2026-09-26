# Giai đoạn 1 — Data Exploration

Mục tiêu của giai đoạn này là hiểu cấu trúc, độ đầy đủ và quan hệ giữa các bảng HOSP trước khi định nghĩa cohort, early-admission window, feature hoặc label threshold. Giai đoạn này không tạo dataset huấn luyện và không lọc mạnh dữ liệu.

## Task 1 — Inventory toàn bộ bảng

- Liệt kê các file HOSP, kích thước nén, số dòng, số cột và schema.
- Xác định bảng patient-level, admission-level, event-level và dictionary.
- Đầu ra: `outputs/machine_readable/hosp_inventory.json`, các bảng CSV/XLSX và bảng tóm tắt trong báo cáo.

## Task 2 — Khảo sát khóa và liên kết

- Kiểm tra `subject_id`, `hadm_id`, `itemid`, `icd_code + icd_version`.
- Đo số key duy nhất, admission có nhiều patient/admission, orphan khi join dictionary.
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

- Đã tạo script inventory đọc-only: `scripts/explore_hosp.py`.
- Task 1 hoàn tất: inventory đủ 22 bảng.
- Task 2 bắt đầu: đã có kiểm tra ban đầu cho admissions, labevents và diagnoses_icd; cần tiếp tục đo overlap và orphan theo khóa trong các task kế tiếp.
