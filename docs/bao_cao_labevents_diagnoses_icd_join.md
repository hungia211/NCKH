# Báo cáo riêng: labevents và diagnoses_icd trong MIMIC-IV v3.1 hosp

- Đường dẫn local: `G:\My Drive\UIT\NCKH\DTS\mimic-iv-3.1\mimic-iv-3.1\hosp`
- Ngày tạo: 2026-08-25
- Phạm vi: hai bảng `labevents` và `diagnoses_icd`, các dictionary/bảng có thể join, và dữ liệu minh họa join thật từ local.

## 1. labevents
- Số dòng local: 158,374,764; số cột: 16.
- Cột: `labevent_id, subject_id, hadm_id, specimen_id, itemid, order_provider_id, charttime, storetime, value, valuenum, valueuom, ref_range_lower, ref_range_upper, flag, priority, comments`.
- Ý nghĩa: mỗi dòng là một kết quả/sự kiện xét nghiệm. `itemid` mô tả loại xét nghiệm và nối với `d_labitems`; `subject_id` nối bệnh nhân; `hadm_id` nối admission nếu không thiếu; `charttime` là thời điểm xét nghiệm được ghi nhận/đo, `storetime` là thời điểm lưu vào hệ thống.
- Timestamp range local: charttime 2105-01-19 12:01:00 -> 2215-01-12 11:45:00; storetime 2105-01-19 12:26:00 -> 2215-01-12 15:59:00.
- Missing quan trọng: subject_id: 0 (0.0%); hadm_id: 73,768,897 (46.579%); labevent_id: 0 (0.0%); specimen_id: 0 (0.0%); itemid: 0 (0.0%); order_provider_id: 113,933,995 (71.939%); charttime: 0 (0.0%); storetime: 2,568,511 (1.622%); value: 16,062,783 (10.142%); valuenum: 21,490,341 (13.569%); valueuom: 26,555,866 (16.768%); ref_range_lower: 31,579,618 (19.94%); ref_range_upper: 31,579,618 (19.94%); flag: 112,405,302 (70.974%); priority: 7,652,745 (4.832%); comments: 130,357,314 (82.309%).

### 1.1. Các join có thể dùng từ labevents
| Khóa nguồn | Bảng/cột nối | Mục đích | Quan sát local |
| --- | --- | --- | --- |
| labevents.subject_id | patients.subject_id | Cấp bệnh nhân | orphan rows = 0 |
| labevents.hadm_id | admissions.hadm_id | Cấp lần nhập viện khi hadm_id không thiếu | missing = 73,768,897 (46.579%); orphan khi có hadm_id = 0 |
| labevents.itemid | d_labitems.itemid | Diễn giải tên xét nghiệm, fluid, category | orphan rows = 0 |
| labevents.order_provider_id | provider.provider_id | Provider order nếu trường không thiếu | Trường này thiếu nhiều trong local, cần kiểm tra trước khi dùng |
| labevents.specimen_id | labevents.specimen_id | Gom các xét nghiệm cùng specimen trong nội bộ labevents | Không phải dictionary ngoài trong hosp |

### 1.2. Top xét nghiệm sau join d_labitems
| itemid | label | fluid | category | số dòng |
| --- | --- | --- | --- | --- |
| 51221 | Hematocrit | Blood | Hematology | 4,331,615 |
| 50912 | Creatinine | Blood | Chemistry | 4,319,091 |
| 51265 | Platelet Count | Blood | Hematology | 4,214,048 |
| 51006 | Urea Nitrogen | Blood | Chemistry | 4,202,807 |
| 51222 | Hemoglobin | Blood | Hematology | 4,181,121 |
| 51301 | White Blood Cells | Blood | Hematology | 4,157,284 |
| 51249 | MCHC | Blood | Hematology | 4,152,226 |
| 51279 | Red Blood Cells | Blood | Hematology | 4,152,106 |
| 51250 | MCV | Blood | Hematology | 4,152,105 |
| 51248 | MCH | Blood | Hematology | 4,152,104 |
| 51277 | RDW | Blood | Hematology | 4,151,884 |
| 50971 | Potassium | Blood | Chemistry | 4,149,507 |
| 50983 | Sodium | Blood | Chemistry | 4,111,289 |
| 50902 | Chloride | Blood | Chemistry | 4,055,101 |
| 50882 | Bicarbonate | Blood | Chemistry | 3,934,240 |

