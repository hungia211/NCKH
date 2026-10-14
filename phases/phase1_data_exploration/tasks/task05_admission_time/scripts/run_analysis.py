"""Task 5 full-data survey of admission and laboratory event timing.

The script reads MIMIC-IV HOSP source files without modifying them. It only
uses laboratory rows with an existing, valid hadm_id and never imputes a
missing hadm_id.
"""
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
WINDOWS = (6, 12, 24)


def nonempty(series: pd.Series) -> pd.Series:
    return series.notna() & series.astype("string").str.strip().ne("")


def quantiles(values: np.ndarray) -> dict[str, float | int]:
    values = values[np.isfinite(values)]
    if not values.size:
        return {}
    return {
        "min": float(values.min()), "p25": float(np.quantile(values, 0.25)),
        "median": float(np.quantile(values, 0.5)), "p75": float(np.quantile(values, 0.75)),
        "p90": float(np.quantile(values, 0.9)), "p95": float(np.quantile(values, 0.95)),
        "p99": float(np.quantile(values, 0.99)), "max": float(values.max()),
        "mean": float(values.mean()),
    }


def add_by_position(target: np.ndarray, positions: np.ndarray, mask: np.ndarray) -> None:
    if mask.any():
        np.add.at(target, positions[mask], 1)


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

    admissions = pd.read_csv(
        paths["admissions"],
        usecols=["subject_id", "hadm_id", "admittime", "dischtime", "edregtime", "edouttime"],
        dtype={"subject_id": "Int64", "hadm_id": "Int64", "admittime": "string", "dischtime": "string", "edregtime": "string", "edouttime": "string"},
    )
    if admissions["hadm_id"].isna().any() or admissions["hadm_id"].duplicated().any():
        raise SystemExit("admissions.hadm_id must be complete and unique")
    admissions["admittime_parsed"] = pd.to_datetime(admissions["admittime"], format="%Y-%m-%d %H:%M:%S", errors="coerce")
    admissions["dischtime_parsed"] = pd.to_datetime(admissions["dischtime"], format="%Y-%m-%d %H:%M:%S", errors="coerce")
    duration_hours = (admissions["dischtime_parsed"] - admissions["admittime_parsed"]).dt.total_seconds() / 3600
    admissions["duration_hours"] = duration_hours
    admissions["time_complete"] = admissions[["admittime_parsed", "dischtime_parsed"]].notna().all(axis=1)
    admissions["time_interval_valid"] = admissions["time_complete"] & duration_hours.ge(0)

    n_adm = len(admissions)
    hadm_values = admissions["hadm_id"].astype("int64").to_numpy()
    subject_values = admissions["subject_id"].astype("int64").to_numpy()
    position_by_hadm = pd.Series(np.arange(n_adm, dtype=np.int64), index=hadm_values)
    owner_by_hadm = pd.Series(subject_values, index=hadm_values)
    admit_values = admissions["admittime_parsed"].to_numpy(dtype="datetime64[ns]")
    discharge_values = admissions["dischtime_parsed"].to_numpy(dtype="datetime64[ns]")
    valid_interval_values = admissions["time_interval_valid"].to_numpy(dtype=bool)

    labitems = pd.read_csv(paths["d_labitems"], usecols=["itemid"], dtype={"itemid": "Int64"})
    if labitems["itemid"].isna().any() or labitems["itemid"].duplicated().any():
        raise SystemExit("d_labitems.itemid must be complete and unique")
    valid_itemids = set(labitems["itemid"].astype(int))

    admission_counts = {name: np.zeros(n_adm, dtype=np.int64) for name in (
        "candidate_rows", "before_admission_rows", "during_admission_rows", "after_discharge_rows",
        "invalid_interval_rows", "within_6h_rows", "within_12h_rows", "within_24h_rows",
    )}
    first_in_admission_hour = np.full(n_adm, np.nan)
    last_in_admission_hour = np.full(n_adm, np.nan)
    counts: Counter[str] = Counter()
    relative_bins: Counter[str] = Counter()
    store_lag_bins: Counter[str] = Counter()
    relative_labels = ("before_-24h", "-24_to_-6h", "-6_to_0h", "0_to_6h", "6_to_12h", "12_to_24h", "24_to_72h", "72_to_168h", "after_168h")

    usecols = ["subject_id", "hadm_id", "itemid", "charttime", "storetime", "value", "valuenum"]
    dtype = {"subject_id": "Int64", "hadm_id": "Int64", "itemid": "Int64", "charttime": "string", "storetime": "string", "value": "string"}
    for chunk_number, frame in enumerate(pd.read_csv(paths["labevents"], usecols=usecols, dtype=dtype, chunksize=args.chunksize), start=1):
        counts["source_rows"] += len(frame)
        subject_present = frame["subject_id"].notna(); hadm_present = frame["hadm_id"].notna(); item_present = frame["itemid"].notna()
        expected_subject = frame["hadm_id"].map(owner_by_hadm)
        known_admission = hadm_present & expected_subject.notna()
        subject_match = subject_present & known_admission & frame["subject_id"].eq(expected_subject)
        item_match = item_present & frame["itemid"].isin(valid_itemids)
        chart = pd.to_datetime(frame["charttime"], format="%Y-%m-%d %H:%M:%S", errors="coerce")
        result_present = frame["valuenum"].notna() | nonempty(frame["value"])
        candidate = subject_match & item_match & chart.notna() & result_present

        counts["rows_with_hadm_id"] += int(hadm_present.sum())
        counts["candidate_rows"] += int(candidate.sum())
        if not candidate.any():
            continue

        positions = frame.loc[candidate, "hadm_id"].map(position_by_hadm).astype("int64").to_numpy()
        chart_candidate = chart.loc[candidate]
        chart_values = chart_candidate.to_numpy(dtype="datetime64[ns]")
        delta_hours = (chart_values - admit_values[positions]) / np.timedelta64(1, "h")
        valid_interval = valid_interval_values[positions]
        before = valid_interval & (chart_values < admit_values[positions])
        during = valid_interval & (chart_values >= admit_values[positions]) & (chart_values <= discharge_values[positions])
        after = valid_interval & (chart_values > discharge_values[positions])
        invalid_interval = ~valid_interval

        add_by_position(admission_counts["candidate_rows"], positions, np.ones(len(positions), dtype=bool))
        add_by_position(admission_counts["before_admission_rows"], positions, before)
        add_by_position(admission_counts["during_admission_rows"], positions, during)
        add_by_position(admission_counts["after_discharge_rows"], positions, after)
        add_by_position(admission_counts["invalid_interval_rows"], positions, invalid_interval)
        counts["before_admission_rows"] += int(before.sum())
        counts["during_admission_rows"] += int(during.sum())
        counts["after_discharge_rows"] += int(after.sum())
        counts["invalid_interval_rows"] += int(invalid_interval.sum())

        for hours in WINDOWS:
            within = during & (delta_hours < hours)
            add_by_position(admission_counts[f"within_{hours}h_rows"], positions, within)
            counts[f"within_{hours}h_rows"] += int(within.sum())

        if during.any():
            temp = pd.DataFrame({"position": positions[during], "delta": delta_hours[during]})
            grouped = temp.groupby("position")["delta"].agg(["min", "max"])
            idx = grouped.index.to_numpy(dtype=np.int64)
            group_min = grouped["min"].to_numpy(); group_max = grouped["max"].to_numpy()
            current_first = first_in_admission_hour[idx]
            first_in_admission_hour[idx] = np.where(np.isnan(current_first), group_min, np.minimum(current_first, group_min))
            current_last = last_in_admission_hour[idx]
            last_in_admission_hour[idx] = np.where(np.isnan(current_last), group_max, np.maximum(current_last, group_max))

        rel = delta_hours[valid_interval]
        if rel.size:
            cut = pd.cut(rel, bins=[-np.inf, -24, -6, 0, 6, 12, 24, 72, 168, np.inf], right=False, labels=relative_labels)
            relative_bins.update({str(k): int(v) for k, v in pd.Series(cut).value_counts(sort=False).items()})

        store_text = frame.loc[candidate, "storetime"]
        store_present = nonempty(store_text)
        store = pd.to_datetime(store_text, format="%Y-%m-%d %H:%M:%S", errors="coerce")
        store_valid = store.notna()
        counts["candidate_missing_storetime"] += int((~store_present).sum())
        counts["candidate_invalid_storetime_nonempty"] += int((store_present & ~store_valid).sum())
        if store_valid.any():
            lag = (store.loc[store_valid].to_numpy(dtype="datetime64[ns]") - chart_candidate.loc[store_valid].to_numpy(dtype="datetime64[ns]")) / np.timedelta64(1, "h")
            labels = np.select(
                [lag < 0, lag == 0, (lag > 0) & (lag <= 1), (lag > 1) & (lag <= 6), (lag > 6) & (lag <= 24), lag > 24],
                ["before_charttime", "same_time", "0_to_1h", "1_to_6h", "6_to_24h", "after_24h"], default="unclassified",
            )
            store_lag_bins.update(Counter(labels.tolist()))
            counts["candidate_storetime_before_charttime"] += int((lag < 0).sum())

        if chunk_number % 20 == 0:
            print(f"labevents chunks={chunk_number} rows={counts['source_rows']:,}", flush=True)

    profile = admissions[["subject_id", "hadm_id", "admittime", "dischtime", "edregtime", "edouttime", "duration_hours", "time_complete", "time_interval_valid"]].copy()
    for name, values in admission_counts.items(): profile[name] = values
    profile["first_in_admission_hour"] = first_in_admission_hour
    profile["last_in_admission_hour"] = last_in_admission_hour
    profile.to_csv(output_dir / "admission_time_profile.csv", index=False, encoding="utf-8-sig")

    window_rows = []
    for hours in WINDOWS:
        values = admission_counts[f"within_{hours}h_rows"]
        window_rows.append({
            "window_hours": hours, "boundary_rule": f"0 <= delta_hours < {hours} and charttime <= dischtime",
            "lab_rows": int(values.sum()), "admissions_with_lab": int((values > 0).sum()),
            "share_candidate_rows": float(values.sum() / counts["candidate_rows"]),
            "share_all_admissions": float((values > 0).sum() / n_adm),
            "admissions_discharged_before_window": int((admissions["time_interval_valid"] & duration_hours.lt(hours)).sum()),
        })
    pd.DataFrame(window_rows).to_csv(output_dir / "window_coverage.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame([{"time_bin": label, "rows": relative_bins[label], "share_candidate_rows": relative_bins[label] / counts["candidate_rows"]} for label in relative_labels]).to_csv(output_dir / "lab_time_distribution.csv", index=False, encoding="utf-8-sig")
    lag_order = ("before_charttime", "same_time", "0_to_1h", "1_to_6h", "6_to_24h", "after_24h", "unclassified")
    valid_store_total = sum(store_lag_bins.values())
    pd.DataFrame([{"storetime_lag_bin": label, "rows": store_lag_bins[label], "share_valid_storetime": store_lag_bins[label] / valid_store_total if valid_store_total else 0} for label in lag_order]).to_csv(output_dir / "storetime_lag_distribution.csv", index=False, encoding="utf-8-sig")

    duration_valid = duration_hours[admissions["time_interval_valid"]].to_numpy(dtype=float)
    candidate_admissions = admission_counts["candidate_rows"] > 0
    manifest = []
    for path in paths.values():
        stat = path.stat(); manifest.append({"path": str(path), "bytes": stat.st_size, "mtime_ns": stat.st_mtime_ns})
    summary = {
        "task": 5, "started_utc": started.isoformat(), "finished_utc": datetime.now(timezone.utc).isoformat(),
        "read_only": True, "missing_hadm_policy": "exclude; do not recover or infer",
        "candidate_definition": "Task 3 definition: valid hadm_id and matching subject; dictionary item; parseable charttime; numeric or non-empty text result",
        "window_definition": "descriptive half-open windows from admittime; row must also be within a non-negative admission interval",
        "inputs": manifest, "counts": dict(counts), "admissions": n_adm,
        "unique_subjects": int(admissions["subject_id"].nunique()),
        "subjects_with_multiple_admissions": int((admissions.groupby("subject_id").size() > 1).sum()),
        "missing_admittime": int(admissions["admittime_parsed"].isna().sum()),
        "missing_dischtime": int(admissions["dischtime_parsed"].isna().sum()),
        "negative_duration_admissions": int((admissions["time_complete"] & duration_hours.lt(0)).sum()),
        "zero_duration_admissions": int((admissions["time_complete"] & duration_hours.eq(0)).sum()),
        "valid_interval_admissions": int(admissions["time_interval_valid"].sum()),
        "candidate_admissions": int(candidate_admissions.sum()),
        "candidate_admissions_with_during_lab": int((admission_counts["during_admission_rows"] > 0).sum()),
        "candidate_admissions_only_outside_valid_interval": int((candidate_admissions & (admission_counts["during_admission_rows"] == 0)).sum()),
        "admission_duration_hours": quantiles(duration_valid),
        "first_in_admission_lab_hour": quantiles(first_in_admission_hour[np.isfinite(first_in_admission_hour)]),
        "window_coverage": window_rows,
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "runtime": {"python": platform.python_version(), "pandas": pd.__version__, "numpy": np.__version__},
        "source_rows_removed": 0,
    }
    (output_dir / "results.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"OUTPUT {output_dir}", flush=True)


if __name__ == "__main__":
    main()
