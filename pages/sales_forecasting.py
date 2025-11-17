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
from auth import is_logged_in
from utilities import custom_sidebar,require_upload
import base64
import os
from auth import logout
import db # NEW: Import the database module

st.set_page_config(page_title="SalesSight - Dashboard", layout="wide")

custom_sidebar()


# --- Sidebar Content ---
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
    with open("logo.png", "rb") as f:
        logo_base64 = base64.b64encode(f.read()).decode()

    st.markdown(
        f"""
        <div style='text-align:center; padding:60px;'>
            <img src="data:image/png;base64,{logo_base64}" width="60" style="margin-bottom:20px;" />
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

        st.session_state["forecast_generated"] = True

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

        points_actual_chart = alt.Chart(df_actual).mark_point(filled=True, size=10, color='black').encode(
            x='date:T', y='Sales:Q'
        )
        points_forecast_chart = alt.Chart(df_forecast.iloc[1::3, :] if forecast_days > 30 else df_forecast.iloc[1:, :]).mark_point(filled=True, size=10, color='black').encode(
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
    else:
        st.markdown(
            """
            <div class='info-msg' style='background:#000000;color:#ffffff;padding:12px;border-radius:8px;border:1px solid rgba(255,255,255,0.04);'>
            👈 Select options and click '🔮 Generate Forecast' to see the forecast.
            </div>
            """,
            unsafe_allow_html=True,
        )
        
        
        # --- Feedback Form ---
    st.markdown("---")
    st.markdown("### 📝 Provide Feedback")
    st.markdown("We value your input! Please share your experience with our sales forecasting tool.")

    with st.form("feedback_form", clear_on_submit=True):
        feedback_rating = st.slider(
            "How would you rate the usefulness of this sales forecasting tool?",
            min_value=1, max_value=5, value=5, step=1,
            format="⭐ %d stars"
        )
        feedback_comments = st.text_area(
            "Any additional comments or suggestions? (Optional)",
            height=100,
            placeholder="e.g., 'The forecast was accurate and the recommendations were helpful.'"
        )
        submit_feedback = st.form_submit_button("Submit Feedback")

        if submit_feedback:
            # # Debug: Check session state
            # st.write("🔍 Debug Info:")
            # st.write(f"Session state keys: {list(st.session_state.keys())}")
            # st.write(f"User ID exists: {'user_id' in st.session_state}")
            
            # if 'user_id' in st.session_state:
            #     st.write(f"User ID value: {st.session_state.user_id}")
            #     st.write(f"User ID type: {type(st.session_state.user_id)}")
            
            # st.write(f"Rating: {feedback_rating} (type: {type(feedback_rating)})")
            # st.write(f"Comments: '{feedback_comments}' (length: {len(feedback_comments)})")
            
            # Now try to submit
            if 'user_id' in st.session_state and st.session_state.user_id is not None:
                user_id = st.session_state.user_id
                try:
                    # Clean comments
                    clean_comments = feedback_comments.strip() if feedback_comments.strip() else None
                    
                    st.write(f"Attempting to save: user_id={user_id}, rating={feedback_rating}, comments={clean_comments}")
                    
                    result = db.save_feedback(user_id, feedback_rating, clean_comments)
                    
                    st.write(f"Function returned: {result}")
                    
                    if result:
                        st.success("Thank you for your feedback! It has been submitted successfully.")
                    else:
                        st.error("Failed to submit feedback. The save_feedback function returned False.")
                except Exception as e:
                    st.error(f"An error occurred while submitting feedback: {str(e)}")
                    import traceback
                    st.code(traceback.format_exc())
            else:
                st.error("You must be logged in to submit feedback. Please log in via the Home page.")