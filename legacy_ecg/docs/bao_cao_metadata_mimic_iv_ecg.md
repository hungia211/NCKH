# Báo cáo phân tích metadata bộ dữ liệu MIMIC-IV-ECG

## 1. Mục tiêu báo cáo

Báo cáo này phân tích bốn file metadata đã được tải từ bộ dữ liệu MIMIC-IV-ECG:

- `record_list.csv`
- `machine_measurements.csv`
- `machine_measurements_data_dictionary.csv`
- `waveform_note_links.csv`

Hiện tại các file này được lưu cục bộ trong thư mục `metadata/` và được đưa vào `.gitignore` để tránh push các file dữ liệu lớn lên GitHub. Mục tiêu của báo cáo là làm rõ cấu trúc dữ liệu, ý nghĩa từng bảng, khả năng liên kết giữa các bảng, chất lượng dữ liệu, các vấn đề cần xử lý trước khi nghiên cứu, và định hướng sử dụng metadata để xây dựng một nghiên cứu khoa học về điện tâm đồ.

Do dữ liệu waveform ECG đầy đủ có dung lượng lớn, metadata đóng vai trò rất quan trọng trong giai đoạn đầu. Các file metadata cho phép xây dựng cohort, tạo nhãn ban đầu, đánh giá số lượng mẫu theo từng bệnh lý, và quyết định chỉ tải waveform của những ECG cần thiết.

## 2. Tổng quan bộ metadata

Bốn file metadata có vai trò khác nhau nhưng liên kết với nhau thông qua hai khóa chính:

- `subject_id`: định danh bệnh nhân, dùng để nối với dữ liệu lâm sàng MIMIC-IV.
- `study_id`: định danh một lần đo ECG, dùng để nối giữa waveform, machine report và note.

Tổng quan kích thước các file:

| File | Số dòng | Vai trò chính |
|---|---:|---|
| `record_list.csv` | 800.035 | Danh sách toàn bộ ECG và đường dẫn waveform |
| `machine_measurements.csv` | 800.035 | Thông số đo tự động và báo cáo do máy ECG sinh ra |
| `machine_measurements_data_dictionary.csv` | 16 | Từ điển mô tả biến trong `machine_measurements.csv` |
| `waveform_note_links.csv` | 609.272 | Liên kết ECG waveform với note/báo cáo lâm sàng |

Hai bảng `record_list.csv` và `machine_measurements.csv` có cùng số dòng và cùng tập `study_id`, cho thấy mỗi ECG trong danh sách đều có thông tin đo tự động từ máy ECG.

## 3. Phân tích file `record_list.csv`

### 3.1. Vai trò

`record_list.csv` là bảng chỉ mục chính của toàn bộ waveform ECG. Mỗi dòng tương ứng với một lần đo ECG. File này không chứa tín hiệu ECG trực tiếp, nhưng chứa đường dẫn để truy cập cặp file waveform `.hea` và `.dat`.

Các cột chính:

| Cột | Ý nghĩa |
|---|---|
| `subject_id` | Mã bệnh nhân |
| `study_id` | Mã lần đo ECG |
| `file_name` | Tên file waveform, thường trùng với `study_id` |
| `ecg_time` | Thời điểm ghi ECG |
| `path` | Đường dẫn waveform trong bộ dữ liệu |

Ví dụ một đường dẫn:

```text
files/p1000/p10000032/s40689238/40689238
```

Từ đường dẫn này có thể suy ra hai file waveform:

```text
files/p1000/p10000032/s40689238/40689238.hea
files/p1000/p10000032/s40689238/40689238.dat
```

### 3.2. Thống kê chính

- Tổng số ECG: 800.035
- Số bệnh nhân duy nhất: 161.352
- Số `study_id` duy nhất: 800.035
- Số `path` duy nhất: 800.035
- Không phát hiện missing value trong file này
- Không phát hiện sai lệch giữa `subject_id`, `study_id`, `file_name` và cấu trúc `path`

Phân bố số ECG trên mỗi bệnh nhân:

| Chỉ số | Giá trị |
|---|---:|
| Ít nhất | 1 |
| Q1 | 1 |
| Trung vị | 2 |
| Trung bình | 4,958 |
| Q3 | 5 |
| P90 | 12 |
| P99 | 39 |
| Nhiều nhất | 260 |

