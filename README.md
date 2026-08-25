# MIMIC-IV-ECG Research Workspace

README này được viết để một agent AI mới có thể nhanh chóng hiểu dự án, cấu trúc repo và hướng nghiên cứu hiện tại.

## Mục tiêu dự án

Dự án đang xây dựng nền tảng nghiên cứu trên bộ dữ liệu **MIMIC-IV-ECG**. Trọng tâm hiện tại là:

- Phân tích metadata ECG.
- Tải và đọc một bản ghi ECG mẫu ở định dạng WFDB.
- Xuất tín hiệu ECG sang CSV.
- Vẽ tín hiệu ECG 12 đạo trình và một đạo trình cụ thể.
- Chuẩn bị hướng nghiên cứu sâu hơn: **ECG-text contrastive learning** kết hợp **physiology-guided confidence calibration**.

Ý tưởng nghiên cứu chính trong tài liệu hiện có là **Physio-Calibrated ECG-CLIP**: học biểu diễn giữa raw ECG 12 đạo trình và báo cáo text, sau đó dùng các thông số sinh lý ECG để hiệu chỉnh độ tin cậy của dự đoán.

## Cấu trúc thư mục

```text
.
├── data/
│   ├── metadata/
│   │   ├── record_list.csv
│   │   ├── machine_measurements.csv
│   │   ├── machine_measurements_data_dictionary.csv
│   │   └── waveform_note_links.csv
│   ├── raw/
│   │   └── sample_ecg/
│   │       ├── 40689238.hea
│   │       └── 40689238.dat
│   └── processed/
│       └── 40689238_signal.csv
├── docs/
│   ├── bao_cao_metadata_mimic_iv_ecg.md
│   ├── de_xuat_nghien_cuu_mimic_iv_ecg.md
│   ├── Bao_cao_gioi_thieu_de_tai_MIMIC_IV_ECG_bo_sung_dataset.docx
│   ├── Bao_cao_tom_tat_ECG_CLIP_2025.docx
│   └── note.txt
├── outputs/
│   └── figures/
│       ├── 40689238_all_leads.png
│       └── 40689238_lead_II.png
├── src/
│   ├── download_sample.py
│   └── read_and_plot_ecg.py
├── demo.ipynb
├── requirements.txt
└── README.md
```

## Môi trường Python

Dự án dùng Python với các thư viện trong `requirements.txt`:

```text
matplotlib
numpy
pandas
wfdb
```

Cài đặt nhanh:

```bash
pip install -r requirements.txt
```

## Script chính

### `src/download_sample.py`

Script này đọc dòng đầu tiên từ:

```text
data/metadata/record_list.csv
```

Sau đó tạo URL tải cặp file WFDB `.hea` và `.dat` từ PhysioNet:

```text
https://physionet.org/files/mimic-iv-ecg/1.0/
```

Output được lưu vào:

```text
data/raw/sample_ecg/
```

Chạy:

```bash
python src/download_sample.py
```

Lưu ý: việc tải dữ liệu từ PhysioNet có thể cần quyền truy cập hợp lệ tùy trạng thái dataset và tài khoản.

### `src/read_and_plot_ecg.py`

Script này đang xử lý cố định record mẫu:

```text
40689238
```

Input:

```text
data/raw/sample_ecg/40689238.hea
data/raw/sample_ecg/40689238.dat
```

Các bước xử lý:

1. Đọc ECG bằng `wfdb.rdrecord`.
2. In thông tin bản ghi: sampling rate, số đạo trình, số mẫu, thời lượng, tên đạo trình.
3. Xuất tín hiệu vật lý sang CSV.
4. Vẽ toàn bộ 12 đạo trình.
5. Vẽ riêng đạo trình `II` trong 10 giây đầu.

Output:

```text
data/processed/40689238_signal.csv
outputs/figures/40689238_all_leads.png
outputs/figures/40689238_lead_II.png
```

Chạy:

```bash
python src/read_and_plot_ecg.py
```

Nếu muốn hiện biểu đồ trực tiếp:

```bash
SHOW_PLOTS=1 python src/read_and_plot_ecg.py
```

Trên PowerShell:

```powershell
$env:SHOW_PLOTS = "1"
python src/read_and_plot_ecg.py
```

## Dữ liệu hiện có

### Metadata

Các file metadata trong `data/metadata/` là nền tảng để xây dựng cohort, tạo nhãn và quyết định tải waveform nào.

| File | Vai trò |
|---|---|
| `record_list.csv` | Bảng chỉ mục trung tâm của toàn bộ ECG, gồm `subject_id`, `study_id`, `ecg_time`, `path`. |
| `machine_measurements.csv` | Báo cáo do máy ECG sinh ra và các thông số đo tự động. |
| `machine_measurements_data_dictionary.csv` | Từ điển mô tả các biến trong `machine_measurements.csv`. |
| `waveform_note_links.csv` | Liên kết ECG waveform với note/báo cáo lâm sàng nếu có. |

Theo tài liệu phân tích trong `docs/`, `record_list.csv` nên được xem là bảng trung tâm khi join dữ liệu.

### Waveform mẫu

Record mẫu hiện tại:

```text
record_name: 40689238
sampling rate: 500 Hz
length: 5000 samples
duration: 10 seconds
leads: 12
```

