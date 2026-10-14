"""Build Markdown and Word reports for a completed Task 4 run."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "AGENTS.md").is_file())


def fmt(value: int | float) -> str: return f"{value:,.0f}"
def pct(value: int | float, total: int | float) -> str: return f"{100 * value / total:.3f}%"


def md_table(headers: list[str], rows: list[list[object]]) -> list[str]:
    return ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"] + ["| " + " | ".join(str(x) for x in row) + " |" for row in rows]


def add_table(doc: Document, headers: list[str], rows: list[list[object]], widths: list[float]) -> None:
    table = doc.add_table(rows=1, cols=len(headers)); table.style = "Table Grid"
    for cell, text in zip(table.rows[0].cells, headers):
        cell.text = str(text)
        for run in cell.paragraphs[0].runs: run.bold = True
    for row in rows:
        cells = table.add_row().cells
        for cell, value in zip(cells, row): cell.text = str(value)
    for row in table.rows:
        for cell, width in zip(row.cells, widths): cell.width = Cm(width)
    table.rows[0]._tr.get_or_add_trPr().append(OxmlElement("w:tblHeader"))


def build_docx(path: Path, sections: list[tuple]) -> None:
    template = ROOT / "tmp" / "phase1_reference.docx"
    doc = Document(template) if template.exists() else Document(); body = doc._element.body
    for child in list(body):
        if child.tag != qn("w:sectPr"): body.remove(child)
    for section in doc.sections:
        section.top_margin = Cm(2); section.bottom_margin = Cm(2); section.left_margin = Cm(2.5); section.right_margin = Cm(2)
        for part in (section.header, section.footer, section.first_page_header, section.first_page_footer):
            for paragraph in part.paragraphs: paragraph.clear()
    for name, size in (("Normal", 12), ("Title", 18), ("Heading 1", 15), ("Heading 2", 13)):
        style = doc.styles[name]; style.font.name = "Times New Roman"; style.font.size = Pt(size); style.font.color.rgb = RGBColor(0, 0, 0)
        style.paragraph_format.space_after = Pt(6); style.paragraph_format.line_spacing = 1.25
    doc.styles["Normal"].paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    for entry in sections:
        if entry[0] == "title": doc.add_paragraph(entry[1], "Title")
        elif entry[0] == "p": doc.add_paragraph(entry[1])
        elif entry[0] == "h1": doc.add_paragraph(entry[1], "Heading 1")
        elif entry[0] == "table": add_table(doc, entry[1], entry[2], entry[3])
        elif entry[0] == "bullet":
            paragraph = doc.add_paragraph()
            paragraph.paragraph_format.left_indent = Cm(0.6)
            paragraph.add_run("• " + entry[1])
    doc.core_properties.title = "Báo cáo khảo sát diagnoses icd MIMIC IV"; doc.core_properties.author = ""; doc.save(path)


def main() -> None:
    parser = argparse.ArgumentParser(); parser.add_argument("run_dir", type=Path); args = parser.parse_args(); run = args.run_dir.resolve()
    data = json.loads((run / "results.json").read_text(encoding="utf-8")); c = data["counts"]; total = c["rows"]
    codes = pd.read_csv(run / "icd_code_profile.csv", dtype={"icd_code": "string"}); top = codes.head(15)
    top_rows = [[int(r.icd_version), r.icd_code, r.long_title, fmt(r.admissions), fmt(r.rows)] for r in top.itertuples()]
    version_rows = [[version, fmt(rows), pct(rows, total), fmt(data["admissions_by_icd_version"].get(str(version), data["admissions_by_icd_version"].get(version, 0))), fmt(data["unique_complete_codes_by_version"][str(version)])] for version, rows in sorted((int(k), v) for k, v in data["rows_by_icd_version"].items())]
    q_rows = data["diagnosis_rows_per_admission"]; q_unique = data["unique_codes_per_admission"]
    distribution_rows = [[label, fmt(q_rows[key]), fmt(q_unique[key])] for key, label in (("min", "Nhỏ nhất"), ("p25", "Phân vị 25"), ("median", "Trung vị"), ("p75", "Phân vị 75"), ("p95", "Phân vị 95"), ("p99", "Phân vị 99"), ("max", "Lớn nhất"), ("mean", "Trung bình"))]
    quality_rows = [
        ["Tổng số dòng", fmt(total), "100.000%"], ["Đủ bốn trường khóa", fmt(c["complete_label_keys"]), pct(c["complete_label_keys"], total)],
        ["Khớp admission và subject_id", fmt(c["subject_match_after_known_admission"]), pct(c["subject_match_after_known_admission"], total)],
        ["Khớp dictionary", fmt(c["dictionary_match"]), pct(c["dictionary_match"], total)],
        ["Có nền tảng sử dụng", fmt(c["usable_diagnosis_row"]), pct(c["usable_diagnosis_row"], total)],
    ]
    md = [
        "# Báo cáo Task 4 khảo sát diagnoses icd", "", "## 1 Mục đích và phạm vi", "",
        "Task 4 khảo sát toàn bộ `diagnoses_icd` để đánh giá khả năng dùng các mã ICD làm nguồn xây dựng nhãn bệnh theo admission. Task không map Phecode, không chọn phenotype, không đặt ngưỡng tần suất và không chỉ giữ primary diagnosis.", "",
        "Một dòng được ghi nhận là có nền tảng sử dụng khi có `subject_id`, `hadm_id`, `icd_code`, `icd_version`; admission tồn tại; bệnh nhân khớp admission; và cặp mã cùng phiên bản khớp `d_icd_diagnoses`.", "",
        "## 2 Dữ liệu và cách thực hiện", "",
        f"Script đã đọc toàn bộ {fmt(total)} dòng theo khối 500.000 dòng, giữ `icd_code` ở dạng chuỗi để bảo toàn số 0 đầu. Các nhánh được tổng hợp ở cấp mã và admission; không nối trực tiếp với từng dòng xét nghiệm.", "",
        "## 3 Chất lượng khóa và khả năng sử dụng", "", *md_table(["Chỉ số", "Số dòng", "Tỷ lệ"], quality_rows), "",
        "Không có dòng thiếu `subject_id`, `hadm_id`, `icd_code`, `icd_version` hoặc `seq_num`. Toàn bộ admission và bệnh nhân khớp bảng `admissions`; toàn bộ cặp `icd_code + icd_version` khớp dictionary. Vì vậy toàn bộ 6.364.488 dòng có nền tảng dùng cho bước xây dựng nhãn.", "",
        "## 4 ICD 9 và ICD 10", "", *md_table(["Phiên bản", "Số dòng", "Tỷ lệ", "Admission", "Mã duy nhất"], version_rows), "",
        f"Tổng cộng có {fmt(data['unique_complete_code_version_pairs'])} cặp mã và phiên bản. Một admission thuộc một giai đoạn mã hóa, nên tổng admission ICD-9 và ICD-10 bằng {fmt(data['usable_admissions'])} admission có diagnosis.", "",
        "## 5 Số diagnosis trên admission", "", *md_table(["Thống kê", "Số dòng diagnosis", "Mã duy nhất"], distribution_rows), "",
        f"Có {fmt(data['duplicate_usable_rows_within_admission'])} dòng dư khi xét trùng cùng `hadm_id + icd_code + icd_version`. Con số này cần được xem là vấn đề chất lượng ở bước xây dựng nhãn; task này chưa xóa các dòng đó.", "",
        "## 6 seq num và primary diagnosis", "",
        f"Có {fmt(c['seq_num_1_row'])} dòng có `seq_num = 1`, phủ đủ {fmt(data['admissions_with_seq_num_1'])} admission. Có {fmt(data['admissions_with_multiple_seq_num_1_rows'])} admission chứa hơn một dòng `seq_num = 1`. Vì bài toán là multi-label, Task 4 chưa giới hạn dữ liệu ở primary diagnosis.", "",
        "## 7 Các mã có độ phủ cao", "", *md_table(["ICD", "Mã", "Mô tả", "Admission", "Số dòng"], top_rows), "",
        "Độ phủ cao không đồng nghĩa mã sẽ trở thành nhãn cuối. Mã ICD-9 và ICD-10 còn phải được map sang phenotype, đo coverage và phân bố trước khi chọn label set.", "",
        "## 8 Giới hạn diễn giải", "",
        "`diagnoses_icd` cho biết diagnosis được ghi nhận cho admission nhưng không có timestamp xác định lúc bác sĩ thiết lập từng diagnosis. Kết quả chỉ hỗ trợ xây dựng nhãn admission-level; không chứng minh mô hình dự đoán trước thời điểm chẩn đoán lâm sàng.", "",
        "## 9 Kết luận của Task 4", "",
        f"Nguồn diagnosis có độ đầy đủ rất cao: {fmt(total)} trên {fmt(total)} dòng khớp admission, bệnh nhân và dictionary. Có {fmt(data['usable_admissions'])} admission với {fmt(data['unique_complete_code_version_pairs'])} cặp mã ICD. Các việc còn lại thuộc Phase 4 gồm mapping Phecode, xử lý 388 dòng trùng và quyết định tập phenotype dựa trên tần suất thực tế.", "",
        "## 10 File đầu ra", "", "- `icd_code_profile.csv`: độ phủ toàn bộ mã ICD.", "- `icd_version_summary.csv`: tổng hợp ICD-9 và ICD-10.",
        "- `seq_num_distribution.csv`: phân bố thứ tự diagnosis.", "- `diagnoses_per_admission.csv`: phân bố số diagnosis theo admission.",
        "- `row_usability_funnel.csv`: các bước kiểm tra khóa.", "- `results.json`: metadata và số liệu máy đọc.", "- `task04_diagnoses_review.xlsx`: workbook dành cho người đọc.",
    ]
    (run / "REPORT_task04.md").write_text("\n".join(md), encoding="utf-8")
    sections = [
        ("title", "BÁO CÁO KHẢO SÁT DIAGNOSES ICD MIMIC IV"), ("p", "Task 4 của Giai đoạn 1 đánh giá khả năng sử dụng mã ICD làm nguồn xây dựng nhãn bệnh theo admission."),
        ("h1", "1 Mục đích và phạm vi"),
        ("p", "Task 4 khảo sát toàn bộ diagnoses_icd để đánh giá khả năng dùng các mã ICD làm nguồn xây dựng nhãn bệnh theo admission. Task không map Phecode, không chọn phenotype, không đặt ngưỡng tần suất và không chỉ giữ primary diagnosis."),
        ("p", "Một dòng được ghi nhận là có nền tảng sử dụng khi có subject_id, hadm_id, icd_code và icd_version; admission tồn tại; bệnh nhân khớp admission; và cặp mã cùng phiên bản khớp d_icd_diagnoses."),
        ("h1", "2 Dữ liệu và cách thực hiện"),
        ("p", f"Script đã đọc toàn bộ {fmt(total)} dòng theo khối 500.000 dòng, giữ icd_code ở dạng chuỗi để bảo toàn số 0 đầu. Các nhánh được tổng hợp ở cấp mã và admission; không nối trực tiếp với từng dòng xét nghiệm."),
        ("h1", "3 Chất lượng khóa và khả năng sử dụng"), ("table", ["Chỉ số", "Số dòng", "Tỷ lệ"], quality_rows, [8.5, 3.5, 3.5]),
        ("p", "Không có dòng thiếu subject_id, hadm_id, icd_code, icd_version hoặc seq_num. Toàn bộ admission và bệnh nhân khớp bảng admissions; toàn bộ cặp icd_code và icd_version khớp dictionary. Vì vậy toàn bộ 6.364.488 dòng có nền tảng dùng cho bước xây dựng nhãn."),
        ("h1", "4 ICD 9 và ICD 10"), ("table", ["Phiên bản", "Số dòng", "Tỷ lệ", "Admission", "Mã duy nhất"], version_rows, [2.5, 3, 2.5, 3, 3]), ("p", f"Tổng cộng có {fmt(data['unique_complete_code_version_pairs'])} cặp mã và phiên bản trên {fmt(data['usable_admissions'])} admission."),
        ("h1", "5 Số diagnosis trên admission"), ("table", ["Thống kê", "Số dòng diagnosis", "Mã duy nhất"], distribution_rows, [5.5, 5, 5]), ("p", f"Có {fmt(data['duplicate_usable_rows_within_admission'])} dòng dư khi xét trùng cùng hadm_id, icd_code và icd_version. Task chưa xóa các dòng đó."),
        ("h1", "6 seq num và primary diagnosis"), ("p", f"Có {fmt(c['seq_num_1_row'])} dòng seq_num = 1, phủ đủ {fmt(data['admissions_with_seq_num_1'])} admission. Có {fmt(data['admissions_with_multiple_seq_num_1_rows'])} admission chứa hơn một dòng seq_num = 1. Task chưa giới hạn dữ liệu ở primary diagnosis."),
        ("h1", "7 Các mã có độ phủ cao"), ("table", ["ICD", "Mã", "Mô tả", "Admission", "Số dòng"], top_rows, [1.5, 2, 7.5, 2.5, 2.5]),
        ("p", "Độ phủ cao chưa quyết định nhãn cuối. Cần map ICD sang phenotype và khảo sát tần suất trước khi chọn label set."),
        ("h1", "8 Giới hạn diễn giải"), ("p", "diagnoses_icd không có timestamp xác định lúc bác sĩ thiết lập từng diagnosis. Dữ liệu hỗ trợ nhãn admission-level nhưng không chứng minh dự đoán xảy ra trước chẩn đoán lâm sàng."),
        ("h1", "9 Kết luận"), ("p", f"Toàn bộ {fmt(total)} dòng khớp admission, bệnh nhân và dictionary. Có {fmt(data['usable_admissions'])} admission với {fmt(data['unique_complete_code_version_pairs'])} cặp mã ICD. Phase 4 sẽ xử lý mapping Phecode, dòng trùng và lựa chọn phenotype."),
        ("h1", "10 File đầu ra"),
        ("p", "Kết quả gồm icd_code_profile.csv, icd_version_summary.csv, seq_num_distribution.csv, diagnoses_per_admission.csv, row_usability_funnel.csv, results.json và task04_diagnoses_review.xlsx."),
    ]
    build_docx(run / "REPORT_task04.docx", sections); print(run / "REPORT_task04.docx")


if __name__ == "__main__": main()
