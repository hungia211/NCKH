# Phase 2 — Task Breakdown

## Task 1 — Soạn đặc tả cohort nháp

### Mục đích

Chuyển các quyết định đã có từ Phase 1 thành đặc tả rõ ràng, đồng thời liệt kê riêng những rule chưa được phép áp dụng.

### Công việc

- Xác nhận input và schema cần dùng: `admissions`, `labevents`, `diagnoses_icd`.
- Định nghĩa một admission đủ điều kiện theo từng thành phần: khóa, diagnosis, lab và thời gian.
- Định nghĩa chính xác các mốc `admittime`, `charttime`, `storetime`, `dischtime`.
- Ghi quy ước biên cửa sổ dưới dạng công thức; chưa điền số giờ chính thức khi chưa được duyệt.
- Phân biệt rule đã chốt, rule đề xuất và rule còn chờ.

### Đầu ra

- `COHORT_SPEC.md` phiên bản nháp.
- Bảng định nghĩa trường và rule.
- Danh sách câu hỏi cần người nghiên cứu/giảng viên quyết định.

### Điều kiện hoàn tất

Mỗi rule có mã, nguồn dữ liệu, logic, lý do, đơn vị đếm và trạng thái quyết định.

---

## Task 2 — So sánh các kịch bản cohort

### Mục đích

Cung cấp bằng chứng chi tiết để chọn cửa sổ và xử lý admission kết thúc sớm, không tự chọn thay người nghiên cứu.

### Công việc

- Tái lập số liệu 6/12/24 giờ từ Phase 1.
- Với mỗi cửa sổ, thống kê:
  - số admission và subject;
  - số dòng lab;
  - số itemid có mặt;
  - số admission kết thúc trước độ dài cửa sổ;
  - số admission có lab theo `charttime` nhưng kết quả được lưu sau cutoff theo `storetime`;
  - phân bố số loại xét nghiệm và số kết quả trên admission;
  - overlap giữa các kịch bản.
- Tách rõ các lựa chọn về `storetime`: chỉ dùng để audit hoặc yêu cầu kết quả đã được lưu trước cutoff.
- Không lọc raw data và không công bố một cửa sổ là lựa chọn cuối.

### Đầu ra

- Bảng CSV/XLSX so sánh kịch bản.
- `REPORT_phase2_task02.md` và `.docx`.
- Đề xuất có ưu, nhược điểm và ảnh hưởng số lượng của từng phương án.

### Điều kiện hoàn tất

Các số lượng đối soát được với Phase 1 và có đủ thông tin để ra quyết định về window, admission kết thúc sớm và `storetime`.

---

## Task 3 — Chốt inclusion/exclusion criteria

### Mục đích

Ghi nhận quyết định nghiên cứu trước khi tạo dữ liệu xử lý.

### Quyết định bắt buộc

1. Cửa sổ chính thức: 6, 12, 24 giờ hoặc phương án khác do người nghiên cứu phê duyệt.
2. Cách xử lý admission có `dischtime < admittime`.
3. Cách xử lý admission kết thúc trước độ dài cửa sổ.
4. Có loại toàn bộ lab trước `admittime` và sau `dischtime` hay không.
5. Chính sách `storetime` tại cutoff.
6. Điều kiện lab tối thiểu: chỉ cần ít nhất một kết quả hợp lệ hay có yêu cầu khác.
7. Có thêm giới hạn quần thể như tuổi hoặc loại admission hay không.

### Đầu ra

- `COHORT_SPEC.md` đã duyệt.
- `DECISION_LOG.md` cập nhật.
- Bảng rule theo thứ tự áp dụng.

### Điều kiện hoàn tất

Không còn rule bắt buộc nào ở trạng thái “Chờ quyết định”. Việc đồng ý phải được ghi bằng nội dung cụ thể, không suy ra từ im lặng hoặc từ code.

---

## Task 4 — Tạo cohort xử lý mới

### Mục đích

