import pandas as pd

def validate_schema(df, required_columns):
    missing = [c for c in required_columns if c not in df.columns]
    if missing:
        return {"status":"blocked_schema","row_count":len(df),"missing_columns":missing}
    return {"status":"validated","row_count":len(df),"missing_columns":[]}

if __name__ == "__main__":
    clean_df = pd.read_csv("orders_clean.csv")
    required = ["order_id","order_date","region","category","product","quantity","sales_inr","profit_inr"]
    print("Clean data check:", validate_schema(clean_df, required))
    broken_df = clean_df.drop(columns=["product"])
    print("Broken data check:", validate_schema(broken_df, required))
