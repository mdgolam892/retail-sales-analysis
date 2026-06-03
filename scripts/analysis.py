"""
analysis.py — Retail Sales Analytics
Generates KPI summaries, YoY growth metrics, and profitability breakdowns
from the cleaned dataset. Outputs are saved as Excel sheets for reference
and validation alongside the Power BI dashboard.
"""

import pandas as pd
import numpy as np
import os

CLEAN_PATH   = os.path.join(os.path.dirname(__file__), "../data/superstore_clean.csv")
ANALYSIS_OUT = os.path.join(os.path.dirname(__file__), "../data/analysis_output.xlsx")


# ── Load ───────────────────────────────────────────────────────────────────
def load_clean(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, parse_dates=["order_date", "ship_date"])
    print(f"[✓] Loaded clean data: {len(df):,} rows")
    return df


# ── KPIs ───────────────────────────────────────────────────────────────────
def overall_kpis(df: pd.DataFrame) -> pd.DataFrame:
    """Top-level KPIs across the full dataset."""
    order_col = "order_id" if "order_id" in df.columns else None
    kpis = {
        "Total Revenue ($)":       round(df["sales"].sum(), 2),
        "Total Profit ($)":        round(df["profit"].sum(), 2),
        "Avg Profit Margin (%)":   round(df["profit_margin_pct"].mean(), 2),
        "Total Orders":            df[order_col].nunique() if order_col else len(df),
        "Total Quantity Sold":     int(df["quantity"].sum()),
        "Avg Discount (%)":        round(df["discount"].mean() * 100, 2),
        "Avg Shipping Days":       round(df["shipping_days"].mean(), 1) if "shipping_days" in df.columns else "N/A",
        "% Profitable Orders":     round((df["is_profitable"].sum() / len(df)) * 100, 2),
    }
    return pd.DataFrame(list(kpis.items()), columns=["KPI", "Value"])


# ── YoY ────────────────────────────────────────────────────────────────────
def yoy_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """Year-over-Year Sales, Profit, and Order growth."""
    order_col = "order_id" if "order_id" in df.columns else None
    agg = {"sales": "sum", "profit": "sum"}
    if order_col:
        agg[order_col] = "nunique"

    yearly = df.groupby("order_year").agg(agg).reset_index()
    yearly.columns = ["Year", "Revenue", "Profit"] + (["Orders"] if order_col else [])
    yearly = yearly.sort_values("Year")

    # YoY growth %
    for col in ["Revenue", "Profit"] + (["Orders"] if order_col else []):
        yearly[f"{col} YoY (%)"] = yearly[col].pct_change().mul(100).round(2)

    yearly["Profit Margin (%)"] = (yearly["Profit"] / yearly["Revenue"] * 100).round(2)
    return yearly


# ── Regional ───────────────────────────────────────────────────────────────
def regional_analysis(df: pd.DataFrame) -> pd.DataFrame:
    region_col = next((c for c in ["region", "market"] if c in df.columns), None)
    if not region_col:
        print("[!] No region/market column found — skipping regional analysis")
        return pd.DataFrame()

    order_col = "order_id" if "order_id" in df.columns else None
    agg = {
        "sales":              "sum",
        "profit":             "sum",
        "quantity":           "sum",
        "profit_margin_pct":  "mean",
        "discount":           "mean",
    }
    if order_col:
        agg[order_col] = "nunique"

    regional = df.groupby(region_col).agg(agg).reset_index()
    regional.columns = ([region_col.title(), "Revenue", "Profit",
                         "Qty Sold", "Avg Margin (%)", "Avg Discount"]
                        + (["Orders"] if order_col else []))
    regional["Revenue"]       = regional["Revenue"].round(2)
    regional["Profit"]        = regional["Profit"].round(2)
    regional["Avg Margin (%)"] = regional["Avg Margin (%)"].round(2)
    regional["Avg Discount"]  = (regional["Avg Discount"] * 100).round(2)
    regional = regional.sort_values("Revenue", ascending=False)

    # Flag underperformers (below-median margin)
    median_margin = regional["Avg Margin (%)"].median()
    regional["Performance Flag"] = np.where(
        regional["Avg Margin (%)"] < median_margin, "⚠ Underperformer", "✓ On Target"
    )
    return regional


