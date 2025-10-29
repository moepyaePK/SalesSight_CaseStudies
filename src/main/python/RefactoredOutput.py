Okay, this is a great feature to add for product improvement! We'll integrate a feedback mechanism into your Streamlit application.

Here's the plan:

1.  **Update `db.py`**:
    *   Add a new table `feedback` to your `users.db` database.
    *   Add a function to insert feedback into this table.
2.  **Update `pages/sales_forecasting.py`**:
    *   Display the feedback form *after* the sales analysis results are shown.
    *   Collect user rating and comments.
    *   Store the feedback in the database, associating it with the logged-in user.
3.  **Update `auth.py` (Assumption Check)**:
    *   We'll assume `auth.py` correctly sets `st.session_state.user_id` upon successful login, which is crucial for associating feedback with a specific user.

Let's get started!

---

### Step 1: Modify `db.py` to handle feedback storage

We'll add a new function to create the `feedback` table and another to insert feedback.

```python
# File: db.py

import sqlite3
import hashlib
import streamlit as st # Assuming Streamlit is used for session state in auth

DATABASE_NAME = "users.db"

def get_db_connection():
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def create_users_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def create_feedback_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            rating INTEGER NOT NULL,
            comments TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)
    conn.commit()
    conn.close()

# Ensure tables are created when the module is imported
create_users_table()
create_feedback_table()


def register_user(username, password):
    conn = get_db_connection()
    cursor = conn.cursor()
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False # Username already exists
    finally:
        conn.close()

def authenticate_user(username, password):
    conn = get_db_connection()
    cursor = conn.cursor()
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    cursor.execute("SELECT id, username FROM users WHERE username = ? AND password = ?", (username, hashed_password))
    user = cursor.fetchone()
    conn.close()
    if user:
        return {'id': user['id'], 'username': user['username']}
    return None

def add_feedback(user_id, rating, comments):
    """Inserts user feedback into the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO feedback (user_id, rating, comments) VALUES (?, ?, ?)",
            (user_id, rating, comments)
        )
        conn.commit()
        return True
    except Exception as e:
        st.error(f"Error saving feedback: {e}")
        return False
    finally:
        conn.close()

# You can add functions to retrieve feedback for admin purposes later if needed
def get_all_feedback():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT
            f.id,
            u.username,
            f.rating,
            f.comments,
            f.timestamp
        FROM
            feedback f
        JOIN
            users u ON f.user_id = u.id
        ORDER BY f.timestamp DESC
    """)
    feedback_data = cursor.fetchall()
    conn.close()
    return feedback_data

```

**Explanation for `db.py` changes:**
*   `create_feedback_table()`: This new function defines the schema for the `feedback` table. It includes `user_id` (linked to `users` table), `rating`, `comments`, and `timestamp`.
*   `add_feedback()`: This function takes `user_id`, `rating`, and `comments` and inserts them into the `feedback` table.
*   We've added calls to `create_users_table()` and `create_feedback_table()` at the end of the `db.py` file to ensure these tables exist when the application starts.
*   Added `get_all_feedback()` (optional but useful for later analysis).

---

### Step 2: Modify `pages/sales_forecasting.py` to display the feedback form

We need to add the feedback form after the sales analysis results are displayed. We'll use `st.session_state` to determine when the analysis has completed.

