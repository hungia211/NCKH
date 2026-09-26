# Đề xuất nghiên cứu khoa học dựa trên bộ dữ liệu MIMIC-IV-ECG

## 1. Tên đề tài đề xuất

### Tiếng Việt

**Hiệu chỉnh độ tin cậy dựa trên tri thức sinh lý cho mô hình học biểu diễn ECG-text trong phát hiện bất thường ECG 12 đạo trình**

### Tiếng Anh

**Physiology-Guided Confidence Calibration for ECG-Text Contrastive Learning in 12-Lead ECG Abnormality Detection**

Tên ngắn có thể dùng trong quá trình triển khai:

**Physio-Calibrated ECG-CLIP**

## 2. Bối cảnh và lý do chọn đề tài

Điện tâm đồ, hay ECG, là một phương pháp chẩn đoán không xâm lấn, chi phí thấp và được sử dụng rộng rãi để phát hiện các bất thường tim mạch. Với sự phát triển của học sâu, nhiều nghiên cứu đã sử dụng CNN, ResNet, DenseNet hoặc Transformer để phân loại ECG tự động.

Tuy nhiên, nhiều hướng nghiên cứu truyền thống vẫn có một số hạn chế:

1. Mô hình thường chỉ học theo một tập nhãn cố định.
2. Khi cần thêm nhãn bệnh mới, mô hình thường phải được huấn luyện lại hoặc fine-tune.
3. Nhiều nghiên cứu chuyển ECG thành ảnh 2D để dùng CNN thị giác máy tính, có thể làm mất một phần thông tin chuỗi thời gian.
4. Các nhãn dùng để huấn luyện có thể nhiễu, đặc biệt khi lấy từ machine-generated report.
5. Mô hình thường trả về xác suất hoặc score nhưng chưa đánh giá dự đoán đó có hợp lý với tri thức sinh lý ECG hay không.

Bộ dữ liệu **MIMIC-IV-ECG** phù hợp để giải quyết các hạn chế này vì có:

- Tín hiệu ECG 12 đạo trình dạng waveform.
- Metadata chứa `subject_id`, `study_id`, `ecg_time`, `path`.
- Machine measurements như `rr_interval`, `qrs_onset`, `qrs_end`, `t_end`, `qrs_axis`.
- Machine-generated reports trong các cột `report_0` đến `report_17`.
- Khả năng nối với MIMIC-IV Clinical thông qua `subject_id` nếu có quyền truy cập bổ sung.

Nguồn dữ liệu chính: https://physionet.org/content/mimic-iv-ecg/1.0/

## 3. Tổng quan dữ liệu sử dụng

Trong giai đoạn đầu, nghiên cứu sử dụng các file metadata đã tải:

| File | Vai trò |
|---|---|
| `record_list.csv` | Danh sách ECG, `subject_id`, `study_id`, `ecg_time`, đường dẫn waveform |
| `machine_measurements.csv` | Machine report và các chỉ số đo tự động của ECG |
| `machine_measurements_data_dictionary.csv` | Từ điển biến của bảng machine measurements |
| `waveform_note_links.csv` | Liên kết waveform với note/báo cáo nếu có |

Khi triển khai mô hình chính, nghiên cứu sẽ tải waveform ECG theo `path` trong `record_list.csv`. Mỗi ECG thường là tín hiệu 12 đạo trình, dài khoảng 10 giây, tần số lấy mẫu 500 Hz.

Input chính của mô hình:

```text
ECG waveform 12 đạo trình
```

Nguồn giám sát văn bản:

```text
report_0 + report_1 + ... + report_17
```

Nguồn kiểm tra sinh lý:

```text
rr_interval
p_onset
p_end
qrs_onset
qrs_end
t_end
p_axis
qrs_axis
t_axis
```

## 4. Các nghiên cứu liên quan và khoảng trống

### 4.1. Hai bài nghiên cứu đã tham khảo

Hai bài báo/khóa luận được cung cấp trước đó chủ yếu đi theo hướng:

| Bài | Dataset | Hướng chính | Mô hình |
|---|---|---|---|
| Bài 1 | MIT-BIH, PTB Diagnostic, PTB-XL | Chuyển ECG thành ảnh 2D để phân loại bất thường | ResNet, CNN, SVM, Random Forest |
| Bài 2 | CPSC2018 | Multi-label ECG classification từ ảnh ECG 12 đạo trình | DenseNet201, ResNet, Grad-CAM |

