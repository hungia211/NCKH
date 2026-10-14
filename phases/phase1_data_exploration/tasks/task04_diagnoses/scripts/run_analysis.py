"""Task 4 full-data exploration of MIMIC-IV HOSP diagnoses_icd."""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "AGENTS.md").is_file())
TASK_DIR = Path(__file__).resolve().parents[1]


class UniqueInt64Accumulator:
    def __init__(self) -> None: self.levels: list[np.ndarray | None] = []
    def add(self, values: np.ndarray) -> None:
        current = np.unique(values.astype(np.int64, copy=False)); level = 0
        while current.size:
            if level == len(self.levels): self.levels.append(current); return
            if self.levels[level] is None: self.levels[level] = current; return
            current = np.union1d(self.levels[level], current); self.levels[level] = None; level += 1
    def finish(self) -> np.ndarray:
        arrays = [array for array in self.levels if array is not None and array.size]
        return np.unique(np.concatenate(arrays)) if arrays else np.array([], dtype=np.int64)


def quantiles(values: list[int]) -> dict[str, float | int]:
    array = np.asarray(values, dtype=np.int64)
    return {"min": int(array.min()), "p25": float(np.quantile(array, .25)), "median": float(np.quantile(array, .5)),
            "p75": float(np.quantile(array, .75)), "p90": float(np.quantile(array, .9)), "p95": float(np.quantile(array, .95)),
            "p99": float(np.quantile(array, .99)), "max": int(array.max()), "mean": float(array.mean())} if array.size else {}


