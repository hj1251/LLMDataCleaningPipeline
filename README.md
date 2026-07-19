# LLM Data Cleaning Pipeline

An end-to-end, LLM-powered pipeline that extracts an automotive parts catalogue from
a SQL Server ERP, identifies items not yet imported, standardises their product
descriptions with an LLM, and produces a validated file ready for re-upload to the ERP.

Ships with a bundled demo dataset, so the full pipeline runs out of the box with
**no SQL Server or ERP access required**.

---

## Features

* SQL Server extraction of the live product catalogue (falls back to demo data when unconfigured)
* New-item detection — diffs the catalogue against items already imported into the ERP
* LLM-powered product description cleaning and standardisation
* Merge of cleaned descriptions back into the original ERP fields, ready for upload
* Description-length validation (flags anything over a configurable character limit)
* Batch processing with automatic retry and fallback logic
* Local response cache to avoid re-paying for identical LLM calls
* Parallel execution via a thread pool
* Environment-driven configuration (`.env`), no secrets in code
* Unit tests and CI (GitHub Actions)
* Docker deployment ready

---

## Example Transformations

| Raw Description                          | Cleaned Description |
| ----------------------------------------- | -------------------- |
| BMW X2 18-24 Conscious Carpet 3639-0      | BMW X2 18-24 Carpet   |
| BMW Z4 (G29) 18-24 Conscious Carpet 4380  | BMW Z4 18-24 Carpet   |
| BMW X4 14- Boot Mat Conscious Carpet      | BMW X4 14- Boot Mat   |

---

## Processing Flow

```text
SQL Server (or demo CSV)
        ↓
Top Level Code catalogue
        ↓
Diff against items.csv  →  new items only
        ↓
Batch LLM cleaning + validation + retry
        ↓
Merge cleaned descriptions into original ERP fields
        ↓
Length validation (OK / ERROR)
        ↓
upload_file.xlsx  (ready to re-upload to the ERP)
```

A lighter **quick-clean** mode is also available for cleaning a one-off Excel file
that isn't tied to the ERP catalogue at all (see [Usage](#usage)).

---

## Project Structure

```text
LLMDataCleaningPipeline/
├── main.py                    # CLI entrypoint
├── pipeline/
│   ├── config.py               # environment-driven settings
│   ├── db.py                   # SQL Server extraction (+ demo fallback)
│   ├── new_items.py            # new-vs-existing item diffing
│   ├── llm_cleaner.py          # LLM batch cleaning + cache
│   ├── retry.py                # LLM retry for failed validation
│   ├── validation.py           # structural validation rules
│   ├── clean.py                # batching, concurrency, retry orchestration
│   ├── merge.py                # merge cleaned data into ERP upload format
│   ├── run.py                  # full ERP pipeline orchestration
│   └── quick_clean.py          # standalone Excel-column cleaning
├── sample_data/
│   ├── toplevelcode_demo.csv   # demo catalogue (used when SQL Server is unset)
│   └── items_demo.csv          # demo "already imported" items
├── tests/                      # pytest unit tests
├── .github/workflows/tests.yml # CI
├── .env.example
├── requirements.txt
├── requirements-dev.txt
└── Dockerfile
```

---

## Setup

```bash
git clone https://github.com/hj1251/LLMDataCleaningPipeline.git
cd LLMDataCleaningPipeline
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Edit `.env` and set at least `OPENAI_API_KEY`. Everything else is optional:

* Leave `SQL_SERVER` / `SQL_DATABASE` blank to run against the bundled demo data in `sample_data/`.
* To connect to a real SQL Server ERP, fill in `SQL_SERVER`, `SQL_DATABASE`, `SQL_USERNAME`, `SQL_PASSWORD`, and make sure the [Microsoft ODBC Driver for SQL Server](https://learn.microsoft.com/sql/connect/odbc/download-odbc-driver-for-sql-server) is installed locally.

---

## Usage

Run the full ERP pipeline (extract → diff → clean → merge → export):

```bash
python main.py
# or explicitly
python main.py pipeline
```

This produces `upload_file.xlsx` (ERP-ready) and, if any rows failed, `error_log.txt`.

Clean a standalone Excel file (must contain a `Desc` column) without touching the ERP:

```bash
python main.py quick-clean data.xlsx -o output.xlsx
```

Run with Docker:

```bash
docker build -t llm-data-cleaning-pipeline .
docker run --env-file .env llm-data-cleaning-pipeline
```

---

## Output Format

**Full pipeline** → `upload_file.xlsx`:

| STKCODE     | STKNAME                              | STK_COSTPRICE | STK_BASEPRICE | stk_sort_key | Cleaned_Desc         | Validation |
| ----------- | ------------------------------------- | -------------- | -------------- | ------------- | --------------------- | ---------- |
| BMW-Z4-002  | BMW Z4 (G29) 18-24 Conscious Carpet 4380 | 52.00       | 89.99          | TOP LEVEL CODE      | BMW Z4 18-24 Carpet    | OK         |

`Validation` is `ERROR` when `Cleaned_Desc` exceeds `MAX_DESCRIPTION_LENGTH` (default 40 characters).

**Quick-clean mode** → `output.xlsx`:

| original                             | cleaned             | is_valid | validation_issues | retry_count |
| ------------------------------------ | ------------------- | -------- | ------------------ | ------------ |
| BMW X2 18-24 Conscious Carpet 3639-0 | BMW X2 18-24 Carpet | TRUE     |                     | 0            |

Error records for either mode are written to `error_log.txt`.

---

## Tests

```bash
pip install -r requirements-dev.txt
pytest
```

Unit tests cover the pure-logic modules (`validation`, `new_items`, `merge`) and run in CI on every push via GitHub Actions — no OpenAI or SQL Server access required.

---

## Tech Stack

* Python
* OpenAI API
* Pandas
* SQL Server (`pyodbc`)
* ThreadPoolExecutor
* pytest + GitHub Actions
* Docker

---

## Future Improvements

* Resume support for interrupted runs
* Rule-based preprocessing before the LLM pass
* Admin review interface for flagged rows
* Vector search for duplicate detection

---

## Author

Maintained by [@hj1251](https://github.com/hj1251).
