from pathlib import Path
import sys
import pypdfium2 as pdfium

p = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("phases/phase1_data_exploration/tasks/task01_inventory/outputs/qa/DATA_DICTIONARY_task01.pdf")
out = Path(sys.argv[2]) if len(sys.argv) > 2 else p.parent / "data_dictionary_docx_render"
out.mkdir(parents=True, exist_ok=True)
for old_page in out.glob("page-*.png"):
    old_page.unlink()
doc = pdfium.PdfDocument(str(p))
print(f"pages={len(doc)}")
for i, page in enumerate(doc):
    page.render(scale=1.6).to_pil().save(out / f"page-{i + 1}.png")
