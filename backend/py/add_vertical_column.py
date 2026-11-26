"""Add the "vertical" column to an existing device table.

create_tables.py only creates missing tables, it doesn't add new columns to existing
ones, so a database made before "vertical" existed needs this once.

Run directly (from the project root):
    venv\\Scripts\\python backend/py/add_vertical_column.py

Safe to run again: does nothing if the column is already there.
"""
from sqlalchemy import inspect, text

from db.database import engine


def main() -> None:
    columns = [column["name"] for column in inspect(engine).get_columns("device")]

    if "vertical" in columns:
        print("device.vertical already exists")
        return

    with engine.begin() as connection:
        connection.execute(text("ALTER TABLE device ADD COLUMN vertical VARCHAR"))

    print("added device.vertical")


if __name__ == "__main__":
    main()
