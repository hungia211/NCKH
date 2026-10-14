# Từ điển dữ liệu các bảng chính MIMIC-IV HOSP — Task 1

Tài liệu giải thích 44 cột thuộc năm bảng đang dùng trực tiếp để xây dựng bộ dữ liệu dự đoán multi-label disease phenotypes.

## Cách nối dữ liệu

- Đơn vị phân tích: `hadm_id`.
- Chia tập: `subject_id`, để các admission của cùng bệnh nhân không nằm ở nhiều tập.
- Feature xét nghiệm: `labevents`, nối `admissions` bằng `hadm_id` và nối `d_labitems` bằng `itemid`.
- Nhãn bệnh: `diagnoses_icd`, nối `admissions` bằng `hadm_id`; tên ICD lấy từ `d_icd_diagnoses` bằng khóa ghép `icd_code + icd_version`.
- Các dòng `labevents` thiếu `hadm_id` không thuộc tập ứng viên huấn luyện theo admission.

## Cách đọc các mốc thời gian

| Trường | Ý nghĩa | Cách dùng trong nghiên cứu |
|---|---|---|
| admissions.admittime | Bắt đầu admission | Mốc 0 để tính thời gian tương đối của xét nghiệm. |
| labevents.charttime | Ghi nhận/lấy mẫu xét nghiệm | Dùng xác định xét nghiệm xảy ra trước hay sau admittime và có nằm trong admission hay không. |
| labevents.storetime | Kết quả có trong hệ thống | Dùng kiểm tra kết quả đã sẵn có tại mốc dự đoán, hạn chế rò rỉ thông tin tương lai. |
| admissions.dischtime | Kết thúc admission | Giới hạn trên để kiểm tra sự kiện xét nghiệm thuộc đúng lần nhập viện. |
| admissions.edregtime | Đăng ký khoa cấp cứu | Mốc phụ cho admission đi qua ED; có thể trước admittime. |
| admissions.edouttime | Rời khoa cấp cứu | Mốc phụ cho admission đi qua ED; không có ở mọi admission. |
| admissions.deathtime | Tử vong trong bệnh viện | Mốc kết cục, không phải feature đầu vào sớm của bài toán hiện tại. |

Thời gian trong MIMIC đã được dịch chuyển để khử định danh, nhưng thứ tự và khoảng cách tương đối của các sự kiện trong cùng bệnh nhân vẫn dùng được. Với bài toán này, thời gian chủ yếu dùng để lọc đúng quan hệ nhập viện → xét nghiệm → kết quả sẵn có; chưa mặc định đưa timestamp thô vào vector feature.

## Bảng `admissions`

