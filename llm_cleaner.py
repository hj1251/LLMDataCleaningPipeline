from openai import OpenAI
import json
import logging
import os

client = OpenAI(api_key="123")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("pipeline.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)


CACHE_FILE = "cache.json"

if os.path.exists(CACHE_FILE):
    with open(CACHE_FILE, "r", encoding="utf-8") as f:
        cache = json.load(f)
    logging.info("Cache loaded successfully")
else:
    cache = {}
    logging.info("No existing cache found")


def save_cache():
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=4)
    logging.info("Cache saved")


def clean_batch(text_list):
    cache_key = json.dumps(text_list, ensure_ascii=False)

    if cache_key in cache:
        logging.info("CACHE HIT")
        return cache[cache_key]

    logging.info(f"Processing batch with {len(text_list)} records")

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
        logging.info("Sending request to OpenAI")

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0,
            timeout=60,
        )

        logging.info("Response received from OpenAI")

        content = response.choices[0].message.content.strip()

        if content.startswith("```"):
            logging.warning("Markdown detected in response")
            content = (
                content.replace("```json", "")
                .replace("```JSON", "")
                .replace("```", "")
                .strip()
            )

        cleaned = json.loads(content)


        cache[cache_key] = cleaned
        save_cache()

        logging.info("Batch processed successfully")

        return cleaned

    except Exception as e:
        logging.error(f"Failed batch: {str(e)}")
        logging.error(f"Raw response: {content}")
        raise ValueError(f"\nInvalid JSON:\n{content}")
