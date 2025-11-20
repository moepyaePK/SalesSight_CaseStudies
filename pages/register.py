import streamlit as st
from auth import register_user

# ---- Hide Sidebar Completely (including arrow + space) ----
# This is a UI-specific enhancement and can remain as is.
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
    </style>
"""
st.markdown(hide_sidebar_style, unsafe_allow_html=True)
# --------------------------------------------------------

st.title("📝 Register New Account")

# Use a form for better user experience
with st.form("registration_form"):
    username = st.text_input("Username")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")
    submitted = st.form_submit_button("Register")

if submitted:
    # Delegate all registration logic, including validation and user creation,
    # to the centralized auth module.
    success, message = register_user(username, email, password, confirm_password)

    if success:
        st.success(message)
        st.info("Redirecting to login page...")
        # The user might not see the message if we switch immediately.
        # A small delay can improve UX, though st.switch_page is quite fast.
        st.switch_page("pages/login.py")
    else:
        # Display the specific error message returned from the auth module.
        st.error(f"⚠️ {message}")

st.markdown("---")
st.write("Already have an account?")
if st.button("Login"):
    st.switch_page("pages/login.py")