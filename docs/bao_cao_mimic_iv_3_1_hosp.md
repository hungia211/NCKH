# Khảo sát MIMIC-IV v3.1 - hosp module

- Đường dẫn local: `G:\My Drive\UIT\NCKH\DTS\mimic-iv-3.1\mimic-iv-3.1\hosp`
- Ngày tạo báo cáo: 2026-08-25
- Phạm vi: tập trung hosp; các bảng trọng tâm được thống kê chi tiết, các bảng còn lại được mô tả tổng quan theo header/size/row count local.
- Nguyên tắc: không chỉnh sửa raw data; không tạo giá trị/quan hệ giả; các nhận xét được tách khỏi documentation và quan sát local.

## 1. Theo documentation
- Bộ dữ liệu dùng đúng release MIMIC-IV v3.1 trên PhysioNet; documentation chính thức là PhysioNet MIMIC-IV v3.1 và MIMIC-IV docs mục hosp.
- Documentation định nghĩa subject_id là mã định danh bệnh nhân ẩn danh, hadm_id là mã định danh lần nhập viện hospital admission, itemid là mã khái niệm cho các sự kiện như xét nghiệm.
- Documentation mô tả patients là cấp bệnh nhân; admissions là cấp lần nhập viện; transfers là location/careunit intervals; labevents là xét nghiệm và nối d_labitems qua itemid; diagnoses/procedures dùng ICD dictionaries; prescriptions/pharmacy/poe liên quan thuốc và orders.
- Thời gian trong MIMIC-IV đã được dịch để bảo vệ riêng tư; cần dùng quan hệ tương đối trong cùng bệnh nhân thay vì diễn giải năm lịch thật.

## 2. Quan sát trực tiếp từ dataset local
- Số bảng/file `.csv.gz` trong hosp: 22.
- patients có 364,627 subject_id duy nhất.
- admissions có 546,028 hadm_id duy nhất thuộc 223,452 bệnh nhân có nhập viện.
- Bệnh nhân có nhiều admission: 100,163; nhiều nhất 238 admissions trên một subject_id.

