# Báo cáo định kỳ — Tổng kết Giai đoạn 1: Khảo sát dữ liệu MIMIC-IV HOSP

**Ngày báo cáo:** 04/10/2026  
**Phạm vi:** Task 1 đến Task 7  
**Dữ liệu:** `D:\UIT_thu\NCKH\data\hosp` (chỉ đọc)

## 1. Mục tiêu nghiên cứu

Nghiên cứu xây dựng mô hình Machine Learning sử dụng dữ liệu xét nghiệm giai đoạn sớm của một hospital admission để dự đoán đồng thời các phenotype bệnh được ghi nhận cho admission đó. Đơn vị phân tích là `hadm_id`; bài toán là multi-label classification; chia tập theo `subject_id`.

## 2. Tóm tắt điều hành

- Hoàn tất 7/7 task của Phase 1 và không sửa dữ liệu HOSP gốc.
- Đã khảo sát 22 bảng; phân tích sâu các bảng admission, lab và diagnosis.
- Có 446.891 admission có cả lab ứng viên và diagnosis; 432.410 admission có lab nằm trong admission hợp lệ và có diagnosis.
- Các kịch bản 6/12/24 giờ có lần lượt 189.102/308.719/400.092 admission có cả lab và diagnosis.
- Đã chốt loại lab thiếu `hadm_id` khỏi dataset xử lý admission-level, tổng hợp X/Y riêng và chia tập theo bệnh nhân.
- Chưa chọn cửa sổ chính thức, cohort cuối, quy tắc đơn vị/giá trị hoặc label set PheCode.

## 3. Tiến độ Task 1–7

| Task | Nội dung | Trạng thái | Kết quả chính |
|---:|---|---|---|
| 1 | Inventory HOSP | Hoàn tất | Kiểm kê 22 bảng, schema và quy mô; bổ sung từ điển tiếng Việt cho 44 cột của 5 bảng chính. |
| 2 | Khóa và liên kết | Hoàn tất | Kiểm tra toàn bộ khóa, orphan, sai bệnh nhân và bốn nhóm overlap admission. |
| 3 | Khảo sát labevents | Hoàn tất | Đánh giá 158.374.764 dòng về khả năng liên kết, kết quả, đơn vị và độ phủ itemid. |
| 4 | Khảo sát diagnoses_icd | Hoàn tất | Đánh giá 6.364.488 dòng ICD-9/10, dictionary, trùng mã và phân bố diagnosis/admission. |
| 5 | Admission và thời gian | Hoàn tất | Đo quan hệ charttime/admittime/dischtime và độ phủ mô tả trong 6/12/24 giờ. |
| 6 | Chất lượng và leakage | Hoàn tất | Lập danh mục 11 vấn đề chất lượng, 6 nguy cơ leakage và mức sẵn sàng của cohort. |
| 7 | Tổng hợp Phase 1 | Hoàn tất | Tổng hợp kết quả, quyết định, vấn đề còn mở và đề xuất kế hoạch Phase 2. |

## 4. Quy mô và cấu trúc dữ liệu

| Bảng | Quy mô | Đơn vị dòng | Vai trò |
|---|---:|---|---|
| admissions | 546.028 | 546.028 admission | Xác định admission và mốc nhập/xuất viện |
| patients | 364.627 | 364.627 bệnh nhân | Đối chiếu bệnh nhân; chia tập theo subject_id |
| labevents | 158.374.764 | Kết quả xét nghiệm | Nguồn feature X |
| d_labitems | 1.650 | Từ điển xét nghiệm | Tên, bệnh phẩm, category của itemid |
| diagnoses_icd | 6.364.488 | Mã ICD theo admission | Nguồn nhãn Y trước ánh xạ PheCode |
| d_icd_diagnoses | 112.107 khóa | Từ điển ICD | Mô tả mã theo icd_code + icd_version |

## 5. Khả năng liên kết ở cấp admission

