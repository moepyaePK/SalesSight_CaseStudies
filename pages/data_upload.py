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
        return json.dumps([
            {"metricName": "error", "value": "File not found", "unit": None}
        ])
    except Exception as e:
        return json.dumps([
            {"metricName": "error", "value": f"Error reading file: {e}", "unit": None}
        ])

    # Check for essential columns
    has_sales = 'Sales' in df.columns
    has_profit = 'Profit' in df.columns
    has_order_id = 'Order ID' in df.columns
    
    # 1. Calculate Total Sales
    total_sales = df['Sales'].sum() if has_sales else None

    # 2. Calculate Total Profit
    total_profit = df['Profit'].sum() if has_profit else None

    # 3. Calculate Number of Orders (unique Order IDs)
    number_of_orders = df['Order ID'].nunique() if has_order_id else None

    # 4. Calculate Gross Margin
    # Gross Margin = (Total Profit / Total Sales) * 100
    gross_margin = None
    if total_profit is not None and total_sales is not None and total_sales != 0:
        gross_margin = (total_profit / total_sales) * 100
        # Round the margin percentage for presentation
        gross_margin = round(gross_margin, 2)
    
    # --- Format the Output as a JSON Array ---
    
    metrics = [
        {
            "metricName": "total sales",
            "value": round(total_sales, 2) if total_sales is not None else None,
            "unit": "$" if total_sales is not None else None
        },
        {
            "metricName": "total profit",
            "value": round(total_profit, 2) if total_profit is not None else None,
            "unit": "$" if total_profit is not None else None
        },
        {
            "metricName": "number of orders",
            "value": number_of_orders,
            "unit": "orders" if number_of_orders is not None else None
        },
        {
            "metricName": "gross margin",
            "value": gross_margin,
            "unit": "%" if gross_margin is not None else None
        }
    ]
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
    
    