| Vị trí | Cột | Kiểu | Có thể thiếu | Ý nghĩa tiếng Việt | Vai trò | Cách nối | Dùng hiện tại | Ghi chú dữ liệu cục bộ |
|---:|---|---|---|---|---|---|---|---|
| 1 | subject_id | INTEGER NOT NULL | Không | Mã định danh duy nhất của bệnh nhân. | Khóa bệnh nhân; khóa chia tập | Nối với subject_id ở labevents và diagnoses_icd. | Có | 223.452 bệnh nhân trong dữ liệu khảo sát. |
| 2 | hadm_id | INTEGER NOT NULL | Không | Mã định danh duy nhất của một lần nhập viện. | Đơn vị phân tích chính | Nối với hadm_id ở labevents và diagnoses_icd. | Có | 546.028 admission; là khóa trung tâm của bài toán. |
| 3 | admittime | TIMESTAMP NOT NULL | Không | Thời điểm bệnh nhân được ghi nhận nhập viện. | Mốc bắt đầu admission | So sánh với labevents.charttime để chọn xét nghiệm sau nhập viện. | Có | Thời gian đã dịch chuyển nhưng thứ tự tương đối trong cùng bệnh nhân vẫn dùng được. |
| 4 | dischtime | TIMESTAMP | Có thể | Thời điểm kết thúc lần nằm viện hoặc xuất viện. | Mốc kết thúc admission | Dùng kiểm tra charttime có nằm trong admission. | Có | Task 5 ghi nhận 175 admission có dischtime < admittime; cần loại/điều tra khi tạo cohort. |
| 5 | deathtime | TIMESTAMP | Có | Thời điểm tử vong trong bệnh viện nếu có. | Kết cục và kiểm tra dữ liệu | Gắn trực tiếp với hadm_id trong cùng dòng admissions. | Không trực tiếp | Không phải nhãn phenotype hiện tại. |
| 6 | admission_type | VARCHAR(40) NOT NULL | Không | Loại hoặc mức độ khẩn cấp của lần nhập viện. | Thông tin bối cảnh | Không cần nối. | Cần quyết định | Có thể dùng mô tả cohort hoặc phân tầng sau này. |
| 7 | admit_provider_id | VARCHAR(10) | Có | Mã ẩn danh của nhân viên y tế phụ trách tiếp nhận. | Metadata | Có thể nối bảng provider nếu cần. | Không trực tiếp | Mã chỉ có ý nghĩa định danh nhất quán, không mang ý nghĩa lâm sàng nội tại. |
| 8 | admission_location | VARCHAR(60) | Có | Nơi bệnh nhân ở ngay trước khi nhập viện. | Thông tin bối cảnh | Không cần nối. | Cần quyết định | Dùng mô tả nguồn nhập viện nếu cần. |
| 9 | discharge_location | VARCHAR(60) | Có | Nơi hoặc hình thức chuyển đến sau khi xuất viện. | Thông tin kết cục | Không cần nối. | Không trực tiếp | Thông tin xảy ra sau admission, tránh dùng làm feature đầu vào sớm. |
| 10 | insurance | VARCHAR(255) | Có | Loại bảo hiểm được ghi nhận cho admission. | Nhân khẩu học/bối cảnh | Không cần nối. | Cần quyết định | Có thể thay đổi giữa các admission của cùng bệnh nhân. |
| 11 | language | VARCHAR(10) | Có | Ngôn ngữ được ghi nhận của bệnh nhân. | Nhân khẩu học/bối cảnh | Không cần nối. | Cần quyết định | Không phải feature xét nghiệm. |
| 12 | marital_status | VARCHAR(30) | Có | Tình trạng hôn nhân được ghi nhận tại admission. | Nhân khẩu học/bối cảnh | Không cần nối. | Cần quyết định | Có thể thay đổi giữa các admission. |
| 13 | race | VARCHAR(80) | Có | Nhóm chủng tộc/sắc tộc được ghi nhận. | Nhân khẩu học/bối cảnh | Không cần nối. | Cần quyết định | Cần phân tích công bằng nếu đưa vào mô hình. |
| 14 | edregtime | TIMESTAMP | Có | Thời điểm đăng ký tại khoa cấp cứu. | Mốc thời gian ED | So với admittime khi admission đi qua ED. | Không trực tiếp | Có thể sớm hơn admittime; không phải mọi admission đều qua ED. |
| 15 | edouttime | TIMESTAMP | Có | Thời điểm rời khoa cấp cứu. | Mốc thời gian ED | So với admittime và charttime khi cần. | Không trực tiếp | Không phải mọi admission đều qua ED. |
| 16 | hospital_expire_flag | SMALLINT | Có thể | Cờ tử vong trong lần nằm viện: 1 là tử vong, 0 là sống khi xuất viện. | Kết cục và kiểm tra dữ liệu | Gắn trực tiếp với hadm_id. | Không trực tiếp | Không phải nhãn phenotype theo đề cương hiện tại. |

Nguồn chính thức: https://mimic.mit.edu/docs/iv/modules/hosp/admissions.html

## Bảng `labevents`

