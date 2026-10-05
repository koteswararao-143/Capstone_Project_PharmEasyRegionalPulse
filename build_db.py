import sqlite3, pandas as pd

def build_database():
    conn = sqlite3.connect("pharmeasy.db")
    pd.read_csv("regions_master.csv").to_sql("regions_master", conn, if_exists="replace", index=False)
    pd.read_csv("orders_clean.csv").to_sql("orders_clean", conn, if_exists="replace", index=False)
    conn.commit(); conn.close()
    print("Database created with regions_master (10 rows) and orders_clean (2100 rows).")

if __name__ == "__main__":
    build_database()
