To add a feature that asks the user about the effectiveness of the tool after they analyze their sales file, we'll implement the following steps:

1.  **Modify `db.py`**: Add functions to create a new `feedback` table and to insert feedback data into it.
2.  **Modify `auth.py`**: Ensure we can retrieve the `user_id` of the currently logged-in user.
3.  **Modify `pages/sales_forecasting.py`**: This is where the sales analysis likely happens. We will add the feedback form after the analysis results are displayed.

---

### Step 1: Update `db.py` to handle feedback storage

We need to add a new table to `users.db` to store the feedback.

**File: `db.py`**

```python
import sqlite3
import hashlib # Assuming this is used for password hashing in auth.py if not already imported

DATABASE_FILE = 'users.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row  # This allows accessing columns by name
    return conn

# Existing functions in db.py (e.g., create_users_table, add_user, check_user, etc.)
# ...

# --- NEW FUNCTIONS FOR FEEDBACK ---

def create_feedback_table():
    """Creates the feedback table if it doesn't already exist."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            feature_name TEXT NOT NULL,
            effectiveness_score INTEGER NOT NULL,
            comments TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE SET NULL
        )
    ''')
    conn.commit()
    conn.close()

def insert_feedback(user_id, feature_name, effectiveness_score, comments):
    """Inserts a new feedback entry into the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO feedback (user_id, feature_name, effectiveness_score, comments) VALUES (?, ?, ?, ?)',
        (user_id, feature_name, effectiveness_score, comments)
    )
    conn.commit()
    conn.close()
    
# Call create_feedback_table() when the database module is imported, 
# ensuring the table exists. This is a common pattern for Streamlit apps.
create_feedback_table() 
```

**Explanation of changes in `db.py`:**
*   `create_feedback_table()`: This function defines and creates a new table named `feedback`.
    *   `id`: Primary key for unique feedback entries.
    *   `user_id`: Foreign key referencing the `users` table, allowing us to link feedback to a specific user. `ON DELETE SET NULL` ensures feedback remains even if a user account is deleted.
    *   `feature_name`: To specify which feature the feedback is for (e.g., "Sales Forecasting").
    *   `effectiveness_score`: An integer representing the rating (e.g., 1-5).
    *   `comments`: An optional text field for detailed feedback.
    *   `timestamp`: Automatically records when the feedback was submitted.
*   `insert_feedback()`: A utility function to easily add new feedback records.
*   `create_feedback_table()` is called directly when `db.py` is imported. This ensures the table is created early in the application lifecycle.

---

### Step 2: Update `auth.py` to get current user ID

We need the `user_id` to link the feedback to a specific user. Assuming your `auth.py` handles user sessions with `st.session_state`, we'll add a helper function.

**File: `auth.py`**

```python
import streamlit as st
import hashlib
from db import get_db_connection # Assuming get_db_connection is in db.py

# ... (Existing login, register, logout functions) ...

def get_current_username():
    """Returns the username of the currently logged-in user from session state."""
    return st.session_state.get('username')

def get_current_user_id():
    """
    Returns the user ID of the currently logged-in user from session state.
    Assumes 'user_id' is stored in st.session_state upon successful login.
    If not, it fetches it from the database using the username.
    """
    if 'user_id' in st.session_state and st.session_state['user_id'] is not None:
        return st.session_state['user_id']
    else:
        # Fallback: if user_id is not directly in session, try to get it from username
        username = get_current_username()
        if username:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
            user = cursor.fetchone()
            conn.close()
            if user:
                # Store it in session state for future use
                st.session_state['user_id'] = user['id']
                return user['id']
    return None

# Make sure your login function (e.g., in auth.py) populates st.session_state['user_id']
# Example (if your login function looks similar):
# def login_user(username, password):
#     conn = get_db_connection()
#     cursor = conn.cursor()
#     cursor.execute('SELECT id, username, password FROM users WHERE username = ?', (username,))
#     user = cursor.fetchone()
#     conn.close()
#     if user and check_password_hash(user['password'], password): # Assuming check_password_hash exists
#         st.session_state['logged_in'] = True
#         st.session_state['username'] = username
#         st.session_state['user_id'] = user['id'] # IMPORTANT: Store user_id here
#         return True
#     return False

```

**Explanation of changes in `auth.py`:**
*   `get_current_user_id()`: This function retrieves the `user_id` from Streamlit's `session_state`. It includes a fallback to fetch it from the database if it's not directly present in `session_state`, though it's best practice to store it there during login.
*   **Important:** Ensure your existing `login_user` function (likely in `auth.py`) stores the `user_id` in `st.session_state` when a user successfully logs in.

---

### Step 3: Add feedback form to `pages/sales_forecasting.py`

This is where the user interacts with the sales analysis. We'll present the feedback form *after* they've performed an analysis.

**File: `pages/sales_forecasting.py`**

