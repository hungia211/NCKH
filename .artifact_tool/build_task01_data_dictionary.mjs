import fs from "node:fs/promises";
import path from "node:path";
import { Workbook, SpreadsheetFile } from "@oai/artifact-tool";

const repo = "D:/UIT_thu/NCKH";
const task = path.join(repo, "phases/phase1_data_exploration/tasks/task01_inventory");
const inputPath = path.join(task, "outputs/tables/data_dictionary_core_tables_task01.json");
const outputPath = path.join(task, "outputs/tables/DATA_DICTIONARY_task01.xlsx");
const previewDir = path.join(task, "outputs/qa/data_dictionary_xlsx_preview");

const source = JSON.parse(await fs.readFile(inputPath, "utf8"));
const rows = source.rows;
const workbook = Workbook.create();

const colors = {
  navy: "#1F4E78",
  blue: "#D9EAF7",
  pale: "#EEF5FA",
  dark: "#1F2937",
  white: "#FFFFFF",
  green: "#E2F0D9",
  amber: "#FFF2CC",
};

function setTitle(range, text) {
  range.values = [[text]];
  range.merge();
  range.format = {
    fill: colors.navy,
    font: { bold: true, color: colors.white, size: 16 },
    horizontalAlignment: "left",
    verticalAlignment: "center",
  };
  range.format.rowHeight = 30;
}

function setHeader(range) {
  range.format = {
    fill: colors.navy,
    font: { bold: true, color: colors.white, size: 10 },
    horizontalAlignment: "center",
    verticalAlignment: "center",
    wrapText: true,
  };
  range.format.rowHeight = 34;
}

function addBorders(range) {
  range.format.borders = {
    top: { style: "continuous", color: "#B8C6D1" },
    bottom: { style: "continuous", color: "#B8C6D1" },
    left: { style: "continuous", color: "#B8C6D1" },
    right: { style: "continuous", color: "#B8C6D1" },
    insideHorizontal: { style: "continuous", color: "#D7E0E7" },
    insideVertical: { style: "continuous", color: "#D7E0E7" },
  };
}

const overview = workbook.worksheets.add("Overview");
setTitle(overview.getRange("A1:F1"), "TỪ ĐIỂN DỮ LIỆU MIMIC-IV HOSP — TASK 1");
overview.getRange("A2:F2").values = [["Phạm vi", "5 bảng chính", "Số cột", 44, "Đơn vị phân tích", "hadm_id"]];
overview.getRange("A2:F2").format = { fill: colors.blue, font: { bold: true, color: colors.dark }, wrapText: true };
overview.getRange("A4:F4").values = [["Bảng", "Đơn vị mỗi dòng", "Khóa chính", "Khóa nối", "Vai trò trong đề tài", "Nguồn chính thức"]];
setHeader(overview.getRange("A4:F4"));
const overviewRows = [
  ["admissions", "Một dòng / admission", "hadm_id", "subject_id; hadm_id", "Xác định admission và mốc thời gian", "https://mimic.mit.edu/docs/iv/modules/hosp/admissions.html"],
  ["labevents", "Một dòng / kết quả xét nghiệm", "labevent_id", "subject_id; hadm_id; itemid", "Nguồn feature xét nghiệm", "https://mimic.mit.edu/docs/iv/modules/hosp/labevents.html"],
  ["d_labitems", "Một dòng / khái niệm xét nghiệm", "itemid", "itemid", "Từ điển xét nghiệm", "https://mimic.mit.edu/docs/iv/modules/hosp/d_labitems.html"],
  ["diagnoses_icd", "Một dòng / mã ICD của admission", "hadm_id + seq_num", "subject_id; hadm_id; icd_code + icd_version", "Nguồn nhãn bệnh", "https://mimic.mit.edu/docs/iv/modules/hosp/diagnoses_icd.html"],
  ["d_icd_diagnoses", "Một dòng / mã từ điển ICD", "icd_code + icd_version", "icd_code + icd_version", "Tên mô tả chẩn đoán", "https://mimic.mit.edu/docs/iv/modules/hosp/d_icd_diagnoses.html"],
];
overview.getRange("A5:F9").values = overviewRows;
overview.getRange("A5:F9").format = { wrapText: true, verticalAlignment: "top" };
overview.getRange("A10:F10").values = [["Quy tắc chính", "labevents phải có hadm_id", "Chia tập", "Theo subject_id", "Nhãn", "diagnoses_icd → PheCode ở bước sau"]];
overview.getRange("A10:F10").format = { fill: colors.amber, font: { bold: true }, wrapText: true };
addBorders(overview.getRange("A4:F10"));
overview.freezePanes.freezeRows(4);
overview.getRange("A1:A10").format.columnWidth = 18;
overview.getRange("B1:B10").format.columnWidth = 28;
overview.getRange("C1:C10").format.columnWidth = 19;
overview.getRange("D1:D10").format.columnWidth = 36;
overview.getRange("E1:E10").format.columnWidth = 34;
overview.getRange("F1:F10").format.columnWidth = 46;

