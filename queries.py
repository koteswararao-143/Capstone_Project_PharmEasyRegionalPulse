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
    print("Duplicate order IDs:", cur.fetchall())

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
        SELECT region, substr(order
