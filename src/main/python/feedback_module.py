"""
feedback_module.py

This module provides Streamlit UI components and logic for collecting user feedback
on the sales forecasting model. It integrates with a database module (`db.py`)
to store feedback data, including user ratings and comments.
"""

import streamlit as st
import datetime
import uuid
import sys
import os

# Attempt to import the database module.
# The `db.py` file is expected to exist at the project root and contain
# functions for database interaction, specifically `store_feedback`.
try:
    import db
except ImportError:
    st.error("Error: Could not import the 'db' module. Please ensure 'db.py' is in the same directory or accessible via PYTHONPATH.")
    st.info("Feedback submission will be simulated as the database module is not available.")

    # Define a dummy class for `db` to prevent crashes if `db.py` is not yet implemented
    # or not found, allowing the UI component to be tested in isolation.
    class DummyDB:
        """
        A dummy database class to simulate feedback storage when the actual `db.py`
        module is not available or fully implemented.
        """
        def store_feedback(self, user_id: str, analysis_session_id: str, rating: int, feedback_text: str) -> bool:
            """
            Simulates storing user feedback.

            Args:
                user_id (str): The unique identifier of the user.
                analysis_session_id (str): The unique identifier for the analysis session.
                rating (int): The user's rating (e.g., 1-5).
                feedback_text (str): The user's detailed feedback.

            Returns:
                bool: True if storage was "successful", False otherwise.
            """
            st.warning("Database module ('db.py') not fully implemented or accessible. Feedback will not be stored persistently.")
            st.info(f"Simulated feedback storage: User ID='{user_id}', Session ID='{analysis_session_id}', "
                    f"Rating={rating}, Feedback='{feedback_text}'")
            return True
    db = DummyDB()
except AttributeError:
    st.error("Error: The 'db' module was imported, but 'store_feedback' function was not found.")
    st.info("Feedback submission will be simulated as the required database function is missing.")
    # If db.py exists but store_feedback is missing, replace db with DummyDB
    class DummyDB:
        def store_feedback(self, user_id: str, analysis_session_id: str, rating: int, feedback_text: str) -> bool:
            st.warning("The 'db.store_feedback' function is missing. Feedback will not be stored persistently.")
            st.info(f"Simulated feedback storage: User ID='{user_id}', Session ID='{analysis_session_id}', "
                    f"Rating={rating}, Feedback='{feedback_text}'")
            return True
    db = DummyDB()


def display_feedback_form(user_id: str, analysis_session_id: str):
    """
    Displays a Streamlit form for users to submit feedback on the sales forecasting model.

    This function should be called within a Streamlit application after the sales data
    analysis results have been presented to the user. It captures a numerical rating
    and optional text feedback, then attempts to store this information in the database
    via the `db.store_feedback` function.

    Args:
        user_id (str): The unique identifier of the current user. This is crucial for
                       linking feedback to specific users.
        analysis_session_id (str): A unique identifier for the current analysis session.
                                   This helps link feedback to specific model runs,
                                   data sets, or forecasting scenarios.
    """
    st.subheader("We'd Love Your Feedback!")
    st.write("Help us improve our sales forecasting model by sharing your thoughts on its performance and usefulness.")

    # Use a unique key for the form to prevent issues if multiple forms are on the page
    # or if the page re-runs. This ensures Streamlit correctly identifies the form state.
    form_key = f"feedback_form_{analysis_session_id}_{uuid.uuid4()}"

    with st.form(key=form_key):
        st.write("How would you rate the accuracy and usefulness of the sales forecast?")
        rating = st.slider(
            "Rating",
            min_value=1,
            max_value=5,
            value=3,  # Default value for the slider
            step=1,
            help="1 = Very Poor, 2 = Poor, 3 = Average, 4 = Good, 5 = Excellent"
        )

        feedback_text = st.text_area(
            "Any additional comments or suggestions?",
            height=150,
            placeholder="e.g., 'The forecast was very accurate for product X but struggled with product Y. "
                        "I'd like to see more details on the confidence intervals.'\n"
                        "Or: 'The UI was intuitive, but the data upload process could be smoother.'",
            max_chars=1000,
            help="Provide detailed comments to help us understand your experience."
        )

        submit_button = st.form_submit_button("Submit Feedback")

        if submit_button:
            # Basic input validation
            if not user_id:
                st.error("User ID is missing. Cannot submit feedback without a user identifier. Please log in or ensure user ID is passed.")
                return
            if not analysis_session_id:
                st.error("Analysis Session ID is missing. Cannot submit feedback without a session identifier. This indicates an internal application error.")
                return

            try:
                # Call the store_feedback function from the imported `db` module.
                # This function is expected to handle database connection, table creation
                # (if necessary), and insertion of the feedback data.
                success = db.store_feedback(
                    user_id=user_id,
                    analysis_session_id=analysis_session_id,
                    rating=rating,
                    feedback_text=feedback_text
                )

                if success:
                    st.success("Thank you for your valuable feedback! We appreciate your input and will use it to improve our service.")
                    # Optionally, clear the form or disable it after successful submission
                    # For now, the success message is sufficient.
                else:
                    st.error("Failed to submit feedback. Please try again later. If the problem persists, contact support.")
            except Exception as e:
                # Catch any unexpected errors during the database operation
                st.error(f"An unexpected error occurred during feedback submission: {e}")
                st.exception(e)  # Display full traceback for debugging purposes


