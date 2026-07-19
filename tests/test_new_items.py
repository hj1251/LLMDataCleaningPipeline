import pandas as pd

from pipeline.new_items import find_new_items


def test_find_new_items_excludes_existing_codes():
    catalogue = pd.DataFrame({"STKCODE": ["A1", "A2", "A3"], "STKNAME": ["x", "y", "z"]})
    existing = pd.DataFrame({"STKCODE": ["A1", "A3"]})

    new_items = find_new_items(catalogue, existing)

    assert list(new_items["STKCODE"]) == ["A2"]


def test_find_new_items_returns_all_when_none_exist():
    catalogue = pd.DataFrame({"STKCODE": ["A1", "A2"]})
    existing = pd.DataFrame({"STKCODE": pd.Series([], dtype=str)})

    new_items = find_new_items(catalogue, existing)

    assert len(new_items) == 2