## 2. diagnoses_icd
- Số dòng local: 6,364,488; số cột: 5.
- Cột: `subject_id, hadm_id, seq_num, icd_code, icd_version`.
- Ý nghĩa: chẩn đoán ICD ở cấp admission; `seq_num` là thứ tự chẩn đoán; `icd_code` phải đi kèm `icd_version` để nối đúng dictionary.
- Missing quan trọng: subject_id: 0 (0.0%); hadm_id: 0 (0.0%); seq_num: 0 (0.0%); icd_code: 0 (0.0%); icd_version: 0 (0.0%).

### 2.1. Các join có thể dùng từ diagnoses_icd
| Khóa nguồn | Bảng/cột nối | Mục đích | Quan sát local |
| --- | --- | --- | --- |
| diagnoses_icd.subject_id | patients.subject_id | Cấp bệnh nhân | orphan rows = 0 |
| diagnoses_icd.hadm_id | admissions.hadm_id | Cấp lần nhập viện | orphan rows = 0 |
| diagnoses_icd.icd_code + icd_version | d_icd_diagnoses.icd_code + icd_version | Diễn giải tên chẩn đoán ICD | orphan rows = 0 |
| diagnoses_icd.hadm_id | labevents.hadm_id | Ghép chẩn đoán với xét nghiệm trong cùng admission | Chỉ áp dụng cho lab rows có hadm_id; labevents thiếu hadm_id 46.579% |

### 2.2. Top chẩn đoán sau join d_icd_diagnoses
| icd_code | version | long_title | số dòng |
| --- | --- | --- | --- |
| 4019 | 9 | Unspecified essential hypertension | 102,368 |
| E785 | 10 | Hyperlipidemia, unspecified | 84,570 |
| I10 | 10 | Essential (primary) hypertension | 83,775 |
| 2724 | 9 | Other and unspecified hyperlipidemia | 67,293 |
| Z87891 | 10 | Personal history of nicotine dependence | 62,806 |
| K219 | 10 | Gastro-esophageal reflux disease without esophagitis | 56,157 |
| 53081 | 9 | Esophageal reflux | 48,628 |
| 25000 | 9 | Diabetes mellitus without mention of complication, type II or unspecified type, not stated as uncontrolled | 43,077 |
| F329 | 10 | Major depressive disorder, single episode, unspecified | 41,876 |
| I2510 | 10 | Atherosclerotic heart disease of native coronary artery without angina pectoris | 41,550 |
| F419 | 10 | Anxiety disorder, unspecified | 38,911 |
| 42731 | 9 | Atrial fibrillation | 37,070 |
| 4280 | 9 | Congestive heart failure, unspecified | 36,606 |
| 311 | 9 | Depressive disorder, not elsewhere classified | 36,349 |
| 41401 | 9 | Coronary atherosclerosis of native coronary artery | 36,083 |

## 3. Minh họa join thật trên một vài admission
Các dòng dưới đây được lấy trực tiếp từ dữ liệu local. Luồng join: `patients` -> `admissions` -> `diagnoses_icd` + `d_icd_diagnoses`, và `admissions` -> `labevents` + `d_labitems`.

### subject_id=10005749, hadm_id=20010003
- Patient/admission: gender=F, anchor_age=63, admission_type=DIRECT EMER., admittime=2140-09-23 17:59:00, dischtime=2140-09-29 15:30:00.
**Diagnoses joined with d_icd_diagnoses**
| seq | icd | ver | long_title |
| --- | --- | --- | --- |
| 1 | 42823 | 9 | Acute on chronic systolic heart failure |
| 2 | 5849 | 9 | Acute kidney failure, unspecified |
| 3 | V420 | 9 | Kidney replaced by transplant |
| 4 | 75162 | 9 | Congenital cystic disease of liver |
| 5 | 28419 | 9 | Other pancytopenia |
**Labs joined with d_labitems**
| labevent_id | charttime | itemid | label | fluid | value | valuenum | unit | flag |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 94210 | 2140-09-23 19:15:00 | 51237 | INR(PT) | Blood | 1.1 | 1.1 | None | None |
| 94211 | 2140-09-23 19:15:00 | 51274 | PT | Blood | ___ | 11.8 | sec | None |
| 94212 | 2140-09-23 19:15:00 | 51275 | PTT | Blood | ___ | 31 | sec | None |
| 94213 | 2140-09-23 19:15:00 | 51146 | Basophils | Blood | 0.5 | 0.5 | % | None |
| 94214 | 2140-09-23 19:15:00 | 51200 | Eosinophils | Blood | 1.8 | 1.8 | % | None |

