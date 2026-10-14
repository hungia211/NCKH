# Ý tưởng mở rộng — Dự đoán theo lịch sử nhiều admission

## Trạng thái

Đây là **hướng nghiên cứu mở rộng**, chưa thay thế pipeline admission-level hiện tại và chưa được triển khai. Pipeline chính vẫn sử dụng xét nghiệm giai đoạn sớm của một admission để dự đoán các phenotype được ghi nhận cho chính admission đó.

Tài liệu này lưu lại ý tưởng để tiếp tục rà soát sau khi baseline admission-level đã hoàn thành.

## 1. Mục tiêu

Khi một bệnh nhân quay lại bệnh viện ở lần nhập viện tiếp theo, sử dụng:

1. lịch sử xét nghiệm của các admission trước;
2. xét nghiệm giai đoạn sớm vừa có trong admission hiện tại;

để dự đoán sớm các phenotype có khả năng được ghi nhận trong admission hiện tại.

Ví dụ với Admission 3 là admission mục tiêu:

```text
Lịch sử Admission 1 + Admission 2
                 +
Xét nghiệm giai đoạn sớm của Admission 3
                 ↓
Dự đoán các phenotype được ghi nhận cho Admission 3
```

Mô hình không dự đoán trước khi Admission 3 xảy ra. Dự đoán được tạo sau khi bệnh nhân bắt đầu Admission 3 và đã có các xét nghiệm sớm theo cửa sổ được quy định.

## 2. Cách tạo mẫu theo chuỗi admission

Với bệnh nhân có các admission theo thứ tự thời gian `A1, A2, A3, A4`, các mẫu longitudinal dự kiến là:

```text
Lịch sử A1 + lab sớm A2          → phenotype của A2
Lịch sử A1 + A2 + lab sớm A3     → phenotype của A3
Lịch sử A1 + A2 + A3 + lab sớm A4 → phenotype của A4
```

Mỗi admission mục tiêu vẫn tạo một mẫu dự đoán. Điểm khác biệt là feature của mẫu chứa thêm thông tin từ các admission xảy ra trước đó của cùng bệnh nhân.

Admission đầu tiên của bệnh nhân không có lịch sử trước đó. Admission này có thể tiếp tục dùng cho mô hình admission-level; cách sử dụng trong mô hình longitudinal sẽ được quyết định khi thiết kế thực nghiệm.

## 3. Input và target

### Input của admission mục tiêu `Ak`

- Feature xét nghiệm giai đoạn sớm của `Ak`.
- Feature tóm tắt từ các admission `A1 ... A(k-1)`.
- Thứ tự và khoảng cách thời gian giữa các admission, nếu sau này được chứng minh cần thiết.

Không sử dụng:

- xét nghiệm xảy ra sau cutoff của admission mục tiêu;
- diagnosis của admission mục tiêu làm input;
- bất kỳ admission nào xảy ra sau admission mục tiêu.

### Target

Các phenotype được ghi nhận cho admission mục tiêu `Ak`, xây dựng từ `diagnoses_icd` của chính admission đó sau bước ICD → PheCode.

Do `diagnoses_icd` không có timestamp xác lập chẩn đoán, kết quả phải được diễn giải là:

> Nguy cơ hoặc khả năng các phenotype được ghi nhận trong admission mục tiêu.

Không diễn giải thành dự đoán thời điểm bệnh khởi phát hoặc chứng minh mô hình phát hiện bệnh trước bác sĩ.

## 4. Ý nghĩa của việc dùng nhiều admission

Mô hình không được huấn luyện riêng một lần cho từng bệnh nhân. Mô hình vẫn được huấn luyện trên nhiều mẫu của nhiều bệnh nhân.

Việc dùng nhiều admission giúp biểu diễn một mẫu tốt hơn bằng cách bổ sung lịch sử của bệnh nhân, chẳng hạn:

- xu hướng tăng hoặc giảm của xét nghiệm giữa các admission;
- bất thường xuất hiện lặp lại;
- giá trị gần nhất trước admission mục tiêu;
- số admission trước đó có cùng loại bất thường;
- khoảng thời gian kể từ admission gần nhất.

Giả thuyết cần kiểm chứng là lịch sử này giúp dự đoán tốt hơn so với chỉ dùng xét nghiệm sớm của admission mục tiêu.

## 5. Thiết kế so sánh dự kiến

| Mô hình | Input | Vai trò |
|---|---|---|
| A — Admission-level baseline | Chỉ lab giai đoạn sớm của admission mục tiêu | Pipeline chính và mốc so sánh |
| B — Longitudinal laboratory | Lab sớm của admission mục tiêu + lịch sử lab của các admission trước | Đo giá trị bổ sung của lịch sử xét nghiệm |
| C — Có prior diagnoses | Input của B + diagnosis từ các admission trước | Thí nghiệm mở rộng riêng, chỉ thực hiện nếu được duyệt |

Mô hình B chỉ được xem là có lợi nếu cải thiện kết quả trên cùng cohort đánh giá, cùng label set và cùng cách chia bệnh nhân so với mô hình A.

Mô hình C phải được tách riêng vì prior diagnoses có thể làm mô hình chủ yếu học sự lặp lại của bệnh mạn tính, làm giảm khả năng xác định đóng góp riêng của laboratory data.

## 6. Kiểm soát leakage

1. Sắp xếp admission theo thời gian trong từng `subject_id`.
2. Với target `Ak`, chỉ dùng dữ liệu có trước cutoff của `Ak`.
3. Không dùng diagnosis của `Ak` hoặc admission tương lai làm feature.
4. Toàn bộ admission của một `subject_id` phải nằm trong cùng train, validation hoặc test.
5. Fit imputation, scaling, feature selection và các phép biến đổi học từ dữ liệu chỉ trên train.
6. Khi tạo feature lịch sử, không dùng thống kê được tính từ tương lai của bệnh nhân.

## 7. Các quyết định chưa chốt

- Dùng toàn bộ lịch sử hay chỉ `N` admission gần nhất.
- Cách tóm tắt lịch sử: giá trị gần nhất, mean/min/max, slope, số lần bất thường hoặc biểu diễn chuỗi.
- Có sử dụng diagnosis của admission trước hay chỉ laboratory history.
- Cách xử lý khoảng thời gian rất dài giữa hai admission.
- Yêu cầu tối thiểu về số admission trước đó.
- Mô hình biểu diễn dữ liệu: feature bảng tổng hợp hay sequence model.
- Metric và cohort con dùng để so sánh công bằng với baseline admission-level.

Không chốt các lựa chọn này trước khi hoàn thành pipeline chính và đo được số bệnh nhân có ít nhất hai admission hợp lệ sau Phase 2–4.

## 8. Vị trí trong roadmap

Hướng longitudinal được xem là phase mở rộng sau khi đã hoàn thành:

1. cohort admission-level;
2. laboratory feature matrix;
3. PheCode label matrix;
4. patient-level split;
5. baseline admission-level và đánh giá ban đầu.

Kết quả chính của đề tài vẫn là bài toán admission-level. Hướng nhiều admission dùng để kiểm tra liệu lịch sử của cùng bệnh nhân có làm tăng khả năng dự đoán phenotype trong admission tiếp theo hay không.
