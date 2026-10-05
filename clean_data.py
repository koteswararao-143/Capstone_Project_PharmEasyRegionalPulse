"""
Clean the monthly order export.

The cleaning order follows the assignment:
1. exact duplicates
2. region normalization
3. category lookup from product
4. profit imputation using category-level margin
"""

from pathlib import Path
import pandas as pd


ROOT = Path(__file__).resolve().parent
RAW_FILE = ROOT / "pharmeasy_orders_raw.csv"
MASTER_FILE = ROOT / "regions_master.csv"
CLEAN_FILE = ROOT / "orders_clean.csv"


PRODUCT_TO_CATEGORY = {
    "Paracetamol 500mg": "OTC Medicines",
    "Cetirizine 10mg": "OTC Medicines",
    "ORS Sachet": "OTC Medicines",
    "Cough Syrup 100ml": "OTC Medicines",
    "Antacid Tablets": "OTC Medicines",

    "Metformin 500mg": "Prescription Medicines",
    "Amlodipine 5mg": "Prescription Medicines",
    "Atorvastatin 10mg": "Prescription Medicines",
    "Azithromycin 500mg": "Prescription Medicines",
    "Insulin Pen": "Prescription Medicines",

    "Multivitamin Tablets": "Wellness & Nutrition",
    "Whey Protein 1kg": "Wellness & Nutrition",
    "Fish Oil Capsules": "Wellness & Nutrition",
    "Immunity Booster Syrup": "Wellness & Nutrition",
    "Calcium + D3 Tablets": "Wellness & Nutrition",

    "Sunscreen SPF50": "Personal Care",
    "Hand Sanitizer 500ml": "Personal Care",
    "Face Wash": "Personal Care",
    "Antiseptic Liquid": "Personal Care",
    "Baby Diaper Pack": "Personal Care",

    "Digital BP Monitor": "Medical Devices",
    "Pulse Oximeter": "Medical Devices",
    "Glucometer Kit": "Medical Devices",
    "Nebulizer": "Medical Devices",
    "Thermometer": "Medical Devices",

    "Full Body Checkup": "Lab Tests",
    "Thyroid Profile": "Lab Tests",
    "Vitamin D Test": "Lab Tests",
    "HbA1c Test": "Lab Tests",
    "Lipid Profile": "Lab Tests",
}


def load_orders(path=RAW_FILE):
    df = pd.read_csv(path)
    numeric_columns = ["quantity", "sales_inr", "profit_inr"]

    for column in numeric_columns:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    return df


def clean_orders(df):
    result = df.copy()

    # Keep a small audit trail so it is clear what each step changed.
    audit = {
        "rows_before": len(result),
        "duplicates_removed": int(result.duplicated(keep="first").sum()),
        "missing_category_before": int(result["category"].isna().sum()),
        "missing_profit_before": int(result["profit_inr"].isna().sum()),
    }

    # 1. Remove rows where every one of the eight fields is identical.
    result = result.drop_duplicates().copy()

    # 2. Normalize region text.
    result["region"] = result["region"].astype("string").str.strip().str.title()

    # 3. Product is an exact key, so use it to restore missing categories.
    missing_category = result["category"].isna()
    result.loc[missing_category, "category"] = (
        result.loc[missing_category, "product"].map(PRODUCT_TO_CATEGORY)
    )

    if result["category"].isna().any():
        raise ValueError("Category lookup failed for at least one product.")

    # 4. Calculate each category's observed profit margin, then fill missing
    # profit with sales multiplied by that category margin.
    result["profit_margin"] = result["profit_inr"] / result["sales_inr"]

    category_margin = (
        result.loc[result["profit_inr"].notna()]
        .groupby("category")["profit_margin"]
        .mean()
    )

    result["category_mean_margin"] = result["category"].map(category_margin)

    missing_profit = result["profit_inr"].isna()
    result.loc[missing_profit, "profit_inr"] = (
        result.loc[missing_profit, "sales_inr"]
        * result.loc[missing_profit, "category_mean_margin"]
    ).round(2)

    result.drop(columns=["profit_margin", "category_mean_margin"], inplace=True)

    if result["category"].isna().any():
        raise ValueError("Clean data still contains missing categories.")

    if result["profit_inr"].isna().any():
        raise ValueError("Clean data still contains missing profits.")

    audit["rows_after"] = len(result)
    audit["missing_category_after"] = int(result["category"].isna().sum())
    audit["missing_profit_after"] = int(result["profit_inr"].isna().sum())

    return result, audit


def validate_schema(df, required_columns):
    """Validate that every required column is present in the DataFrame."""
    missing = [column for column in required_columns if column not in df.columns]
    if missing:
        return {"status": "blocked_schema", "row_count": len(df), "missing_columns": missing}
    return {"status": "validated", "row_count": len(df), "missing_columns": []}


def main():
    orders = load_orders()
    clean, audit = clean_orders(orders)

    clean.to_csv(CLEAN_FILE, index=False)

    print("Cleaning completed.")
    for key, value in audit.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
