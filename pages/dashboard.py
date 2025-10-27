# ##############NEW dashboard.py##############
import streamlit as st
import pandas as pd
import altair as alt
from pages.data_upload import data_extraction
from utils import custom_sidebar,require_upload
from auth import is_logged_in
from auth import logout
import base64
import os



# ---- Page Config ----
st.set_page_config(page_title="SalesSight - Dashboard", layout="wide")

custom_sidebar()

st.title("📊 SalesSight Dashboard")
st.caption("Overview of sales metrics, top products, and trends")


st.markdown("""
<style>
[data-testid="stSidebarNav"] {display: none !important;}
</style>
""", unsafe_allow_html=True)


# --- Sidebar Style ---
logo_path = "logo.png"
title = "SalesSight"

with open(logo_path, "rb") as f:
    logo_base64 = base64.b64encode(f.read()).decode()

st.markdown(
    f"""
    <style>
        [data-testid="stSidebar"] {{
            background-color: #ffffff !important;
            padding-top: 0 !important;
        }}

        [data-testid="stSidebarNav"]::before {{
            content: "";
            display: flex;
            align-items: center;
            justify-content: flex-start;
            height: 60px;
            width: 100%;
            background-color: #ffffff;
            background-image: url("data:image/png;base64,{logo_base64}");
            background-repeat: no-repeat;
            background-size: 26px 26px;
            background-position: 18px center;
            border-bottom: 1px solid #f2f2f2;
            position: relative;
            z-index: 1;
            pointer-events: none;
        }}

        [data-testid="stSidebarNav"]::after {{
            content: "{title}";
            position: absolute;
            top: 18px;
            left: 52px;
            font-family: 'Inter', sans-serif;
            font-weight: 600;
            font-size: 18px;
            color: #1E90FF;
            z-index: 1;
            pointer-events: none;
        }}

        [data-testid="stSidebarNav"] {{
            margin-top: -60px !important;
            position: relative;
            z-index: 0;
        }}

        [data-testid="stSidebarNav"] ul {{
            padding-left: 10px;
        }}

        [data-testid="stSidebarNav"] li a {{
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 8px 14px;
            border-radius: 8px;
            text-decoration: none;
            font-family: 'Inter', sans-serif;
            font-size: 15px;
            font-weight: 500;
            color: #4B5563 !important;
            transition: all 0.2s ease-in-out;
        }}

        [data-testid="stSidebarNav"] li a[data-testid="stSidebarNavLinkActive"] {{
            background-color: #bbddfc !important;
            color: #1E90FF !important;
            font-weight: 600 !important;
        }}
    </style>
    """,
    unsafe_allow_html=True
)

with st.sidebar:
    st.page_link("pages/dashboard.py", label="📊 Dashboard")
    st.page_link("pages/data_upload.py", label="📂 Upload")
    st.page_link("pages/sales_forecasting.py", label="📈 Sales Forecasting")
    st.page_link("pages/setting.py", label="⚙️ Settings")
    if st.button("Logout"):
        logout() 

if not is_logged_in():
    st.warning("You must be logged in to access the Dashboard.")
    st.switch_page("Home.py")
    st.stop()



# ---- If file not uploaded ----
if "save_path" not in st.session_state:
    st.markdown(
        """
        <div style='text-align:center; padding:60px;'>
            <h2 style='color:#6c63ff;'>No file uploaded yet 📂</h2>
            <p style='font-size:16px; color:#555;'>Please upload your sales CSV file on the <b>Data Upload</b> page to view analytics.</p>
            <img src='https://cdn-icons-png.flaticon.com/512/992/992703.png' width='180'/>
        </div>
        """,
        unsafe_allow_html=True
    )
else:
    # ---- Extract metrics ----
    metrics = data_extraction(st.session_state.save_path)

    if "error" in metrics:
        st.error(metrics["error"])
    else:
        # ---- KPI Cards (sales only) ----
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Sales", f"${metrics['total_sales']:,.0f}")
        col2.metric("Average Daily Sales", f"${metrics['avg_sales']:,.0f}")
        col3.metric("Latest Sales", f"${metrics['latest_sales']:,.0f}")
        col4.metric("Growth Rate", f"{metrics['growth']:+.2f}%")

        st.markdown("---")

        # ---- Layout: Sales Trend & Top Products ----
        left_col, right_col = st.columns((2, 1))

        with left_col:
            st.subheader("📈 Sales Trend (Last 12 Months)")
            if metrics.get("sales_trend") is not None and not metrics["sales_trend"].empty:
                df_trend = metrics["sales_trend"].copy()
                df_trend['Month'] = pd.to_datetime(df_trend['Date']).dt.to_period('M').dt.to_timestamp()

                chart = alt.Chart(df_trend).mark_line(point=True).encode(
                    x=alt.X('Month:T', title="Month"),
                    y=alt.Y('Sales:Q', title="Sales ($)"),
                    tooltip=[
                        alt.Tooltip('Month:T', title='Month'),
                        alt.Tooltip('Sales:Q', title='Sales', format='$,.0f')
                    ]
                ).properties(height=350)
                st.altair_chart(chart, use_container_width=True)
            else:
                st.info("No 'Date' column found for trend visualization.")
        with right_col:
            st.subheader("🏆 Top Products")
            if metrics.get("top_products") is not None and not metrics["top_products"].empty:
                for _, row in metrics["top_products"].iterrows():
                    st.write(f"**{row['Product']}** — ${row['Sales']:,.0f}")
            else:
                st.info("No 'Product' column found for ranking.")

        st.markdown("---")

        # # ---- Optional: Monthly Sales Heatmap ----
        if metrics.get("sales_trend") is not None and not metrics["sales_trend"].empty:
            st.subheader("🗓 Monthly Sales Heatmap")
            df_heatmap = metrics["sales_trend"].copy()
            df_heatmap['Month'] = pd.to_datetime(df_heatmap['Date']).dt.to_period('M').dt.to_timestamp()
            df_heatmap['Day'] = pd.to_datetime(df_heatmap['Date']).dt.day

            heatmap = alt.Chart(df_heatmap).mark_rect().encode(
                x=alt.X('Day:O', title="Day of Month"),
                y=alt.Y('Month:T', title="Month"),
                color=alt.Color('Sales:Q', scale=alt.Scale(scheme='greens'), title='Sales ($)'),
                tooltip=[
                    alt.Tooltip('Date:T', title='Date'),
                    alt.Tooltip('Sales:Q', title='Sales', format='$,.0f')
                ]
            ).properties(height=400)

            st.altair_chart(heatmap, use_container_width=True)
