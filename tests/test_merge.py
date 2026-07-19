import pandas as pd

from pipeline.merge import build_upload_file


def test_build_upload_file_flags_long_descriptions():
    new_items = pd.DataFrame(
        {
            "STKCODE": ["A1", "A2"],
            "STKNAME": ["raw a1", "raw a2"],
            "STK_COSTPRICE": [10.0, 20.0],
            "STK_BASEPRICE": [15.0, 25.0],
            "stk_sort_key": ["TOP LEVEL CODE", "TOP LEVEL CODE"],
        }
    )
    cleaned = pd.DataFrame(
        {
            "STKCODE": ["A1", "A2"],
            "cleaned": ["BMW X2 18-24 Carpet", "A" * 41],
        }
    )

    upload_df = build_upload_file(new_items, cleaned)

    row_a1 = upload_df[upload_df["STKCODE"] == "A1"].iloc[0]
    row_a2 = upload_df[upload_df["STKCODE"] == "A2"].iloc[0]

    assert row_a1["Validation"] == "OK"
    assert row_a2["Validation"] == "ERROR"