def main() -> None:
    parser = argparse.ArgumentParser(); parser.add_argument("--data-dir", type=Path, default=ROOT / "data" / "hosp")
    parser.add_argument("--output-dir", type=Path); parser.add_argument("--chunksize", type=int, default=500_000); args = parser.parse_args()
    started = datetime.now(timezone.utc); output_dir = args.output_dir or TASK_DIR / "outputs" / started.strftime("%Y%m%dT%H%M%SZ")
    output_dir.mkdir(parents=True, exist_ok=False); data_dir = args.data_dir.resolve()
    paths = {name: data_dir / f"{name}.csv.gz" for name in ("admissions", "d_icd_diagnoses", "diagnoses_icd")}
    if not all(path.is_file() for path in paths.values()): raise SystemExit(f"Missing required input under {data_dir}")
    admissions = pd.read_csv(paths["admissions"], usecols=["hadm_id", "subject_id"])
    if admissions["hadm_id"].isna().any() or admissions["hadm_id"].duplicated().any(): raise SystemExit("admissions.hadm_id must be complete and unique")
    owners = admissions.set_index("hadm_id")["subject_id"]
    admission_index = {int(hadm): index for index, hadm in enumerate(admissions["hadm_id"].astype("int64"))}; admission_count = len(admission_index)
    dictionary = pd.read_csv(paths["d_icd_diagnoses"], dtype={"icd_code": "string", "icd_version": "Int64"})
    if dictionary[["icd_code", "icd_version"]].isna().any().any() or dictionary.duplicated(["icd_code", "icd_version"]).any(): raise SystemExit("d_icd_diagnoses key must be complete and unique")
    dictionary["icd_code"] = dictionary["icd_code"].str.strip()
    keys = [(str(code), int(version)) for code, version in zip(dictionary["icd_code"], dictionary["icd_version"])]
    key_to_id = {key: index for index, key in enumerate(keys)}
    title_by_key = {(str(row.icd_code), int(row.icd_version)): row.long_title for row in dictionary.itertuples()}
    counts: Counter[str] = Counter(); version_rows: Counter[int] = Counter(); seq_rows: Counter[int] = Counter()
    code_rows: Counter[int] = Counter(); admission_rows: Counter[int] = Counter(); primary_rows_by_admission: Counter[int] = Counter()
    observed_complete_keys: set[tuple[str, int]] = set()
    usable_pairs = UniqueInt64Accumulator()
    dtype = {"subject_id": "Int64", "hadm_id": "Int64", "seq_num": "Int64", "icd_code": "string", "icd_version": "Int64"}
    for chunk_number, frame in enumerate(pd.read_csv(paths["diagnoses_icd"], dtype=dtype, chunksize=args.chunksize), start=1):
        counts["rows"] += len(frame)
        subject_present = frame["subject_id"].notna(); hadm_present = frame["hadm_id"].notna()
        code_present = frame["icd_code"].notna() & frame["icd_code"].str.strip().ne("")
        version_present = frame["icd_version"].notna(); seq_present = frame["seq_num"].notna()
        complete = subject_present & hadm_present & code_present & version_present
        expected_subject = frame["hadm_id"].map(owners); known_admission = complete & expected_subject.notna()
        subject_match = known_admission & frame["subject_id"].eq(expected_subject)
        clean_codes = frame["icd_code"].fillna("").str.strip()
        clean_versions = frame["icd_version"].fillna(-1).astype("int64")
        key_series = pd.Series(list(zip(clean_codes, clean_versions)), index=frame.index)
        code_ids = key_series.map(key_to_id); dictionary_match = code_ids.notna(); usable = subject_match & dictionary_match
        masks = {"missing_subject_id": ~subject_present, "missing_hadm_id": ~hadm_present, "missing_icd_code": ~code_present,
                 "missing_icd_version": ~version_present, "missing_seq_num": ~seq_present, "complete_label_keys": complete,
                 "known_admission_after_complete_keys": known_admission, "subject_match_after_known_admission": subject_match,
                 "subject_mismatch_after_known_admission": known_admission & ~frame["subject_id"].eq(expected_subject),
                 "dictionary_match": complete & dictionary_match, "dictionary_orphan": complete & ~dictionary_match,
                 "usable_diagnosis_row": usable, "seq_num_1_row": seq_present & frame["seq_num"].eq(1)}
        for name, mask in masks.items(): counts[name] += int(mask.sum())
        version_rows.update({int(k): int(v) for k, v in frame.loc[version_present].groupby("icd_version").size().items()})
        seq_rows.update({int(k): int(v) for k, v in frame.loc[seq_present].groupby("seq_num").size().items()})
        observed_complete_keys.update((str(code).strip(), int(version)) for code, version in frame.loc[complete, ["icd_code", "icd_version"]].itertuples(index=False, name=None))
        usable_frame = frame.loc[usable, ["hadm_id"]].copy(); usable_frame["code_id"] = code_ids.loc[usable].astype("int64")
        usable_frame["admission_index"] = usable_frame["hadm_id"].map(admission_index).astype("int64")
        if not usable_frame.empty:
            code_rows.update({int(k): int(v) for k, v in usable_frame.groupby("code_id").size().items()})
            admission_rows.update({int(k): int(v) for k, v in usable_frame.groupby("hadm_id").size().items()})
            usable_pairs.add(usable_frame["code_id"].to_numpy(dtype=np.int64) * np.int64(admission_count) + usable_frame["admission_index"].to_numpy(dtype=np.int64))
        primary_usable = usable & seq_present & frame["seq_num"].eq(1)
        if primary_usable.any():
            primary_rows_by_admission.update({int(k): int(v) for k, v in frame.loc[primary_usable].groupby("hadm_id").size().items()})
        print(f"diagnoses chunks={chunk_number} rows={counts['rows']:,}", flush=True)
    pairs = usable_pairs.finish(); code_admissions: Counter[int] = Counter(); admission_unique_codes: Counter[int] = Counter()
    version_admissions: dict[int, int] = {}
    if pairs.size:
        pair_code_ids = pairs // np.int64(admission_count); pair_admission_index = pairs % np.int64(admission_count)
        unique_keys, unique_values = np.unique(pair_code_ids, return_counts=True); code_admissions.update({int(k): int(v) for k, v in zip(unique_keys, unique_values)})
        admission_keys, admission_values = np.unique(pair_admission_index, return_counts=True); indexed_hadm = admissions["hadm_id"].astype("int64").to_numpy()
        admission_unique_codes.update({int(indexed_hadm[int(k)]): int(v) for k, v in zip(admission_keys, admission_values)})
        pair_versions = np.asarray([keys[int(code_id)][1] for code_id in pair_code_ids], dtype=np.int64)
        version_pairs = np.unique(pair_versions * np.int64(admission_count) + pair_admission_index)
        versions, version_counts = np.unique(version_pairs // np.int64(admission_count), return_counts=True)
        version_admissions = {int(k): int(v) for k, v in zip(versions, version_counts)}
    profiles = []
    for code_id, row_count in code_rows.items():
        code, version = keys[code_id]
        profiles.append({"icd_version": version, "icd_code": code, "long_title": title_by_key.get((code, version), ""),
                         "rows": row_count, "admissions": code_admissions[code_id], "duplicate_rows_within_admission": row_count - code_admissions[code_id]})
    profiles.sort(key=lambda row: (-row["admissions"], -row["rows"], row["icd_version"], row["icd_code"]))
    manifest = []
    for path in paths.values(): stat = path.stat(); manifest.append({"path": str(path), "bytes": stat.st_size, "mtime_ns": stat.st_mtime_ns})
    summary = {"task": 4, "started_utc": started.isoformat(), "finished_utc": datetime.now(timezone.utc).isoformat(), "read_only": True,
               "usable_definition": "subject_id, hadm_id, icd_code and icd_version present; hadm_id exists in admissions; subject_id matches admission owner; code and version match d_icd_diagnoses",
               "inputs": manifest, "counts": dict(counts), "rows_by_icd_version": dict(sorted(version_rows.items())),
               "unique_complete_codes_by_version": {str(v): len({c for c, version in observed_complete_keys if version == v}) for v in sorted({version for _, version in observed_complete_keys})},
               "unique_complete_code_version_pairs": len(observed_complete_keys), "usable_admissions": len(admission_rows),
               "usable_code_version_pairs": len(code_rows), "duplicate_usable_rows_within_admission": counts["usable_diagnosis_row"] - len(pairs),
               "admissions_by_icd_version": version_admissions, "admissions_with_seq_num_1": len(primary_rows_by_admission),
               "admissions_with_multiple_seq_num_1_rows": sum(1 for value in primary_rows_by_admission.values() if value > 1),
               "diagnosis_rows_per_admission": quantiles(list(admission_rows.values())), "unique_codes_per_admission": quantiles(list(admission_unique_codes.values())),
               "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
               "runtime": {"python": platform.python_version(), "pandas": pd.__version__, "numpy": np.__version__}}
    pd.DataFrame(profiles).to_csv(output_dir / "icd_code_profile.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame([{"icd_version": k, "rows": v, "rate": v / counts["rows"]} for k, v in sorted(version_rows.items())]).to_csv(output_dir / "icd_version_summary.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame([{"seq_num": k, "rows": v, "rate": v / counts["rows"]} for k, v in sorted(seq_rows.items())]).to_csv(output_dir / "seq_num_distribution.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame([{"metric": k, "count": v, "rate_of_all_rows": v / counts["rows"]} for k, v in counts.items()]).to_csv(output_dir / "row_usability_funnel.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame([{"statistic": k, "diagnosis_rows": v, "unique_codes": summary["unique_codes_per_admission"].get(k)} for k, v in summary["diagnosis_rows_per_admission"].items()]).to_csv(output_dir / "diagnoses_per_admission.csv", index=False, encoding="utf-8-sig")
    (output_dir / "results.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"OUTPUT {output_dir}", flush=True)


if __name__ == "__main__": main()
