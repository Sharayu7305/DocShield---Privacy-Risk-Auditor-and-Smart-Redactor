from __future__ import annotations
from dataclasses import dataclass
from typing import List
from presidio_analyzer import AnalyzerEngine, PatternRecognizer, Pattern, RecognizerResult
from presidio_analyzer.nlp_engine import SpacyNlpEngine, NlpEngineProvider
import spacy

# --- Detected span dataclass for easy tables ---
@dataclass
class DetectedSpan:
    start: int
    end: int
    entity_type: str
    score: float
    text: str

class AadhaarRecognizer(PatternRecognizer):
    """
    Custom recognizer for Indian Aadhaar numbers.
    Pattern: 4-4-4 digits separated by space or no separator.
    Example: 1234 5678 9012  or 123456789012
    """

    def __init__(self):
        name = "IN_AADHAAR"
        patterns = [
            Pattern(name="aadhaar_spaced", regex=r"(?<!\d)\d{4}[ -]?\d{4}[ -]?\d{4}(?!\d)", score=0.6),
        ]
        context = ["aadhaar", "uidai", "aadhar"]
        super().__init__(supported_entity= name, patterns=patterns, context=context)

class PiiEngine:
    def __init__(self):
        # Configure spaCy NLP engine
        nlp_conf = {
            "nlp_engine_name": "spacy",
            "models": [{"lang_code": "en", "model_name": "en_core_web_md"}],
        }
        provider = NlpEngineProvider(nlp_configuration=nlp_conf)
        nlp_engine = provider.create_engine()

        # Create Presidio analyzer with spaCy
        self.analyzer = AnalyzerEngine(nlp_engine=nlp_engine, supported_languages=["en"])

        # Add custom Aadhaar recognizer
        self.analyzer.registry.add_recognizer(AadhaarRecognizer())

    def analyze(self, text: str, language: str = "en", score_threshold: float = 0.5) -> List[DetectedSpan]:
        results: List[RecognizerResult] = self.analyzer.analyze(
            text=text,
            language=language,
            score_threshold=score_threshold,
        )
        spans = []
        for r in results:
            spans.append(DetectedSpan(
                start=r.start,
                end=r.end,
                entity_type=r.entity_type,
                score=round(float(r.score), 3),
                text=text[r.start:r.end]
            ))
        # Sort by start index for consistency
        spans.sort(key=lambda x: x.start)
        return spans
