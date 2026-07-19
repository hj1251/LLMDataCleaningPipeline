# Demo data

These two files let the full pipeline run without a real SQL Server connection —
see `pipeline/db.py` and `pipeline/run.py`, which fall back to them whenever
`SQL_SERVER` / `SQL_DATABASE` aren't set in `.env`.

## `toplevelcode_demo.xlsx`

Stands in for the SQL Server catalogue query in `pipeline/db.py`. Columns match
what a real ERP export would have: `STKCODE`, `STKNAME`, `STK_COSTPRICE`,
`STK_BASEPRICE`, `stk_sort_key`. All 8 rows use `stk_sort_key = "TOP LEVEL CODE"`
(the default value of `STK_SORT_KEY_FILTER`).

## `items_demo.xlsx`

Stands in for the "already imported into the ERP" export in
`pipeline/new_items.py`. Only 3 of the 8 catalogue `STKCODE`s appear here
(`BMW-X2-001`, `AUDI-A3-004`, `VW-GOLF-006`), so running the pipeline against
these two files together produces exactly 5 "new" items to clean.