```python
# File: pages/sales_forecasting.py

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
import numpy as np
import db # Import the database module

# --- Helper Functions (assuming these are already in your utils.py or sales_forecasting.py) ---
# You might have more sophisticated functions for preprocessing, model training, etc.
# These are placeholders for demonstration.

def preprocess_data(df):
    # Ensure 'Date' column is datetime
    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        df.dropna(subset=['Date'], inplace=True)
        df.set_index('Date', inplace=True)
    elif 'OrderDate' in df.columns: # Common alternative
        df['OrderDate'] = pd.to_datetime(df['OrderDate'], errors='coerce')
        df.dropna(subset=['OrderDate'], inplace=True)
        df.set_index('OrderDate', inplace=True)
    elif 'InvoiceDate' in df.columns: # Another alternative
        df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'], errors='coerce')
        df.dropna(subset=['InvoiceDate'], inplace=True)
        df.set_index('InvoiceDate', inplace=True)
    else:
        st.error("No suitable date column found (e.g., 'Date', 'OrderDate', 'InvoiceDate'). Please ensure your sales data has one.")
        return pd.DataFrame() # Return empty DataFrame if no date column

    # Ensure 'Sales' or similar column exists and is numeric
    sales_col = next((col for col in ['Sales', 'Revenue', 'Amount'] if col in df.columns), None)
    if sales_col:
        df[sales_col] = pd.to_numeric(df[sales_col], errors='coerce')
        df.dropna(subset=[sales_col], inplace=True)
    else:
        st.error("No suitable sales column found (e.g., 'Sales', 'Revenue', 'Amount'). Please ensure your sales data has one.")
        return pd.DataFrame()

    return df

def aggregate_sales_data(df, sales_col='Sales', freq='D'):
    """Aggregates sales data by frequency."""
    df_agg = df.resample(freq)[sales_col].sum().fillna(0)
    return df_agg

def train_and_forecast_model(data, forecast_periods=30, model_type='Linear Regression'):
    """Trains a model and generates a forecast."""
    # Create numerical features from date
    data['day_of_year'] = data.index.dayofyear
    data['month'] = data.index.month
    data['day_of_week'] = data.index.dayofweek
    data['week_of_year'] = data.index.isocalendar().week.astype(int) # Convert to int

    X = data[['day_of_year', 'month', 'day_of_week', 'week_of_year']]
    y = data['Sales']

    # Handle cases where not enough data points
    if len(data) < 2:
        st.warning("Not enough data to train a model. Please upload more sales data.")
        return pd.DataFrame(), pd.DataFrame()

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    if model_type == 'Linear Regression':
        model = LinearRegression()
    elif model_type == 'Random Forest':
        model = RandomForestRegressor(n_estimators=100, random_state=42)
    else:
        st.error("Unsupported model type.")
        return pd.DataFrame(), pd.DataFrame()

    model.fit(X_train, y_train)
    predictions = model.predict(X_test)
    rmse = np.sqrt(mean_squared_error(y_test, predictions))
    st.write(f"Model RMSE: {rmse:.2f}")

    # Generate future dates for forecasting
    last_date = data.index.max()
    future_dates = pd.date_range(start=last_date + timedelta(days=1), periods=forecast_periods, freq='D')
    future_data = pd.DataFrame(index=future_dates)
    future_data['day_of_year'] = future_data.index.dayofyear
    future_data['month'] = future_data.index.month
    future_data['day_of_week'] = future_data.index.dayofweek
    future_data['week_of_year'] = future_data.index.isocalendar().week.astype(int)

    forecast = model.predict(future_data)
    forecast_df = pd.DataFrame({'Forecasted Sales': forecast}, index=future_dates)
    return data, forecast_df

# --- Streamlit Page Logic ---

st.set_page_config(page_title="Sales Forecasting", page_icon="📈")

if 'authenticated' not in st.session_state or not st.session_state.authenticated:
    st.warning("Please log in to access this page.")
    st.stop()

st.title("📈 Sales Forecasting and Analysis")

# Initialize session state for analysis completion
if 'sales_analyzed' not in st.session_state:
    st.session_state.sales_analyzed = False

# Check if data was uploaded in data_upload.py and stored in session state
if 'uploaded_data' in st.session_state and st.session_state.uploaded_data is not None:
    df = st.session_state.uploaded_data

    st.subheader("Raw Data Preview")
    st.dataframe(df.head())

    # --- Analysis & Forecasting Controls ---
    st.sidebar.header("Analysis Settings")
    date_col_options = [col for col in df.columns if 'date' in col.lower()]
    selected_date_col = st.sidebar.selectbox("Select Date Column", options=date_col_options)
    
    sales_col_options = [col for col in df.columns if 'sales' in col.lower() or 'revenue' in col.lower() or 'amount' in col.lower()]
    selected_sales_col = st.sidebar.selectbox("Select Sales/Revenue Column", options=sales_col_options)

    if selected_date_col and selected_sales_col:
        
        # Preprocess the data using selected columns
        try:
            processed_df = df[[selected_date_col, selected_sales_col]].copy()
            processed_df.rename(columns={selected_date_col: 'Date', selected_sales_col: 'Sales'}, inplace=True)
            processed_df = preprocess_data(processed_df)

            if not processed_df.empty:
                st.subheader("Aggregated Daily Sales")
                aggregated_data = aggregate_sales_data(processed_df, sales_col='Sales', freq='D')
                st.line_chart(aggregated_data)

                # Forecasting
                st.subheader("Sales Forecasting")
                forecast_periods = st.sidebar.slider("Forecast for how many days?", 7, 180, 30)
                model_type = st.sidebar.selectbox("Select Forecasting Model", ['Linear Regression', 'Random Forest'])

                if st.sidebar.button("Run Forecast"):
                    with st.spinner("Generating forecast..."):
                        historical_data, forecast_data = train_and_forecast_model(
                            aggregated_data.to_frame(name='Sales'),
                            forecast_periods,
                            model_type
                        )

                        if not historical_data.empty and not forecast_data.empty:
                            st.write("### Sales Forecast Results")
                            fig = px.line(
                                historical_data['Sales'],
                                x=historical_data.index,
                                y='Sales',
                                title="Historical and Forecasted Sales"
                            )
                            fig.add_scatter(
                                x=forecast_data.index,
                                y=forecast_data['Forecasted Sales'],
                                mode='lines',
                                name='Forecast',
                                line=dict(color='red', dash='dash')
                            )
                            st.plotly_chart(fig, use_container_width=True)

                            st.write("#### Forecasted Values")
                            st.dataframe(forecast_data)
                            st.session_state.sales_analyzed = True # Set flag after analysis

            else:
                st.error("Processed data is empty. Please check your date and sales columns.")
                st.session_state.sales_analyzed = False # Reset flag if analysis fails
        except Exception as e:
            st.error(f"An error occurred during data processing or forecasting: {e}")
            st.session_state.sales_analyzed = False # Reset flag if analysis fails

    else:
        st.warning("Please select both a Date and a Sales/Revenue column from the sidebar to proceed with analysis.")
        st.session_state.sales_analyzed = False # Reset flag if columns not selected
else:
    st.info("Please upload a sales file on the 'Data Upload' page to analyze.")
    st.session_state.sales_analyzed = False # Reset if no data


# --- Feedback Section ---
if st.session_state.sales_analyzed:
    st.markdown("---")
    st.subheader("🌟 We'd love your feedback!")
    st.write("Help us improve our tools by sharing your experience.")

    with st.form(key="feedback_form"):
        rating = st.slider(
            "How would you rate your overall experience with the sales forecasting tool?",
            1, 5, 5, help="1 = Very Poor, 5 = Excellent"
        )
        comments = st.text_area(
            "Do you have any suggestions, comments, or encountered any issues?",
            placeholder="e.g., 'The forecast was very accurate!', 'Could you add a feature for seasonal adjustments?'",
            height=150
        )
        submit_feedback = st.form_submit_button("Submit Feedback")

        if submit_feedback:
            if 'user_id' in st.session_state:
                user_id = st.session_state.user_id
                if db.add_feedback(user_id, rating, comments):
                    st.success("🎉 Thank you for your valuable feedback! We appreciate it.")
                    st.session_state.sales_analyzed = False # Prevent re-submission on refresh
                else:
                    st.error("Failed to submit feedback. Please try again later.")
            else:
                st.error("You must be logged in to submit feedback.")

```

