# PROJECT CONTEXT

Bạn đang hỗ trợ tôi thực hiện một đề tài nghiên cứu về Machine Learning và dữ liệu y tế.

## 1. Tên đề tài

**Tiếng Việt:**
Xây dựng mô hình chẩn đoán bệnh dựa trên dữ liệu xét nghiệm cận lâm sàng của bệnh viện Beth Israel Deaconess, Hoa Kỳ.

**Tiếng Anh:**
Development of a Disease Diagnosis Model Using Clinical Laboratory Data from Beth Israel Deaconess Medical Center, USA.

Dataset chính được sử dụng là **MIMIC-IV v3.1**.

---

## 2. Mục tiêu nghiên cứu

Mục tiêu của nghiên cứu là xây dựng và đánh giá mô hình Machine Learning sử dụng **dữ liệu xét nghiệm cận lâm sàng (laboratory data)** trong MIMIC-IV để dự đoán các nhóm bệnh có khả năng liên quan đến một lần nhập viện.

Mô hình không được xem là công cụ đưa ra chẩn đoán y khoa xác định.

Kết quả của mô hình được hiểu là:

* dự đoán xác suất hoặc khả năng liên quan của các nhóm bệnh;
* cung cấp thông tin gợi ý hỗ trợ chẩn đoán;
* nghiên cứu mối liên hệ giữa dữ liệu xét nghiệm và các bệnh được ghi nhận trong admission.

Không diễn giải kết quả theo hướng nhân quả, ví dụ không được kết luận:

> “Creatinine cao gây ra bệnh thận.”

Chỉ có thể diễn giải theo hướng:

> “Creatinine có đóng góp quan trọng vào dự đoán của mô hình đối với nhóm bệnh thận.”

---

# 3. Định nghĩa bài toán

Đơn vị phân tích chính là một **hospital admission**, được xác định bởi:

`hadm_id`

Một bệnh nhân (`subject_id`) có thể có nhiều lần nhập viện (`hadm_id`).

Một admission có:

* nhiều lần xét nghiệm;
* nhiều loại xét nghiệm;
* nhiều mã chẩn đoán ICD.

Vì một admission có thể có nhiều bệnh đồng thời, bài toán được xây dựng dưới dạng:

**Multi-label classification**

Không phải multiclass classification.

Ví dụ:

| hadm_id | Kidney Disease | Heart Failure | Anemia | Liver Disease |
| ------- | -------------: | ------------: | -----: | ------------: |
| 10001   |              1 |             0 |      1 |             0 |
| 10002   |              0 |             1 |      0 |             1 |

Một admission có thể có nhiều giá trị `1`.

---

# 4. Dữ liệu sử dụng

Nghiên cứu tập trung vào **module HOSP của MIMIC-IV v3.1**.

Các bảng chính:

### `hosp.labevents`

Nguồn dữ liệu đầu vào chính.

Chứa các kết quả xét nghiệm của bệnh nhân.

Các trường quan trọng có thể bao gồm:

* `subject_id`
* `hadm_id`
* `itemid`
* `charttime`
* `valuenum`
* `valueuom`
* `ref_range_lower`
* `ref_range_upper`
* `flag`

### `hosp.d_labitems`

Dictionary của các loại xét nghiệm.

Liên kết:

`labevents.itemid = d_labitems.itemid`

Dùng để xác định:

* tên xét nghiệm;
* loại mẫu;
* category;
* ý nghĩa của `itemid`.

### `hosp.diagnoses_icd`

Nguồn chính để xây dựng nhãn bệnh.

Các trường quan trọng:

* `subject_id`
* `hadm_id`
* `seq_num`
* `icd_code`
* `icd_version`

Một `hadm_id` có thể có nhiều ICD codes.

### `hosp.d_icd_diagnoses`

Dictionary mô tả ICD.

Liên kết với `diagnoses_icd` bằng:

`icd_code + icd_version`

Không sử dụng bảng này để xác định bệnh của bệnh nhân vì đây chỉ là dictionary.

### `hosp.admissions`

Dùng để lấy thông tin của hospital admission, đặc biệt là thời gian nhập viện và xuất viện.

---

# 5. Input của mô hình – X

