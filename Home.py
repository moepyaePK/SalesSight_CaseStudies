import streamlit as st
from auth import is_logged_in, logout

st.set_page_config(page_title="SalesSight - Home", layout="wide")

# ---- Hide Sidebar Completely & Custom Button Styles ----
hide_sidebar_style = """
    <style>
        /* Hide the sidebar completely */
        [data-testid="stSidebar"], 
        [data-testid="stSidebarNav"], 
        [data-testid="stSidebarCollapsedControl"],
        section[data-testid="stSidebar"] {
            display: none !important;
        }

        /* Hide the expand/collapse button */
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

        /* Remove internal padding */
        [data-testid="stVerticalBlock"] > div:first-child {
            padding-left: 0 !important;
            padding-right: 0 !important;
        }

        /* Hide top navbar dropdown */
        [data-testid="stHeaderActionElements"] {
            display: none !important;
        }

        /* ---------------------------------------------- */
        /* 🎨 Custom Styles for ALL Buttons               */
        /* ---------------------------------------------- */

        /* Base button styles */
        div.stButton > button {
            background-color: #1e40af !important;
            color: white !important;
            border-radius: 8px !important;
            padding: 8px 18px !important;
            font-weight: 600 !important;
            border: 1px solid #1e3a8a !important;
            transition: all 0.3s ease !important;
        }
        
        /* Button hover state */
        div.stButton > button:hover {
            background-color: #3b82f6 !important;
            border: 1px solid #60a5fa !important;
            color: white !important;
            transform: translateY(-1px) !important;
            box-shadow: 0 4px 6px rgba(59, 130, 246, 0.3) !important;
        }
        
        /* Button active/pressed state */
        div.stButton > button:active {
            transform: translateY(0) !important;
            box-shadow: 0 2px 4px rgba(59, 130, 246, 0.2) !important;
        }
        
        /* Ensure button text is white */
        div.stButton > button p {
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
        st.rerun()

else:
    st.info("Please log in or register to access the Dashboard.")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("🔐 Login"):
            st.switch_page("pages/login.py")

    with col2:
        if st.button("📝 Register"):
            st.switch_page("pages/register.py")
