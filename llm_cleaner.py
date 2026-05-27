from openai import OpenAI
import json

client = OpenAI(
    api_key="123"
)


def clean_batch(text_list):

    prompt = f"""
Extract ONLY:

1. brand
2. product

Rules:
- Keep ONLY brand and product
- Remove numbers
- Remove colors
- Remove extra details
- Do NOT guess
- If description is unclear:
    keep brand empty
    product = original text

Return STRICT JSON ONLY.

NO explanation.
NO markdown.
NO ```json

Format:

[
    {{
        "brand":"BMW",
        "product":"rubber mat"
    }},
    {{
        "brand":"Audi",
        "product":"card"
    }}
]

Input:

{text_list}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0,
        timeout=20
    )

    content = response.choices[0].message.content.strip()

    if content.startswith("```"):
        content = (
            content
            .replace("```json", "")
            .replace("```", "")
            .strip()
        )

    try:
        cleaned = json.loads(content)

        if not isinstance(cleaned, list):
            raise ValueError("Not list")

        return cleaned

    except Exception:
        raise ValueError(
            f"\nInvalid JSON:\n{content}"
        )