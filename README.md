# Retail Sales Analytics Dashboard
### Power BI · Python · Pandas · DAX

An end-to-end sales analytics project built on the **Global Superstore** dataset. I designed and developed a 5-page interactive Power BI dashboard to analyse 10,000+ rows of multi-year transactional data, uncovering profitability trends across regions, product categories, and customer segments — and closing with a written insights page that turns the analysis into concrete recommendations.

---

## Objective

To derive actionable business insights that help improve:
- Profitability and margin health by region and sub-category
- Product strategy — identifying top performers and loss-making lines
- Regional performance — spotting underperformers before they're a problem
- Customer and segment behaviour

---

## Project Background

Working with raw retail order data, I wanted to build something that goes beyond basic bar charts — a dashboard that regional managers could actually use to make decisions. The key questions I set out to answer:

- Which regions are underperforming on profit margin?
- How has revenue grown year-over-year, and is that growth consistent?
- Which product sub-categories are being sold at a loss due to heavy discounting?
- What does the shipping behaviour look like across different ship modes?
- Given everything above, what should actually change?

---

## What I Built

### ETL Pipeline (`scripts/etl.py`)
A Pandas pipeline to clean and transform the raw CSV before loading it into Power BI:
- Standardised column names and data types
- Parsed order and ship dates, derived `shipping_days`
- Engineered new columns: `profit_margin_pct`, `revenue_per_unit`, `discount_band`, `order_yearmonth`
- Exported a clean CSV for Power BI ingestion and a summary Excel for validation

### Analysis Script (`scripts/analysis.py`)
A standalone Python script that generates KPI summaries, YoY growth tables, regional breakdowns, and discount impact analysis — exported to Excel as a reference alongside the dashboard.

### Power BI Dashboard (5 pages)
Built entirely in Power BI Desktop with custom DAX measures and interactive slicers synced across all pages.

---

## Dashboard Pages

### Page 1 — Executive Overview
High-level KPIs with year-over-year context for quick executive consumption.

![Executive Overview](screenshots/page1_executive_overview.png)

- **KPI Cards** (with icons): Total Revenue (12.64M), Total Profit (1.47M), Profit Margin % (11.61%), Total Orders (25K) — each with YoY % built into the card itself, not just a static total
- **Revenue & Profit Trend**: Line chart over `order_yearmonth` showing both measures across 4 years
- **Regional Revenue**: Clustered bar comparing Total Revenue and Total Profit by region
- **Segment Share**: Donut chart — Consumer (51.48%), Corporate (30.25%), Home Office (18.27%)
- **Profit Margin Matrix**: `order_year` × `region` heatmap with red-to-green conditional formatting

---

### Page 2 — Regional Deep Dive
Built for regional managers to identify underperformers at a glance.

![Regional Deep Dive](screenshots/page2_regional_deep_dive.png)

- **World Map**: Bubble map sized by Total Revenue with colour encoding by margin — red clusters immediately visible in loss-making areas
- **Margin Bar Chart**: Regions sorted by Profit Margin % with gradient colouring (red → green) — Southeast Asia (2.02%) and EMEA (5.45%) clearly flagged
- **Performance Table**: Region | Revenue | Profit | Margin % | Orders | Avg Discount % — conditionally formatted to match Page 1's heatmap style for visual consistency
- **Revenue Trend Line**: Monthly revenue filtered dynamically by year/region slicers

---

### Page 3 — Product & Category Analysis
Focused on understanding which products drive revenue vs which ones erode margin.

![Product & Category Analysis](screenshots/page3_product_category.png)

- **Revenue Treemap**: Category → Sub-category hierarchy showing Phones (1.71M) and Copiers (1.51M) dominating Technology
- **Top 10 Products by Sales**: Horizontal bar, colour-coded green, surfacing the biggest revenue drivers by name
- **Bottom 10 Products by Profit**: Horizontal bar, colour-coded red — surfaces loss-making products by name rather than burying them in an aggregate
- **Discount vs Margin Scatter**: The most insightful visual — one dot per sub-category with a trend line and break-even reference line at Y=0. Tables sits at ~30% discount with -9% margin, proving discount-driven margin erosion
- **Profit Waterfall**: Sub-category contribution to total profit — Tables is the only red (decrease) bar

---

### Page 4 — YoY & Trend Analysis
Revenue growth patterns over time with shipping behaviour analysis.

![YoY & Trend Analysis](screenshots/page4_yoy_trend_analysis.png)

- **YoY Combo Chart**: Clustered columns for annual revenue with line overlay showing YoY growth rate (18.5% → 27.2% → 26.3%)
- **Monthly Small Multiples**: 4 panels (one per year) showing Jan–Dec revenue pattern — Q4 spike visible across all years
- **Revenue YTD Card**: 4.30M cumulative
- **Shipping Analysis**: Standard Class handles 60%+ of orders (15,154) with avg 5-day lead time vs Same Day at 0 days

---

