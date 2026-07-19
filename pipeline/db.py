"""Extract the current Top Level Code catalogue from SQL Server.

Falls back to a bundled demo CSV when no SQL Server is configured, so the
pipeline can be run end-to-end without real ERP credentials.
"""
import logging

import pandas as pd

from .config import settings

logger = logging.getLogger(__name__)

TOP_LEVEL_CODE_QUERY = """
SELECT STKCODE, STKNAME, STK_COSTPRICE, STK_BASEPRICE, stk_sort_key
FROM dbo.StockItems
WHERE stk_sort_key = 'TOP LEVEL CODE'
"""

REQUIRED_COLUMNS = ["STKCODE", "STKNAME", "STK_COSTPRICE", "STK_BASEPRICE", "stk_sort_key"]


def fetch_top_level_items() -> pd.DataFrame:
    """Return the current Top Level Code catalogue as a DataFrame."""
    if settings.sql_server and settings.sql_database:
        df = _fetch_from_sql_server()
    else:
        logger.warning(
            "SQL_SERVER not configured — loading demo catalogue from %s",
            settings.demo_catalogue_path,
        )
        df = pd.read_csv(settings.demo_catalogue_path)

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
        df = pd.read_sql(TOP_LEVEL_CODE_QUERY, conn)

    logger.info("Fetched %d rows from SQL Server", len(df))
    return df
