import os
import io
import base64
from datetime import datetime, timedelta

import altair as alt
import numpy as np
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from groq import Groq

from auth import is_logged_in, logout
from utilities import custom_sidebar, require_upload
import db  # NEW: Import the database module

# -------------------------------------------------------
# Page Config
# -------------------------------------------------------
st.set_page_config(page_title="SalesSight - Dashboard", layout="wide")
custom_sidebar(sidebar_bg="#0f1720")

st.markdown(
    """
    <style>
    [data-testid="stSidebar"], section[data-testid="stSidebar"] {
        background: #0f1720 !important;
        color: #ffffff !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# -------------------------------------------------------
# Sidebar
# -------------------------------------------------------
with st.sidebar:
    st.page_link("pages/dashboard.py", label="📊 Dashboard")
    st.page_link("pages/data_upload.py", label="📂 Upload")
    st.page_link("pages/sales_forecasting.py", label="📈 Sales Forecasting")
    st.page_link("pages/setting.py", label="⚙️ Settings")

    if st.button("Logout"):
        logout()

# -------------------------------------------------------
# Login Check
# -------------------------------------------------------
if not is_logged_in():
    st.warning("⚠️ Please login to continue.")
    st.switch_page("Home.py")
    st.stop()

# -------------------------------------------------------
# Load CSV
# -------------------------------------------------------
if "save_path" not in st.session_state or not isinstance(st.session_state.get("save_path"), str):

    with open("logo.png", "rb") as f:
        logo_base64 = base64.b64encode(f.read()).decode()

    st.markdown(
        f"""
        <div style='text-align:center; padding:60px;'>
            <img src="data:image/png;base64,{logo_base64}" width="60" style="margin-bottom:20px;" />
            <h2 style='color:#6c63ff;'>No file uploaded yet 📂</h2>
            <p style='font-size:16px; color:#666;'>
                Please upload your sales CSV file on the <b>Data Upload</b> page to use forecasting.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.stop()

file_path = st.session_state.get("save_path")

try:
    df = pd.read_csv(file_path)
except Exception as e:
    st.error("❌ Unable to read the uploaded file. Please re-upload a CSV file.")
    st.exception(e)
    st.stop()

# -------------------------------------------------------
# Dark Theme CSS
# -------------------------------------------------------
st.markdown(
    """
    <style>
        .stApp .main .block-container {
            background-color: #000000 !important;
            color: #ffffff !important;
        }
        .stApp, .reportview-container, .main, header {
            background-color: #000000 !important;
        }
        .card, .recommended, .radio-card {
            background: #000000 !important;
            color: #ffffff !important;
            border: 1px solid rgba(255,255,255,0.03) !important;
            box-shadow: none !important;
        }
        h1, h2, h3 { color: #ffffff !important; }
        .stButton>button {
            background-color: #111827 !important;
            color: #ffffff !important;
            border-radius: 8px !important;
        }
        .vega-embed text, .vega-embed .mark-text {
            fill: #ffffff !important;
        }

        /* Regular buttons (Generate Forecast) */
        .stButton>button {
            background-color: #1e40af !important;
            color: #ffffff !important;
            border-radius: 8px !important;
            padding: 8px 18px !important;
            font-weight: 600 !important;
            border: 1px solid #1e3a8a !important;
            transition: all 0.3s ease !important;
        }
        
        .stButton>button:hover {
            background-color: #3b82f6 !important;
            border: 1px solid #60a5fa !important;
            color: #ffffff !important;
            transform: translateY(-1px) !important;
            box-shadow: 0 4px 6px rgba(59, 130, 246, 0.3) !important;
        }
        
        .stButton>button:active {
            transform: translateY(0) !important;
            box-shadow: 0 2px 4px rgba(59, 130, 246, 0.2) !important;
        }
        
        /* Form Submit buttons (Submit Feedback) */
        div.stFormSubmitButton > button,
        button[kind="formSubmit"] {
            background-color: #1e40af !important;
            color: #ffffff !important;
            border-radius: 8px !important;
            padding: 12px 24px !important;
            font-weight: 600 !important;
            border: 1px solid #1e3a8a !important;
            transition: all 0.3s ease !important;
            width: 100% !important;
        }
        
        div.stFormSubmitButton > button:hover,
        button[kind="formSubmit"]:hover {
            background-color: #3b82f6 !important;
            border: 1px solid #60a5fa !important;
            color: #ffffff !important;
            transform: translateY(-1px) !important;
            box-shadow: 0 4px 6px rgba(59, 130, 246, 0.3) !important;
        }
        
        div.stFormSubmitButton > button:active,
        button[kind="formSubmit"]:active {
            transform: translateY(0) !important;
            box-shadow: 0 2px 4px rgba(59, 130, 246, 0.2) !important;
        }
        
        /* Ensure button text is white */
        .stButton>button p,
        div.stFormSubmitButton > button p,
        button[kind="formSubmit"] p {
            color: #ffffff !important;
        }
        
        .vega-embed text, .vega-embed .mark-text {
            fill: #ffffff !important;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# -------------------------------------------------------
# Groq Environment Setup
# -------------------------------------------------------
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    st.error("❌ GROQ_API_KEY is missing.")
    st.stop()

client = Groq(api_key=GROQ_API_KEY)

# -------------------------------------------------------
# Page Title
# -------------------------------------------------------
st.title("Sales Forecasting Dashboard")
st.markdown(
    "<div class='section-title' style='margin-bottom:24px;'>"
    "Sales Forecasting : Configure Forecast Parameters and Generate Predictive Analytics"
    "</div>",
    unsafe_allow_html=True,
)

# -------------------------------------------------------
# Layout
# -------------------------------------------------------
left_col, right_col = st.columns([1, 2])

# ======================================================
# LEFT COLUMN — FORECAST CONTROLS
# ======================================================
with left_col:

    st.markdown("<strong>Forecast Period</strong>", unsafe_allow_html=True)

    # Radio button styling
    st.markdown(
        """
        <style>
            div[role="radiogroup"] > label {
                background-color: #000000;
                border: 1px solid #222222;
                border-radius: 8px;
                padding: 12px 14px;
                margin-bottom: 8px;
                display:flex;
                cursor:pointer;
                color:#ffffff;
            }
            div[role="radiogroup"] > label:hover {
                background-color: #111111;
            }
            .radio-main { font-size:15px; font-weight:700; }
            .radio-sub { font-size:12px; color:#bfbfbf; }
        </style>
        """,
        unsafe_allow_html=True,
    )

    labels = ["30 Days", "60 Days", "90 Days"]
    sublabels = ["SHT-term Forecast", "MED-term Forecast", "LNG-term Forecast"]

    display_labels = [f"{main} - {sub}" for main, sub in zip(labels, sublabels)]

    selected_display = st.radio("Forecast Period", display_labels, index=0, label_visibility="collapsed")
    selected_index = display_labels.index(selected_display)
    main_label = labels[selected_index]

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("<strong>Forecast Target</strong>", unsafe_allow_html=True)

    if "Product" in df.columns:
        products = ["All Products"] + sorted(df["Product"].dropna().unique().tolist())
    else:
        products = ["All Products"]

    product = st.selectbox("", products)

    generate_btn = st.button("🔮 Generate Forecast")

    # Validate CSV columns
    if generate_btn:
        if "Date" not in df.columns or "Sales" not in df.columns:
            st.error("❌ CSV must contain 'Date' and 'Sales' columns.")
            st.stop()

        if product != "All Products" and "Product" in df.columns:
            df = df[df["Product"] == product]

            if df.empty:
                st.warning(f"⚠️ No data available for '{product}'.")
                st.stop()

        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        df = df.dropna(subset=["Date", "Sales"]).sort_values("Date")

        actual_df = df.tail(30)
        actual = actual_df["Sales"].values
        rng_actual = actual_df["Date"]

# ======================================================
# RIGHT COLUMN — FORECAST + CHART
# ======================================================
with right_col:

    st.markdown("<strong>Sales Trend</strong>", unsafe_allow_html=True)
    st.markdown(
        "<div style='color:#6b7280;margin-bottom:8px;'>Actual vs Forecast Sales</div>",
        unsafe_allow_html=True,
    )

    if generate_btn:

        st.session_state["forecast_generated"] = True

        # Prep data
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        df = df.dropna(subset=["Date", "Sales"]).sort_values("Date")

        forecast_days = int(main_label.split()[0])
        rng_forecast = pd.date_range(start=datetime.today() + timedelta(days=1), periods=forecast_days)

        # -------------------------------------------------------
        # AI Forecast Prompt
        # -------------------------------------------------------
        prompt = f"""
        You are a sales forecasting assistant.

        Given the past {forecast_days} days of sales:
        {actual.tolist()}

        Forecast the next {forecast_days} days as a Python list.

        Respond ONLY in this format:
        [list]
        Explanation: text_here
        """

        try:
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}]
            )
            forecast_text = response.choices[0].message.content

            import re, ast
            raw_list = re.findall(r'\[.*\]', forecast_text)[0]
            forecast = ast.literal_eval(raw_list)

            # Smoothing + clipping
            last_value = actual[-1]
            forecast = np.clip(forecast, last_value * 0.7, last_value * 1.3)
            forecast = np.convolve(forecast, np.ones(5)/5, mode='same').tolist()

            # Fix length mismatch
            if len(forecast) != forecast_days:
                if len(forecast) > forecast_days:
                    forecast = forecast[:forecast_days]
                else:
                    forecast += [forecast[-1]] * (forecast_days - len(forecast))

        except Exception as e:
            st.error(f"❌ Forecast error: {e}")
            forecast = [actual[-1]] * forecast_days

        # -------------------------------------------------------
        # Build Forecast DataFrame
        # -------------------------------------------------------
        df_actual = pd.DataFrame({"date": rng_actual, "Sales": actual, "Type": "Actual"})
        df_forecast = pd.DataFrame({"date": rng_forecast, "Sales": forecast, "Type": "Forecast"})

        # Bridge point for continuous line
        bridge = pd.DataFrame({
            "date": [df_actual["date"].iloc[-1]],
            "Sales": [df_actual["Sales"].iloc[-1]],
            "Type": ["Forecast"]
        })

        df_forecast = pd.concat([bridge, df_forecast]).reset_index(drop=True)
        df_chart = pd.concat([df_actual, df_forecast])

        # -------------------------------------------------------
        # Altair Chart
        # -------------------------------------------------------
        base = alt.Chart(df_chart).encode(
            x=alt.X("date:T", axis=alt.Axis(format="%d %b"))
        )

        line = base.mark_line().encode(
            y="Sales:Q",
            color=alt.Color(
                "Type:N",
                scale=alt.Scale(domain=["Actual", "Forecast"], range=["#1E61D4", "#34C759"]),
                legend=alt.Legend(title=None, orient="top")
            ),
            strokeDash=alt.condition(
                alt.datum.Type == "Forecast",
                alt.value([4, 2]),
                alt.value([])
            )
        )

        points_actual = alt.Chart(df_actual).mark_point(
            filled=True, size=10, color="black"
        ).encode(x="date:T", y="Sales:Q")

        points_forecast = alt.Chart(df_forecast.iloc[1:, :]).mark_point(
            filled=True, size=10, color="black"
        ).encode(x="date:T", y="Sales:Q")

        chart = (line + points_actual + points_forecast).properties(height=320)
        st.altair_chart(chart, use_container_width=True)

        # -------------------------------------------------------
        # Recommendations
        # -------------------------------------------------------
        trend_prompt = f"""
        You are a sales analyst.

        Based on the forecast:
        {forecast}

        And the recent actual data:
        {actual.tolist()}

        Identify the trend AND give 3 actionable recommendations.
        """

        try:
            recommendation_response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": trend_prompt}]
            )
            recommendations_text = recommendation_response.choices[0].message.content

        except Exception as e:
            recommendations_text = f"⚠️ Unable to generate recommendations automatically: {e}"

        st.markdown("<h4>✨ Recommended Actions</h4>", unsafe_allow_html=True)
        st.markdown(recommendations_text)

    else:
        st.markdown(
            """
            <div class='info-msg' style='background:#000;color:#fff;padding:12px;border-radius:8px;border:1px solid rgba(255,255,255,0.04);'>
                👈 Select options and click '<b>🔮 Generate Forecast</b>' to begin.
            </div>
            """,
            unsafe_allow_html=True,
        )

    # -------------------------------------------------------
    # Feedback Form
    # -------------------------------------------------------
    st.markdown("---")
    st.markdown("### 📝 Provide Feedback")
    st.markdown("We value your input! Please share your experience.")

    with st.form("feedback_form", clear_on_submit=True):

        feedback_rating = st.slider(
            "How would you rate this tool?",
            min_value=1,
            max_value=5,
            value=5,
            step=1,
            format="⭐ %d stars"
        )

        feedback_comments = st.text_area(
            "Additional comments (optional):",
            height=100,
            placeholder="e.g., 'The forecast was accurate and useful!'"
        )

        submit_feedback = st.form_submit_button("Submit Feedback")

        if submit_feedback:

            if "user_id" in st.session_state and st.session_state.user_id is not None:
                user_id = st.session_state.user_id

                try:
                    clean_comments = feedback_comments.strip() or None

                    result = db.save_feedback(user_id, feedback_rating, clean_comments)

                    if result:
                        st.success("Thank you! Your feedback has been submitted.")
                    else:
                        st.error("Feedback could not be saved.")
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
            else:
                st.error("Please log in to submit feedback.")
