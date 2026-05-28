# Automotive Product Description Standardisation Pipeline

A lightweight LLM-powered data cleaning and standardisation pipeline for processing noisy automotive product catalogue descriptions.

The project standardises messy real-world inventory data by removing internal reference codes, unnecessary modifiers and inconsistent formatting while preserving important business information such as manufacturer, model, year range and product type.

Designed for scalable catalogue data cleaning workflows with validation, retry handling, batch processing and structured Excel output.

---

## Features

* LLM-powered product description cleaning
* Automotive catalogue standardisation
* Preservation of meaningful vehicle metadata
* Removal of noisy internal product codes
* Batch processing
* Automatic retry and fallback logic
* Validation layer
* Parallel execution
* Excel input/output support
* Error logging
* FastAPI API support
* Docker deployment ready

---

## Example Transformations

| Raw Description                                    | Cleaned Description       |
| -------------------------------------------------- | ------------------------- |
| BMW X2 18-24 Conscious Carpet 3639-0               | BMW X2 18-24 Carpet       |
| BMW Z4 (G29) 18-24 Conscious Carpet 4380           | BMW Z4 18-24 Carpet       |
| BMW X4 14- Boot Mat Conscious Carpet               | BMW X4 14- Boot Mat       |

---

## Processing Goals

The pipeline is designed to preserve:

* Manufacturer / Brand
* Vehicle model
* Meaningful year ranges
* Important product type

The pipeline removes:

* Internal product reference codes
* Irrelevant numeric identifiers
* Duplicate wording
* Excessive modifiers
* Inconsistent formatting
* Noisy metadata

---

## Processing Flow

```text
Excel Input
↓
Batch Processing
↓
LLM Standardisation
↓
Validation
↓
Retry Logic
↓
Structured Output
↓
Excel Export
```

---

## Project Structure

```text
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

## Input Format

Input file:

```text
data.xlsx
```

Required column:

```text
Desc
```

Example input:

| Desc                                     |
| BMW X2 18-24 Conscious Carpet 3639-0               |
| BMW Z4 (G29) 18-24 Conscious Carpet 4380           | 

---

## Output Format

Generated file:

```text
output.xlsx
```

Example output:

| original                             | cleaned             | is_valid |
| ------------------------------------ | ------------------- | -------- |
| BMW X2 18-24 Conscious Carpet 3639-0 | BMW X2 18-24 Carpet | TRUE     |

Error records:

```text
error_log.txt
```

---

## Current Cleaning Logic

The current pipeline focuses on:

* Preserving meaningful vehicle information
* Preserving year ranges when relevant
* Removing internal stock identifiers
* Removing unnecessary descriptive text
* Standardising product naming
* Avoiding hallucinated product names

---

## Tech Stack

* Python
* OpenAI API
* Pandas
* JSON
* ThreadPoolExecutor
* FastAPI
* Docker

---

## Future Improvements

* Resume support
* Cache layer
* Rule-based preprocessing
* API deployment
* Admin review interface
* Vector search for duplicate detection
