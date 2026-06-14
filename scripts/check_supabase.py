import sys
from pathlib import Path

from sqlalchemy import inspect, text

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config import MissingConfigError, get_engine


def main():
    try:
        engine = get_engine()
    except MissingConfigError as exc:
        raise SystemExit(str(exc)) from exc

    try:
        with engine.connect() as conn:
            version = conn.execute(text("SELECT version()")).scalar_one()
            tables = inspect(conn).get_table_names(schema="public")
    except Exception as exc:
        raise SystemExit(f"Database connection failed: {exc}") from exc

    print("Database connection OK.")
    print(f"Postgres version: {version}")
    if tables:
        print("Public tables:")
        for table in tables:
            print(f"- {table}")
    else:
        print("No public tables found yet. Run `python database.py` to create them.")


if __name__ == "__main__":
    main()