Điều này cho thấy phần lớn bệnh nhân có ít ECG, nhưng một nhóm nhỏ bệnh nhân có rất nhiều lần đo. Khi chia tập train/test, cần chia theo `subject_id` thay vì chia ngẫu nhiên theo ECG để tránh rò rỉ dữ liệu giữa các ECG của cùng một bệnh nhân.

## 4. Phân tích file `machine_measurements.csv`

### 4.1. Vai trò

`machine_measurements.csv` là file metadata quan trọng nhất cho giai đoạn nghiên cứu ban đầu. File này chứa hai nhóm thông tin:

1. Báo cáo dạng text do máy ECG sinh ra: `report_0` đến `report_17`.
2. Các thông số định lượng của ECG: `rr_interval`, `p_onset`, `p_end`, `qrs_onset`, `qrs_end`, `t_end`, `p_axis`, `qrs_axis`, `t_axis`.

Nhờ file này, có thể xây dựng mô hình baseline mà chưa cần tải waveform. Ngoài ra, các cột report có thể được dùng để tạo nhãn tự động cho các bài toán phân loại ECG.

### 4.2. Các cột chính

| Nhóm cột | Cột | Ý nghĩa |
|---|---|---|
| Định danh | `subject_id`, `study_id` | Khóa bệnh nhân và khóa ECG |
| Thiết bị | `cart_id` | Mã máy ECG |
| Thời gian | `ecg_time` | Thời điểm ECG theo bảng machine measurements |
| Báo cáo text | `report_0` đến `report_17` | Nhận xét/chẩn đoán do máy ECG sinh ra |
| Cấu hình máy | `bandwidth`, `filtering` | Băng thông và bộ lọc |
| Khoảng thời gian | `rr_interval`, `p_onset`, `p_end`, `qrs_onset`, `qrs_end`, `t_end` | Các mốc thời gian sóng ECG, đơn vị ms |
| Trục điện học | `p_axis`, `qrs_axis`, `t_axis` | Trục điện học của P, QRS, T, đơn vị độ |

### 4.3. Thống kê chính

- Tổng số dòng: 800.035
- Số bệnh nhân duy nhất: 161.352
- Số `study_id` duy nhất: 800.035
- Số ECG cart duy nhất: 156
- Không có trùng `study_id`
- Khớp hoàn toàn với `record_list.csv` theo `study_id`

### 4.4. Phân tích các report text

Mỗi ECG có thể có nhiều dòng report. Các cột `report_0` đến `report_17` không phải là các nhãn loại trừ nhau. Một ECG có thể đồng thời có nhiều nhận xét, ví dụ:

```text
report_0 = Sinus rhythm
report_1 = Left axis deviation
report_2 = Abnormal ECG
```

Do đó, bài toán phù hợp nhất khi dùng các report này là multi-label classification, tức một ECG có thể mang nhiều nhãn cùng lúc.

Các cụm report phổ biến:

| Cụm report | Số lần xuất hiện | Diễn giải |
|---|---:|---|
| Abnormal ECG | 355.656 | Máy đánh giá ECG bất thường |
| Sinus rhythm | 324.175 | Nhịp xoang |
| Borderline ECG | 171.372 | ECG ở mức ranh giới |
| Normal ECG | 116.608 | ECG bình thường theo máy |
| Left axis deviation | 75.280 | Trục điện tim lệch trái |
| Sinus bradycardia | 60.062 | Nhịp xoang chậm |
| Sinus tachycardia | 42.002 | Nhịp xoang nhanh |
| Inferior infarct - age undetermined | 41.581 | Gợi ý nhồi máu thành dưới, không xác định tuổi |
| Prolonged QT interval | 37.034 | Khoảng QT kéo dài |
| Atrial fibrillation | 32.879 | Rung nhĩ |
| Right bundle branch block | 33.513 | Block nhánh phải |
| Left bundle branch block | 23.277 | Block nhánh trái |

Một số nhóm nhãn có tiềm năng nghiên cứu:

| Nhóm nhãn | Lý do phù hợp |
|---|---|
| Normal vs Abnormal ECG | Bài toán phân loại tổng quát, số lượng mẫu lớn |
| Atrial fibrillation | Bệnh lý nhịp phổ biến, có ý nghĩa lâm sàng cao |
| Sinus bradycardia / tachycardia | Có thể kiểm chứng bằng `rr_interval` |
| Bundle branch block | Có liên quan đến QRS duration và hình dạng waveform |
| Prolonged QT | Có thể kiểm chứng bằng `qt_interval` và cần hiệu chỉnh theo nhịp tim |
| Left axis deviation | Có thể kiểm chứng bằng `qrs_axis` |

