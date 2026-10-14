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
        pd.DataFrame([[5, "A", "Blood", "Chemistry"], [6, "B", "Blood", "Chemistry"]], columns=["itemid", "label", "fluid", "category"]).to_csv(data / "d_labitems.csv.gz", index=False)
        columns = ["subject_id", "hadm_id", "itemid", "charttime", "storetime", "value", "valuenum", "valueuom", "ref_range_lower", "ref_range_upper", "flag"]
        rows = [
            [1, 10, 5, "2150-01-01 01:00:00", "2150-01-01 02:00:00", "1.2", 1.2, "mg/dL", 1, 2, ""],
            [1, 10, 6, "2150-01-01 01:00:00", "2150-01-01 02:00:00", "NEG", None, "", None, None, ""],
            [1, None, 5, "2150-01-01 01:00:00", "", "2", 2, "mg/dL", None, None, ""],
            [2, 10, 5, "2150-01-01 01:00:00", "", "3", 3, "mg/dL", None, None, ""],
            [1, 10, 99, "2150-01-01 01:00:00", "", "4", 4, "mg/dL", None, None, ""],
            [1, 10, 5, "", "", "5", 5, "mg/dL", None, None, ""],
            [1, 10, 5, "2150-01-01 01:00:00", "", "", None, "mg/dL", None, None, ""],
        ]
        pd.DataFrame(rows, columns=columns).to_csv(data / "labevents.csv.gz", index=False)
        subprocess.run([sys.executable, str(script), "--data-dir", str(data), "--output-dir", str(out), "--chunksize", "2"], check=True)
        result = json.loads((out / "results.json").read_text(encoding="utf-8"))
        assert result["counts"]["rows"] == 7
        assert result["counts"]["candidate_usable_row"] == 2
        assert result["counts"]["candidate_numeric_row"] == 1
        assert result["counts"]["candidate_text_only_row"] == 1
        assert result["candidate_admissions"] == 1
        print("PASS task03")


if __name__ == "__main__": main()
