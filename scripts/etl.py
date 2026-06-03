"""
etl.py — Retail Sales Analytics
ETL pipeline for Global Superstore dataset (Superstore.csv)
Cleans, transforms, and exports data ready for Power BI ingestion.
"""

import pandas as pd
import numpy as np
import os

# ── Paths ──────────────────────────────────────────────────────────────────
RAW_PATH    = os.path.join(os.path.dirname(__file__), "../data/Superstore.csv")
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "../data/superstore_clean.csv")
SUMMARY_PATH = os.path.join(os.path.dirname(__file__), "../data/superstore_summary.xlsx")


def load_data(path: str) -> pd.DataFrame:
    """Load raw CSV with encoding fallback."""
    try:
        df = pd.read_csv(path, encoding="utf-8")
    except UnicodeDecodeError:
        df = pd.read_csv(path, encoding="latin-1")
    print(f"[✓] Loaded {len(df):,} rows × {len(df.columns)} columns")
    return df


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Standardise column names, fix types, drop duplicates."""
    # Normalise column names
    df.columns = (
        df.columns.str.strip()
                  .str.lower()
                  .str.replace(" ", "_")
                  .str.replace("-", "_")
    )

    # Parse dates
    for col in ["order_date", "ship_date"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    # Drop exact duplicate rows
    before = len(df)
    df = df.drop_duplicates()
    print(f"[✓] Dropped {before - len(df)} duplicate rows")

    # Strip whitespace from string columns
    str_cols = df.select_dtypes("object").columns
    df[str_cols] = df[str_cols].apply(lambda s: s.str.strip())

    # Ensure numeric columns are correct dtype
    for col in ["sales", "profit", "quantity", "discount"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Fill nulls in critical columns
    df["profit"]   = df["profit"].fillna(0)
    df["discount"] = df["discount"].fillna(0)

    print(f"[✓] Clean data: {len(df):,} rows")
    return df


def feature_engineering(df: pd.DataFrame) -> pd.DataFrame:
    """Derive columns used by DAX measures and Power BI visuals."""
    # Date parts
    df["order_year"]    = df["order_date"].dt.year
    df["order_month"]   = df["order_date"].dt.month
    df["order_quarter"] = df["order_date"].dt.quarter
    df["order_monthname"] = df["order_date"].dt.strftime("%b")
    df["order_yearmonth"] = df["order_date"].dt.to_period("M").astype(str)

    # Shipping lead time (days)
    if "ship_date" in df.columns:
        df["shipping_days"] = (df["ship_date"] - df["order_date"]).dt.days

    # Profitability metrics
    df["profit_margin_pct"] = np.where(
        df["sales"] != 0,
        (df["profit"] / df["sales"]) * 100,
        0
    ).round(2)

    df["revenue_per_unit"] = np.where(
        df["quantity"] != 0,
        df["sales"] / df["quantity"],
        0
    ).round(2)

    # Profitability flag (useful for conditional formatting in Power BI)
    df["is_profitable"] = df["profit"] > 0

    # Discount bucket
    df["discount_band"] = pd.cut(
        df["discount"],
        bins=[-0.001, 0.0, 0.1, 0.2, 0.3, 1.0],
        labels=["No Discount", "0–10%", "10–20%", "20–30%", "30%+"]
    )

    print("[✓] Feature engineering complete")
    return df


def export_data(df: pd.DataFrame, csv_path: str, excel_path: str) -> None:
    """Export cleaned data to CSV (Power BI source) and summary Excel."""
    df.to_csv(csv_path, index=False)
    print(f"[✓] Cleaned CSV → {csv_path}")

    # Summary sheets for quick validation
    with pd.ExcelWriter(excel_path, engine="openpyxl") as writer:
        # Regional summary
        region_col = next((c for c in ["region", "market"] if c in df.columns), None)
        if region_col:
            regional = (
                df.groupby(region_col)
                  .agg(total_sales=("sales", "sum"),
                       total_profit=("profit", "sum"),
                       orders=("order_id", "nunique") if "order_id" in df.columns else ("sales", "count"),
                       avg_margin=("profit_margin_pct", "mean"))
                  .round(2)
                  .reset_index()
            )
            regional.to_excel(writer, sheet_name="Regional_Summary", index=False)

        # Yearly summary
        yearly = (
            df.groupby("order_year")
              .agg(total_sales=("sales", "sum"),
                   total_profit=("profit", "sum"),
                   avg_margin=("profit_margin_pct", "mean"))
              .round(2)
              .reset_index()
        )
        yearly.to_excel(writer, sheet_name="Yearly_Summary", index=False)

        # Category summary
        cat_col = next((c for c in ["category", "sub_category"] if c in df.columns), None)
        if cat_col:
            cat = (
                df.groupby(cat_col)
                  .agg(total_sales=("sales", "sum"),
                       total_profit=("profit", "sum"),
                       avg_margin=("profit_margin_pct", "mean"))
                  .round(2)
                  .reset_index()
            )
            cat.to_excel(writer, sheet_name="Category_Summary", index=False)

    print(f"[✓] Summary Excel → {excel_path}")


def run():
    print("=" * 55)
    print("  Retail Sales Analytics — ETL Pipeline")
    print("=" * 55)
    df = load_data(RAW_PATH)
    df = clean_data(df)
    df = feature_engineering(df)
    export_data(df, OUTPUT_PATH, SUMMARY_PATH)

    # Quick sanity check
    print("\n── Data Preview ───────────────────────────────────────")
    print(df[["order_date", "sales", "profit", "profit_margin_pct",
              "order_year", "shipping_days"]].head(5).to_string(index=False))
    print("\n── Null Check ─────────────────────────────────────────")
    nulls = df.isnull().sum()
    print(nulls[nulls > 0].to_string() if nulls.any() else "No nulls found ✓")
    print("\n[✓] ETL complete — load superstore_clean.csv into Power BI")


if __name__ == "__main__":
    run()
