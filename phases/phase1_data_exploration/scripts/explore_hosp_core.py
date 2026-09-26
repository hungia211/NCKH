"""Chunked Phase 1 analysis for the core HOSP tables.

Read-only analysis of labevents, diagnoses_icd, admissions and dictionaries.
It deliberately reports distributions and missingness without applying cohort
filters or selecting thresholds.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "data" / "hosp"
OUT = (
    ROOT
    / "phases"
    / "phase1_data_exploration"
    / "outputs"
    / "machine_readable"
    / "core_summary.json"
)


def analyse_labs(path: Path, chunksize: int) -> dict[str, object]:
    usecols = ["subject_id", "hadm_id", "itemid", "charttime", "valuenum", "valueuom"]
    counts = Counter()
    subjects: set[int] = set()
    admissions: set[int] = set()
    items: Counter[int] = Counter()
    units_by_item: dict[int, set[str]] = {}
    min_time = None
    max_time = None
    for chunk in pd.read_csv(path, compression="gzip", usecols=usecols, chunksize=chunksize):
        counts["rows"] += len(chunk)
        counts["missing_hadm_id"] += int(chunk["hadm_id"].isna().sum())
        counts["missing_valuenum"] += int(chunk["valuenum"].isna().sum())
        counts["missing_valueuom"] += int(chunk["valueuom"].isna().sum())
        valid_subjects = chunk["subject_id"].dropna().astype("int64")
        valid_hadm = chunk["hadm_id"].dropna().astype("int64")
        subjects.update(valid_subjects.tolist())
        admissions.update(valid_hadm.tolist())
        items.update(chunk["itemid"].dropna().astype("int64").tolist())
        for itemid, group in chunk.dropna(subset=["itemid"]).groupby("itemid")["valueuom"]:
            units_by_item.setdefault(int(itemid), set()).update(
                str(value) for value in group.dropna().unique()
            )
        times = pd.to_datetime(chunk["charttime"], errors="coerce")
        if times.notna().any():
            low, high = times.min(), times.max()
            min_time = low if min_time is None else min(min_time, low)
            max_time = high if max_time is None else max(max_time, high)
    return {
        "rows": counts["rows"],
        "unique_subject_id": len(subjects),
        "unique_hadm_id_non_null": len(admissions),
        "unique_itemid": len(items),
        "missing": {key: counts[key] for key in ("missing_hadm_id", "missing_valuenum", "missing_valueuom")},
        "top_itemid": [{"itemid": item, "rows": count} for item, count in items.most_common(30)],
        "items_with_multiple_units": sum(1 for units in units_by_item.values() if len(units) > 1),
        "charttime_min": str(min_time),
        "charttime_max": str(max_time),
    }


def analyse_diagnoses(path: Path, chunksize: int) -> dict[str, object]:
    usecols = ["subject_id", "hadm_id", "seq_num", "icd_code", "icd_version"]
    counts = Counter()
    subjects: set[int] = set()
    admissions: set[int] = set()
    codes: Counter[tuple[int, str]] = Counter()
    diagnoses_per_admission: Counter[int] = Counter()
    for chunk in pd.read_csv(path, compression="gzip", usecols=usecols, chunksize=chunksize, dtype={"icd_code": "string"}):
        counts["rows"] += len(chunk)
        subjects.update(chunk["subject_id"].dropna().astype("int64").tolist())
        admissions.update(chunk["hadm_id"].dropna().astype("int64").tolist())
        codes.update(zip(chunk["icd_version"].astype(int), chunk["icd_code"].astype(str)))
        diagnoses_per_admission.update(chunk.groupby("hadm_id").size().to_dict())
    versions = Counter(version for version, _ in codes)
    return {
        "rows": counts["rows"],
        "unique_subject_id": len(subjects),
        "unique_hadm_id": len(admissions),
        "unique_icd_code_version_pairs": len(codes),
        "icd_version_counts": dict(sorted(versions.items())),
        "diagnoses_per_admission": {
            "min": min(diagnoses_per_admission.values()),
            "max": max(diagnoses_per_admission.values()),
            "mean": sum(diagnoses_per_admission.values()) / len(diagnoses_per_admission),
        },
        "top_icd_code_version": [
            {"icd_version": version, "icd_code": code, "rows": count}
            for (version, code), count in codes.most_common(30)
        ],
    }


def analyse_admissions(path: Path) -> dict[str, object]:
    frame = pd.read_csv(path, compression="gzip", parse_dates=["admittime", "dischtime"])
    duration = (frame["dischtime"] - frame["admittime"]).dt.total_seconds() / 86400
    return {
        "rows": len(frame),
        "unique_subject_id": int(frame["subject_id"].nunique()),
        "unique_hadm_id": int(frame["hadm_id"].nunique()),
        "admission_duration_days": {
            "min": float(duration.min()), "median": float(duration.median()), "max": float(duration.max())
        },
        "missing": {column: int(frame[column].isna().sum()) for column in frame.columns},
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", type=Path, default=DATA)
    parser.add_argument("--output", type=Path, default=OUT)
    parser.add_argument("--chunksize", type=int, default=500_000)
    args = parser.parse_args()
    data = args.data_dir.resolve()
    result = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "data_dir": str(data),
        "read_only": True,
        "admissions": analyse_admissions(data / "admissions.csv.gz"),
        "labevents": analyse_labs(data / "labevents.csv.gz", args.chunksize),
        "diagnoses_icd": analyse_diagnoses(data / "diagnoses_icd.csv.gz", args.chunksize),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote: {args.output}")


if __name__ == "__main__":
    main()
