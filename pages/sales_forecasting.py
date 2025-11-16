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
from utils import custom_sidebar,require_upload, submit_user_feedback # Added submit_user_feedback
import base64
import os
from auth import logout

st.set_page_config(page_title="SalesSight - Dashboard", layout="wide")

custom_sidebar()


st.markdown("""
<style>
[data-testid="stSidebarNav"] {display: none !important;}
</style>
""", unsafe_allow_html=True)


# --- Sidebar Style ---
logo_path = "logo.png"
title = "SalesSight"

# Check if logo_path exists before trying to open it
if os.path.exists(logo_path):
    with open(logo_path, "rb") as f:
        logo_base64 = base64.b64encode(f.read()).decode()
else:
    # Fallback if logo.png is not found
    logo_base64 = "" # Or a default base64 string for a placeholder image

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
require_upload() # Using the utility function
file_path = st.session_state.save_path
df = pd.read_csv(file_path)

# ---- Summaries ----
# Ensure 'Product' column exists before grouping
if 'Product' in df.columns:
    product_summary = df.groupby('Product')['Sales'].sum().reset_index()
    data_str = product_summary.to_csv(index=False)
else:
    product_summary = pd.DataFrame(columns=['Product', 'Sales'])
    data_str = ""


# ---- Load Environment Variables ----
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    st.error("❌ GROQ_API_KEY is not set in your environment variables.")
    st.stop()

client = Groq(api_key=GROQ_API_KEY)

