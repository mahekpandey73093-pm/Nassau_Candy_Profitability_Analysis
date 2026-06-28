import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

st.set_page_config(
    page_title="Nassau Candy Profitability Dashboard",
    page_icon="🍬",
    layout="wide"
)

# ---------------- CSS ---------------- #

st.markdown("""
<style>

.stApp{
background:#F5F7FA;
}

.main-title{
font-size:40px;
font-weight:bold;
color:white;
text-align:center;
padding:20px;
background:linear-gradient(90deg,#5B2C6F,#8E44AD,#3498DB);
border-radius:15px;
}

.kpi{
background:white;
padding:20px;
border-radius:15px;
box-shadow:0px 4px 15px rgba(0,0,0,0.15);
}

</style>
""",unsafe_allow_html=True)

st.markdown("""
<div class='main-title'>
🍬 Product Line Profitability & Margin Performance Dashboard
</div>
""",unsafe_allow_html=True)

# ---------------- Load Dataset ---------------- #

df = pd.read_csv("Nassau Candy Distributor.csv")

# ---------------- Cleaning ---------------- #

df=df.dropna()

df["Order Date"] = pd.to_datetime(
    df["Order Date"],
    dayfirst=True,
    errors="coerce"
)

df["Ship Date"] = pd.to_datetime(
    df["Ship Date"],
    dayfirst=True,
    errors="coerce"
)

# Invalid dates remove kar do
df = df.dropna(subset=["Order Date", "Ship Date"])
df["Gross Margin %"]=(df["Gross Profit"]/df["Sales"])*100

df["Profit Per Unit"]=df["Gross Profit"]/df["Units"]

# ---------------- Sidebar ---------------- #

st.sidebar.header("Filters")

division=st.sidebar.multiselect(
"Division",
options=df["Division"].unique(),
default=df["Division"].unique()
)

region=st.sidebar.multiselect(
"Region",
options=df["Region"].unique(),
default=df["Region"].unique()
)

date=st.sidebar.date_input(
"Date Range",
[
df["Order Date"].min(),
df["Order Date"].max()
]
)

filtered=df[
(df["Division"].isin(division))&
(df["Region"].isin(region))
]

# ---------------- KPIs ---------------- #

total_sales=filtered["Sales"].sum()

total_profit=filtered["Gross Profit"].sum()

margin=(total_profit/total_sales)*100

products=filtered["Product Name"].nunique()

orders=filtered["Order ID"].nunique()

col1,col2,col3,col4,col5=st.columns(5)

col1.metric("Revenue",f"${total_sales:,.0f}")

col2.metric("Gross Profit",f"${total_profit:,.0f}")

col3.metric("Margin %",f"{margin:.2f}%")

col4.metric("Products",products)

col5.metric("Orders",orders)

st.markdown("---")


# ==========================================================
# PRODUCT PROFITABILITY DASHBOARD
# ==========================================================

st.header("📊 Product Profitability Overview")

tab1, tab2, tab3 = st.tabs(
[
"🏆 Top Products",
"📈 Profitability",
"📦 Revenue Contribution"
]
)

# ==========================================================
# TAB 1
# ==========================================================

