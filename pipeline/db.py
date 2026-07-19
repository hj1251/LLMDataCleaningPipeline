"""Extract the current product catalogue from SQL Server.

Falls back to a bundled demo file when no SQL Server is configured, so the
pipeline can be run end-to-end without real ERP credentials.
"""
import logging

import pandas as pd

from .config import settings

logger = logging.getLogger(__name__)

CATALOGUE_QUERY = """
SELECT STKCODE, STKNAME, STK_COSTPRICE, STK_BASEPRICE, stk_sort_key
FROM dbo.StockItems
WHERE stk_sort_key = ?
"""

REQUIRED_COLUMNS = ["STKCODE", "STKNAME", "STK_COSTPRICE", "STK_BASEPRICE", "stk_sort_key"]


def fetch_catalogue_items() -> pd.DataFrame:
    """Return the ERP catalogue as a DataFrame, filtered to ``settings.stk_sort_key_filter``.

    ``stk_sort_key`` is an ERP category field with many possible values (a real
    catalogue has more than one) — which value to pull is configured via
    ``STK_SORT_KEY_FILTER`` in ``.env`` rather than hardcoded here.
    """
    if settings.sql_server and settings.sql_database:
        df = _fetch_from_sql_server()
    else:
        logger.warning(
            "SQL_SERVER not configured — loading demo catalogue from %s",
            settings.demo_catalogue_path,
        )
        df = pd.read_excel(settings.demo_catalogue_path)
        # The demo file has no WHERE clause to lean on like the SQL Server path
        # does, so the same stk_sort_key filter is applied here in pandas.
        df = df[df["stk_sort_key"] == settings.stk_sort_key_filter]

    return df[REQUIRED_COLUMNS]


def _fetch_from_sql_server() -> pd.DataFrame:
    import pyodbc  # imported lazily: the ODBC driver is only required in live mode

    conn_str = (
        f"DRIVER={{{settings.sql_driver}}};"
        f"SERVER={settings.sql_server};"
        f"DATABASE={settings.sql_database};"
        f"UID={settings.sql_username};"
        f"PWD={settings.sql_password};"
    )

    logger.info("Connecting to SQL Server %s/%s", settings.sql_server, settings.sql_database)
    with pyodbc.connect(conn_str, timeout=30) as conn:
        df = pd.read_sql(CATALOGUE_QUERY, conn, params=[settings.stk_sort_key_filter])

    logger.info("Fetched %d rows from SQL Server (stk_sort_key=%s)", len(df), settings.stk_sort_key_filter)
    return df
