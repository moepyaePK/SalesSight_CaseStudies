import streamlit as st
import pandas as pd
import altair as alt
import textwrap
from pages.data_upload import data_extraction
from utilities import custom_sidebar
from auth import is_logged_in, logout

# ---- Page Config ----
st.set_page_config(page_title="SalesSight - Dashboard", layout="wide")

custom_sidebar()

# Header and global dark styles
st.markdown(textwrap.dedent("""
<style>
/* App-wide dark background for dashboard */
.stApp .main .block-container { background-color: #0b0f14; color: #e6eef8; }
.stApp, .reportview-container, .main, header { background-color: #0b0f14; }

/* Sidebar: deep charcoal with white labels */
[data-testid="stSidebar"] { background-color: #0f1720 !important; color: #ffffff !important; }
[data-testid="stSidebar"] a, [data-testid="stSidebar"] .st-Button button { color: #f8fafc !important; }

/* Subtle button style */
.stButton>button { background-color: #111827 !important; color: #ffffff !important; border-radius: 8px !important; }
</style>
"""), unsafe_allow_html=True)

st.markdown("""<div style='display:flex;align-items:center;gap:18px;margin-bottom:14px;'>
  <div style='font-size:30px;'>📊</div>
  <div style='font-size:36px;font-weight:800;color:#ffffff;'>SalesSight Dashboard</div>
</div>
<div style='color:#9aa4b2;margin-bottom:28px;'>Overview of sales metrics, top products, and trends</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.page_link("pages/dashboard.py", label="📊 Dashboard")
    st.page_link("pages/data_upload.py", label="📂 Upload")
    st.page_link("pages/sales_forecasting.py", label="📈 Sales Forecasting")
    st.page_link("pages/setting.py", label="⚙️ Settings")
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Logout"):
        logout()

if not is_logged_in():
    st.warning("⚠️ Please login to continue.")
    st.switch_page("Home.py")
    st.stop()

# ---- If no file uploaded: show centered dashed upload card ----
if "save_path" not in st.session_state or not isinstance(st.session_state.get("save_path"), str):
    st.markdown(textwrap.dedent("""
    <div style='display:flex;flex-direction:column;align-items:center;justify-content:center;padding:80px 0;'>
      <h2 style='color:#6c63ff;font-size:30px;margin:0 0 10px 0;'>No file uploaded yet 📂</h2>

      <div style='width:820px;max-width:92%;border-radius:12px;border:2px dashed rgba(255,255,255,0.06);padding:36px 20px;background:rgba(255,255,255,0.008);display:flex;align-items:center;justify-content:center;'>
        <div style='text-align:center;color:#cbd5e1;display:flex;flex-direction:column;align-items:center;gap:8px;'>
          <div style='font-size:48px;line-height:1;margin:0;'></div>
            <svg width='60' height='60' viewBox='0 0 24 24' xmlns='http://www.w3.org/2000/svg' style='display:block;margin-bottom:25px;'>
              <circle cx='12' cy='12' r='10' fill='none' stroke='#9aa4b2' stroke-width='1.6' />
              <path d='M12 8v6' stroke='#9aa4b2' stroke-width='1.8' stroke-linecap='round' stroke-linejoin='round' />
              <path d='M9.5 10.5L12 8l2.5 2.5' stroke='#9aa4b2' stroke-width='1.8' stroke-linecap='round' stroke-linejoin='round' />
            </svg>
          <div style='color:#9aa4b2;margin-bottom:24px;'>Please upload your sales CSV file on the <b>Data Upload</b> page to view analytics.</div>
        </div>
      </div>
    </div>
    """), unsafe_allow_html=True)
else:
    # ---- Extract metrics ----
    metrics = data_extraction(st.session_state.save_path)

    if isinstance(metrics, dict) and metrics.get("error"):
        st.error(metrics["error"])
    else:
        # KPI row
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Sales", f"${metrics['total_sales']:,.0f}")
        col2.metric("Average Daily Sales", f"${metrics['avg_sales']:,.0f}")
        col3.metric("Latest Sales", f"${metrics['latest_sales']:,.0f}")
        col4.metric("Growth Rate", f"{metrics['growth']:+.2f}%")

        st.markdown("---")

        left_col, right_col = st.columns((2, 1))
        with left_col:
            st.subheader("📈 Sales Trend")
            if metrics.get("sales_trend") is not None and not metrics["sales_trend"].empty:
                df_trend = metrics["sales_trend"].copy()
                df_trend['Month'] = pd.to_datetime(df_trend['Date']).dt.to_period('M').dt.to_timestamp()
                chart = alt.Chart(df_trend).mark_line(point=True).encode(
                    x=alt.X('Month:T', title='Month'),
                    y=alt.Y('Sales:Q', title='Sales ($)'),
                    tooltip=[alt.Tooltip('Month:T', title='Month'), alt.Tooltip('Sales:Q', title='Sales', format='$,.0f')]
                ).properties(height=340)
                st.altair_chart(chart, use_container_width=True)
            else:
                st.info("No sales trend data available.")

        with right_col:
            st.subheader("🏆 Top Products")
            if metrics.get("top_products") is not None and not metrics["top_products"].empty:
                for _, row in metrics["top_products"].iterrows():
                    st.write(f"**{row['Product']}** — ${row['Sales']:,.0f}")
            else:
                st.info("No product ranking available.")

        st.markdown("---")
