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

    # Validate columns
    required_cols = ['Sales', 'Profit', 'Order ID']
    for col in required_cols:
        if col not in df.columns:
            return {"error": f"Missing required column: {col}"}

    # Compute KPIs
    total_sales = df['Sales'].sum()
    total_profit = df['Profit'].sum()
    num_orders = df['Order ID'].nunique()
    gross_margin = round((total_profit / total_sales) * 100, 2) if total_sales != 0 else 0

    # Sales trend over time (if date exists)
    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        sales_trend = (
            df.groupby(df['Date'].dt.to_period('M'))['Sales']
            .sum()
            .reset_index()
            .sort_values('Date')
        )
        sales_trend['Date'] = sales_trend['Date'].astype(str)
    else:
        sales_trend = None

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

    # Store metrics
    metrics = {
        "total_sales": round(total_sales, 2),
        "total_profit": round(total_profit, 2),
        "num_orders": int(num_orders),
        "gross_margin": gross_margin,
        "sales_trend": sales_trend,
        "top_products": top_products
    }

    return metrics
    

st.title("📤 Upload Sale Data")

uploaded_files = st.file_uploader(
    "Drop files here or browse",
    type=["csv", "xlsx"],
    accept_multiple_files=True
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
    
    
