# Current state

## Repo overview

Repo hiện có hướng tài liệu và mã nguồn ban đầu cho MIMIC-IV-ECG trong `README.md`, `src/` và các báo cáo trong `docs/`. Đây là bối cảnh liên quan nhưng không thay thế research design laboratory multi-label trong `PROJECT_CONTEXT.md`.

## Dữ liệu và báo cáo đã biết

- Đã kiểm tra ngày 2026-09-21: `D:\UIT_thu\NCKH\data\hosp` tồn tại và chứa các file HOSP `.csv.gz`, bao gồm `admissions`, `labevents`, `d_labitems`, `diagnoses_icd`, `d_icd_diagnoses`.
- Đường dẫn người dùng cung cấp `D:\UIT\_thu\NCKH\data\hosp` hiện không tồn tại; dùng đường dẫn đã xác nhận ở trên cho workspace này.

- `docs/bao_cao_labevents_diagnoses_icd_join.md` ghi nhận khảo sát local của `labevents` và `diagnoses_icd`.
- Báo cáo local nêu khoảng 158 triệu dòng `labevents` và 6,36 triệu dòng `diagnoses_icd`.
- `labevents` có nhiều dòng thiếu `hadm_id`; chỉ các dòng có `hadm_id` mới ghép trực tiếp với admission.
- `d_labitems` và `d_icd_diagnoses` là dictionary, không phải bảng bệnh nhân.

## Chưa hoàn tất

- Chưa có cohort chính thức cho laboratory early-admission.
- Chưa quyết định window 6/12/24 giờ.
- Chưa có bộ aggregation cuối.
- Chưa có mapping ICD → Phecode và label set cuối.
- Chưa có final admission-level X + Y và patient-level split.
- Chưa có baseline multi-label và bộ đánh giá cuối.

## Giai đoạn 1 đã thực hiện

- Task 2 ngày 2026-09-26: `phases/phase1_data_exploration/tasks/task02_key_linkage/outputs/20260926T154108Z/`. Có 447.414 admission có cả lab và diagnosis khớp hadm_id + subject_id. Có 413 lab rows sai subject_id so với admissions; 447.688 admission có lab khớp cả hai khóa (447.689 nếu chỉ đếm hadm_id không null). Bất nhất chưa được sửa; nguyên nhân còn mở trước khi chốt cohort. CSV, Markdown và Word lưu cùng thư mục lần chạy.

- Toàn bộ Giai đoạn 1 được quản lý tại `phases/phase1_data_exploration/`.
- Task 1 nằm trong `phases/phase1_data_exploration/tasks/task01_inventory/`, gồm script, output và báo cáo.
- Task 2 nằm trong `phases/phase1_data_exploration/tasks/task02_key_linkage/`, gồm script, test và các lần chạy.
- Trang theo dõi duy nhất của Phase 1 là `phases/phase1_data_exploration/STATUS.md`.
- Ảnh QA và file kỹ thuật được gom trong `phases/phase1_data_exploration/.internal/`.
- Báo cáo Task 1 đã sửa lỗi mô tả số itemid: 976 trong events, 1.650 dòng dictionary.
- Task 1 có thêm từ điển dữ liệu tiếng Việt cho 44 cột của `admissions`, `labevents`, `d_labitems`, `diagnoses_icd` và `d_icd_diagnoses`, lưu ở `report/DATA_DICTIONARY_task01.docx` và `outputs/tables/DATA_DICTIONARY_task01.xlsx`.

## Tiến độ Phase 1

