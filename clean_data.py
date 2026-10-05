import pandas as pd

def run_cleaning():
    df = pd.read_csv("pharmeasy_orders_raw.csv")
    print("Raw rows:", len(df))

    before = len(df)
    df = df.drop_duplicates()
    after = len(df)
    print("Duplicates removed:", before - after)

    df["region"] = df["region"].str.strip().str.title()

    product_to_category = df.dropna(subset=["category"]).set_index("product")["category"].to_dict()
    df["category"] = df.apply(lambda r: product_to_category.get(r["product"], r["category"]), axis=1)

    df["sales_inr"] = pd.to_numeric(df["sales_inr"], errors="coerce")
    df["profit_inr"] = pd.to_numeric(df["profit_inr"], errors="coerce")

    margins = (
    df.dropna(subset=["profit_inr"])
      .assign(margin=lambda d: d["profit_inr"] / d["sales_inr"])
      .groupby("category")["margin"]
      .mean()
)


    def impute_profit(row):
        if pd.isna(row["profit_inr"]):
            return round(row["sales_inr"] * margins[row["category"]], 2)
        return row["profit_inr"]

    df["profit_inr"] = df.apply(impute_profit, axis=1)

    df.to_csv("orders_clean.csv", index=False)
    print("Cleaned rows:", len(df))

if __name__ == "__main__":
    run_cleaning()