| Nhóm admission | Số admission | Tỷ lệ | Ý nghĩa |
|---|---:|---:|---|
| Có cả lab và diagnosis | 447.414 | 81,940% | Điểm xuất phát liên kết; chưa phải cohort cuối |
| Chỉ có lab | 274 | 0,050% | Không có nhãn diagnosis cho thiết kế hiện tại |
| Chỉ có diagnosis | 98.083 | 17,963% | Không có feature lab liên kết trực tiếp |
| Không có cả hai | 257 | 0,047% | Không dùng cho bài toán X + Y hiện tại |

Có 413 dòng lab sai `subject_id` so với chủ sở hữu `hadm_id`. Nếu nối trực tiếp nhiều lab với nhiều diagnosis, phép nối dự kiến tạo khoảng 1,685 tỷ dòng; vì vậy hai nhánh phải được tổng hợp riêng.

## 6. Kết quả khảo sát labevents

| Chỉ số | Số dòng | Tỷ lệ |
|---|---:|---:|
| Tổng labevents | 158.374.764 | 100,000% |
| Có hadm_id | 84.605.867 | 53,421% |
| Khớp admission và subject_id | 84.605.454 | 53,421% |
| Có kết quả số | 136.884.423 | 86,431% |
| Chỉ có kết quả chữ | 5.427.558 | 3,427% |
| Không có kết quả số hoặc chữ | 16.062.783 | 10,142% |
| Đủ nền tảng sử dụng của Task 3 | 79.439.965 | 50,159% |

Có 447.165 admission và 817 itemid có ít nhất một dòng đạt định nghĩa nền tảng sử dụng. Có 10 itemid xuất hiện với nhiều chuỗi đơn vị. Trung vị số dòng xét nghiệm trên một admission là 85; thống kê này chưa giới hạn cửa sổ sớm.

## 7. Kết quả khảo sát diagnosis

- Toàn bộ 6.364.488 dòng đủ khóa, khớp admission, bệnh nhân và dictionary.
- Có 545.497 admission, 2.908.741 dòng ICD-9 và 3.455.747 dòng ICD-10.
- Có 9.143 mã ICD-9, 19.440 mã ICD-10 và 28.583 cặp `icd_code + icd_version`.
- Trung vị 10 diagnosis/admission; lớn nhất 57 dòng diagnosis.
- Có 388 dòng dư trùng mã trong admission và 10 admission có nhiều hơn một `seq_num = 1`.
- Dữ liệu đủ nền tảng để ánh xạ PheCode, nhưng chưa thể coi toàn bộ ICD là label set cuối.

## 8. Thời gian và ba kịch bản cửa sổ

Quy ước khảo sát là `0 <= charttime - admittime < số giờ`, chỉ trên admission có interval không âm.

| Cửa sổ | Dòng lab | Admission có lab | Admission có lab + diagnosis | Tỷ lệ toàn admission |
|---|---:|---:|---:|---:|
| 6 giờ | 4.701.358 | 189.225 | 189.102 | 34,632% |
| 12 giờ | 9.786.000 | 308.886 | 308.719 | 56,539% |
| 24 giờ | 16.805.692 | 400.315 | 400.092 | 73,273% |

Cửa sổ dài hơn tăng độ phủ nhưng cũng tăng khả năng sử dụng thông tin xuất hiện muộn. Phase 1 chưa lựa chọn 6, 12 hay 24 giờ.

## 9. Danh mục vấn đề chất lượng

| Nguồn | Vấn đề | Mức ảnh hưởng | Hướng xử lý/điểm cần chốt |
|---|---|---:|---|
| labevents | Thiếu hadm_id | 73.768.897 dòng; 46,579% | Loại khỏi dữ liệu xử lý admission-level; không khôi phục khóa |
| labevents | subject_id sai so với admission | 413 dòng | Loại khỏi tập ứng viên; lưu audit count |
| labevents | Không có kết quả số hoặc chữ | 16.062.783 dòng; 10,142% | Không dùng làm giá trị feature |
| labevents | Thiếu storetime | 224.118 dòng ứng viên | Không loại chỉ vì thiếu storetime; tiếp tục kiểm soát tính sẵn có |
| labevents | storetime trước charttime | 762 dòng | Kiểm tra trước khi dùng storetime |
| lab item | Nhiều chuỗi đơn vị | 10/976 itemid | Xem xét từng itemid trước chuẩn hóa |
| admissions | dischtime trước admittime | 175 admission | Không dùng interval âm cho cohort/window |
| lab/admission | Lab trước admittime | 2.816.594 dòng | Không đưa vào cửa sổ bắt đầu tại admittime nếu chưa có quy tắc khác |
| lab/admission | Lab sau dischtime | 53.761 dòng | Không đưa vào feature của admission |
| diagnoses_icd | Trùng mã trong admission | 388 dòng dư | Khử trùng khi tạo nhãn admission-phenotype |
| diagnoses_icd | Nhiều seq_num = 1 | 10 admission | Không giả định primary diagnosis luôn duy nhất |

