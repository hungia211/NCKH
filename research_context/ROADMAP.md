# Research roadmap

## Giai đoạn 1 — Data exploration

Thống kê subject, admission, lab có `hadm_id`, itemid, missingness, đơn vị đo, ICD-9/ICD-10 và phân bố diagnosis. Chưa lọc mạnh.

Task, script và kết quả được quản lý tại `../phases/phase1_data_exploration/`.

## Giai đoạn 2 — Cohort definition

Xác định admission đủ điều kiện, admission có lab và diagnosis, early-admission window, inclusion/exclusion criteria. Ghi lại mọi rule.

Kế hoạch, trạng thái và decision log được quản lý tại `../phases/phase2_cohort_definition/`.

## Giai đoạn 3 — Laboratory features

Kiểm tra itemid và đơn vị, xử lý missing/outlier, khảo sát aggregation, chuyển long → wide theo `hadm_id`.

## Giai đoạn 4 — Disease labels

Chuẩn hóa ICD-9/ICD-10, map ICD → Phecode, đo coverage và frequency, sau đó mới quyết định label set.

## Giai đoạn 5 — Final dataset

Ghép X và Y, kiểm tra missing/class imbalance/leakage, patient-level split theo `subject_id`.

## Giai đoạn 6 — Modeling

Có baseline trước, sau đó so sánh các mô hình multi-label phù hợp và cách xử lý imbalance.

## Giai đoạn 7 — Evaluation and explainability

Dùng F1, AUROC, AUPRC và phân tích per-label; SHAP/feature importance chỉ được diễn giải là đóng góp vào dự đoán.

## Hướng mở rộng sau pipeline chính — Longitudinal multi-admission

Sau khi hoàn thành baseline admission-level, có thể so sánh với mô hình sử dụng lịch sử các admission trước cùng xét nghiệm giai đoạn sớm của admission mục tiêu để dự đoán phenotype của admission mục tiêu.

Hướng mở rộng này chưa thay đổi kế hoạch Phase 1–7. Thiết kế chi tiết được lưu tại [`LONGITUDINAL_EXTENSION.md`](LONGITUDINAL_EXTENSION.md).
