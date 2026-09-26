"""Phase 1 inventory for the local MIMIC-IV v3.1 HOSP module.

This script is read-only. It scans gzip CSV headers and row counts and writes
a compact inventory so later cohort decisions are based on observed data.
"""

from __future__ import annotations

import argparse
import csv
import gzip
import json
from datetime import datetime, timezone
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_DATA_DIR = PROJECT_ROOT / "data" / "hosp"
DEFAULT_OUTPUT = (
    PROJECT_ROOT
    / "phases"
    / "phase1_data_exploration"
    / "outputs"
    / "machine_readable"
    / "hosp_inventory.json"
)


def inspect_csv_gz(path: Path) -> dict[str, object]:
    with gzip.open(path, "rt", encoding="utf-8", newline="") as handle:
        reader = csv.reader(handle)
        columns = next(reader)
        row_count = sum(1 for _ in reader)
    return {
        "table": path.name.removesuffix(".csv.gz"),
        "file": str(path),
        "compressed_bytes": path.stat().st_size,
        "row_count": row_count,
        "column_count": len(columns),
        "columns": columns,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", type=Path, default=DEFAULT_DATA_DIR)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    data_dir = args.data_dir.resolve()
    if not data_dir.is_dir():
        raise SystemExit(f"Data directory does not exist: {data_dir}")

    files = sorted(data_dir.glob("*.csv.gz"))
    if not files:
        raise SystemExit(f"No .csv.gz files found in: {data_dir}")

    tables = []
    for index, path in enumerate(files, start=1):
        print(f"[{index}/{len(files)}] {path.name}", flush=True)
        tables.append(inspect_csv_gz(path))

    payload = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "data_dir": str(data_dir),
        "read_only": True,
        "tables": tables,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote: {args.output}")


if __name__ == "__main__":
    main()
