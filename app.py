import os
import io
import argparse
import pandas as pd
import streamlit as st
from pathlib import Path
from typing import Tuple, Dict, Any, List

from pii_engine import PiiEngine, DetectedSpan
from utils_io import read_file_any, write_html_report, ensure_dir
from redactors import redact_txt, redact_docx, redact_pdf
from risk_policies import score_spans, summarize_risks

APP_TITLE = "DocShield — Privacy Risk Auditor & Smart Redactor"
st.set_page_config(page_title=APP_TITLE, layout="wide")

def analyze_bytes(name: str, data: bytes, threshold: float = 0.5) -> Tuple[List[DetectedSpan], str]:
    text, loader_info = read_file_any(name, data)
    engine = PiiEngine()
    spans = engine.analyze(text, language="en", score_threshold=threshold)
    return spans, text

def export_all(original_name: str, original_bytes: bytes, text: str, spans: List[DetectedSpan], outdir: Path) -> Dict[str, str]:
    ensure_dir(outdir)
    base = outdir / Path(original_name).stem

    # 1) HTML report
    report_path = str(base.with_suffix(".report.html"))
    write_html_report(report_path, original_name, text, spans)

    # 2) Redacted files per type
    ext = Path(original_name).suffix.lower()
    redacted_path = ""
    if ext == ".txt":
        red_text = redact_txt(text, spans)
        redacted_path = str(base.with_suffix(".redacted.txt"))
        with open(redacted_path, "w", encoding="utf-8") as f:
            f.write(red_text)
    elif ext == ".docx":
        redacted_path = str(base.with_suffix(".redacted.docx"))
        redact_docx(original_bytes, spans, redacted_path)
    elif ext == ".pdf":
        redacted_path = str(base.with_suffix(".redacted.pdf"))
        redact_pdf(original_bytes, spans, redacted_path)
    else:
        # default to TXT redaction export
        red_text = redact_txt(text, spans)
        redacted_path = str(base.with_suffix(".redacted.txt"))
        with open(redacted_path, "w", encoding="utf-8") as f:
            f.write(red_text)

    return {"report": report_path, "redacted": redacted_path}

def main_streamlit():
    st.title(APP_TITLE)
    st.write("Upload a **PDF/DOCX/TXT**. We’ll detect PII, score risk, and export a **redacted** copy + **HTML report**.")

    uploaded = st.file_uploader("Upload file", type=["pdf", "docx", "txt"])
    threshold = st.slider("Detection confidence threshold", 0.0, 1.0, 0.55, 0.01)
    outdir = st.text_input("Output folder (created if missing)", value="outputs")
    run_btn = st.button("Analyze", type="primary")

    if uploaded and run_btn:
        name = uploaded.name
        data = uploaded.read()
        with st.spinner("Analyzing..."):
            spans, text = analyze_bytes(name, data, threshold)
            df = pd.DataFrame([s.__dict__ for s in spans])
            if df.empty:
                st.success("No PII detected above the threshold.")
            else:
                st.subheader("Detections")
                st.dataframe(df)

                st.subheader("Risk Summary")
                risk_rows = score_spans(spans)
                risk_df = pd.DataFrame(risk_rows)
                st.dataframe(risk_df)

                st.subheader("Actionable Summary")
                st.write(summarize_risks(risk_rows))

                paths = export_all(name, data, text, spans, Path(outdir))
                with open(paths["report"], "rb") as f:
                    st.download_button("Download HTML Report", f, file_name=os.path.basename(paths["report"]))
                with open(paths["redacted"], "rb") as f:
                    st.download_button("Download Redacted File", f, file_name=os.path.basename(paths["redacted"]))

def main_cli(args):
    in_path = Path(args.input)
    with open(in_path, "rb") as f:
        data = f.read()
    spans, text = analyze_bytes(in_path.name, data, args.threshold)
    out_paths = export_all(in_path.name, data, text, spans, Path(args.outdir))
    print("Report:", out_paths["report"])
    print("Redacted:", out_paths["redacted"])

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--cli", action="store_true", help="Run in CLI mode")
    parser.add_argument("--input", type=str, help="Path to input file for CLI mode")
    parser.add_argument("--outdir", type=str, default="outputs", help="Output directory")
    parser.add_argument("--threshold", type=float, default=0.55, help="Detection confidence threshold")
    args, _ = parser.parse_known_args()
    if args.cli:
        main_cli(args)
    else:
        main_streamlit()