### 2.1. Toàn bộ bảng trong hosp
| Bảng | Số dòng local | Kích thước nén | Số cột | Nội dung |
| --- | --- | --- | --- | --- |
| admissions | 546,028 | 19.0 MB | 16 | Thông tin một lần nhập viện bệnh viện; một dòng tương ứng một hadm_id, gồm thời điểm vào/ra viện, loại nhập viện, nguồn vào/đích ra viện, bảo hiểm, ngôn ngữ, tình trạng tử vong nội viện. |
| d_hcpcs | 89,208 | 0.4 MB | 4 | Dictionary mã HCPCS dùng để diễn giải hcpcsevents.hcpcs_cd/code. |
| d_icd_diagnoses | 112,107 | 0.8 MB | 3 | Dictionary mã chẩn đoán ICD, nối với diagnoses_icd bằng icd_code + icd_version. |
| d_icd_procedures | 86,423 | 0.6 MB | 3 | Dictionary mã thủ thuật ICD, nối với procedures_icd bằng icd_code + icd_version. |
| d_labitems | 1,650 | 0.0 MB | 4 | Dictionary xét nghiệm; itemid là khóa khái niệm xét nghiệm, nối với labevents.itemid. |
| diagnoses_icd | 6,364,488 | 32.0 MB | 5 | Chẩn đoán ICD đã mã hóa/billing theo từng lần nhập viện; có seq_num để biểu diễn thứ tự chẩn đoán. |
| drgcodes | 761,856 | 9.3 MB | 7 | Mã DRG billing theo lần nhập viện. |
| emar | 42,808,593 | 773.7 MB | 12 | Electronic Medication Administration Record: bản ghi quản trị/ghi nhận dùng thuốc. |
| emar_detail | 87,371,064 | 713.5 MB | 33 | Chi tiết bổ sung theo từng emar_id/emar_seq, gồm thông tin sản phẩm, barcode, liều dùng. |
| hcpcsevents | 186,074 | 2.1 MB | 6 | Sự kiện/billing HCPCS theo bệnh nhân/lần nhập viện/ngày. |
| labevents | 158,374,764 | 2472.8 MB | 16 | Kết quả xét nghiệm; mỗi dòng là một sự kiện xét nghiệm, dùng itemid để nối d_labitems. |
| microbiologyevents | 3,988,224 | 112.2 MB | 25 | Sự kiện vi sinh: specimen, test, organism, antibiotic và interpretation nếu có. |
| omr | 7,753,027 | 42.0 MB | 5 | Online Medical Record: kết quả dạng ngày như BMI, blood pressure, weight, eGFR. |
| patients | 364,627 | 2.7 MB | 6 | Thông tin cấp bệnh nhân: subject_id, giới, tuổi/năm anchor đã dịch thời gian, ngày tử vong nếu có. |
| pharmacy | 17,847,567 | 501.4 MB | 27 | Thông tin pharmacy cho thuốc/order: pharmacy_id, poe_id, thời gian bắt đầu/kết thúc, medication, route, frequency, status. |
| poe | 52,212,109 | 635.7 MB | 12 | Provider Order Entry: lệnh do provider nhập, bao gồm ordertime, order_type/subtype và liên kết poe_id. |
| poe_detail | 8,504,982 | 52.7 MB | 5 | Chi tiết bổ sung của POE theo poe_id/poe_seq với field_name/field_value. |
| prescriptions | 20,292,611 | 578.2 MB | 21 | Thuốc được kê trong hospital module; nối được admission, pharmacy, poe, provider và có starttime/stoptime. |
| procedures_icd | 859,655 | 7.4 MB | 6 | Thủ thuật ICD theo lần nhập viện, có chartdate và seq_num. |
| provider | 42,244 | 0.1 MB | 1 | Dictionary provider_id đã ẩn danh. |
| services | 593,071 | 8.2 MB | 5 | Lịch sử dịch vụ/chuyên khoa phụ trách theo transfertime. |
| transfers | 2,413,581 | 44.0 MB | 7 | Sự kiện di chuyển vị trí/careunit; mô tả khoảng intime-outtime, eventtype, transfer_id. |

### 2.2. Cấu trúc bảng trọng tâm
#### patients
- Số dòng: 364,627; số cột: 6; file nén: 2.7 MB.
- Column local: `subject_id, gender, anchor_age, anchor_year, anchor_year_group, dod`.
- Ý nghĩa theo documentation: Thông tin cấp bệnh nhân: subject_id, giới, tuổi/năm anchor đã dịch thời gian, ngày tử vong nếu có.
- Distinct key quan sát: `{'subject_id': 364627}`.
- Timestamp/date range local: dod: 2104-12-24 -> 2215-02-16.
- Missing selected: subject_id: 0 (0.000%); gender: 0 (0.000%); anchor_age: 0 (0.000%); anchor_year: 0 (0.000%); anchor_year_group: 0 (0.000%); dod: 326,326 (89.496%).
- Kiểm tra link local: orphan subject rows = 0; orphan hadm rows = 0.

