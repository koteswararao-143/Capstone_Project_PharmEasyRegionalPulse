"""Run the required Part 2 SQLite validation and metrics queries."""

import sqlite3
from pathlib import Path

DB_FILE = Path(__file__).resolve().parent / "pharmeasy.db"


def run_queries(db_path=DB_FILE):
    with sqlite3.connect(db_path) as con:
        left_count = con.execute("""
            SELECT COUNT(*)
            FROM regions_master r
            LEFT JOIN orders_clean o ON r.region = o.region
        """).fetchone()[0]

        inner_count = con.execute("""
            SELECT COUNT(*)
            FROM regions_master r
            INNER JOIN orders_clean o ON r.region = o.region
        """).fetchone()[0]

        duplicates = con.execute("""
            SELECT order_id, COUNT(*) AS occurrences
            FROM orders_clean
            GROUP BY order_id
            HAVING COUNT(*) > 1
        """).fetchall()

        null_check = con.execute("""
            SELECT r.region, COUNT(*), COUNT(o.order_id)
            FROM regions_master r
            LEFT JOIN orders_clean o ON r.region = o.region
            GROUP BY r.region
            ORDER BY r.region
        """).fetchall()

        order_counts = con.execute("""
            SELECT r.region, COUNT(o.order_id) AS order_count
            FROM regions_master r
            LEFT JOIN orders_clean o ON r.region = o.region
            GROUP BY r.region
            ORDER BY order_count ASC, r.region ASC
        """).fetchall()

        region_month = con.execute("""
            SELECT region,
                   substr(order_date, 1, 7) AS month,
                   ROUND(SUM(sales_inr), 2) AS sales_inr
            FROM orders_clean
            GROUP BY region, substr(order_date, 1, 7)
            ORDER BY region, month
        """).fetchall()

    print("LEFT JOIN row count:", left_count)
    print("INNER JOIN row count:", inner_count)
    print("Duplicate order IDs:", duplicates)
    print("Region COUNT(*) vs COUNT(order_id):")
    for row in null_check:
        print(row)
    print("Per-region order counts:")
    for row in order_counts:
        print(row)
    print("Region × month sales:")
    for row in region_month:
        print(row)

    return {
        "left_count": left_count,
        "inner_count": inner_count,
        "duplicates": duplicates,
        "null_check": null_check,
        "order_counts": order_counts,
        "region_month": region_month,
    }


if __name__ == "__main__":
    run_queries()
