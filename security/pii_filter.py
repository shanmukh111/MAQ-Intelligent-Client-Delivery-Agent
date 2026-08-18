from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine


# ---------------------------------------------------------
# Presidio engines
# ---------------------------------------------------------

_analyzer = AnalyzerEngine()
_anonymizer = AnonymizerEngine()


# ---------------------------------------------------------
# PII detection
# ---------------------------------------------------------

def detect_pii(
    text: str,
) -> list[dict]:
    """
    Detect PII entities in text.

    Returns only metadata about the detected
    entities. The actual sensitive values are
    not returned.
    """

    results = _analyzer.analyze(
        text=text,
        language="en",
    )

    return [
        {
            "entity_type": result.entity_type,
            "start": result.start,
            "end": result.end,
            "score": round(
                result.score,
                3,
            ),
        }
        for result in results
    ]


# ---------------------------------------------------------
# PII masking
# ---------------------------------------------------------

def anonymize_pii(
    text: str,
) -> dict:
    """
    Detect and mask PII before the text reaches
    the routing and agent orchestration layer.

    Important:
    The caller should avoid logging original_text
    when PII is detected.
    """

    analyzer_results = _analyzer.analyze(
        text=text,
        language="en",
    )

    if not analyzer_results:
        return {
            "original_text": text,
            "sanitized_text": text,
            "pii_detected": False,
            "entities": [],
        }

    anonymized = _anonymizer.anonymize(
        text=text,
        analyzer_results=analyzer_results,
    )

    entities = [
        {
            "entity_type": result.entity_type,
            "score": round(
                result.score,
                3,
            ),
        }
        for result in analyzer_results
    ]

    return {
        "original_text": text,
        "sanitized_text": anonymized.text,
        "pii_detected": True,
        "entities": entities,
    }