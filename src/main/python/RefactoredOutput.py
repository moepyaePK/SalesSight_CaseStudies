To add a new feature that asks for user feedback after analyzing sales data, we'll primarily modify three files: `db.py` for database operations, `pages/sales_forecasting.py` to display the feedback form, and `Home.py` to initialize the new database table.

This enhancement will involve:
1.  **Database Schema Update**: Create a new table in `users.db` to store feedback.
2.  **Feedback Form UI**: Add a Streamlit form to the `Sales Forecasting` page.
3.  **Feedback Submission Logic**: Implement the functionality to save feedback to the database.
4.  **Integration**: Ensure the feedback form appears conditionally after a forecast is generated and doesn't pester the user repeatedly within the same session.

Let's assume the `pages/sales_forecasting.py` is the point where users "finish analyzing" their data, specifically after a forecast has been generated.

---

### **1. Modify `db.py`**

This file will handle creating the new `feedback` table and saving user feedback.

```python
# db.py

import sqlite3
import datetime

DATABASE_FILE = 'users.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row  # This allows accessing columns by name
    return conn

# --- Existing functions (e.g., create_user_table, add_user, get_user, etc.) ---

# Add these new functions:

def create_feedback_table():
    """Creates the feedback table if it doesn't exist."""
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            feedback_text TEXT NOT NULL,
            rating INTEGER, -- e.g., 1 to 5
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    conn.commit()
    conn.close()

def save_feedback(user_id, feedback_text, rating=None):
    """Saves user feedback into the database."""
    conn = get_db_connection()
    c = conn.cursor()
    try:
        c.execute("INSERT INTO feedback (user_id, feedback_text, rating) VALUES (?, ?, ?)",
                  (user_id, feedback_text, rating))
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Error saving feedback: {e}")
        return False
    finally:
        conn.close()

def get_user_id_by_username(username):
    """Retrieves the user ID given a username."""
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT id FROM users WHERE username = ?", (username,))
    result = c.fetchone()
    conn.close()
    return result['id'] if result else None

# --- End of new functions ---
```

---

### **2. Modify `pages/sales_forecasting.py`**

This is where the user interacts with the forecasting tool. We'll add the feedback form here, displayed conditionally after a forecast is generated.