const columns = workbook.worksheets.add("Columns");
setTitle(columns.getRange("A1:L1"), "44 CỘT CỦA 5 BẢNG CHÍNH");
columns.getRange("A2:L2").values = [["table", "vị trí", "column_name", "kiểu dữ liệu", "có thể thiếu", "ý nghĩa tiếng Việt", "ví dụ/giá trị", "vai trò nghiên cứu", "quy tắc nối", "dùng hiện tại", "quan sát dữ liệu cục bộ", "nguồn"]];
setHeader(columns.getRange("A2:L2"));
const columnValues = rows.map((r) => [
  r.table, Number(r.column_position), r.column_name, r.postgres_type, r.nullable,
  r.meaning_vi, r.example_or_values, r.research_role, r.join_rule,
  r.use_in_current_pipeline, r.local_observation, r.official_source,
]);
columns.getRange(`A3:L${columnValues.length + 2}`).values = columnValues;
columns.getRange(`A3:L${columnValues.length + 2}`).format = { wrapText: true, verticalAlignment: "top", font: { size: 9 } };
for (let i = 0; i < columnValues.length; i += 2) {
  columns.getRange(`A${i + 3}:L${i + 3}`).format.fill = colors.pale;
}
addBorders(columns.getRange(`A2:L${columnValues.length + 2}`));
columns.freezePanes.freezeRows(2);
columns.freezePanes.freezeColumns(3);
const widths = [16, 8, 22, 21, 17, 46, 24, 27, 44, 20, 48, 48];
"ABCDEFGHIJKL".split("").forEach((c, i) => { columns.getRange(`${c}1:${c}${columnValues.length + 2}`).format.columnWidth = widths[i]; });

const time = workbook.worksheets.add("Time fields");
setTitle(time.getRange("A1:D1"), "CÁCH ĐỌC CÁC MỐC THỜI GIAN");
time.getRange("A2:D2").values = [["Thứ tự", "Trường", "Ý nghĩa", "Cách dùng trong nghiên cứu"]];
setHeader(time.getRange("A2:D2"));
const timeRows = [
  [1, "admissions.edregtime", "Đăng ký khoa cấp cứu", "Mốc phụ; có thể trước admittime và không có ở mọi admission."],
  [2, "admissions.admittime", "Bắt đầu admission", "Mốc 0 để tính thời gian tương đối của xét nghiệm."],
  [3, "labevents.charttime", "Ghi nhận/lấy mẫu xét nghiệm", "Xác định xét nghiệm xảy ra trước hay sau admittime và có nằm trong admission."],
  [4, "labevents.storetime", "Kết quả có trong hệ thống", "Kiểm tra kết quả đã sẵn có tại mốc dự đoán, hạn chế rò rỉ tương lai."],
  [5, "admissions.edouttime", "Rời khoa cấp cứu", "Mốc phụ cho admission đi qua ED."],
  [6, "admissions.dischtime", "Kết thúc admission", "Giới hạn trên để kiểm tra sự kiện thuộc đúng admission."],
  [7, "admissions.deathtime", "Tử vong trong bệnh viện nếu có", "Mốc kết cục; không dùng làm feature đầu vào sớm."],
];
time.getRange("A3:D9").values = timeRows;
time.getRange("A3:D9").format = { wrapText: true, verticalAlignment: "top" };
time.getRange("A11:D12").merge();
time.getRange("A11:D12").values = [["Ngày giờ trong MIMIC đã được dịch chuyển để khử định danh, nhưng thứ tự và khoảng cách tương đối trong cùng bệnh nhân vẫn dùng được. Timestamp hiện dùng để lọc đúng quan hệ nhập viện → xét nghiệm → kết quả sẵn có; chưa mặc định đưa timestamp thô vào vector feature."]];
time.getRange("A11:D12").format = { fill: colors.green, wrapText: true, font: { bold: true, color: colors.dark }, verticalAlignment: "center" };
addBorders(time.getRange("A2:D12"));
time.freezePanes.freezeRows(2);
time.getRange("A1:A12").format.columnWidth = 10;
time.getRange("B1:B12").format.columnWidth = 30;
time.getRange("C1:C12").format.columnWidth = 32;
time.getRange("D1:D12").format.columnWidth = 66;

await workbook.recalculate();
const errors = await workbook.inspect({
  kind: "match",
  searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!",
  options: { useRegex: true, maxResults: 100 },
  summary: "final formula error scan",
});
console.log(errors.ndjson);

await fs.mkdir(previewDir, { recursive: true });
for (const [sheetName, range] of [["Overview", "A1:F10"], ["Columns", "A1:L46"], ["Time fields", "A1:D12"]]) {
  const blob = await workbook.render({ sheetName, range, scale: 1.2, format: "png" });
  await fs.writeFile(path.join(previewDir, `${sheetName.replaceAll(" ", "_")}.png`), new Uint8Array(await blob.arrayBuffer()));
}

await fs.mkdir(path.dirname(outputPath), { recursive: true });
const output = await SpreadsheetFile.exportXlsx(workbook);
await output.save(outputPath);
console.log(outputPath);
