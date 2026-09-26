# Giai đoạn 1 — Báo cáo khảo sát dữ liệu HOSP

**Ngày chạy:** 2026-09-22  
**Input:** `D:\UIT_thu\NCKH\data\hosp`  
**Nguyên tắc:** đọc-only; chưa lọc cohort, chưa chọn early window, chưa đặt threshold.

## 1. Inventory toàn bộ module

Module HOSP có **22 file `.csv.gz`**. Kết quả inventory đầy đủ gồm schema, số cột, số dòng và kích thước nén tại [`outputs/machine_readable/hosp_inventory.json`](outputs/machine_readable/hosp_inventory.json). Các bảng lớn nhất:

| Bảng | Số dòng | Số cột |
|---|---:|---:|
| `labevents` | 158,374,764 | 16 |
| `emar_detail` | 87,371,064 | 33 |
| `poe` | 52,212,109 | 12 |
| `emar` | 42,808,593 | 12 |
| `prescriptions` | 20,292,611 | 21 |
| `pharmacy` | 17,847,567 | 27 |
| `diagnoses_icd` | 6,364,488 | 5 |
| `admissions` | 546,028 | 16 |
| `patients` | 364,627 | 6 |
| `d_labitems` | 1,650 | 4 |

Đối với research question hiện tại, nhóm bảng cốt lõi là `admissions`, `patients`, `labevents`, `d_labitems`, `diagnoses_icd` và `d_icd_diagnoses`. Các bảng medication/order/procedure chưa được dùng làm input chính.

## 2. Admissions

- 546,028 dòng và 546,028 `hadm_id` duy nhất.
- 223,452 `subject_id` có admission; 100% dòng có `subject_id`, `hadm_id`, `admittime`, `dischtime`.
- Median thời lượng theo chênh lệch `dischtime - admittime`: **2.82 ngày**; maximum **515.56 ngày**.
- Có giá trị thời lượng âm (minimum **-0.945 ngày**), cần kiểm tra như một vấn đề chất lượng dữ liệu trước khi định nghĩa cohort. Chưa loại các dòng này.
- `deathtime` thiếu 97.84%; `edregtime` và `edouttime` mỗi trường thiếu 166,788 dòng.

## 3. Lab events

- 158,374,764 dòng, 313,442 bệnh nhân, 447,689 admission có `hadm_id` không null.
- 1,650 `itemid` trong file events; 1,650 dòng dictionary trong `d_labitems`.
- `hadm_id` thiếu 73,768,897 dòng (**46.579%**). Chỉ các event có `hadm_id` mới có thể nối trực tiếp với admission.
- `valuenum` thiếu 21,490,341 dòng (**13.569%**).
- `valueuom` thiếu 26,555,866 dòng (**16.768%**).
- `charttime` quan sát từ `2105-01-19 12:01:00` đến `2215-01-12 11:45:00`. Đây là thời gian đã dịch của MIMIC và chỉ nên dùng cho quan hệ tương đối.
- Có 10 `itemid` xuất hiện với nhiều đơn vị; cần khảo sát riêng trước khi aggregation.
- Các `itemid` có nhiều dòng nhất gồm: 51221 Hematocrit, 50912 Creatinine, 51265 Platelet Count, 51006 Urea Nitrogen, 51222 Hemoglobin và 51301 White Blood Cells. Đây chỉ là thống kê frequency, chưa phải quyết định chọn feature.

## 4. Diagnoses ICD

- 6,364,488 dòng, 223,291 bệnh nhân và 545,497 admission.
- 28,583 cặp `icd_version + icd_code` duy nhất.
- ICD-9 có 9,143 code; ICD-10 có 19,440 code.
- Số diagnosis mỗi admission: minimum 1, maximum 57, mean 11.67.
- Các code phổ biến gồm ICD-9 `4019`, ICD-10 `E785`, ICD-10 `I10`, ICD-9 `2724`, ICD-10 `Z87891`. Frequency này chưa phải label set.
- `d_icd_diagnoses` chỉ là dictionary diễn giải code. Việc tạo nhãn sau này phải bắt đầu từ `diagnoses_icd`, rồi map ICD → Phecode và kiểm tra coverage.

## 5. Kết quả và rủi ro hiện tại

1. Cần phân biệt admission có lab (`447,689`) với toàn bộ admission (`546,028`) ở bước cohort sau.
2. Cần xử lý các event lab thiếu `hadm_id`; không được tự động gán vào admission.
3. Cần kiểm tra 10 item có nhiều đơn vị trước khi tính feature.
4. Có admission có thời lượng âm; cần truy nguyên và thống nhất quy tắc xử lý ở Giai đoạn 2.
5. `diagnoses_icd` bao phủ ít hơn toàn bộ admissions một lượng nhỏ; cần đo overlap chính xác với admission có lab.
6. Chưa có căn cứ để chọn 6/12/24 giờ, top lab, aggregation hoặc ngưỡng label.

## 6. Cách tái lập

```powershell
python phases\phase1_data_exploration\scripts\explore_hosp.py
python phases\phase1_data_exploration\scripts\explore_hosp_core.py
```

Hai script chỉ đọc file `.csv.gz` và ghi kết quả vào `phases/phase1_data_exploration/outputs/machine_readable/`. Không ghi vào `data/hosp`.
