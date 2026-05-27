from openai import OpenAI
client = OpenAI(api_key="123")

def retry(original, cleaned, issues):
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

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    return response.choices[0].message.content.strip()