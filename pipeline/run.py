"""Full ERP pipeline: SQL Server extract -> new item diff -> LLM cleaning -> ERP upload file."""
from __future__ import annotations

import logging
import os

import pandas as pd

from .clean import clean_texts
from .config import settings
from .db import fetch_top_level_items
from .merge import build_upload_file
from .new_items import find_new_items

logger = logging.getLogger(__name__)


def run_pipeline(output_path: str = "upload_file.xlsx", error_log_path: str = "error_log.txt") -> pd.DataFrame | None:
    catalogue_df = fetch_top_level_items()
    catalogue_df = catalogue_df[catalogue_df["STKNAME"].notna()].copy()
    logger.info("Catalogue loaded: %d rows", len(catalogue_df))

    existing_df = _load_existing_items()
    new_items_df = find_new_items(catalogue_df, existing_df) if existing_df is not None else catalogue_df

    if new_items_df.empty:
        logger.info("No new items found — nothing to clean.")
        return None

    id_text_pairs = list(zip(new_items_df["STKCODE"].astype(str), new_items_df["STKNAME"].astype(str)))
    cleaned_df, errors = clean_texts(id_text_pairs)
    cleaned_df = cleaned_df.rename(columns={"id": "STKCODE"})

    upload_df = build_upload_file(new_items_df, cleaned_df)
    upload_df.to_excel(output_path, index=False)

    if errors:
        with open(error_log_path, "w", encoding="utf-8") as f:
            f.write("\n".join(errors))

    logger.info("Saved ERP upload file -> %s (%d rows, %d errors)", output_path, len(upload_df), len(errors))
    return upload_df


def _load_existing_items() -> pd.DataFrame | None:
    path = settings.existing_items_path
    if not os.path.exists(path):
        logger.warning("No existing items file at %s — treating all catalogue rows as new", path)
        return None
    return pd.read_csv(path)
