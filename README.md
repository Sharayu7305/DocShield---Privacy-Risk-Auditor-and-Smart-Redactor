# DocShield — Privacy Risk Auditor & Smart Redactor (NLP Final-Year Project)

DocShield is a VS Code–friendly, **no-Anaconda** Python app that scans uploaded documents (PDF/DOCX/TXT), **detects Personally Identifiable Information (PII)** using a hybrid NLP pipeline (spaCy + Microsoft Presidio + custom Aadhaar recognizer), **scores privacy risk**, and **exports a redacted copy** plus a **share‑safe compliance report** (aligned with India’s DPDP Act 2023 at a high level).

## What makes it unique?
- **End‑to‑end workflow**: Ingest → Detect → Score → Redact → Report.
- **Hybrid detection**: Rule + ML (spaCy + Presidio) + **custom Aadhaar detector** for India‑specific PII.
- **Policy‑aware risk scoring** mapped to DPDP (India) and GDPR categories (for interview discussion).
- **Multi‑format redaction**: Creates redacted PDF/DOCX/TXT you can share safely.
- **Interactive UI** (Streamlit) + CLI fallback.
- **Extensible**: Plug in your own recognizers or a fine‑tuned NER model (optional script included).

> ⚠️ **Disclaimer**: This is an academic project and not legal advice. Validate outputs before using in production.

---

## Quickstart (No Anaconda)
1) **Install Python 3.10 or 3.11** from python.org and ensure `python` & `pip` on PATH.
2) **Create a virtual env (Windows/Mac/Linux)**:
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate
```
3) **Install dependencies**:
```bash
pip install -r requirements.txt
python -m spacy download en_core_web_md
```
4) **Run the app**:
```bash
streamlit run app.py
```
5) Upload any **PDF/DOCX/TXT** and click **Analyze**. Download the **Redacted file** and **HTML Report**.

---

## Repo Structure
```
docshield_privacy_auditor/
├─ app.py                      # Streamlit UI (upload → analyze → export)
├─ pii_engine.py               # PII detection (Presidio + spaCy + Aadhaar recognizer)
├─ redactors.py                # Redaction for PDF/DOCX/TXT
├─ utils_io.py                 # File reading, report writer, helpers
├─ risk_policies.py            # Risk scoring & policy mapping (DPDP/GDPR)
├─ train_synthetic_ner.py      # Optional: fine-tune a token classifier on synthetic PII
├─ requirements.txt
├─ README.md
└─ sample_data/
   └─ sample.txt
```

---

## Pitch Points (for interviews)
- **Problem**: Organizations accidentally leak PII in documents (emails, IDs, phone, Aadhaar). Manual redaction is slow and error‑prone.
- **Innovation**: Combines **ML NER** + **rule‑based recognizers** + **policy‑aware scoring** and **automatic redaction** in a **single tool**.
- **Impact**: Reduces breach risk, speeds reviews, creates audit trail via reports.
- **Extensibility**: Plug‑in recognizers (bank‑specific IDs), multilingual (add spaCy model + recognizers), train custom NER.
- **Metrics**: Track precision/recall vs. labeled datasets (e.g., Kaggle PII Detection).

---

## CLI (headless) usage
```bash
python app.py --cli --input path/to/file.pdf --outdir outputs/ --threshold 0.55
```

---

## Notes
- PDF redaction uses **PyMuPDF** search + redact annotations; DOCX uses runs replacement; TXT uses inline masks.
- For scanned PDFs (images), add OCR (e.g., `pytesseract`) as an extension.
- Risk mapping aligns entity types with severity to help prioritize remediation.