### 4.5. Thống kê thông số định lượng

Một số chỉ số dẫn xuất từ các cột numeric:

| Chỉ số | Trung vị | Diễn giải |
|---|---:|---|
| `rr_interval` | 810 ms | Khoảng R-R, dùng để suy ra nhịp tim |
| Heart rate ước tính | 74,1 bpm | Tính từ `60000 / rr_interval` |
| QRS duration | 93 ms | Tính từ `qrs_end - qrs_onset` |
| QT interval | 396 ms | Tính từ `t_end - qrs_onset` |

Các chỉ số này có thể dùng làm đặc trưng đầu vào cho các mô hình học máy truyền thống như logistic regression, random forest, XGBoost hoặc LightGBM.

### 4.6. Vấn đề chất lượng dữ liệu

Mặc dù các cột numeric không có missing value theo nghĩa ô trống, dữ liệu có nhiều giá trị đặc biệt hoặc bất thường. Một số giá trị có khả năng là sentinel value hoặc mã lỗi của máy:

- `29999`
- `32767`
- `-32768`
- `65535`
- `65534`
- `61440`

Khi tiền xử lý, không nên dùng trực tiếp các giá trị này như số đo sinh lý bình thường. Cần chuyển chúng thành missing hoặc đánh dấu invalid.

Ngoài ra, có 17.850 dòng có `ecg_time` khác giữa `machine_measurements.csv` và `record_list.csv`. Vì `record_list.csv` là bảng chỉ mục waveform chính, nên khuyến nghị dùng `record_list.ecg_time` làm thời gian chuẩn khi nối với dữ liệu khác.

## 5. Phân tích file `machine_measurements_data_dictionary.csv`

File này là từ điển mô tả các biến trong `machine_measurements.csv`. Nó giúp xác nhận ý nghĩa của từng cột, đặc biệt là các cột thời gian sóng ECG và trục điện học.

File có 16 dòng, mô tả các biến:

- `subject_id`
- `study_id`
- `cart_id`
- `ecg_time`
- `report_#`
- `bandwidth`
- `filtering`
- `rr_interval`
- `p_onset`
- `p_end`
- `qrs_onset`
- `qrs_end`
- `t_end`
- `p_axis`
- `qrs_axis`
- `t_axis`

Một điểm kỹ thuật cần lưu ý là file có lỗi encoding nhẹ ở tên cột mô tả, hiển thị thành `Description�`. Tuy nhiên nội dung mô tả vẫn đọc được và không ảnh hưởng lớn đến phân tích.

## 6. Phân tích file `waveform_note_links.csv`

### 6.1. Vai trò

`waveform_note_links.csv` liên kết ECG waveform với các note/báo cáo ECG trong hệ thống lâm sàng. File này hữu ích nếu nghiên cứu cần so sánh machine report với note của bác sĩ hoặc muốn lấy nhãn đáng tin cậy hơn từ báo cáo lâm sàng.

Các cột chính:

| Cột | Ý nghĩa |
|---|---|
| `subject_id` | Mã bệnh nhân |
| `study_id` | Mã lần đo ECG |
| `waveform_path` | Đường dẫn waveform |
| `note_id` | Mã note |
| `note_seq` | Thứ tự note của bệnh nhân |
| `charttime` | Thời điểm note |

### 6.2. Thống kê chính

- Tổng số dòng: 609.272
- Số `study_id` duy nhất: 609.265
- Số bệnh nhân duy nhất: 105.293
- Số ECG có liên kết note: 609.265
- Số ECG trong `record_list.csv` không có note link: 190.770
- Tỷ lệ ECG có note link: khoảng 76,15%

`waveform_path` khớp hoàn toàn với `record_list.path`, cho thấy file này có thể nối rất tốt với bảng chỉ mục waveform.

### 6.3. Vấn đề chất lượng dữ liệu

Có một số điểm cần lưu ý:

- Có 7 `study_id` bị lặp, tức một ECG có thể liên kết với hơn một note.
- Có 866 dòng có `charttime` khác `record_list.ecg_time`.
- Có một số trường hợp `note_id` có vẻ liên quan đến bệnh nhân khác, do đó khi dùng note làm nhãn cần kiểm tra kỹ `subject_id`, `study_id`, `note_id` và `charttime`.

