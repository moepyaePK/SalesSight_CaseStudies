import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import altair as alt

st.set_page_config(page_title="SalesSight - Dashboard", layout="wide")

st.markdown(
    """
    <style>
    /* general background and container spacing */
    .reportview-container, .main, header, .stApp {
        background-color: #f6f7fb;
    }
    /* sidebar style */
    .sidebar .sidebar-content {
        background: #ffffff;
        padding-top: 14px;
    }
    /* Logo in sidebar */
    .logo {
        font-weight: 700;
        font-size: 18px;
        padding: 10px 14px;
        color: #1155cc;
    }
    /* navigation items */
    .nav-item {
        padding: 12px 14px;
        display: block;
        color: #333333;
        border-radius: 6px;
        margin: 6px 8px;
    }
    .nav-item.selected {
        background-color: #f1f6ff;
        color: #1155cc;
        font-weight: 600;
    }
    /* left control card look */
    .card {
        background: #ffffff;
        padding: 18px;
        border-radius: 8px;
        box-shadow: 0 1px 0 rgba(16,24,40,0.04);
        border: 1px solid rgba(16,24,40,0.04);
    }
    .radio-card {
        border:1px solid rgba(16,24,40,0.06);
        padding:12px;
        border-radius:8px;
        margin-bottom:8px;
    }
    .generate-btn {
        background-color:#1148d8;
        color:white;
        padding:12px 18px;
        border-radius:8px;
        text-align:center;
        display:inline-block;
        font-weight:700;
    }
    .section-title {
        font-size:20px;
        font-weight:700;
        margin-bottom:6px;
    }
    .subtitle {
        color: #6b7280;
        margin-bottom:12px;
    }
    .recommended {
        background: #ffffff;
        padding: 18px;
        border-radius:8px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


st.markdown("<div class='section-title'>Sales Forecasting</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Configure Forecast Parameters and Generate Predictive Sales Analytics</div>", unsafe_allow_html=True)

left_col, right_col = st.columns([1,2])

with left_col:

    st.markdown("<strong>Forecast Period</strong>", unsafe_allow_html=True)
    
    # period = st.radio("", ["30 Days\nShort-term Forecast", "60 Days\nShort-term Forecast", "90 Days\nShort-term Forecast"], index=0)
    # st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("""
    <style>
    /* Make each radio label look like a card */
    div[role="radiogroup"] > label {
        background-color: white;
        border: 1px solid #e5e7eb;
        border-radius: 8px;
        padding: 12px 14px;
        margin-bottom: 8px;
        display: flex;
        flex-direction: column;
        align-items: flex-start;
        cursor: pointer;
        transition: all 0.2s ease-in-out;
    }
    div[role="radiogroup"] > label:hover {
        background-color: #f1f6ff;
        border-color: #2563eb;
    }
    div[role="radiogroup"] input:checked + div {
        color: #03045e !important;
        font-weight: 700 !important;
    }
    /* Style the main and sub text lines separately */
    .radio-main {
        font-size: 15px;
        font-weight: 700;
        line-height: 1.1;
    }
    .radio-sub {
        font-size: 12px;
        color: #6b7280;
        margin-top: 2px;
    }
    </style>
    """, unsafe_allow_html=True)
    
# 1148d8

    labels = ["30 Days", "60 Days", "90 Days"]
    sublabels = ["Short-term Forecast", "Medium-term Forecast", "Long-term Forecast"]

    display_labels = [f"{main} -  {sub}" for main, sub in zip(labels, sublabels)]

    selected_display = st.radio("Forecast Period", display_labels, index=0, label_visibility="collapsed")

    selected_index = display_labels.index(selected_display)
    main_label, sub_label = labels[selected_index], sublabels[selected_index]

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("<strong>Forecast Target</strong>", unsafe_allow_html=True)
    product = st.selectbox("", ["All Products", "Top Products", "Single Product"])

    st.markdown("<br>", unsafe_allow_html=True)
    st.button("✨ Generate Analytics")
    st.markdown("</div>", unsafe_allow_html=True)

with right_col:

    st.markdown("<strong>Sales Trend</strong>", unsafe_allow_html=True)
    st.markdown("<div style='color:#6b7280;margin-bottom:8px;'>Actual Sales Data vs Forecast Sales</div>", unsafe_allow_html=True)
    
    rng_actual = pd.date_range(end=datetime.today(), periods=15)
    actual = (np.sin(np.linspace(0, 1.5, 15)) + 1.5) * 50000 + np.linspace(80000, 60000, 15)

    forecast_days = int(main_label.split()[0])
    rng_forecast = pd.date_range(start=datetime.today() + timedelta(days=1), periods=forecast_days)
    forecast = actual[-1] * (1 + np.linspace(0, 0.08, forecast_days))

    df_actual = pd.DataFrame({'date': rng_actual, 'Sales': actual, 'Type': 'Actual'})
    df_forecast = pd.DataFrame({'date': rng_forecast, 'Sales': forecast, 'Type': 'Forecast'})
    df = pd.concat([df_actual, df_forecast])

    base = alt.Chart(df).encode(
        x=alt.X('date:T', axis=alt.Axis(title=None, format='%d %b'))
    )
    line = base.mark_line().encode(
        y='Sales:Q',
        color=alt.Color(
            'Type:N',
            scale=alt.Scale(domain=['Actual','Forecast'], range=['#1E61D4','#34C759']),
            legend=alt.Legend(title=None, orient='top')
        ),
        strokeDash=alt.condition(alt.datum.Type=='Forecast', alt.value([4,2]), alt.value([]))
    )

    points_actual = df_actual.copy()
    points_actual_chart = alt.Chart(points_actual).mark_point(filled=True, size=10, color='black').encode(
        x='date:T',
        y='Sales:Q'
    )
    if forecast_days > 30:
        points_forecast = df_forecast.iloc[::3, :]  
    else:
        points_forecast = df_forecast

    points_forecast_chart = alt.Chart(points_forecast).mark_point(filled=True, size=10, color='black').encode(
        x='date:T',
        y='Sales:Q'
    )
    chart = (line + points_actual_chart + points_forecast_chart).properties(height=320)
    st.altair_chart(chart, use_container_width=True)
    
    # st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<h4>✨ Recommended Actions</h4>", unsafe_allow_html=True)
    st.write("""
    • Review products with declining forecasts and consider promotions.\n
    • Rebalance inventory for items with increasing forecast trends to avoid stockouts.\n
    • Investigate external factors (seasonality, events) affecting dips in sales and prepare targeted campaigns.
    """)
    st.markdown("</div>", unsafe_allow_html=True)
    