"""
Build the local SQLite database used by the metrics engine.

The database contains exactly two tables:
    regions_master
    orders_clean
"""

from pathlib import Path
import sqlite3
import pandas as pd


ROOT = Path(__file__).resolve().parent
DB_FILE = ROOT / "pharmeasy.db"
REGIONS_FILE = ROOT / "regions_master.csv"
ORDERS_FILE = ROOT / "orders_clean.csv"


def build_database(
    db_path=DB_FILE,
    regions_path=REGIONS_FILE,
    orders_path=ORDERS_FILE,
):
    regions = pd.read_csv(regions_path)
    orders = pd.read_csv(orders_path)

    with sqlite3.connect(db_path) as connection:
        regions.to_sql("regions_master", connection, if_exists="replace", index=False)
        orders.to_sql("orders_clean", connection, if_exists="replace", index=False)

        # These indexes are not required for correctness, but make repeated
        # joins and order-id checks inexpensive.
        connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_orders_region "
            "ON orders_clean(region)"
        )
        connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_orders_order_id "
            "ON orders_clean(order_id)"
        )
        connection.commit()

    return db_path


def main():
    path = build_database()
    print(f"Created SQLite database: {path}")
    with sqlite3.connect(path) as connection:
        for table in ("regions_master", "orders_clean"):
            count = connection.execute(
                f"SELECT COUNT(*) FROM {table}"
            ).fetchone()[0]
            print(f"{table}: {count} rows")


if __name__ == "__main__":
    main()
