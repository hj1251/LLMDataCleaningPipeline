"""Single-shot LLM retry for rows that failed validation."""
import logging

from openai import OpenAI

from .config import settings

logger = logging.getLogger(__name__)

_client = None


def _get_client() -> OpenAI:
    global _client
    if _client is None:
        if not settings.openai_api_key:
            raise RuntimeError("OPENAI_API_KEY is not set. Add it to your .env file (see .env.example).")
        _client = OpenAI(api_key=settings.openai_api_key)
    return _client


def retry(original: str, cleaned: str, issues: list[str]) -> str:
    """Ask the LLM to fix a description that failed validation."""
    # Feeding back the specific validation issues (not just "try again") gives the
    # model a concrete target instead of repeating the same mistake a second time.
    prompt = f"""
    You previously cleaned this text incorrectly.

    Original input:
    {original}

    Your previous output:
    {cleaned}

    Problems identified:
    {issues}

    Fix the output by following these STRICT rules:
    - Keep ONLY: Brand + Product type
    - Remove ALL numbers, years, colors, extra descriptons
    - DO NOT guess missing information
    - If the original text is unclear, return it unchanged
    - Keep output within 2-5 words

    Return ONLY the corrected result. No explanation.
    """

    logger.info("Retrying validation for: %s", original)

    response = _get_client().chat.completions.create(
        model=settings.openai_model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
    )

    return response.choices[0].message.content.strip()
