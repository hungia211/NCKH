"""Convert Phase 1 JSON outputs into reader-friendly CSV tables."""

from __future__ import annotations

import csv
import gzip
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
PHASE_DIR = ROOT / "phases" / "phase1_data_exploration"
JSON_DIR = PHASE_DIR / "outputs" / "machine_readable"
TABLE_DIR = PHASE_DIR / "outputs" / "tables"
HOSP_DIR = ROOT / "data" / "hosp"


def load_json(name: str) -> dict:
    return json.loads((JSON_DIR / name).read_text(encoding="utf-8"))


def write_csv(name: str, headers: list[str], rows: list[list[object]]) -> None:
    TABLE_DIR.mkdir(parents=True, exist_ok=True)
    with (TABLE_DIR / name).open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(headers)
        writer.writerows(rows)


def read_dictionary(path: Path, key_fields: tuple[str, ...]) -> dict[tuple[str, ...], dict[str, str]]:
    with gzip.open(path, "rt", encoding="utf-8", newline="") as handle:
        return {
            tuple(row[field] for field in key_fields): row
            for row in csv.DictReader(handle)
        }


def main() -> None:
    inventory = load_json("hosp_inventory.json")
    core = load_json("core_summary.json")

    inventory_rows = []
    schema_rows = []
    for table in inventory["tables"]:
        inventory_rows.append([
            table["table"], table["row_count"], table["column_count"],
            table["compressed_bytes"], table["file"],
        ])
        schema_rows.extend(
            [table["table"], position, column]
            for position, column in enumerate(table["columns"], start=1)
        )
    write_csv(
        "table_inventory.csv",
        ["table", "row_count", "column_count", "compressed_bytes", "source_file"],
        inventory_rows,
    )
    write_csv("table_schema.csv", ["table", "column_position", "column_name"], schema_rows)

    summary_rows = [
        ["admissions", "rows", core["admissions"]["rows"]],
        ["admissions", "unique_subject_id", core["admissions"]["unique_subject_id"]],
        ["admissions", "unique_hadm_id", core["admissions"]["unique_hadm_id"]],
        ["admissions", "duration_days_min", core["admissions"]["admission_duration_days"]["min"]],
        ["admissions", "duration_days_median", core["admissions"]["admission_duration_days"]["median"]],
        ["admissions", "duration_days_max", core["admissions"]["admission_duration_days"]["max"]],
        ["labevents", "rows", core["labevents"]["rows"]],
        ["labevents", "unique_subject_id", core["labevents"]["unique_subject_id"]],
        ["labevents", "unique_hadm_id_non_null", core["labevents"]["unique_hadm_id_non_null"]],
        ["labevents", "unique_itemid", core["labevents"]["unique_itemid"]],
        ["labevents", "items_with_multiple_units", core["labevents"]["items_with_multiple_units"]],
        ["diagnoses_icd", "rows", core["diagnoses_icd"]["rows"]],
        ["diagnoses_icd", "unique_subject_id", core["diagnoses_icd"]["unique_subject_id"]],
        ["diagnoses_icd", "unique_hadm_id", core["diagnoses_icd"]["unique_hadm_id"]],
        ["diagnoses_icd", "unique_icd_code_version_pairs", core["diagnoses_icd"]["unique_icd_code_version_pairs"]],
        ["diagnoses_icd", "diagnoses_per_admission_min", core["diagnoses_icd"]["diagnoses_per_admission"]["min"]],
        ["diagnoses_icd", "diagnoses_per_admission_mean", core["diagnoses_icd"]["diagnoses_per_admission"]["mean"]],
        ["diagnoses_icd", "diagnoses_per_admission_max", core["diagnoses_icd"]["diagnoses_per_admission"]["max"]],
    ]
    write_csv("core_summary.csv", ["source_table", "metric", "value"], summary_rows)

    missing_rows = []
    for column, count in core["admissions"]["missing"].items():
        missing_rows.append(["admissions", column, count, count / core["admissions"]["rows"]])
    lab_missing_name = {
        "missing_hadm_id": "hadm_id", "missing_valuenum": "valuenum", "missing_valueuom": "valueuom"
    }
    for metric, count in core["labevents"]["missing"].items():
        missing_rows.append(["labevents", lab_missing_name[metric], count, count / core["labevents"]["rows"]])
    write_csv("missingness.csv", ["source_table", "column", "missing_count", "missing_rate"], missing_rows)

    lab_dictionary = read_dictionary(HOSP_DIR / "d_labitems.csv.gz", ("itemid",))
    lab_rows = []
    for rank, item in enumerate(core["labevents"]["top_itemid"], start=1):
        detail = lab_dictionary.get((str(item["itemid"]),), {})
        lab_rows.append([
            rank, item["itemid"], detail.get("label", ""), detail.get("fluid", ""),
            detail.get("category", ""), item["rows"], item["rows"] / core["labevents"]["rows"],
        ])
    write_csv(
        "top_lab_items.csv",
        ["rank", "itemid", "label", "fluid", "category", "row_count", "share_of_labevents"],
        lab_rows,
    )

    icd_dictionary = read_dictionary(HOSP_DIR / "d_icd_diagnoses.csv.gz", ("icd_code", "icd_version"))
    icd_rows = []
    for rank, item in enumerate(core["diagnoses_icd"]["top_icd_code_version"], start=1):
        key = (str(item["icd_code"]), str(item["icd_version"]))
        detail = icd_dictionary.get(key, {})
        icd_rows.append([
            rank, item["icd_version"], item["icd_code"], detail.get("long_title", ""),
            item["rows"], item["rows"] / core["diagnoses_icd"]["rows"],
        ])
    write_csv(
        "top_icd_codes.csv",
        ["rank", "icd_version", "icd_code", "long_title", "row_count", "share_of_diagnoses"],
        icd_rows,
    )
    print(f"Wrote readable tables to: {TABLE_DIR}")


if __name__ == "__main__":
    main()
