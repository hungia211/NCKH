# Luồng xây dựng mô hình kết hợp MIMIC-IV-ECG và MIMIC-IV v3.1 hosp

## 1. Mục tiêu nghiên cứu

Dự án hướng tới xây dựng một pipeline học máy đa phương thức để hỗ trợ chẩn đoán và phản ánh trạng thái sinh lý của bệnh nhân bằng cách kết hợp:

- **MIMIC-IV-ECG v1.0**: tín hiệu ECG 12 đạo trình, machine measurements và báo cáo ECG.
- **MIMIC-IV v3.1 hosp**: thông tin bệnh nhân, nhập viện, xét nghiệm trong `labevents`, và chẩn đoán ICD trong `diagnoses_icd`.

Ý tưởng cốt lõi:

```text
ECG waveform + xét nghiệm gần thời điểm ECG + thông tin bệnh nhân
        -> mô hình học biểu diễn / mô hình chẩn đoán
        -> dự đoán nhãn bệnh hoặc trạng thái sinh lý
```

Trong đó, `labevents` nên được xem là nguồn phản ánh trạng thái sinh lý quanh thời điểm ECG, còn `diagnoses_icd` nên được dùng chủ yếu để tạo nhãn bệnh theo lần nhập viện.

## 2. Vai trò của từng nguồn dữ liệu

### MIMIC-IV-ECG

MIMIC-IV-ECG cung cấp khoảng 800.000 ECG chẩn đoán 12 đạo trình, mỗi ECG dài khoảng 10 giây và lấy mẫu ở 500 Hz. Các trường quan trọng:

- `subject_id`: định danh bệnh nhân, dùng để nối với MIMIC-IV Clinical.
- `study_id`: định danh một lần đo ECG.
- `ecg_time`: thời điểm đo ECG.
- `path`: đường dẫn tới waveform `.hea` và `.dat`.
- `machine_measurements.csv`: chứa `report_0..report_17` và các thông số máy đo như `rr_interval`, `qrs_onset`, `qrs_end`, `t_end`, `qrs_axis`.
- `waveform_note_links.csv`: liên kết waveform với cardiologist report khi có.

Không phải toàn bộ ECG đều nằm trong một lần nhập viện. Vì vậy cần match ECG với `admissions` bằng `subject_id` và khoảng thời gian nhập viện.

### MIMIC-IV v3.1 hosp

Module `hosp` là dữ liệu bệnh viện diện rộng. Các bảng quan trọng cho hướng nghiên cứu hiện tại:

- `patients`: tuổi neo, giới, năm neo.
- `admissions`: mỗi lần nhập viện, gồm `hadm_id`, `admittime`, `dischtime`, `admission_type`, `hospital_expire_flag`.
- `labevents`: kết quả xét nghiệm theo thời gian.
- `d_labitems`: từ điển giải nghĩa `itemid` trong `labevents`.
- `diagnoses_icd`: mã ICD-9/ICD-10 được gán cho lần nhập viện.
- `d_icd_diagnoses`: từ điển giải nghĩa ICD code.

## 3. Nguyên tắc dùng `diagnoses_icd`

Nên dùng `diagnoses_icd`, nhưng phải dùng đúng vai trò.

### Nên dùng

Dùng `diagnoses_icd` để tạo nhãn bệnh hoặc phenotype:

```text
ECG + lab trước ECG -> dự đoán heart failure / myocardial infarction / atrial fibrillation / CKD / sepsis
```

Các nhãn có thể bắt đầu:

- Heart failure.
- Acute myocardial infarction.
- Atrial fibrillation.
- Ischemic heart disease.
- Chronic kidney disease.
- Sepsis.
- Electrolyte disorder.
- Respiratory failure hoặc hypoxia-related condition nếu mã ICD phù hợp.

### Không nên dùng

Không nên đưa trực tiếp `diagnoses_icd` vào input nếu mục tiêu là mô hình chẩn đoán bệnh. ICD là thông tin billing/chẩn đoán sau quá trình điều trị hoặc sau xuất viện, nên nếu dùng làm input sẽ gây **label leakage**.

Ví dụ nên tránh:

```text
Input: ECG + lab + diagnoses_icd
Output: disease diagnosis
```

Ví dụ đúng hơn:

```text
Input: ECG + lab trước hoặc gần ecg_time + demographic/admission context
Output: ICD-derived disease labels
```

## 4. Cách match ECG với admission

MIMIC-IV-ECG có `subject_id` và `ecg_time`, nhưng không có sẵn `hadm_id`. Vì vậy cần suy ra `hadm_id` từ bảng `admissions`.

