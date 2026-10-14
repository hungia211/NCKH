"""Build the Phase 1 report from the current Markdown and inventory."""
import re
from pathlib import Path
from docx import Document
from docx.shared import Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

ROOT = next(
    parent for parent in Path(__file__).resolve().parents
    if (parent / 'AGENTS.md').is_file()
)
TASK = Path(__file__).resolve().parents[1]
PHASE = TASK.parents[1]

def clean(text):
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
    return text.replace('**', '').replace('`', '')

def build():
    doc = Document(ROOT / 'tmp/phase1_reference.docx')
    body = doc._element.body
    for child in list(body):
        if child.tag != qn('w:sectPr'):
            body.remove(child)
    for sec in doc.sections:
        for part in [sec.header, sec.footer, sec.first_page_header, sec.first_page_footer]:
            for p in part.paragraphs:
                p.clear()
    for name, size in [('Normal', 13), ('Title', 18), ('Heading 1',16), ('Heading 2',14)]:
        style = doc.styles[name]
        style.font.name = 'Times New Roman'
        style.font.size = Pt(size)
        style.font.color.rgb = RGBColor(0,0,0)
        style.paragraph_format.line_spacing = 1.5
        style.paragraph_format.space_after = Pt(6)
    doc.styles['Normal'].paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    for name in ['Title','Heading 1','Heading 2']:
        style = doc.styles[name]
        style.font.bold = True
        style.paragraph_format.keep_with_next = True
        for tag in ['w:numPr', 'w:pBdr']:
            for el in list(style.element.iter(qn(tag))): el.getparent().remove(el)
    doc.add_paragraph('BÁO CÁO KHẢO SÁT DỮ LIỆU MIMIC IV HOSP', 'Title')
    doc.add_paragraph('Giai đoạn 1 của nghiên cứu dự đoán đa nhãn từ dữ liệu xét nghiệm')
    doc.add_paragraph('Báo cáo trình bày kết quả kiểm kê 22 bảng HOSP và khảo sát ban đầu các bảng nhập viện, xét nghiệm và chẩn đoán. Kết quả giúp nhận diện độ phủ dữ liệu và những vấn đề cần giải quyết trước khi xây dựng tập admission nghiên cứu. Các lựa chọn về cửa sổ thời gian, đặc trưng và nhãn bệnh vẫn đang được khảo sát.')
    doc.add_paragraph('Số liệu khảo sát ngày 22 tháng 9 năm 2026. Bản báo cáo được biên soạn từ các kết quả đã lưu, không phải một lần chạy lại dữ liệu.')

    def markdown(text, skip_title=True):
        lines = text.splitlines(); i=0; code=False
        while i<len(lines):
            line=lines[i].strip(); i+=1
            if not line: continue
            if line.startswith('```'): code=not code; continue
            if line.startswith('# ') and skip_title: continue
            if line.startswith('|'):
                rows=[line]
                while i<len(lines) and lines[i].strip().startswith('|'):
                    rows.append(lines[i].strip()); i+=1
                cells=[[clean(c.strip()) for c in r.strip('|').split('|')] for r in rows if not re.match(r'^\|[ :|\-]+$',r)]
                t=doc.add_table(rows=0, cols=len(cells[0])); t.style='Table Grid'
                for ri, row in enumerate(cells):
                    cs=t.add_row().cells
                    for c, text in zip(cs,row):
                        c.text=text
                        for p in c.paragraphs:
                            p.paragraph_format.line_spacing=1.15
                            p.paragraph_format.space_after=Pt(4)
                            for r in p.runs: r.font.size=Pt(11); r.font.name='Times New Roman'; r.bold=ri==0
                    if ri==0:
                        repeat=OxmlElement('w:tblHeader'); t.rows[0]._tr.get_or_add_trPr().append(repeat)
                continue
            if line.startswith('### '): doc.add_paragraph(clean(line[4:]), 'Heading 2')
            elif line.startswith('## '): doc.add_paragraph(clean(line[3:]), 'Heading 1')
            else:
                p=doc.add_paragraph(clean(line))
                if code:
                    p.paragraph_format.line_spacing=1
                    for r in p.runs:r.font.size=Pt(10)
    markdown((TASK/'report'/'REPORT_task01.md').read_text(encoding='utf-8'))
    doc.add_paragraph('7 Giải thích kế hoạch khảo sát tiếp theo','Heading 1')
    task=(PHASE/'TASK_BREAKDOWN.md').read_text(encoding='utf-8')
    task=task.split('## Giải thích các task tiếp theo')[1].split('## Tiến độ thực tế')[0]
    markdown(task)
    doc.add_paragraph('8 Nguồn số liệu và giới hạn','Heading 1')
    doc.add_paragraph('Số liệu: tasks/task01_inventory/outputs/machine_readable/hosp_inventory.json và core_summary.json trong thư mục Phase 1. Tên xét nghiệm được diễn giải bằng d_labitems. Số itemid thực tế trong labevents là 976; số dòng dictionary là 1.650. Các tần suất hiện tại không thay thế độ phủ trong cửa sổ sớm. Việc thiếu deathtime cũng không đủ để kết luận lỗi dữ liệu vì ý nghĩa trường này phụ thuộc tình trạng tử vong.')
    doc.core_properties.title='Báo cáo khảo sát dữ liệu MIMIC IV HOSP'
    doc.core_properties.author=''
    doc.core_properties.last_modified_by=''
    output=TASK/'report'/'REPORT_task01.docx'; doc.save(output); print(output)

if __name__=='__main__': build()