| Vị trí | Cột | Kiểu | Có thể thiếu | Ý nghĩa tiếng Việt | Vai trò | Cách nối | Dùng hiện tại | Ghi chú dữ liệu cục bộ |
|---:|---|---|---|---|---|---|---|---|
| 1 | labevent_id | INTEGER NOT NULL | Không | Mã duy nhất của một dòng kết quả xét nghiệm. | Khóa dòng | Không dùng để nối cohort. | Không trực tiếp | Dùng truy vết và loại trùng nếu cần. |
| 2 | subject_id | INTEGER NOT NULL | Không | Mã bệnh nhân sở hữu kết quả xét nghiệm. | Khóa bệnh nhân; kiểm tra nối | Phải khớp subject_id của hadm_id trong admissions. | Có | Dùng kiểm tra toàn vẹn và chia tập theo bệnh nhân. |
| 3 | hadm_id | INTEGER | Có | Mã admission mà kết quả xét nghiệm được gán vào. | Khóa admission | Nối admissions.hadm_id và diagnoses_icd.hadm_id. | Có; bắt buộc | 73.768.897/158.374.764 dòng (46,579%) thiếu hadm_id và không thuộc tập ứng viên train theo admission. |
| 4 | specimen_id | INTEGER NOT NULL | Không | Mã mẫu bệnh phẩm; nhiều xét nghiệm có thể dùng chung một mẫu. | Nhóm mẫu bệnh phẩm | Nhóm các dòng cùng mẫu khi phân tích kỹ thuật. | Cần quyết định | Không thay thế hadm_id. |
| 5 | itemid | INTEGER NOT NULL | Không | Mã khái niệm xét nghiệm. | Khóa feature xét nghiệm | Nối d_labitems.itemid để lấy tên, loại dịch và nhóm xét nghiệm. | Có | 976 itemid thực sự xuất hiện trong labevents. |
| 6 | order_provider_id | VARCHAR(10) | Có | Mã ẩn danh của nhân viên y tế đặt xét nghiệm. | Metadata | Có thể nối provider nếu cần. | Không trực tiếp | Không phải feature xét nghiệm chính. |
| 7 | charttime | TIMESTAMP(0) | Có thể | Thời điểm kết quả được ghi nhận; thường gần thời điểm lấy mẫu. | Mốc thời gian xét nghiệm | So với admissions.admittime và dischtime để chọn đúng khoảng thời gian. | Có; dùng để lọc | Không nhất thiết là lúc bác sĩ nhìn thấy kết quả. |
| 8 | storetime | TIMESTAMP(0) | Có thể | Thời điểm kết quả được lưu và có thể truy cập trong hệ thống xét nghiệm. | Mốc sẵn có của kết quả | So với charttime và mốc dự đoán để kiểm soát rò rỉ tương lai. | Có; dùng kiểm tra | Task 6 dùng trường này để đánh giá nguy cơ kết quả có sau mốc dự đoán. |
| 9 | value | VARCHAR(200) | Có | Giá trị kết quả ở dạng gốc, có thể là số hoặc văn bản. | Giá trị thô | Kết hợp itemid và valueuom để diễn giải. | Cần quyết định | Không ép toàn bộ thành số; một số xét nghiệm mang giá trị định tính. |
| 10 | valuenum | DOUBLE PRECISION | Có | Phiên bản số của value khi kết quả có thể chuyển thành số. | Feature số ứng viên | Kết hợp itemid, valueuom và mốc thời gian. | Có với xét nghiệm số | Dòng định tính có thể không có valuenum nhưng vẫn có value. |
| 11 | valueuom | VARCHAR(20) | Có | Đơn vị đo của kết quả xét nghiệm. | Chuẩn hóa feature | Phân tích theo cặp itemid + valueuom. | Có | Có 10 itemid xuất hiện với nhiều đơn vị; phải chuẩn hóa trước khi gộp giá trị. |
| 12 | ref_range_lower | DOUBLE PRECISION | Có | Giới hạn dưới của khoảng tham chiếu. | Thông tin tham chiếu | Diễn giải cùng itemid và valueuom. | Cần quyết định | Không mặc định dùng làm feature. |
| 13 | ref_range_upper | DOUBLE PRECISION | Có | Giới hạn trên của khoảng tham chiếu. | Thông tin tham chiếu | Diễn giải cùng itemid và valueuom. | Cần quyết định | Không mặc định dùng làm feature. |
| 14 | flag | VARCHAR(10) | Có | Cờ cho biết kết quả bất thường theo hệ thống xét nghiệm. | Feature phụ ứng viên | Diễn giải cùng khoảng tham chiếu. | Cần quyết định | Cần kiểm tra tính nhất quán trước khi dùng. |
| 15 | priority | VARCHAR(7) | Có | Mức ưu tiên xử lý xét nghiệm. | Metadata quy trình | Không cần nối. | Cần quyết định | Có thể phản ánh quy trình chăm sóc hơn là sinh lý. |
| 16 | comments | TEXT | Có | Ghi chú đã khử định danh; đôi khi chứa kết quả hoặc diễn giải. | Văn bản phụ | Không cần nối. | Không trực tiếp | Không dùng trong pipeline bảng số ban đầu. |

Nguồn chính thức: https://mimic.mit.edu/docs/iv/modules/hosp/labevents.html

## Bảng `d_labitems`