Điều kiện match cơ bản:

```sql
ecg.subject_id = admissions.subject_id
AND ecg.ecg_time BETWEEN admissions.admittime AND admissions.dischtime
```

Kết quả mong muốn:

```text
subject_id
study_id
ecg_time
path
hadm_id
admittime
dischtime
admission_type
hospital_expire_flag
```

Với ECG không match admission:

- Giai đoạn đầu nên loại bỏ để pipeline đơn giản.
- Giai đoạn sau có thể xử lý riêng outpatient/ED ECG nếu có thêm dữ liệu ED hoặc note.

## 5. Tạo feature từ `labevents`

`labevents` nên được dùng để phản ánh trạng thái sinh lý của bệnh nhân quanh thời điểm ECG.

### Cửa sổ thời gian đề xuất

Nếu mục tiêu là chẩn đoán tại thời điểm ECG, nên ưu tiên lab trước ECG:

```text
ecg_time - 24h <= charttime <= ecg_time
```

Có thể thử thêm các biến thể:

```text
[-6h, 0h]
[-12h, 0h]
[-24h, 0h]
[-24h, +6h] nếu mục tiêu là mô tả trạng thái quanh ECG, không phải dự đoán real-time
```

Không nên dùng lab sau ECG quá xa nếu claim là mô hình dự đoán tại thời điểm ECG.

### Nhóm xét nghiệm nên ưu tiên

Nên chọn item bằng cách tra `d_labitems`, không hardcode vội `itemid`.

Các nhóm lab quan trọng:

- Điện giải: potassium, sodium, chloride, calcium, magnesium, bicarbonate.
- Chức năng thận: creatinine, BUN.
- Tim mạch: troponin, BNP hoặc NT-proBNP nếu có.
- Khí máu/toan kiềm: pH, pCO2, pO2, lactate, bicarbonate.
- Huyết học: hemoglobin, hematocrit, WBC, platelet.
- Viêm/nhiễm trùng: WBC, lactate, CRP nếu có.
- Chuyển hóa: glucose.

### Cách tổng hợp lab

Với mỗi ECG và mỗi loại xét nghiệm, tạo feature:

```text
latest_value_before_ecg
min_value_before_ecg
max_value_before_ecg
mean_value_before_ecg
is_abnormal_by_flag
time_since_last_lab_hours
missing_indicator
```

Giai đoạn đầu có thể dùng `latest_value_before_ecg` và `missing_indicator` trước để đơn giản.

## 6. Tạo label từ `diagnoses_icd`

Sau khi match được ECG với `hadm_id`, join:

```text
ecg_admission.hadm_id -> diagnoses_icd.hadm_id
diagnoses_icd.icd_code + icd_version -> d_icd_diagnoses
```

Mỗi ECG có thể nhận nhiều nhãn bệnh từ cùng một admission, vì vậy bài toán nên là **multi-label classification**.

Output label dạng:

```text
heart_failure: 0/1
myocardial_infarction: 0/1
atrial_fibrillation: 0/1
chronic_kidney_disease: 0/1
sepsis: 0/1
electrolyte_disorder: 0/1
```

Cần xây dựng mapping ICD-9 và ICD-10 cho từng phenotype. Không nên chỉ dùng text search trên `long_title` nếu muốn kết quả nghiên cứu nghiêm túc; text search có thể dùng để EDA ban đầu, sau đó cần kiểm tra code set.

## 7. Bảng master dataset đề xuất

Một dòng tương ứng với một ECG:

```text
subject_id
study_id
ecg_time
path
hadm_id
age_at_ecg
gender
admission_type
hospital_expire_flag

ecg_waveform_path
ecg_machine_report_text
ecg_machine_measurements

lab_features_before_ecg
lab_missing_indicators

icd_derived_labels
```

Tên file output gợi ý:

```text
data/processed/ecg_hosp_master.parquet
data/processed/ecg_hosp_labels.parquet
data/processed/ecg_hosp_lab_features.parquet
```

Nên ưu tiên Parquet thay vì CSV khi dữ liệu lớn.

## 8. Luồng xây dựng model

### Giai đoạn 1: Dataset và baseline tabular

Mục tiêu là chứng minh pipeline join dữ liệu đúng trước khi đụng tới deep learning waveform.

Input:

```text
demographics + admission context + lab features trước ECG
```

Output:

```text
ICD-derived labels
```

Model:

- Logistic Regression.
- Random Forest.
- XGBoost hoặc LightGBM nếu có.
- MLP nhỏ cho tabular.

