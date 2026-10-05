# app.py
import streamlit as st
import pandas as pd
import plotly.express as px

orders = pd.read_csv("orders_clean.csv")

order_count = orders["order_id"].nunique()
total_sales = orders["sales_inr"].sum()
total_profit = orders["profit_inr"].sum()

st.title("PharmEasy Regional Pulse Dashboard")
st.metric("Total Sales (₹)", f"{total_sales:,.2f}")
st.metric("Total Profit (₹)", f"{total_profit:,.2f}")
st.metric("Total Orders", order_count)

regions = orders["region"].unique()
selected_region = st.selectbox("Select region:", regions)
filtered = orders[orders["region"] == selected_region]

cat_summary = filtered.groupby("category")["sales_inr"].sum().reset_index()
st.plotly_chart(px.pie(cat_summary, names="category", values="sales_inr", title="Sales share by category"))

filtered["month"] = filtered["order_date"].str.slice(0,7)
trend = filtered.groupby("month")["sales_inr"].sum().reset_index()
st.plotly_chart(px.line(trend, x="month", y="sales_inr", title=f"Monthly sales trend for {selected_region}"))

region_sales = orders.groupby("region")["sales_inr"].sum().reset_index()
st.plotly_chart(px.bar(region_sales, x="region", y="sales_inr", title="Total sales by region"))

detail = filtered.groupby(["month","region"]).agg(
    {"sales_inr":"sum","profit_inr":"sum","order_id":"nunique"}).reset_index()
st.write("Per-region, per-month detail:")
st.dataframe(detail)
