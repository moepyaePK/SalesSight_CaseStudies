import streamlit as st
from auth import is_logged_in, logout

st.set_page_config(page_title="SalesSight - Home", layout="wide")



# ---- Hide Sidebar Completely (including arrow + space) ----
hide_sidebar_style = """
    <style>
        /* Hide the sidebar completely */
        [data-testid="stSidebar"], 
        [data-testid="stSidebarNav"], 
        [data-testid="stSidebarCollapsedControl"],
        section[data-testid="stSidebar"] {
            display: none !important;
        }

        /* Hide the expand/collapse button (for older/newer versions) */
        button[title="Expand sidebar"], 
        button[kind="header"], 
        [data-testid="baseButton-header"] {
            display: none !important;
        }

        /* Remove sidebar space and expand main view fully */
        [data-testid="stAppViewContainer"] {
            margin-left: 0 !important;
            width: 100% !important;
        }

        /* Remove any internal padding */
        [data-testid="stVerticalBlock"] > div:first-child {
            padding-left: 0 !important;
            padding-right: 0 !important;
        }

        /* Optional: hide top navbar dropdown if present */
        [data-testid="stHeaderActionElements"] {
            display: none !important;
        }

        /* Light blue styling for login and register buttons */
        .stButton > button {
            background-color: #1E61D4 !important;
            color: white !important;
            border: none !important;
            border-radius: 5px !important;
            padding: 0.5rem 1rem !important;
            font-weight: 500 !important;
        }
        
        .stButton > button:hover {
            background-color: #5DADE2 !important;
            color: white !important;
        }
    </style>
"""
st.markdown(hide_sidebar_style, unsafe_allow_html=True)
# --------------------------------------------------------



st.title("💼 Welcome to SalesSight!")
st.write("Gain insights from your sales data with interactive dashboards and forecasting tools.")

st.markdown("---")

if is_logged_in():
    st.success(f"You're logged in as **{st.session_state['email']}**.")
    if st.button("Go to Dashboard"):
        st.switch_page("dashboard.py")
    if st.button("Logout"):
        logout()
        st.experimental_rerun()
else:
    st.info("Please log in or register to access the Dashboard.")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔐 Login"):
            st.switch_page("pages/login.py")
    with col2:
        if st.button("📝 Register"):
            st.switch_page("pages/register.py")