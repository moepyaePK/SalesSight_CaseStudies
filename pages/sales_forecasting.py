import streamlit as st
import pandas as pd
import numpy as np
from utils import add_sidebar_logo



st.set_page_config(page_title="SalesSight - Sales Forecasting", layout="wide")
add_sidebar_logo()

st.title("📈 Sales Forecasting")
st.write("Configure Forecast Parameters and Generate Predictive Sales Analytics")

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("Forecast Period")
    period = st.radio("", ["30 Days", "60 Days", "90 Days"], index=0)

    st.subheader("Forecast Target")
    target = st.selectbox("", ["All Products", "Product A", "Product B"])

    st.button("🔮 Generate Analytics")

with col2:
    st.subheader("Sales Trend")
    dates = pd.date_range("2023-09-12", periods=12)
    actual = np.random.randint(60_000, 100_000, len(dates))
    forecast = actual + np.random.randint(-5000, 15000, len(dates))
    st.line_chart({"Actual Sales": actual, "Sales Forecasting": forecast}, x=dates)

st.markdown("---")
st.subheader("✨ Recommended Actions")
st.info("This is where AI-generated recommended actions will appear.")

