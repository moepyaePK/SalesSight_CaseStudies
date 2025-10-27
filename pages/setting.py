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

# --- Sidebar Style ---
logo_path = "logo.png"
title = "SalesSight"

with open(logo_path, "rb") as f:
    logo_base64 = base64.b64encode(f.read()).decode()

st.markdown(
    f"""
    <style>
        [data-testid="stSidebar"] {{
            background-color: #ffffff !important;
            padding-top: 0 !important;
        }}

        [data-testid="stSidebarNav"]::before {{
            content: "";
            display: flex;
            align-items: center;
            justify-content: flex-start;
            height: 60px;
            width: 100%;
            background-color: #ffffff;
            background-image: url("data:image/png;base64,{logo_base64}");
            background-repeat: no-repeat;
            background-size: 26px 26px;
            background-position: 18px center;
            border-bottom: 1px solid #f2f2f2;
            position: relative;
            z-index: 1;
            pointer-events: none;
        }}

        [data-testid="stSidebarNav"]::after {{
            content: "{title}";
            position: absolute;
            top: 18px;
            left: 52px;
            font-family: 'Inter', sans-serif;
            font-weight: 600;
            font-size: 18px;
            color: #1E90FF;
            z-index: 1;
            pointer-events: none;
        }}

        [data-testid="stSidebarNav"] {{
            margin-top: -60px !important;
            position: relative;
            z-index: 0;
        }}

        [data-testid="stSidebarNav"] ul {{
            padding-left: 10px;
        }}

        [data-testid="stSidebarNav"] li a {{
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 8px 14px;
            border-radius: 8px;
            text-decoration: none;
            font-family: 'Inter', sans-serif;
            font-size: 15px;
            font-weight: 500;
            color: #4B5563 !important;
            transition: all 0.2s ease-in-out;
        }}

        [data-testid="stSidebarNav"] li a[data-testid="stSidebarNavLinkActive"] {{
            background-color: #bbddfc !important;
            color: #1E90FF !important;
            font-weight: 600 !important;
        }}
    </style>
    """,
    unsafe_allow_html=True
)

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

