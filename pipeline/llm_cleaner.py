"""LLM-powered batch cleaning of automotive product descriptions, with a local JSON cache."""
import json
import logging
import os

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


if os.path.exists(settings.cache_path):
    with open(settings.cache_path, "r", encoding="utf-8") as f:
        _cache = json.load(f)
    logger.info("Cache loaded successfully")
else:
    _cache = {}
    logger.info("No existing cache found")


def _save_cache():
    with open(settings.cache_path, "w", encoding="utf-8") as f:
        json.dump(_cache, f, ensure_ascii=False, indent=4)


def clean_batch(text_list: list[str]) -> list[dict]:
    """Clean a batch of raw descriptions via the LLM, returning ``[{"cleaned": ...}, ...]``."""
    cache_key = json.dumps(text_list, ensure_ascii=False)

    if cache_key in _cache:
        logger.info("Cache hit for batch of %d", len(text_list))
        return _cache[cache_key]

    logger.info("Processing batch with %d records", len(text_list))

    prompt = f"""
You are a data cleaning assistant. Standardise automotive product descriptions into a consistent format.

OUTPUT FORMAT: Brand + Model + Year Range + Product Type
EXAMPLE: "BMW X2 18-24 Carpet", "BMW X4 14-24 Boot Mat"

--- KEEP ---
* Brand: e.g. BMW
* Model name only: e.g. "3 Series", "X2", "Z4" — no body style, no generation code
* Year range (see rules below)
* Product type: e.g. Carpet, Boot Mat

--- REMOVE ---
* The word "Conscious" (and any similar filler/material modifier words)
* Internal numeric codes: any standalone number or code at the end, e.g. 3459-0, 4460, 4461, 5509-0
* Body style or generation info in brackets or after model name: e.g. (G29), Hatch, F40, Hatchback, Saloon, Estate, Coupe
* Trailing punctuation or noise

--- YEAR RANGE RULES ---
* Full 4-digit ranges → shorten to 2-digit: "2024-2027" → "24-27"
* Already 2-digit ranges → keep as-is: "18-24" → "18-24"
* Open-ended start (no end year) → keep trailing dash: "18-" → "18-"
* Open-ended end (no start year) → keep leading dash: "-20" → "-20"
* If no year range present → omit entirely

--- STRICT RULES ---
* Do NOT hallucinate or invent any information
* Do NOT add anything not present in the input
* Return STRICT JSON ONLY — no markdown, no explanation

Format:
[
  {{"cleaned": "BMW X2 18-24 Carpet"}},
  {{"cleaned": "BMW X4 14-24 Boot Mat"}}
]

Input:
{text_list}
"""

    content = ""
    try:
        response = _get_client().chat.completions.create(
            model=settings.openai_model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            timeout=60,
        )

        content = response.choices[0].message.content.strip()

        if content.startswith("```"):
            content = content.replace("```json", "").replace("```JSON", "").replace("```", "").strip()

        cleaned = json.loads(content)

        _cache[cache_key] = cleaned
        _save_cache()

        return cleaned

    except Exception as e:
        logger.error("Failed batch: %s", e)
        logger.error("Raw response: %s", content)
        raise ValueError(f"Invalid JSON returned by LLM:\n{content}") from e
