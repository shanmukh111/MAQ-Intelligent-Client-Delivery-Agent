import re


_SECRET_PATTERNS = [
    # OpenAI-style API keys
    re.compile(
        r"\bsk-[A-Za-z0-9_\-]{20,}\b"
    ),

    # Bearer tokens / JWT-like values
    re.compile(
        r"\bBearer\s+[A-Za-z0-9._\-]{20,}\b",
        re.IGNORECASE,
    ),

    # JWT tokens
    re.compile(
        r"\beyJ[A-Za-z0-9_\-]+"
        r"\.[A-Za-z0-9_\-]+"
        r"\.[A-Za-z0-9_\-]+\b"
    ),

    # Common secret assignment patterns
    re.compile(
        r"(?i)\b("
        r"api[_\-]?key|"
        r"access[_\-]?token|"
        r"secret|"
        r"password|"
        r"pat"
        r")\b"
        r"\s*[:=]\s*"
        r"[^\s,;]+"
    ),
]


def redact_secrets(
    text: str,
) -> tuple[str, bool]:
    """
    Redacts high-risk secret patterns from model output.

    Returns:
        (sanitized_text, secret_detected)
    """

    if not text:
        return text, False

    sanitized = text
    detected = False

    for pattern in _SECRET_PATTERNS:
        updated = pattern.sub(
            "[REDACTED_SECRET]",
            sanitized,
        )

        if updated != sanitized:
            detected = True

        sanitized = updated

    return sanitized, detected