Áp dụng đúng đặc tả đã duyệt và tạo danh sách admission đủ điều kiện mà không sửa dữ liệu nguồn.

### Thứ tự xử lý dự kiến

Thứ tự cuối cùng phải lấy từ `COHORT_SPEC.md`. Khung hiện tại:

1. Bắt đầu từ `admissions` và xác minh `hadm_id`, `subject_id`.
2. Áp dụng rule interval admission đã duyệt.
3. Xây dựng tập diagnosis hợp lệ ở cấp `hadm_id`.
4. Quét `labevents`; loại dòng thiếu `hadm_id` và dòng sai chủ admission.
5. Áp dụng quan hệ thời gian và cửa sổ đã chốt.
6. Tổng hợp cờ/số lượng lab ở cấp `hadm_id`.
7. Giữ admission thỏa đồng thời điều kiện cohort và diagnosis.
8. Ghi audit funnel sau từng rule.

### Đầu ra

- Danh sách cohort tối thiểu gồm `subject_id`, `hadm_id` và các cờ audit cần thiết.
- Audit funnel ở cấp dòng, admission và subject.
- Danh sách record bị loại theo `reason_code`, khi kích thước phù hợp.
- Manifest mô tả input, thời gian chạy, script/version và output.
- `REPORT_phase2_task04.md` và `.docx`.

### Yêu cầu kỹ thuật

- Đọc `labevents` theo chunk hoặc engine phù hợp dữ liệu lớn.
- Không ghi đè file nguồn.
- Script chạy lại được và tạo output theo thư mục phiên bản/timestamp.
- Không làm feature aggregation hoặc PheCode mapping trong task này.

### Điều kiện hoàn tất

Funnel cộng/trừ chính xác, khóa cohort duy nhất và mọi admission còn lại đều thỏa toàn bộ rule đã duyệt.

---

## Task 5 — Kiểm tra, đóng băng và bàn giao cohort

### Mục đích

Xác nhận cohort có thể dùng làm đầu vào chung cho Phase 3 và Phase 4.

### Kiểm tra bắt buộc

- `hadm_id` duy nhất và không thiếu.
- `subject_id` không thiếu, khớp `admissions`.
- Mọi admission có diagnosis hợp lệ.
- Mọi admission có lab hợp lệ trong cửa sổ đã chọn.
- Không có record vi phạm interval hoặc cutoff đã chốt.
- Các tổng số khớp audit funnel.
- Chạy lại trên cùng input tạo cùng kết quả.
- Ghi checksum hoặc dấu vết tương đương cho artifact cuối.

### Đầu ra

- Cohort version cố định.
- Báo cáo kiểm tra và manifest.
- `REPORT_phase2_task05.md` và `.docx` tổng kết Phase 2.
- Hướng dẫn input cho Phase 3 Laboratory Features và Phase 4 Disease Labels.

### Điều kiện hoàn tất Phase 2

Cohort vượt tất cả kiểm tra, đặc tả và decision log khớp với code, đồng thời các giới hạn còn lại được ghi rõ.

---

## Quan hệ phụ thuộc

| Task | Phụ thuộc | Có thể bắt đầu ngay? |
|---|---|---|
| Task 1 | Phase 1 hoàn tất | Có |
| Task 2 | Kết quả Task 1 và Phase 1 | Có sau bản nháp Task 1 |
| Task 3 | Báo cáo Task 2 và quyết định của người nghiên cứu | Chưa |
| Task 4 | Task 3 đã chốt toàn bộ rule bắt buộc | Chưa |
| Task 5 | Cohort Task 4 đã tạo | Chưa |

## Ngoài phạm vi Phase 2

- Chuẩn hóa 10 itemid nhiều đơn vị.
- Xử lý outlier, missing-value imputation và scaling.
- Chọn xét nghiệm cuối và aggregation `first/last/mean/...`.
- Chuyển lab long → wide thành feature matrix X.
- ICD → PheCode và chọn label set Y.
- Train/validation/test split thực tế và huấn luyện mô hình.
