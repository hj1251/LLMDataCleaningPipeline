"""CLI entrypoint for the LLM data cleaning pipeline."""
import logging

from pipeline.config import settings
from pipeline.run import run_pipeline


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[logging.FileHandler(settings.log_path, encoding="utf-8"), logging.StreamHandler()],
    )
    run_pipeline()


if __name__ == "__main__":
    main()
