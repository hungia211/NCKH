from pathlib import Path
import gzip
import importlib.util
import json
import sys
import tempfile
import unittest
from unittest.mock import patch

import pandas as pd


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "run_analysis.py"


def write_gz(frame: pd.DataFrame, path: Path) -> None:
    with gzip.open(path, "wt", encoding="utf-8", newline="") as handle:
        frame.to_csv(handle, index=False)


class Task05TimeTest(unittest.TestCase):
    def test_time_categories_and_windows(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder); data = root / "hosp"; data.mkdir(); out = root / "out"
            write_gz(pd.DataFrame([
                {"subject_id": 1, "hadm_id": 10, "admittime": "2020-01-01 00:00:00", "dischtime": "2020-01-02 00:00:00", "edregtime": "", "edouttime": ""},
                {"subject_id": 2, "hadm_id": 20, "admittime": "2020-01-03 00:00:00", "dischtime": "2020-01-02 00:00:00", "edregtime": "", "edouttime": ""},
            ]), data / "admissions.csv.gz")
            write_gz(pd.DataFrame([{"itemid": 100}]), data / "d_labitems.csv.gz")
            write_gz(pd.DataFrame([
                {"subject_id": 1, "hadm_id": 10, "itemid": 100, "charttime": "2019-12-31 23:00:00", "storetime": "2020-01-01 00:00:00", "value": "1", "valuenum": 1},
                {"subject_id": 1, "hadm_id": 10, "itemid": 100, "charttime": "2020-01-01 05:00:00", "storetime": "2020-01-01 06:00:00", "value": "2", "valuenum": 2},
                {"subject_id": 1, "hadm_id": 10, "itemid": 100, "charttime": "2020-01-02 01:00:00", "storetime": "2020-01-02 02:00:00", "value": "3", "valuenum": 3},
                {"subject_id": 2, "hadm_id": 20, "itemid": 100, "charttime": "2020-01-02 12:00:00", "storetime": "2020-01-02 13:00:00", "value": "4", "valuenum": 4},
                {"subject_id": 1, "hadm_id": None, "itemid": 100, "charttime": "2020-01-01 02:00:00", "storetime": "2020-01-01 03:00:00", "value": "5", "valuenum": 5},
            ]), data / "labevents.csv.gz")
            spec = importlib.util.spec_from_file_location("task05_run", SCRIPT); module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
            with patch.object(sys, "argv", [str(SCRIPT), "--data-dir", str(data), "--output-dir", str(out), "--chunksize", "2"]): module.main()
            result = json.loads((out / "results.json").read_text(encoding="utf-8"))
            self.assertEqual(result["counts"]["candidate_rows"], 4)
            self.assertEqual(result["counts"]["before_admission_rows"], 1)
            self.assertEqual(result["counts"]["during_admission_rows"], 1)
            self.assertEqual(result["counts"]["after_discharge_rows"], 1)
            self.assertEqual(result["counts"]["invalid_interval_rows"], 1)
            self.assertEqual(result["counts"]["within_6h_rows"], 1)
            self.assertEqual(result["negative_duration_admissions"], 1)


if __name__ == "__main__": unittest.main()
