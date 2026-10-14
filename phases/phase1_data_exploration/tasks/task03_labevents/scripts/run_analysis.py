"""Task 3 full-data exploration of MIMIC-IV HOSP labevents.

The script reads source files only and writes a new timestamped output folder.
It measures candidate usability without deleting or correcting source rows.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "AGENTS.md").is_file())
TASK_DIR = Path(__file__).resolve().parents[1]


class UniqueInt64Accumulator:
    """Logarithmic merging of sorted unique int64 arrays."""

    def __init__(self) -> None:
        self.levels: list[np.ndarray | None] = []

    def add(self, values: np.ndarray) -> None:
        current = np.unique(values.astype(np.int64, copy=False))
        level = 0
        while current.size:
            if level == len(self.levels):
                self.levels.append(current)
                return
            if self.levels[level] is None:
                self.levels[level] = current
                return
            current = np.union1d(self.levels[level], current)
            self.levels[level] = None
            level += 1

    def finish(self) -> np.ndarray:
        arrays = [array for array in self.levels if array is not None and array.size]
        return np.unique(np.concatenate(arrays)) if arrays else np.array([], dtype=np.int64)


def nonempty(series: pd.Series) -> pd.Series:
    return series.notna() & series.astype("string").str.strip().ne("")


def update_counter(counter: Counter, series: pd.Series) -> None:
    counter.update({int(key): int(value) for key, value in series.items()})


def quantiles(values: list[int]) -> dict[str, float | int]:
    array = np.asarray(values, dtype=np.int64)
    if not array.size:
        return {}
    return {
        "min": int(array.min()), "p25": float(np.quantile(array, 0.25)),
        "median": float(np.quantile(array, 0.5)), "p75": float(np.quantile(array, 0.75)),
        "p90": float(np.quantile(array, 0.9)), "p95": float(np.quantile(array, 0.95)),
        "p99": float(np.quantile(array, 0.99)), "max": int(array.max()), "mean": float(array.mean()),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", type=Path, default=ROOT / "data" / "hosp")
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--chunksize", type=int, default=500_000)
    args = parser.parse_args()
    started = datetime.now(timezone.utc)
    output_dir = args.output_dir or TASK_DIR / "outputs" / started.strftime("%Y%m%dT%H%M%SZ")
    output_dir.mkdir(parents=True, exist_ok=False)
    data_dir = args.data_dir.resolve()
    paths = {name: data_dir / f"{name}.csv.gz" for name in ("admissions", "d_labitems", "labevents")}
    if not all(path.is_file() for path in paths.values()):
        raise SystemExit(f"Missing required input under {data_dir}")

    admissions = pd.read_csv(paths["admissions"], usecols=["hadm_id", "subject_id"])
    if admissions["hadm_id"].isna().any() or admissions["hadm_id"].duplicated().any():
        raise SystemExit("admissions.hadm_id must be complete and unique")
    owners = admissions.set_index("hadm_id")["subject_id"]
    labitems = pd.read_csv(paths["d_labitems"], dtype={"itemid": "Int64"})
    if labitems["itemid"].isna().any() or labitems["itemid"].duplicated().any():
        raise SystemExit("d_labitems.itemid must be complete and unique")
    item_ids = set(labitems["itemid"].astype(int))
    item_meta = labitems.set_index("itemid").to_dict("index")

    counts: Counter[str] = Counter()
    subjects: set[int] = set()
    admissions_non_null: set[int] = set()
    observed_items: set[int] = set()
    item_counts: dict[str, Counter[int]] = defaultdict(Counter)
    item_numeric_min: dict[int, float] = {}
    item_numeric_max: dict[int, float] = {}
    unit_counts: Counter[tuple[int, str]] = Counter()
    admission_candidate_counts: Counter[int] = Counter()
    candidate_pairs = UniqueInt64Accumulator()

    usecols = ["subject_id", "hadm_id", "itemid", "charttime", "storetime", "value", "valuenum", "valueuom", "ref_range_lower", "ref_range_upper", "flag"]
    dtype = {"value": "string", "valueuom": "string", "flag": "string", "charttime": "string", "storetime": "string"}
    for chunk_number, frame in enumerate(pd.read_csv(paths["labevents"], usecols=usecols, dtype=dtype, chunksize=args.chunksize), start=1):
        counts["rows"] += len(frame)
        subjects.update(frame["subject_id"].dropna().astype("int64").tolist())
        admissions_non_null.update(frame["hadm_id"].dropna().astype("int64").tolist())
        observed_items.update(frame["itemid"].dropna().astype("int64").tolist())

        subject_present = frame["subject_id"].notna(); hadm_present = frame["hadm_id"].notna(); item_present = frame["itemid"].notna()
        complete_keys = subject_present & hadm_present & item_present
        expected_subject = frame["hadm_id"].map(owners)
        known_admission = complete_keys & expected_subject.notna()
        subject_match = known_admission & frame["subject_id"].eq(expected_subject)
        dictionary_match = item_present & frame["itemid"].isin(item_ids)
        chart_present = nonempty(frame["charttime"])
        chart_valid = pd.to_datetime(frame["charttime"], format="%Y-%m-%d %H:%M:%S", errors="coerce").notna()
        store_present = nonempty(frame["storetime"])
        numeric_result = frame["valuenum"].notna(); text_result = nonempty(frame["value"])
        text_only = ~numeric_result & text_result; result_present = numeric_result | text_result
        unit_present = nonempty(frame["valueuom"]); flag_present = nonempty(frame["flag"])
        lower_present = frame["ref_range_lower"].notna(); upper_present = frame["ref_range_upper"].notna()
        matched_dictionary = subject_match & dictionary_match
        candidate = matched_dictionary & chart_valid & result_present

        metrics = {
            "missing_subject_id": ~subject_present, "missing_hadm_id": ~hadm_present, "missing_itemid": ~item_present,
            "complete_subject_hadm_item": complete_keys, "known_admission_after_complete_keys": known_admission,
            "subject_match_after_known_admission": subject_match,
            "subject_mismatch_after_known_admission": known_admission & ~frame["subject_id"].eq(expected_subject),
            "dictionary_match": dictionary_match, "matched_admission_subject_and_dictionary": matched_dictionary,
            "missing_charttime": ~chart_present, "invalid_charttime_nonempty": chart_present & ~chart_valid,
            "missing_storetime": ~store_present, "numeric_result": numeric_result, "text_only_result": text_only,
            "no_numeric_or_text_result": ~result_present, "missing_valueuom": ~unit_present, "has_flag": flag_present,
            "has_both_reference_bounds": lower_present & upper_present, "candidate_usable_row": candidate,
            "candidate_numeric_row": candidate & numeric_result, "candidate_text_only_row": candidate & text_only,
        }
        for name, mask in metrics.items(): counts[name] += int(mask.sum())

        masks_by_name = {
            "rows": item_present, "admission_subject_matched_rows": item_present & subject_match,
            "candidate_rows": item_present & candidate, "numeric_rows": item_present & numeric_result,
            "text_only_rows": item_present & text_only, "no_result_rows": item_present & ~result_present,
            "missing_charttime_rows": item_present & ~chart_present, "missing_valueuom_rows": item_present & ~unit_present,
        }
        for name, mask in masks_by_name.items(): update_counter(item_counts[name], frame.loc[mask].groupby("itemid", observed=True).size())

        numeric_frame = frame.loc[item_present & numeric_result, ["itemid", "valuenum"]]
        if not numeric_frame.empty:
            grouped = numeric_frame.groupby("itemid", observed=True)["valuenum"].agg(["min", "max"])
            for itemid, row in grouped.iterrows():
                key = int(itemid)
                item_numeric_min[key] = min(item_numeric_min.get(key, float("inf")), float(row["min"]))
                item_numeric_max[key] = max(item_numeric_max.get(key, float("-inf")), float(row["max"]))

        units = frame.loc[item_present & unit_present, ["itemid", "valueuom"]].copy()
        if not units.empty:
            units["valueuom"] = units["valueuom"].str.strip()
            grouped_units = units.groupby(["itemid", "valueuom"], observed=True).size()
            unit_counts.update({(int(itemid), str(unit)): int(value) for (itemid, unit), value in grouped_units.items()})

        candidate_frame = frame.loc[candidate, ["hadm_id", "itemid"]].astype("int64")
        if not candidate_frame.empty:
            update_counter(admission_candidate_counts, candidate_frame.groupby("hadm_id").size())
            encoded = (candidate_frame["itemid"].to_numpy(dtype=np.int64) << np.int64(32)) | candidate_frame["hadm_id"].to_numpy(dtype=np.int64)
            candidate_pairs.add(encoded)
        if chunk_number % 20 == 0: print(f"labevents chunks={chunk_number} rows={counts['rows']:,}", flush=True)

    unique_pairs = candidate_pairs.finish()
    candidate_admissions_by_item: Counter[int] = Counter()
    if unique_pairs.size:
        keys, values = np.unique(unique_pairs >> np.int64(32), return_counts=True)
        candidate_admissions_by_item.update({int(k): int(v) for k, v in zip(keys, values)})
    units_by_item: dict[int, list[tuple[str, int]]] = defaultdict(list)
    for (itemid, unit), row_count in unit_counts.items(): units_by_item[itemid].append((unit, row_count))
    item_rows = []
    for itemid in sorted(observed_items):
        meta = item_meta.get(itemid, {}); unit_list = sorted(units_by_item.get(itemid, []), key=lambda pair: (-pair[1], pair[0]))
        total = item_counts["rows"][itemid]; candidate_rows = item_counts["candidate_rows"][itemid]
        item_rows.append({
            "itemid": itemid, "label": meta.get("label", ""), "fluid": meta.get("fluid", ""), "category": meta.get("category", ""),
            "rows": total, "candidate_rows": candidate_rows, "candidate_row_rate": candidate_rows / total if total else 0,
            "candidate_admissions": candidate_admissions_by_item[itemid],
            "admission_subject_matched_rows": item_counts["admission_subject_matched_rows"][itemid],
            "numeric_rows": item_counts["numeric_rows"][itemid], "text_only_rows": item_counts["text_only_rows"][itemid],
            "no_result_rows": item_counts["no_result_rows"][itemid], "missing_charttime_rows": item_counts["missing_charttime_rows"][itemid],
            "missing_valueuom_rows": item_counts["missing_valueuom_rows"][itemid], "distinct_units": len(unit_list),
            "most_common_unit": unit_list[0][0] if unit_list else "", "numeric_min_observed": item_numeric_min.get(itemid),
            "numeric_max_observed": item_numeric_max.get(itemid), "dictionary_match": itemid in item_ids,
        })
    unit_rows = [{"itemid": itemid, "label": item_meta.get(itemid, {}).get("label", ""), "valueuom": unit, "rows": row_count}
                 for (itemid, unit), row_count in sorted(unit_counts.items(), key=lambda pair: (pair[0][0], -pair[1], pair[0][1]))]
    manifest = []
    for path in paths.values():
        stat = path.stat(); manifest.append({"path": str(path), "bytes": stat.st_size, "mtime_ns": stat.st_mtime_ns})
    summary = {
        "task": 3, "started_utc": started.isoformat(), "finished_utc": datetime.now(timezone.utc).isoformat(), "read_only": True,
        "candidate_definition": "subject_id, hadm_id and itemid present; hadm_id exists in admissions; subject_id matches admission owner; itemid exists in d_labitems; charttime parses; valuenum or non-empty value exists",
        "inputs": manifest, "counts": dict(counts), "unique_subject_id": len(subjects), "unique_hadm_id_non_null": len(admissions_non_null),
        "unique_itemid_observed": len(observed_items), "candidate_admissions": len(admission_candidate_counts),
        "candidate_itemids": sum(1 for row in item_rows if row["candidate_rows"] > 0),
        "items_with_multiple_observed_units": sum(1 for row in item_rows if row["distinct_units"] > 1),
        "candidate_measurements_per_admission": quantiles(list(admission_candidate_counts.values())),
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "runtime": {"python": platform.python_version(), "pandas": pd.__version__, "numpy": np.__version__},
    }
    pd.DataFrame(item_rows).sort_values(["candidate_admissions", "candidate_rows"], ascending=False).to_csv(output_dir / "lab_item_profile.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame(unit_rows).to_csv(output_dir / "lab_unit_profile.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame([{"metric": key, "count": value, "rate_of_all_rows": value / counts["rows"]} for key, value in counts.items()]).to_csv(output_dir / "row_usability_funnel.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame([{"statistic": key, "value": value} for key, value in summary["candidate_measurements_per_admission"].items()]).to_csv(output_dir / "measurements_per_admission.csv", index=False, encoding="utf-8-sig")
    (output_dir / "results.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"OUTPUT {output_dir}", flush=True)


if __name__ == "__main__": main()