# ── Channel / Segment ──────────────────────────────────────────────────────
def channel_analysis(df: pd.DataFrame) -> pd.DataFrame:
    seg_col = next((c for c in ["segment", "ship_mode", "channel"] if c in df.columns), None)
    if not seg_col:
        return pd.DataFrame()

    channel = (
        df.groupby(seg_col)
          .agg(revenue=("sales", "sum"),
               profit=("profit", "sum"),
               avg_margin=("profit_margin_pct", "mean"),
               orders=("sales", "count"))
          .round(2)
          .reset_index()
    )
    channel["revenue_share (%)"] = (channel["revenue"] / channel["revenue"].sum() * 100).round(2)
    return channel.sort_values("revenue", ascending=False)


# ── Category deep-dive ──────────────────────────────────────────────────────
def category_analysis(df: pd.DataFrame) -> pd.DataFrame:
    cols = [c for c in ["category", "sub_category"] if c in df.columns]
    if not cols:
        return pd.DataFrame()

    cat = (
        df.groupby(cols)
          .agg(revenue=("sales", "sum"),
               profit=("profit", "sum"),
               qty=("quantity", "sum"),
               avg_margin=("profit_margin_pct", "mean"),
               avg_discount=("discount", "mean"))
          .round(2)
          .reset_index()
    )
    cat["avg_discount"] = (cat["avg_discount"] * 100).round(2)
    return cat.sort_values("profit", ascending=False)


# ── Discount impact ─────────────────────────────────────────────────────────
def discount_impact(df: pd.DataFrame) -> pd.DataFrame:
    if "discount_band" not in df.columns:
        return pd.DataFrame()
    d = (
        df.groupby("discount_band", observed=True)
          .agg(orders=("sales", "count"),
               revenue=("sales", "sum"),
               profit=("profit", "sum"),
               avg_margin=("profit_margin_pct", "mean"))
          .round(2)
          .reset_index()
    )
    return d


# ── Monthly trend ───────────────────────────────────────────────────────────
def monthly_trend(df: pd.DataFrame) -> pd.DataFrame:
    trend = (
        df.groupby("order_yearmonth")
          .agg(revenue=("sales", "sum"),
               profit=("profit", "sum"))
          .round(2)
          .reset_index()
          .sort_values("order_yearmonth")
    )
    trend["rolling_3m_revenue"] = trend["revenue"].rolling(3, min_periods=1).mean().round(2)
    return trend


# ── Export ──────────────────────────────────────────────────────────────────
def export_analysis(sheets: dict, path: str) -> None:
    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        for sheet_name, df_sheet in sheets.items():
            if df_sheet is not None and not df_sheet.empty:
                df_sheet.to_excel(writer, sheet_name=sheet_name[:31], index=False)
    print(f"[✓] Analysis exported → {path}")


# ── Main ────────────────────────────────────────────────────────────────────
def run():
    print("=" * 55)
    print("  Retail Sales Analytics — Analysis")
    print("=" * 55)

    df = load_clean(CLEAN_PATH)

    kpis     = overall_kpis(df)
    yoy      = yoy_metrics(df)
    regional = regional_analysis(df)
    channel  = channel_analysis(df)
    category = category_analysis(df)
    discount = discount_impact(df)
    monthly  = monthly_trend(df)

    # Print to console
    print("\n── Overall KPIs ───────────────────────────────────────")
    print(kpis.to_string(index=False))

    print("\n── YoY Metrics ────────────────────────────────────────")
    print(yoy.to_string(index=False))

    if not regional.empty:
        print("\n── Regional Performance ───────────────────────────────")
        print(regional.to_string(index=False))

    export_analysis({
        "KPIs":             kpis,
        "YoY_Metrics":      yoy,
        "Regional":         regional,
        "Channel_Segment":  channel,
        "Category":         category,
        "Discount_Impact":  discount,
        "Monthly_Trend":    monthly,
    }, ANALYSIS_OUT)

    print("\n[✓] Analysis complete — review analysis_output.xlsx")


if __name__ == "__main__":
    run()


if __name__ == "__main__":
    run()