Các đạo trình trong file mẫu:

```text
I, II, III, aVR, aVF, aVL, V1, V2, V3, V4, V5, V6
```

## Ý nghĩa các trường metadata quan trọng

Các khóa chính:

- `subject_id`: định danh bệnh nhân, dùng để nối với dữ liệu MIMIC-IV khác.
- `study_id`: định danh một lần đo ECG, dùng để nối waveform, machine report và note.

Các trường text report:

- `report_0` đến `report_17`: báo cáo/chẩn đoán dạng text do máy ECG sinh ra.
- Một ECG có thể có nhiều report cùng lúc, nên bài toán phù hợp thường là multi-label classification.

Các trường machine measurement:

- `rr_interval`: khoảng R-R, đơn vị ms.
- `p_onset`, `p_end`: thời điểm bắt đầu/kết thúc sóng P.
- `qrs_onset`, `qrs_end`: thời điểm bắt đầu/kết thúc phức bộ QRS.
- `t_end`: thời điểm kết thúc sóng T.
- `p_axis`, `qrs_axis`, `t_axis`: trục điện học, đơn vị độ.

Các đặc trưng dẫn xuất có thể tạo:

```text
heart_rate = 60000 / rr_interval
pr_interval = qrs_onset - p_onset
qrs_duration = qrs_end - qrs_onset
qt_interval = t_end - qrs_onset
```

## Hướng nghiên cứu đang được đề xuất

Hướng chính trong `docs/de_xuat_nghien_cuu_mimic_iv_ecg.md`:

```text
ECG-text contrastive learning
+ physiology-guided confidence calibration
+ noise-aware report usage
```

Pipeline nghiên cứu dự kiến:

1. Tạo master metadata table từ các file metadata.
2. Làm sạch numeric features và report text.
3. Tạo nhãn từ `report_0..report_17`.
4. Chia train/validation/test theo `subject_id`.
5. Tải waveform theo cohort đã chọn.
6. Huấn luyện baseline supervised trên waveform.
7. Huấn luyện ECG-CLIP style baseline.
8. Thêm module kiểm tra nhất quán sinh lý.
9. Hiệu chỉnh confidence hoặc weighted contrastive loss.
10. Đánh giá supervised, zero-shot, few-shot và retrieval.

Các nhãn nên ưu tiên giai đoạn đầu:

- Normal ECG
- Abnormal ECG
- Atrial fibrillation
- Sinus tachycardia
- Sinus bradycardia
- Prolonged QT interval
- Left axis deviation
- Right axis deviation
- Right bundle branch block
- Left bundle branch block
- First-degree AV block

## Lưu ý quan trọng cho agent AI

- Không chia train/test ngẫu nhiên theo ECG nếu nghiên cứu mô hình; hãy chia theo `subject_id` để tránh data leakage giữa các ECG của cùng bệnh nhân.
- Dùng `record_list.csv` làm bảng trung tâm khi join metadata.
- Khi có khác biệt timestamp giữa các bảng, ưu tiên `record_list.ecg_time` làm thời gian ECG chuẩn.
- Các report trong `machine_measurements.csv` là machine-generated report, không phải nhãn vàng tuyệt đối.
- Một ECG có thể có nhiều nhãn, tránh ép thành single-label nếu không có lý do rõ ràng.
- Cần xử lý các giá trị sentinel hoặc bất thường trong numeric features, ví dụ:

```text
29999
32767
-32768
65535
65534
61440
```

- `waveform_note_links.csv` không bao phủ toàn bộ ECG; tài liệu hiện có ghi nhận khoảng 76,15% ECG có note link.
- Dữ liệu metadata lớn, không nên đọc toàn bộ CSV vào bộ nhớ nếu chỉ cần kiểm tra schema hoặc lấy mẫu nhỏ.
- Các file dữ liệu lớn nên được giữ ngoài Git nếu chưa có chính sách versioning dữ liệu rõ ràng.

## Tài liệu nội bộ

- `docs/bao_cao_metadata_mimic_iv_ecg.md`: phân tích chi tiết các file metadata, khóa nối, chất lượng dữ liệu và đề xuất tiền xử lý.
- `docs/de_xuat_nghien_cuu_mimic_iv_ecg.md`: đề xuất hướng nghiên cứu Physio-Calibrated ECG-CLIP.
- `demo.ipynb`: notebook demo hiện có, nên kiểm tra trước khi mở rộng workflow tương tác.

## Gợi ý việc tiếp theo

Các task hợp lý để giao tiếp cho agent AI sau README này:

1. Viết script tạo master metadata table từ `record_list.csv`, `machine_measurements.csv` và `waveform_note_links.csv`.
2. Viết module làm sạch sentinel values và tạo các feature `heart_rate`, `pr_interval`, `qrs_duration`, `qt_interval`.
3. Viết module gộp `report_0..report_17` thành `report_text` và sinh nhãn multi-label bằng keyword matching.
4. Viết script chia train/validation/test theo `subject_id`.
5. Mở rộng `download_sample.py` để tải waveform theo danh sách `study_id` thay vì chỉ dòng đầu tiên.
6. Tạo notebook EDA cho phân bố nhãn và chất lượng metadata.

