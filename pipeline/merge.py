"""Merge cleaned descriptions back into the original ERP fields for upload."""
import logging

import pandas as pd

from .config import settings

logger = logging.getLogger(__name__)

UPLOAD_COLUMNS = [
    "STKCODE",
    "STKNAME",
    "STK_COSTPRICE",
    "STK_BASEPRICE",
    "stk_sort_key",
    "Cleaned_Desc",
    "Validation",
]


def build_upload_file(new_items_df: pd.DataFrame, cleaned_df: pd.DataFrame) -> pd.DataFrame:
    """Merge cleaned descriptions with the original ERP columns and flag length violations."""
    left = new_items_df.copy()
    left["STKCODE"] = left["STKCODE"].astype(str)

    right = cleaned_df[["STKCODE", "cleaned"]].rename(columns={"cleaned": "Cleaned_Desc"}).copy()
    right["STKCODE"] = right["STKCODE"].astype(str)

    merged = left.merge(right, on="STKCODE", how="left")
    merged["Validation"] = merged["Cleaned_Desc"].apply(_validate_length)

    invalid = int((merged["Validation"] == "ERROR").sum())
    if invalid:
        logger.warning("%d rows exceed %d characters", invalid, settings.max_description_length)

    return merged[UPLOAD_COLUMNS]


def _validate_length(desc) -> str:
    if not isinstance(desc, str) or not desc:
        return "ERROR"
    return "ERROR" if len(desc) > settings.max_description_length else "OK"