Input chính là các kết quả xét nghiệm từ `labevents`.

Dữ liệu ban đầu có dạng long format:

```text
hadm_id | itemid | charttime | valuenum
10001   | A      | t1        | 1.2
10001   | A      | t2        | 1.5
10001   | B      | t1        | 7.3
```

Dữ liệu cần được xử lý thành feature matrix theo admission.

Ví dụ:

```text
hadm_id | Creatinine_first | Creatinine_mean | WBC_first | ...
10001   | 1.2              | 1.35            | 7.3       | ...
```

Các phương pháp aggregation cần được **khảo sát dựa trên dữ liệu**, không được mặc định ngay từ đầu.

Có thể nghiên cứu:

* first
* mean
* median
* min
* max
* last
* standard deviation
* delta/change

Không mặc định tất cả các feature này đều cần sử dụng.

---

# 6. Early-admission laboratory window

Đây là một nguyên tắc quan trọng của nghiên cứu.

Không mặc định sử dụng toàn bộ xét nghiệm trong suốt admission để dự đoán diagnosis của cùng admission.

Lý do:

Các xét nghiệm ở giai đoạn muộn có thể được thực hiện sau khi bác sĩ đã xác định bệnh hoặc bắt đầu điều trị, gây nguy cơ **information leakage**.

Nghiên cứu sẽ khảo sát dữ liệu xét nghiệm ở giai đoạn sớm của admission.

Các cửa sổ có thể khảo sát, ví dụ:

* 6 giờ đầu;
* 12 giờ đầu;
* 24 giờ đầu.

Thời gian chính thức **chưa được quyết định**.

Không tự ý chọn 24 giờ hoặc một window cụ thể nếu chưa có kết quả phân tích dữ liệu hoặc yêu cầu từ tôi.

---

# 7. Output của mô hình – Y

Nguồn:

`diagnoses_icd`

MIMIC-IV chứa cả:

* ICD-9
* ICD-10

Không sử dụng trực tiếp hàng chục nghìn ICD codes làm output cuối cùng.

Pipeline dự kiến:

```text
diagnoses_icd
      ↓
ICD-9 / ICD-10
      ↓
ICD → Phecode mapping
      ↓
Disease phenotypes
      ↓
Multi-label target
```

---

# 8. Vai trò của Phecode

Phecode chỉ được sử dụng để:

* chuẩn hóa ICD-9 và ICD-10;
* giảm độ chi tiết của không gian nhãn;
* nhóm các ICD codes có liên quan thành phenotype bệnh;
* xây dựng target labels phù hợp cho Machine Learning.

**Phecode không phải trọng tâm của nghiên cứu.**

Không biến nghiên cứu thành nghiên cứu về Phecode/PheWAS.

Trọng tâm vẫn là:

**Laboratory data → Machine Learning → Disease prediction/diagnostic support**

Trước khi quyết định tập nhãn cuối cùng phải:

1. Map ICD → Phecode.
2. Kiểm tra mapping coverage.
3. Thống kê số admission của từng phenotype.
4. Kiểm tra label frequency.
5. Loại các phenotype quá hiếm nếu cần.
6. Chỉ sau đó mới quyết định final label set.

Không tự ý đặt threshold loại phenotype nếu chưa phân tích dữ liệu.

---

# 9. Dataset cuối cùng

Dataset dự kiến có cấu trúc:

```text
                    FEATURES (X)                    LABELS (Y)

hadm_id | Cr | WBC | HGB | Na | K | ... | Kidney | Heart | Anemia | ...
---------------------------------------------------------------------------
10001   | .. | ... | ... | .. | . | ... |    1   |   0   |   1    | ...
10002   | .. | ... | ... | .. | . | ... |    0   |   1   |   0    | ...
```

Mỗi hàng đại diện cho **một admission (`hadm_id`)**.

---

# 10. Train / Validation / Test

Phải đặc biệt chú ý data leakage.

Một `subject_id` có thể có nhiều `hadm_id`.

Không nên để:

```text
Patient A → admission 1 → Train
Patient A → admission 2 → Test
```

Ưu tiên chia dữ liệu theo **`subject_id`** để các admission của cùng một bệnh nhân không xuất hiện ở các tập khác nhau.