**Explanation for `pages/sales_forecasting.py` changes:**

1.  **`import db`**: We import our `db` module to interact with the database.
2.  **`st.session_state.sales_analyzed`**: A new session state variable is introduced.
    *   It's initialized to `False`.
    *   It's set to `True` *only after* a successful sales forecast has been displayed.
    *   It's reset to `False` if analysis fails or if new data is needed, ensuring the feedback form only appears when relevant.
3.  **Conditional Feedback Section**:
    ```python
    if st.session_state.sales_analyzed:
        # ... feedback form code ...
    ```
    This ensures the feedback form only appears once the user has actually seen the analysis results.
4.  **`st.form("feedback_form")`**: We use a Streamlit form for the feedback to encapsulate the inputs and ensure an atomic submission.
    *   `st.slider` for a 1-5 rating.
    *   `st.text_area` for open-ended comments.
    *   `st.form_submit_button` to trigger the submission.
5.  **Submission Logic**:
    *   When the form is submitted, it checks if `st.session_state.user_id` exists (meaning the user is logged in).
    *   It calls `db.add_feedback()` to store the data.
    *   Displays a success or error message.
    *   Sets `st.session_state.sales_analyzed = False` after successful submission to hide the form until a new analysis is run, preventing accidental duplicate submissions or allowing a new analysis to trigger it again.

---

### To test this:

1.  **Save the changes:** Make sure both `db.py` and `pages/sales_forecasting.py` are updated as shown.
2.  **Run your Streamlit app:** `streamlit run Home.py` (or whatever your main entry point is).
3.  **Log in:** Use an existing user or register a new one.
4.  **Go to "Data Upload":** Upload a sample sales CSV file. Ensure it has a date column (e.g., `Date`, `OrderDate`) and a sales/revenue column (e.g., `Sales`, `Amount`).
5.  **Go to "Sales Forecasting":**
    *   Select the correct date and sales columns in the sidebar.
    *   Click "Run Forecast".
    *   After the forecast graph and data are displayed, you should see the "We'd love your feedback!" section appear.
6.  **Submit Feedback:** Fill in the rating and comments, then click "Submit Feedback". You should see a success message.
7.  **Verify (Optional):** You can use a tool like DB Browser for SQLite to open `users.db` and check if the `feedback` table contains your submitted feedback. (If you want to view it in the app, you'd need to build an admin page).

This enhancement provides a clear and user-friendly way to gather feedback on your sales analysis tool!