with tab1:

    product_summary = (
        filtered
        .groupby("Product Name")
        .agg({
            "Sales":"sum",
            "Gross Profit":"sum",
            "Gross Margin %":"mean",
            "Units":"sum"
        })
        .reset_index()
    )

    top_profit = (
        product_summary
        .sort_values(
            "Gross Profit",
            ascending=False
        )
        .head(10)
    )

    fig = px.bar(
        top_profit,
        x="Gross Profit",
        y="Product Name",
        orientation="h",
        color="Gross Profit",
        title="Top 10 Products by Gross Profit",
        color_continuous_scale="Viridis"
    )

    fig.update_layout(
        height=550,
        yaxis=dict(categoryorder="total ascending")
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# ==========================================================
# TAB 2
# ==========================================================

with tab2:

    c1,c2 = st.columns(2)

    with c1:

        top_margin = (
            product_summary
            .sort_values(
                "Gross Margin %",
                ascending=False
            )
            .head(10)
        )

        fig = px.bar(
            top_margin,
            x="Gross Margin %",
            y="Product Name",
            orientation="h",
            color="Gross Margin %",
            title="Highest Margin Products",
            color_continuous_scale="Turbo"
        )

        fig.update_layout(
            height=550,
            yaxis=dict(
                categoryorder="total ascending"
            )
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    with c2:

        low_margin = (
            product_summary
            .sort_values(
                "Gross Margin %",
                ascending=True
            )
            .head(10)
        )

        fig = px.bar(
            low_margin,
            x="Gross Margin %",
            y="Product Name",
            orientation="h",
            color="Gross Margin %",
            title="Lowest Margin Products",
            color_continuous_scale="Reds"
        )

        fig.update_layout(
            height=550,
            yaxis=dict(
                categoryorder="total ascending"
            )
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

# ==========================================================
# TAB 3
# ==========================================================

with tab3:

    product_summary["Revenue Contribution"] = (
        product_summary["Sales"] /
        product_summary["Sales"].sum()
    ) * 100

    product_summary["Profit Contribution"] = (
        product_summary["Gross Profit"] /
        product_summary["Gross Profit"].sum()
    ) * 100

    c1,c2 = st.columns(2)

    with c1:

        top_revenue = (
            product_summary
            .sort_values(
                "Revenue Contribution",
                ascending=False
            )
            .head(10)
        )

        fig = px.pie(
            top_revenue,
            names="Product Name",
            values="Revenue Contribution",
            title="Revenue Contribution"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    with c2:

        top_profit = (
            product_summary
            .sort_values(
                "Profit Contribution",
                ascending=False
            )
            .head(10)
        )

        fig = px.pie(
            top_profit,
            names="Product Name",
            values="Profit Contribution",
            title="Profit Contribution"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

# ==========================================================
# PRODUCT LEADERBOARD
# ==========================================================

st.subheader("🏅 Product Profitability Leaderboard")

leaderboard = (
    product_summary
    .sort_values(
        "Gross Profit",
        ascending=False
    )
)

leaderboard = leaderboard.rename(
columns={
"Sales":"Revenue",
"Gross Profit":"Profit",
"Gross Margin %":"Margin %",
"Units":"Units Sold"
}
)

st.dataframe(
leaderboard,
use_container_width=True,
height=500
)

csv = leaderboard.to_csv(index=False)

st.download_button(
"📥 Download Product Leaderboard",
csv,
file_name="Product_Profitability.csv",
mime="text/csv"
)


# ==========================================================
# DIVISION PERFORMANCE DASHBOARD
# ==========================================================

st.markdown("---")
st.header("🏭 Division Performance Dashboard")

division_summary = (
    filtered
    .groupby("Division")
    .agg({
        "Sales":"sum",
        "Gross Profit":"sum",
        "Cost":"sum",
        "Units":"sum",
        "Gross Margin %":"mean"
    })
    .reset_index()
)

tab4, tab5, tab6 = st.tabs(
[
"📊 Division Overview",
"📈 Regional Analysis",
"📅 Monthly Trend"
]
)

# ==========================================================
# TAB 4
# ==========================================================

with tab4:

    c1, c2 = st.columns(2)

    with c1:

        fig = px.bar(
            division_summary,
            x="Division",
            y="Sales",
            color="Division",
            text_auto=".2s",
            title="Revenue by Division"
        )

        fig.update_layout(height=500)

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    with c2:

        fig = px.bar(
            division_summary,
            x="Division",
            y="Gross Profit",
            color="Division",
            text_auto=".2s",
            title="Profit by Division"
        )

        fig.update_layout(height=500)

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    st.markdown("### Division Summary")

    st.dataframe(
        division_summary,
        use_container_width=True
    )

# ==========================================================
# TAB 5
# ==========================================================

with tab5:

    region_summary = (
        filtered
        .groupby("Region")
        .agg({
            "Sales":"sum",
            "Gross Profit":"sum"
        })
        .reset_index()
    )

    c1, c2 = st.columns(2)

    with c1:

        fig = px.pie(
            region_summary,
            names="Region",
            values="Sales",
            hole=0.45,
            title="Revenue by Region"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    with c2:

        fig = px.bar(
            region_summary,
            x="Region",
            y="Gross Profit",
            color="Region",
            title="Profit by Region"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

# ==========================================================
# TAB 6
# ==========================================================

with tab6:

    monthly = (
        filtered
        .groupby(
            filtered["Order Date"].dt.to_period("M")
        )
        .agg({
            "Sales":"sum",
            "Gross Profit":"sum"
        })
        .reset_index()
    )

    monthly["Order Date"] = monthly[
        "Order Date"
    ].astype(str)

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=monthly["Order Date"],
            y=monthly["Sales"],
            mode="lines+markers",
            name="Revenue"
        )
    )

    fig.add_trace(
        go.Scatter(
            x=monthly["Order Date"],
            y=monthly["Gross Profit"],
            mode="lines+markers",
            name="Profit"
        )
    )

    fig.update_layout(
        title="Monthly Revenue vs Profit Trend",
        height=550
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# ==========================================================
# DIVISION INSIGHTS
# ==========================================================

st.markdown("---")

best_division = division_summary.loc[
    division_summary["Gross Profit"].idxmax(),
    "Division"
]

worst_division = division_summary.loc[
    division_summary["Gross Profit"].idxmin(),
    "Division"
]

highest_margin = division_summary.loc[
    division_summary["Gross Margin %"].idxmax(),
    "Division"
]

lowest_margin = division_summary.loc[
    division_summary["Gross Margin %"].idxmin(),
    "Division"
]

col1, col2, col3, col4 = st.columns(4)

col1.success(f"🏆 Best Division\n\n{best_division}")

col2.error(f"⚠ Lowest Profit\n\n{worst_division}")

col3.info(f"📈 Highest Margin\n\n{highest_margin}")

col4.warning(f"📉 Lowest Margin\n\n{lowest_margin}")


# ==========================================================
# PARETO ANALYSIS
# ==========================================================

st.markdown("---")
st.header("📈 Pareto Analysis (80/20 Rule)")

pareto = (
    filtered
    .groupby("Product Name")
    .agg({
        "Sales":"sum",
        "Gross Profit":"sum"
    })
    .reset_index()
)

pareto = pareto.sort_values(
    "Gross Profit",
    ascending=False
)

pareto["Cumulative Profit"] = pareto[
    "Gross Profit"
].cumsum()

pareto["Cumulative %"] = (
    pareto["Cumulative Profit"]
    /
    pareto["Gross Profit"].sum()
) * 100

fig = go.Figure()

fig.add_trace(
    go.Bar(
        x=pareto["Product Name"],
        y=pareto["Gross Profit"],
        name="Gross Profit"
    )
)

fig.add_trace(
    go.Scatter(
        x=pareto["Product Name"],
        y=pareto["Cumulative %"],
        yaxis="y2",
        mode="lines",
        name="Cumulative %",
        line=dict(color="red", width=3)
    )
)

fig.update_layout(

title="Pareto Analysis",

height=650,

yaxis=dict(title="Gross Profit"),

yaxis2=dict(
title="Cumulative %",
overlaying="y",
side="right"
)

)

st.plotly_chart(
fig,
use_container_width=True
)

# ==========================================================
# COST VS SALES
# ==========================================================

st.markdown("---")
st.header("💰 Cost vs Sales Diagnostics")

fig = px.scatter(

filtered,

x="Cost",

y="Sales",

size="Gross Profit",

color="Division",

hover_name="Product Name",

title="Cost vs Sales"

)

fig.update_layout(height=600)

st.plotly_chart(
fig,
use_container_width=True
)

# ==========================================================
# COST VS PROFIT
# ==========================================================

fig = px.scatter(

filtered,

x="Cost",

y="Gross Profit",

size="Sales",

color="Division",

hover_name="Product Name",

title="Cost vs Gross Profit"

)

fig.update_layout(height=600)

st.plotly_chart(
fig,
use_container_width=True
)

# ==========================================================
# MARGIN RISK
# ==========================================================

st.markdown("---")
st.header("⚠ Margin Risk Analysis")

risk = filtered.copy()

risk["Margin %"] = (
risk["Gross Profit"] /
risk["Sales"]
)*100

risk["Risk"] = np.where(

risk["Margin %"] < 20,

"High Risk",

np.where(

risk["Margin %"] <40,

"Medium Risk",

"Low Risk"

)

)

fig = px.pie(

risk,

names="Risk",

title="Margin Risk Distribution",

color="Risk",

color_discrete_map={

"High Risk":"red",

"Medium Risk":"orange",

"Low Risk":"green"

}

)

st.plotly_chart(
fig,
use_container_width=True
)

# ==========================================================
# RISK TABLE
# ==========================================================

st.subheader("Products Requiring Attention")

risk_table = risk[
risk["Risk"]=="High Risk"
][[
"Product Name",
"Division",
"Sales",
"Cost",
"Gross Profit",
"Margin %"
]]

st.dataframe(

risk_table,

height=350,

use_container_width=True

)

# ==========================================================
# EXECUTIVE SUMMARY
# ==========================================================

st.markdown("---")
st.header("📋 Executive Summary")

total_revenue = filtered["Sales"].sum()

total_profit = filtered["Gross Profit"].sum()

margin = (
total_profit /
total_revenue
)*100

st.success(f"""
### Overall Business Performance

• Total Revenue : ${total_revenue:,.0f}

• Total Gross Profit : ${total_profit:,.0f}

• Overall Margin : {margin:.2f} %

• Products Analysed : {filtered['Product Name'].nunique()}

• Divisions : {filtered['Division'].nunique()}

""")

# ==========================================================
# RECOMMENDATIONS
# ==========================================================

st.info("""

### 🎯 Strategic Recommendations

✅ Focus marketing on highest profit products.

✅ Review pricing for High Sales Low Margin products.

✅ Negotiate supplier cost for expensive products.

✅ Reduce inventory of low performing products.

✅ Increase promotion for high margin products.

✅ Monitor margin below 20%.

""")

# ==========================================================
# DOWNLOAD REPORT
# ==========================================================

st.markdown("---")

report = filtered.to_csv(index=False)

st.download_button(

"📥 Download Complete Report",

report,

file_name="Nassau_Candy_Analytics.csv",

mime="text/csv"

)

# ==========================================================
# FOOTER
# ==========================================================

st.markdown("---")

st.markdown("""

### 👨‍💻 Developed by

**Mahek Pandey**

**Product Line Profitability & Margin Performance Analysis**

Unified Mentor Internship Project

Python | Pandas | Plotly | Streamlit

""")


# ==========================================================
# FACTORY MAPPING & ADVANCED ANALYTICS
# ==========================================================

st.markdown("---")
st.header("🏭 Factory Analytics")

factory_df = pd.DataFrame({
    "Factory":[
        "Lot's O' Nuts",
        "Wicked Choccy's",
        "Sugar Shack",
        "Secret Factory",
        "The Other Factory"
    ],
    "Latitude":[
        32.881893,
        32.076176,
        48.11914,
        41.446333,
        35.1175
    ],
    "Longitude":[
        -111.768036,
        -81.088371,
        -96.18115,
        -90.565487,
        -89.971107
    ]
})

st.map(factory_df.rename(
    columns={
        "Latitude":"lat",
        "Longitude":"lon"
    }
))

st.markdown("---")
st.header("🌍 Regional Sales Performance")

region_sales = (
    filtered
    .groupby("Region")
    .agg({
        "Sales":"sum",
        "Gross Profit":"sum",
        "Units":"sum"
    })
    .reset_index()
)

fig = px.treemap(
    region_sales,
    path=["Region"],
    values="Sales",
    color="Gross Profit",
    color_continuous_scale="Viridis",
    title="Regional Revenue Distribution"
)

st.plotly_chart(fig, use_container_width=True)

# ==========================================================
# SHIP MODE ANALYSIS
# ==========================================================

st.markdown("---")
st.header("🚚 Ship Mode Performance")

ship = (
    filtered
    .groupby("Ship Mode")
    .agg({
        "Sales":"sum",
        "Gross Profit":"sum"
    })
    .reset_index()
)

fig = px.bar(
    ship,
    x="Ship Mode",
    y="Sales",
    color="Gross Profit",
    text_auto=".2s",
    title="Sales by Shipping Mode"
)

st.plotly_chart(fig, use_container_width=True)

# ==========================================================
# TOP STATES
# ==========================================================

st.markdown("---")
st.header("🏆 Top Performing States")

state_sales = (
    filtered
    .groupby("State/Province")
    .agg({
        "Sales":"sum",
        "Gross Profit":"sum"
    })
    .reset_index()
)

state_sales = state_sales.sort_values(
    "Sales",
    ascending=False
).head(15)

fig = px.bar(
    state_sales,
    x="Sales",
    y="State/Province",
    orientation="h",
    color="Gross Profit",
    title="Top States by Revenue"
)

fig.update_layout(
    yaxis=dict(categoryorder="total ascending")
)

st.plotly_chart(fig, use_container_width=True)

# ==========================================================
# PRODUCT SEARCH
# ==========================================================

st.markdown("---")
st.header("🔍 Product Search")

search = st.text_input("Search Product")

if search:

    result = filtered[
        filtered["Product Name"]
        .str.contains(search, case=False)
    ]

    st.dataframe(
        result,
        use_container_width=True
    )

# ==========================================================
# EXPORT CSV
# ==========================================================

st.markdown("---")
st.header("📥 Export Dashboard Data")

csv = filtered.to_csv(index=False)

st.download_button(
    label="📄 Download CSV Report",
    data=csv,
    file_name="Nassau_Candy_Dashboard.csv",
    mime="text/csv"
)

# ==========================================================
# FINAL DASHBOARD FOOTER
# ==========================================================

st.markdown("---")

st.success("""
✅ Dashboard Completed Successfully

✔ Executive KPIs
✔ Product Profitability
✔ Division Performance
✔ Pareto Analysis
✔ Margin Risk
✔ Cost Diagnostics
✔ Factory Mapping
✔ Regional Analysis
✔ Ship Mode Analytics
✔ Product Search
✔ CSV Download
✔ Excel Download
""")
