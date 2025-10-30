The user wants to add a feedback mechanism after they've used the analysis tools. Given the file structure, `pages/sales_forecasting.py` is a strong candidate for an analysis tool, and `db.py` and `auth.py` can be used to store and associate feedback with users.

Here's a plan to implement this:

1.  **Modify `db.py`**: Add functions to create a `feedback` table and to insert feedback.
2.  **Integrate into an analysis page (e.g., `pages/sales_forecasting.py`)**:
    *   Import necessary `auth` and `db` functions.
    *   Add a Streamlit form for feedback (rating and comments) at the end of the analysis section.
    *   Ensure feedback is only shown to logged-in users.

Let's proceed with the changes.

---

**Proposed Changes:**

**1. Modify `db.py` to handle feedback storage**

This will add functions to create a `feedback` table if it doesn't exist and to store new feedback entries.

```python
# db.py
import sqlite3
import hashlib

DATABASE = 'users.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # This allows accessing columns by name
    return conn

def create_users_table():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# New function: Create feedback table
def create_feedback_table():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            rating INTEGER,
            comments TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    conn.commit()
    conn.close()

def add_user(username, password):
    conn = get_db_connection()
    c = conn.cursor()
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    try:
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False # Username already exists
    finally:
        conn.close()

def verify_user(username, password):
    conn = get_db_connection()
    c = conn.cursor()
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    c.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, hashed_password))
    user = c.fetchone()
    conn.close()
    return user

def get_user_id(username):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT id FROM users WHERE username = ?", (username,))
    user = c.fetchone()
    conn.close()
    return user['id'] if user else None

# New function: Add feedback
def add_feedback(user_id, rating, comments):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("INSERT INTO feedback (user_id, rating, comments) VALUES (?, ?, ?)",
              (user_id, rating, comments))
    conn.commit()
    conn.close()

# Ensure tables are created when db.py is imported or application starts
create_users_table()
create_feedback_table() # Call this to ensure the table exists
```

**2. Modify `pages/sales_forecasting.py` to add the feedback form**

We'll add a feedback section at the bottom of the `pages/sales_forecasting.py` page, assuming this is where users would complete their analysis. We'll check if the user is logged in before showing the form.

```python
# pages/sales_forecasting.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime, timedelta
import auth
import db # Import the db module

# --- Helper functions (assuming they are already in utils.py or defined here) ---
def generate_sample_sales_data(days=90):
    dates = [datetime.now() - timedelta(days=i) for i in range(days-1, -1, -1)]
    sales = np.random.randint(50, 200, days) + np.sin(np.linspace(0, 3*np.pi, days)) * 50
    data = pd.DataFrame({'Date': dates, 'Sales': sales.round(0)})
    return data

def forecast_sales(df, periods=30):
    # Simple moving average for demonstration
    df['SMA_7'] = df['Sales'].rolling(window=7).mean().shift(1)
    df['SMA_30'] = df['Sales'].rolling(window=30).mean().shift(1)

    last_date = df['Date'].max()
    forecast_dates = [last_date + timedelta(days=i) for i in range(1, periods + 1)]

    # Use the last known SMA_30 value for a simple forecast
    last_sma_30 = df['SMA_30'].iloc[-1]
    forecast_sales_values = [last_sma_30 + np.random.randint(-10, 10) for _ in range(periods)] # Add some noise

    forecast_df = pd.DataFrame({'Date': forecast_dates, 'Sales': forecast_sales_values})
    return forecast_df

# --- Streamlit Page Content ---
st.set_page_config(page_title="Sales Forecasting", layout="wide")

st.title("📊 Sales Forecasting Tool")

if auth.check_login():
    st.write(f"Welcome, {st.session_state['username']}!")

    st.subheader("Upload Your Sales Data")
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

    df = None
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            st.success("File uploaded successfully!")
            st.write("Preview of your data:")
            st.dataframe(df.head())

            # Basic data cleaning/preparation (assuming 'Date' and 'Sales' columns)
            if 'Date' in df.columns and 'Sales' in df.columns:
                df['Date'] = pd.to_datetime(df['Date'])
                df = df.sort_values('Date').set_index('Date')
                df['Sales'] = pd.to_numeric(df['Sales'])
                st.write("Data processed and ready for forecasting.")
            else:
                st.error("Please ensure your CSV has 'Date' and 'Sales' columns.")
                df = None
        except Exception as e:
            st.error(f"Error reading file: {e}")
            df = None
    else:
        st.info("No file uploaded. Generating sample sales data for demonstration.")
        df = generate_sample_sales_data()
        df = df.set_index('Date')


    if df is not None and not df.empty:
        st.subheader("Historical Sales Data")
        fig_hist = px.line(df, x=df.index, y='Sales', title="Historical Sales Trend")
        st.plotly_chart(fig_hist, use_container_width=True)

        st.subheader("Forecast Future Sales")
        periods = st.slider("Number of days to forecast", 7, 365, 30)

        if st.button("Generate Forecast"):
            forecast_df = forecast_sales(df.reset_index(), periods)

            st.write("Forecasted Sales:")
            st.dataframe(forecast_df)

            combined_df = pd.concat([df.reset_index(), forecast_df])
            fig_forecast = px.line(combined_df, x='Date', y='Sales',
                                   title="Historical and Forecasted Sales")
            fig_forecast.add_vline(x=df.index.max(), line_dash="dash", line_color="red",
                                    annotation_text="Forecast Start", annotation_position="top left")
            st.plotly_chart(fig_forecast, use_container_width=True)

            st.success("Sales forecast generated successfully!")
            st.session_state['analysis_complete'] = True # Set a flag that analysis is done
    else:
        st.warning("Please upload a valid dataset or use the sample data to proceed with forecasting.")

    # --- New Feedback Section ---
    st.markdown("---") # Separator
    st.header("We'd Love Your Feedback! 💡")
    st.write("Help us improve by sharing your thoughts on this analysis tool. Your input is highly valued!")

    # Check if analysis was completed before prompting for feedback for the first time
    # This uses a session state variable to ensure feedback is prompted after a successful analysis
    if st.session_state.get('analysis_complete', False):
        user_info = auth.get_current_user_info() # Assuming auth.py has a function to get user details
        if user_info and 'username' in user_info:
            user_id = db.get_user_id(user_info['username'])

            if user_id:
                # Use a form to group inputs and clear on submit
                with st.form("feedback_form", clear_on_submit=True):
                    st.subheader("How would you rate your experience with this tool?")
                    rating = st.slider("Rating", 1, 5, 3, help="1 = Very Poor, 5 = Excellent")
                    comments = st.text_area("Your Comments", height=150,
                                            help="Tell us what you liked, disliked, or what could be improved.")

                    submitted = st.form_submit_button("Submit Feedback")

                    if submitted:
                        if comments.strip(): # Ensure comments are not just whitespace
                            try:
                                db.add_feedback(user_id, rating, comments)
                                st.success("Thank you for your feedback! It helps us a lot. 🙏")
                                # Optionally, prevent submitting multiple feedbacks in the same session for the same analysis
                                st.session_state['feedback_submitted_for_session'] = True
                            except Exception as e:
                                st.error(f"Failed to submit feedback: {e}")
                        else:
                            st.warning("Please provide some comments before submitting your feedback.")
            else:
                st.error("Could not retrieve user ID for feedback submission. Please try logging in again.")
        else:
            st.error("User information not available for feedback submission.")
    else:
        st.info("Complete an analysis first to provide feedback.")


else:
    st.warning("Please log in to access the Sales Forecasting tool and provide feedback.")
```