```python
# pages/sales_forecasting.py

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import db # Import the database module

# Ensure user is logged in
if "username" not in st.session_state or not st.session_state.get("logged_in"):
    st.warning("Please log in to access this page.")
    st.stop()

# Ensure user_id is in session_state, if not, fetch it.
if "user_id" not in st.session_state:
    st.session_state["user_id"] = db.get_user_id_by_username(st.session_state["username"])
    if not st.session_state["user_id"]:
        st.error("Could not retrieve user ID. Please log in again.")
        st.session_state["logged_in"] = False
        st.experimental_rerun()

st.title("📊 Sales Forecasting")

st.markdown("""
    This page helps you forecast future sales based on your uploaded data.
    Please ensure your data contains a 'Date' column and a 'Sales' column.
""")

# Check if data is available for analysis
if 'df' not in st.session_state or st.session_state['df'].empty:
    st.info("Please upload your sales data on the 'Data Upload' page first.")
else:
    df = st.session_state['df'].copy()

    # --- Data Preprocessing (Ensure Date and Sales columns) ---
    if 'Date' not in df.columns:
        st.warning("The uploaded data does not contain a 'Date' column. Please rename a column or upload suitable data.")
        st.stop()
    if 'Sales' not in df.columns:
        st.warning("The uploaded data does not contain a 'Sales' column. Please rename a column or upload suitable data.")
        st.stop()
    
    try:
        df['Date'] = pd.to_datetime(df['Date'])
        df = df.sort_values('Date')
        df['Sales'] = pd.to_numeric(df['Sales'])
    except Exception as e:
        st.error(f"Error processing 'Date' or 'Sales' columns: {e}")
        st.info("Please ensure 'Date' column is in a recognized date format and 'Sales' is numeric.")
        st.stop()

    st.subheader("Current Sales Data Preview")
    st.write(df.tail())

    # --- Forecasting Parameters ---
    st.subheader("Forecast Settings")
    forecast_period_days = st.slider("Forecast for how many days into the future?", 7, 365, 30)

    # --- Generate Sales Forecast Button ---
    if st.button("Generate Sales Forecast", key="generate_forecast_btn"):
        # Placeholder for actual forecasting algorithm (e.g., ARIMA, Prophet, simple moving average)
        # For demonstration, we'll use a very simple linear extrapolation based on last values.
        
        if len(df) < 2:
            st.warning("Not enough data points to generate a meaningful forecast.")
            st.session_state.forecast_generated = False
        else:
            last_date = df['Date'].max()
            last_sales = df['Sales'].iloc[-1]
            
            # Calculate a simple average daily change from the last 7 days for a crude trend
            if len(df) > 7:
                recent_sales = df.tail(7)['Sales']
                daily_change_avg = (recent_sales.iloc[-1] - recent_sales.iloc[0]) / 7
            else:
                daily_change_avg = 0 # No significant trend detected with limited data

            forecast_data = []
            for i in range(1, forecast_period_days + 1):
                new_date = last_date + timedelta(days=i)
                # Apply a slight trend, avoid negative sales
                predicted_sales = max(0, last_sales + (daily_change_avg * i))
                forecast_data.append({'Date': new_date, 'Sales': predicted_sales})

            forecast_df = pd.DataFrame(forecast_data)
            
            # Combine historical and forecast for plotting
            combined_df = pd.concat([df, forecast_df], ignore_index=True)
            
            st.subheader("Sales Forecast Results")
            fig = px.line(combined_df, x='Date', y='Sales', title=f'Sales Forecast for the next {forecast_period_days} Days')
            fig.add_vline(x=last_date, line_width=2, line_dash="dash", line_color="red", annotation_text="End of Historical Data")
            st.plotly_chart(fig, use_container_width=True)
            
            st.success(f"Sales forecast generated for {forecast_period_days} days!")
            st.session_state.forecast_generated = True # Mark that forecast is done

    # --- Feedback Section (Appears after forecast) ---
    if st.session_state.get('forecast_generated', False) and not st.session_state.get('feedback_given', False):
        st.markdown("---")
        st.subheader("Help Us Improve! Your Feedback Matters.")
        st.write("We'd love to hear your thoughts on the sales forecasting tool and your overall experience.")

        with st.form("feedback_form", clear_on_submit=True):
            feedback_text = st.text_area("Your feedback (required):", height=100, key="feedback_text")
            rating = st.slider("Rate your experience with this tool (1=Poor, 5=Excellent):", 1, 5, 3, key="feedback_rating")
            
            submit_button = st.form_submit_button("Submit Feedback")

            if submit_button:
                if feedback_text:
                    user_id = st.session_state.get('user_id')
                    if user_id:
                        if db.save_feedback(user_id, feedback_text, rating):
                            st.success("Thank you for your valuable feedback! It helps us improve.")
                            st.session_state.feedback_given = True # Mark feedback as given for this session
                            st.experimental_rerun() # Rerun to hide the form after submission
                        else:
                            st.error("There was an error saving your feedback. Please try again.")
                    else:
                        st.error("Could not identify your user ID. Please log in again.")
                else:
                    st.warning("Please enter your feedback before submitting.")

```

---

### **3. Modify `Home.py`**

This file typically serves as the main entry point for the Streamlit app. We'll add a call to create the feedback table when the application starts.