```python
import streamlit as st
import pandas as pd
# Assuming db and auth are in the root directory or correctly imported via path
from db import insert_feedback 
from auth import get_current_user_id, get_current_username # Import necessary auth functions

st.set_page_config(page_title="Sales Forecasting", page_icon="📈")

st.title("📈 Sales Forecasting and Analysis")

# --- Existing logic for sales file analysis and forecasting ---
# This part of your code would involve uploading files, processing them,
# displaying charts, tables, and forecasts.
# We need a way to determine when this analysis is "complete".
# For demonstration, let's use a session state variable.

if 'sales_analysis_completed' not in st.session_state:
    st.session_state['sales_analysis_completed'] = False

# Simulate sales analysis completion
if st.button("Perform Sales Analysis (Simulated)"):
    # In a real scenario, this would be triggered after data processing
    # and model execution.
    st.write("Performing complex sales analysis...")
    st.write("Displaying forecast results...")
    # Example dummy results:
    st.success("Sales analysis complete! Here are your forecasts.")
    st.line_chart(pd.DataFrame({'Actual': [10, 12, 15, 13, 16], 'Forecast': [11, 13, 14, 14, 15]}))
    st.session_state['sales_analysis_completed'] = True
    # Reset feedback submission state for a new analysis session
    st.session_state['feedback_submitted_for_this_analysis'] = False

# Only show the feedback form if the analysis has been completed
if st.session_state.get('sales_analysis_completed'):
    st.markdown("---") # Separator for clarity
    st.subheader("We value your feedback!")
    st.write("How effective did you find our sales forecasting tool for your needs?")

    # Define effectiveness options and their corresponding scores
    feedback_options = {
        "1 - Very Ineffective": 1,
        "2 - Ineffective": 2,
        "3 - Neutral": 3,
        "4 - Effective": 4,
        "5 - Very Effective": 5
    }
    
    # Check if feedback has already been submitted for this analysis session
    if not st.session_state.get('feedback_submitted_for_this_analysis', False):
        selected_effectiveness_text = st.radio(
            "Select your rating:",
            list(feedback_options.keys()),
            index=2, # Default to "3 - Neutral"
            key="effectiveness_rating_radio" # Unique key for this widget
        )
        effectiveness_score = feedback_options[selected_effectiveness_text]

        comments = st.text_area("Optional: Any specific comments or suggestions?", key="feedback_comments_area")

        if st.button("Submit Feedback", key="submit_feedback_button"):
            user_id = get_current_user_id() # Get the logged-in user's ID
            username = get_current_username() # For logging/debug if needed

            if user_id is None:
                st.warning("Please log in to submit feedback.")
            else:
                try:
                    insert_feedback(
                        user_id=user_id,
                        feature_name="Sales Forecasting", # Specific to this page/feature
                        effectiveness_score=effectiveness_score,
                        comments=comments
                    )
                    st.success("Thank you for your valuable feedback! We appreciate it.")
                    st.session_state['feedback_submitted_for_this_analysis'] = True
                    # Optionally clear the form elements visually
                    st.session_state["effectiveness_rating_radio"] = "3 - Neutral" # Reset radio
                    st.session_state["feedback_comments_area"] = "" # Clear text area
                except Exception as e:
                    st.error(f"Failed to submit feedback. Please try again. Error: {e}")
    else:
        st.info("You've already submitted feedback for this analysis session. Thank you!")

# --- Rest of your sales_forecasting.py content ---
# ... (e.g., sidebar, other analysis components) ...

```

**Explanation of changes in `pages/sales_forecasting.py`:**
*   **Imports**: Import `insert_feedback` from `db` and `get_current_user_id`, `get_current_username` from `auth`.
*   **`st.session_state['sales_analysis_completed']`**: A flag to control when the feedback form appears. It should be set to `True` *after* the sales analysis results are presented to the user. I've added a dummy button to simulate this.
*   **Feedback Form**:
    *   `st.subheader` and `st.write` introduce the feedback section.
    *   `st.radio` provides a Likert scale (1-5) for effectiveness.
    *   `st.text_area` allows for optional detailed comments.
    *   `st.button("Submit Feedback")` triggers the submission process.
*   **Submission Logic**:
    *   When the button is clicked, `get_current_user_id()` fetches the ID of the logged-in user.
    *   `insert_feedback()` is called to save the data to the `feedback` table.
    *   Success/error messages (`st.success`, `st.error`) provide user feedback.
    *   `st.session_state['feedback_submitted_for_this_analysis']` is used to prevent multiple submissions for the same analysis results in a single session.

---

### To run and test:

1.  **Ensure all files are saved** with the changes.
2.  **Make sure your `users.db` exists** and has a `users` table (created by your `auth.py`/`db.py` on first run usually).
3.  **Start your Streamlit app**: `streamlit run Home.py` (or `streamlit run pages/login.py` if that's your entry for pages).
4.  **Log in** with a registered user.
5.  **Navigate to the "Sales Forecasting" page**.
6.  **Click the "Perform Sales Analysis (Simulated)" button** (or whichever action in your actual code triggers the analysis completion).
7.  **The feedback form should appear**. Select a rating, add comments, and click "Submit Feedback".
8.  **Verify**: You can use a SQLite browser (like DB Browser for SQLite) to open `users.db` and check if the `feedback` table has been created and contains your submitted data.