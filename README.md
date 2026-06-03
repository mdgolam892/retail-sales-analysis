# Retail Sales Analytics Dashboard
### Power BI · Python · Pandas · DAX

An end-to-end sales analytics project built on the **Global Superstore** dataset. I designed and developed a 4-page interactive Power BI dashboard to analyse 10,000+ rows of multi-year transactional data, uncovering profitability trends across regions, product categories, and customer segments.

---

## Project Background

Working with raw retail order data, I wanted to build something that goes beyond basic bar charts — a dashboard that regional managers could actually use to make decisions. The key questions I set out to answer:

- Which regions are underperforming on profit margin?
- How has revenue grown year-over-year, and is that growth consistent?
- Which product sub-categories are being sold at a loss due to heavy discounting?
- What does the shipping behaviour look like across different ship modes?

---

## What I Built

### ETL Pipeline (`scripts/etl.py`)
I wrote a Pandas pipeline to clean and transform the raw CSV before loading it into Power BI:
- Standardised column names and data types
- Parsed order and ship dates, derived `shipping_days`
- Engineered new columns: `profit_margin_pct`, `revenue_per_unit`, `discount_band`, `order_yearmonth`
- Exported a clean CSV for Power BI ingestion and a summary Excel for validation

### Analysis Script (`scripts/analysis.py`)
A standalone Python script that generates KPI summaries, YoY growth tables, regional breakdowns, and discount impact analysis — exported to Excel as a reference alongside the dashboard.

### Power BI Dashboard (4 pages)
Built entirely in Power BI Desktop with custom DAX measures and interactive slicers synced across all pages.

---

## Dashboard Pages

### Page 1 — Executive Overview
High-level KPIs with year-over-year context for quick executive consumption.

![Executive Overview](dashboard/screenshots/page1_executive_overview.png)

- **KPI Cards**: Total Revenue (12.64M), Total Profit (1.47M), Profit Margin % (11.61%), Total Orders (25K) — each with YoY % as additional value
- **Revenue & Profit Trend**: Line chart over `order_yearmonth` showing both measures across 4 years
- **Regional Revenue**: Clustered bar comparing Total Revenue and Total Profit by region
- **Segment Share**: Donut chart — Consumer (51.48%), Corporate (30.25%), Home Office (18.27%)
- **Profit Margin Matrix**: `order_year` × `region` heatmap with red-to-green conditional formatting

---

### Page 2 — Regional Deep Dive
Built for regional managers to identify underperformers at a glance.

![Regional Deep Dive](dashboard/screenshots/page2_regional_deep_dive.png)

- **World Map**: Bubble map sized by Total Revenue with colour encoding by margin — red clusters immediately visible in loss-making areas
- **Margin Bar Chart**: Regions sorted by Profit Margin % with gradient colouring (red → green) — Southeast Asia (2.02%) and EMEA (5.45%) clearly flagged
- **Performance Table**: Region | Revenue | Profit | Margin % | Orders | Avg Discount % with conditional formatting
- **Revenue Trend Line**: Monthly revenue filtered dynamically by year/region slicers

---

### Page 3 — Product & Category Analysis
Focused on understanding which products drive revenue vs which ones erode margin.

![Product & Category Analysis](dashboard/screenshots/page3_product_category.png)

- **Revenue Treemap**: Category → Sub-category hierarchy showing Phones (1.71M) and Copiers (1.51M) dominating Technology
- **Top Sub-categories Bar**: Horizontal bar filtered to Top 10 by revenue
- **Discount vs Margin Scatter**: The most insightful visual — 17 dots (one per sub-category) with a trend line and break-even reference line at Y=0. Tables sits at ~30% discount with -0.09 margin, proving discount-driven margin erosion
- **Profit Waterfall**: Sub-category contribution to total profit — Tables is the only red (decrease) bar

---

### Page 4 — YoY & Trend Analysis
Revenue growth patterns over time with shipping behaviour analysis.

![YoY & Trend Analysis](dashboard/screenshots/page4_yoy_trend_analysis.png)

