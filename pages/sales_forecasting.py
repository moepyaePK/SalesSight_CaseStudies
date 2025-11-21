import io
import streamlit as st
import pandas as pd
import plotly.express as px
import openai
import os
from dotenv import load_dotenv
from groq import Groq
import altair as alt
import numpy as np
from datetime import datetime, timedelta
from auth import is_logged_in, logout
from utils import require_upload, custom_sidebar
from db import add_feedback

st.set_page_config(page_title="SalesSight - Dashboard", layout="wide")

custom_sidebar()

with st.sidebar:
    st.page_link("pages/dashboard.py", label="📊 Dashboard")
    st.page_link("pages/data_upload.py", label="📂 Upload")
    st.page_link("pages/sales_forecasting.py", label="📈 Sales Forecasting")
    st.page_link("pages/setting.py", label="⚙️ Settings")
    if st.button("Logout"):
        logout()


if not is_logged_in():
    st.warning("⚠️ Please login to continue.")
    st.switch_page("Home.py")
    st.stop()



# ---- Load CSV ----
# Ensure a file path string exists and is readable. Show friendly message otherwise.
if "save_path" not in st.session_state or not isinstance(st.session_state.get("save_path"), str):
    st.markdown(
        """
        <div style='text-align:center; padding:60px;'>
            <h2 style='color:#6c63ff;'>No file uploaded yet 📂</h2>
            <p style='font-size:16px; color:#666;'>Please upload your sales CSV file on the <b>Data Upload</b> page to use forecasting.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.stop()

file_path = st.session_state.get("save_path")
try:
    df = pd.read_csv(file_path)
except Exception as e:
    st.error("❌ Unable to read the uploaded file. Please re-upload a CSV file on the Data Upload page.")
    st.exception(e)
    st.stop()

# Apply strict black theme CSS for forecasting page after a successful file load
st.markdown(
    """
    <style>
    /* Forecasting page: pure black background and crisp white text after file load */
    .stApp .main .block-container { background-color: #000000 !important; color: #ffffff !important; }
    .stApp, .reportview-container, .main, header { background-color: #000000 !important; }

    /* Cards and containers use black panels */
    .card, .recommended, .radio-card { background: #000000 !important; color: #ffffff !important; border: 1px solid rgba(255,255,255,0.03) !important; box-shadow: none !important; }

    /* Headings and text */
    .section-title, h1, h2, h3 { color: #ffffff !important; }

    /* Buttons (subtle dark style with enough contrast) */
    .stButton>button { background-color: #111827 !important; color: #ffffff !important; border-radius: 8px !important; }

    /* Chart text/readability */
    .vega-embed text, .vega-embed .mark-text { fill: #ffffff !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---- Summaries ----
product_summary = df.groupby('Product')['Sales'].sum().reset_index()
data_str = product_summary.to_csv(index=False)

# ---- Load Environment Variables ----
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    st.error("❌ GROQ_API_KEY is not set in your environment variables.")
    st.stop()

client = Groq(api_key=GROQ_API_KEY)

st.title("Sales Forecasting Dashboard")


# (Removed always-on dark theme block — theming is applied only after a successful file load above.)


st.markdown("<div class='section-title' style='margin-bottom:24px;'>Sales Forecasting : Configure Forecast Parameters and Generate Predictive Sales Analytics</div>", unsafe_allow_html=True)

left_col, right_col = st.columns([1,2])

with left_col:

    st.markdown("<strong>Forecast Period</strong>", unsafe_allow_html=True)

    st.markdown("""
    <style>
    /* Radio labels styled as pure black / white cards (applies after load) */
    div[role="radiogroup"] > label {
        background-color: #000000; border: 1px solid #222222; border-radius: 8px; padding: 12px 14px; margin-bottom: 8px; display:flex; flex-direction:column; align-items:flex-start; cursor:pointer; transition: all 0.12s ease-in-out; color:#ffffff;
    }
    div[role="radiogroup"] > label:hover { background-color: #111111; border-color: #333333; }
    div[role="radiogroup"] input:checked + div { color: #ffffff !important; font-weight:700 !important; }
    .radio-main { font-size:15px; font-weight:700; color:#ffffff; }
    .radio-sub { font-size:12px; color:#bfbfbf; margin-top:2px; }
    </style>
    """, unsafe_allow_html=True)
    
# 1148d8

    labels = ["30 Days", "60 Days", "90 Days"]
    sublabels = [" SHT-term Forecast", "MED-term Forecast", "LNG-term Forecast"]

    display_labels = [f"{main} -  {sub}" for main, sub in zip(labels, sublabels)]

    selected_display = st.radio("Forecast Period", display_labels, index=0, label_visibility="collapsed")

    selected_index = display_labels.index(selected_display)
    main_label, sub_label = labels[selected_index], sublabels[selected_index]

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("<strong>Forecast Target</strong>", unsafe_allow_html=True)
    
    if 'Product' in df.columns:
        products = ['All Products'] + sorted(df['Product'].dropna().unique().tolist())
    else:
        products = ['All Products']

    # Place selectbox in a slightly wider column to improve usability
    prod_col, _ = st.columns([3, 4])
    product = prod_col.selectbox("", products)

    generate_btn = st.button("🔮 Generate Forecast")

    if generate_btn:

        if 'Date' not in df.columns or 'Sales' not in df.columns:
            st.error("❌ Your CSV must include 'Date' and 'Sales' columns.")
            st.stop()

        if product != "All Products" and 'Product' in df.columns:
            df = df[df['Product'] == product]

            if df.empty:
                st.warning(f"⚠️ No sales data found for '{product}'. Please select another product.")
                st.stop()

        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        df = df.dropna(subset=['Date', 'Sales']).sort_values('Date')

        actual_df = df.tail(30)
        rng_actual = actual_df['Date']
        actual = actual_df['Sales'].values



with right_col:
    st.markdown("<strong>Sales Trend</strong>", unsafe_allow_html=True)
    st.markdown("<div style='color:#6b7280;margin-bottom:8px;'>Actual Sales Data vs Forecast Sales</div>", unsafe_allow_html=True)

    if generate_btn:

        
        if 'Date' not in df.columns or 'Sales' not in df.columns:
            st.error("❌ Your CSV must include 'Date' and 'Sales' columns.")
            st.stop()

        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        df = df.dropna(subset=['Date', 'Sales']).sort_values('Date')

        products = ['All Products'] + sorted(df['Product'].unique()) if 'Product' in df.columns else ['All Products']

        actual_df = df.tail(30)
        rng_actual = actual_df['Date']
        actual = actual_df['Sales'].values


        forecast_days = int(main_label.split()[0])
        rng_forecast = pd.date_range(start=datetime.today() + timedelta(days=1), periods=forecast_days)

        prompt = f"""
        You are a sales forecasting assistant.
        Given the past {forecast_days} days of sales data:
        {actual.tolist()}

        Forecast the next {forecast_days} days of sales as a Python list of {forecast_days} numeric values.

        Rules:
        - Base your forecast on the dataset (increasing, decreasing, or stable).
        - No flattening or constraining unless extreme outliers are present.

        Then, in 2 sentences, explain the likely trend (rising, falling, or stable).
        Respond in this exact format:
        [forecast_list]
        Explanation: your_text_here
        """

        try:
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}]
            )
            forecast_text = response.choices[0].message.content
            import re, ast
            forecast = ast.literal_eval(re.findall(r'\[.*\]', forecast_text)[0])
            
            last_value = actual[-1]
            forecast = np.clip(forecast, last_value * 0.7, last_value * 1.3)  # limit growth
            window = 5
            forecast = np.convolve(forecast, np.ones(window)/window, mode='same').tolist()

            # Ensure forecast has exact length
            if len(forecast) != forecast_days:
                # st.warning(f"⚠️ Groq returned {len(forecast)} values instead of {forecast_days}. Adjusting to match.")
                if len(forecast) > forecast_days:
                    forecast = forecast[:forecast_days]
                else:
                    forecast += [forecast[-1]] * (forecast_days - len(forecast))

        except Exception as e:
            st.error(f"❌ Error generating forecast: {e}")
            forecast = [actual[-1]] * forecast_days

        # ---- Combine actual and forecast ----
        # For a continuous line, prepend the last actual to forecast
        df_actual = pd.DataFrame({'date': rng_actual, 'Sales': actual, 'Type': 'Actual'})
        df_forecast = pd.DataFrame({'date': rng_forecast, 'Sales': forecast, 'Type': 'Forecast'})
        
        # Add bridge: first forecast point uses last actual value
        bridge = pd.DataFrame({
            'date': [df_actual['date'].iloc[-1]],  # last actual date
            'Sales': [df_actual['Sales'].iloc[-1]], # last actual value
            'Type': ['Forecast']  # make it part of forecast so dash continues correctly
        })

        df_forecast = pd.concat([bridge, df_forecast]).reset_index(drop=True)
        df = pd.concat([df_actual, df_forecast])

        # ---- Chart ----
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
            strokeDash=alt.condition(
                alt.datum.Type == 'Forecast',
                alt.value([4,2]),  # dashed forecast
                alt.value([])      # solid actual
            )
        )

        points_actual_chart = alt.Chart(df_actual).mark_point(filled=True, size=10, color='#ffffff').encode(
            x='date:T', y='Sales:Q'
        )
        points_forecast_chart = alt.Chart(df_forecast.iloc[1::3, :] if forecast_days > 30 else df_forecast.iloc[1:, :]).mark_point(filled=True, size=10, color='#ffffff').encode(
            x='date:T', y='Sales:Q'
        )

        chart = (line + points_actual_chart + points_forecast_chart).properties(height=320)
        st.altair_chart(chart, use_container_width=True)
        
        forecast_text = response.choices[0].message.content
        forecast = ast.literal_eval(re.findall(r'\[.*\]', forecast_text)[0])

        try:
            trend_prompt = f"""
            You are a sales analyst. Based on the following sales forecast:
            {forecast}
            and recent actual data:
            {actual.tolist()}
            
            Identify the trend (rising, falling, or stable), and provide 3 specific, actionable recommendations 
            for improving or sustaining sales performance over the next {forecast_days} days.
            Focus on marketing, inventory, and pricing strategies.
            Format your response in short, concise phrasing as bullet points.
            """

            recommendation_response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": trend_prompt}]
            )

            recommendations_text = recommendation_response.choices[0].message.content

        except Exception as e:
            recommendations_text = f"⚠️ Unable to generate recommendations automatically due to error: {e}"

        st.markdown("<h4>✨ Recommended Actions</h4>", unsafe_allow_html=True)
        st.markdown(recommendations_text)

        # ---- User Feedback Section ----
        st.markdown("---")
        st.subheader("Feedback")
        st.markdown("Was this analysis helpful? Let us know what you think.")

        feedback_text = st.text_area("Your feedback:", key="feedback_text_area", height=100)

        if st.button("Submit Feedback"):
            if feedback_text:
                user_id = st.session_state.get("user_id")
                if user_id:
                    try:
                        add_feedback(user_id=user_id, feedback_text=feedback_text)
                        st.success("Thank you for your feedback! It has been submitted successfully.")
                    except Exception as e:
                        st.error(f"An error occurred while submitting your feedback: {e}")
                else:
                    st.error("Could not submit feedback. User not identified. Please log in again.")
            else:
                st.warning("Please enter some feedback before submitting.")


    else:
        st.markdown(
            """
            <div class='info-msg' style='background:#000000;color:#ffffff;padding:12px;border-radius:8px;border:1px solid rgba(255,255,255,0.04);'>
            👈 Select options and click '🔮 Generate Forecast' to see the forecast.
            </div>
            """,
            unsafe_allow_html=True,
        )



###############MPPK's CODE###############

# import io
# import streamlit as st
# import pandas as pd
# import altair as alt
# import numpy as np
# from datetime import datetime, timedelta
# import os, re, ast
# from dotenv import load_dotenv
# from groq import Groq

# # ========== PAGE CONFIG ==========
# st.set_page_config(page_title="SalesSight - Forecast Dashboard", layout="wide")

# # ========== LOAD CSV ==========
# if "save_path" not in st.session_state:
#     st.warning("⚠️ Please upload a CSV file first.")
#     st.stop()

# file_path = st.session_state.save_path
# df = pd.read_csv(file_path)

# # ========== LOAD ENV KEYS ==========
# load_dotenv()
# GROQ_API_KEY = os.getenv("GROQ_API_KEY")
# if not GROQ_API_KEY:
#     st.error("❌ GROQ_API_KEY not set in environment variables.")
#     st.stop()
# client = Groq(api_key=GROQ_API_KEY)

# # ========== PAGE HEADER ==========
# st.title("📊 SalesSight – AI Forecasting Dashboard")
# st.caption("Analyze your sales trends and get personalized recommendations powered by LLaMA 3.3-70B")

# # ========== CLEAN DATA ==========
# if 'Date' not in df.columns or 'Sales' not in df.columns:
#     st.error("Your CSV must contain at least 'Date' and 'Sales' columns.")
#     st.stop()

# df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
# df = df.dropna(subset=['Date', 'Sales']).sort_values('Date')

# products = ['All Products'] + sorted(df['Product'].unique()) if 'Product' in df.columns else ['All Products']

# # ========== SIDEBAR ==========
# with st.sidebar:
#     st.header("⚙️ Forecast Settings")
#     forecast_label = st.radio(
#         "Forecast Horizon",
#         ["30 Days (Short-term)", "60 Days (Medium-term)", "90 Days (Long-term)"]
#     )
#     forecast_days = int(forecast_label.split()[0])
#     product = st.selectbox("Product", products)
#     st.markdown("---")
#     generate_btn = st.button("🔮 Generate Forecast", use_container_width=True)

# # ========== FILTER PRODUCT ==========
# if product != "All Products" and 'Product' in df.columns:
#     df = df[df['Product'] == product]

# # ========== LEFT: KPI SUMMARY ==========
# total_sales = df['Sales'].sum()
# avg_sales = df['Sales'].mean()
# latest_sales = df['Sales'].iloc[-1]
# growth = ((df['Sales'].iloc[-1] - df['Sales'].iloc[-2]) / df['Sales'].iloc[-2] * 100) if len(df) > 2 else 0

# col1, col2, col3, col4 = st.columns(4)
# col1.metric("Total Sales", f"${total_sales:,.0f}")
# col2.metric("Average Daily Sales", f"${avg_sales:,.0f}")
# col3.metric("Latest Sales", f"${latest_sales:,.0f}")
# col4.metric("Growth Rate", f"{growth:+.2f}%")

# st.markdown("---")

# # ========== RIGHT: FORECAST CHART ==========
# if generate_btn:
#     lookback = min(len(df), forecast_days * 2)
#     actual_df = df.tail(lookback)
#     rng_actual = actual_df['Date']
#     actual = actual_df['Sales'].values

#     # ========== LLM FORECAST ==========
#     prompt = f"""
#     You are a data analyst assistant.
#     Here are the past {lookback} days of sales:
#     {actual.tolist()}

#     Forecast the next {forecast_days} days of sales as a Python list of {forecast_days} numeric values.
#     Then, in 2 sentences, explain the likely trend (rising, falling, or stable).
#     Respond in this exact format:
#     [forecast_list]
#     Explanation: your_text_here
#     """

#     try:
#         response = client.chat.completions.create(
#             model="llama-3.3-70b-versatile",
#             messages=[{"role": "user", "content": prompt}]
#         )
#         content = response.choices[0].message.content
#         forecast = ast.literal_eval(re.findall(r'\[.*?\]', content, re.S)[0])
#         explanation_match = re.search(r"Explanation:(.*)", content, re.S)
#         explanation = explanation_match.group(1).strip() if explanation_match else "No explanation provided."
#     except Exception as e:
#         st.error(f"❌ Forecast generation failed: {e}")
#         forecast = [actual[-1]] * forecast_days
#         explanation = "Using flat projection due to error."

#     # ========== ENSURE FORECAST LENGTH ==========
#     if len(forecast) != forecast_days:
#         if len(forecast) > forecast_days:
#             forecast = forecast[:forecast_days]
#         else:
#             forecast += [forecast[-1]] * (forecast_days - len(forecast))

#     # ========== BUILD FORECAST DF ==========
#     rng_forecast = pd.date_range(start=rng_actual.iloc[-1] + timedelta(days=1), periods=forecast_days)
#     df_actual = pd.DataFrame({'Date': rng_actual, 'Sales': actual, 'Type': ['Actual'] * len(rng_actual)})
#     df_forecast = pd.DataFrame({'Date': rng_forecast, 'Sales': forecast, 'Type': ['Forecast'] * forecast_days})
#     df_combined = pd.concat([df_actual, df_forecast]).reset_index(drop=True)

#     # ========== CHART ==========
#     # Solid line for actual, dashed for forecast
#     base = alt.Chart(df_combined).encode(
#         x=alt.X('Date:T', title="Date"),
#         y=alt.Y('Sales:Q', title="Sales ($)", scale=alt.Scale(zero=False)),
#         color=alt.Color('Type:N', scale=alt.Scale(domain=['Actual','Forecast'], range=['#1E61D4','#34C759'])),
#         tooltip=['Date:T', 'Sales:Q', 'Type:N']
#     )

#     line = base.mark_line().encode(
#         strokeDash=alt.condition(
#             alt.datum.Type == 'Forecast',
#             alt.value([4,2]),
#             alt.value([])
#         )
#     )

#     points_actual = alt.Chart(df_actual).mark_point(filled=True, size=60, color='#1E61D4').encode(
#         x='Date:T', y='Sales:Q'
#     )

#     points_forecast = alt.Chart(df_forecast).mark_point(filled=True, size=60, color='#34C759').encode(
#         x='Date:T', y='Sales:Q'
#     )

#     chart = (line + points_actual + points_forecast).properties(height=400)
#     st.altair_chart(chart, use_container_width=True)

#     # ========== AI TREND INSIGHT ==========
#     st.markdown("### 📈 AI Trend Insight")
#     st.info(explanation)

#     # ========== AI PERSONALIZED RECOMMENDATIONS ==========
#     rec_prompt = f"""
#     Based on the following forecasted sales data:
#     {forecast}
#     and the recent sales trend that {explanation},
#     give 4 concise, personalized business recommendations
#     for a sales manager to act on.
#     Format them as bullet points with short actionable phrasing.
#     """

#     try:
#         rec_response = client.chat.completions.create(
#             model="llama-3.3-70b-versatile",
#             messages=[{"role": "user", "content": rec_prompt}]
#         )
#         rec_text = rec_response.choices[0].message.content.strip()
#     except Exception as e:
#         rec_text = f"⚠️ Unable to generate AI recommendations: {e}"

#     st.markdown("### 💡 Personalized Recommendations")
#     st.markdown(rec_text)

# else:
#     st.info("👈 Configure your forecast settings in the sidebar and click **🔮 Generate Forecast** to begin.")
