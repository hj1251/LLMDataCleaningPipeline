"""Centralised, environment-driven configuration for the pipeline."""
import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _path(env_var: str, default_relative: str) -> str:
    value = os.getenv(env_var)
    return value if value else os.path.join(PROJECT_ROOT, default_relative)


@dataclass(frozen=True)
class Settings:
    # OpenAI
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    # SQL Server — leave unset to run the pipeline against the bundled demo data
    sql_server: str = os.getenv("SQL_SERVER", "")
    sql_database: str = os.getenv("SQL_DATABASE", "")
    sql_username: str = os.getenv("SQL_USERNAME", "")
    sql_password: str = os.getenv("SQL_PASSWORD", "")
    sql_driver: str = os.getenv("SQL_DRIVER", "ODBC Driver 18 for SQL Server")

    # Batching / concurrency
    batch_size: int = int(os.getenv("BATCH_SIZE", "50"))
    small_batch: int = int(os.getenv("SMALL_BATCH", "10"))
    max_retry: int = int(os.getenv("MAX_RETRY", "1"))
    max_workers: int = int(os.getenv("MAX_WORKERS", "2"))

    # ERP export validation
    max_description_length: int = int(os.getenv("MAX_DESCRIPTION_LENGTH", "40"))

    # File paths
    demo_catalogue_path: str = _path("DEMO_CATALOGUE_PATH", "sample_data/toplevelcode_demo.csv")
    existing_items_path: str = _path("EXISTING_ITEMS_PATH", "sample_data/items_demo.csv")
    cache_path: str = _path("CACHE_PATH", "cache.json")
    log_path: str = _path("LOG_PATH", "pipeline.log")


settings = Settings()
