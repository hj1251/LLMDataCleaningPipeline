"""Structural validation for cleaned product descriptions."""

# Tuned against the "Brand + Model + Year Range + Product Type" shape the LLM
# prompt asks for — 2 words is roughly the shortest valid output ("BMW Carpet"),
# 5 is roughly the longest before it starts including extra description noise.
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
