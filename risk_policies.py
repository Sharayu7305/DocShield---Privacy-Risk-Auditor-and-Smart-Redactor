from __future__ import annotations
from typing import List, Dict
from pii_engine import DetectedSpan

# Map entity types to a simple severity score and rationale.
SEVERITY_MAP = {
    "IN_AADHAAR": ("HIGH", "Government ID (Aadhaar) — high breach risk under DPDP."),
    "PHONE_NUMBER": ("MEDIUM", "Direct contact info."),
    "EMAIL_ADDRESS": ("MEDIUM", "Direct contact info."),
    "CREDIT_CARD": ("HIGH", "Financial identifier."),
    "IBAN_CODE": ("HIGH", "Financial identifier."),
    "IP_ADDRESS": ("LOW", "Network identifier (context-dependent)."),
    "PERSON": ("LOW", "Name alone is low unless linked to other identifiers."),
    "LOCATION": ("LOW", "General location mention."),
    "DATE_TIME": ("LOW", "May be sensitive with other fields."),
}

def score_spans(spans: List[DetectedSpan]) -> List[Dict]:
    rows = []
    for s in spans:
        sev, why = SEVERITY_MAP.get(s.entity_type, ("LOW", "Unmapped type; treat as low by default."))
        rows.append({
            "entity_type": s.entity_type,
            "text": s.text,
            "score": s.score,
            "severity": sev,
            "rationale": why
        })
    return rows

def summarize_risks(rows: List[Dict]) -> str:
    if not rows:
        return "No PII detected. Document appears safe to share."
    # Simple roll-up counts
    from collections import Counter
    sev_counts = Counter([r["severity"] for r in rows])
    top_types = Counter([r["entity_type"] for r in rows]).most_common(5)
    summary = [
        f"- **Totals by severity**: {dict(sev_counts)}",
        f"- **Top types**: {top_types}",
        "- **Recommended actions**:",
        "  1) Share the **redacted** file exported by DocShield.",
        "  2) Manually review HIGH severity items (e.g., Aadhaar, credit cards).",
        "  3) Keep the HTML report as audit evidence of remediation.",
    ]
    return "\n".join(summary)
