"""Read-only inspection of the PR7 SQLite database before moving to Django ORM.

Run from the project root:  python db/inspect_source_db.py
"""
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SOURCE_DB = BASE_DIR / "data" / "places.sqlite3"


def inspect(source_db: Path = SOURCE_DB) -> None:
    if not source_db.exists():
        raise FileNotFoundError(f"Исходная база не найдена: {source_db}")

    # mode=ro guarantees that the script cannot modify the source database.
    with sqlite3.connect(f"file:{source_db}?mode=ro", uri=True) as connection:
        connection.row_factory = sqlite3.Row
        tables = connection.execute(
            """SELECT name FROM sqlite_master
               WHERE type = 'table' AND name NOT LIKE 'sqlite_%'
               ORDER BY name"""
        ).fetchall()
        for (table_name,) in tables:
            print(f"\nТаблица: {table_name}")
            print("Столбцы:")
            for column in connection.execute(f'PRAGMA table_info("{table_name}")'):
                print(
                    f"  имя={column['name']}, тип={column['type']}, "
                    f"NOT NULL={column['notnull']}, PRIMARY KEY={column['pk']}"
                )
            count = connection.execute(f'SELECT COUNT(*) FROM "{table_name}"').fetchone()[0]
            print(f"Количество записей: {count}")

        # Referential checks: every foreign key must point to an existing row.
        orphans = connection.execute(
            """SELECT COUNT(*) FROM recommendations
               WHERE user_id NOT IN (SELECT id FROM users)
                  OR place_id NOT IN (SELECT id FROM places)"""
        ).fetchone()[0]
        print(f"\nРекомендаций с несуществующими ссылками: {orphans}")
        values = connection.execute(
            "SELECT DISTINCT is_cancelled FROM recommendations ORDER BY 1"
        ).fetchall()
        print("Значения is_cancelled:", [row[0] for row in values])


if __name__ == "__main__":
    inspect()