### subject_id=10017886, hadm_id=20015927
- Patient/admission: gender=F, anchor_age=80, admission_type=EW EMER., admittime=2140-12-15 18:55:00, dischtime=2140-12-20 17:30:00.
**Diagnoses joined with d_icd_diagnoses**
| seq | icd | ver | long_title |
| --- | --- | --- | --- |
| 1 | 42843 | 9 | Acute on chronic combined systolic and diastolic heart failure |
| 2 | 5990 | 9 | Urinary tract infection, site not specified |
| 3 | 99664 | 9 | Infection and inflammatory reaction due to indwelling urinary catheter |
| 4 | 70711 | 9 | Ulcer of thigh |
| 5 | 4280 | 9 | Congestive heart failure, unspecified |
**Labs joined with d_labitems**
| labevent_id | charttime | itemid | label | fluid | value | valuenum | unit | flag |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 293945 | 2140-12-16 05:00:00 | 51221 | Hematocrit | Blood | 35.2 | 35.2 | % | abnormal |
| 293946 | 2140-12-16 05:00:00 | 51222 | Hemoglobin | Blood | 11.8 | 11.8 | g/dL | abnormal |
| 293947 | 2140-12-16 05:00:00 | 51248 | MCH | Blood | 33.1 | 33.1 | pg | abnormal |
| 293948 | 2140-12-16 05:00:00 | 51249 | MCHC | Blood | 33.5 | 33.5 | % | None |
| 293949 | 2140-12-16 05:00:00 | 51250 | MCV | Blood | 99 | 99 | fL | abnormal |

### subject_id=10037602, hadm_id=20016088
- Patient/admission: gender=F, anchor_age=58, admission_type=EW EMER., admittime=2154-11-14 02:21:00, dischtime=2154-11-16 19:00:00.
**Diagnoses joined with d_icd_diagnoses**
| seq | icd | ver | long_title |
| --- | --- | --- | --- |
| 1 | L239 | 10 | Allergic contact dermatitis, unspecified cause |
| 2 | L02223 | 10 | Furuncle of chest wall |
| 3 | L299 | 10 | Pruritus, unspecified |
| 4 | I10 | 10 | Essential (primary) hypertension |
| 5 | E785 | 10 | Hyperlipidemia, unspecified |
**Labs joined with d_labitems**
| labevent_id | charttime | itemid | label | fluid | value | valuenum | unit | flag |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 586110 | 2154-11-13 20:35:00 | 50955 | Light Green Top Hold | Blood | ___ | None | None | None |
| 586111 | 2154-11-13 20:35:00 | 50813 | Lactate | Blood | 1.2 | 1.2 | mmol/L | None |
| 586112 | 2154-11-13 20:35:00 | 50825 | Temperature | Blood | 36.9 | 36.9 | None | None |
| 586113 | 2154-11-13 20:35:00 | 52033 | Specimen Type | Blood | VEN. | None | None | None |
| 586114 | 2154-11-13 20:35:00 | 50861 | Alanine Aminotransferase (ALT) | Blood | 22 | 22 | IU/L | None |

## 4. Nhận xét thực hành
- Join `diagnoses_icd` rất sạch trong local: subject_id/hadm_id/dictionary ICD đều không có orphan rows trong kiểm tra này.
- Join `labevents` với `d_labitems` sạch theo itemid trong local, nhưng gần một nửa lab rows thiếu hadm_id nên không thể luôn gắn lab vào admission.
- Khi cần ghép lab với diagnosis, nên ưu tiên các lab rows có hadm_id; với lab rows thiếu hadm_id, cần dùng subject_id + charttime và admission window nếu muốn ánh xạ về admission.
- Không nên nối ICD chỉ bằng icd_code; phải dùng cả icd_version vì ICD-9 và ICD-10 có không gian mã khác nhau.
- Để chuẩn bị Clinical-ECG, cặp labevents+d_labitems cung cấp biến xét nghiệm theo thời gian; diagnoses_icd+d_icd_diagnoses cung cấp phenotype theo admission.

## 5. Nguồn
- PhysioNet MIMIC-IV v3.1: https://physionet.org/content/mimiciv/3.1/
- MIMIC-IV hosp documentation: https://mimic.mit.edu/docs/iv/modules/hosp/
- Quan sát local từ các file hosp trong đường dẫn dataset của người dùng.
