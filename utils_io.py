from __future__ import annotations
import io
from typing import Tuple, List
import fitz  # PyMuPDF
from docx import Document
from html import escape
from pii_engine import DetectedSpan

def read_file_any(name: str, data: bytes) -> Tuple[str, str]:
    ext = name.lower().split(".")[-1]
    if ext == "pdf":
        text = _read_pdf(data)
        return text, "pdf:pymupdf"
    elif ext == "docx":
        text = _read_docx(data)
        return text, "docx:python-docx"
    elif ext == "txt":
        return data.decode("utf-8", errors="ignore"), "txt"
    else:
        # Fallback: try utf-8
        return data.decode("utf-8", errors="ignore"), "unknown"

def _read_pdf(data: bytes) -> str:
    doc = fitz.open(stream=data, filetype="pdf")
    texts = []
    for page in doc:
        texts.append(page.get_text("text"))
    return "\n".join(texts)

def _read_docx(data: bytes) -> str:
    doc = Document(io.BytesIO(data))
    paras = [p.text for p in doc.paragraphs]
    return "\n".join(paras)

def ensure_dir(path):
    import os
    d = str(path)
    if not os.path.exists(d):
        os.makedirs(d, exist_ok=True)

def write_html_report(out_path: str, original_name: str, text: str, spans: List[DetectedSpan]) -> None:
    rows = []
    for s in spans:
        rows.append(f"<tr><td>{s.start}</td><td>{s.end}</td><td>{escape(s.entity_type)}</td><td>{s.score}</td><td>{escape(s.text)}</td></tr>")
    table = "\\n".join(rows) if rows else "<tr><td colspan='5'>No PII detected</td></tr>"
    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8"/>
<title>DocShield Report</title>
<style>
body {{ font-family: Arial, sans-serif; margin: 24px; }}
h1 {{ margin-bottom: 0; }}
small {{ color: #666; }}
table {{ border-collapse: collapse; width: 100%; margin-top: 12px; }}
th, td {{ border: 1px solid #ddd; padding: 8px; }}
th {{ background: #f5f5f5; }}
.code {{ white-space: pre-wrap; background: #fafafa; border: 1px solid #eee; padding: 12px; border-radius: 6px; }}
.badge {{ display:inline-block; background:#222; color:#fff; padding:2px 8px; border-radius:12px; font-size:12px; }}
</style>
</head>
<body>
<h1>DocShield — Privacy Risk Auditor</h1>
<small>File: {escape(original_name)}</small>

<h2>Detections</h2>
<table>
<thead><tr><th>Start</th><th>End</th><th>Type</th><th>Score</th><th>Snippet</th></tr></thead>
<tbody>
{table}
</tbody>
</table>

<h2>Original Text (for review)</h2>
<div class="code">{escape(text)}</div>
</body>
</html>"""
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
