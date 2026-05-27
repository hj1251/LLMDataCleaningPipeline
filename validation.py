def validate(text):
    issues = []

    words = text.split()

    if len(words) < 2:
        issues.append("Too short - missing brand or product type")

    if len(words) > 5:
        issues.append("Too long - contains extra details")

    noise_words = ["for", "includes", "tailored"]
    if any(word.lower() in noise_words for word in words):
        issues.append("Contains noise words")

    return {
        "is_valid": len(issues) == 0,
        "issues": issues
    }