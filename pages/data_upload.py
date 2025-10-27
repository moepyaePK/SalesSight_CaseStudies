import streamlit as st
import os
import time
import json
import pandas as pd
from utils import custom_sidebar
from auth import is_logged_in
import base64
import os
from auth import logout

st.markdown("""
<style>
[data-testid="stSidebarNav"] {display: none !important;}
</style>
""", unsafe_allow_html=True)


st.set_page_config(page_title="SalesSight - Data Upload", layout="wide")



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




def data_extraction(file_path):
    try:
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        return {"error": "File not found"}
    except Exception as e:
        return {"error": f"Error reading file: {e}"}

    # Validate required columns
    required_cols = ['Sales', 'Date']
    for col in required_cols:
        if col not in df.columns:
            return {"error": f"Missing required column: {col}"}

    # Clean and sort data
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df = df.dropna(subset=['Date', 'Sales']).sort_values('Date')

    # Compute KPIs
    total_sales = df['Sales'].sum()
    avg_sales = df['Sales'].mean()
    latest_sales = df['Sales'].iloc[-1] if len(df) > 0 else 0
    growth = ((df['Sales'].iloc[-1] - df['Sales'].iloc[-2]) / df['Sales'].iloc[-2] * 100) if len(df) > 1 else 0

    # Sales trend over time (monthly aggregation)
    sales_trend = (
        df.groupby(df['Date'].dt.to_period('M'))['Sales']
        .sum()
        .reset_index()
        .sort_values('Date')
    )
    sales_trend['Date'] = sales_trend['Date'].dt.to_timestamp()

    # Top products by sales (if Product column exists)
    if 'Product' in df.columns:
        top_products = (
            df.groupby('Product')['Sales']
            .sum()
            .sort_values(ascending=False)
            .head(5)
            .reset_index()
        )
    else:
        top_products = None

    metrics = {
        "total_sales": round(total_sales, 2),
        "avg_sales": round(avg_sales, 2),
        "latest_sales": round(latest_sales, 2),
        "growth": round(growth, 2),
        "sales_trend": sales_trend,
        "top_products": top_products
    }

    return metrics

    

st.title("📤 Upload Sale Data")

col1, col2 = st.columns([1.5, 1])

with col1:
    uploaded_files = st.file_uploader(
        "",
        type=["csv", "xlsx"],
        accept_multiple_files=True,
        label_visibility="visible"
    )


with col2:
    st.markdown(
        """
        <div style="
            border: 1px solid #B3D4FC;
            background-color: #F0F7FF;
            border-radius: 8px;
            padding: 15px 20px;
            margin-bottom: 20px;
            font-family: 'Segoe UI', sans-serif;
        ">
            <strong style="color:#2C6BED; font-size:16px;">📘 File Requirements</strong>
            <ul style="margin-top: 10px; margin-bottom: 0; color:#333; font-size:14px;">
                <li><strong>File formats:</strong> CSV, XLSX</li>
                <li><strong>Maximum file size:</strong> 200 MB</li>
                <li><strong>Required columns:</strong> Date, Product, Sales</li>
                <li><strong>Date format:</strong> YYYY-MM-DD or MM/DD/YYYY</li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True
    )


if "file_status" not in st.session_state:
    st.session_state.file_status = {}
    st.session_state.save_path = {}


if uploaded_files:
    os.makedirs("tmp", exist_ok=True)
    for uploaded_file in uploaded_files:
        file_name = uploaded_file.name
        save_path = os.path.join("tmp", file_name)
        with open(save_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        st.session_state.save_path = save_path  # ✅ Store string only
        st.session_state.file_status[file_name] = "✅ Completed"


st.subheader("Uploaded Files")
if st.session_state.file_status:
    for file, status in st.session_state.file_status.items():
        if "✅" in status:
            st.success(f"{file} {status}")
        elif "⏳" in status:
            st.warning(f"{file} {status}")
        else:
            st.error(f"{file} ❌ {status}")
else:
    st.info("No files uploaded yet.")
    
    
