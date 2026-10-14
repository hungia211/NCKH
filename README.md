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

Đang ở Giai đoạn 1 — Data Exploration. Đã hoàn tất **6/7 task**: inventory HOSP, kiểm tra khóa/liên kết, khảo sát `labevents`, khảo sát `diagnoses_icd`, khảo sát thời gian và tổng hợp chất lượng/leakage. Mở [trạng thái Phase 1](phases/phase1_data_exploration/STATUS.md) để xem task đã làm, task tiếp theo và vị trí báo cáo.

Chưa có cohort, early-admission window, bộ đặc trưng lab, tập nhãn Phecode hoặc mô hình cuối được chốt. Không tự chọn các ngưỡng này trước khi khảo sát dữ liệu.

## Cấu trúc cần quan tâm

| Thư mục | Nội dung |
| --- | --- |
| `research_context/` | Bối cảnh, nguyên tắc và trạng thái chung của nghiên cứu. |
| `phases/` | Mã nguồn, kết quả và báo cáo được quản lý theo từng giai đoạn và task. |
| `data/hosp/` | Dữ liệu MIMIC-IV gốc, chỉ đọc. |
| `data/processed/` | Dữ liệu dẫn xuất; không dùng thay dữ liệu gốc. |
| `docs/` | Báo cáo khảo sát cũ còn giá trị tham khảo. |
| `legacy_ecg/` | Mã và tài liệu ECG cũ, không thuộc pipeline hiện tại. |
| `tmp/` | File làm việc kỹ thuật; không phải đầu ra nghiên cứu chính. |

Mã nguồn và tài liệu của đề tài ECG trước đây được lưu ở `legacy_ecg/` để tham khảo lịch sử; chúng không thuộc pipeline hiện tại.
