# Research context for agents

Thư mục này là điểm đọc đầu tiên cho agent khi làm việc với đề tài MIMIC-IV laboratory data.

## Tài liệu

- [PROJECT_CONTEXT.md](PROJECT_CONTEXT.md): câu hỏi nghiên cứu, định nghĩa dữ liệu, multi-label target, early-admission window, nguyên tắc leakage và giới hạn diễn giải.
- [AGENT_GUIDE.md](AGENT_GUIDE.md): cách agent kiểm tra, thực hiện và báo cáo từng task.
- [ROADMAP.md](ROADMAP.md): các giai đoạn triển khai và đầu ra dự kiến.
- [CURRENT_STATE.md](CURRENT_STATE.md): trạng thái repo và các việc đã biết.
- [Phase 1 Data Exploration](../phases/phase1_data_exploration/README.md): task, script, báo cáo và kết quả khảo sát HOSP.

## Vị trí dữ liệu

Dữ liệu MIMIC-IV v3.1 HOSP trên máy hiện tại nằm tại `D:\UIT_thu\NCKH\data\hosp` (`data/hosp/`). Đây là dữ liệu gốc, chỉ đọc. Đường dẫn người dùng gõ `D:\UIT\_thu\NCKH\data\hosp` không tồn tại trên máy hiện tại; cần xác minh lại khi làm việc ở môi trường khác.

## Quy tắc cập nhật

1. Không sửa dữ liệu gốc để thử nghiệm.
2. Ghi lại mọi quyết định lọc cohort, window, aggregation và threshold.
3. Cập nhật `CURRENT_STATE.md` sau mỗi bước lớn.
4. Khi thay đổi research design, ghi rõ vấn đề, phương án và tác động trước khi triển khai.
5. Các tài liệu cũ trong `docs/` vẫn được giữ nguyên.
