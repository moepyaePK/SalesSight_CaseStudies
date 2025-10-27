import streamlit as st
from auth import register_user , add_user
from db import is_valid_email

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
    </style>
"""
st.markdown(hide_sidebar_style, unsafe_allow_html=True)
# --------------------------------------------------------



st.title("📝 Register New Account")
username = st.text_input("Username")
email = st.text_input("Email")
password = st.text_input("Password", type="password")
confirm_password = st.text_input("Confirm Password", type="password")

if st.button("Register"):
    # Basic validation
    if not username or not email or not password or not confirm_password:
        st.warning("⚠️ Please fill in all fields.")
    elif password != confirm_password:
        st.warning("⚠️ Passwords do not match.")
    elif not is_valid_email(email):
        st.warning("⚠️ Invalid email address. Please enter a valid email.")
    else:
        try:
            add_user(username, email, password)
            st.switch_page("pages/login.py")
            st.success("✅ Registration successful! You can now login.")
            st.info("Go to the login page to access your account.")
        except Exception as e:
            if "UNIQUE constraint failed: users.username" in str(e):
                st.error("⚠️ Username already exists. Choose another one.")
            elif "UNIQUE constraint failed: users.email" in str(e):
                st.error("⚠️ Email already registered. Try logging in.")
            else:
                st.error(f"⚠️ Registration failed: {e}")


st.markdown("---")
st.write("Already have an account?")
if st.button("📝 Login"):
    st.switch_page("pages/login.py")