st.title("Sales Forecasting Dashboard")


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
    
    if 'Product' in df.columns:
        products = ['All Products'] + sorted(df['Product'].dropna().unique().tolist())
    else:
        products = ['All Products']

    product = st.selectbox("", products)

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

        # Ensure there's enough data for actual_df
        if len(df) < 30:
            st.warning("Not enough historical data to display a meaningful 'Actual' trend (less than 30 days).")
            # Adjust actual_df to use all available data if less than 30
            actual_df = df
        else:
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

        # Ensure there's enough data for actual_df
        if len(df) < 30:
            st.warning("Not enough historical data to display a meaningful 'Actual' trend (less than 30 days).")
            actual_df = df
        else:
            actual_df = df.tail(30)
        
        rng_actual = actual_df['Date']
        actual = actual_df['Sales'].values

        if len(actual) == 0:
            st.error("No valid sales data found after filtering. Cannot generate forecast.")
            st.stop()

        forecast_days = int(main_label.split()[0])
        rng_forecast = pd.date_range(start=actual_df['Date'].iloc[-1] + timedelta(days=1), periods=forecast_days)

        prompt = f"""
        You are a sales forecasting assistant.
        Given the past {len(actual)} days of sales data:
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
            forecast_text_raw = response.choices[0].message.content
            
            # Extract forecast list
            forecast_list_match = re.findall(r'\[.*?\]', forecast_text_raw, re.DOTALL)
            if forecast_list_match:
                forecast = ast.literal_eval(forecast_list_match[0])
            else:
                raise ValueError("Could not extract forecast list from LLM response.")
            
            # Extract explanation
            explanation_match = re.search(r'Explanation:\s*(.*)', forecast_text_raw, re.DOTALL)
            explanation_text = explanation_match.group(1).strip() if explanation_match else "No explanation provided."

            # Apply smoothing and clipping
            last_value = actual[-1]
            forecast = np.clip(forecast, last_value * 0.7, last_value * 1.3)  # limit growth/decline
            window = min(5, len(forecast)) # Ensure window is not larger than forecast length
            if window > 0:
                forecast = np.convolve(forecast, np.ones(window)/window, mode='same').tolist()

            # Ensure forecast has exact length
            if len(forecast) != forecast_days:
                if len(forecast) > forecast_days:
                    forecast = forecast[:forecast_days]
                else:
                    # Pad with the last value if forecast is too short
                    forecast += [forecast[-1]] * (forecast_days - len(forecast))

        except Exception as e:
            st.error(f"❌ Error generating forecast: {e}")
            forecast = [actual[-1]] * forecast_days # Fallback to flat forecast
            explanation_text = "Forecast generation failed. Displaying a flat projection."

        # ---- Combine actual and forecast ----
        df_actual = pd.DataFrame({'date': rng_actual, 'Sales': actual, 'Type': 'Actual'})
        df_forecast = pd.DataFrame({'date': rng_forecast, 'Sales': forecast, 'Type': 'Forecast'})
        
        # Add bridge: first forecast point uses last actual value
        bridge = pd.DataFrame({
            'date': [df_actual['date'].iloc[-1]],  # last actual date
            'Sales': [df_actual['Sales'].iloc[-1]], # last actual value
            'Type': ['Forecast']  # make it part of forecast so dash continues correctly
        })

        df_forecast = pd.concat([bridge, df_forecast]).reset_index(drop=True)
        df_combined_chart = pd.concat([df_actual, df_forecast])

        # ---- Chart ----
        base = alt.Chart(df_combined_chart).encode(
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
        # Only show points for forecast at reasonable intervals
        points_forecast_chart = alt.Chart(df_forecast.iloc[1::max(1, forecast_days // 10), :]).mark_point(filled=True, size=10, color='black').encode(
            x='date:T', y='Sales:Q'
        )

        chart = (line + points_actual_chart + points_forecast_chart).properties(height=320)
        st.altair_chart(chart, use_container_width=True)
        
        st.markdown("<h4>✨ AI Trend Insight</h4>", unsafe_allow_html=True)
        st.info(explanation_text)

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

        st.markdown("---")
        st.markdown("<h3>We'd love your feedback!</h3>", unsafe_allow_html=True)
        st.write("Help us improve SalesSight by sharing your experience with this forecasting model.")

        # Initialize session state for feedback if not present
        if 'feedback_text' not in st.session_state:
            st.session_state.feedback_text = ""
        if 'feedback_rating' not in st.session_state:
            st.session_state.feedback_rating = 3 # Default rating

        feedback_text_input = st.text_area(
            "Your feedback (optional)",
            value=st.session_state.feedback_text,
            height=100,
            key="feedback_text_widget" # Use a key to manage state
        )
        feedback_rating_input = st.slider(
            "How would you rate the usefulness of this forecast?",
            min_value=1, max_value=5, value=st.session_state.feedback_rating, step=1,
            format="%d star(s)",
            key="feedback_rating_widget" # Use a key to manage state
        )

        if st.button("Submit Feedback", key="submit_feedback_button"):
            user_id = st.session_state.get('user_id') # Assuming user_id is stored in session_state
            if user_id:
                if submit_user_feedback(user_id, feedback_text_input, feedback_rating_input):
                    st.success("Thank you for your feedback! We appreciate it.")
                    # Clear feedback fields after successful submission
                    st.session_state.feedback_text = ""
                    st.session_state.feedback_rating = 3
                    # Rerun to clear the widgets
                    st.rerun()
                else:
                    st.error("Failed to submit feedback. Please try again.")
            else:
                st.error("You must be logged in to submit feedback.")


    else:
        st.info("👈 Select options and click '🔮 Generate Forecast' to see the forecast.")

import streamlit as st
import pandas as pd
import base64
import os
from datetime import datetime
from db import store_feedback # Import the new function

def custom_sidebar():
    """
    Placeholder for custom sidebar functionality.
    The actual UI/styling for the sidebar is often defined directly in the main app.
    """
    pass # No functional code needed here for this specific request, as UI is in sales_forecasting.py

def require_upload():
    """
    Checks if a file has been uploaded and stops execution if not.
    """
    if "save_path" not in st.session_state:
        st.warning("Please upload a CSV file first.")
        st.stop()

def submit_user_feedback(user_id, feedback_text, rating):
    """
    Handles the submission of user feedback to the database.

    Args:
        user_id (int): The ID of the user submitting feedback.
        feedback_text (str): The text content of the feedback.
        rating (int): The rating given by the user (e.g., 1-5).

    Returns:
        bool: True if feedback was stored successfully, False otherwise.
    """
    if not user_id:
        st.error("User not logged in. Cannot submit feedback.")
        return False
    
    # Allow submission even if only rating or only text is provided
    if not feedback_text and rating is None:
        st.warning("Please provide some feedback or a rating before submitting.")
        return False

    try:
        success = store_feedback(user_id, feedback_text, rating)
        return success
    except Exception as e:
        st.error(f"An error occurred while submitting feedback: {e}")
        return False

import sqlite3
from datetime import datetime

DATABASE_FILE = 'salesight.db'

def get_db_connection():
    """Establishes and returns a connection to the SQLite database."""
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row # This allows accessing columns by name
    return conn

def init_db():
    """Initializes the database schema, creating tables if they don't exist."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Create users table if it doesn't exist (assuming auth.py uses this)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        );
    """)

    # Create feedback table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            feedback_text TEXT,
            rating INTEGER,
            timestamp TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        );
    """)
    conn.commit()
    conn.close()

def add_user(username, password):
    """Adds a new user to the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False # Username already exists
    finally:
        conn.close()

def get_user(username):
    """Retrieves a user by username."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()
    return user

def get_user_by_id(user_id):
    """Retrieves a user by ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    return user

def store_feedback(user_id, feedback_text, rating):
    """Stores user feedback into the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    timestamp = datetime.now().isoformat()
    try:
        cursor.execute(
            "INSERT INTO feedback (user_id, feedback_text, rating, timestamp) VALUES (?, ?, ?, ?)",
            (user_id, feedback_text, rating, timestamp)
        )
        conn.commit()
        return True
    except Exception as e:
        print(f"Error storing feedback: {e}")
        return False
    finally:
        conn.close()

# Ensure DB is initialized when db.py is imported
init_db()
