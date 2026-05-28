# LLM Data Cleaning Pipeline

A lightweight LLM-based data cleaning pipeline for extracting structured product information from messy product descriptions.

This project uses OpenAI models to standardise raw descriptions into clean and structured outputs with validation, retry logic, batch processing and error handling.

---

## Features

- LLM-powered text cleaning
- Batch processing 
- Automatic fallback to smaller batches
- Structured output (Brand + Product)
- Validation layer
- Retry mechanism
- Error logging
- Parallel execution
- Excel input / output
- FastAPI API
- Docker deployment

---

## Project Structure

```
data_cleaning_pipeline/

├── main.py
├── llm_cleaner.py
├── validation.py
├── retry.py

├── data.xlsx
├── output.xlsx
├── error_log.txt

├── requirements.txt
├── README.md
```

---

## Input

Place the source file in project root:

```
data.xlsx
```

Required column:

```
Desc
```

Example:

| Desc |
|------|
| BMW X5 Rubber Floor Mat Black |
| Audi Card Holder 2024 |

---

## Output

Generated:

```
output.xlsx
```

Output format:

| original | brand | product | cleaned | is_valid |
|----------|--------|---------|---------|----------|
| BMW X5 Rubber Floor Mat | BMW | floor mat | BMW floor mat | TRUE |

Error records:

```
error_log.txt
```

---

## Processing Flow

```
Excel Input
↓

Batch Processing
↓

LLM Extraction
↓

Validation
↓

Retry
↓

Structured Output
↓

Excel Export
```

---

## Prompt Rules

Current extraction logic:

- Keep ONLY brand + product
- Remove colours
- Remove numbers
- Remove extra details
- Do NOT guess
- Preserve original if unclear

---

## Future Improvements

- Resume support
- Cache layer
- Docker deployment
- Rule-based preprocessing
- API service (FastAPI)

---

## Tech Stack

- Python
- OpenAI API
- Pandas
- JSON
- ThreadPoolExecutor

---

## Author

Hanyi Jiang
