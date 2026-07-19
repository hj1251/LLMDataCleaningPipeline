"""Standalone mode: clean a single Excel column without the SQL Server / ERP pipeline."""
import logging

import pandas as pd

from .clean import clean_texts

logger = logging.getLogger(__name__)


def run_quick_clean(input_path: str, output_path: str = "output.xlsx", error_log_path: str = "error_log.txt") -> pd.DataFrame:
    """Clean the ``Desc`` column of an arbitrary Excel file and write ``output_path``."""
    df = pd.read_excel(input_path)

    if "Desc" not in df.columns:
        raise ValueError("Input file must contain a 'Desc' column")

    df = df[df["Desc"].notna()].copy()
    df["Desc"] = df["Desc"].astype(str).str.strip()
    df = df[df["Desc"] != ""]

    id_text_pairs = list(enumerate(df["Desc"].tolist()))
    results_df, errors = clean_texts(id_text_pairs)
    results_df = results_df.drop(columns=["id"])

    results_df.to_excel(output_path, index=False)

    if errors:
        with open(error_log_path, "w", encoding="utf-8") as f:
            f.write("\n".join(errors))

    logger.info("Saved -> %s (%d rows, %d errors)", output_path, len(results_df), len(errors))
    return results_df