```python
# Home.py

import streamlit as st
import db # Import the database module
from auth import login, register # Assuming auth.py handles login/register

# --- Database Initialization ---
# Ensure user table exists (this should already be present)
db.create_user_table()
# Add this line to ensure the feedback table is created when the app starts
db.create_feedback_table()

st.set_page_config(
    page_title="Sales Data Analyzer",
    page_icon="📈",
    layout="wide"
)

# Initialize session state variables if they don't exist
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'username' not in st.session_state:
    st.session_state['username'] = None
if 'user_id' not in st.session_state: # Initialize user_id
    st.session_state['user_id'] = None
if 'feedback_given' not in st.session_state:
    st.session_state['feedback_given'] = False
if 'forecast_generated' not in st.session_state:
    st.session_state['forecast_generated'] = False

# --- Authentication Logic (existing) ---
if not st.session_state['logged_in']:
    st.sidebar.title("Login / Register")
    auth_choice = st.sidebar.radio("Choose action", ["Login", "Register"])

    if auth_choice == "Login":
        username = st.sidebar.text_input("Username", key="login_username")
        password = st.sidebar.text_input("Password", type="password", key="login_password")
        if st.sidebar.button("Login"):
            # The login function in auth.py should also return user_id
            # Or get_user_id_by_username should be called after successful login
            if login(username, password): # Assuming login function in auth.py updates session state
                st.session_state['username'] = username
                st.session_state['logged_in'] = True
                # Fetch user_id and store in session_state
                st.session_state['user_id'] = db.get_user_id_by_username(username)
                st.sidebar.success("Logged in successfully!")
                st.experimental_rerun()
            else:
                st.sidebar.error("Incorrect username or password")
    else: # Register
        # ... (existing registration code) ...
        pass # Not modifying registration for this task

else:
    st.sidebar.success(f"Welcome, {st.session_state['username']}!")
    if st.sidebar.button("Logout"):
        st.session_state['logged_in'] = False
        st.session_state['username'] = None
        st.session_state['user_id'] = None # Clear user_id on logout
        st.session_state['df'] = pd.DataFrame() # Clear uploaded data
        st.session_state['forecast_generated'] = False # Reset state
        st.session_state['feedback_given'] = False # Reset state
        st.experimental_rerun()

    # --- Main Application Content (existing) ---
    st.markdown("# Welcome to the Sales Data Analyzer! 📈")
    st.markdown("Use the navigation on the left to upload your data, view dashboards, or forecast sales.")
    
    # You can add more introductory content here
    st.image("logo.png", width=200) # Assuming you have a logo.png

```

---

### **4. (Optional) Update `auth.py` or `pages/login.py`**

To ensure `st.session_state['user_id']` is reliably set right after login, you might want to adjust your `login` function in `auth.py` or `pages/login.py`.

**Example if `auth.py` contains `login` function:**

```python
# auth.py (example modification)

import db # Import db module
import bcrypt # Assuming you're using bcrypt for password hashing

# ... existing code ...

def login(username, password):
    """Authenticates a user and returns True if successful, False otherwise."""
    conn = db.get_db_connection()
    c = conn.cursor()
    c.execute("SELECT id, password_hash FROM users WHERE username = ?", (username,))
    user_data = c.fetchone()
    conn.close()

    if user_data:
        # Check password hash (assuming bcrypt is used)
        if bcrypt.checkpw(password.encode('utf-8'), user_data['password_hash']):
            # If authentication is handled here, you might set session state
            # but usually, session state is set in the calling Streamlit page (e.g., Home.py)
            return True
    return False

# In Home.py, after login(username, password) returns True:
# st.session_state['user_id'] = db.get_user_id_by_username(username)
# This was already covered in Home.py modification.
```

---

### **To Run the Application:**

1.  Make sure you have `streamlit`, `pandas`, and `plotly` installed:
    `pip install streamlit pandas plotly`
2.  Navigate to your project's root directory in the terminal.
3.  Run the Streamlit application:
    `streamlit run Home.py`

Now, after logging in and generating a sales forecast on the "Sales Forecasting" page, a feedback form will appear. Users can submit their thoughts and a rating, which will be stored in your `users.db` file. The form will disappear for the remainder of the session once feedback is submitted.