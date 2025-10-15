# import streamlit as st
# import pandas as pd
# import plotly.express as px
# from pages.data_upload import data_extraction
# from utils import add_sidebar_logo

# # ---- Page Config ----
# st.set_page_config(page_title="SalesSight - Dashboard", layout="wide")
# add_sidebar_logo()

# st.title("📊 Dashboard")

# # ---- If file not uploaded ----
# if "save_path" not in st.session_state:
#     st.markdown(
#         """
#         <div style='text-align:center; padding:60px;'>
#             <h2 style='color:#6c63ff;'>No file uploaded yet 📂</h2>
#             <p style='font-size:16px; color:#555;'>Please upload your sales CSV file on the <b>Data Upload</b> page to view analytics.</p>
#             <img src='https://cdn-icons-png.flaticon.com/512/992/992703.png' width='180'/>
#         </div>
#         """,
#         unsafe_allow_html=True
#     )
# else:
#     metrics = data_extraction(st.session_state.save_path)

#     if "error" in metrics:
#         st.error(metrics["error"])
#     else:
#         # KPI Cards
#         col1, col2, col3, col4 = st.columns(4)
#         col1.metric("Total Sales", f"{metrics['total_sales']:,.0f} THB", "+8% from last month")
#         col2.metric("Orders", f"{metrics['num_orders']:,}", "+12% from last month")
#         col3.metric("Total Profit", f"{metrics['total_profit']:,.0f} THB", "+3% from last month")
#         col4.metric("Gross Profit Margin", f"{metrics['gross_margin']}%", "-2% from last month")

#         st.markdown("---")

#         # Layout: Sales Trend & Top Products
#         left_col, right_col = st.columns((2, 1))

#         with left_col:
#             st.subheader("📈 Sales Trend")
#             if metrics["sales_trend"] is not None:
#                 fig = px.bar(
#                     metrics["sales_trend"],
#                     x="Date",
#                     y="Sales",
#                     title="Monthly Sales Trend",
#                     labels={"Sales": "Sales (THB)", "Date": "Month"},
#                 )
#                 st.plotly_chart(fig, use_container_width=True)
#             else:
#                 st.info("No 'Date' column found for trend visualization.")

#         with right_col:
#             st.subheader("🏆 Top Products")
#             if metrics["top_products"] is not None:
#                 for _, row in metrics["top_products"].iterrows():
#                     st.write(f"**{row['Product']}** — {row['Sales']:,.0f} THB")
#             else:
#                 st.info("No 'Product' column found for ranking.")


##############NEW dashboard.py##############
import streamlit as st
import pandas as pd
import altair as alt
from pages.data_upload import data_extraction
from utils import add_sidebar_logo

# ---- Page Config ----
st.set_page_config(page_title="SalesSight - Dashboard", layout="wide")
add_sidebar_logo()

st.title("📊 SalesSight Dashboard")
st.caption("Overview of sales metrics, top products, and trends")

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

        # ---- Optional: Monthly Sales Heatmap ----
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
