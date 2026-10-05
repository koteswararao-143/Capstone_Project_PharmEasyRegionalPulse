"""PharmEasy Regional Pulse - local Streamlit dashboard.

The dashboard reads the cleaned order data and SQLite-backed metrics produced by
Parts 1 and 2. It intentionally keeps the visual hierarchy simple: KPI overview,
category mix, regional trend/comparison, then a detailed regional-month table.
"""

from __future__ import annotations

from pathlib import Path
import sqlite3

import pandas as pd
import plotly.express as px
import streamlit as st

from draft_report import draft_report_v1
from metrics_engine import compute_mom_changes, flag_significant_regions_v1

ROOT = Path(__file__).resolve().parent
DB_PATH = ROOT / "pharmeasy.db"

st.set_page_config(
    page_title="PharmEasy Regional Pulse",
    page_icon="📊",
    layout="wide",
)


@st.cache_data
def load_orders() -> pd.DataFrame:
    with sqlite3.connect(DB_PATH) as con:
        frame = pd.read_sql_query(
            """
            SELECT order_id, order_date, region, category, product,
                   quantity, sales_inr, profit_inr
            FROM orders_clean
            ORDER BY order_date, order_id
            """,
            con,
        )
    frame["order_date"] = pd.to_datetime(frame["order_date"])
    frame["month"] = frame["order_date"].dt.to_period("M").astype(str)
    return frame


@st.cache_data
def load_region_month() -> pd.DataFrame:
    with sqlite3.connect(DB_PATH) as con:
        frame = pd.read_sql_query(
            """
            SELECT r.region,
                   substr(o.order_date, 1, 7) AS month,
                   COALESCE(SUM(o.sales_inr), 0) AS sales_inr,
                   COALESCE(SUM(o.profit_inr), 0) AS profit_inr,
                   COUNT(DISTINCT o.order_id) AS order_count
            FROM regions_master r
            LEFT JOIN orders_clean o
              ON r.region = o.region
            GROUP BY r.region, substr(o.order_date, 1, 7)
            ORDER BY r.region, month
            """,
            con,
        )
    months = ["2026-04", "2026-05", "2026-06"]
    regions = sorted(frame["region"].unique())
    grid = pd.MultiIndex.from_product(
        [regions, months], names=["region", "month"]
    ).to_frame(index=False)
    frame["month"] = frame["month"].fillna("2026-04")
    frame["sales_inr"] = frame["sales_inr"].fillna(0.0)
    frame["profit_inr"] = frame["profit_inr"].fillna(0.0)
    frame["order_count"] = frame["order_count"].fillna(0).astype(int)
    frame = frame.groupby(["region", "month"], as_index=False)[
        ["sales_inr", "profit_inr", "order_count"]
    ].sum()
    # Complete the region × month grid, retaining zero-order Kurnool.
    return grid.merge(frame, on=["region", "month"], how="left").fillna(0)


def money(value: float) -> str:
    return f"₹{value:,.2f}"


orders = load_orders()
region_month = load_region_month()

regions = ["All regions"] + sorted(region_month["region"].unique().tolist())
selected_region = st.sidebar.selectbox("Region filter", regions)

if selected_region == "All regions":
    view_orders = orders.copy()
    view_region_month = region_month.copy()
else:
    view_orders = orders[orders["region"] == selected_region].copy()
    view_region_month = region_month[region_month["region"] == selected_region].copy()

# ---------- Executive summary ----------
# These values are intentionally computed from the same cleaned data used below.
total_sales = float(view_orders["sales_inr"].sum())
total_profit = float(view_orders["profit_inr"].sum())
total_orders = int(view_orders["order_id"].nunique())

monthly_sales = (
    view_orders.groupby("month", as_index=False)["sales_inr"]
    .sum()
    .sort_values("month")
)
if len(monthly_sales) >= 2:
    latest = float(monthly_sales.iloc[-1]["sales_inr"])
    previous = float(monthly_sales.iloc[-2]["sales_inr"])
    latest_change = 0 if previous == 0 else (latest - previous) / previous * 100
else:
    latest_change = 0.0

if selected_region == "All regions":
    april_may = region_month[region_month["month"].isin(["2026-04", "2026-05"])].groupby("month")["sales_inr"].sum()
    if "2026-04" in april_may.index and "2026-05" in april_may.index:
        overall_am = (april_may["2026-05"] - april_may["2026-04"]) / april_may["2026-04"] * 100
    else:
        overall_am = 0.0
    headline = f"The dashboard covers {total_orders:,} distinct orders and {money(total_sales)} in sales."
    trend_sentence = f"Across all regions, April→May sales changed {overall_am:+.2f}%, while the latest month-to-month movement is {latest_change:+.2f}%."
    breakdown_sentence = "Use the category chart and regional trend below to identify where the movement is concentrated."