| Vị trí | Cột | Kiểu | Có thể thiếu | Ý nghĩa tiếng Việt | Vai trò | Cách nối | Dùng hiện tại | Ghi chú dữ liệu cục bộ |
|---:|---|---|---|---|---|---|---|---|
| 1 | itemid | INTEGER | Có thể theo schema | Mã duy nhất của khái niệm xét nghiệm. | Khóa từ điển xét nghiệm | Nối labevents.itemid. | Có | Task 2 xác nhận 1.650 itemid, không thiếu và không trùng. |
| 2 | label | VARCHAR(50) | Có thể theo schema | Tên dễ đọc của xét nghiệm. | Tên feature | Tra cứu bằng itemid. | Có | Dùng đặt tên feature và báo cáo. |
| 3 | fluid | VARCHAR(50) | Có thể theo schema | Loại bệnh phẩm được xét nghiệm. | Phân biệt ngữ cảnh xét nghiệm | Tra cứu bằng itemid. | Có | Giúp tránh gộp các phép đo cùng tên nhưng khác bệnh phẩm. |
| 4 | category | VARCHAR(50) | Có thể theo schema | Nhóm xét nghiệm cấp cao. | Nhóm feature | Tra cứu bằng itemid. | Có | Hỗ trợ thống kê và chọn nhóm xét nghiệm. |

Nguồn chính thức: https://mimic.mit.edu/docs/iv/modules/hosp/d_labitems.html

## Bảng `diagnoses_icd`

| Vị trí | Cột | Kiểu | Có thể thiếu | Ý nghĩa tiếng Việt | Vai trò | Cách nối | Dùng hiện tại | Ghi chú dữ liệu cục bộ |
|---:|---|---|---|---|---|---|---|---|
| 1 | subject_id | INTEGER NOT NULL | Không | Mã bệnh nhân được gán chẩn đoán. | Khóa bệnh nhân; kiểm tra nối | Nối admissions.subject_id và kiểm tra theo hadm_id. | Có | Task 4 ghi nhận không thiếu ở các cột khóa. |
| 2 | hadm_id | INTEGER NOT NULL | Không | Mã admission được gán chẩn đoán ICD. | Khóa admission của nhãn | Nối admissions.hadm_id và labevents.hadm_id. | Có; bắt buộc | Là cầu nối giữa feature xét nghiệm và nhãn bệnh. |
| 3 | seq_num | INTEGER NOT NULL | Không | Thứ tự ưu tiên của chẩn đoán trong admission. | Thứ hạng mã chẩn đoán | Thuộc từng hadm_id. | Cần quyết định | Không phải thời điểm chẩn đoán; không dùng để chứng minh bệnh xuất hiện trước hay sau xét nghiệm. |
| 4 | icd_code | VARCHAR(7) | Có thể theo schema | Mã chẩn đoán ICD; dấu thập phân bị lược bỏ trong dữ liệu. | Nguồn nhãn bệnh | Nối d_icd_diagnoses bằng cả icd_code và icd_version; sau đó ánh xạ PheCode. | Có | Giữ kiểu chuỗi để không mất số 0 đầu mã. |
| 5 | icd_version | INTEGER | Có thể theo schema | Phiên bản hệ mã ICD. | Phân biệt hệ mã | Nối d_icd_diagnoses cùng icd_code; chọn đúng bảng ánh xạ PheCode. | Có | Task 4: 9.143 mã ICD-9 và 19.440 mã ICD-10 phân biệt theo cặp khóa. |

Nguồn chính thức: https://mimic.mit.edu/docs/iv/modules/hosp/diagnoses_icd.html

## Bảng `d_icd_diagnoses`

| Vị trí | Cột | Kiểu | Có thể thiếu | Ý nghĩa tiếng Việt | Vai trò | Cách nối | Dùng hiện tại | Ghi chú dữ liệu cục bộ |
|---:|---|---|---|---|---|---|---|---|
| 1 | icd_code | CHAR(7) NOT NULL | Không | Mã ICD trong từ điển chẩn đoán. | Khóa từ điển ICD | Nối diagnoses_icd.icd_code cùng icd_version. | Có | Không nối chỉ bằng icd_code. |
| 2 | icd_version | INTEGER NOT NULL | Không | Phiên bản ICD tương ứng với mã. | Khóa từ điển ICD | Nối diagnoses_icd.icd_version cùng icd_code. | Có | Hai cột tạo khóa ghép của từ điển. |
| 3 | long_title | VARCHAR(255) | Có thể | Tên mô tả đầy đủ của chẩn đoán ICD. | Tên nhãn để đọc và báo cáo | Tra cứu theo icd_code + icd_version. | Có | Chỉ là từ điển; không chứng minh bệnh nhân có chẩn đoán nếu không có dòng trong diagnoses_icd. |

Nguồn chính thức: https://mimic.mit.edu/docs/iv/modules/hosp/d_icd_diagnoses.html
