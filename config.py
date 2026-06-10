import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine


PROJECT_ROOT = Path(__file__).resolve().parent
DATA_DIR = PROJECT_ROOT / "data"
ENV_FILE = PROJECT_ROOT / ".env.local"

load_dotenv(ENV_FILE)


class MissingConfigError(RuntimeError):
    """Raised when a required environment variable is missing."""


def get_required_env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise MissingConfigError(f"{name} not found. Add it to {ENV_FILE.name}.")
    return value


@lru_cache(maxsize=1)
def get_database_url() -> str:
    return get_required_env("DATABASE_URL")


@lru_cache(maxsize=1)
def get_engine():
    return create_engine(get_database_url())
