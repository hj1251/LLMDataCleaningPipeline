import pandas as pd
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

from llm_cleaner import clean_batch
from validation import validate
from retry import retry


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

input_file = os.path.join(BASE_DIR, "data.xlsx")
output_file = os.path.join(BASE_DIR, "output.xlsx")
error_log_file = os.path.join(BASE_DIR, "error_log.txt")


BATCH_SIZE = 50
SMALL_BATCH = 10
MAX_RETRY = 1
MAX_WORKERS = 2


df = pd.read_excel(input_file)

if "Desc" not in df.columns:
    raise ValueError("No Desc column")

df = df[df["Desc"].notna()].copy()
df["Desc"] = df["Desc"].astype(str).str.strip()
df = df[df["Desc"] != ""]

rows = df["Desc"].tolist()
total = len(rows)

print(f"Starting processing {total} rows...")
print(f"Batch={BATCH_SIZE}")


def process_row(raw, cleaned):

    try:

        brand = cleaned.get("brand", "")

        product = cleaned.get("product", raw)

        final = (f"{brand} {product}").strip()

        val = validate(final)

        attempt = 0

        while not val["is_valid"] and attempt < MAX_RETRY:

            final = retry(raw, final, val["issues"])

            val = validate(final)

            attempt += 1

        return {
            "original": raw,
            "brand": brand,
            "product": product,
            "cleaned": final,
            "is_valid": val["is_valid"],
            "validation_issues": ", ".join(val["issues"]),
            "retry_count": attempt,
        }

    except Exception:

        return {
            "original": raw,
            "brand": "",
            "product": "",
            "cleaned": "",
            "is_valid": False,
            "validation_issues": "STRUCTURE_ERROR",
            "retry_count": 0,
        }


def process_batch(batch, batch_number):

    print(f"\nBatch {batch_number}")

    local_results = []
    local_errors = []

    try:

        cleaned_list = clean_batch(batch)

        if len(cleaned_list) == len(batch):

            for raw, cleaned in zip(batch, cleaned_list):

                local_results.append(process_row(raw, cleaned))

        else:

            print(f"Mismatch → fallback")

            for i in range(0, len(batch), SMALL_BATCH):

                sub_batch = batch[i : i + SMALL_BATCH]

                try:

                    sub_cleaned = clean_batch(sub_batch)

                    if len(sub_cleaned) == len(sub_batch):

                        for (raw, cleaned) in zip(sub_batch, sub_cleaned):

                            local_results.append(process_row(raw, cleaned))

                    else:

                        raise ValueError("Sub mismatch")

                except Exception as e:

                    local_errors.append(str(e))

                    for raw in sub_batch:

                        local_results.append(
                            {
                                "original": raw,
                                "brand": "",
                                "product": "",
                                "cleaned": "",
                                "is_valid": False,
                                "validation_issues": "SUB_BATCH_ERROR",
                                "retry_count": 0,
                            }
                        )

    except Exception as e:

        local_errors.append(str(e))

        for raw in batch:

            local_results.append(
                {
                    "original": raw,
                    "brand": "",
                    "product": "",
                    "cleaned": "",
                    "is_valid": False,
                    "validation_issues": "BATCH_ERROR",
                    "retry_count": 0,
                }
            )

    return (local_results, local_errors)


results = []
errors = []


with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:

    futures = []

    for start_idx in range(0, total, BATCH_SIZE):

        batch = rows[start_idx : start_idx + BATCH_SIZE]

        batch_number = start_idx // BATCH_SIZE + 1

        futures.append(executor.submit(process_batch, batch, batch_number))

    for future in as_completed(futures):

        res, err = future.result()

        results.extend(res)

        errors.extend(err)


output_df = pd.DataFrame(results)

output_df.to_excel(output_file, index=False)


if errors:

    with open(error_log_file, "w", encoding="utf-8") as f:

        for err in errors:

            f.write(err + "\n")

print(f"\nSaved → {output_file}")

print(f"Rows={len(results)}")

print(f"Errors={len(errors)}")
