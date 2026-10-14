import json
import subprocess
import sys
import tempfile
from pathlib import Path

import pandas as pd


def main() -> None:
    script = Path(__file__).resolve().parents[1] / "scripts" / "run_analysis.py"
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp); data = root / "data"; data.mkdir(); out = root / "out"
        pd.DataFrame([[1, 10], [2, 20]], columns=["subject_id", "hadm_id"]).to_csv(data / "admissions.csv.gz", index=False)
        pd.DataFrame([["001", 9, "A"], ["A01", 10, "B"]], columns=["icd_code", "icd_version", "long_title"]).to_csv(data / "d_icd_diagnoses.csv.gz", index=False)
        rows = [[1, 10, 1, "001", 9], [1, 10, 2, "001", 9], [2, 20, 1, "A01", 10], [2, 10, 3, "001", 9], [1, 10, 4, "ZZZ", 10], [1, 10, None, None, None]]
        pd.DataFrame(rows, columns=["subject_id", "hadm_id", "seq_num", "icd_code", "icd_version"]).to_csv(data / "diagnoses_icd.csv.gz", index=False)
        subprocess.run([sys.executable, str(script), "--data-dir", str(data), "--output-dir", str(out), "--chunksize", "2"], check=True)
        result = json.loads((out / "results.json").read_text(encoding="utf-8"))
        assert result["counts"]["rows"] == 6
        assert result["counts"]["usable_diagnosis_row"] == 3
        assert result["duplicate_usable_rows_within_admission"] == 1
        assert result["usable_admissions"] == 2
        assert result["unique_complete_codes_by_version"] == {"9": 1, "10": 2}
        print("PASS task04")


if __name__ == "__main__": main()
