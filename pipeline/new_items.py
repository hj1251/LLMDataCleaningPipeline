"""Identify catalogue items that have not yet been imported into the ERP."""
import logging

import pandas as pd

logger = logging.getLogger(__name__)


def find_new_items(catalogue_df: pd.DataFrame, existing_items_df: pd.DataFrame, key: str = "STKCODE") -> pd.DataFrame:
    """Return the rows of ``catalogue_df`` whose ``key`` is not present in ``existing_items_df``.

    ``existing_items_df`` is the current export of items already imported into the
    ERP. Comparing on ``key`` avoids re-cleaning and re-uploading items that are
    already live.
    """
    # Cast to str before comparing: STKCODE can come back as a numeric dtype from
    # Excel/SQL depending on the source, which would otherwise break the match.
    existing_keys = set(existing_items_df[key].astype(str))
    new_df = catalogue_df[~catalogue_df[key].astype(str).isin(existing_keys)].copy()

    logger.info(
        "Catalogue=%d Existing=%d New=%d",
        len(catalogue_df),
        len(existing_items_df),
        len(new_df),
    )
    return new_df.reset_index(drop=True)
