"""Create the SQLite database and any missing tables.

Run directly (from the project root):
    venv\\Scripts\\python backend/py/create_tables.py

Existing tables and their data are left untouched.
"""
from sqlmodel import SQLModel

from config.paths import DATA_DIR, DB_PATH
from db.database import engine
from db import models  # noqa: F401  (importing registers the tables)


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    SQLModel.metadata.create_all(engine)
    print(f"Tables ready in {DB_PATH}: {', '.join(SQLModel.metadata.tables)}")


if __name__ == "__main__":
    main()