Các hướng này có giá trị tham khảo, nhưng đề tài mới cần tránh làm trùng các điểm sau:

- Không chỉ chuyển ECG thành ảnh 2D rồi dùng CNN/ResNet/DenseNet.
- Không chỉ so sánh mô hình supervised truyền thống.
- Không lấy web app làm đóng góp chính.
- Không chỉ phân loại nhãn cố định theo cách thông thường.

### 4.2. ECG-CLIP và khoảng trống còn lại

Một hướng mới hơn là ECG-CLIP, trong đó mô hình học tương quan giữa:

```text
ECG waveform <-> diagnostic report text
```

Cách này cho phép thực hiện zero-shot hoặc few-shot classification bằng các prompt mô tả bệnh.

Tuy nhiên, nếu chỉ làm lại ECG-CLIP thì chưa đủ mới. Khoảng trống nghiên cứu có thể khai thác là:

1. Report do máy ECG sinh ra có thể nhiễu.
2. Điểm similarity của ECG-CLIP chưa chắc là xác suất lâm sàng đáng tin cậy.
3. ECG-CLIP chưa nhấn mạnh việc kiểm tra dự đoán bằng các chỉ số sinh lý ECG.
4. Một số nhãn có thể được kiểm tra logic bằng machine measurements, nhưng thông tin này chưa được khai thác đầy đủ trong quá trình hiệu chỉnh độ tin cậy.

Vì vậy, hướng mới của đề tài không phải là sao chép ECG-CLIP, mà là:

> Kết hợp ECG-text contrastive learning với module kiểm tra tính nhất quán sinh lý để hiệu chỉnh độ tin cậy và giảm tác động của nhãn nhiễu.

## 5. Ý tưởng nghiên cứu đề xuất

Mô hình cơ sở sẽ học biểu diễn chung giữa tín hiệu ECG 12 đạo trình và report text.

Ví dụ:

```text
ECG A
report A = "Atrial fibrillation | Abnormal ECG"

ECG B
report B = "Sinus rhythm | Normal ECG"
```

Mô hình học sao cho:

```text
ECG A gần report A
ECG A xa report B

ECG B gần report B
ECG B xa report A
```

Sau đó, thay vì chỉ trả về score như ECG-CLIP thông thường, nghiên cứu thêm một module kiểm tra sinh lý.

Ví dụ:

```text
Model dự đoán: Sinus tachycardia
rr_interval = 850 ms
heart_rate = 60000 / 850 = 70,6 bpm
```

Vì sinus tachycardia thường liên quan đến nhịp tim nhanh, dự đoán này không thật sự nhất quán. Hệ thống sẽ giảm độ tin cậy hoặc đưa ra cảnh báo.

Ngược lại:

```text
Model dự đoán: Sinus tachycardia
rr_interval = 480 ms
heart_rate = 60000 / 480 = 125 bpm
```

Dự đoán này phù hợp sinh lý hơn, nên độ tin cậy được giữ hoặc tăng.

## 6. Câu hỏi nghiên cứu

1. Mô hình ECG-text contrastive learning có thể học biểu diễn hữu ích từ ECG 12 đạo trình và machine-generated reports trong MIMIC-IV-ECG không?
2. Việc hiệu chỉnh độ tin cậy bằng các chỉ số sinh lý ECG có cải thiện độ tin cậy của dự đoán so với ECG-CLIP baseline không?
3. Các cặp ECG-report có độ nhất quán sinh lý cao có giúp mô hình học tốt hơn so với việc dùng toàn bộ report không phân biệt nhiễu?
4. Mô hình có cải thiện trong bối cảnh zero-shot và few-shot classification không?
5. Những nhãn ECG nào phù hợp nhất với physiology-guided calibration?

## 7. Mục tiêu nghiên cứu

### 7.1. Mục tiêu tổng quát

Xây dựng và đánh giá một mô hình học biểu diễn đa phương thức ECG-text có khả năng phát hiện bất thường ECG 12 đạo trình, đồng thời hiệu chỉnh độ tin cậy dựa trên tính nhất quán sinh lý từ machine measurements.