## 10. Kiểm soát leakage

| Nguy cơ | Kiểm soát |
|---|---|
| Xét nghiệm muộn | Chọn cửa sổ sớm đã được duyệt; chỉ tạo feature trong cửa sổ đó. |
| Cùng bệnh nhân ở nhiều tập | Group split theo subject_id. |
| Tiền xử lý học từ toàn bộ dữ liệu | Fit imputation, scaling và lựa chọn học từ dữ liệu chỉ trên train. |
| Chọn nhãn dựa trên test | Chốt protocol lựa chọn nhãn trước đánh giá cuối. |
| Diễn giải sai thời điểm diagnosis | Chỉ nói phenotype được ghi nhận cho admission. |
| Nhân dòng khi join | Tổng hợp X và Y riêng theo hadm_id, sau đó mới nối. |

## 11. Quyết định và vấn đề còn mở

| Mã | Trạng thái | Chủ đề | Nội dung |
|---|---|---|---|
| D01 | Đã chốt | Đơn vị phân tích | Một hàng cuối cùng đại diện một hadm_id. |
| D02 | Đã chốt | Chia tập | Chia train/validation/test theo subject_id. |
| D03 | Đã chốt | Lab thiếu hadm_id | Không khôi phục hoặc suy diễn; loại khỏi dataset xử lý admission-level và ghi audit. |
| D04 | Đã chốt | Cách ghép X và Y | Tổng hợp nhánh lab và nhánh nhãn riêng ở cấp hadm_id rồi mới ghép. |
| D05 | Đã chốt | Diễn giải diagnosis | Không coi diagnoses_icd là timestamp chẩn đoán và không tuyên bố dự đoán trước bác sĩ. |
| D06 | Chờ quyết định | Early-admission window | Chọn 6, 12 hoặc 24 giờ sau khi cân bằng độ phủ và nguy cơ thông tin muộn. |
| D07 | Chờ quyết định | Cohort | Chốt inclusion/exclusion, cách xử lý admission interval âm và admission kết thúc sớm. |
| D08 | Chờ quyết định | Đơn vị xét nghiệm | Quy tắc cho 10 itemid có nhiều chuỗi đơn vị. |
| D09 | Chờ quyết định | Giá trị xét nghiệm | Quy tắc dùng kết quả chữ, missing và outlier. |
| D10 | Chờ khảo sát Phase 4 | Nhãn phenotype | Map ICD→PheCode, đo coverage và frequency rồi mới chọn threshold/label set. |

## 12. Đánh giá kết thúc Phase 1

Phase 1 đã hoàn thành mục tiêu khảo sát cấu trúc, độ đầy đủ, liên kết, thời gian và rủi ro dữ liệu. Dữ liệu chưa phải dataset sạch để huấn luyện vì cohort và các quy tắc biến đổi chưa được chốt. Có đủ bằng chứng để bắt đầu thiết kế Phase 2 ở mức đặc tả và so sánh kịch bản.

## 13. Đề xuất kế hoạch Phase 2 — Cohort Definition

Đây là kế hoạch đề xuất để thảo luận; chưa phải quyết định nghiên cứu đã chốt.