else:
    headline = f"{selected_region} has {total_orders:,} distinct orders and {money(total_sales)} in sales."
    trend_sentence = f"Its latest month-to-month sales movement is {latest_change:+.2f}%."
    breakdown_sentence = "The category view shows which product areas contribute to the selected region's sales."

implication_sentence = "Treat large month-to-month movements as review signals, then use the detail table to investigate before taking action."

st.title("PharmEasy Regional Pulse")
st.caption("Regional performance intelligence | April–June 2026 | SQL-backed local data")

st.subheader("Executive summary")
st.info(" ".join([headline, trend_sentence, breakdown_sentence, implication_sentence]))

# ---------- CII narrative ----------
changes = compute_mom_changes(DB_PATH)
if selected_region == "All regions":
    cii_regions = sorted(set(
        region
        for transition in changes.values()
        for region in flag_significant_regions_v1(transition, threshold=8)
    ))
else:
    cii_regions = [selected_region]

cii_blocks = draft_report_v1(cii_regions, changes)
with st.expander("CII narrative — what should a regional lead take away?", expanded=True):
    if selected_region == "All regions":
        st.caption("Flagged regions are based on the Part 2 absolute month-over-month threshold of >8%.")
    for block in cii_blocks:
        st.markdown(f"**{block['region']}**")
        st.markdown(f"**Context:** {block['Context']}")
        st.markdown(f"**Insight:** {block['Insight']}")
        st.markdown(f"**Implication:** {block['Implication']}")
        st.divider()

# ---------- Overview level ----------
k1, k2, k3 = st.columns(3)
k1.metric("Total sales (INR)", money(total_sales))
k2.metric("Total profit (INR)", money(total_profit))
k3.metric("Distinct order count", f"{total_orders:,}")

st.divider()

# ---------- Category level ----------
st.subheader("Category level — which category drives sales?")
category_sales = (
    view_orders.groupby("category", as_index=False)["sales_inr"]
    .sum()
    .sort_values("sales_inr", ascending=False)
)

fig_category = px.bar(
    category_sales,
    x="category",
    y="sales_inr",
    title="Which categories contribute the most sales?",
    labels={"category": "Category", "sales_inr": "Sales (INR)"},
)
fig_category.update_layout(showlegend=False, xaxis_tickangle=-25)
st.plotly_chart(fig_category, use_container_width=True)

# ---------- Trend + comparison ----------
left, right = st.columns(2)

with left:
    st.subheader("Trend level — how did sales move by month?")
    trend_source = view_orders.copy()
    if selected_region == "All regions":
        trend_source = trend_source.groupby(["month", "region"], as_index=False)["sales_inr"].sum()
    else:
        trend_source = trend_source.groupby(["month", "region"], as_index=False)["sales_inr"].sum()

    fig_line = px.line(
        trend_source,
        x="month",
        y="sales_inr",
        color="region",
        markers=True,
        title="How did monthly sales change across regions?",
        labels={"month": "Month", "sales_inr": "Sales (INR)", "region": "Region"},
    )
    fig_line.update_layout(legend_title_text="Region")
    st.plotly_chart(fig_line, use_container_width=True)

with right:
    st.subheader("Comparison level — which regions lead total sales?")
    region_totals = (
        orders.groupby("region", as_index=False)["sales_inr"]
        .sum()
        .sort_values("sales_inr", ascending=True)
    )
    if selected_region != "All regions":
        region_totals = region_totals[region_totals["region"] == selected_region]

    fig_bar = px.bar(
        region_totals,
        x="sales_inr",
        y="region",
        orientation="h",
        title="Which regions have the highest total sales?",
        labels={"region": "Region", "sales_inr": "Sales (INR)"},
    )
    fig_bar.update_layout(showlegend=False)
    st.plotly_chart(fig_bar, use_container_width=True)

# ---------- Part-of-whole ----------
st.subheader("Part-of-whole — what is the sales mix by category?")
fig_pie = px.pie(
    category_sales,
    names="category",
    values="sales_inr",
    hole=0.45,
    title="What share of sales comes from each category?",
)
fig_pie.update_traces(textposition="inside", textinfo="percent+label")
st.plotly_chart(fig_pie, use_container_width=True)

# ---------- Detail level ----------
st.subheader("Detail level — regional monthly evidence")
detail = view_region_month.copy()
detail = detail.sort_values(["region", "month"])
detail["sales_inr"] = detail["sales_inr"].round(2)
detail["profit_inr"] = detail["profit_inr"].round(2)
st.dataframe(
    detail[["region", "month", "sales_inr", "profit_inr", "order_count"]],
    use_container_width=True,
    hide_index=True,
    column_config={
        "region": "Region",
        "month": "Month",
        "sales_inr": st.column_config.NumberColumn("Sales (INR)", format="₹%.2f"),
        "profit_inr": st.column_config.NumberColumn("Profit (INR)", format="₹%.2f"),
        "order_count": st.column_config.NumberColumn("Distinct orders", format="%d"),
    },
)

st.caption("Source: local pharmeasy.db / orders_clean. No API keys or network access are required.")