### Giai đoạn 2: ECG-only baseline

Input:

```text
ECG waveform 12 x 5000
```

Model:

- 1D CNN.
- ResNet1D.
- InceptionTime.
- Transformer 1D nếu đủ tài nguyên.

Output:

```text
ICD-derived labels hoặc ECG abnormality labels
```

### Giai đoạn 3: Multimodal ECG + lab

Kiến trúc đề xuất:

```text
ECG waveform -> ECG encoder -> ECG embedding
                                      \
                                       concat -> fusion MLP -> sigmoid outputs
                                      /
Lab features  -> Lab encoder -> Lab embedding
```

Loss:

```text
Binary Cross Entropy
Weighted BCE hoặc Focal Loss nếu mất cân bằng nhãn
```

Metrics:

- AUROC.
- AUPRC.
- F1-score.
- Precision.
- Recall.
- Sensitivity.
- Specificity.

Với bệnh hiếm hoặc dữ liệu mất cân bằng, AUPRC quan trọng hơn accuracy.

### Giai đoạn 4: ECG-text và physiology-guided calibration

Khi đã có pipeline ổn định, có thể mở rộng sang ECG-text contrastive learning:

```text
ECG waveform -> ECG encoder -> ECG embedding
Report text  -> Text encoder -> Text embedding
```

Sau đó dùng lab và machine measurements để kiểm tra consistency:

```text
tachycardia prediction <-> heart_rate
prolonged QT prediction <-> QT/QTc
bundle branch block <-> QRS duration
axis deviation <-> qrs_axis
myocardial injury <-> troponin
electrolyte-related ECG changes <-> potassium/calcium/magnesium
```

## 9. Chia dữ liệu và tránh leakage

Nguyên tắc quan trọng nhất:

```text
Train/validation/test phải chia theo subject_id, không chia theo study_id.
```

Lý do: một bệnh nhân có thể có nhiều ECG. Nếu cùng bệnh nhân xuất hiện ở cả train và test, model có thể học đặc điểm cá nhân thay vì học tín hiệu bệnh.

Các nguy cơ leakage cần tránh:

- Dùng `diagnoses_icd` làm input khi nó là label.
- Dùng lab sau ECG quá xa để dự đoán tại thời điểm ECG.
- Chia dữ liệu theo ECG thay vì theo bệnh nhân.
- Dùng cardiologist report hoặc machine report làm input nếu output là cùng chẩn đoán được suy ra từ report.
- Tạo label từ toàn bộ admission nhưng input lấy ở thời điểm quá sớm; cần mô tả rõ đây là dự đoán diagnosis trong admission, không phải chẩn đoán tức thời.

## 10. Sơ đồ pipeline tổng quát

```text
MIMIC-IV-ECG record_list
        |
        | subject_id + ecg_time
        v
MIMIC-IV hosp admissions
        |
        +----> match hadm_id
        |
        +----> labevents before ecg_time
        |
        +----> diagnoses_icd labels
        |
        v
ECG-hosp master dataset
        |
        +----> tabular/lab baseline
        |
        +----> ECG-only baseline
        |
        +----> ECG + lab multimodal model
        |
        v
Evaluation by subject-level split
```

## 11. Task tiếp theo nên giao cho agent AI

1. Viết script đọc metadata ECG và match ECG với `admissions` bằng `subject_id`, `admittime`, `dischtime`.
2. Viết script chọn danh sách lab item quan trọng từ `d_labitems`.
3. Viết module tạo lab features theo cửa sổ `[-24h, 0h]` trước ECG.
4. Viết module tạo ICD phenotype labels từ `diagnoses_icd`.
5. Tạo master dataset dạng Parquet.
6. Viết baseline tabular model dùng lab features.
7. Viết baseline ECG-only model cho một subset nhỏ.
8. Viết multimodal model ECG + lab.

## 12. Nguồn tham khảo chính

- MIMIC-IV-ECG v1.0 PhysioNet: https://physionet.org/content/mimic-iv-ecg/1.0/
- MIMIC-IV v3.1 PhysioNet: https://physionet.org/content/mimiciv/3.1/
- MIMIC-IV schema overview: https://mimic.mit.edu/docs/iv/about/schema-overview.html
- `labevents`: https://mimic.mit.edu/docs/iv/modules/hosp/labevents.html
- `diagnoses_icd`: https://mimic.mit.edu/docs/iv/modules/hosp/diagnoses_icd.html
- `d_labitems`: https://mimic.mit.edu/docs/iv/modules/hosp/d_labitems.html