#### admissions
- Số dòng: 546,028; số cột: 16; file nén: 19.0 MB.
- Column local: `subject_id, hadm_id, admittime, dischtime, deathtime, admission_type, admit_provider_id, admission_location, discharge_location, insurance, language, marital_status, race, edregtime, edouttime, hospital_expire_flag`.
- Ý nghĩa theo documentation: Thông tin một lần nhập viện bệnh viện; một dòng tương ứng một hadm_id, gồm thời điểm vào/ra viện, loại nhập viện, nguồn vào/đích ra viện, bảo hiểm, ngôn ngữ, tình trạng tử vong nội viện.
- Distinct key quan sát: `{'hadm_id': 546028, 'subject_id': 223452}`.
- Timestamp/date range local: admittime: 2105-10-04 17:26:00 -> 2214-12-15 19:11:00; deathtime: 2110-01-25 09:40:00 -> 2214-10-12 12:51:00; dischtime: 2105-10-12 11:11:00 -> 2214-12-24 13:44:00; edouttime: 2106-02-07 09:31:00 -> 2214-12-15 22:50:00; edregtime: 2106-02-06 15:47:00 -> 2214-12-15 00:45:00.
- Missing selected: subject_id: 0 (0.000%); hadm_id: 0 (0.000%); admittime: 0 (0.000%); dischtime: 0 (0.000%); deathtime: 534,238 (97.841%); admission_type: 0 (0.000%); admit_provider_id: 4 (0.001%); admission_location: 1 (0.000%); discharge_location: 149,818 (27.438%); insurance: 9,355 (1.713%).
- Kiểm tra link local: orphan subject rows = 0; orphan hadm rows = 0.

#### transfers
- Số dòng: 2,413,581; số cột: 7; file nén: 44.0 MB.
- Column local: `subject_id, hadm_id, transfer_id, eventtype, careunit, intime, outtime`.
- Ý nghĩa theo documentation: Sự kiện di chuyển vị trí/careunit; mô tả khoảng intime-outtime, eventtype, transfer_id.
- Distinct key quan sát: `{'hadm_id': 546024, 'subject_id': 364627}`.
- Timestamp/date range local: intime: 2105-10-04 17:27:12 -> 2214-12-24 13:59:52; outtime: 2105-10-06 15:00:50 -> 2214-12-24 13:59:52.
- Missing selected: subject_id: 0 (0.000%); hadm_id: 408,977 (16.945%); transfer_id: 0 (0.000%); eventtype: 0 (0.000%); careunit: 0 (0.000%); intime: 0 (0.000%); outtime: 546,123 (22.627%).
- Kiểm tra link local: orphan subject rows = 0; orphan hadm rows = 0.

#### labevents
- Số dòng: 158,374,764; số cột: 16; file nén: 2472.8 MB.
- Column local: `labevent_id, subject_id, hadm_id, specimen_id, itemid, order_provider_id, charttime, storetime, value, valuenum, valueuom, ref_range_lower, ref_range_upper, flag, priority, comments`.
- Ý nghĩa theo documentation: Kết quả xét nghiệm; mỗi dòng là một sự kiện xét nghiệm, dùng itemid để nối d_labitems.
- Distinct key quan sát: `{'hadm_id': 447689, 'itemid': 976, 'subject_id': 313442}`.
- Timestamp/date range local: charttime: 2105-01-19 12:01:00 -> 2215-01-12 11:45:00; storetime: 2105-01-19 12:26:00 -> 2215-01-12 15:59:00.
- Missing selected: subject_id: 0 (0.000%); hadm_id: 73,768,897 (46.579%); labevent_id: 0 (0.000%); specimen_id: 0 (0.000%); itemid: 0 (0.000%); order_provider_id: 113,933,995 (71.939%); charttime: 0 (0.000%); storetime: 2,568,511 (1.622%); value: 16,062,783 (10.142%); valuenum: 21,490,341 (13.569%).
- Kiểm tra link local: orphan subject rows = 0; orphan hadm rows = 0.

#### d_labitems
- Số dòng: 1,650; số cột: 4; file nén: 0.0 MB.
- Column local: `itemid, label, fluid, category`.
- Ý nghĩa theo documentation: Dictionary xét nghiệm; itemid là khóa khái niệm xét nghiệm, nối với labevents.itemid.
- Distinct key quan sát: `{'itemid': 1650}`.
- Missing selected: itemid: 0 (0.000%); label: 4 (0.242%); fluid: 0 (0.000%); category: 0 (0.000%).
- Kiểm tra link local: orphan subject rows = 0; orphan hadm rows = 0.

