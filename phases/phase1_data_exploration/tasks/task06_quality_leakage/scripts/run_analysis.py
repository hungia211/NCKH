"""Task 6 synthesis of Phase 1 data-quality and leakage findings."""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "AGENTS.md").is_file())
PHASE = ROOT / "phases" / "phase1_data_exploration"
TASK_DIR = Path(__file__).resolve().parents[1]


def latest_run(task_name: str) -> Path:
    candidates = sorted(path.parent for path in (PHASE / "tasks" / task_name / "outputs").glob("*/results.json"))
    if not candidates:
        raise SystemExit(f"No completed run found for {task_name}")
    return candidates[-1]


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", type=Path, default=ROOT / "data" / "hosp")
    parser.add_argument("--task2-run", type=Path, default=PHASE / "tasks" / "task02_key_linkage" / "outputs" / "20260926T154108Z")
    parser.add_argument("--task3-run", type=Path, default=PHASE / "tasks" / "task03_labevents" / "outputs" / "20260930T163439Z")
    parser.add_argument("--task4-run", type=Path, default=PHASE / "tasks" / "task04_diagnoses" / "outputs" / "20260930T164935Z")
    parser.add_argument("--task5-run", type=Path)
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()

    started = datetime.now(timezone.utc)
    task5_run = (args.task5_run or latest_run("task05_admission_time")).resolve()
    runs = {"task2": args.task2_run.resolve(), "task3": args.task3_run.resolve(), "task4": args.task4_run.resolve(), "task5": task5_run}
    if not all((path / "results.json").is_file() for path in runs.values()):
        raise SystemExit("A required Task 2–5 results.json file is missing")
    output_dir = args.output_dir or TASK_DIR / "outputs" / started.strftime("%Y%m%dT%H%M%SZ")
    output_dir.mkdir(parents=True, exist_ok=False)

    t2, t3, t4, t5 = (load_json(runs[name] / "results.json") for name in ("task2", "task3", "task4", "task5"))
    profile = pd.read_csv(task5_run / "admission_time_profile.csv", dtype={"subject_id": "int64", "hadm_id": "int64"})
    diagnosis_path = args.data_dir.resolve() / "diagnoses_icd.csv.gz"
    if not diagnosis_path.is_file():
        raise SystemExit(f"Missing input: {diagnosis_path}")
    diagnosis_hadm: set[int] = set()
    for chunk in pd.read_csv(diagnosis_path, usecols=["hadm_id"], dtype={"hadm_id": "Int64"}, chunksize=500_000):
        diagnosis_hadm.update(chunk["hadm_id"].dropna().astype("int64").tolist())

    diagnosis_mask = profile["hadm_id"].isin(diagnosis_hadm)
    masks = {
        "all_admissions": pd.Series(True, index=profile.index),
        "diagnosis_available": diagnosis_mask,
        "candidate_lab_available": profile["candidate_rows"].gt(0),
        "lab_during_admission": profile["during_admission_rows"].gt(0),
        "lab_within_6h": profile["within_6h_rows"].gt(0),
        "lab_within_12h": profile["within_12h_rows"].gt(0),
        "lab_within_24h": profile["within_24h_rows"].gt(0),
    }
    cohort_rows = []
    for name, mask in masks.items():
        combined = mask if name in ("all_admissions", "diagnosis_available") else mask & diagnosis_mask
        subject_counts = profile.loc[combined].groupby("subject_id").size()
        cohort_rows.append({
            "cohort_step": name,
            "requires_diagnosis": name not in ("all_admissions", "diagnosis_available"),
            "admissions": int(combined.sum()),
            "subjects": int(subject_counts.size),
            "subjects_with_multiple_admissions": int((subject_counts > 1).sum()),
            "share_all_admissions": float(combined.sum() / len(profile)),
        })
    pd.DataFrame(cohort_rows).to_csv(output_dir / "cohort_readiness.csv", index=False, encoding="utf-8-sig")

    c3 = t3["counts"]; c4 = t4["counts"]; c5 = t5["counts"]
    quality_rows = [
        {"source": "labevents", "issue": "Thiếu hadm_id", "count": c3["missing_hadm_id"], "denominator": c3["rows"], "unit": "rows", "decision_or_next_action": "Loại khỏi dữ liệu xử lý admission-level; không khôi phục khóa"},
        {"source": "labevents", "issue": "subject_id không khớp chủ admission", "count": c3["subject_mismatch_after_known_admission"], "denominator": c3["rows"], "unit": "rows", "decision_or_next_action": "Loại khỏi tập ứng viên và lưu audit count"},
        {"source": "labevents", "issue": "Không có kết quả số hoặc chữ", "count": c3["no_numeric_or_text_result"], "denominator": c3["rows"], "unit": "rows", "decision_or_next_action": "Không dùng làm giá trị feature; xem xét metadata riêng nếu cần"},
        {"source": "labevents", "issue": "Thiếu storetime trong dòng ứng viên", "count": c5.get("candidate_missing_storetime", 0), "denominator": c5["candidate_rows"], "unit": "rows", "decision_or_next_action": "Không loại chỉ vì thiếu storetime; charttime là mốc đo chính đang khảo sát"},
        {"source": "labevents", "issue": "storetime trước charttime", "count": c5.get("candidate_storetime_before_charttime", 0), "denominator": c5["candidate_rows"] - c5.get("candidate_missing_storetime", 0), "unit": "rows", "decision_or_next_action": "Kiểm tra trước khi dùng storetime làm mốc sẵn có"},
        {"source": "d_labitems/labevents", "issue": "itemid có nhiều chuỗi đơn vị", "count": t3["items_with_multiple_observed_units"], "denominator": t3["unique_itemid_observed"], "unit": "itemids", "decision_or_next_action": "Xem xét từng itemid trước chuẩn hóa và tạo feature"},
        {"source": "admissions", "issue": "dischtime trước admittime", "count": t5["negative_duration_admissions"], "denominator": t5["admissions"], "unit": "admissions", "decision_or_next_action": "Không dùng interval âm để phân loại thời gian hoặc chọn cohort"},
        {"source": "labevents/admissions", "issue": "Dòng ứng viên trước admittime", "count": c5["before_admission_rows"], "denominator": c5["candidate_rows"], "unit": "rows", "decision_or_next_action": "Không đưa vào cửa sổ bắt đầu tại admittime nếu chưa có quyết định khác"},
        {"source": "labevents/admissions", "issue": "Dòng ứng viên sau dischtime", "count": c5["after_discharge_rows"], "denominator": c5["candidate_rows"], "unit": "rows", "decision_or_next_action": "Không đưa vào feature của admission"},
        {"source": "diagnoses_icd", "issue": "Dòng trùng cùng hadm_id, icd_code, icd_version", "count": t4["duplicate_usable_rows_within_admission"], "denominator": c4["rows"], "unit": "rows", "decision_or_next_action": "Khử trùng ở bước tạo nhãn admission-phenotype"},
        {"source": "diagnoses_icd", "issue": "Admission có nhiều dòng seq_num = 1", "count": t4["admissions_with_multiple_seq_num_1_rows"], "denominator": t4["usable_admissions"], "unit": "admissions", "decision_or_next_action": "Không giả định seq_num = 1 luôn duy nhất; giữ bài toán multi-label"},
    ]
    for row in quality_rows:
        row["rate"] = row["count"] / row["denominator"] if row["denominator"] else None
    pd.DataFrame(quality_rows).to_csv(output_dir / "quality_issue_register.csv", index=False, encoding="utf-8-sig")

    leakage_rows = [
        {"risk": "Sử dụng xét nghiệm muộn", "mechanism": "Xét nghiệm sau giai đoạn đầu có thể phản ánh chẩn đoán hoặc điều trị đã diễn ra", "required_control": "Chọn cửa sổ sớm dựa trên Task 5 và chỉ tạo feature trong cửa sổ đã chốt", "decision_status": "Chưa chọn 6, 12 hoặc 24 giờ"},
        {"risk": "Cùng bệnh nhân ở nhiều tập", "mechanism": "Một subject_id có nhiều hadm_id", "required_control": "Chia train validation test theo subject_id", "decision_status": "Đã chốt nguyên tắc"},
        {"risk": "Tiền xử lý học từ toàn bộ dữ liệu", "mechanism": "Imputation, scaling hoặc chọn feature trước split làm rò thông tin", "required_control": "Fit mọi biến đổi học từ dữ liệu chỉ trên train rồi áp dụng sang validation và test", "decision_status": "Bắt buộc ở phase modeling"},
        {"risk": "Chọn nhãn theo toàn bộ dữ liệu", "mechanism": "Dùng tần suất của test để quyết định phenotype làm thay đổi không gian nhãn", "required_control": "Chốt protocol lựa chọn nhãn trước đánh giá cuối và ghi rõ dữ liệu dùng để đặt ngưỡng", "decision_status": "Chờ ICD sang Phecode"},
        {"risk": "Diễn giải thời điểm diagnosis", "mechanism": "diagnoses_icd không có timestamp xác lập từng chẩn đoán", "required_control": "Chỉ mô tả nhãn được ghi nhận cho admission; không tuyên bố dự đoán trước bác sĩ", "decision_status": "Đã ghi thành giới hạn diễn giải"},
        {"risk": "Nhân dòng khi nối lab với diagnosis", "mechanism": "Nối trực tiếp hai bảng nhiều dòng trên hadm_id tạo tích Descartes", "required_control": "Tổng hợp X và Y riêng ở cấp hadm_id rồi mới ghép", "decision_status": "Đã chốt nguyên tắc"},
    ]
    pd.DataFrame(leakage_rows).to_csv(output_dir / "leakage_control_plan.csv", index=False, encoding="utf-8-sig")

    summary = {
        "task": 6, "started_utc": started.isoformat(), "finished_utc": datetime.now(timezone.utc).isoformat(), "read_only": True,
        "input_runs": {name: str(path) for name, path in runs.items()}, "diagnoses_input": str(diagnosis_path),
        "quality_issue_count": len(quality_rows), "leakage_risk_count": len(leakage_rows), "cohort_readiness": cohort_rows,
        "candidate_lab_rows": c3["candidate_usable_row"], "candidate_lab_admissions": t3["candidate_admissions"],
        "diagnosis_rows": c4["rows"], "diagnosis_admissions": t4["usable_admissions"],
        "final_cohort_not_selected": True, "official_window_not_selected": True, "final_label_set_not_selected": True,
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "runtime": {"python": platform.python_version(), "pandas": pd.__version__}, "source_rows_removed": 0,
    }
    (output_dir / "results.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"OUTPUT {output_dir}", flush=True)


if __name__ == "__main__":
    main()
