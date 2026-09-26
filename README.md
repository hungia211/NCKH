# MIMIC-IV laboratory multi-label research

Đề tài hiện tại nghiên cứu khả năng dùng dữ liệu xét nghiệm cận lâm sàng ở giai đoạn sớm của một lần nhập viện để dự đoán đồng thời các phenotype bệnh được ghi nhận cho admission đó trong **MIMIC-IV v3.1 HOSP**. Kết quả là gợi ý hỗ trợ chẩn đoán, không phải chẩn đoán xác định hay kết luận nhân quả.

## Bắt đầu từ đâu

- [Bối cảnh và nguyên tắc nghiên cứu](research_context/PROJECT_CONTEXT.md)
- [Trạng thái hiện tại](research_context/CURRENT_STATE.md)
- [Roadmap](research_context/ROADMAP.md)
- [Hướng dẫn cho agent](research_context/AGENT_GUIDE.md)
- [Phase 1 — Data Exploration](phases/phase1_data_exploration/README.md)
- [Tài liệu và báo cáo](docs/)

## Dữ liệu

Thư mục HOSP được xác nhận trong workspace hiện tại: `D:\UIT_thu\NCKH\data\hosp` (`data/hosp/`). Các bảng đầu vào dự kiến là `admissions.csv.gz`, `labevents.csv.gz`, `d_labitems.csv.gz`, `diagnoses_icd.csv.gz` và `d_icd_diagnoses.csv.gz`. Dữ liệu gốc được giữ nguyên và không đưa vào Git.

Đường dẫn đã được người dùng cung cấp là `D:\UIT\_thu\NCKH\data\hosp`, nhưng đường dẫn đó không tồn tại trong môi trường hiện tại. Hãy kiểm tra lại nếu chuyển máy hoặc checkout khác.

## Tình trạng

Đang ở giai đoạn chuẩn bị và data exploration. Chưa có cohort, early-admission window, bộ đặc trưng lab, tập nhãn Phecode hoặc mô hình cuối được chốt. Không tự chọn các ngưỡng này trước khi khảo sát dữ liệu.

Mã nguồn và tài liệu của đề tài ECG trước đây được lưu ở `legacy_ecg/` để tham khảo lịch sử; chúng không thuộc pipeline hiện tại.