def _get_current_user_id() -> str:
    """
    Placeholder function to retrieve the current user's ID for demonstration purposes.
    In a real application, this would integrate with an authentication system (e.g., `auth.py`)
    or retrieve the ID from `st.session_state` after a successful login.
    """
    if 'user_id' in st.session_state and st.session_state['user_id']:
        return st.session_state['user_id']
    return "anonymous_user_" + str(uuid.uuid4())[:8] # Fallback for testing


def _get_current_analysis_session_id() -> str:
    """
    Placeholder function to retrieve the current analysis session ID for demonstration.
    In a real application, this ID should be generated by `pages/sales_forecasting.py`
    when an analysis begins and stored in `st.session_state` or passed explicitly.
    """
    if 'current_analysis_session_id' not in st.session_state:
        st.session_state['current_analysis_session_id'] = str(uuid.uuid4())
    return st.session_state['current_analysis_session_id']


if __name__ == "__main__":
    # This block demonstrates how to use the feedback form in a standalone Streamlit app.
    # It simulates the context of a user and an analysis session.
    st.set_page_config(layout="centered", page_title="Feedback Module Test")
    st.title("Feedback Module Standalone Test")
    st.write("This is a standalone test of the feedback form component. "
             "It simulates a user submitting feedback after an analysis.")

    # Simulate user and session IDs for testing purposes
    test_user_id = _get_current_user_id()
    test_analysis_session_id = _get_current_analysis_session_id()

    st.info(f"Simulated User ID: `{test_user_id}`")
    st.info(f"Simulated Analysis Session ID: `{test_analysis_session_id}`")

    # Display the feedback form
    display_feedback_form(test_user_id, test_analysis_session_id)

    st.markdown("---")
    st.subheader("Expected `db.py` Implementation for Feedback Storage")
    st.write(
        "For the feedback to be stored persistently, your `db.py` file "
        "should contain functions similar to the example below. "
        "This example uses SQLite for simplicity, but it can be adapted "
        "for other databases."
    )
    st.code(
        """
# In db.py

import sqlite3
import datetime
from typing import Optional

def get_db_connection():
    \"\"\"Establishes and returns a connection to the SQLite database.\"\"\"
    conn = sqlite3.connect('app_data.db')
    conn.row_factory = sqlite3.Row # Allows accessing columns by name
    return conn

def create_feedback_table_if_not_exists():
    \"\"\"Creates the 'feedback' table in the database if it doesn't already exist.\"\"\"
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                analysis_session_id TEXT NOT NULL,
                rating INTEGER NOT NULL,
                feedback_text TEXT,
                timestamp TEXT NOT NULL
            )
        ''')
        conn.commit()
    except sqlite3.Error as e:
        print(f"Database error creating feedback table: {e}")
        # In a production app, you might log this error more robustly
    finally:
        conn.close()

def store_feedback(user_id: str, analysis_session_id: str, rating: int, feedback_text: Optional[str]) -> bool:
    \"\"\"
    Stores user feedback in the 'feedback' table.

    Args:
        user_id (str): The unique identifier of the user.
        analysis_session_id (str): The unique identifier for the analysis session.
        rating (int): The user's rating (e.g., 1-5).
        feedback_text (Optional[str]): The user's detailed feedback, can be None or empty.

    Returns:
        bool: True if the feedback was successfully stored, False otherwise.
    \"\"\"
    create_feedback_table_if_not_exists() # Ensure the table exists before inserting
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        timestamp = datetime.datetime.now().isoformat()
        cursor.execute(
            "INSERT INTO feedback (user_id, analysis_session_id, rating, feedback_text, timestamp) "
            "VALUES (?, ?, ?, ?, ?)",
            (user_id, analysis_session_id, rating, feedback_text if feedback_text else "", timestamp)
        )
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Database error storing feedback: {e}")
        # Log the error for debugging
        return False
    finally:
        conn.close()

# Example usage (not part of db.py itself, but for testing db.py functions)
if __name__ == '__main__':
    create_feedback_table_if_not_exists()
    print("Feedback table ensured to exist.")
    if store_feedback("test_user_123", "session_abc_456", 4, "Great model, very insightful!"):
        print("Test feedback stored successfully.")
    else:
        print("Failed to store test feedback.")
    """
    )