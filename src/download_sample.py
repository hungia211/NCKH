from pathlib import Path
from urllib.request import urlretrieve

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]

CSV_PATH = PROJECT_ROOT / "data" / "metadata" / "record_list.csv"
OUTPUT_DIR = PROJECT_ROOT / "data" / "raw" / "sample_ecg"
BASE_URL = "https://physionet.org/files/mimic-iv-ecg/1.0"


def main() -> None:
    if not CSV_PATH.exists():
        raise FileNotFoundError(f"Không tìm thấy: {CSV_PATH}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    records = pd.read_csv(CSV_PATH, nrows=1)
    row = records.iloc[0]

    print("Các cột:", records.columns.tolist())
    print("\nDòng được chọn:")
    print(row)

    record_path = str(row["path"]).strip().lstrip("/").replace("\\", "/")

    if "file_name" in records.columns and pd.notna(row["file_name"]):
        record_name = str(row["file_name"]).strip()
    else:
        record_name = str(row["study_id"]).strip()

    # Một số file metadata lưu path tới record, không chỉ thư mục.
    if record_path.endswith(f"/{record_name}"):
        record_directory = record_path.rsplit("/", 1)[0]
    else:
        record_directory = record_path

    for extension in ("hea", "dat"):
        url = (
            f"{BASE_URL}/"
            f"{record_directory}/"
            f"{record_name}.{extension}"
        )

        destination = OUTPUT_DIR / f"{record_name}.{extension}"

        print(f"\nĐang tải: {url}")
        urlretrieve(url, destination)
        print(f"Đã lưu: {destination}")

    print("\nTải ECG mẫu thành công.")


if __name__ == "__main__":
    main()
