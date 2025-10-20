import streamlit as st
import os
import time
import json
import pandas as pd
from utils import add_sidebar_logo
st.set_page_config(page_title="SalesSight - Data Upload", layout="wide")

add_sidebar_logo()


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
    
    
