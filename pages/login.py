import streamlit as st
from auth import login_user

# ---- Hide Sidebar Completely (including arrow + space) ----
# This is kept for consistent UI experience on the login/register pages
# as they are outside the main authenticated app flow.
hide_sidebar_style = """
    <style>
        [data-testid="stSidebar"],
        [data-testid="stSidebarNav"],
        [data-testid="stSidebarCollapsedControl"] {
            display: none !important;
        }
        section[data-testid="stSidebar"] {
            display: none !important;
        }
        [data-testid="stAppViewContainer"] {
            margin-left: 0 !important;
            width: 100% !important;
        }
    </style>
"""
st.markdown(hide_sidebar_style, unsafe_allow_html=True)
# --------------------------------------------------------

st.title("🔑 Login")

with st.form("login_form"):
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    submitted = st.form_submit_button("Login")

    if submitted:
        if login_user(email, password):
            st.success("Login successful!")
            st.switch_page("pages/data_upload.py")
        else:
            st.error("Invalid email or password.")

st.markdown("---")
st.write("Don't have an account yet?")
if st.button("📝 Register"):
    st.switch_page("pages/register.py")