#### diagnoses_icd
- Số dòng: 6,364,488; số cột: 5; file nén: 32.0 MB.
- Column local: `subject_id, hadm_id, seq_num, icd_code, icd_version`.
- Ý nghĩa theo documentation: Chẩn đoán ICD đã mã hóa/billing theo từng lần nhập viện; có seq_num để biểu diễn thứ tự chẩn đoán.
- Distinct key quan sát: `{'hadm_id': 545497, 'icd_code': 28562, 'icd_version': 2, 'subject_id': 223291}`.
- Missing selected: subject_id: 0 (0.000%); hadm_id: 0 (0.000%); seq_num: 0 (0.000%); icd_code: 0 (0.000%); icd_version: 0 (0.000%).
- Kiểm tra link local: orphan subject rows = 0; orphan hadm rows = 0.

#### d_icd_diagnoses
- Số dòng: 112,107; số cột: 3; file nén: 0.8 MB.
- Column local: `icd_code, icd_version, long_title`.
- Ý nghĩa theo documentation: Dictionary mã chẩn đoán ICD, nối với diagnoses_icd bằng icd_code + icd_version.
- Distinct key quan sát: `{'icd_code': 111594, 'icd_version': 2}`.
- Missing selected: icd_code: 0 (0.000%); icd_version: 0 (0.000%); long_title: 0 (0.000%).
- Kiểm tra link local: orphan subject rows = 0; orphan hadm rows = 0.

#### procedures_icd
- Số dòng: 859,655; số cột: 6; file nén: 7.4 MB.
- Column local: `subject_id, hadm_id, seq_num, chartdate, icd_code, icd_version`.
- Ý nghĩa theo documentation: Thủ thuật ICD theo lần nhập viện, có chartdate và seq_num.
- Distinct key quan sát: `{'hadm_id': 287504, 'icd_code': 14911, 'icd_version': 2, 'subject_id': 150711}`.
- Timestamp/date range local: chartdate: 2105-10-05 -> 2214-10-01.
- Missing selected: subject_id: 0 (0.000%); hadm_id: 0 (0.000%); seq_num: 0 (0.000%); chartdate: 0 (0.000%); icd_code: 0 (0.000%); icd_version: 0 (0.000%).
- Kiểm tra link local: orphan subject rows = 0; orphan hadm rows = 0.

#### d_icd_procedures
- Số dòng: 86,423; số cột: 3; file nén: 0.6 MB.
- Column local: `icd_code, icd_version, long_title`.
- Ý nghĩa theo documentation: Dictionary mã thủ thuật ICD, nối với procedures_icd bằng icd_code + icd_version.
- Distinct key quan sát: `{'icd_code': 86417, 'icd_version': 2}`.
- Missing selected: icd_code: 0 (0.000%); icd_version: 0 (0.000%); long_title: 0 (0.000%).
- Kiểm tra link local: orphan subject rows = 0; orphan hadm rows = 0.

#### prescriptions
- Số dòng: 20,292,611; số cột: 21; file nén: 578.2 MB.
- Column local: `subject_id, hadm_id, pharmacy_id, poe_id, poe_seq, order_provider_id, starttime, stoptime, drug_type, drug, formulary_drug_cd, gsn, ndc, prod_strength, form_rx, dose_val_rx, dose_unit_rx, form_val_disp, form_unit_disp, doses_per_24_hrs, route`.
- Ý nghĩa theo documentation: Thuốc được kê trong hospital module; nối được admission, pharmacy, poe, provider và có starttime/stoptime.
- Distinct key quan sát: `{'hadm_id': 463328, 'subject_id': 196738}`.
- Timestamp/date range local: starttime: 2105-10-04 18:00:00 -> 2214-12-24 12:00:00; stoptime: 2105-10-05 07:00:00 -> 2214-12-24 18:00:00.
- Missing selected: subject_id: 0 (0.000%); hadm_id: 0 (0.000%); pharmacy_id: 0 (0.000%); poe_id: 184,441 (0.909%); poe_seq: 184,441 (0.909%); order_provider_id: 66,367 (0.327%); starttime: 21,890 (0.108%); stoptime: 31,436 (0.155%); drug_type: 0 (0.000%); drug: 1 (0.000%).
- Kiểm tra link local: orphan subject rows = 0; orphan hadm rows = 0.