### 7.2. Mục tiêu cụ thể

1. Phân tích metadata MIMIC-IV-ECG để chọn cohort, nhãn và waveform cần tải.
2. Xây dựng pipeline đọc và tiền xử lý ECG waveform 12 đạo trình.
3. Xây dựng ECG-CLIP style baseline cho ECG waveform và report text.
4. Đề xuất module physiology consistency dựa trên machine measurements.
5. Đề xuất phương pháp hiệu chỉnh confidence hoặc weighted contrastive loss.
6. Đánh giá mô hình trên các tác vụ supervised, zero-shot và few-shot classification.
7. So sánh mô hình đề xuất với baseline truyền thống và ECG-CLIP baseline.

## 8. Phạm vi nghiên cứu

### 8.1. Dữ liệu

Dataset chính:

```text
MIMIC-IV-ECG
```

Giai đoạn đầu có thể dùng subset thay vì tải toàn bộ waveform.

### 8.2. Nhãn bệnh dự kiến

Nên chọn các nhãn phổ biến và có thể kiểm tra một phần bằng machine measurements:

| Nhãn | Lý do chọn |
|---|---|
| Normal ECG | Nhãn nền |
| Abnormal ECG | Nhãn tổng quát |
| Sinus tachycardia | Có thể kiểm tra bằng heart rate |
| Sinus bradycardia | Có thể kiểm tra bằng heart rate |
| Prolonged QT interval | Có thể kiểm tra bằng QT/QTc |
| Left axis deviation | Có thể kiểm tra bằng `qrs_axis` |
| Right axis deviation | Có thể kiểm tra bằng `qrs_axis` |
| Right bundle branch block | Liên quan đến QRS duration |
| Left bundle branch block | Liên quan đến QRS duration |
| First-degree AV block | Có thể kiểm tra bằng PR interval |

Không nên chọn quá nhiều nhãn ngay từ đầu. Giai đoạn thực nghiệm đầu tiên nên chọn khoảng 5 đến 8 nhãn.

## 9. Phương pháp đề xuất

### 9.1. Tiền xử lý metadata

Các bước:

1. Đọc `record_list.csv` để lấy `subject_id`, `study_id`, `ecg_time`, `path`.
2. Đọc `machine_measurements.csv` để lấy report text và machine measurements.
3. Gộp `report_0` đến `report_17` thành một trường `report_text`.
4. Chuẩn hóa text:
   - lowercase
   - loại dấu câu không cần thiết
   - chuẩn hóa các biến thể như `Sinus rhythm.` và `Sinus rhythm`
5. Tạo label bằng keyword matching ban đầu.
6. Làm sạch các giá trị bất thường như `29999`, `32767`, `-32768`, `65535`.

### 9.2. Tiền xử lý ECG waveform

Các bước dự kiến:

1. Đọc waveform bằng WFDB.
2. Chuẩn hóa tín hiệu về dạng:

```text
5000 x 12
```

3. Xử lý missing lead nếu có.
4. Chuẩn hóa biên độ từng lead.
5. Có thể áp dụng lọc nhiễu nhẹ nếu cần.

Không nên chuyển ECG thành ảnh 2D làm hướng chính, vì hai bài trước đã khai thác hướng đó.

### 9.3. ECG-text contrastive learning baseline

Mô hình gồm hai encoder:

```text
ECG waveform -> ECG Encoder -> ECG embedding
Report text  -> Text Encoder -> Text embedding
```

Loss cơ bản:

```text
InfoNCE / CLIP contrastive loss
```

Mục tiêu:

```text
ECG đúng gần report đúng
ECG đúng xa report sai
```

ECG encoder có thể thử:

- ResNet1D
- InceptionTime
- Transformer 1D
- PatchTST

Text encoder có thể thử:

- BioClinicalBERT
- PubMedBERT
- Sentence-BERT biomedical
- BERT nhỏ hơn nếu tài nguyên hạn chế

### 9.4. Module physiology consistency

Từ machine measurements, tính các chỉ số:

| Chỉ số | Công thức |
|---|---|
| Heart rate | `60000 / rr_interval` |
| PR interval | `qrs_onset - p_onset` |
| QRS duration | `qrs_end - qrs_onset` |
| QT interval | `t_end - qrs_onset` |
| QRS axis | `qrs_axis` |