- **YoY Combo Chart**: Clustered columns for annual revenue with line overlay showing YoY growth rate (18.5% → 27.2% → 26.3%)
- **Monthly Small Multiples**: 4 panels (one per year) showing Jan–Dec revenue pattern — Q4 spike visible across all years
- **Revenue YTD Card**: 4.30M cumulative
- **Shipping Analysis**: Standard Class handles 60%+ of orders (15,154) with avg 5-day lead time vs Same Day at 0 days

---

## DAX Measures

I wrote 13 custom DAX measures organised in a `_Measures` display folder. Key ones:

| Measure | Purpose |
|---|---|
| `Profit Margin %` | `DIVIDE(profit, sales, 0)` — safe division, no error on zero sales |
| `Revenue YoY %` | Year-over-year growth using `MAX(order_year)` context — works on combo chart and card |
| `Latest Year Revenue YoY %` | Uses `MAXX(ALL(...))` to always return 2014 vs 2013, ignoring slicer context |
| `Revenue YTD` | `TOTALYTD` against Date table for cumulative tracking |
| `Revenue 3M Rolling Avg` | Custom rolling average using `order_yearmonth` string — no Date table dependency |
| `Underperformer Flag` | `REMOVEFILTERS` on region to compare each region against global average margin |

Full DAX with inline comments: [`powerbi/dax_measures.dax`](powerbi/dax_measures.dax)

---

## Key Findings

- **Central region** generates the highest revenue (2.82M) but profit is disproportionately lower — driven by high average discount (13.89%)
- **Canada** has the highest profit margin (26.62%) with 0% average discount — confirms discounting directly erodes margin
- **Southeast Asia** is the worst performer at 2.02% margin with 27.21% average discount — clear underperformer
- **Tables** sub-category operates at negative margin (~-9%) at its current discount level of ~30% — should be reviewed for pricing strategy
- **Q4 revenue spike** is consistent across all 4 years — seasonal demand pattern useful for inventory planning
- **Standard Class** shipping accounts for 60.5% of all orders with an average 5-day lead time

---

## Tech Stack

| Layer | Tool |
|---|---|
| Data cleaning & transformation | Python 3, Pandas, NumPy |
| Feature engineering | Pandas (derived columns in ETL) |
| Dashboard & visualisation | Power BI Desktop |
| Business logic & metrics | DAX (11 custom measures) |
| Output validation | openpyxl (Excel summaries) |
| Dataset | Global Superstore — Kaggle |

---

## Project Structure

```
retail-sales-analytics/
│
├── data/
│   ├── Superstore.csv               ← Raw dataset (download from Kaggle)
│   ├── superstore_clean.csv         ← Generated by etl.py → load into Power BI
│   ├── superstore_summary.xlsx      ← Generated by etl.py
│   └── analysis_output.xlsx         ← Generated by analysis.py
│
├── scripts/
│   ├── etl.py                       ← ETL pipeline (run first)
│   └── analysis.py                  ← KPI & profitability analysis
│
├── dashboard/
│   ├── RetailSalesAnalytics.pbix    ← Power BI dashboard
│   ├── dax_measures.dax             ← All DAX measures with comments
│   └── screenshots/                     ← Dashboard page screenshots
│
├── requirements.txt
└── README.md
```

---

## How to Run

```bash
# 1. Clone the repo
git clone https://github.com/YOUR_USERNAME/retail-sales-analytics.git
cd retail-sales-analytics

# 2. Install dependencies
pip install -r requirements.txt

# 3. Add the dataset
# Download from https://www.kaggle.com/datasets/vivek468/superstore-dataset-final
# Save as data/Superstore.csv

# 4. Run ETL
python scripts/etl.py

# 5. (Optional) Run analysis
python scripts/analysis.py

# 6. Open Power BI
# Load data/superstore_clean.csv into Power BI Desktop
# Open powerbi/RetailSalesAnalytics.pbix
```

---

## Dataset

**Global Superstore** — [Kaggle](https://www.kaggle.com/datasets/vivek468/superstore-dataset-final)
- 10,000+ order line items across 4 years (2011–2014)
- Fields: Order ID, Dates, Customer, Segment, Region, Product, Category, Sales, Profit, Quantity, Discount, Ship Mode

---

## License

MIT License — see [LICENSE](LICENSE) for details.
