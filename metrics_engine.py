"""
SQL-backed regional metrics and significance flagging.

The public function names in this module intentionally match the assignment.
"""

from __future__ import annotations

from pathlib import Path
import json
import sqlite3
from typing import Any


ROOT = Path(__file__).resolve().parent
DB_FILE = ROOT / "pharmeasy.db"


def compute_percentage_change_v1(current, previous):
    """Return percentage change; return 0 when the previous value is zero."""
    if previous == 0:
        return 0
    return ((current - previous) / previous) * 100


def get_region_month_sales(db_path=DB_FILE):
    """Get SQL-computed sales by region and month."""
    query = """
        SELECT
            region,
            substr(order_date, 1, 7) AS month,
            SUM(sales_inr) AS sales_inr
        FROM orders_clean
        GROUP BY region, substr(order_date, 1, 7)
        ORDER BY region, month
    """

    with sqlite3.connect(db_path) as connection:
        rows = connection.execute(query).fetchall()

    return rows


def build_month_summary(db_path=DB_FILE, month=None):
    """
    Return a dictionary keyed by region.

    Every region in regions_master is retained, including Kurnool. A missing
    month is represented by zero sales rather than dropping the region.
    """
    months = ["2026-04", "2026-05", "2026-06"]
    if month is not None:
        months = [month]

    placeholders = ",".join("?" for _ in months)

    query = f"""
        SELECT
            r.region,
            COALESCE(SUM(o.sales_inr), 0) AS sales_inr,
            COUNT(o.order_id) AS order_count
        FROM regions_master AS r
        LEFT JOIN orders_clean AS o
            ON r.region = o.region
            AND substr(o.order_date, 1, 7) IN ({placeholders})
        GROUP BY r.region
        ORDER BY r.region
    """

    with sqlite3.connect(db_path) as connection:
        rows = connection.execute(query, months).fetchall()

    return {
        region: {
            "sales_inr": round(float(sales), 2),
            "order_count": int(order_count),
        }
        for region, sales, order_count in rows
    }


def compute_mom_changes(db_path=DB_FILE):
    """Compute April→May and May→June changes for every master region."""
    summaries = {
        month: build_month_summary(db_path, month)
        for month in ["2026-04", "2026-05", "2026-06"]
    }

    changes = {
        "2026-04_to_2026-05": {},
        "2026-05_to_2026-06": {},
    }

    for region in summaries["2026-04"]:
        april = summaries["2026-04"][region]["sales_inr"]
        may = summaries["2026-05"][region]["sales_inr"]
        june = summaries["2026-06"][region]["sales_inr"]

        changes["2026-04_to_2026-05"][region] = compute_percentage_change_v1(
            may, april
        )
        changes["2026-05_to_2026-06"][region] = compute_percentage_change_v1(
            june, may
        )

    return changes


def flag_significant_regions_v1(changes, threshold=8):
    """
    Return regions whose absolute percentage movement is greater than the
    supplied threshold.
    """
    return [
        region
        for region, change in changes.items()
        if abs(change) > threshold
    ]


def save_state_v1(current, path):
    """Persist a month summary as JSON for the next pipeline run."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as file:
        json.dump(current, file, indent=2, sort_keys=True)

    return path


def load_previous_state_v1(path):
    """Reload a state JSON file into the same dictionary structure."""
    path = Path(path)

    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def main():
    changes = compute_mom_changes()

    print("April → May significant regions:")
    print(
        flag_significant_regions_v1(
            changes["2026-04_to_2026-05"], threshold=8
        )
    )

    print("\nMay → June significant regions:")
    print(
        flag_significant_regions_v1(
            changes["2026-05_to_2026-06"], threshold=8
        )
    )

    # Persist April's summary. This demonstrates the state contract required
    # by the assignment: the next process can reload it independently.
    april_summary = build_month_summary(DB_FILE, "2026-04")
    state_path = ROOT / "state" / "2026-04.json"
    save_state_v1(april_summary, state_path)

    reloaded = load_previous_state_v1(state_path)
    print(f"\nSaved and reloaded {len(reloaded)} regional April summaries.")


if __name__ == "__main__":
    main()
