from __future__ import annotations
from typing import List
import io
import fitz  # PyMuPDF
from docx import Document
from pii_engine import DetectedSpan

MASK = "[REDACTED:{etype}]"

def redact_txt(text: str, spans: List[DetectedSpan]) -> str:
    # Replace from right to left to preserve indices
    red_text = text
    for s in sorted(spans, key=lambda x: x.start, reverse=True):
        red_text = red_text[:s.start] + MASK.format(etype=s.entity_type) + red_text[s.end:]
    return red_text

def redact_docx(file_bytes: bytes, spans: List[DetectedSpan], out_path: str) -> None:
    doc = Document(io.BytesIO(file_bytes))
    # For simplicity, do straightforward replacements using the span texts
    # Collect unique target strings to search within runs
    targets = {s.text for s in spans if s.text and not s.text.isspace()}
    for para in doc.paragraphs:
        for t in targets:
            if t in para.text:
                # Rebuild runs: simple replace on paragraph text
                para.text = para.text.replace(t, MASK.format(etype="PII"))
    doc.save(out_path)

def redact_pdf(file_bytes: bytes, spans: List[DetectedSpan], out_path: str) -> None:
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    # Search for each unique detected string
    targets = {s.text for s in spans if s.text and not s.text.isspace()}
    for page in doc:
        for t in targets:
            rects = page.search_for(t)
            for r in rects:
                page.add_redact_annot(r, text="█")
        page.apply_redactions()
    doc.save(out_path)
