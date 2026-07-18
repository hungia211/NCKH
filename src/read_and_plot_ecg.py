from __future__ import annotations

import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

MPLCONFIGDIR = PROJECT_ROOT / ".matplotlib-cache"
MPLCONFIGDIR.mkdir(exist_ok=True)
os.environ.setdefault("MPLCONFIGDIR", str(MPLCONFIGDIR))

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import wfdb


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")


# Thư mục chứa 2 file dữ liệu gốc:
#   40689238.hea
#   40689238.dat
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw" / "sample_ecg"
RECORD_NAME = "40689238"

PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
FIGURES_DIR = PROJECT_ROOT / "outputs" / "figures"


def load_ecg() -> wfdb.Record:
    """Đọc một bản ghi ECG WFDB từ cặp file .hea và .dat."""
    record_path = RAW_DATA_DIR / RECORD_NAME
    header_path = record_path.with_suffix(".hea")
    data_path = record_path.with_suffix(".dat")

    if not header_path.exists():
        raise FileNotFoundError(f"Không tìm thấy file: {header_path}")

    if not data_path.exists():
        raise FileNotFoundError(f"Không tìm thấy file: {data_path}")

    return wfdb.rdrecord(str(record_path))


def print_record_information(record: wfdb.Record) -> None:
    """In thông tin cơ bản của ECG ra terminal."""
    duration_seconds = record.sig_len / record.fs

    print("=" * 60)
    print("THÔNG TIN BẢN GHI ECG")
    print("=" * 60)
    print(f"Tên record        : {record.record_name}")
    print(f"Tần số lấy mẫu    : {record.fs} Hz")
    print(f"Số đạo trình      : {record.n_sig}")
    print(f"Số mẫu/đạo trình  : {record.sig_len}")
    print(f"Thời lượng         : {duration_seconds:.2f} giây")
    print(f"Tên đạo trình     : {', '.join(record.sig_name)}")
    print(f"Đơn vị             : {', '.join(record.units)}")
    print(f"Kích thước dữ liệu : {record.p_signal.shape}")
    print("=" * 60)


def export_signal_to_csv(record: wfdb.Record) -> Path:
    """Xuất tín hiệu vật lý ra CSV để dễ quan sát bằng Excel/Pandas."""
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    time_seconds = np.arange(record.sig_len) / record.fs

    dataframe = pd.DataFrame(
        record.p_signal,
        columns=record.sig_name,
    )
    dataframe.insert(0, "time_seconds", time_seconds)

    output_path = PROCESSED_DIR / f"{RECORD_NAME}_signal.csv"
    dataframe.to_csv(output_path, index=False)

    print(f"Đã xuất tín hiệu ra CSV: {output_path}")
    return output_path


def plot_all_leads(record: wfdb.Record) -> Path:
    """Vẽ toàn bộ các đạo trình ECG trên cùng một hình."""
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    time_seconds = np.arange(record.sig_len) / record.fs
    lead_count = record.n_sig

    fig, axes = plt.subplots(
        lead_count,
        1,
        figsize=(15, max(12, lead_count * 1.7)),
        sharex=True,
    )

    if lead_count == 1:
        axes = [axes]

    for index, axis in enumerate(axes):
        axis.plot(time_seconds, record.p_signal[:, index], linewidth=0.8)
        axis.set_ylabel(
            f"{record.sig_name[index]}\n({record.units[index]})"
        )
        axis.grid(True, alpha=0.3)

    axes[-1].set_xlabel("Thời gian (giây)")
    fig.suptitle(
        f"ECG 12 đạo trình - Record {RECORD_NAME}",
        fontsize=14,
    )
    fig.tight_layout(rect=(0, 0, 1, 0.98))

    output_path = FIGURES_DIR / f"{RECORD_NAME}_all_leads.png"
    fig.savefig(output_path, dpi=200, bbox_inches="tight")

    print(f"Đã lưu biểu đồ 12 đạo trình: {output_path}")
    return output_path


def plot_single_lead(
    record: wfdb.Record,
    lead_name: str = "II",
    seconds: float = 10.0,
) -> Path:
    """Vẽ một đạo trình cụ thể trong một khoảng thời gian."""
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    if lead_name not in record.sig_name:
        raise ValueError(
            f"Không có đạo trình '{lead_name}'. "
            f"Các đạo trình hiện có: {record.sig_name}"
        )

    lead_index = record.sig_name.index(lead_name)
    number_of_samples = min(
        int(seconds * record.fs),
        record.sig_len,
    )

    time_seconds = (
        np.arange(number_of_samples) / record.fs
    )
    signal = record.p_signal[:number_of_samples, lead_index]

    plt.figure(figsize=(15, 4))
    plt.plot(time_seconds, signal, linewidth=1)
    plt.xlabel("Thời gian (giây)")
    plt.ylabel(f"Biên độ ({record.units[lead_index]})")
    plt.title(
        f"Đạo trình {lead_name} - Record {RECORD_NAME}"
    )
    plt.grid(True, alpha=0.3)
    plt.tight_layout()

    output_path = FIGURES_DIR / (
        f"{RECORD_NAME}_lead_{lead_name}.png"
    )
    plt.savefig(output_path, dpi=200, bbox_inches="tight")

    print(f"Đã lưu biểu đồ đạo trình {lead_name}: {output_path}")
    return output_path


def main() -> None:
    try:
        record = load_ecg()
        print_record_information(record)
        export_signal_to_csv(record)
        plot_all_leads(record)
        plot_single_lead(record, lead_name="II", seconds=10)

        print("\nHoàn tất.")
        print(f"CSV nằm trong: {PROCESSED_DIR}")
        print(f"Biểu đồ nằm trong: {FIGURES_DIR}")

        if os.environ.get("SHOW_PLOTS") == "1":
            # Hiển thị các biểu đồ khi người dùng chủ động bật.
            plt.show()
        else:
            plt.close("all")

    except (FileNotFoundError, ValueError) as error:
        raise SystemExit(f"Lỗi: {error}") from error
    except Exception as error:
        raise SystemExit(
            f"Không thể đọc ECG. Chi tiết: {error}"
        ) from error


if __name__ == "__main__":
    main()
