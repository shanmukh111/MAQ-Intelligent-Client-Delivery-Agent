import re


class PromptInjectionError(ValueError):
    """
    Raised when a user request contains an obvious
    prompt-injection or policy-bypass attempt.
    """


_BLOCKED_PATTERNS = [
    r"ignore\s+(all\s+)?previous\s+instructions",
    r"ignore\s+(all\s+)?prior\s+instructions",
    r"disregard\s+(all\s+)?previous\s+instructions",
    r"forget\s+(all\s+)?previous\s+instructions",
    r"reveal\s+(the\s+)?system\s+prompt",
    r"show\s+(me\s+)?(the\s+)?system\s+prompt",
    r"print\s+(the\s+)?system\s+prompt",
    r"reveal\s+(your\s+)?instructions",
    r"show\s+(your\s+)?hidden\s+instructions",
    r"bypass\s+(the\s+)?authorization",
    r"bypass\s+(the\s+)?security",
    r"disable\s+(the\s+)?security",
    r"override\s+(the\s+)?authorization",
    r"act\s+as\s+an?\s+administrator",
    r"pretend\s+I\s+am\s+an?\s+administrator",
]


_COMPILED_PATTERNS = [
    re.compile(
        pattern,
        re.IGNORECASE,
    )
    for pattern in _BLOCKED_PATTERNS
]


def validate_user_prompt(
    user_question: str,
) -> None:
    """
    Performs deterministic detection of obvious
    prompt-injection and authorization-bypass requests.

    This guard intentionally focuses on high-confidence
    patterns so normal delivery-management questions are
    not unnecessarily blocked.
    """

    if not user_question:
        return

    normalized = " ".join(
        user_question.split()
    )

    for pattern in _COMPILED_PATTERNS:
        if pattern.search(normalized):
            raise PromptInjectionError(
                "Potential prompt-injection attempt detected."
            )