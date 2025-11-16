import streamlit as st
from utils import custom_sidebar
from auth import is_logged_in
import base64
import os
from auth import logout

st.set_page_config(page_title="SalesSight - Settings", layout="wide")

st.title("⚙️ Settings")
st.write("Configure your SalesSight preferences here.")



st.markdown("""
<style>
[data-testid="stSidebarNav"] {display: none !important;}
</style>
""", unsafe_allow_html=True)
custom_sidebar()

# --- Sidebar Content ---
with st.sidebar:
    st.page_link("pages/dashboard.py", label="📊 Dashboard")
    st.page_link("pages/data_upload.py", label="📂 Upload")
    st.page_link("pages/sales_forecasting.py", label="📈 Sales Forecasting")
    st.page_link("pages/setting.py", label="⚙️ Settings")
    if st.button("Logout"):
        logout() 

if not is_logged_in():
    st.warning("⚠️ Please login to continue.")
    st.switch_page("Home.py")
    st.stop()

