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
SQL Server (or demo Excel data)
        ↓
Catalogue, filtered by STK_SORT_KEY_FILTER (default: TOP LEVEL CODE)
        ↓
Diff against items already in the ERP  →  new items only
        ↓
Batch LLM cleaning + validation + retry
        ↓
Merge cleaned descriptions into original ERP fields
        ↓
Length validation (OK / ERROR)
        ↓
upload_file.xlsx  (ready to re-upload to the ERP)
```

---

## Project Structure

```text
LLMDataCleaningPipeline/
├── main.py                    # CLI entrypoint — python main.py runs the whole pipeline
├── pipeline/
│   ├── config.py               # environment-driven settings
│   ├── db.py                   # SQL Server extraction (+ demo fallback)
│   ├── new_items.py            # new-vs-existing item diffing
│   ├── llm_cleaner.py          # LLM batch cleaning + cache
│   ├── retry.py                # LLM retry for failed validation
│   ├── validation.py           # structural validation rules
│   ├── clean.py                # batching, concurrency, retry orchestration
│   ├── merge.py                # merge cleaned data into ERP upload format
│   └── run.py                  # pipeline orchestration (ties the above together)
├── sample_data/
│   ├── toplevelcode_demo.xlsx  # demo catalogue (used when SQL Server is unset)
│   └── items_demo.xlsx         # demo "already imported" items
├── .env.example
├── requirements.txt
└── Dockerfile
```

Everything under `pipeline/` is a single step in the flow above; `main.py` just wires
them together in order. `sample_data/` is only there so the pipeline is runnable
without a real ERP connection — swap in real SQL Server credentials via `.env` and it's ignored.

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

```bash
python main.py
```

This extracts the catalogue, filters out items already in the ERP, cleans the new
descriptions with the LLM, and writes `upload_file.xlsx` (ERP-ready). If any rows
failed, they're written to `error_log.txt`.

Run with Docker:

```bash
docker build -t llm-data-cleaning-pipeline .
docker run --env-file .env llm-data-cleaning-pipeline
```

---

## Output Format

`upload_file.xlsx`:

| STKCODE     | STKNAME                                  | STK_COSTPRICE | STK_BASEPRICE | stk_sort_key   | Cleaned_Desc        | Validation |
| ----------- | ----------------------------------------- | -------------- | -------------- | -------------- | -------------------- | ---------- |
| BMW-Z4-002  | BMW Z4 (G29) 18-24 Conscious Carpet 4380  | 52.00          | 89.99          | TOP LEVEL CODE | BMW Z4 18-24 Carpet  | OK         |

`Validation` is `ERROR` when `Cleaned_Desc` exceeds `MAX_DESCRIPTION_LENGTH` (default 40 characters).

---

## Tech Stack

* Python
* OpenAI API
* Pandas
* SQL Server (`pyodbc`)
* ThreadPoolExecutor
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
