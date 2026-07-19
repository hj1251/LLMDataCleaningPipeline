"""Structural validation for cleaned product descriptions."""

NOISE_WORDS = {"for", "includes", "tailored"}
MIN_WORDS = 2
MAX_WORDS = 5


def validate(text: str) -> dict:
    """Check a cleaned description for obvious structural problems."""
    issues = []
    words = text.split()

    if len(words) < MIN_WORDS:
        issues.append("Too short - missing brand or product type")

    if len(words) > MAX_WORDS:
        issues.append("Too long - contains extra details")

    if any(word.lower() in NOISE_WORDS for word in words):
        issues.append("Contains noise words")

    return {"is_valid": len(issues) == 0, "issues": issues}