| Task | Nội dung | Công việc | Đầu ra | Trạng thái |
|---|---|---|---|---|
| 2.1 | Soạn cohort specification | Tập hợp tiêu chí bắt buộc và lựa chọn còn mở; định nghĩa mốc thời gian và biên cửa sổ. | Bản đặc tả cohort để duyệt | Chờ duyệt |
| 2.2 | So sánh kịch bản cohort | Lập bảng 6/12/24 giờ theo admission, subject, số lab, thời lượng và nhóm bị loại. | Bảng so sánh có số liệu | Đề xuất |
| 2.3 | Chốt inclusion/exclusion | Quyết định interval âm, admission kết thúc sớm, lab ngoài admission và dòng sai subject_id. | Decision log và quy tắc lọc | Chờ quyết định |
| 2.4 | Tạo cohort xử lý mới | Áp dụng quy tắc đã duyệt, không ghi đè nguồn và ghi funnel trước/sau từng bước. | Danh sách hadm_id/subject_id và audit counts | Sau 2.1–2.3 |
| 2.5 | Kiểm tra và đóng băng cohort | Kiểm tra khóa duy nhất, liên kết, thời gian, overlap và khả năng tái lập. | Cohort manifest/version | Sau 2.4 |

### Các quyết định cần thống nhất trước khi tạo cohort

1. Mục tiêu cân bằng giữa độ phủ và tính sớm khi chọn 6/12/24 giờ.
2. Xử lý admission có `dischtime < admittime` và admission kết thúc trước độ dài cửa sổ.
3. Có yêu cầu tối thiểu về loại xét nghiệm hoặc số lượng kết quả trong cửa sổ hay không.
4. Cách kiểm soát `storetime` khi kết quả được lưu sau mốc dự đoán.
5. Có giới hạn quần thể bổ sung theo tuổi, loại admission hoặc đặc điểm khác hay không; chỉ bổ sung nếu phục vụ câu hỏi nghiên cứu.

## 14. Kết luận báo cáo định kỳ

Giai đoạn 1 đã tạo nền tảng có thể tái lập cho việc định nghĩa cohort: dữ liệu nguồn được giữ nguyên, các bảng và khóa chính đã được xác minh, độ phủ của các kịch bản thời gian đã được đo, và các nguy cơ leakage đã được ghi thành quy tắc kiểm soát. Công việc tiếp theo nên bắt đầu bằng việc duyệt đặc tả cohort, sau đó mới tạo tập dữ liệu xử lý mới cho Phase 2.

## Phụ lục A. Sản phẩm đã hoàn thành

| Nhóm sản phẩm | Thành phần | Mục đích |
|---|---|---|
| Báo cáo Task 1–6 | 06 bộ Markdown/Word cùng các bảng CSV/XLSX theo từng task | Bằng chứng chi tiết cho từng bước khảo sát |
| Từ điển dữ liệu | 44 cột của 5 bảng chính, có bản Word, Excel và CSV | Giải thích schema và vai trò của từng trường |
| Báo cáo tổng kết | REPORT_task07.md và REPORT_task07.docx | Báo cáo định kỳ cho giảng viên |
| Nhật ký quyết định | decision_register_task07.csv | Tách nội dung đã chốt và nội dung chờ duyệt |
| Kế hoạch Phase 2 | phase2_proposed_plan_task07.csv | Khung thảo luận cho bước định nghĩa cohort |
| Mã tái lập | Script của từng task và manifest lần chạy | Cho phép kiểm tra lại số liệu mà không sửa dữ liệu gốc |

## Phụ lục B. Nội dung đề nghị trao đổi với giảng viên

- Xác nhận phạm vi bài toán multi-label ở cấp admission và cách diễn giải đầu ra.
- Thảo luận tiêu chí chọn cửa sổ 6/12/24 giờ dựa trên độ phủ và nguy cơ thông tin muộn.
- Thống nhất inclusion/exclusion criteria trước khi tạo cohort xử lý.
- Xác nhận lộ trình: Phase 2 cohort, Phase 3 lab features, Phase 4 PheCode labels, sau đó mới ghép dataset và modeling.
- Ghi nhận rằng Phase 1 mới khảo sát và kiểm soát rủi ro; chưa có kết quả mô hình.