- Hoàn tất 7/7 task của Phase 1.
- Task 3: 79.439.965/158.374.764 dòng labevents đáp ứng định nghĩa nền tảng sử dụng; 447.165 admission và 817 itemid có ít nhất một dòng như vậy. Đây chưa phải dữ liệu đã làm sạch.
- Task 4: toàn bộ 6.364.488 dòng diagnoses_icd đủ khóa, khớp admission, subject và dictionary; có 545.497 admission và 28.583 cặp mã cùng phiên bản.
- Với thiết kế hiện tại lấy `hadm_id` làm đơn vị phân tích, 73.768.897 dòng `labevents` thiếu `hadm_id` không thể ghép xác định vào một admission và nhãn của admission đó. Các dòng này không thuộc tập ứng viên tạo feature huấn luyện theo admission; dữ liệu gốc vẫn được giữ nguyên.
- Quyết định ngày 2026-10-03: không khôi phục hoặc suy diễn `hadm_id` bằng `subject_id` và thời gian. Khi tạo dữ liệu xử lý, loại các dòng `labevents` thiếu `hadm_id`, ghi rõ số lượng và lý do loại; không sửa dữ liệu gốc. Task 5 chỉ khảo sát quan hệ thời gian trên các dòng có `hadm_id` hợp lệ.
- “Toàn bộ diagnoses_icd dùng được” ở Task 4 nghĩa là toàn bộ 6.364.488 dòng đạt kiểm tra cấu trúc và liên kết. Điều này chưa có nghĩa mọi dòng sẽ trở thành một nhãn cuối: pipeline sau còn xử lý trùng mã trong admission, map ICD sang Phecode và lựa chọn label set dựa trên khảo sát.
- Task 5: trong 79.439.965 dòng lab ứng viên, có 2.816.594 dòng trước `admittime`, 76.563.834 dòng trong admission, 53.761 dòng sau `dischtime` và 5.776 dòng thuộc admission có interval âm. Có 175 admission có `dischtime < admittime`.
- Độ phủ mô tả trong 6/12/24 giờ lần lượt là 189.225/308.886/400.315 admission có lab; khi yêu cầu thêm diagnosis còn 189.102/308.719/400.092 admission. Chưa chọn cửa sổ chính thức.
- Task 6 đã ghi 11 vấn đề chất lượng và 6 nguy cơ leakage. Có 446.891 admission có lab ứng viên và diagnosis; 432.410 admission có diagnosis và ít nhất một lab nằm trong admission hợp lệ.
- Task 7 đã hoàn tất tại `phases/phase1_data_exploration/tasks/task07_phase1_summary/`. Báo cáo định kỳ nằm ở `report/REPORT_task07.docx`; các quyết định mở và kế hoạch Phase 2 đề xuất được lưu thành CSV riêng.
- Bước tiếp theo là cùng người nghiên cứu duyệt đặc tả Phase 2 — Cohort Definition trước khi tạo dataset xử lý mới.
- Kế hoạch Phase 2 đã được tạo tại `phases/phase2_cohort_definition/`, gồm 5 task: đặc tả nháp, so sánh kịch bản, chốt quyết định, tạo cohort và kiểm tra/đóng băng cohort.
- Task 1 Phase 2 hoàn tất bản nháp ngày 2026-10-14: `COHORT_SPEC.md` phiên bản 0.1, rule register, danh sách câu hỏi cần quyết định và báo cáo Task 1 đã được tạo. Đặc tả chưa được duyệt để chạy lọc; P2-D08 đến P2-D14 vẫn chờ quyết định.
- Tiến độ thực thi Phase 2 là 1/5. Task 2 sẵn sàng; chưa chạy lọc tạo cohort.
- Phát hiện cần theo dõi: 46.579% `labevents` thiếu `hadm_id` và đã quyết định loại khỏi dữ liệu xử lý; 10 itemid có nhiều đơn vị; 175 admission có thời lượng âm; chưa có quyết định cohort/window/threshold.

## Chuyển hướng đề tài

Hướng nghiên cứu hiện tại là laboratory data → multi-label disease prediction. Mã và tài liệu ECG trước đây được lưu ở `legacy_ecg/` để tham khảo, không dùng làm điểm khởi đầu cho pipeline mới. Dữ liệu HOSP gốc tại `data/hosp/` được giữ nguyên.

Ngày 2026-09-21 đã chuyển các thành phần ECG cũ (script trong `src/`, notebook, tài liệu ECG, metadata ECG, record mẫu và hình ECG) sang `legacy_ecg/`. Các báo cáo HOSP còn liên quan vẫn ở `docs/`. Việc này là lưu trữ có thể phục hồi, không phải xóa vĩnh viễn.

## Ý tưởng mở rộng longitudinal

Ngày 2026-10-12 đã ghi nhận hướng mở rộng tại `research_context/LONGITUDINAL_EXTENSION.md`: khi bệnh nhân bước vào một admission mới và đã có xét nghiệm giai đoạn sớm, kết hợp các xét nghiệm đó với lịch sử admission trước để dự đoán phenotype được ghi nhận trong admission mới. Pipeline admission-level hiện tại vẫn là hướng chính; longitudinal chỉ được triển khai sau khi baseline chính hoàn thành.

Cập nhật file này khi một quyết định hoặc đầu ra quan trọng đã được xác nhận.