### Page 5 — Strategic Business Insights
The page that turns the dashboard from "here's what happened" into "here's what to do about it."

![Strategic Business Insights](screenshots/page5_strategic_insights.png)

- **Findings panel**: Six written insights, each anchored to specific numbers already shown on Pages 1–4 (e.g. *"Southeast Asia: 2.02% profit margin despite 1,517 orders and 27.21% avg discount — heaviest discounting actively destroying margin"*)
- **Recommendations panel**: A paired action for each finding (e.g. *"Cap discount at 15% for Tables and other negative-margin sub-categories"*)
- **4 headline stat cards**: Top Region by Margin (Canada — 26.62%), Top Category by Profit (Technology — 664K), Strongest YoY Growth (2013 — +27.2%), Margin Risk to Watch (Southeast Asia — 2.02%)

This page exists because raw charts answer *what happened*; stakeholders also need *so what*. Every insight here is read directly off a number already visible elsewhere in the dashboard — nothing here is speculative.

---

## DAX Measures

20+ custom DAX measures organised by page/purpose, including YoY logic baked into KPI cards, Top N/Bottom N product ranking, and dynamic "winner" measures that power the Strategic Insights cards. Key ones:

| Measure | Purpose |
|---|---|
| `Profit Margin %` | `DIVIDE(profit, sales, 0)` — safe division, no error on zero sales |
| `Latest Year Revenue YoY %` | Always compares the most recent year vs prior year, regardless of slicer context |
| `Product Rank by Sales` / `Product Rank by Profit` | Powers the Top 10 / Bottom 10 product visuals on Page 3 |
| `Top Region by Margin Name/Value` | Dynamically finds the best-margin region for the Page 5 headline card — updates automatically if data changes |
| `Margin Risk Region Name/Value` | Dynamically finds the worst-margin region — same logic, opposite direction |
| `Avg Order Value` / `Orders per Customer` | Customer behaviour metrics |
| `Revenue YTD` | `TOTALYTD` against the date table for cumulative tracking |

Full DAX with inline comments: [`powerbi/dax_measures.dax`](powerbi/dax_measures.dax)

---

## Key Findings

- **Southeast Asia**: 2.02% profit margin despite 1,517 orders and a 27.21% average discount — the heaviest discounting in the dataset, actively destroying margin
- **Central region**: highest order volume (5,249 orders, 2.82M revenue) but only 11.03% margin — versus Canada's 26.62% margin on just 201 orders, exposing an efficiency gap at scale
- **Revenue grew** from 2.3M (2011) to 4.3M (2014), a sustained climb — yet profit margin held flat at 11–12% throughout, meaning growth hasn't translated into better unit economics
- **Tables** sub-category turns negative (~-9% margin) at ~30% discount — the only loss-making line on the profit waterfall
- **EMEA** (5.45%) and **Southeast Asia** (2.02%) are the two lowest-margin regions, both well below the 11.61% portfolio average
- **Standard Class** shipping handles 60.5% of all 25K orders at a 5-day average lead time — the widest customer-impact area if delayed

**Recommendations arising from these findings:**
- Cap discount at 15% for Tables and other negative-margin sub-categories
- Investigate Southeast Asia's discount policy — bring the 27% average down toward the 11.61% portfolio benchmark
- Replicate Canada's low-discount, high-margin model in comparable mid-size regions
- Pre-stock inventory and shipping capacity ahead of the recurring Q4 demand spike
- Set a minimum margin floor per sub-category to prevent revenue growth from masking margin erosion

---

## Tech Stack

| Layer | Tool |
|---|---|
| Data cleaning & transformation | Python 3, Pandas, NumPy |
| Feature engineering | Pandas (derived columns in ETL) |
| Dashboard & visualisation | Power BI Desktop |
| Business logic & metrics | DAX (20+ custom measures) |
| Output validation | openpyxl (Excel summaries) |
| Dataset | Global Superstore — Kaggle |

---

## Project Structure

```
retail-sales-analytics/
│
├── data/                          ← add Superstore.csv here (download from Kaggle)
│
├── scripts/
│   ├── etl.py                     ← ETL pipeline (run first)
│   └── analysis.py                ← KPI & profitability analysis
│
├── powerbi/
│   ├── RetailSalesAnalytics.pbix  ← Power BI dashboard
│   ├── dax_measures.dax           ← All DAX measures with comments
│   └── POWERBI_BUILD_GUIDE.md     ← Step-by-step build guide
│
├── screenshots/                   ← dashboard page screenshots (5 pages)
│
├── README.md
├── LICENSE
├── UPLOAD_TO_GIT.md
├── requirements.txt
└── .gitignore
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
# Load the cleaned CSV into Power BI Desktop
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

---

## Contact

**MD GOLAM MOHIUDDIN**
📧 mdgolammohiuddin892@gmail.com
🌐 [LinkedIn](https://www.linkedin.com/in/md-golam-mohiuddin-980b18150/)