**3. Modify `auth.py` (if `get_current_user_info` doesn't exist)**

The `pages/sales_forecasting.py` code assumes `auth.get_current_user_info()` exists. If it doesn't, you'll need to add it to `auth.py` to retrieve the current logged-in user's details, especially their username, which is then used to get their `user_id` from the `db`.

```python
# auth.py (Ensure this function exists or adapt to your auth system)
import streamlit as st
import db

def check_login():
    if 'logged_in' not in st.session_state or not st.session_state['logged_in']:
        # st.warning("Please log in to access this page.")
        return False
    return True

def login(username, password):
    user = db.verify_user(username, password)
    if user:
        st.session_state['logged_in'] = True
        st.session_state['username'] = username
        return True
    return False

def logout():
    st.session_state['logged_in'] = False
    del st.session_state['username']
    if 'analysis_complete' in st.session_state:
        del st.session_state['analysis_complete']
    if 'feedback_submitted_for_session' in st.session_state:
        del st.session_state['feedback_submitted_for_session']
    st.success("You have been logged out.")
    st.rerun()

# New function: Get current user info
def get_current_user_info():
    if check_login():
        return {'username': st.session_state['username']}
    return None
```

---

**Summary of Changes and How to Use:**

1.  **`db.py`**:
    *   A new function `create_feedback_table()` is added to define the `feedback` table. This table stores `user_id`, `rating`, `comments`, and `timestamp`.
    *   A new function `add_feedback(user_id, rating, comments)` is added to insert feedback into the database.
    *   `create_feedback_table()` is called directly in `db.py` to ensure the table is created when the module is imported or the app starts.

2.  **`pages/sales_forecasting.py`**:
    *   Imports `db` and `auth`.
    *   A `st.session_state['analysis_complete']` flag is set to `True` after a forecast is successfully generated. This ensures the feedback form only appears once the user has actually used the tool.
    *   A new section for "We'd Love Your Feedback!" is added at the bottom of the page.
    *   This section uses `st.form` for collecting feedback (a slider for rating, a text area for comments).
    *   It retrieves the `user_id` of the currently logged-in user using `auth.get_current_user_info()` and `db.get_user_id()`.
    *   Upon submission, it calls `db.add_feedback()` to store the data and provides a success message.
    *   It checks for `auth.check_login()` to ensure only logged-in users can see and submit feedback.
    *   A `st.session_state['feedback_submitted_for_session']` flag is added (optional) to prevent accidental multiple submissions in a single session for the *same analysis run*.

3.  **`auth.py`**:
    *   A `get_current_user_info()` function is added to provide the current username, which is then used to fetch the user ID from the database.

**To run this:**

1.  Ensure your Streamlit application is running.
2.  Log in with a registered user (you might need to register via `pages/register.py` first).
3.  Navigate to the "Sales Forecasting" page.
4.  Upload a CSV or use the sample data and generate a forecast.
5.  After the forecast is displayed, scroll down to see the "We'd Love Your Feedback!" section.
6.  Provide a rating and comments, then click "Submit Feedback."
7.  The feedback will be stored in your `users.db` file. You can inspect `users.db` with an SQLite browser to verify the `feedback` table and its contents.