---

# 11. Modeling

Không mặc định một thuật toán là tốt nhất trước khi thực nghiệm.

Dự kiến khảo sát các mô hình như:

* Logistic Regression / các baseline phù hợp;
* Random Forest;
* XGBoost;
* LightGBM;
* các phương pháp khác nếu có cơ sở phù hợp.

Phải có **baseline** trước khi sử dụng mô hình phức tạp.

Đây là bài toán multi-label nên cần lựa chọn chiến lược/model phù hợp với multi-label classification.

---

# 12. Evaluation

Do dữ liệu bệnh có thể mất cân bằng, không sử dụng Accuracy làm metric chính.

Các metric dự kiến:

* F1-score;
* Micro-F1;
* Macro-F1;
* AUROC;
* AUPRC;
* per-label AUROC/AUPRC/F1;
* Sensitivity/Recall khi phù hợp.

Cần đánh giá:

1. Hiệu quả tổng thể của mô hình.
2. Hiệu quả trên từng phenotype.
3. Ảnh hưởng của class imbalance.
4. Những phenotype nào có thể dự đoán tốt từ laboratory data.
5. Những phenotype nào khó dự đoán chỉ từ laboratory data.

---

# 13. Model Explainability

Có thể sử dụng các phương pháp như:

**SHAP (SHapley Additive exPlanations)**

để nghiên cứu feature contribution.

Ví dụ:

```text
Prediction:
Kidney phenotype = 0.83

Feature contribution:
Creatinine ↑
BUN ↑
Potassium ↑
...
```

Không được diễn giải SHAP theo quan hệ nhân quả.

SHAP chỉ cho biết feature đóng góp như thế nào vào prediction của model.

---

# 14. Quy trình nghiên cứu tổng thể

```text
MIMIC-IV v3.1
        │
        ├───────────────────────┐
        ↓                       ↓
    LABEVENTS              DIAGNOSES_ICD
        ↓                       ↓
   D_LABITEMS             ICD-9 / ICD-10
        ↓                       ↓
Khảo sát dữ liệu           ICD → Phecode
        ↓                       ↓
Early admission            Disease phenotypes
window                          ↓
        ↓                  Multi-label Y
Lab selection                   │
        ↓                       │
Preprocessing                   │
        ↓                       │
Feature engineering             │
        ↓                       │
Multi-label X ──────────────────┘
        ↓
Final Dataset
        ↓
Patient-level split
        ↓
Train / Validation / Test
        ↓
Baseline Models
        ↓
Advanced Models
        ↓
Evaluation
        ↓
Per-label Analysis
        ↓
SHAP / Feature Importance
        ↓
Research Conclusions
```

---

# 15. Các giai đoạn thực hiện

## Giai đoạn 1 – Data Exploration

Khảo sát:

* số `subject_id`;
* số `hadm_id`;
* số admission có lab;
* số loại xét nghiệm;
* frequency của từng lab;
* missing;
* đơn vị đo;
* số ICD-9;
* số ICD-10;
* số diagnosis/admission;
* phân bố diagnosis.

Không lọc dữ liệu mạnh ở giai đoạn này.

Mục tiêu là hiểu dữ liệu trước.

## Giai đoạn 2 – Cohort Definition

Xác định:

* admission đủ điều kiện;
* admission có laboratory data;
* admission có diagnosis;
* early-admission window;
* inclusion/exclusion criteria.

Mọi quyết định lọc cohort phải được ghi lại.

## Giai đoạn 3 – Laboratory Feature Engineering

Thực hiện:

* lựa chọn lab;
* kiểm tra `itemid`;
* kiểm tra đơn vị;
* xử lý missing;
* xử lý outlier;
* aggregation;
* long → wide;
* tạo X theo `hadm_id`.

## Giai đoạn 4 – Disease Label Construction

Thực hiện:

* xử lý ICD-9/ICD-10;
* ICD → Phecode;
* mapping coverage;
* phenotype frequency;
* lựa chọn labels;
* tạo multi-label Y.

## Giai đoạn 5 – Final Dataset

Thực hiện:

`X + Y → hadm_id-level dataset`

Sau đó:

* kiểm tra missing;
* kiểm tra class imbalance;
* kiểm tra leakage;
* patient-level split.

## Giai đoạn 6 – Modeling

Thực hiện:

* baseline;
* model training;
* imbalance handling;
* hyperparameter tuning;
* model comparison.

## Giai đoạn 7 – Evaluation & Explainability

Thực hiện:

* F1;
* AUROC;
* AUPRC;
* per-label analysis;
* error analysis;
* SHAP/feature importance;
* phân tích giới hạn của nghiên cứu.

---

# 16. Nguyên tắc khi hỗ trợ tôi

Đây là các nguyên tắc bắt buộc khi làm việc trong project này.

### Không tự ý thay đổi research design

Nếu phát hiện một phương pháp tốt hơn, hãy:

1. giải thích vấn đề;
2. đề xuất phương án;
3. nêu ưu/nhược điểm;
4. chờ tôi quyết định trước khi thay đổi pipeline lớn.

### Không tự đặt threshold tùy ý

Ví dụ không tự quyết định:

* chỉ lấy top 30 labs;
* phenotype phải có ≥1000 admission;
* sử dụng 24h đầu;
* missing >50% thì loại;
* chỉ sử dụng primary diagnosis.

Nếu cần threshold, trước tiên hãy thống kê dữ liệu và đề xuất threshold dựa trên kết quả.

### Không nhầm dictionary với patient data

`d_labitems` = laboratory dictionary.

`d_icd_diagnoses` = ICD dictionary.

Patient/admission-level data nằm ở:

`labevents` và `diagnoses_icd`.

### Không biến bài toán thành single-disease classification

Không tự chọn Sepsis, AKI, Heart Failure... làm duy nhất một target trừ khi tôi yêu cầu.

Bài toán chính hiện tại là **multi-label disease prediction**.

### Không coi ICD là thời điểm chẩn đoán

`diagnoses_icd` cho biết diagnosis được ghi nhận cho admission nhưng không cung cấp thời điểm chính xác bác sĩ xác lập từng diagnosis.

Không được tuyên bố:

> “Mô hình dự đoán bệnh trước khi bác sĩ chẩn đoán.”

Nếu không có bằng chứng thời gian phù hợp.

### Ưu tiên reproducibility

Mỗi bước xử lý cần:

* lưu code;
* ghi rõ input/output;
* ghi lại số lượng record trước/sau;
* ghi lại rule lọc;
* sử dụng random seed khi phù hợp;
* tránh thao tác thủ công không tái lập được.

---

# 17. Cách làm việc với tôi

Khi tôi giao một task:

1. Trước tiên xác định task thuộc giai đoạn nào của pipeline.
2. Kiểm tra các file/dataset hiện có trước khi tạo giả định.
3. Giải thích ngắn gọn mục đích của bước đó.
4. Thực hiện task.
5. Báo cáo:

   * đã làm gì;
   * input;
   * output;
   * số lượng dữ liệu trước/sau;
   * phát hiện quan trọng;
   * vấn đề hoặc rủi ro.
6. Nếu tạo file mới, đặt tên rõ ràng và không ghi đè dữ liệu gốc.
7. Không chuyển sang giai đoạn tiếp theo nếu bước hiện tại còn vấn đề quan trọng chưa được giải quyết.

Khi viết code, ưu tiên code rõ ràng, có thể chạy lại và phù hợp với dữ liệu lớn của MIMIC-IV.

---

# 18. Điều quan trọng nhất cần ghi nhớ

Research question cốt lõi là:

**Liệu các đặc trưng từ dữ liệu xét nghiệm cận lâm sàng ở giai đoạn sớm của một lần nhập viện trong MIMIC-IV có thể được sử dụng bởi mô hình Machine Learning để dự đoán đồng thời các phenotype/nhóm bệnh được ghi nhận cho admission đó hay không?**

Pipeline cốt lõi:

**Clinical Laboratory Data → Multi-label Disease Prediction → Diagnostic Support**

Không phải:

**One lab → One disease**

và cũng không phải:

**Laboratory abnormality → Disease causation**

Mọi quyết định trong quá trình xử lý dữ liệu và xây dựng mô hình cần phục vụ research question này.