Với các ECG có nhiều note, cần chọn chiến lược xử lý rõ ràng:

1. Giữ note gần nhất với `ecg_time`.
2. Gộp tất cả note theo cùng `study_id`.
3. Loại các trường hợp trùng nếu cần nhãn sạch.

## 7. Khả năng liên kết giữa các bảng

Kết quả kiểm tra khóa nối:

| Liên kết | Kết quả |
|---|---:|
| `record_list` và `machine_measurements` theo `study_id` | 800.035 / 800.035 khớp |
| `record_list` có machine measurement | 100% |
| `machine_measurements` không có record | 0 |
| `record_list` và `waveform_note_links` theo `study_id` | 609.265 khớp |
| ECG có note link | 609.265 |
| ECG không có note link | 190.770 |
| `waveform_note_links` không có record | 0 |

Sơ đồ liên kết đề xuất:

```text
record_list.csv
  ├── join machine_measurements.csv
  │       on subject_id + study_id
  │
  └── join waveform_note_links.csv
          on subject_id + study_id
```

Trong đó, `record_list.csv` nên được xem là bảng trung tâm.

## 8. Đề xuất tiền xử lý dữ liệu

### 8.1. Chuẩn hóa bảng nền

Tạo một bảng master metadata với cấu trúc:

```text
subject_id
study_id
ecg_time
path
has_machine_measurement
has_note
note_id
machine_reports_combined
numeric_ecg_features
```

Khuyến nghị dùng `record_list.ecg_time` làm thời gian ECG chuẩn.

### 8.2. Làm sạch numeric features

Các bước đề xuất:

1. Chuyển các giá trị sentinel thành missing:
   - `29999`
   - `32767`
   - `-32768`
   - `65535`
   - `65534`
   - `61440`
2. Kiểm tra điều kiện sinh lý:
   - `rr_interval > 0`
   - `p_onset <= p_end <= qrs_onset <= qrs_end <= t_end`
   - `qrs_axis`, `p_axis`, `t_axis` nằm trong khoảng hợp lý, ví dụ `[-180, 180]`
3. Tạo biến dẫn xuất:
   - `heart_rate = 60000 / rr_interval`
   - `pr_interval = qrs_onset - p_onset`
   - `qrs_duration = qrs_end - qrs_onset`
   - `qt_interval = t_end - qrs_onset`

### 8.3. Chuẩn hóa report text

Các bước đề xuất:

1. Gộp `report_0` đến `report_17` thành một chuỗi duy nhất.
2. Chuẩn hóa chữ thường.
3. Loại dấu câu không cần thiết.
4. Map các cụm tương đương về cùng nhãn, ví dụ:
   - `Sinus rhythm` và `Sinus rhythm.`
   - `Right bundle branch block` và các biến thể viết tắt nếu có
   - `Prolonged QT interval` và `Prolonged QT`
5. Tạo nhãn binary cho từng bệnh lý.

Ví dụ nhãn:

```text
label_normal_ecg
label_abnormal_ecg
label_atrial_fibrillation
label_sinus_tachycardia
label_sinus_bradycardia
label_rbbb
label_lbbb
label_lvh
label_prolonged_qt
label_axis_deviation
```

## 9. Định hướng nghiên cứu khoa học

Từ metadata hiện có, có thể triển khai nghiên cứu theo ba giai đoạn.

### 9.1. Giai đoạn 1: Nghiên cứu mô tả metadata

Mục tiêu:

- Mô tả phân bố ECG theo bệnh nhân.
- Mô tả tỷ lệ ECG có note.
- Mô tả các nhóm chẩn đoán phổ biến từ machine report.
- Đánh giá chất lượng và độ đầy đủ của metadata.

Đây có thể là phần dữ liệu và phương pháp trong bài nghiên cứu.

### 9.2. Giai đoạn 2: Baseline model không dùng waveform

Mục tiêu:

- Dự đoán một số nhãn ECG từ numeric features.
- So sánh khả năng dự đoán của các feature định lượng so với text report.

Feature đầu vào:

- `rr_interval`
- `heart_rate`
- `pr_interval`
- `qrs_duration`
- `qt_interval`
- `p_axis`
- `qrs_axis`
- `t_axis`
- `bandwidth`
- `filtering`