#### pharmacy
- Số dòng: 17,847,567; số cột: 27; file nén: 501.4 MB.
- Column local: `subject_id, hadm_id, pharmacy_id, poe_id, starttime, stoptime, medication, proc_type, status, entertime, verifiedtime, route, frequency, disp_sched, infusion_type, sliding_scale, lockout_interval, basal_rate, one_hr_max, doses_per_24_hrs, duration, duration_interval, expiration_value, expiration_unit, expirationdate, dispensation, fill_quantity`.
- Ý nghĩa theo documentation: Thông tin pharmacy cho thuốc/order: pharmacy_id, poe_id, thời gian bắt đầu/kết thúc, medication, route, frequency, status.
- Distinct key quan sát: `{'hadm_id': 463328, 'subject_id': 196738}`.
- Timestamp/date range local: entertime: 2105-10-04 17:47:05 -> 2214-12-24 11:26:21; expirationdate: 2111-03-24 00:00:00 -> 2341-10-18 00:00:00; starttime: 1931-04-24 17:00:00 -> 5117-07-25 08:00:00; stoptime: 2078-05-30 23:00:00 -> 2214-12-24 18:00:00; verifiedtime: 2105-10-04 17:47:05 -> 2214-12-24 11:26:21.
- Missing selected: subject_id: 0 (0.000%); hadm_id: 0 (0.000%); pharmacy_id: 0 (0.000%); poe_id: 145,597 (0.816%); starttime: 21,894 (0.123%); stoptime: 92,169 (0.516%); medication: 1,137,574 (6.374%); proc_type: 0 (0.000%); status: 0 (0.000%); entertime: 0 (0.000%).
- Kiểm tra link local: orphan subject rows = 0; orphan hadm rows = 0.

## 3. Khóa và quan hệ
- `subject_id`: khóa bệnh nhân. Xuất hiện trong hầu hết bảng sự kiện; nối về `patients.subject_id`.
- `hadm_id`: khóa một lần nhập viện. `admissions.hadm_id` là duy nhất; dùng nối admission với diagnoses/procedures/lab/medication/transfers khi trường này không thiếu.
- `itemid`: khóa khái niệm item, đặc biệt `labevents.itemid` nối `d_labitems.itemid`.
- `icd_code + icd_version`: khóa dictionary ICD; dùng nối `diagnoses_icd` với `d_icd_diagnoses` và `procedures_icd` với `d_icd_procedures`.
- `pharmacy_id` và `poe_id`: liên kết medication/order giữa `prescriptions`, `pharmacy`, `emar`, `poe`; cần kiểm tra thêm ở bước phân tích thuốc sâu vì không phải mọi dòng prescription có poe_id.
- `transfer_id`: định danh sự kiện transfer trong `transfers`.

## 4. Một bệnh nhân được biểu diễn như thế nào
- Mô hình chính: Patient (`patients.subject_id`) -> nhiều Admissions (`admissions.hadm_id`) -> nhiều sự kiện theo admission như lab, diagnosis, procedure, medication, transfer.
- Quan sát local: 223,452 / 364,627 bệnh nhân có ít nhất một admission trong `admissions`.
- Phân phối admissions/subject_id thường gặp: {'1': 123289, '2': 44123, '3': 20108, '4': 11172, '5': 6629, '6': 4312, '7': 2964, '8': 2187, '9': 1651, '10': 1266, '11': 977, '12': 762, '13': 620, '14': 518, '15': 413, '16': 297, '17': 281, '18': 246, '19': 175, '20': 155, '21': 145, '22': 122, '23': 102, '24': 81, '26': 73, '27': 64, '25': 62, '28': 62, '30': 48, '29': 44, '32': 42, '33': 36, '35': 32, '31': 30, '40': 25, '34': 25, '36': 23, '37': 22, '39': 19, '38': 17, '41': 17, '47': 15, '43': 13, '44': 13, '46': 13, '45': 12, '49': 10, '52': 9, '48': 8, '42': 8}.
- Lưu ý: `labevents.hadm_id` thiếu 46.579%, nên không phải mọi xét nghiệm nối được cấp admission; vẫn nối được cấp bệnh nhân qua `subject_id`. `transfers.hadm_id` thiếu 16.945%, phù hợp với các event không gắn admission như ED-only/ngoài admission.

