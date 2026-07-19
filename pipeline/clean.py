"""Batch LLM cleaning with validation and retry, shared by every entrypoint."""
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

import pandas as pd

from .config import settings
from .llm_cleaner import clean_batch
from .retry import retry
from .validation import validate

logger = logging.getLogger(__name__)


def clean_texts(id_text_pairs: list[tuple[str, str]]) -> tuple[pd.DataFrame, list[str]]:
    """Clean a list of ``(id, raw_text)`` pairs and return ``(results_df, error_messages)``."""
    results: list[dict] = []
    errors: list[str] = []

    with ThreadPoolExecutor(max_workers=settings.max_workers) as executor:
        futures = [
            executor.submit(
                _process_batch,
                id_text_pairs[i : i + settings.batch_size],
                i // settings.batch_size + 1,
            )
            for i in range(0, len(id_text_pairs), settings.batch_size)
        ]
        for future in as_completed(futures):
            batch_results, batch_errors = future.result()
            results.extend(batch_results)
            errors.extend(batch_errors)

    return pd.DataFrame(results), errors


def _process_batch(batch: list[tuple[str, str]], batch_number: int) -> tuple[list[dict], list[str]]:
    logger.info("Processing batch %d (%d rows)", batch_number, len(batch))

    local_results: list[dict] = []
    local_errors: list[str] = []

    try:
        texts = [text for _, text in batch]
        cleaned_list = clean_batch(texts)

        if len(cleaned_list) != len(batch):
            raise ValueError("LLM returned a mismatched number of results")

        for (item_id, raw), cleaned in zip(batch, cleaned_list):
            local_results.append(_process_row(item_id, raw, cleaned))

    except Exception as e:
        local_errors.append(f"Batch {batch_number}: {e}")
        for item_id, raw in batch:
            local_results.append(_error_row(item_id, raw, "BATCH_ERROR"))

    return local_results, local_errors


def _process_row(item_id: str, raw: str, cleaned) -> dict:
    try:
        text = cleaned.get("cleaned", raw) if isinstance(cleaned, dict) else str(cleaned)
        val = validate(text)

        attempt = 0
        while not val["is_valid"] and attempt < settings.max_retry:
            text = retry(raw, text, val["issues"])
            val = validate(text)
            attempt += 1

        return {
            "id": item_id,
            "original": raw,
            "cleaned": text,
            "is_valid": val["is_valid"],
            "validation_issues": ", ".join(val["issues"]),
            "retry_count": attempt,
        }

    except Exception:
        return _error_row(item_id, raw, "STRUCTURE_ERROR")


def _error_row(item_id: str, raw: str, reason: str) -> dict:
    return {
        "id": item_id,
        "original": raw,
        "cleaned": "",
        "is_valid": False,
        "validation_issues": reason,
        "retry_count": 0,
    }