Nhãn đầu ra có thể chọn:

- Atrial fibrillation
- Sinus tachycardia
- Sinus bradycardia
- Right bundle branch block
- Left bundle branch block
- Prolonged QT
- Normal vs Abnormal ECG

Mô hình đề xuất:

- Logistic Regression
- Random Forest
- XGBoost hoặc LightGBM
- Multilabel classification nếu dự đoán nhiều nhãn cùng lúc

### 9.3. Giai đoạn 3: Tải waveform có chọn lọc

Sau khi đã xác định nhãn và cohort, chỉ tải waveform tương ứng với các `study_id` cần dùng.

Ví dụ:

```text
path = files/p1000/p10000032/s40689238/40689238
```

Tải:

```text
files/p1000/p10000032/s40689238/40689238.hea
files/p1000/p10000032/s40689238/40689238.dat
```

Sau đó có thể huấn luyện mô hình deep learning trên tín hiệu ECG 12 đạo trình.

## 10. Bài toán nghiên cứu đề xuất

Một hướng nghiên cứu phù hợp với metadata hiện tại:

**Đề tài đề xuất:**  
Xây dựng và đánh giá mô hình phân loại bất thường điện tâm đồ từ metadata và tín hiệu ECG trong bộ dữ liệu MIMIC-IV-ECG.

### Câu hỏi nghiên cứu

1. Các machine measurements có đủ khả năng dự đoán một số bất thường ECG phổ biến hay không?
2. Các nhãn sinh từ machine report có thể dùng để chọn cohort và huấn luyện mô hình ban đầu hay không?
3. Khi bổ sung waveform ECG, hiệu năng mô hình có cải thiện so với chỉ dùng metadata hay không?

### Thiết kế nghiên cứu đề xuất

1. Tạo bảng master metadata từ 4 file.
2. Làm sạch numeric features và report text.
3. Tạo nhãn từ report text.
4. Chia train/validation/test theo `subject_id`.
5. Huấn luyện baseline model bằng metadata.
6. Tải waveform cho một số nhãn trọng tâm.
7. Huấn luyện mô hình waveform.
8. So sánh hiệu năng giữa metadata model và waveform model.

### Metrics đánh giá

- AUROC
- AUPRC
- Accuracy
- Sensitivity
- Specificity
- F1-score
- Confusion matrix

Với dữ liệu mất cân bằng, nên ưu tiên thêm AUPRC và F1-score thay vì chỉ báo cáo accuracy.

## 11. Rủi ro và hạn chế

Một số hạn chế cần nêu rõ trong nghiên cứu:

1. Report trong `machine_measurements.csv` là báo cáo do máy sinh ra, không phải nhãn vàng tuyệt đối.
2. Một ECG có thể có nhiều nhãn, nên bài toán không nên ép thành single-label nếu không có lý do rõ ràng.
3. Có nhiều giá trị numeric bất thường cần xử lý trước khi mô hình hóa.
4. Một số timestamp không khớp giữa các bảng.
5. Khoảng 23,85% ECG không có note link.
6. Nếu chia dữ liệu theo ECG thay vì theo bệnh nhân, có nguy cơ data leakage.
7. Các ECG có thể không nằm trong cùng bối cảnh admission/ICU/ED, nên khi nối với dữ liệu lâm sàng cần kiểm tra thời gian cẩn thận.

## 12. Kết luận

Bốn file metadata hiện có đủ để bắt đầu một nghiên cứu khoa học theo hướng có kiểm soát mà chưa cần tải toàn bộ waveform ECG. `record_list.csv` nên được dùng làm bảng nền, `machine_measurements.csv` là nguồn quan trọng để tạo đặc trưng và nhãn ban đầu, `waveform_note_links.csv` hỗ trợ liên kết với báo cáo lâm sàng, còn `machine_measurements_data_dictionary.csv` giúp giải thích các biến đo tự động.

Hướng đi hợp lý là xây dựng trước một pipeline metadata gồm: nối bảng, làm sạch dữ liệu, tạo nhãn từ report, phân tích phân bố nhãn, huấn luyện baseline model, sau đó mới tải waveform có chọn lọc cho các bài toán cụ thể. Cách tiếp cận này giúp tiết kiệm tài nguyên, giảm rủi ro tải dữ liệu không cần thiết, và tạo nền tảng vững chắc cho nghiên cứu sâu hơn trên tín hiệu ECG.