Sau đó xây dựng rule kiểm tra:

| Nhãn | Rule gợi ý |
|---|---|
| Sinus tachycardia | heart rate > 100 bpm |
| Sinus bradycardia | heart rate < 60 bpm |
| Prolonged QT interval | QT/QTc cao hơn ngưỡng |
| First-degree AV block | PR interval > 200 ms |
| Bundle branch block | QRS duration >= 120 ms |
| Left axis deviation | QRS axis lệch trái |
| Right axis deviation | QRS axis lệch phải |

Các rule này không thay thế bác sĩ, chỉ dùng để đánh giá mức độ nhất quán của nhãn hoặc dự đoán.

### 9.5. Hiệu chỉnh độ tin cậy

Có ba mức triển khai:

#### Mức 1: Rule-based confidence adjustment

```text
adjusted_score = model_score * consistency_weight
```

Ví dụ:

```text
consistency high   -> weight = 1.0
consistency medium -> weight = 0.75
consistency low    -> weight = 0.5
```

#### Mức 2: Learned calibration model

Huấn luyện một mô hình nhỏ nhận đầu vào:

```text
ECG-CLIP score
machine measurements
consistency flags
```

và trả về:

```text
calibrated probability
```

Mô hình có thể là Logistic Regression, MLP nhỏ hoặc Gradient Boosting.

#### Mức 3: Weighted contrastive learning

Trong quá trình train, cặp ECG-report có độ nhất quán cao được weight cao hơn:

```text
loss = w * contrastive_loss(ECG, text)
```

Trong đó `w` là consistency score.

## 10. Output của hệ thống

Khi đưa một ECG mới vào, hệ thống có thể trả:

```json
{
  "predictions": [
    {
      "label": "Atrial fibrillation",
      "score": 0.86,
      "adjusted_confidence": 0.82
    },
    {
      "label": "Prolonged QT interval",
      "score": 0.77,
      "adjusted_confidence": 0.41
    }
  ],
  "top_text_match": "This ECG shows atrial fibrillation.",
  "physiology_consistency": {
    "status": "medium",
    "notes": [
      "Prolonged QT prediction is weakly supported by QT interval."
    ]
  }
}
```

Điểm khác biệt là hệ thống không chỉ dự đoán bệnh, mà còn đánh giá dự đoán có đáng tin về mặt sinh lý hay không.

## 11. Thiết kế thực nghiệm

### 11.1. Baseline

Các baseline cần so sánh:

1. ResNet1D supervised.
2. InceptionTime supervised.
3. ECG-CLIP style baseline.
4. ECG-CLIP + rule-based confidence calibration.
5. ECG-CLIP + learned calibration.
6. ECG-CLIP + weighted contrastive learning nếu thời gian cho phép.

### 11.2. Tác vụ đánh giá

1. Multi-label ECG classification.
2. Zero-shot classification bằng text prompt.
3. Few-shot classification với 1%, 5%, 10% dữ liệu có nhãn.
4. ECG-to-text retrieval: ECG có tìm đúng report tương ứng không.
5. Text-to-ECG retrieval: report có tìm đúng ECG tương ứng không.
6. Calibration evaluation: xác suất có đáng tin không.

### 11.3. Metrics

Metrics phân loại:

- AUROC
- AUPRC
- F1-score
- Precision
- Recall
- Sensitivity
- Specificity

Metrics calibration:

- Expected Calibration Error
- Brier Score
- Reliability Diagram

Metrics retrieval:

- Recall@1
- Recall@5
- Mean Reciprocal Rank

## 12. Đóng góp khoa học dự kiến

Đề tài có thể có các đóng góp sau:

1. Đề xuất pipeline học biểu diễn ECG-text trên MIMIC-IV-ECG sử dụng raw ECG 12 đạo trình.
2. Đề xuất module đánh giá tính nhất quán sinh lý dựa trên machine measurements.
3. Đề xuất phương pháp hiệu chỉnh độ tin cậy cho ECG-text contrastive learning.
4. Phân tích tác động của nhãn nhiễu từ machine-generated reports.
5. So sánh giữa supervised learning, ECG-text contrastive learning và physiology-guided calibration.
6. Đánh giá mô hình trong bối cảnh zero-shot và few-shot.

