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

- Toàn bộ Giai đoạn 1 được quản lý tại `phases/phase1_data_exploration/`.
- Hai script đọc-only nằm trong `phases/phase1_data_exploration/scripts/`.
- Inventory và summary JSON nằm trong `phases/phase1_data_exploration/outputs/machine_readable/`.
- CSV và workbook Excel dành cho người đọc nằm trong `phases/phase1_data_exploration/outputs/tables/`.
- Báo cáo kết quả ban đầu nằm tại `phases/phase1_data_exploration/REPORT.md`.
- Phát hiện cần theo dõi: 46.579% `labevents` thiếu `hadm_id`; 10 itemid có nhiều đơn vị; một số admission có thời lượng âm; chưa có quyết định cohort/window/threshold.

## Chuyển hướng đề tài

Hướng nghiên cứu hiện tại là laboratory data → multi-label disease prediction. Mã và tài liệu ECG trước đây được lưu ở `legacy_ecg/` để tham khảo, không dùng làm điểm khởi đầu cho pipeline mới. Dữ liệu HOSP gốc tại `data/hosp/` được giữ nguyên.

Ngày 2026-09-21 đã chuyển các thành phần ECG cũ (script trong `src/`, notebook, tài liệu ECG, metadata ECG, record mẫu và hình ECG) sang `legacy_ecg/`. Các báo cáo HOSP còn liên quan vẫn ở `docs/`. Việc này là lưu trữ có thể phục hồi, không phải xóa vĩnh viễn.

Cập nhật file này khi một quyết định hoặc đầu ra quan trọng đã được xác nhận.
