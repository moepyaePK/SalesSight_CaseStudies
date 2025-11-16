import streamlit as st
import base64
import datetime
import uuid
import db # Assuming db.py is in the same directory or importable path.

def require_upload():
    """
    Check if the user has uploaded a file.
    If not, show a warning and stop the page from rendering main content.
    """
    if "save_path" not in st.session_state:
        st.warning("⚠️ Please upload a sales CSV file first on the Upload page to view analytics.")
        st.stop()

def custom_sidebar(logo_path="logo.png", title="SalesSight"):
    """
    Configures a custom sidebar for the Streamlit application,
    including a logo and title, and hides the default Streamlit navigation.

    Args:
        logo_path (str): The file path to the application logo image.
        title (str): The title to display in the sidebar.
    """
    # Hide Streamlit default sidebar navigation
    st.markdown("""
        <style>
        [data-testid="stSidebarNav"] {display: none;}
        </style>
    """, unsafe_allow_html=True)

    # Encode logo to base64
    logo_base64 = ""
    try:
        with open(logo_path, "rb") as f:
            logo_base64 = base64.b64encode(f.read()).decode()
    except FileNotFoundError:
        st.error(f"Logo file not found at {logo_path}. Please ensure it exists.")
        # Continue without logo if not found
    except Exception as e:
        st.error(f"An error occurred while reading the logo file: {e}")
        # Continue without logo

    # Sidebar styling
    st.markdown(f"""
        <style>
        .sidebar-title {{
            display: flex;
            align-items: center;
            gap: 10px;
            font-family: 'Inter', sans-serif;
            font-weight: 600;
            font-size: 18px;
            color: #1E90FF;
            margin-bottom: 25px;
        }}
        .sidebar-title img {{
            width: 30px;
            height: 30px;
        }}
        </style>
    """, unsafe_allow_html=True)

    # Sidebar structure
    with st.sidebar:
        if logo_base64:
            st.markdown(
                f"""
                <div class="sidebar-title">
                    <img src="data:image/png;base64,{logo_base64}" />
                    <span>{title}</span>
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            # Fallback if logo not found or error occurred
            st.markdown(
                f"""
                <div class="sidebar-title">
                    <span>{title}</span>
                </div>
                """,
                unsafe_allow_html=True
            )

def submit_user_feedback(feedback_text: str, rating: int) -> bool:
    """
    Handles the submission of user feedback by storing it in the database.
    It generates a user ID (if not already present in session) and a timestamp.
    Displays a confirmation message upon successful submission or an error message otherwise.

    Args:
        feedback_text (str): The text content of the user's feedback. Can be an empty string.
        rating (int): The rating provided by the user (e.g., 1-5).

    Returns:
        bool: True if feedback was successfully stored, False otherwise.
    """
    # Generate a simple user ID for the session if not already present.
    # In a real application with authentication, this would come from the logged-in user's ID.
    if 'user_id' not in st.session_state:
        st.session_state['user_id'] = str(uuid.uuid4())
    user_id = st.session_state['user_id']

    timestamp = datetime.datetime.now().isoformat()

    try:
        # Call the db.py function to store feedback.
        # This assumes db.py has a function named 'store_feedback'
        # that accepts user_id, feedback_text, rating, and timestamp,
        # and returns True on success, False on failure.
        success = db.store_feedback(user_id, feedback_text, rating, timestamp)
        if success:
            st.success("Thank you for your feedback! It helps us improve.")
            return True
        else:
            st.error("Failed to submit feedback due to a database issue. Please try again later.")
            return False
    except AttributeError:
        st.error("Database module 'db' or 'store_feedback' function not found. Please ensure 'db.py' is correctly set up with a 'store_feedback' function.")
        print("Error: 'db.store_feedback' not found. Ensure db.py is correctly implemented and imported.")
        return False
    except Exception as e:
        st.error(f"An unexpected error occurred while submitting feedback: {e}")
        # Log the error for debugging purposes
        print(f"Error storing feedback for user {user_id}: {e}")
        return False
