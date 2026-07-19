"""CLI entrypoint for the LLM data cleaning pipeline."""
import argparse
import logging

from pipeline.config import settings
from pipeline.quick_clean import run_quick_clean
from pipeline.run import run_pipeline


def main():
    parser = argparse.ArgumentParser(description="LLM-powered ERP catalogue cleaning pipeline")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser(
        "pipeline",
        help="Run the full SQL Server -> new item diff -> clean -> ERP upload file pipeline (default)",
    )

    quick = subparsers.add_parser("quick-clean", help="Clean a standalone Excel file with a 'Desc' column")
    quick.add_argument("input_file")
    quick.add_argument("-o", "--output", default="output.xlsx")

    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[logging.FileHandler(settings.log_path, encoding="utf-8"), logging.StreamHandler()],
    )

    if args.command == "quick-clean":
        run_quick_clean(args.input_file, args.output)
    else:
        run_pipeline()


if __name__ == "__main__":
    main()
