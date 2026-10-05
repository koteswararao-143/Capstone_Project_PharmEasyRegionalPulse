import sqlite3

def run_queries():
    conn = sqlite3.connect("pharmeasy.db")
    cur = conn.cursor()

    print("\n--- Validation Checks ---")

    # 1. Row counts
    cur.execute("SELECT COUNT(*) FROM orders_clean")
    print("Orders_clean row count:", cur.fetchone()[0])

    cur.execute("SELECT COUNT(*) FROM regions_master")
    print("Regions_master row count:", cur.fetchone()[0])

    # 2. Duplicate order IDs
    cur.execute("""
        SELECT order_id, COUNT(*) 
        FROM orders_clean 
        GROUP BY order_id 
        HAVING COUNT(*) > 1
    """)
    duplicates = cur.fetchall()
    print("Duplicate order IDs:", duplicates if duplicates else "None")

    # 3. Null checks
    cur.execute("""
        SELECT COUNT(*) 
        FROM orders_clean 
        WHERE region IS NULL OR category IS NULL
    """)
    print("Rows with null region/category:", cur.fetchone()[0])

    # 4. Per-region counts
    cur.execute("""
        SELECT region, COUNT(*) 
        FROM orders_clean 
        GROUP BY region
    """)
    print("Per-region counts:", cur.fetchall())

    print("\n--- Metrics Queries ---")

    # 5. Region × month sales
    cur.execute("""
        SELECT region, substr(order_date,1,7) AS month, SUM(sales_inr) AS total_sales
        FROM orders_clean
        GROUP BY region, month
        ORDER BY region, month
    """)
    sales = cur.fetchall()
    print("Region × month sales (first 10 rows):", sales[:10])

    # 6. Region × month profit
    cur.execute("""
        SELECT region, substr(order_date,1,7) AS month, SUM(profit_inr) AS total_profit
        FROM orders_clean
        GROUP BY region, month
        ORDER BY region, month
    """)
    profit = cur.fetchall()
    print("Region × month profit (first 10 rows):", profit[:10])

    # 7. Distinct orders per region × month
    cur.execute("""
        SELECT region, substr(order_date,1,7) AS month, COUNT(DISTINCT order_id) AS distinct_orders
        FROM orders_clean
        GROUP BY region, month
        ORDER BY region, month
    """)
    distinct_orders = cur.fetchall()
    print("Region × month distinct orders (first 10 rows):", distinct_orders[:10])

    conn.close()

if __name__ == "__main__":
    run_queries()