## 5. Timestamp quan trọng
- `admittime`, `dischtime`: thời điểm vào/ra viện trong `admissions`.
- `deathtime`: thời điểm tử vong nội viện nếu có; local thiếu 97.841%, vì chỉ có ở một phần admission.
- `edregtime`, `edouttime`: thời điểm đăng ký/rời ED nếu admission đi qua ED; local thiếu 30.546%.
- `intime`, `outtime`: khoảng thời gian bệnh nhân ở location/careunit trong `transfers`.
- `charttime`: thời điểm sự kiện được ghi nhận/đo/thu thập; trong `labevents` không thiếu trên dữ liệu local.
- `storetime`: thời điểm dữ liệu được lưu vào hệ thống; trong `labevents` thiếu 1.622%.
- `starttime`, `stoptime`: khoảng hiệu lực của thuốc/order trong `prescriptions`/`pharmacy`.
- `chartdate`: ngày của procedure/HCPCS/microbiology/OMR khi chỉ có độ phân giải ngày.

## 6. Bảng quan trọng cho liên kết Clinical với ECG sau này
- `patients`: bắt buộc để nối cấp bệnh nhân bằng subject_id.
- `admissions`: cần để xác định admission windows bằng admittime/dischtime và hadm_id.
- `transfers`: hữu ích để xác định location/careunit gần thời điểm ECG.
- `labevents` + `d_labitems`: rất quan trọng cho biomarkers gần ECG theo charttime; cần xử lý hadm_id missing.
- `diagnoses_icd` + `d_icd_diagnoses`: phenotype/bệnh nền ở cấp admission.
- `procedures_icd` + `d_icd_procedures`: thủ thuật/can thiệp ở cấp admission/ngày.
- `prescriptions` + `pharmacy`: thuốc quanh thời điểm ECG qua starttime/stoptime; cần chuẩn hóa route/drug/gsn/ndc.
- `microbiologyevents`, `omr`, `services`: phụ trợ tùy câu hỏi nghiên cứu; có thể thêm sau khi đã xác định cohort ECG.

## 7. Nhận xét của agent
- Dữ liệu local khớp cấu trúc documentation ở các bảng trọng tâm: tên bảng/cột và các khóa chính xuất hiện đúng kỳ vọng.
- Không nên giả định `hadm_id` luôn có trong bảng sự kiện: `labevents` thiếu nhiều `hadm_id`, vì vậy liên kết theo admission cần lọc/ánh xạ cẩn thận.
- Các timestamp là thời gian đã dịch, phù hợp để tính khoảng cách tương đối trong cùng bệnh nhân nhưng không diễn giải như thời gian lịch thật.
- Với Clinical-ECG, trục nối an toàn nhất ban đầu là `subject_id` + cửa sổ thời gian; dùng `hadm_id` khi có và nằm trong khoảng `admittime`-`dischtime`.

## 8. Nguồn
- PhysioNet MIMIC-IV v3.1: https://physionet.org/content/mimiciv/3.1/
- MIMIC-IV hosp documentation: https://mimic.mit.edu/docs/iv/modules/hosp/
- MIMIC-IV patients/admissions/transfers/labevents/prescriptions pages under hosp documentation.
- Kết quả quét local: mimic_hosp_survey_stats.json trong thư mục báo cáo.