## 13. Điểm khác biệt so với các bài đã có

| Tiêu chí | Hai bài đã tham khảo | Đề tài đề xuất |
|---|---|---|
| Dạng input | ECG chuyển thành ảnh 2D | Raw ECG waveform 12 đạo trình |
| Mô hình chính | CNN, ResNet, DenseNet | ECG encoder + text encoder |
| Kiểu học | Supervised classification | Contrastive multimodal learning |
| Text report | Ít hoặc không khai thác | Dùng làm nguồn giám sát |
| Độ tin cậy | Chưa phải trọng tâm | Có confidence calibration |
| Tri thức sinh lý ECG | Chủ yếu giải thích sau mô hình | Dùng trong calibration/training |
| Nhãn mới | Cần train/fine-tune lại | Có thể thử zero-shot bằng prompt |

## 14. Kế hoạch triển khai

### Giai đoạn 1: Chuẩn bị dữ liệu

- Hoàn thiện phân tích metadata.
- Tạo master metadata table.
- Chọn nhãn và cohort ban đầu.
- Tải subset waveform theo `study_id`.

### Giai đoạn 2: Baseline supervised

- Đọc waveform bằng WFDB.
- Train ResNet1D hoặc InceptionTime.
- Đánh giá multi-label classification.

### Giai đoạn 3: ECG-text contrastive baseline

- Tạo report text từ `report_0..report_17`.
- Xây dựng ECG encoder và text encoder.
- Huấn luyện contrastive loss.
- Đánh giá zero-shot/few-shot.

### Giai đoạn 4: Physiology-guided calibration

- Tạo rule consistency.
- Tính consistency score.
- Hiệu chỉnh confidence.
- So sánh với ECG-CLIP baseline.

### Giai đoạn 5: Phân tích và viết báo cáo

- Phân tích kết quả theo từng nhãn.
- Phân tích case đúng/sai.
- Phân tích nhóm consistency cao/thấp.
- Viết kết luận và hướng phát triển.

## 15. Rủi ro và phương án xử lý

| Rủi ro | Cách xử lý |
|---|---|
| Dữ liệu waveform quá lớn | Tải subset theo nhãn trước |
| Report text nhiễu | Dùng consistency score và lọc nhiễu |
| Tài nguyên GPU hạn chế | Dùng subset, model nhỏ, mixed precision |
| Text encoder nặng | Bắt đầu bằng sentence-transformer nhỏ hoặc frozen BERT |
| Zero-shot kém | Thử prompt engineering và few-shot fine-tuning |
| Machine measurements có sentinel values | Làm sạch trước khi tính chỉ số |

## 16. Tài liệu tham khảo ban đầu

1. MIMIC-IV-ECG: https://physionet.org/content/mimic-iv-ecg/1.0/
2. MIMIC-IV Clinical: https://physionet.org/content/mimiciv/3.1/
3. MIMIC-IV Documentation: https://mimic.mit.edu/docs/IV/
4. ECG-CLIP: Diagnosis of cardiac conditions from 12-lead ECG through natural language supervision.
5. K-MERL: Knowledge-enhanced Multimodal ECG Representation Learning.
6. Self-supervised representation learning from 12-lead ECG data.
7. PCLR: Patient Contrastive Learning of Representations.

## 17. Kết luận

Đề tài đề xuất không chỉ dừng lại ở việc phân loại ECG bằng CNN hoặc sao chép ECG-CLIP. Hướng nghiên cứu tập trung vào việc kết hợp raw ECG 12 đạo trình, report text và machine measurements để xây dựng mô hình ECG-text có khả năng dự đoán bất thường, đồng thời đánh giá độ tin cậy của dự đoán dựa trên tri thức sinh lý ECG.

Điểm mới chính là:

```text
ECG-text contrastive learning
+ physiology-guided confidence calibration
+ noise-aware report usage
```

Hướng này phù hợp với MIMIC-IV-ECG, khác biệt rõ so với các nghiên cứu chuyển ECG thành ảnh 2D, và có tiềm năng phát triển thành một khóa luận có chiều sâu về AI y tế hiện đại.
